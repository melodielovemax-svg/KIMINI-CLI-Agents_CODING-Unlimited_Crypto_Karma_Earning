"""
KARMA POWER POINTS ENGINE
Positive Impact Scoring System for Global Good
Protected by VaultLock integrity verification.
"""

import os
import json
import time
from datetime import datetime

from .security import (
    secure_load, secure_save, can_earn, validate_earn,
    make_fingerprint, check_replay, is_debugged, get_tamper_log,
    compute_earn, BalanceGuard,
)
from .anticheat import anticheat

DATA_DIR = os.path.join(os.getcwd(), "data", "karma")
os.makedirs(DATA_DIR, exist_ok=True)

DB_FILE = os.path.join(DATA_DIR, "karma.json")

# ============================================================
#  KARMA SCORING DIMENSIONS
# ============================================================

IMPACT_DIMENSIONS = {
    "education":       {"weight": 1.5, "icon": "EDU", "desc": "Learning & Knowledge"},
    "health":          {"weight": 1.4, "icon": "HLT", "desc": "Health & Wellness"},
    "environment":     {"weight": 1.3, "icon": "ENV", "desc": "Environmental Care"},
    "community":       {"weight": 1.2, "icon": "COM", "desc": "Community Service"},
    "innovation":      {"weight": 1.1, "icon": "INN", "desc": "Tech Innovation"},
    "arts":            {"weight": 1.0, "icon": "ART", "desc": "Arts & Culture"},
    "charity":         {"weight": 1.3, "icon": "CHT", "desc": "Charity & Giving"},
    "sustainability":  {"weight": 1.2, "icon": "SUS", "desc": "Sustainability"},
    "research":        {"weight": 1.1, "icon": "RES", "desc": "Scientific Research"},
    "mentorship":      {"weight": 1.0, "icon": "MNT", "desc": "Mentorship & Guidance"},
    "open_source":     {"weight": 0.9, "icon": "OSS", "desc": "Open Source Contribution"},
    "accessibility":   {"weight": 1.0, "icon": "ACC", "desc": "Accessibility & Inclusion"},
}

POSITIVE_KEYWORDS = {
    "education":     ["learn", "teach", "study", "course", "tutorial", "knowledge", "school", "university", "book", "read"],
    "health":        ["health", "wellness", "medical", "cure", "therapy", "exercise", "nutrition", "mental health"],
    "environment":   ["plant", "recycle", "renewable", "carbon", "green", "clean", "ocean", "forest", "wildlife"],
    "community":     ["volunteer", "community", "help", "support", "neighbor", "local", "together", "serve"],
    "innovation":    ["invent", "create", "build", "design", "develop", "prototype", "solution", "engineer"],
    "arts":          ["art", "music", "paint", "write", "poetry", "theater", "design", "creative"],
    "charity":       ["donate", "give", "fund", "charity", "nonprofit", "aid", "relief", "sponsor"],
    "sustainability":["sustainable", "eco", "organic", "zero waste", "compost", "energy efficient"],
    "research":      ["research", "study", "experiment", "discover", "analyze", "investigate"],
    "mentorship":    ["mentor", "guide", "coach", "teach", "lead", "inspire", "empower"],
    "open_source":   ["open source", "contribute", "collaborate", "share", "public", "free"],
    "accessibility": ["accessible", "inclusive", "disability", "universal", "equitable", "diverse"],
}

NEGATIVE_KEYWORDS = {
    "harm":         ["harm", "hurt", "damage", "destroy", "attack", "violence", "hate"],
    "waste":        ["waste", "pollute", "litter", "destroy", "dump", "contaminate"],
    "fraud":        ["scam", "fraud", "steal", "cheat", "deceive", "fake", "counterfeit"],
    "exploitation": ["exploit", "abuse", "manipulate", "bully", "harass", "discriminate"],
    "illegal":      ["illegal", "unlawful", "criminal", "smuggle", "pirate"],
}

# Attempt to tamper with these constants is detected
_CONST_HASH = None
def _verify_constants():
    global _CONST_HASH
    raw = json.dumps(IMPACT_DIMENSIONS, sort_keys=True, separators=(",", ":"))
    h = __import__("hashlib").sha256(raw.encode()).hexdigest()
    if _CONST_HASH is not None and _CONST_HASH != h:
        from .security import _TamperLog
        _TamperLog.record("karma", "CONSTANTS_TAMPERED")
        return False
    _CONST_HASH = h
    return True

_verify_constants()


def _load_db():
    return secure_load(DB_FILE, lambda: {
        "users": {}, "sessions": [],
        "global_stats": {"total_karma": 0, "total_prompts": 0}
    })

def _save_db(db):
    secure_save(DB_FILE, db)


# ============================================================
#  KARMA SCORER
# ============================================================

