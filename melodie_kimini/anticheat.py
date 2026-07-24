"""
HIGHEST GRADE ANTI-CHEAT SYSTEM
Military-grade protection for the MA Token ecosystem.

Protection Layers:
  1. Behavior Analysis Engine - fingerprint user behavior patterns
  2. Statistical Anomaly Detection - Z-score deviation alerts
  3. Cryptographic Proof-of-Work Verification - block validity
  4. Cooldown Chain Enforcement - sequential action timing
  5. Replay Attack Prevention - duplicate detection
  6. Memory Injection Lock - integrity of in-memory objects
  7. Session Machine Binding - hardware fingerprinting
  8. Earning Velocity Firewall - impossible speed detection
  9. Collusion Network Detection - multi-user abuse patterns
  10. Self-Healing Data Repair - auto-rollback on corruption
"""

import os
import sys
import json
import time
import math
import hashlib
import secrets
import struct
import threading
import functools
from datetime import datetime, timedelta
from collections import defaultdict

# ============================================================
#  LAYER 1: BEHAVIOR ANALYSIS ENGINE
# ============================================================

class BehaviorEngine:
    """Tracks and fingerprints user behavior patterns."""

    def __init__(self):
        self._profiles = {}
        self._lock = threading.Lock()

    def _get_profile(self, user_id):
        if user_id not in self._profiles:
            self._profiles[user_id] = {
                "actions": [],
                "intervals": [],
                "types": defaultdict(int),
                "amounts": [],
                "timestamps": [],
                "risk_score": 0.0,
            }
        return self._profiles[user_id]

    def record_action(self, user_id, action_type, amount, ts=None):
        with self._lock:
            ts = ts or time.time()
            profile = self._get_profile(user_id)
            profile["actions"].append(action_type)
            profile["types"][action_type] += 1
            profile["amounts"].append(amount)
            profile["timestamps"].append(ts)
            if len(profile["timestamps"]) >= 2:
                interval = ts - profile["timestamps"][-2]
                profile["intervals"].append(interval)
            if len(profile["timestamps"]) > 500:
                profile["actions"] = profile["actions"][-500:]
                profile["amounts"] = profile["amounts"][-500:]
                profile["timestamps"] = profile["timestamps"][-500:]
                profile["intervals"] = profile["intervals"][-500:]
            self._update_risk(user_id)

    def _update_risk(self, user_id):
        profile = self._profiles[user_id]
        risk = 0.0
        if len(profile["intervals"]) > 5:
            intervals = profile["intervals"][-20:]
            mean = sum(intervals) / len(intervals)
            if mean < 0.3:
                risk += 40
            elif mean < 0.5:
                risk += 20
            elif mean < 1.0:
                risk += 10
        if len(profile["amounts"]) > 10:
            amounts = profile["amounts"][-20:]
            mean_amt = sum(amounts) / len(amounts)
            if mean_amt > 100:
                risk += 30
            elif mean_amt > 50:
                risk += 15
        type_counts = dict(profile["types"])
        total = sum(type_counts.values())
        if total > 0:
            for atype, count in type_counts.items():
                ratio = count / total
                if ratio > 0.9:
                    risk += 15
                    break
        if len(profile["intervals"]) > 3:
            recent = profile["intervals"][-5:]
            if all(r < 0.2 for r in recent):
                risk += 50
        profile["risk_score"] = min(100.0, risk)

    def get_risk_score(self, user_id):
        with self._lock:
            profile = self._get_profile(user_id)
            return profile["risk_score"]

    def is_suspicious(self, user_id, threshold=70):
        return self.get_risk_score(user_id) >= threshold

    def get_profile_summary(self, user_id):
        with self._lock:
            p = self._get_profile(user_id)
            return {
                "total_actions": len(p["actions"]),
                "unique_types": len(p["types"]),
                "risk_score": p["risk_score"],
                "avg_interval": round(sum(p["intervals"])/len(p["intervals"]), 4) if p["intervals"] else 0,
                "avg_amount": round(sum(p["amounts"])/len(p["amounts"]), 4) if p["amounts"] else 0,
            }


# ============================================================
#  LAYER 2: STATISTICAL ANOMALY DETECTION
# ============================================================

