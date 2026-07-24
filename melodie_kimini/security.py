"""
ANTI-HACKING SECURITY MODULE
Protects crypto earning logic from reverse engineering, injection, and tampering.

Layers of Protection:
1. HMAC-SHA256 integrity verification on all data files
2. Rate limiting with rolling window to prevent rapid-fire earning
3. Tamper detection via checksums and file hashing
4. Obfuscated earning calculations with rolling salt
5. Anti-debugging / anti-hooking checks
6. Balance bounds validation with hard limits
7. Transaction fingerprinting to detect replay attacks
8. Cooldown enforcement between earning events
"""

import os
import sys
import json
import time
import hmac
import hashlib
import struct
import secrets
import functools
from datetime import datetime, timedelta

# ============================================================
#  OBFUSCATED CONSTANTS (rolling salt changes per session)
# ============================================================

_SESSION_SALT = secrets.token_hex(16)
_BOOT_TIME = time.time()

# Internal secret key derived at runtime - never stored, never static
def _derive_key():
    t = int(_BOOT_TIME * 1000) & 0xFFFFFFFF
    h = hashlib.sha256(
        b"MK-SEC-" + _SESSION_SALT.encode() + struct.pack(">I", t) + b"-V3"
    ).digest()
    return h[:32]

# ============================================================
#  DATA FILE INTEGRITY (HMAC-SHA256)
# ============================================================

class VaultLock:
    """HMAC integrity wrapper for all JSON data files."""

    def __init__(self):
        self._key = _derive_key()
        self._meta_file = None

    def _hmac_path(self, filepath):
        return filepath + ".vault"

    def seal(self, filepath, data):
        """Write data + HMAC signature."""
        raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
        tag = hmac.new(self._key, raw, hashlib.sha256).hexdigest()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, separators=(",", ":"))
        with open(self._hmac_path(filepath), "w") as f:
            f.write(tag)

    def verify_and_load(self, filepath, default=None):
        """Load and verify integrity. Returns default if tampered."""
        if not os.path.exists(filepath):
            return default() if callable(default) else default
        if not os.path.exists(self._hmac_path(filepath)):
            return self._recover_fallback(filepath, default)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return default() if callable(default) else default
        raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
        expected_tag = hmac.new(self._key, raw, hashlib.sha256).hexdigest()
        with open(self._hmac_path(filepath), "r") as f:
            stored_tag = f.read().strip()
        if not hmac.compare_digest(expected_tag, stored_tag):
            _TamperLog.record(filepath, "HMAC_MISMATCH")
            return default() if callable(default) else default
        return data

    def _recover_fallback(self, filepath, default):
        """If vault file missing but data exists, re-seal and allow."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.seal(filepath, data)
            _TamperLog.record(filepath, "RESEALED")
            return data
        except Exception:
            return default() if callable(default) else default


# ============================================================
#  TAMPER DETECTION LOG
# ============================================================

class _TamperLog:
    _log = []
    _MAX = 200

    @classmethod
    def record(cls, filepath, reason):
        entry = {
            "file": os.path.basename(filepath),
            "reason": reason,
            "time": datetime.utcnow().isoformat(),
            "pid": os.getpid(),
        }
        cls._log.append(entry)
        if len(cls._log) > cls._MAX:
            cls._log = cls._log[-cls._MAX:]

    @classmethod
    def get_log(cls):
        return list(cls._log)

    @classmethod
    def has_tampering(cls):
        return len(cls._log) > 0


# ============================================================
#  RATE LIMITER (Rolling Window)
# ============================================================

class RateLimiter:
    """Prevents rapid-fire earning via rolling time windows."""

    def __init__(self):
        self._events = []

    def check(self, event_type, min_interval_sec=1.0, max_per_minute=30):
        now = time.time()
        self._events = [t for t in self._events if now - t < 60]
        recent = sum(1 for t in self._events if now - t < 60)
        if recent >= max_per_minute:
            _TamperLog.record(event_type, f"RATE_EXCEEDED:{recent}/min")
            return False
        if self._events and (now - self._events[-1]) < min_interval_sec:
            _TamperLog.record(event_type, "TOO_FAST")
            return False
        self._events.append(now)
        return True


# ============================================================
#  BALANCE BOUNDS VALIDATOR
# ============================================================

class BalanceGuard:
    """Hard limits on earning and balance to prevent injection."""

    MAX_SINGLE_EARN = 500.0
    MAX_DAILY_EARN = 2000.0
    MAX_TOTAL_BALANCE = 1000000.0
    MAX_STAKED = 500000.0

    @staticmethod
    def validate_earn(amount, daily_earned, current_balance, action="earn"):
        if amount < 0:
            return 0.0, "PENALTY"
        if amount > BalanceGuard.MAX_SINGLE_EARN:
            _TamperLog.record(action, f"EXCESSIVE_SINGLE:{amount}")
            return 0.0, "BLOCKED_SINGLE"
        if daily_earned + amount > BalanceGuard.MAX_DAILY_EARN:
            remaining = max(0, BalanceGuard.MAX_DAILY_EARN - daily_earned)
            _TamperLog.record(action, f"DAILY_CAP:{daily_earned}+{amount}")
            return remaining, "DAILY_CAP"
        if current_balance + amount > BalanceGuard.MAX_TOTAL_BALANCE:
            remaining = max(0, BalanceGuard.MAX_TOTAL_BALANCE - current_balance)
            _TamperLog.record(action, f"TOTAL_CAP:{current_balance}+{amount}")
            return remaining, "TOTAL_CAP"
        return amount, "OK"

    @staticmethod
    def validate_stake(amount, balance):
        if amount <= 0:
            return 0.0, "INVALID"
        if amount > balance:
            return 0.0, "INSUFFICIENT"
        if amount > BalanceGuard.MAX_STAKED:
            _TamperLog.record("stake", f"EXCESSIVE_STAKE:{amount}")
            return 0.0, "BLOCKED"
        return amount, "OK"


# ============================================================
#  TRANSACTION FINGERPRINTING (Replay Protection)
# ============================================================

class Fingerprint:
    """Generates unique fingerprints to detect replay attacks."""

    def __init__(self):
        self._seen = set()
        self._MAX_SEEN = 10000

    def generate(self, user_id, action, amount, timestamp):
        raw = f"{user_id}:{action}:{amount}:{timestamp}:{_SESSION_SALT}"
        fp = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return fp

    def is_replay(self, fp):
        if fp in self._seen:
            _TamperLog.record("replay", f"DUPLICATE_FP:{fp}")
            return True
        self._seen.add(fp)
        if len(self._seen) > self._MAX_SEEN:
            self._seen = set(list(self._seen)[-self._MAX_SEEN // 2:])
        return False


# ============================================================
#  EARNING CALCULATION OBFUSCATOR
# ============================================================

class SecureCalc:
    """Obfuscated earning math that can't be trivially patched."""

    _MULT_ROUNDS = 3

    @staticmethod
    def compute_earn(base_amount, multiplier, category_rate, round_seed):
        """Multi-round obfuscated calculation."""
        a = base_amount
        for _ in range(SecureCalc._MULT_ROUNDS):
            a = a * multiplier
            a = round(a * category_rate, 6)
        jitter = (round_seed % 7) * 0.001
        a += jitter
        return round(a, 4)

    @staticmethod
    def compute_daily_projection(base_daily, streak_days, staked_amount, apy):
        """Obfuscated daily projection."""
        s_mult = 1.0 + (min(streak_days, 365) * 0.005)
        s_yield = staked_amount * (apy / 365.0)
        proj = base_daily * s_mult + s_yield
        return round(proj, 4)


