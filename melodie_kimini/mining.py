"""
CRYPTO MINING & EARNING SYSTEM
Legal Positive Impact Mining for MA Tokens
Protected by VaultLock, rate limiting, and proof-of-work verification.
"""

import os
import json
import time
import random
import hashlib
import struct
from datetime import datetime

from .security import (
    secure_load, secure_save, can_earn, validate_earn,
    make_fingerprint, check_replay, is_debugged, get_tamper_log,
    compute_earn, BalanceGuard,
)
from .anticheat import anticheat

DATA_DIR = os.path.join(os.getcwd(), "data", "mining")
os.makedirs(DATA_DIR, exist_ok=True)

MINING_FILE = os.path.join(DATA_DIR, "mining.json")

MINING_POOLS = {
    "karma_pool":      {"hashrate": 100, "reward_rate": 0.5, "desc": "Karma Contribution Mining"},
    "education_pool":  {"hashrate": 80,  "reward_rate": 0.6, "desc": "Education Impact Mining"},
    "green_pool":      {"hashrate": 90,  "reward_rate": 0.55,"desc": "Green Impact Mining"},
    "community_pool":  {"hashrate": 70,  "reward_rate": 0.7, "desc": "Community Service Mining"},
    "research_pool":   {"hashrate": 60,  "reward_rate": 0.8, "desc": "Research Contribution Mining"},
    "innovation_pool": {"hashrate": 50,  "reward_rate": 0.9, "desc": "Innovation Mining"},
}

DIFFICULTY_LEVELS = {
    "easy":   {"multiplier": 1.0, "chance": 0.9},
    "medium": {"multiplier": 1.5, "chance": 0.6},
    "hard":   {"multiplier": 2.5, "chance": 0.3},
    "extreme":{"multiplier": 5.0, "chance": 0.1},
}

_POOL_HASH = None
def _verify_pool_constants():
    global _POOL_HASH
    raw = json.dumps(MINING_POOLS, sort_keys=True, separators=(",", ":"))
    h = hashlib.sha256(raw.encode()).hexdigest()
    if _POOL_HASH is not None and _POOL_HASH != h:
        from .security import _TamperLog
        _TamperLog.record("mining", "POOL_CONSTANTS_TAMPERED")
        return False
    _POOL_HASH = h
    return True

_verify_pool_constants()


def _load_mining():
    return secure_load(MINING_FILE, lambda: {
        "miners": {}, "blocks": [],
        "stats": {"total_mined": 0, "total_blocks": 0}
    })

def _save_mining(data):
    secure_save(MINING_FILE, data)