class KarmaScorer:
    """Evaluates prompts and assigns karma power points."""

    def __init__(self):
        self.db = _load_db()

    def score_prompt(self, prompt, user_id="default"):
        if is_debugged():
            return {"error": "Debugger detected", "score": 0}

        pre_ok, pre_reason = anticheat.pre_action_check(user_id, "karma_score", len(prompt))
        if not pre_ok:
            return {"error": pre_reason, "score": 0}

        if not can_earn("karma_score", min_interval=0.5, max_per_min=60):
            return {"error": "Rate limited", "score": 0}

        fp = make_fingerprint(user_id, "karma", len(prompt), time.time())
        if check_replay(fp):
            return {"error": "Replay detected", "score": 0}

        _verify_constants()

        prompt_lower = prompt.lower()
        dimensions = {}
        total_score = 0
        is_positive = False
        is_negative = False

        for dim, config in IMPACT_DIMENSIONS.items():
            keywords = POSITIVE_KEYWORDS.get(dim, [])
            matches = sum(1 for kw in keywords if kw in prompt_lower)
            if matches > 0:
                score = matches * config["weight"] * 10
                dimensions[dim] = {
                    "score": round(score, 2),
                    "icon": config["icon"],
                    "desc": config["desc"],
                    "matches": matches,
                }
                total_score += score
                is_positive = True

        for category, keywords in NEGATIVE_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in prompt_lower)
            if matches > 0:
                penalty = matches * 15
                total_score -= penalty
                is_negative = True
                dimensions[f"neg_{category}"] = {
                    "score": -penalty,
                    "icon": "!!!",
                    "desc": f"Negative: {category}",
                    "matches": matches,
                }

        if not is_positive and not is_negative:
            base_score = 1.0
            total_score = base_score
            dimensions["general"] = {
                "score": base_score,
                "icon": "GEN",
                "desc": "General Usage",
                "matches": 1,
            }

        total_score = round(max(total_score, -100), 2)

        user = self.db["users"].get(user_id, {"karma": 0})
        validated, reason = validate_earn(
            total_score if total_score > 0 else 0,
            0,
            user.get("karma", 0),
            "karma_score"
        )
        if reason != "OK" and total_score > 0:
            total_score = validated

        result = {
            "user_id": user_id,
            "prompt": prompt[:100],
            "dimensions": dimensions,
            "total_score": total_score,
            "is_positive": is_positive,
            "is_negative": is_negative and total_score < 0,
            "timestamp": datetime.utcnow().isoformat(),
            "_fp": fp,
        }

        self._record_session(user_id, result)
        return result

    def _record_session(self, user_id, result):
        if user_id not in self.db["users"]:
            self.db["users"][user_id] = {
                "karma": 0,
                "total_sessions": 0,
                "positive_count": 0,
                "negative_count": 0,
                "level": 1,
                "title": "Beginner",
                "achievements": [],
            }

        user = self.db["users"][user_id]
        user["karma"] = round(user["karma"] + result["total_score"], 2)
        user["total_sessions"] += 1

        if result["is_positive"]:
            user["positive_count"] += 1
        if result["is_negative"]:
            user["negative_count"] += 1

        user["level"] = self._calc_level(user["karma"])
        user["title"] = self._get_title(user["karma"])

        achievements = self._check_achievements(user)
        for a in achievements:
            if a not in user["achievements"]:
                user["achievements"].append(a)

        self.db["global_stats"]["total_karma"] = round(
            self.db["global_stats"]["total_karma"] + result["total_score"], 2
        )
        self.db["global_stats"]["total_prompts"] += 1
        self.db["sessions"].append(result)
        if len(self.db["sessions"]) > 1000:
            self.db["sessions"] = self.db["sessions"][-1000:]

        _save_db(self.db)

    def _calc_level(self, karma):
        if karma >= 10000:
            return 10
        elif karma >= 5000:
            return 9
        elif karma >= 2500:
            return 8
        elif karma >= 1000:
            return 7
        elif karma >= 500:
            return 6
        elif karma >= 200:
            return 5
        elif karma >= 100:
            return 4
        elif karma >= 50:
            return 3
        elif karma >= 10:
            return 2
        return 1

    def _get_title(self, karma):
        titles = [
            (10000, "Cosmic Guardian"),
            (5000,  "Universal Sage"),
            (2500,  "Planetary Hero"),
            (1000,  "World Changer"),
            (500,   "Community Leader"),
            (200,   "Impact Maker"),
            (100,   "Positive Force"),
            (50,    "Good Spirit"),
            (10,    "Rising Star"),
            (0,     "Beginner"),
        ]
        for threshold, title in titles:
            if karma >= threshold:
                return title
        return "Beginner"

    def _check_achievements(self, user):
        achievements = []
        karma = user["karma"]
        sessions = user["total_sessions"]

        if sessions >= 1:
            achievements.append("First Prompt")
        if sessions >= 10:
            achievements.append("Dedicated User")
        if sessions >= 50:
            achievements.append("Power User")
        if sessions >= 100:
            achievements.append("Century Club")
        if karma >= 10:
            achievements.append("Karma Beginner")
        if karma >= 100:
            achievements.append("Karma Adept")
        if karma >= 500:
            achievements.append("Karma Master")
        if karma >= 1000:
            achievements.append("Karma Legend")
        if karma >= 5000:
            achievements.append("Karma God")
        if user["positive_count"] >= 20:
            achievements.append("Positive Champion")
        if user["negative_count"] == 0 and sessions >= 10:
            achievements.append("Pure Heart")
        return achievements

    def get_user(self, user_id="default"):
        return self.db["users"].get(user_id, {
            "karma": 0, "total_sessions": 0, "positive_count": 0,
            "negative_count": 0, "level": 1, "title": "Beginner", "achievements": [],
        })

    def get_global_stats(self):
        return self.db["global_stats"]

    def get_recent_sessions(self, limit=20):
        return self.db["sessions"][-limit:]
