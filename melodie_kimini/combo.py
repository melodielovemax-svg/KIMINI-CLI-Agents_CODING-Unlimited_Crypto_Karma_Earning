"""
COMBO POSITIVE IMPACT SCORER + ASCENSION RANK SYSTEM
Gaming-style multiplier combos with divine rank progression.

Combo System:
  Consecutive positive actions build combo multiplier: 1x -> 1.5x -> 2x -> 3x -> 5x -> 10x
  Missing a day or negative action resets combo. Combo tiers: NONE > BRONZE > SILVER > GOLD > PLATINUM > DIAMOND > LEGENDARY > MYTHIC

Ascension Ranks:
  Mortal -> Acolyte -> Monk -> Sage -> Buddha -> Demigod -> God -> Archangel -> Seraphim -> Cosmic Overlord

Visual Effects:
  Gaming-style combo counters, rank-up animations, % multiplier displays,
  glowing bars, particle-style text, achievement popups.
"""

import os
import json
import time
import math
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.getcwd(), "data", "combo")
os.makedirs(DATA_DIR, exist_ok=True)

COMBO_FILE = os.path.join(DATA_DIR, "combo.json")


# ============================================================
#  COMBO TIER DEFINITIONS
# ============================================================

COMBO_TIERS = {
    0:   {"name": "NONE",       "color": "dim",          "mult": 1.0,  "bar": "....................", "glow": ""},
    5:   {"name": "BRONZE",     "color": "yellow",       "mult": 1.25, "bar": "#####...............", "glow": "**"},
    15:  {"name": "SILVER",     "color": "white",        "mult": 1.5,  "bar": "#########...........", "glow": "**+"},
    30:  {"name": "GOLD",       "color": "bright_yellow","mult": 2.0,  "bar": "###############.....", "glow": "**+"},
    50:  {"name": "PLATINUM",   "color": "bright_cyan",  "mult": 3.0,  "bar": "###################.", "glow": "***"},
    75:  {"name": "DIAMOND",    "color": "bright_magenta","mult": 5.0,  "bar": "####################", "glow": "****"},
    100: {"name": "LEGENDARY",  "color": "bright_red",   "mult": 7.5,  "bar": "####################", "glow": "*****"},
    150: {"name": "MYTHIC",     "color": "bright_green", "mult": 10.0, "bar": "####################", "glow": "*******"},
}


def get_combo_tier(combo_count):
    tier = COMBO_TIERS[0]
    for threshold, info in sorted(COMBO_TIERS.items()):
        if combo_count >= threshold:
            tier = info
    return tier


# ============================================================
#  ASCENSION RANK DEFINITIONS
# ============================================================

ASCENSION_RANKS = [
    {"min_karma": 0,       "name": "Mortal",         "icon": "--",  "color": "dim",          "title": "Unawakened Soul",         "bonus_mult": 1.0,   "next": 50},
    {"min_karma": 50,      "name": "Acolyte",        "icon": ">>",  "color": "white",        "title": "Seeker of Light",         "bonus_mult": 1.1,   "next": 150},
    {"min_karma": 150,     "name": "Monk",           "icon": "[]",  "color": "bright_white", "title": "Keeper of Harmony",       "bonus_mult": 1.2,   "next": 400},
    {"min_karma": 400,     "name": "Sage",           "icon": "##",  "color": "bright_cyan",  "title": "Wise Pathfinder",         "bonus_mult": 1.35,  "next": 800},
    {"min_karma": 800,     "name": "Buddha",         "icon": "**",  "color": "bright_yellow","title": "Enlightened One",         "bonus_mult": 1.5,   "next": 1500},
    {"min_karma": 1500,    "name": "Demigod",        "icon": "@@",  "color": "bright_magenta","title": "Between Worlds",         "bonus_mult": 1.75,  "next": 3000},
    {"min_karma": 3000,    "name": "God",            "icon": "##+", "color": "bright_red",   "title": "Divine Architect",        "bonus_mult": 2.0,   "next": 6000},
    {"min_karma": 6000,    "name": "Archangel",      "icon": "??+", "color": "bright_green", "title": "Heaven's Champion",       "bonus_mult": 2.5,   "next": 12000},
    {"min_karma": 12000,   "name": "Seraphim",       "icon": "**+", "color": "bright_white", "title": "Six-Winged Sovereign",    "bonus_mult": 3.0,   "next": 25000},
    {"min_karma": 25000,   "name": "Cosmic Overlord","icon": "##++","color": "bright_yellow","title": "Master of the Universe",  "bonus_mult": 5.0,   "next": None},
]


def get_ascension_rank(karma):
    rank = ASCENSION_RANKS[0]
    for r in ASCENSION_RANKS:
        if karma >= r["min_karma"]:
            rank = r
    return rank


def get_next_rank(karma):
    for r in ASCENSION_RANKS:
        if karma < r["min_karma"]:
            return r
    return None


# ============================================================
#  COMBO ENGINE
# ============================================================