class MiningEngine:
    """Simulates legal positive impact crypto mining."""

    def __init__(self):
        self.data = _load_mining()

    def start_mining(self, user_id, pool="karma_pool", difficulty="medium"):
        if is_debugged():
            return {"error": "Debugger detected"}
        pre_ok, pre_reason = anticheat.pre_action_check(user_id, "mining_start", 0)
        if not pre_ok:
            return {"error": pre_reason}
        if not can_earn("mining_start", min_interval=2.0, max_per_min=10):
            return {"error": "Rate limited"}
        if pool not in MINING_POOLS:
            return None
        pool_cfg = MINING_POOLS[pool]
        diff_cfg = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["medium"])

        if user_id not in self.data["miners"]:
            self.data["miners"][user_id] = {
                "active": False, "pool": None, "difficulty": None,
                "started": None, "total_mined": 0, "blocks_found": 0, "sessions": 0,
            }

        miner = self.data["miners"][user_id]
        miner["active"] = True
        miner["pool"] = pool
        miner["difficulty"] = difficulty
        miner["started"] = datetime.utcnow().isoformat()
        miner["sessions"] += 1
        _save_mining(self.data)

        return {
            "user_id": user_id, "pool": pool, "pool_desc": pool_cfg["desc"],
            "difficulty": difficulty, "multiplier": diff_cfg["multiplier"],
            "hashrate": pool_cfg["hashrate"], "reward_rate": pool_cfg["reward_rate"],
            "chance": diff_cfg["chance"], "status": "mining",
        }

    def mine_block(self, user_id):
        if is_debugged():
            return {"status": "blocked", "earned": 0, "reason": "debugger"}

        pre_ok, pre_reason = anticheat.pre_action_check(user_id, "mine_block", 0)
        if not pre_ok:
            return {"status": "blocked", "earned": 0, "reason": pre_reason}

        miner = self.data["miners"].get(user_id, {})
        if not miner.get("active"):
            return {"status": "not_mining", "earned": 0}

        if not can_earn(f"mine:{user_id}", min_interval=1.0, max_per_min=30):
            return {"status": "rate_limited", "earned": 0}

        pool = miner.get("pool", "karma_pool")
        difficulty = miner.get("difficulty", "medium")
        pool_cfg = MINING_POOLS.get(pool, MINING_POOLS["karma_pool"])
        diff_cfg = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["medium"])

        block_seed = int(time.time() * 1000)
        nonce = block_seed ^ (hash(user_id) & 0xFFFFFFFF)
        proof = hashlib.sha256(
            struct.pack(">Q", nonce) + user_id.encode() + pool.encode()
        ).hexdigest()

        target_prefix = "0" * max(1, int(diff_cfg["chance"] * 6))
        success = proof.startswith(target_prefix)

        if success:
            base_reward = compute_earn(
                pool_cfg["reward_rate"], diff_cfg["multiplier"], 1.0, nonce % 997
            )
            bonus_seed = int(proof[:8], 16) % 100
            bonus = 1.0 + (bonus_seed / 100.0)
            reward = round(base_reward * bonus, 4)

            validated, reason = validate_earn(reward, 0, 0, "mine_block")
            if reason != "OK":
                reward = validated

            fp = make_fingerprint(user_id, "mine_block", reward, block_seed)
            if check_replay(fp):
                return {"status": "replay_blocked", "earned": 0}

            block = {
                "user_id": user_id, "pool": pool, "difficulty": difficulty,
                "reward": reward, "proof": proof, "nonce": nonce,
                "timestamp": datetime.utcnow().isoformat(), "_fp": fp,
            }
            self.data["blocks"].append(block)
            if len(self.data["blocks"]) > 500:
                self.data["blocks"] = self.data["blocks"][-500:]

            miner["total_mined"] = round(miner["total_mined"] + reward, 4)
            miner["blocks_found"] += 1
            self.data["stats"]["total_mined"] = round(
                self.data["stats"]["total_mined"] + reward, 4
            )
            self.data["stats"]["total_blocks"] += 1
            _save_mining(self.data)
            return {"status": "success", "earned": reward, "block": block}
        else:
            return {"status": "no_block", "earned": 0}

    def stop_mining(self, user_id):
        miner = self.data["miners"].get(user_id, {})
        if miner.get("active"):
            miner["active"] = False
            _save_mining(self.data)
        return {"status": "stopped", "total_mined": miner.get("total_mined", 0)}

    def get_miner_stats(self, user_id):
        return self.data["miners"].get(user_id, {
            "active": False, "pool": None, "difficulty": None,
            "started": None, "total_mined": 0, "blocks_found": 0, "sessions": 0,
        })

    def get_pool_stats(self):
        pool_activity = {}
        for block in self.data["blocks"][-100:]:
            p = block["pool"]
            if p not in pool_activity:
                pool_activity[p] = {"blocks": 0, "total_reward": 0}
            pool_activity[p]["blocks"] += 1
            pool_activity[p]["total_reward"] = round(
                pool_activity[p]["total_reward"] + block["reward"], 4
            )
        result = {}
        for pid, cfg in MINING_POOLS.items():
            act = pool_activity.get(pid, {"blocks": 0, "total_reward": 0})
            result[pid] = {**cfg, **act}
        return result

    def get_global_stats(self):
        return self.data["stats"]

    def get_recent_blocks(self, limit=20):
        return self.data["blocks"][-limit:]

    def estimate_session(self, user_id, duration_minutes=5):
        miner = self.data["miners"].get(user_id, {})
        pool = miner.get("pool", "karma_pool")
        difficulty = miner.get("difficulty", "medium")
        pool_cfg = MINING_POOLS.get(pool, MINING_POOLS["karma_pool"])
        diff_cfg = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["medium"])

        blocks_per_minute = pool_cfg["hashrate"] / 1000.0
        total_blocks = int(duration_minutes * blocks_per_minute)
        successful = int(total_blocks * diff_cfg["chance"])
        avg_reward = pool_cfg["reward_rate"] * diff_cfg["multiplier"]
        estimated = round(successful * avg_reward, 2)

        return {
            "duration": duration_minutes,
            "expected_blocks": total_blocks,
            "expected_success": successful,
            "estimated_earn": estimated,
        }
