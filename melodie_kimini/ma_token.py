"""
MA TOKENS - Utility Token System
Converts Karma Power Points to Cryptocurrency
Protected by VaultLock integrity, rate limiting, and balance guards.
"""

import os
import json
import time
from datetime import datetime

from .security import (
    secure_load, secure_save, can_earn, validate_earn, validate_stake,
    make_fingerprint, check_replay, is_debugged, get_tamper_log,
    compute_earn, compute_daily,
    BalanceGuard,
)
from .anticheat import anticheat

DATA_DIR = os.path.join(os.getcwd(), "data", "tokens")
os.makedirs(DATA_DIR, exist_ok=True)

WALLET_FILE = os.path.join(DATA_DIR, "wallets.json")

# ============================================================
#  TOKEN ECONOMICS
# ============================================================

TOKEN_NAME = "MA"
TOKEN_FULL = "Melodie-Kimini Action Token"
CONVERSION_RATE = 10.0
MAX_DAILY_EARN = 500.0
MIN_WITHDRAW = 50.0
STAKING_APY = 0.12

CATEGORIES = {
    "prompt_earn":       {"rate": 1.0,  "desc": "Positive Prompt Usage"},
    "karma_convert":     {"rate": 0.1,  "desc": "Karma Point Conversion"},
    "referral":          {"rate": 5.0,  "desc": "Referral Bonus"},
    "streak_bonus":      {"rate": 2.0,  "desc": "Daily Streak Bonus"},
    "milestone":         {"rate": 10.0, "desc": "Milestone Achievement"},
    "community_vote":    {"rate": 3.0,  "desc": "Community Governance Vote"},
    "leaderboard":       {"rate": 7.5,  "desc": "Leaderboard Ranking Reward"},
    "staking_reward":    {"rate": 0.0,  "desc": "Staking APY Reward"},
    "project_fund":      {"rate": -5.0, "desc": "Project Funding Deduction"},
    "penalty":           {"rate": -10.0,"desc": "Negative Impact Penalty"},
}

# Integrity hash for category constants
_CAT_HASH = None
def _verify_categories():
    global _CAT_HASH
    raw = json.dumps(CATEGORIES, sort_keys=True, separators=(",", ":"))
    h = __import__("hashlib").sha256(raw.encode()).hexdigest()
    if _CAT_HASH is not None and _CAT_HASH != h:
        from .security import _TamperLog
        _TamperLog.record("ma_token", "CATEGORIES_TAMPERED")
        return False
    _CAT_HASH = h
    return True

_verify_categories()


def _load_wallets():
    return secure_load(WALLET_FILE, lambda: {
        "wallets": {}, "transactions": [],
        "global": {"total_supply": 0, "total_staked": 0}
    })

def _save_wallets(data):
    secure_save(WALLET_FILE, data)