class ComboEngine:
    """Manages combo streaks, multipliers, and rank progression."""

    def __init__(self):
        self.data = self._load()

    def _load(self):
        path = COMBO_FILE
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {"users": {}, "global": {"total_combos": 0, "max_combo_ever": 0}}

    def _save(self):
        with open(COMBO_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def _get_user(self, user_id):
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "combo": 0,
                "max_combo": 0,
                "last_action_date": None,
                "total_positive": 0,
                "total_negative": 0,
                "current_tier": "NONE",
                "current_rank": "Mortal",
                "rank_ups": [],
                "combo_resets": 0,
                "total_bonus_earned": 0.0,
                "achievements": [],
            }
        return self.data["users"][user_id]

    def record_positive(self, user_id, base_amount, karma_score=0):
        user = self._get_user(user_id)
        today = datetime.utcnow().strftime("%Y-%m-%d")

        if user["last_action_date"]:
            last = datetime.strptime(user["last_action_date"], "%Y-%m-%d")
            delta = (datetime.utcnow() - last).days
            if delta > 1:
                user["combo"] = 0
                user["combo_resets"] += 1
            elif delta == 0:
                pass
            else:
                user["combo"] += 1
        else:
            user["combo"] = 1

        user["last_action_date"] = today
        user["total_positive"] += 1
        if user["combo"] > user["max_combo"]:
            user["max_combo"] = user["combo"]

        tier = get_combo_tier(user["combo"])
        user["current_tier"] = tier["name"]
        multiplier = tier["mult"]

        rank = get_ascension_rank(karma_score)
        prev_rank = user["current_rank"]
        user["current_rank"] = rank["name"]
        if prev_rank != rank["name"]:
            user["rank_ups"].append({
                "from": prev_rank, "to": rank["name"],
                "time": datetime.utcnow().isoformat(),
            })

        bonus = round(base_amount * (multiplier - 1.0), 4)
        total_with_bonus = round(base_amount + bonus, 4)

        achievements = self._check_achievements(user, karma_score)
        for a in achievements:
            if a not in user["achievements"]:
                user["achievements"].append(a)

        self.data["global"]["total_combos"] += 1
        if user["combo"] > self.data["global"]["max_combo_ever"]:
            self.data["global"]["max_combo_ever"] = user["combo"]

        self._save()

        return {
            "combo": user["combo"],
            "tier": tier["name"],
            "tier_color": tier["color"],
            "multiplier": multiplier,
            "glow": tier["glow"],
            "bar": tier["bar"],
            "bonus_earned": bonus,
            "total_earned": total_with_bonus,
            "rank": rank["name"],
            "rank_icon": rank["icon"],
            "rank_color": rank["color"],
            "rank_title": rank["title"],
            "rank_bonus": rank["bonus_mult"],
            "rank_up": prev_rank != rank["name"],
            "prev_rank": prev_rank,
            "achievements": achievements,
        }

    def record_negative(self, user_id):
        user = self._get_user(user_id)
        old_combo = user["combo"]
        user["combo"] = 0
        user["total_negative"] += 1
        user["combo_resets"] += 1
        user["last_action_date"] = datetime.utcnow().strftime("%Y-%m-%d")
        user["current_tier"] = "NONE"
        self._save()
        return {
            "combo_broken": old_combo,
            "was_tier": get_combo_tier(old_combo)["name"],
        }

    def _check_achievements(self, user, karma):
        a = []
        combo = user["combo"]
        if combo >= 5:
            a.append("Combo Starter")
        if combo >= 15:
            a.append("Combo Warrior")
        if combo >= 30:
            a.append("Combo Master")
        if combo >= 50:
            a.append("Combo Legend")
        if combo >= 100:
            a.append("Combo God")
        if combo >= 150:
            a.append("Combo Mythic")
        rank = get_ascension_rank(karma)
        if rank["name"] in ["Buddha", "Demigod", "God", "Archangel", "Seraphim", "Cosmic Overlord"]:
            a.append(f"Rank: {rank['name']}")
        if user["total_positive"] >= 100:
            a.append("Century of Good")
        if user["max_combo"] >= 50:
            a.append("Unbreakable Streak")
        return a

    def get_user(self, user_id):
        user = self._get_user(user_id)
        combo = user["combo"]
        tier = get_combo_tier(combo)
        return {
            "user_id": user_id,
            "combo": combo,
            "max_combo": user["max_combo"],
            "tier": tier["name"],
            "tier_color": tier["color"],
            "multiplier": tier["mult"],
            "bar": tier["bar"],
            "glow": tier["glow"],
            "current_rank": user["current_rank"],
            "total_positive": user["total_positive"],
            "total_negative": user["total_negative"],
            "combo_resets": user["combo_resets"],
            "achievements": user["achievements"],
            "rank_ups": user["rank_ups"][-5:],
        }

    def get_global_stats(self):
        return self.data["global"]

    def get_top_combos(self, limit=10):
        users = []
        for uid, data in self.data["users"].items():
            tier = get_combo_tier(data["combo"])
            users.append({
                "user_id": uid,
                "combo": data["combo"],
                "tier": tier["name"],
                "rank": data["current_rank"],
                "max_combo": data["max_combo"],
            })
        users.sort(key=lambda x: x["combo"], reverse=True)
        return users[:limit]

    def get_leaderboard(self, limit=30):
        users = []
        for uid, data in self.data["users"].items():
            rank = get_ascension_rank(0)
            users.append({
                "user_id": uid,
                "rank": data["current_rank"],
                "combo": data["combo"],
                "tier": data["current_tier"],
                "total_positive": data["total_positive"],
                "max_combo": data["max_combo"],
            })
        rank_order = {r["name"]: i for i, r in enumerate(ASCENSION_RANKS)}
        users.sort(key=lambda x: (rank_order.get(x["rank"], 0), x["combo"]), reverse=True)
        return users[:limit]
