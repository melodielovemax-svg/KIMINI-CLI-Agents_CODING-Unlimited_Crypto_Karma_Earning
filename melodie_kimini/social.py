"""
ULTIMATE SOCIAL MEDIA SHARING ENGINE
Generates detailed profile reports with scoring, ranking, earnings,
and social media share buttons for all major platforms.

Platforms supported:
  Twitter/X, Facebook, LinkedIn, Reddit, WhatsApp, Telegram,
  Instagram, Pinterest, Tumblr, Mastodon, Bluesky, Threads,
  YouTube Community, Discord, WeChat, Line, Email, Copy Link
"""

import os
import json
import time
from datetime import datetime
from urllib.parse import quote_plus

DATA_DIR = os.path.join(os.getcwd(), "data", "social")
os.makedirs(DATA_DIR, exist_ok=True)

SHARE_LOG = os.path.join(DATA_DIR, "shares.json")

# ============================================================
#  SOCIAL MEDIA PLATFORM DEFINITIONS
# ============================================================

SOCIAL_PLATFORMS = {
    "twitter": {
        "name": "Twitter / X",
        "icon": ">>",
        "color": "bright_cyan",
        "max_chars": 280,
        "url_template": "https://twitter.com/intent/tweet?text={text}&url={url}&hashtags={tags}",
        "supports_hashtags": True,
        "supports_url": True,
    },
    "facebook": {
        "name": "Facebook",
        "icon": "FB",
        "color": "bright_blue",
        "max_chars": 63206,
        "url_template": "https://www.facebook.com/sharer/sharer.php?u={url}&quote={text}",
        "supports_hashtags": False,
        "supports_url": True,
    },
    "linkedin": {
        "name": "LinkedIn",
        "icon": "LI",
        "color": "bright_blue",
        "max_chars": 3000,
        "url_template": "https://www.linkedin.com/sharing/share-offsite/?url={url}",
        "supports_hashtags": False,
        "supports_url": True,
    },
    "reddit": {
        "name": "Reddit",
        "icon": "RD",
        "color": "bright_red",
        "max_chars": 40000,
        "url_template": "https://reddit.com/submit?url={url}&title={title}",
        "supports_hashtags": False,
        "supports_url": True,
    },
    "whatsapp": {
        "name": "WhatsApp",
        "icon": "WA",
        "color": "bright_green",
        "max_chars": 65536,
        "url_template": "https://wa.me/?text={text}%20{url}",
        "supports_hashtags": False,
        "supports_url": True,
    },
    "telegram": {
        "name": "Telegram",
        "icon": "TG",
        "color": "bright_blue",
        "max_chars": 4096,
        "url_template": "https://t.me/share/url?url={url}&text={text}",
        "supports_hashtags": False,
        "supports_url": True,
    },
    "instagram": {
        "name": "Instagram",
        "icon": "IG",
        "color": "magenta",
        "max_chars": 2200,
        "url_template": "https://www.instagram.com/",
        "supports_hashtags": True,
        "supports_url": False,
    },
    "pinterest": {
        "name": "Pinterest",
        "icon": "PT",
        "color": "bright_red",
        "max_chars": 500,
        "url_template": "https://pinterest.com/pin/create/button/?url={url}&description={text}",
        "supports_hashtags": False,
        "supports_url": True,
    },
    "tumblr": {
        "name": "Tumblr",
        "icon": "TM",
        "color": "bright_blue",
        "max_chars": 4096,
        "url_template": "https://www.tumblr.com/share/link?url={url}&name={title}&description={text}",
        "supports_hashtags": False,
        "supports_url": True,
    },
    "mastodon": {
        "name": "Mastodon",
        "icon": "MA",
        "color": "bright_magenta",
        "max_chars": 500,
        "url_template": "https://mastodon.social/share?text={text}%20{url}",
        "supports_hashtags": True,
        "supports_url": True,
    },
    "bluesky": {
        "name": "Bluesky",
        "icon": "BS",
        "color": "bright_blue",
        "max_chars": 300,
        "url_template": "https://bsky.app/intent/compose?text={text}%20{url}",
        "supports_hashtags": True,
        "supports_url": True,
    },
    "threads": {
        "name": "Threads",
        "icon": "TH",
        "color": "white",
        "max_chars": 500,
        "url_template": "https://www.threads.net/intent/post?text={text}%20{url}",
        "supports_hashtags": True,
        "supports_url": True,
    },
    "discord": {
        "name": "Discord",
        "icon": "DC",
        "color": "bright_magenta",
        "max_chars": 2000,
        "url_template": "",
        "supports_hashtags": False,
        "supports_url": True,
    },
    "wechat": {
        "name": "WeChat",
        "icon": "WC",
        "color": "bright_green",
        "max_chars": 500,
        "url_template": "",
        "supports_hashtags": False,
        "supports_url": False,
    },
    "line": {
        "name": "LINE",
        "icon": "LN",
        "color": "bright_green",
        "max_chars": 500,
        "url_template": "https://social-plugins.line.me/lineit/share?url={url}&text={text}",
        "supports_hashtags": False,
        "supports_url": True,
    },
    "email": {
        "name": "Email",
        "icon": "@@",
        "color": "bright_white",
        "max_chars": 999999,
        "url_template": "mailto:?subject={title}&body={text}%0A%0A{url}",
        "supports_hashtags": False,
        "supports_url": True,
    },
    "copy": {
        "name": "Copy to Clipboard",
        "icon": "CP",
        "color": "bright_yellow",
        "max_chars": 999999,
        "url_template": "",
        "supports_hashtags": False,
        "supports_url": False,
    },
}


