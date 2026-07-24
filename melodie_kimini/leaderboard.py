"""
LEADERBOARD SYSTEM
Tracks Positive Impact Rankings Across the KIMINI Ecosystem
Protected by VaultLock integrity verification.
"""

import os
import json
from datetime import datetime

from .security import secure_load, secure_save, is_debugged, can_earn
from .anticheat import anticheat

DATA_DIR = os.path.join(os.getcwd(), "data", "leaderboard")
os.makedirs(DATA_DIR, exist_ok=True)

LB_FILE = os.path.join(DATA_DIR, "leaderboard.json")

PROJECTS = [
    {"id": "edu-global",      "name": "Global Education Initiative",    "category": "education",      "goal": 10000},
    {"id": "clean-oceans",    "name": "Clean Oceans Project",           "category": "environment",    "goal": 8000},
    {"id": "health-access",   "name": "Healthcare Access Program",      "category": "health",         "goal": 12000},
    {"id": "code-for-all",    "name": "Code for All Initiative",        "category": "innovation",     "goal": 6000},
    {"id": "green-energy",    "name": "Renewable Energy Research",      "category": "sustainability", "goal": 15000},
    {"id": "open-science",    "name": "Open Science Network",           "category": "research",       "goal": 9000},
    {"id": "arts-culture",    "name": "Arts & Culture Preservation",    "category": "arts",           "goal": 5000},
    {"id": "community-aid",   "name": "Community Aid Foundation",       "category": "community",      "goal": 7000},
    {"id": "mental-health",   "name": "Mental Health Awareness",        "category": "health",         "goal": 8500},
    {"id": "digital-access",  "name": "Digital Accessibility Project",  "category": "accessibility",  "goal": 6500},
]


def _load_lb():
    return secure_load(LB_FILE, lambda: {
        "projects": {
            p["id"]: {**p, "contributions": 0, "contributors": [], "karma_generated": 0}
            for p in PROJECTS
        },
        "users": {}, "history": [],
    })

def _save_lb(data):
    secure_save(LB_FILE, data)


class Leaderboard:
    """Tracks rankings, projects, and positive contributions."""

    def __init__(self):
        self.data = _load_lb()

    def contribute(self, user_id, project_id, karma_score, prompt=""):
        if is_debugged():
            return {"error": "Debugger detected"}
        pre_ok, pre_reason = anticheat.pre_action_check(user_id, "contribute", karma_score)
        if not pre_ok:
            return {"error": pre_reason}
        if not can_earn(f"contribute:{project_id}", min_interval=2.0, max_per_min=10):
            return {"error": "Rate limited"}
        if project_id not in self.data["projects"]:
            return None

        proj = self.data["projects"][project_id]
        proj["contributions"] += 1
        proj["karma_generated"] = round(proj["karma_generated"] + abs(karma_score), 2)
        if user_id not in proj["contributors"]:
            proj["contributors"].append(user_id)

        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "total_karma": 0, "total_contributions": 0,
                "projects_joined": [], "rank": 0,
            }
        user_lb = self.data["users"][user_id]
        user_lb["total_karma"] = round(user_lb["total_karma"] + abs(karma_score), 2)
        user_lb["total_contributions"] += 1
        if project_id not in user_lb["projects_joined"]:
            user_lb["projects_joined"].append(project_id)

        self.data["history"].append({
            "user_id": user_id, "project_id": project_id,
            "karma": abs(karma_score), "ts": datetime.utcnow().isoformat(),
        })
        if len(self.data["history"]) > 500:
            self.data["history"] = self.data["history"][-500:]

        self._update_ranks()
        _save_lb(self.data)
        return proj

    def _update_ranks(self):
        sorted_users = sorted(
            self.data["users"].items(),
            key=lambda x: x[1]["total_karma"], reverse=True,
        )
        for i, (uid, udata) in enumerate(sorted_users):
            udata["rank"] = i + 1

    def get_top_users(self, limit=10):
        sorted_users = sorted(
            self.data["users"].items(),
            key=lambda x: x[1]["total_karma"], reverse=True,
        )
        return [(uid, data) for uid, data in sorted_users[:limit]]

    def get_top_projects(self, limit=10):
        sorted_proj = sorted(
            self.data["projects"].items(),
            key=lambda x: x[1]["karma_generated"], reverse=True,
        )
        return [(pid, data) for pid, data in sorted_proj[:limit]]

    def get_project(self, project_id):
        return self.data["projects"].get(project_id)

    def get_user_rank(self, user_id):
        return self.data["users"].get(user_id, {"rank": 0, "total_karma": 0})

    def get_recent_activity(self, limit=20):
        return self.data["history"][-limit:]

    def get_all_projects(self):
        return self.data["projects"]