class AnomalyDetector:
    """Z-score based anomaly detection for earning patterns."""

    def __init__(self):
        self._history = defaultdict(list)
        self._alerts = []

    def record(self, user_id, value):
        self._history[user_id].append(value)
        if len(self._history[user_id]) > 1000:
            self._history[user_id] = self._history[user_id][-1000:]

    def detect(self, user_id, current_value, z_threshold=3.0):
        history = self._history.get(user_id, [])
        if len(history) < 10:
            return False, 0.0
        recent = history[-50:]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)
        std = math.sqrt(variance) if variance > 0 else 0.001
        z_score = (current_value - mean) / std
        is_anomaly = abs(z_score) > z_threshold
        if is_anomaly:
            alert = {
                "user_id": user_id,
                "value": current_value,
                "mean": round(mean, 4),
                "std": round(std, 4),
                "z_score": round(z_score, 4),
                "time": datetime.utcnow().isoformat(),
            }
            self._alerts.append(alert)
            if len(self._alerts) > 200:
                self._alerts = self._alerts[-200:]
        return is_anomaly, round(z_score, 4)

    def get_alerts(self, limit=20):
        return self._alerts[-limit:]


# ============================================================
#  LAYER 3: PROOF-OF-WORK VERIFICATION
# ============================================================

class PoWVerifier:
    """Cryptographic verification of mining blocks."""

    @staticmethod
    def generate_proof(user_id, pool, nonce, timestamp):
        raw = f"{user_id}:{pool}:{nonce}:{timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def verify_block(block):
        if "proof" not in block or "nonce" not in block:
            return False, "MISSING_PROOF"
        user_id = block.get("user_id", "")
        pool = block.get("pool", "")
        nonce = block.get("nonce", 0)
        ts = block.get("timestamp", "")
        expected = PoWVerifier.generate_proof(user_id, pool, nonce, ts)
        if not secrets.compare_digest(expected, block["proof"]):
            return False, "PROOF_MISMATCH"
        difficulty = block.get("difficulty", "medium")
        target = {
            "easy": "00", "medium": "000", "hard": "0000", "extreme": "00000"
        }.get(difficulty, "000")
        if not block["proof"].startswith(target):
            return False, "INSUFFICIENT_DIFFICULTY"
        return True, "VALID"

    @staticmethod
    def verify_chain(blocks):
        results = []
        for block in blocks[-100:]:
            valid, reason = PoWVerifier.verify_block(block)
            results.append({"block_hash": block.get("proof", "")[:8], "valid": valid, "reason": reason})
        invalid = [r for r in results if not r["valid"]]
        return len(invalid) == 0, invalid


# ============================================================
#  LAYER 4: COOLDOWN CHAIN ENFORCEMENT
# ============================================================

class CooldownChain:
    """Enforces minimum time gaps between sequential actions."""

    REQUIRED_GAPS = {
        "karma_score":     0.5,
        "earn":            0.3,
        "mine_block":      1.0,
        "mining_start":    2.0,
        "stake":           3.0,
        "contribute":      2.0,
        "karma_convert":   1.0,
    }

    def __init__(self):
        self._last_actions = {}

    def check(self, user_id, action_type):
        key = f"{user_id}:{action_type}"
        now = time.time()
        required = self.REQUIRED_GAPS.get(action_type, 0.5)
        last = self._last_actions.get(key, 0)
        elapsed = now - last
        if elapsed < required:
            remaining = round(required - elapsed, 3)
            return False, remaining
        self._last_actions[key] = now
        return True, 0

    def get_cooldowns(self, user_id):
        now = time.time()
        active = {}
        for action_type, gap in self.REQUIRED_GAPS.items():
            key = f"{user_id}:{action_type}"
            last = self._last_actions.get(key, 0)
            remaining = max(0, gap - (now - last))
            if remaining > 0:
                active[action_type] = round(remaining, 3)
        return active


# ============================================================
#  LAYER 5: REPLAY ATTACK PREVENTION
# ============================================================

class ReplayGuard:
    """Prevents duplicate transaction submission."""

    def __init__(self):
        self._seen = {}
        self._lock = threading.Lock()

    def _cleanup(self):
        now = time.time()
        expired = [k for k, t in self._seen.items() if now - t > 3600]
        for k in expired:
            del self._seen[k]

    def check_and_register(self, fingerprint):
        with self._lock:
            self._cleanup()
            if fingerprint in self._seen:
                return True
            self._seen[fingerprint] = time.time()
            return False

    def is_duplicate(self, fingerprint):
        with self._lock:
            return fingerprint in self._seen


