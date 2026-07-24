"""
KIMINI Models Flash Lite Pro Expert Senior
Versions: 3.1, 3.5, 4.0, 5.0, 6.9
All 56 Models - Unlimited Tokens
"""

KIMINI_MODELS = {
    # ── Flash Tier (5 models) ──────────────────────────────────────
    "kimi-flash-3.1": {
        "tier": "flash", "version": "3.1",
        "context": 128000, "speed": "fast",
        "caps": ["chat", "summarize", "translate"],
    },
    "kimi-flash-3.5": {
        "tier": "flash", "version": "3.5",
        "context": 256000, "speed": "fast",
        "caps": ["chat", "summarize", "translate", "code"],
    },
    "kimi-flash-4.0": {
        "tier": "flash", "version": "4.0",
        "context": 512000, "speed": "fast",
        "caps": ["chat", "summarize", "translate", "code", "reasoning"],
    },
    "kimi-flash-5.0": {
        "tier": "flash", "version": "5.0",
        "context": 1000000, "speed": "fast",
        "caps": ["chat", "summarize", "translate", "code", "reasoning", "vision"],
    },
    "kimi-flash-6.9": {
        "tier": "flash", "version": "6.9",
        "context": 2000000, "speed": "fast",
        "caps": ["chat", "summarize", "translate", "code", "reasoning", "vision", "tool_use"],
    },

    # ── Lite Tier (5 models) ──────────────────────────────────────
    "kimi-lite-3.1": {
        "tier": "lite", "version": "3.1",
        "context": 128000, "speed": "ultra-fast",
        "caps": ["chat", "summarize"],
    },
    "kimi-lite-3.5": {
        "tier": "lite", "version": "3.5",
        "context": 256000, "speed": "ultra-fast",
        "caps": ["chat", "summarize", "translate"],
    },
    "kimi-lite-4.0": {
        "tier": "lite", "version": "4.0",
        "context": 512000, "speed": "ultra-fast",
        "caps": ["chat", "summarize", "translate", "code"],
    },
    "kimi-lite-5.0": {
        "tier": "lite", "version": "5.0",
        "context": 1000000, "speed": "ultra-fast",
        "caps": ["chat", "summarize", "translate", "code", "reasoning"],
    },
    "kimi-lite-6.9": {
        "tier": "lite", "version": "6.9",
        "context": 2000000, "speed": "ultra-fast",
        "caps": ["chat", "summarize", "translate", "code", "reasoning", "vision"],
    },

    # ── Pro Tier (5 models) ───────────────────────────────────────
    "kimi-pro-3.1": {
        "tier": "pro", "version": "3.1",
        "context": 128000, "speed": "balanced",
        "caps": ["chat", "summarize", "translate", "code", "analysis"],
    },
    "kimi-pro-3.5": {
        "tier": "pro", "version": "3.5",
        "context": 256000, "speed": "balanced",
        "caps": ["chat", "summarize", "translate", "code", "analysis", "reasoning"],
    },
    "kimi-pro-4.0": {
        "tier": "pro", "version": "4.0",
        "context": 512000, "speed": "balanced",
        "caps": ["chat", "summarize", "translate", "code", "analysis", "reasoning", "vision"],
    },
    "kimi-pro-5.0": {
        "tier": "pro", "version": "5.0",
        "context": 1000000, "speed": "balanced",
        "caps": ["chat", "summarize", "translate", "code", "analysis", "reasoning", "vision", "tool_use"],
    },
    "kimi-pro-6.9": {
        "tier": "pro", "version": "6.9",
        "context": 2000000, "speed": "balanced",
        "caps": ["chat", "summarize", "translate", "code", "analysis", "reasoning", "vision", "tool_use", "agents"],
    },

    # ── Expert Tier (5 models) ────────────────────────────────────
    "kimi-expert-3.1": {
        "tier": "expert", "version": "3.1",
        "context": 128000, "speed": "deep",
        "caps": ["chat", "code", "analysis", "reasoning", "math"],
    },
    "kimi-expert-3.5": {
        "tier": "expert", "version": "3.5",
        "context": 256000, "speed": "deep",
        "caps": ["chat", "code", "analysis", "reasoning", "math", "science"],
    },
    "kimi-expert-4.0": {
        "tier": "expert", "version": "4.0",
        "context": 512000, "speed": "deep",
        "caps": ["chat", "code", "analysis", "reasoning", "math", "science", "vision"],
    },
    "kimi-expert-5.0": {
        "tier": "expert", "version": "5.0",
        "context": 1000000, "speed": "deep",
        "caps": ["chat", "code", "analysis", "reasoning", "math", "science", "vision", "tool_use"],
    },
    "kimi-expert-6.9": {
        "tier": "expert", "version": "6.9",
        "context": 2000000, "speed": "deep",
        "caps": ["chat", "code", "analysis", "reasoning", "math", "science", "vision", "tool_use", "agents", "research"],
    },

    # ── Senior Tier (5 models) ────────────────────────────────────
    "kimi-senior-3.1": {
        "tier": "senior", "version": "3.1",
        "context": 128000, "speed": "thorough",
        "caps": ["chat", "code", "analysis", "reasoning", "writing"],
    },
    "kimi-senior-3.5": {
        "tier": "senior", "version": "3.5",
        "context": 256000, "speed": "thorough",
        "caps": ["chat", "code", "analysis", "reasoning", "writing", "creative"],
    },
    "kimi-senior-4.0": {
        "tier": "senior", "version": "4.0",
        "context": 512000, "speed": "thorough",
        "caps": ["chat", "code", "analysis", "reasoning", "writing", "creative", "vision"],
    },
    "kimi-senior-5.0": {
        "tier": "senior", "version": "5.0",
        "context": 1000000, "speed": "thorough",
        "caps": ["chat", "code", "analysis", "reasoning", "writing", "creative", "vision", "tool_use"],
    },
    "kimi-senior-6.9": {
        "tier": "senior", "version": "6.9",
        "context": 2000000, "speed": "thorough",
        "caps": ["chat", "code", "analysis", "reasoning", "writing", "creative", "vision", "tool_use", "agents"],
    },

    # ── Flash-Lite Combo (5 models) ───────────────────────────────
    "kimi-flash-lite-3.1": {
        "tier": "flash-lite", "version": "3.1",
        "context": 64000, "speed": "instant",
        "caps": ["chat", "summarize"],
    },
    "kimi-flash-lite-3.5": {
        "tier": "flash-lite", "version": "3.5",
        "context": 128000, "speed": "instant",
        "caps": ["chat", "summarize", "translate"],
    },
    "kimi-flash-lite-4.0": {
        "tier": "flash-lite", "version": "4.0",
        "context": 256000, "speed": "instant",
        "caps": ["chat", "summarize", "translate", "code"],
    },
    "kimi-flash-lite-5.0": {
        "tier": "flash-lite", "version": "5.0",
        "context": 512000, "speed": "instant",
        "caps": ["chat", "summarize", "translate", "code", "reasoning"],
    },
    "kimi-flash-lite-6.9": {
        "tier": "flash-lite", "version": "6.9",
        "context": 1000000, "speed": "instant",
        "caps": ["chat", "summarize", "translate", "code", "reasoning", "vision"],
    },

    # ── Pro-Max Combo (5 models) ──────────────────────────────────
    "kimi-pro-max-3.1": {
        "tier": "pro-max", "version": "3.1",
        "context": 256000, "speed": "balanced",
        "caps": ["chat", "code", "analysis", "reasoning", "vision", "tool_use"],
    },
    "kimi-pro-max-3.5": {
        "tier": "pro-max", "version": "3.5",
        "context": 512000, "speed": "balanced",
        "caps": ["chat", "code", "analysis", "reasoning", "vision", "tool_use", "agents"],
    },
    "kimi-pro-max-4.0": {
        "tier": "pro-max", "version": "4.0",
        "context": 1000000, "speed": "balanced",
        "caps": ["chat", "code", "analysis", "reasoning", "vision", "tool_use", "agents", "research"],
    },
    "kimi-pro-max-5.0": {
        "tier": "pro-max", "version": "5.0",
        "context": 2000000, "speed": "balanced",
        "caps": ["chat", "code", "analysis", "reasoning", "vision", "tool_use", "agents", "research", "creative"],
    },
    "kimi-pro-max-6.9": {
        "tier": "pro-max", "version": "6.9",
        "context": 4000000, "speed": "balanced",
        "caps": ["chat", "code", "analysis", "reasoning", "vision", "tool_use", "agents", "research", "creative", "math"],
    },

    # ── Expert-Ultra Combo (5 models) ─────────────────────────────
    "kimi-expert-ultra-3.1": {
        "tier": "expert-ultra", "version": "3.1",
        "context": 256000, "speed": "deep",
        "caps": ["code", "analysis", "reasoning", "math", "science"],
    },
    "kimi-expert-ultra-3.5": {
        "tier": "expert-ultra", "version": "3.5",
        "context": 512000, "speed": "deep",
        "caps": ["code", "analysis", "reasoning", "math", "science", "vision"],
    },
    "kimi-expert-ultra-4.0": {
        "tier": "expert-ultra", "version": "4.0",
        "context": 1000000, "speed": "deep",
        "caps": ["code", "analysis", "reasoning", "math", "science", "vision", "tool_use"],
    },
    "kimi-expert-ultra-5.0": {
        "tier": "expert-ultra", "version": "5.0",
        "context": 2000000, "speed": "deep",
        "caps": ["code", "analysis", "reasoning", "math", "science", "vision", "tool_use", "agents"],
    },
    "kimi-expert-ultra-6.9": {
        "tier": "expert-ultra", "version": "6.9",
        "context": 4000000, "speed": "deep",
        "caps": ["code", "analysis", "reasoning", "math", "science", "vision", "tool_use", "agents", "research"],
    },

    # ── Senior-Elite Combo (5 models) ─────────────────────────────
    "kimi-senior-elite-3.1": {
        "tier": "senior-elite", "version": "3.1",
        "context": 256000, "speed": "thorough",
        "caps": ["code", "analysis", "writing", "creative", "reasoning"],
    },
    "kimi-senior-elite-3.5": {
        "tier": "senior-elite", "version": "3.5",
        "context": 512000, "speed": "thorough",
        "caps": ["code", "analysis", "writing", "creative", "reasoning", "vision"],
    },
    "kimi-senior-elite-4.0": {
        "tier": "senior-elite", "version": "4.0",
        "context": 1000000, "speed": "thorough",
        "caps": ["code", "analysis", "writing", "creative", "reasoning", "vision", "tool_use"],
    },
    "kimi-senior-elite-5.0": {
        "tier": "senior-elite", "version": "5.0",
        "context": 2000000, "speed": "thorough",
        "caps": ["code", "analysis", "writing", "creative", "reasoning", "vision", "tool_use", "agents"],
    },
    "kimi-senior-elite-6.9": {
        "tier": "senior-elite", "version": "6.9",
        "context": 4000000, "speed": "thorough",
        "caps": ["code", "analysis", "writing", "creative", "reasoning", "vision", "tool_use", "agents", "research"],
    },

    # ── Reasoning Specialized (6 models) ──────────────────────────
    "kimi-reason-3.5": {
        "tier": "reason", "version": "3.5",
        "context": 256000, "speed": "deliberate",
        "caps": ["chain_of_thought", "math", "logic", "code", "analysis"],
    },
    "kimi-reason-4.0": {
        "tier": "reason", "version": "4.0",
        "context": 512000, "speed": "deliberate",
        "caps": ["chain_of_thought", "math", "logic", "code", "analysis", "science"],
    },
    "kimi-reason-5.0": {
        "tier": "reason", "version": "5.0",
        "context": 1000000, "speed": "deliberate",
        "caps": ["chain_of_thought", "math", "logic", "code", "analysis", "science", "vision"],
    },
    "kimi-reason-6.9": {
        "tier": "reason", "version": "6.9",
        "context": 2000000, "speed": "deliberate",
        "caps": ["chain_of_thought", "math", "logic", "code", "analysis", "science", "vision", "tool_use"],
    },
    "kimi-reason-pro-5.0": {
        "tier": "reason-pro", "version": "5.0",
        "context": 2000000, "speed": "deliberate",
        "caps": ["chain_of_thought", "math", "logic", "code", "analysis", "science", "vision", "tool_use", "agents"],
    },
    "kimi-reason-pro-6.9": {
        "tier": "reason-pro", "version": "6.9",
        "context": 4000000, "speed": "deliberate",
        "caps": ["chain_of_thought", "math", "logic", "code", "analysis", "science", "vision", "tool_use", "agents", "research"],
    },

    # ── Multimodal Specialized (5 models) ─────────────────────────
    "kimi-vision-4.0": {
        "tier": "vision", "version": "4.0",
        "context": 512000, "speed": "balanced",
        "caps": ["vision", "image_analysis", "ocr", "chart_reading", "diagram"],
    },
    "kimi-vision-5.0": {
        "tier": "vision", "version": "5.0",
        "context": 1000000, "speed": "balanced",
        "caps": ["vision", "image_analysis", "ocr", "chart_reading", "diagram", "video"],
    },
    "kimi-vision-6.9": {
        "tier": "vision", "version": "6.9",
        "context": 2000000, "speed": "balanced",
        "caps": ["vision", "image_analysis", "ocr", "chart_reading", "diagram", "video", "3d"],
    },
    "kimi-audio-5.0": {
        "tier": "audio", "version": "5.0",
        "context": 1000000, "speed": "realtime",
        "caps": ["audio", "transcription", "translation", "voice", "chat"],
    },
    "kimi-audio-6.9": {
        "tier": "audio", "version": "6.9",
        "context": 2000000, "speed": "realtime",
        "caps": ["audio", "transcription", "translation", "voice", "chat", "emotion"],
    },
}


def get_all_model_ids():
    """Return sorted list of all 56 model IDs."""
    return sorted(KIMINI_MODELS.keys())


def get_models_by_tier(tier):
    """Return models matching a specific tier."""
    return {
        k: v for k, v in KIMINI_MODELS.items()
        if v["tier"] == tier
    }


def get_models_by_version(version):
    """Return models matching a specific version."""
    return {
        k: v for k, v in KIMINI_MODELS.items()
        if v["version"] == version
    }


def get_model_info(model_id):
    """Return info for a specific model."""
    return KIMINI_MODELS.get(model_id)


def get_tiers():
    """Return sorted unique tier names."""
    return sorted(set(m["tier"] for m in KIMINI_MODELS.values()))


def get_versions():
    """Return sorted unique version strings."""
    return sorted(set(m["version"] for m in KIMINI_MODELS.values()))
