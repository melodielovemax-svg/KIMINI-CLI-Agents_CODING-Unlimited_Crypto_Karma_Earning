"""
TIME-BASED EARNING ENGINE
Tracks session time and awards % bonus for extended usage.
The longer you use the platform, the more you earn.

Time Tiers:
  0-5 min:   Base rate (100%)
  5-15 min:  +10% bonus
  15-30 min: +25% bonus
  30-60 min: +50% bonus
  1-2 hours: +75% bonus
  2+ hours:  +100% bonus (double!)
  4+ hours:  +150% bonus (VIP!)

Session bonuses stack with combo multipliers and rank bonuses.
"""

import os
import json
import time
from datetime import datetime

DATA_DIR = os.path.join(os.getcwd(), "data", "time_earn")
os.makedirs(DATA_DIR, exist_ok=True)

SESSION_FILE = os.path.join(DATA_DIR, "sessions.json")

TIME_TIERS = [
    {"min_minutes": 0,    "max_minutes": 5,    "boost_pct": 0,    "label": "BASE",       "color": "dim"},
    {"min_minutes": 5,    "max_minutes": 15,   "boost_pct": 10,   "label": "ACTIVE",     "color": "white"},
    {"min_minutes": 15,   "max_minutes": 30,   "boost_pct": 25,   "label": "ENGAGED",    "color": "bright_cyan"},
    {"min_minutes": 30,   "max_minutes": 60,   "boost_pct": 50,   "label": "DEDICATED",  "color": "bright_green"},
    {"min_minutes": 60,   "max_minutes": 120,  "boost_pct": 75,   "label": "COMMITTED",  "color": "bright_yellow"},
    {"min_minutes": 120,  "max_minutes": 240,  "boost_pct": 100,  "label": "LEGENDARY",  "color": "bright_magenta"},
    {"min_minutes": 240,  "max_minutes": 9999, "boost_pct": 150,  "label": "TRANSCENDENT","color": "bright_red"},
]


def get_time_tier(minutes):
    for tier in reversed(TIME_TIERS):
        if minutes >= tier["min_minutes"]:
            return tier
    return TIME_TIERS[0]


def _load_sessions():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return {"users": {}, "global": {"total_session_time": 0, "total_sessions": 0}}


def _save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f, indent=2)


class TimeEarnEngine:
    """Tracks session time and applies time-based earning boosts."""

    def __init__(self):
        self.data = _load_sessions()
        self._active_sessions = {}

    def start_session(self, user_id):
        now = time.time()
        self._active_sessions[user_id] = {
            "start": now,
            "last_earn": now,
            "actions": 0,
        }
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "total_time_minutes": 0,
                "total_sessions": 0,
                "longest_session": 0,
                "total_boost_earned": 0.0,
                "current_session_start": now,
            }
        self.data["users"][user_id]["current_session_start"] = now
        self.data["users"][user_id]["total_sessions"] += 1
        self.data["global"]["total_sessions"] += 1
        _save_sessions(self.data)

    def record_action(self, user_id, amount_earned=0):
        if user_id not in self._active_sessions:
            self.start_session(user_id)

        session = self._active_sessions[user_id]
        session["actions"] += 1
        now = time.time()
        session_minutes = (now - session["start"]) / 60.0

        tier = get_time_tier(session_minutes)
        boost_mult = 1.0 + (tier["boost_pct"] / 100.0)
        boosted_amount = round(amount_earned * boost_mult, 4) if amount_earned > 0 else 0
        boost_bonus = round(boosted_amount - amount_earned, 4) if boosted_amount > 0 else 0

        user_data = self.data["users"].get(user_id, {})
        user_data["total_time_minutes"] = round(
            user_data.get("total_time_minutes", 0) + ((now - session["last_earn"]) / 60.0), 2
        )
        user_data["total_boost_earned"] = round(
            user_data.get("total_boost_earned", 0) + boost_bonus, 4
        )
        if session_minutes > user_data.get("longest_session", 0):
            user_data["longest_session"] = round(session_minutes, 2)

        self.data["global"]["total_session_time"] = round(
            self.data["global"].get("total_session_time", 0) + ((now - session["last_earn"]) / 60.0), 2
        )
        session["last_earn"] = now
        _save_sessions(self.data)

        return {
            "session_minutes": round(session_minutes, 1),
            "tier_label": tier["label"],
            "tier_color": tier["color"],
            "boost_pct": tier["boost_pct"],
            "boost_mult": round(boost_mult, 2),
            "base_earned": amount_earned,
            "boosted_earned": boosted_amount,
            "boost_bonus": boost_bonus,
            "total_earned": boosted_amount,
        }

    def get_session_status(self, user_id):
        if user_id not in self._active_sessions:
            return {
                "active": False,
                "session_minutes": 0,
                "tier_label": "BASE",
                "tier_color": "dim",
                "boost_pct": 0,
                "actions": 0,
            }
        session = self._active_sessions[user_id]
        now = time.time()
        minutes = (now - session["start"]) / 60.0
        tier = get_time_tier(minutes)
        return {
            "active": True,
            "session_minutes": round(minutes, 1),
            "tier_label": tier["label"],
            "tier_color": tier["color"],
            "boost_pct": tier["boost_pct"],
            "actions": session["actions"],
            "start_time": datetime.fromtimestamp(session["start"]).isoformat(),
        }

    def get_user_stats(self, user_id):
        return self.data["users"].get(user_id, {
            "total_time_minutes": 0,
            "total_sessions": 0,
            "longest_session": 0,
            "total_boost_earned": 0.0,
        })

    def get_global_stats(self):
        return self.data["global"]

    def get_time_tiers_display(self):
        return TIME_TIERS

    def end_session(self, user_id):
        if user_id in self._active_sessions:
            session = self._active_sessions[user_id]
            now = time.time()
            minutes = (now - session["start"]) / 60.0
            user_data = self.data["users"].get(user_id, {})
            user_data["total_time_minutes"] = round(
                user_data.get("total_time_minutes", 0) + minutes / 60.0, 2
            )
            if minutes > user_data.get("longest_session", 0):
                user_data["longest_session"] = round(minutes, 2)
            _save_sessions(self.data)
            del self._active_sessions[user_id]
            return {"session_minutes": round(minutes, 1)}
        return {"session_minutes": 0}