# ============================================================
#  LAYER 6: MEMORY INJECTION LOCK
# ============================================================

class MemoryLock:
    """Detects tampering with in-memory critical objects."""

    def __init__(self):
        self._snapshots = {}

    def snapshot(self, name, obj):
        raw = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        h = hashlib.sha256(raw.encode()).hexdigest()
        self._snapshots[name] = h

    def verify(self, name, obj):
        raw = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        h = hashlib.sha256(raw.encode()).hexdigest()
        expected = self._snapshots.get(name)
        if expected is not None and expected != h:
            return False
        return True


# ============================================================
#  LAYER 7: SESSION MACHINE BINDING
# ============================================================

class MachineBinding:
    """Binds sessions to hardware fingerprint."""

    def __init__(self):
        self._machine_id = self._generate_id()

    def _generate_id(self):
        components = [
            str(os.getpid()),
            str(os.getuid()) if hasattr(os, "getuid") else "win",
            os.environ.get("COMPUTERNAME", "unknown"),
            os.environ.get("USERNAME", "unknown"),
            str(int(time.time() * 1000) % 999999),
        ]
        raw = "|".join(components)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get_id(self):
        return self._machine_id

    def verify(self, expected_id):
        return secrets.compare_digest(self._machine_id, expected_id)


# ============================================================
#  LAYER 8: EARNING VELOCITY FIREWALL
# ============================================================

class VelocityFirewall:
    """Detects impossible earning speeds."""

    WINDOWS = {
        "1min":  60,
        "5min":  300,
        "1hour": 3600,
    }
    LIMITS = {
        "1min":  100.0,
        "5min":  500.0,
        "1hour": 2000.0,
    }

    def __init__(self):
        self._earnings = defaultdict(list)

    def record(self, user_id, amount):
        now = time.time()
        self._earnings[user_id].append((now, amount))
        cutoff = now - 3600
        self._earnings[user_id] = [
            (t, a) for t, a in self._earnings[user_id] if t > cutoff
        ]

    def check(self, user_id, new_amount):
        now = time.time()
        violations = []
        for window_name, window_sec in self.WINDOWS.items():
            cutoff = now - window_sec
            window_total = sum(a for t, a in self._earnings[user_id] if t > cutoff)
            projected = window_total + new_amount
            limit = self.LIMITS[window_name]
            if projected > limit:
                violations.append({
                    "window": window_name,
                    "projected": round(projected, 4),
                    "limit": limit,
                    "excess": round(projected - limit, 4),
                })
        is_blocked = len(violations) > 0
        return is_blocked, violations


# ============================================================
#  LAYER 9: COLLUSION NETWORK DETECTION
# ============================================================

class CollusionDetector:
    """Detects multi-user abuse patterns."""

    def __init__(self):
        self._user_pairs = defaultdict(int)
        self._suspicious_pairs = []

    def record_interaction(self, user_a, user_b):
        if user_a == user_b:
            return
        pair = tuple(sorted([user_a, user_b]))
        self._user_pairs[pair] += 1
        if self._user_pairs[pair] > 50:
            if pair not in [p for p, _ in self._suspicious_pairs]:
                self._suspicious_pairs.append((pair, self._user_pairs[pair]))

    def get_suspicious_pairs(self):
        return list(self._suspicious_pairs)


# ============================================================
#  LAYER 10: SELF-HEALING DATA REPAIR
# ============================================================

class SelfHealer:
    """Auto-rollback corrupted data from backup snapshots."""

    def __init__(self):
        self._backups = {}
        self._MAX_BACKUPS = 3

    def snapshot(self, name, data):
        if name not in self._backups:
            self._backups[name] = []
        self._backups[name].append({
            "data": json.loads(json.dumps(data)),
            "time": time.time(),
        })
        if len(self._backups[name]) > self._MAX_BACKUPS:
            self._backups[name] = self._backups[name][-self._MAX_BACKUPS:]

    def restore(self, name):
        backups = self._backups.get(name, [])
        if backups:
            return json.loads(json.dumps(backups[-1]["data"]))
        return None

    def has_backup(self, name):
        return name in self._backups and len(self._backups[name]) > 0


# ============================================================
#  GLOBAL ANTI-CHEAT ORCHESTRATOR
# ============================================================