def _load_share_log():
    if os.path.exists(SHARE_LOG):
        with open(SHARE_LOG, "r") as f:
            return json.load(f)
    return {"shares": [], "total": 0, "by_platform": {}}


def _save_share_log(data):
    with open(SHARE_LOG, "w") as f:
        json.dump(data, f, indent=2)


# ============================================================
#  REPORT DATA COLLECTION
# ============================================================

def collect_user_data(user_id="default"):
    """Collect all user data from karma, combo, tokens, time, leaderboard, subscription."""
    data = {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "karma": {},
        "combo": {},
        "tokens": {},
        "time_earn": {},
        "leaderboard": {},
        "subscription": {},
        "totals": {},
    }

    try:
        from .karma import KarmaScorer
        scorer = KarmaScorer()
        ku = scorer.get_user(user_id)
        data["karma"] = {
            "score": ku.get("karma", 0),
            "level": ku.get("level", 1),
            "title": ku.get("title", "Beginner"),
            "sessions": ku.get("total_sessions", 0),
            "positive": ku.get("positive_count", 0),
            "negative": ku.get("negative_count", 0),
            "achievements": ku.get("achievements", []),
        }
    except Exception:
        data["karma"] = {"score": 0, "level": 1, "title": "Beginner", "sessions": 0,
                         "positive": 0, "negative": 0, "achievements": []}

    try:
        from .combo import ComboManager
        cm = ComboManager()
        cu = cm.get_user(user_id)
        data["combo"] = {
            "combo": cu.get("combo", 0),
            "tier": cu.get("current_tier", "NONE"),
            "rank": cu.get("rank", "Mortal"),
            "total_earned": cu.get("total_karma_earned", 0),
        }
    except Exception:
        data["combo"] = {"combo": 0, "tier": "NONE", "rank": "Mortal", "total_earned": 0}

    try:
        from .ma_token import MATokenManager
        tm = MATokenManager()
        tu = tm.get_user(user_id)
        data["tokens"] = {
            "balance": tu.get("balance", 0),
            "total_earned": tu.get("total_earned", 0),
            "total_spent": tu.get("total_spent", 0),
        }
    except Exception:
        data["tokens"] = {"balance": 0, "total_earned": 0, "total_spent": 0}

    try:
        from .time_earn import TimeEarnEngine
        te = TimeEarnEngine()
        td = te.get_user_data(user_id)
        data["time_earn"] = {
            "total_earned": td.get("total_earned", 0),
            "total_minutes": td.get("total_minutes", 0),
            "time_tier": td.get("current_tier", "BASE"),
        }
    except Exception:
        data["time_earn"] = {"total_earned": 0, "total_minutes": 0, "time_tier": "BASE"}

    try:
        from .leaderboard import Leaderboard
        lb = Leaderboard()
        lu = lb.get_user(user_id) or {}
        data["leaderboard"] = {
            "total_karma": lu.get("total_karma", 0),
            "contributions": lu.get("total_contributions", 0),
            "projects": lu.get("projects_joined", []),
            "rank": lu.get("rank", 0),
        }
    except Exception:
        data["leaderboard"] = {"total_karma": 0, "contributions": 0, "projects": [], "rank": 0}

    try:
        from .subscription import SubscriptionEngine
        sub = SubscriptionEngine()
        su = sub.get_user_plan(user_id)
        data["subscription"] = {
            "plan": su.get("plan", "free"),
            "is_lifetime": su.get("is_lifetime", False),
            "total_spent": su.get("total_spent", 0),
        }
    except Exception:
        data["subscription"] = {"plan": "free", "is_lifetime": False, "total_spent": 0}

    total_karma = data["karma"]["score"] + data["combo"]["total_earned"] + data["tokens"]["total_earned"]
    data["totals"] = {
        "total_karma": round(total_karma, 2),
        "total_tokens": data["tokens"]["balance"],
        "total_prompts": data["karma"]["sessions"],
        "positive_ratio": round(
            (data["karma"]["positive"] / max(1, data["karma"]["sessions"])) * 100, 1
        ),
        "days_active": max(1, data["karma"]["sessions"] // 5),
    }
    return data


# ============================================================
#  SHARE TEXT GENERATORS
# ============================================================

def generate_share_text(platform_id, data):
    """Generate optimized share text for a specific platform."""
    platform = SOCIAL_PLATFORMS[platform_id]
    kd = data["karma"]
    cd = data["combo"]
    td = data["tokens"]
    totals = data["totals"]
    sub = data["subscription"]

    plan_badge = {"free": "", "starter": " >>", "pro": " **", "ultimate": " ##+", "enterprise": " @@+"}
    plan_icon = plan_badge.get(sub["plan"], "")

    if platform_id == "twitter":
        text = (
            f"Melodie-Kimini Godlike AI Scorecard\n"
            f"\n"
            f"Karma: {kd['score']} | Lvl {kd['level']} {kd['title']}\n"
            f"Combo: x{cd['combo']} {cd['tier']}\n"
            f"Rank: {cd['rank']}\n"
            f"Tokens: {td['balance']} MA\n"
            f"Plan: {sub['plan'].upper()}{plan_icon}\n"
            f"\n"
            f"Prompts: {totals['total_prompts']} | Positive: {totals['positive_ratio']}%\n"
            f"#MelodieKimini #KarmaPower #AI"
        )
    elif platform_id == "facebook":
        text = (
            f"I'm on Melodie-Kimini GODLIKE AI!\n\n"
            f"My Impact Scorecard:\n"
            f"- Karma Power: {kd['score']} pts (Level {kd['level']}: {kd['title']})\n"
            f"- Combo Streak: x{cd['combo']} ({cd['tier']})\n"
            f"- Divine Rank: {cd['rank']}\n"
            f"- MA Tokens: {td['balance']} (Earned: {td['total_earned']})\n"
            f"- Subscription: {sub['plan'].upper()}{plan_icon}\n"
            f"- Positive Prompts: {kd['positive']}/{totals['total_prompts']}\n"
            f"- Leaderboard Position: #{data['leaderboard']['rank'] or 'Unranked'}\n\n"
            f"Join me on Melodie-Kimini and track your AI positive impact!"
        )
    elif platform_id == "linkedin":
        text = (
            f"I've been using Melodie-Kimini, an AI-powered positive impact tracker.\n\n"
            f"Here's my progress:\n"
            f"- Karma Score: {kd['score']} (Level {kd['level']}: {kd['title']})\n"
            f"- Active Combo: {cd['combo']}x streak ({cd['tier']})\n"
            f"- Divine Rank: {cd['rank']}\n"
            f"- Digital Assets: {td['balance']} MA Tokens\n"
            f"- Total Prompts: {totals['total_prompts']}\n"
            f"- Positive Ratio: {totals['positive_ratio']}%\n\n"
            f"The platform gamifies positive AI usage and rewards meaningful contributions."
        )
    elif platform_id == "reddit":
        text = (
            f"Melodie-Kimini Impact Report - Karma: {kd['score']} | Rank: {cd['rank']} | "
            f"Combo: {cd['combo']}x {cd['tier']} | Tokens: {td['balance']} MA | "
            f"Prompts: {totals['total_prompts']} | Positive: {totals['positive_ratio']}%"
        )
    elif platform_id == "whatsapp":
        text = (
            f"Melodie-Kimini AI Scorecard:\n\n"
            f"Karma: {kd['score']} | Level {kd['level']} {kd['title']}\n"
            f"Combo: {cd['combo']}x {cd['tier']} | Rank: {cd['rank']}\n"
            f"Tokens: {td['balance']} MA\n"
            f"Prompts: {totals['total_prompts']} | Positive: {totals['positive_ratio']}%"
        )
    elif platform_id == "telegram":
        text = (
            f"Melodie-Kimini Godlike AI Report\n"
            f"Karma: {kd['score']} | Lvl {kd['level']} {kd['title']}\n"
            f"Combo: x{cd['combo']} {cd['tier']} | Rank: {cd['rank']}\n"
            f"Tokens: {td['balance']} MA\n"
            f"Prompts: {totals['total_prompts']} | Positive: {totals['positive_ratio']}%"
        )
    elif platform_id == "bluesky":
        text = (
            f"Melodie-Kimini Scorecard:\n"
            f"Karma {kd['score']} | Lvl {kd['level']} {kd['title']}\n"
            f"Combo x{cd['combo']} {cd['tier']} | {cd['rank']}\n"
            f"{td['balance']} MA Tokens\n"
            f"{totals['total_prompts']} prompts | {totals['positive_ratio']}% positive"
        )
    elif platform_id == "instagram":
        text = (
            f"Melodie-Kimini Godlike AI\n"
            f"Karma: {kd['score']}\n"
            f"Level {kd['level']}: {kd['title']}\n"
            f"Combo: {cd['combo']}x {cd['tier']}\n"
            f"Rank: {cd['rank']}\n"
            f"Tokens: {td['balance']} MA\n"
            f"#MelodieKimini #KarmaPower #AI #PositiveImpact"
        )
    else:
        text = (
            f"Melodie-Kimini Scorecard: Karma {kd['score']} | "
            f"Lvl {kd['level']} {kd['title']} | "
            f"Combo {cd['combo']}x {cd['tier']} | "
            f"Rank {cd['rank']} | "
            f"{td['balance']} MA Tokens | "
            f"{totals['total_prompts']} prompts | "
            f"{totals['positive_ratio']}% positive"
        )
    return text


def generate_share_url(platform_id, data):
    """Generate the share URL for a platform."""
    platform = SOCIAL_PLATFORMS[platform_id]
    text = generate_share_text(platform_id, data)
    title = f"Melodie-Kimini: {data['karma']['title']} - {data['karma']['score']} Karma"
    url = "https://melodie-kimini.app/u/" + data["user_id"]
    tags = "MelodieKimini,KarmaPower,AI,PositiveImpact"

    template = platform["url_template"]
    if not template:
        return ""

    return template.format(
        text=quote_plus(text[:min(len(text), platform["max_chars"])]),
        url=quote_plus(url),
        title=quote_plus(title),
        tags=quote_plus(tags),
    )


# ============================================================
#  SHARE RECORDING
# ============================================================

def record_share(user_id, platform_id):
    """Record a share event for analytics."""
    log = _load_share_log()
    entry = {
        "user_id": user_id,
        "platform": platform_id,
        "timestamp": datetime.utcnow().isoformat(),
    }
    log["shares"].append(entry)
    log["total"] += 1
    log["by_platform"][platform_id] = log["by_platform"].get(platform_id, 0) + 1
    if len(log["shares"]) > 500:
        log["shares"] = log["shares"][-500:]
    _save_share_log(log)
    return log


def get_share_stats():
    """Return global sharing statistics."""
    return _load_share_log()