class MATokenWallet:
    """Manages MA Token wallets, earning, staking, and conversion."""

    def __init__(self):
        self.data = _load_wallets()

    def get_wallet(self, user_id="default"):
        if user_id not in self.data["wallets"]:
            self.data["wallets"][user_id] = {
                "balance": 0.0,
                "staked": 0.0,
                "total_earned": 0.0,
                "total_spent": 0.0,
                "daily_earned": 0.0,
                "daily_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "streak": 0,
                "last_active": None,
                "transactions": 0,
            }
            _save_wallets(self.data)
        return self.data["wallets"][user_id]

    def earn(self, user_id, category, amount, source_desc=""):
        if is_debugged():
            return {"error": "Debugger detected", "amount": 0}

        pre_ok, pre_reason = anticheat.pre_action_check(user_id, f"earn:{category}", amount)
        if not pre_ok:
            return {"error": pre_reason, "amount": 0}

        if not can_earn(f"earn:{category}", min_interval=0.3, max_per_min=60):
            return {"error": "Rate limited", "amount": 0}

        fp = make_fingerprint(user_id, category, amount, time.time())
        if check_replay(fp):
            return {"error": "Replay detected", "amount": 0}

        _verify_categories()

        wallet = self.get_wallet(user_id)
        today = datetime.utcnow().strftime("%Y-%m-%d")

        if wallet["daily_date"] != today:
            wallet["daily_date"] = today
            wallet["daily_earned"] = 0.0

        cat = CATEGORIES.get(category, {"rate": 1.0, "desc": "Unknown"})

        if amount < 0:
            earned = amount * cat["rate"]
            penalty = abs(earned)
            wallet["balance"] = max(0, wallet["balance"] - penalty)
            wallet["total_spent"] += penalty
        else:
            earned = compute_earn(amount, cat["rate"], 1.0, hash(category) % 997)
            validated, reason = validate_earn(
                earned, wallet["daily_earned"], wallet["balance"], f"earn:{category}"
            )
            if reason != "OK":
                earned = validated
            wallet["balance"] += earned
            wallet["total_earned"] += earned
            wallet["daily_earned"] += earned

        wallet["transactions"] += 1

        prev_active = wallet.get("last_active")
        if prev_active:
            prev_date = datetime.fromisoformat(prev_active).strftime("%Y-%m-%d")
            if prev_date < today:
                delta = (datetime.utcnow() - datetime.fromisoformat(prev_active)).days
                if delta == 1:
                    wallet["streak"] += 1
                elif delta > 1:
                    wallet["streak"] = 1
        else:
            wallet["streak"] = 1
        wallet["last_active"] = datetime.utcnow().isoformat()

        tx = {
            "user_id": user_id,
            "category": category,
            "amount": round(earned, 4),
            "balance_after": round(wallet["balance"], 4),
            "desc": source_desc or cat["desc"],
            "timestamp": datetime.utcnow().isoformat(),
            "_fp": fp,
        }
        self.data["transactions"].append(tx)
        if len(self.data["transactions"]) > 2000:
            self.data["transactions"] = self.data["transactions"][-2000:]

        self.data["global"]["total_supply"] = round(
            self.data["global"]["total_supply"] + max(earned, 0), 4
        )
        _save_wallets(self.data)
        return tx

    def convert_karma(self, user_id, karma_points):
        ma_earned = karma_points * CONVERSION_RATE
        return self.earn(user_id, "karma_convert", ma_earned, f"{karma_points} karma points")

    def stake(self, user_id, amount):
        if is_debugged():
            return {"error": "Debugger detected"}
        wallet = self.get_wallet(user_id)
        validated, reason = validate_stake(amount, wallet["balance"])
        if reason != "OK":
            return {"error": reason, "staked": 0}
        wallet["balance"] -= validated
        wallet["staked"] += validated
        self.data["global"]["total_staked"] += validated
        _save_wallets(self.data)
        return {"staked": validated, "balance": wallet["balance"]}

    def unstake(self, user_id, amount):
        if is_debugged():
            return {"error": "Debugger detected"}
        wallet = self.get_wallet(user_id)
        if amount <= 0 or amount > wallet["staked"]:
            return None
        wallet["staked"] -= amount
        wallet["balance"] += amount
        self.data["global"]["total_staked"] -= amount
        _save_wallets(self.data)
        return {"unstaked": amount, "balance": wallet["balance"]}

    def calc_staking_reward(self, user_id):
        wallet = self.get_wallet(user_id)
        if wallet["staked"] <= 0:
            return 0.0
        daily_rate = STAKING_APY / 365.0
        return round(wallet["staked"] * daily_rate, 4)

    def get_balance(self, user_id="default"):
        return self.get_wallet(user_id)["balance"]

    def get_staked(self, user_id="default"):
        return self.get_wallet(user_id)["staked"]

    def get_streak(self, user_id="default"):
        return self.get_wallet(user_id)["streak"]

    def get_transactions(self, user_id=None, limit=20):
        txs = self.data["transactions"]
        if user_id:
            txs = [t for t in txs if t["user_id"] == user_id]
        return txs[-limit:]

    def get_global(self):
        return self.data["global"]

    def estimate_daily_earn(self, user_id="default"):
        wallet = self.get_wallet(user_id)
        base = 15.0
        return compute_daily(base, wallet["streak"], wallet["staked"], STAKING_APY)