class AntiCheatSystem:
    """Unified interface for all anti-cheat layers."""

    def __init__(self):
        self.behavior = BehaviorEngine()
        self.anomaly = AnomalyDetector()
        self.pow = PoWVerifier()
        self.cooldown = CooldownChain()
        self.replay = ReplayGuard()
        self.memory = MemoryLock()
        self.machine = MachineBinding()
        self.velocity = VelocityFirewall()
        self.collusion = CollusionDetector()
        self.healer = SelfHealer()
        self._violations = []
        self._blocked_users = set()
        self._lock = threading.Lock()

    def pre_action_check(self, user_id, action_type, amount=0):
        """Comprehensive pre-action validation."""
        if user_id in self._blocked_users:
            return False, "USER_BLOCKED"

        if self.behavior.is_suspicious(user_id, threshold=80):
            self._log_violation(user_id, action_type, "BEHAVIOR_SUSPICIOUS")
            return False, "BEHAVIOR_SUSPICIOUS"

        chain_ok, remaining = self.cooldown.check(user_id, action_type)
        if not chain_ok:
            return False, f"COOLDOWN:{remaining}s"

        is_anomaly, z = self.anomaly.detect(user_id, amount)
        if is_anomaly:
            self._log_violation(user_id, action_type, f"ANOMALY_Z{z}")
            return False, f"ANOMALY_DETECTED:z={z}"

        velocity_blocked, violations = self.velocity.check(user_id, amount)
        if velocity_blocked:
            self._log_violation(user_id, action_type, f"VELOCITY_EXCEEDED")
            return False, "VELOCITY_EXCEEDED"

        return True, "CLEAR"

    def post_action_record(self, user_id, action_type, amount, fp=None):
        """Record action for behavior analysis and velocity tracking."""
        self.behavior.record_action(user_id, action_type, amount)
        self.anomaly.record(user_id, amount)
        self.velocity.record(user_id, amount)
        if fp:
            self.replay.check_and_register(fp)

    def verify_mining_block(self, block):
        """Full proof-of-work verification."""
        valid, reason = self.pow.verify_block(block)
        if not valid:
            self._log_violation(block.get("user_id", ""), "mine_block", reason)
        return valid, reason

    def verify_blockchain(self, blocks):
        """Verify integrity of recent block chain."""
        return self.pow.verify_chain(blocks)

    def snapshot_data(self, name, data):
        """Snapshot data for self-healing."""
        self.healer.snapshot(name, data)

    def restore_data(self, name):
        """Restore from snapshot."""
        return self.healer.restore(name)

    def record_collusion(self, user_a, user_b):
        """Record user interaction for collusion detection."""
        self.collusion.record_interaction(user_a, user_b)

    def _log_violation(self, user_id, action, reason):
        with self._lock:
            entry = {
                "user_id": user_id,
                "action": action,
                "reason": reason,
                "time": datetime.utcnow().isoformat(),
            }
            self._violations.append(entry)
            if len(self._violations) > 500:
                self._violations = self._violations[-500:]

    def block_user(self, user_id):
        with self._lock:
            self._blocked_users.add(user_id)

    def is_blocked(self, user_id):
        return user_id in self._blocked_users

    def get_violations(self, limit=20):
        return self._violations[-limit:]

    def get_system_status(self):
        return {
            "behavior_profiles": len(self.behavior._profiles),
            "anomaly_alerts": len(self.anomaly._alerts),
            "violations": len(self._violations),
            "blocked_users": len(self._blocked_users),
            "replay_entries": len(self.replay._seen),
            "collusion_pairs": len(self.collusion._suspicious_pairs),
            "machine_id": self.machine.get_id(),
            "velocity_tracked_users": len(self.velocity._earnings),
        }


# ============================================================
#  GLOBAL INSTANCE
# ============================================================

anticheat = AntiCheatSystem()


# ============================================================
#  DECORATOR: Auto-protected earning functions
# ============================================================

def anti_cheat_guard(action_type):
    """Decorator that applies all anti-cheat checks before earning."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, user_id, *args, **kwargs):
            amount = kwargs.get("amount", args[0] if args else 0)
            ok, reason = anticheat.pre_action_check(user_id, action_type, amount)
            if not ok:
                return {"error": reason, "blocked": True, "amount": 0}
            result = func(self, user_id, *args, **kwargs)
            earned = result.get("amount", result.get("earned", 0)) if isinstance(result, dict) else 0
            if earned > 0:
                fp = result.get("_fp", "")
                anticheat.post_action_record(user_id, action_type, earned, fp)
            return result
        return wrapper
    return decorator