# ============================================================
#  ANTI-DEBUGGING / ANTI-HOOKING
# ============================================================

class AntiDebug:
    """Detects debugging/hooking to prevent runtime manipulation."""

    @staticmethod
    def check():
        if "PYDEVD" in os.environ or "PYCHARM" in os.environ:
            _TamperLog.record("anti_debug", "DEBUGGER_ATTACHED")
            return True
        if hasattr(sys, "gettrace") and sys.gettrace() is not None:
            _TamperLog.record("anti_debug", "TRACE_ACTIVE")
            return True
        return False


# ============================================================
#  GLOBAL INSTANCES
# ============================================================

vault = VaultLock()
rate_limiter = RateLimiter()
balance_guard = BalanceGuard()
fingerprint = Fingerprint()
secure_calc = SecureCalc()

# ============================================================
#  SECURE DATA ACCESSORS (Drop-in replacements)
# ============================================================

def secure_load(filepath, default=None):
    """Load with HMAC verification."""
    return vault.verify_and_load(filepath, default)

def secure_save(filepath, data):
    """Save with HMAC seal."""
    vault.seal(filepath, data)

def can_earn(action, min_interval=1.0, max_per_min=30):
    """Check rate limit before earning."""
    return rate_limiter.check(action, min_interval_sec=min_interval, max_per_minute=max_per_min)

def validate_earn(amount, daily_earned, balance, action="earn"):
    """Validate earning amount against hard limits."""
    return balance_guard.validate_earn(amount, daily_earned, balance, action)

def validate_stake(amount, balance):
    """Validate staking amount."""
    return balance_guard.validate_stake(amount, balance)

def make_fingerprint(user_id, action, amount, ts):
    """Generate transaction fingerprint."""
    return fingerprint.generate(user_id, action, amount, ts)

def check_replay(fp):
    """Check if transaction is a replay."""
    return fingerprint.is_replay(fp)

def compute_earn(base, mult, rate, seed):
    """Obfuscated earning computation."""
    return secure_calc.compute_earn(base, mult, rate, seed)

def compute_daily(base, streak, staked, apy):
    """Obfuscated daily projection."""
    return secure_calc.compute_daily_projection(base, streak, staked, apy)

def is_debugged():
    """Check for debugging environment."""
    return AntiDebug.check()

def get_tamper_log():
    """Get tamper event log."""
    return _TamperLog.get_log()

def has_been_tampered():
    """Check if any tampering was detected."""
    return _TamperLog.has_tampering()
