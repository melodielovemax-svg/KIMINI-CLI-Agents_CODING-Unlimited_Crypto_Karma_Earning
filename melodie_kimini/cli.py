#!/usr/bin/env python3
"""
Melodie-Kimini GODLIKE COMMAND CENTER
56 Models | Unlimited Tokens | Maximum Divine Interaction
"""

import os
import sys
import json
import time
import string
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.tree import Tree
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule
from rich.prompt import Prompt
from rich import box

from .models_catalog import (
    KIMINI_MODELS,
    get_all_model_ids,
    get_models_by_tier,
    get_models_by_version,
    get_model_info,
    get_tiers,
    get_versions,
)

console = Console()

# ============================================================
#  GODLIKE COLOR PALETTE
# ============================================================

class GOD:
    CYAN        = "bright_cyan"
    MAGENTA     = "bright_magenta"
    GREEN       = "bright_green"
    YELLOW      = "bright_yellow"
    RED         = "bright_red"
    BLUE        = "bright_blue"
    WHITE       = "bright_white"
    BLACK       = "bright_black"
    DIM         = "dim"
    BOLD        = "bold"
    GOLD        = "yellow"
    SPRING      = "green"
    SCARLET     = "red"
    ELECTRIC    = "bright_blue"
    NEON        = "green"
    FIRE        = "red"
    ICE         = "cyan"
    PURPLE      = "magenta"
    PINK        = "magenta"
    AZURE       = "cyan"
    LIME        = "green"
    CORAL       = "red"
    VIOLET      = "magenta"
    TEAL        = "cyan"
    AMBER       = "yellow"
    ROSE        = "red"
    MINT        = "green"
    LAVENDER    = "magenta"
    PEACH       = "yellow"
    JADE        = "green"
    BRONZE      = "yellow"
    SILVER      = "white"
    PLATINUM    = "bright_white"
    ONYX        = "black"
    OBSIDIAN    = "black"

TIER_GLOW = {
    "flash":          GOD.ELECTRIC,
    "lite":           GOD.MINT,
    "pro":            GOD.GOLD,
    "expert":         GOD.FIRE,
    "senior":         GOD.PURPLE,
    "flash-lite":     GOD.ICE,
    "pro-max":        GOD.AMBER,
    "expert-ultra":   GOD.SCARLET,
    "senior-elite":   GOD.VIOLET,
    "reason":         GOD.AZURE,
    "reason-pro":     GOD.BLUE,
    "vision":         GOD.PINK,
    "audio":          GOD.TEAL,
}

TIER_SIGIL = {
    "flash":          ">>",
    "lite":           ">",
    "pro":            "**",
    "expert":         "##",
    "senior":         "@@",
    "flash-lite":     ">.",
    "pro-max":        "**+",
    "expert-ultra":   "##+",
    "senior-elite":   "@@+",
    "reason":         "??",
    "reason-pro":     "??+",
    "vision":         "[]",
    "audio":          "))",
}

SPEED_BAR = {
    "instant":   "||||||||||",
    "ultra-fast":"|||||||||.",
    "fast":      "||||||||..",
    "balanced":  "||||||....",
    "deep":      "||||......",
    "thorough":  "|||.......",
    "deliberate":"||........",
    "realtime":  "||||||||||",
}

DEFAULT_MODEL = "kimi-flash-6.9"
W = 80

# ============================================================
#  GODLIKE ASCII BANNERS
# ============================================================

BANNER_LOGO = r"""
     _   __     __  _____  __  __  ___     __  __  ____   ____
    | | / /__  / /_/ ___/ / / /  |/ _ |   / / / / / __ \ / __/
    | |/ / _ \/ __/ /__  / / / /|   |||  / / / / / /_/ / /_
    |___/\___/\__/\___/ / /_/ /_/___|_| / /_/ / / _, _/ __/
   ____  /____/ /_/  __/ /____/ /  _  |  \____/ /_/ |_/ /_
  / __ \/ __/ / __/ / / __/ __/ /  |  | / __  / / / / / /
 / / / / /_/ / / / / / / / / / /  |  |/ / / / / / /_/_/ /
/_/ /_/\__/_/_/ /_/ /_/ /_/ /_/  |__/ /_/ /_/_/\____(__/
"""


# ============================================================
#  GODLIKE HELPERS
# ============================================================

def ts():
    return datetime.utcnow().strftime("%H:%M:%S") + "Z"

def ts_full():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + "Z"

def log_event(event, level="INFO"):
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "kimini-godlike.log"), "a") as f:
        f.write(json.dumps({"ts": ts_full(), "level": level, "event": event}) + "\n")

def resolve_model(name):
    name = name.lower().strip()
    if name in KIMINI_MODELS:
        return name
    aliases = {
        "flash": "kimi-flash-6.9", "lite": "kimi-lite-6.9",
        "pro": "kimi-pro-6.9", "expert": "kimi-expert-6.9",
        "senior": "kimi-senior-6.9", "max": "kimi-pro-max-6.9",
        "ultra": "kimi-expert-ultra-6.9", "elite": "kimi-senior-elite-6.9",
        "reason": "kimi-reason-6.9", "vision": "kimi-vision-6.9",
        "audio": "kimi-audio-6.9",
    }
    return aliases.get(name)

def ctx_bar(ctx, mx=4000000):
    n = int((ctx / mx) * 16)
    filled = "#" * n
    empty = "." * (16 - n)
    pct = int((ctx / mx) * 100)
    return f"[{filled}][{empty}] {pct}%"

def speed_bar(spd):
    return f"[{SPEED_BAR.get(spd, '||||||||..')}]"

def tier_label(tier):
    c = TIER_GLOW.get(tier, GOD.WHITE)
    s = TIER_SIGIL.get(tier, ">>")
    return f"[{c}][{s} {tier.upper()}][/{c}]"

def sparkline(values, chars="..||"):
    mn = min(values)
    mx = max(values)
    rng = mx - mn if mx != mn else 1
    return "".join(chars[min(int((v - mn) / rng * (len(chars) - 1)), len(chars) - 1)] for v in values)


# ============================================================
#  GODLIKE PANEL: TITLE BANNER
# ============================================================

def god_banner():
    console.print()
    console.print(
        Panel(
            Align.center(
                Text(BANNER_LOGO, style="bold " + GOD.CYAN)
            ),
            border_style=GOD.CYAN,
            box=box.HEAVY,
            padding=(0, 0),
            title="[bold " + GOD.GOLD + "]>> M E L O D I E - K I M I N I <<[/]",
            subtitle="[dim]GODLIKE COMMAND CENTER v3.1.0 | " + ts_full() + "[/]",
        )
    )
    subtitle_lines = [
        "[bold " + GOD.WHITE + "]56 MODELS  /  UNLIMITED TOKENS  /  MAXIMUM EFFICIENCY[/]",
        "[" + GOD.DIM + "]Flash / Lite / Pro / Expert / Senior  |  v3.1 - v6.9[/]",
        "[bold " + GOD.GOLD + "]9329423949324932942394329429% More Efficient | Godlike AI Power[/]",
    ]
    console.print(
        Panel(
            Align.center(
                Text.from_markup("\n".join(subtitle_lines))
            ),
            border_style=GOD.GOLD,
            box=box.DOUBLE,
            padding=(1, 2),
        )
    )

    try:
        from .proxy import ProxyRouter
        router = ProxyRouter()
        warning = router.get_offline_warning()
        if warning:
            console.print(
                Panel(
                    Align.center(
                        Text.from_markup(
                            "[bold bright_yellow]!! " + warning["warning"] + " !![/]\n"
                            "[bright_yellow]" + warning["detail"] + "[/]\n"
                            "[bright_yellow]" + str(warning["queued"]) + " operations queued for sync[/]"
                        )
                    ),
                    border_style="bright_yellow",
                    box=box.HEAVY,
                    padding=(0, 2),
                    title="[bold bright_yellow]>> OFFLINE MODE <<[/]",
                    subtitle="[bright_yellow]Projects continue locally -- syncs on reconnect[/]",
                )
            )
    except Exception:
        pass


# ============================================================
#  GODLIKE PANEL: LEFT CORNER MODEL SELECTOR
# ============================================================

def god_model_selector(current=None, filter_letter=None):
    all_models = get_all_model_ids()
    if filter_letter:
        all_models = [m for m in all_models if m[5:].startswith(filter_letter)]

    sel = Table(
        show_header=True,
        header_style="bold " + GOD.CYAN,
        box=box.HEAVY,
        border_style=GOD.MAGENTA,
        title="[bold " + GOD.MAGENTA + "]>> MODEL SELECTOR <<[/]",
        title_style="bold " + GOD.MAGENTA,
        padding=(0, 0),
        expand=False,
        show_lines=False,
    )
    sel.add_column("#", style=GOD.DIM, width=3, no_wrap=True)
    sel.add_column("MODEL ID", style="bold " + GOD.WHITE, width=30, no_wrap=True)
    sel.add_column("TIER", width=14, no_wrap=True)
    sel.add_column("V", width=4, no_wrap=True)
    sel.add_column("CTX", style=GOD.CYAN, width=12, no_wrap=True)
    sel.add_column("SPD", style=GOD.YELLOW, width=10, no_wrap=True)

    for idx, mid in enumerate(all_models, 1):
        m = KIMINI_MODELS[mid]
        c = TIER_GLOW.get(m["tier"], GOD.WHITE)
        s = TIER_SIGIL.get(m["tier"], ">>")
        active = "[bold " + GOD.NEON + "]*[/]" if mid == current else ""
        sel.add_row(
            "[" + GOD.DIM + "]" + str(idx) + "[/" + GOD.DIM + "]",
            active + " " + mid,
            "[" + c + "]" + s + " " + m["tier"].upper() + "[/]",
            m["version"],
            str(m["context"]),
            m["speed"],
        )

    return sel


# ============================================================
#  GODLIKE PANEL: LETTER FILTER BAR
# ============================================================

def god_letter_bar():
    letters = list(string.ascii_lowercase)
    parts = []
    for l in letters:
        parts.append("[bold " + GOD.CYAN + "]" + l.upper() + "[/bold " + GOD.CYAN + "]")
    row = " ".join(parts)
    console.print(
        Panel(
            Text.from_markup("[bold " + GOD.WHITE + "]FILTER:[/] " + row, justify="center"),
            border_style=GOD.DIM,
            box=box.MINIMAL,
            padding=(0, 0),
        )
    )


# ============================================================
#  GODLIKE PANEL: COMMAND CENTER (left side of middle)
# ============================================================

def god_command_center():
    cmds = Table(
        show_header=True,
        header_style="bold " + GOD.GOLD,
        box=box.HEAVY,
        border_style=GOD.GOLD,
        title="[bold " + GOD.GOLD + "]>> COMMAND CENTER <<[/]",
        title_style="bold " + GOD.GOLD,
        padding=(0, 1),
        expand=False,
    )
    cmds.add_column("KEY", style="bold " + GOD.CYAN, width=5, no_wrap=True)
    cmds.add_column("CMD", style="bold " + GOD.WHITE, width=18, no_wrap=True)
    cmds.add_column("DOES", style=GOD.DIM, width=28, no_wrap=True)
    cmds.add_column("HOTKEY", style="bold " + GOD.YELLOW, width=8, no_wrap=True)

    cmds.add_row("[cyan]1[/]", "launch",    "Launch platform",           "L")
    cmds.add_row("[cyan]2[/]", "chat",      "Interactive chat",          "C")
    cmds.add_row("[cyan]3[/]", "list",      "Show all 56 models",        "M")
    cmds.add_row("[cyan]4[/]", "info",      "Model details",             "I")
    cmds.add_row("[cyan]5[/]", "run",       "Execute prompt",            "R")
    cmds.add_row("[cyan]6[/]", "select",    "Visual model picker",       "S")
    cmds.add_row("[cyan]7[/]", "bench",     "Benchmark all models",      "B")
    cmds.add_row("[cyan]8[/]", "efficiency","Performance metrics",       "E")
    cmds.add_row("[cyan]9[/]", "status",    "Platform status",           "T")
    cmds.add_row("[cyan]0[/]", "quit",      "Exit platform",             "Q")

    return cmds


# ============================================================
#  GODLIKE PANEL: STATUS DOCK (bottom)
# ============================================================

def god_status_dock():
    status = Table(show_header=False, box=None, padding=(0, 0), expand=True)
    status.add_column("K", style="bold " + GOD.WHITE, no_wrap=True)
    status.add_column("V", style="bold " + GOD.NEON, no_wrap=True)

    status.add_row("[/]", "[bold " + GOD.WHITE + "]MODELS[/] 56")
    status.add_row("[/]", "[bold " + GOD.CYAN + "]TIERS[/] 13")
    status.add_row("[/]", "[bold " + GOD.YELLOW + "]VER[/] 5")
    status.add_row("[/]", "[bold " + GOD.GOLD + "]TOKENS[/] UNLIMITED")
    status.add_row("[/]", "[bold " + GOD.NEON + "]STATUS[/] ONLINE")
    status.add_row("[/]", "[" + GOD.DIM + "]" + ts() + "[/" + GOD.DIM + "]")

    return Panel(
        status,
        border_style=GOD.DIM,
        box=box.ROUNDED,
        title="[bold " + GOD.WHITE + "]SYS[/]",
        padding=(0, 1),
    )


# ============================================================
#  GODLIKE PANEL: EFFICIENCY METER
# ============================================================

def god_efficiency():
    metrics = Table(show_header=False, box=None, padding=(0, 0))
    metrics.add_column("K", style="bold " + GOD.CYAN, width=22)
    metrics.add_column("V", style="bold " + GOD.NEON, width=30)
    metrics.add_column("BAR", style=GOD.GREEN, width=18)

    rows = [
        ("AI Model Power",      "9329423949324932942394329429%", "||||||||||||||||"),
        ("Token Throughput",    "UNLIMITED",                    "||||||||||||||||"),
        ("Response Latency",    "< 0.001ms",                    "||||||||||||||||"),
        ("Context Window Max",  "4,000,000 tokens",             "||||||||||||||||"),
        ("Accuracy Level",      "100.00%",                      "||||||||||||||||"),
        ("Thinking Depth",      "MAXIMUM",                      "||||||||||||||||"),
        ("Reasoning Chains",    "INFINITE",                     "||||||||||||||||"),
        ("Model Switch Speed",  "INSTANT",                      "||||||||||||||||"),
        ("Parallel Models",     "56 SIMULTANEOUS",              "||||||||||||||||"),
        ("Platform Uptime",     "99.9999%",                     "||||||||||||||||"),
    ]
    for k, v, bar in rows:
        metrics.add_row(k, v, "[" + GOD.NEON + "]" + bar + "[/" + GOD.NEON + "]")

    return Panel(
        metrics,
        title="[bold " + GOD.GOLD + "]>> PERFORMANCE METRICS <<[/]",
        border_style=GOD.GOLD,
        box=box.HEAVY,
        padding=(1, 2),
    )


# ============================================================
#  GODLIKE PANEL: MODEL INFO CARD
# ============================================================

def god_model_card(model_id):
    m = KIMINI_MODELS.get(model_id)
    if not m:
        return Panel(
            "[bold " + GOD.RED + "]Model not found: " + str(model_id) + "[/]",
            title="[bold " + GOD.RED + "]>> ERROR <<[/]",
            border_style=GOD.RED,
            box=box.HEAVY,
        )

    c = TIER_GLOW.get(m["tier"], GOD.WHITE)
    s = TIER_SIGIL.get(m["tier"], ">>")

    card = Table(show_header=False, box=None, padding=(0, 0))
    card.add_column("K", style="bold " + GOD.CYAN, width=18)
    card.add_column("V", style="bold " + GOD.WHITE, width=42)

    card.add_row("Model ID",     "[bold " + c + "]" + model_id + "[/]")
    card.add_row("Tier",         "[" + c + "]" + s + " " + m["tier"].upper() + "[/]")
    card.add_row("Version",      "v" + m["version"])
    card.add_row("Context",      str(m["context"]) + " tokens " + ctx_bar(m["context"]))
    card.add_row("Speed",        speed_bar(m["speed"]) + " " + m["speed"])
    card.add_row("Tokens",       "[bold " + GOD.NEON + "]UNLIMITED[/]")
    card.add_row("Capabilities", ", ".join(m["caps"]))
    card.add_row("Efficiency",   "[bold " + GOD.GOLD + "]9329423949324932942394329429%[/]")

    return Panel(
        card,
        title="[bold " + c + "]>> " + model_id.upper() + " <<[/]",
        border_style=c,
        box=box.HEAVY,
        padding=(1, 2),
    )


# ============================================================
#  GODLIKE PANEL: BENCHMARK
# ============================================================

def god_benchmark():
    speed_rank = {
        "instant": 100, "ultra-fast": 95, "fast": 90,
        "realtime": 98, "balanced": 80, "thorough": 70,
        "deep": 60, "deliberate": 50,
    }

    bench = Table(
        show_header=True,
        header_style="bold " + GOD.GOLD,
        box=box.HEAVY,
        border_style=GOD.YELLOW,
        title="[bold " + GOD.YELLOW + "]>> MODEL BENCHMARK <<[/]",
        title_style="bold " + GOD.YELLOW,
        padding=(0, 0),
        expand=False,
    )
    bench.add_column("#",   style=GOD.DIM, width=3)
    bench.add_column("MODEL", style="bold " + GOD.WHITE, width=30)
    bench.add_column("TIER", width=14)
    bench.add_column("CTX",  style=GOD.CYAN, width=12)
    bench.add_column("SPD",  style=GOD.YELLOW, width=10)
    bench.add_column("POWER", style=GOD.GREEN, width=12)
    bench.add_column("SCORE", style="bold " + GOD.NEON, width=7)

    for idx, mid in enumerate(sorted(KIMINI_MODELS.keys()), 1):
        m = KIMINI_MODELS[mid]
        sp = speed_rank.get(m["speed"], 75)
        ctx_score = min(100, m["context"] // 40000)
        score = (sp + ctx_score) // 2
        c = TIER_GLOW.get(m["tier"], GOD.WHITE)
        s = TIER_SIGIL.get(m["tier"], ">>")
        bar_len = score // 10
        power = "#" * bar_len + "." * (10 - bar_len)
        bench.add_row(
            "[" + GOD.DIM + "]" + str(idx) + "[/" + GOD.DIM + "]",
            mid,
            "[" + c + "]" + s + " " + m["tier"].upper() + "[/]",
            str(m["context"]),
            m["speed"],
            "[" + GOD.NEON + "]" + power + "[/" + GOD.NEON + "]",
            "[" + GOD.NEON + "]" + str(score) + "%[/" + GOD.NEON + "]",
        )

    return bench


# ============================================================
#  GODLIKE PANEL: TREE VIEW (tier hierarchy)
# ============================================================

def god_tier_tree():
    tree = Tree(
        "[bold " + GOD.GOLD + "]>> KIMINI MODEL TREE <<[/]",
        guide_style="bold " + GOD.DIM,
    )

    for tier in get_tiers():
        c = TIER_GLOW.get(tier, GOD.WHITE)
        s = TIER_SIGIL.get(tier, ">>")
        tier_branch = tree.add("[bold " + c + "]" + s + " " + tier.upper() + "[/]")
        models = get_models_by_tier(tier)
        for mid in sorted(models.keys()):
            m = models[mid]
            tier_branch.add(
                "[" + GOD.WHITE + "]" + mid + "[/" + GOD.WHITE + "] "
                "[" + GOD.DIM + "]v" + m["version"] + " | " + str(m["context"]) + " ctx | " + m["speed"] + "[/" + GOD.DIM + "]"
            )

    return Panel(
        tree,
        title="[bold " + GOD.PURPLE + "]>> MODEL HIERARCHY <<[/]",
        border_style=GOD.PURPLE,
        box=box.HEAVY,
        padding=(0, 1),
    )


# ============================================================
#  GODLIKE PANEL: QUICK ACTIONS (bottom left)
# ============================================================

def god_quick_actions():
    actions = Table(show_header=False, box=None, padding=(0, 0), expand=True)
    actions.add_column("A", style="bold " + GOD.CYAN, no_wrap=True)

    actions.add_row("[" + GOD.CYAN + "]ALT+L[/] [dim]Launch[/]")
    actions.add_row("[" + GOD.CYAN + "]ALT+C[/] [dim]Chat[/]")
    actions.add_row("[" + GOD.CYAN + "]ALT+M[/] [dim]Models[/]")
    actions.add_row("[" + GOD.CYAN + "]ALT+S[/] [dim]Select[/]")
    actions.add_row("[" + GOD.CYAN + "]ALT+B[/] [dim]Bench[/]")
    actions.add_row("[" + GOD.CYAN + "]ALT+Q[/] [dim]Quit[/]")

    return Panel(
        actions,
        title="[bold " + GOD.CYAN + "]>> HOTKEYS[/]",
        border_style=GOD.CYAN,
        box=box.ROUNDED,
        padding=(0, 1),
    )


# ============================================================
#  GODLIKE PANEL: LIVE STATS (sparkline)
# ============================================================

def god_live_stats():
    import random
    random.seed(int(time.time()))
    tokens = [random.randint(80, 100) for _ in range(20)]
    latency = [random.randint(1, 5) for _ in range(20)]
    throughput = [random.randint(70, 100) for _ in range(20)]

    stats = Table(show_header=False, box=None, padding=(0, 0))
    stats.add_column("K", style="bold " + GOD.CYAN, width=14)
    stats.add_column("V", width=22)

    stats.add_row(
        "[" + GOD.NEON + "]Tokens[/]",
        "[" + GOD.GREEN + "]~~~~~~~~[/] [" + GOD.DIM + "]" + sparkline(tokens) + "[/" + GOD.DIM + "]"
    )
    stats.add_row(
        "[" + GOD.YELLOW + "]Latency[/]",
        "[" + GOD.YELLOW + "]~~~~~~~~[/] [" + GOD.DIM + "]" + sparkline(latency, chars="..||") + "[/" + GOD.DIM + "]"
    )
    stats.add_row(
        "[" + GOD.CYAN + "]Throughput[/]",
        "[" + GOD.CYAN + "]~~~~~~~~[/] [" + GOD.DIM + "]" + sparkline(throughput) + "[/" + GOD.DIM + "]"
    )

    return Panel(
        stats,
        title="[bold " + GOD.NEON + "]>> LIVE METRICS[/]",
        border_style=GOD.NEON,
        box=box.ROUNDED,
        padding=(0, 1),
    )


# ============================================================
#  GODLIKE PANEL: INTERACTIVE HELP
# ============================================================

def god_help():
    help_table = Table(
        show_header=True,
        header_style="bold " + GOD.CYAN,
        box=box.HEAVY,
        border_style=GOD.CYAN,
        title="[bold " + GOD.CYAN + "]>> INTERACTIVE COMMANDS <<[/]",
        title_style="bold " + GOD.CYAN,
        padding=(0, 1),
        expand=False,
    )
    help_table.add_column("CMD", style="bold " + GOD.WHITE, width=20)
    help_table.add_column("WHAT IT DOES", style=GOD.DIM, width=40)

    help_table.add_row("[cyan]/exit, /quit, /q[/]",  "Shut down the platform")
    help_table.add_row("[cyan]/models[/]",            "Show all 56 models in table")
    help_table.add_row("[cyan]/use <model>[/]",       "Switch to a different model")
    help_table.add_row("[cyan]/info[/]",              "Show current model details")
    help_table.add_row("[cyan]/select[/]",            "Open visual A-Z model picker")
    help_table.add_row("[cyan]/bench[/]",             "Run full benchmark display")
    help_table.add_row("[cyan]/efficiency[/]",        "Show performance metrics")
    help_table.add_row("[cyan]/tree[/]",              "Show model hierarchy tree")
    help_table.add_row("[cyan]/live[/]",              "Show live metrics sparklines")
    help_table.add_row("[cyan]/status[/]",            "Platform status overview")
    help_table.add_row("[cyan]/clear[/]",             "Clear the terminal")
    help_table.add_row("[cyan]/help[/]",              "Show this help panel")

    console.print(help_table)


# ============================================================
#  GODLIKE LAYOUT: CENTERED SPLIT (left=selector, right=info)
# ============================================================

def god_split_layout(current_model, filter_letter=None):
    left_table = god_model_selector(current=current_model, filter_letter=filter_letter)
    right_panel = god_model_card(current_model)

    console.print(
        Columns(
            [
                Panel(
                    left_table,
                    title="[bold " + GOD.MAGENTA + "]>> MODELS A-Z <<[/]",
                    border_style=GOD.MAGENTA,
                    box=box.HEAVY,
                    width=62,
                ),
                right_panel,
            ],
            padding=(0, 1),
            expand=True,
        )
    )


# ============================================================
#  GODLIKE LAYOUT: FULL COMMAND CENTER
# ============================================================

def god_full_layout():
    god_banner()
    console.print()

    left_actions = god_quick_actions()
    left_stats = god_live_stats()

    right_commands = god_command_center()

    console.print(
        Columns(
            [
                Panel(
                    Columns([left_actions, left_stats], padding=(0, 1)),
                    border_style=GOD.CYAN,
                    box=box.ROUNDED,
                    title="[bold " + GOD.CYAN + "]>> QUICK ACCESS[/]",
                    width=48,
                ),
                right_commands,
            ],
            padding=(0, 1),
            expand=True,
        )
    )
    console.print()
    god_status_dock()


# ============================================================
#  GODLIKE: VISUAL MODEL SELECTOR (interactive)
# ============================================================

def god_visual_selector():
    console.clear()
    god_banner()
    god_letter_bar()
    console.print()

    current = DEFAULT_MODEL
    filter_letter = None

    while True:
        god_split_layout(current, filter_letter)
        console.print()

        console.print(
            Panel(
                Text.from_markup(
                    "[bold " + GOD.WHITE + "]SELECTOR COMMANDS[/]\n\n"
                    "[" + GOD.CYAN + "]a-z[/]      Filter by letter\n"
                    "[" + GOD.CYAN + "]all[/]      Show all 56 models\n"
                    "[" + GOD.CYAN + "]number[/]   Select model by #\n"
                    "[" + GOD.CYAN + "]name[/]     Select by model name\n"
                    "[" + GOD.CYAN + "]info[/]     Show model details\n"
                    "[" + GOD.CYAN + "]tree[/]     Show tier hierarchy\n"
                    "[" + GOD.CYAN + "]bench[/]    Run benchmark\n"
                    "[" + GOD.CYAN + "]back[/]     Return to main menu"
                ),
                border_style=GOD.GOLD,
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

        choice = Prompt.ask(
            "[bold " + GOD.GOLD + "]>> selector[/]",
            default="all",
        ).strip().lower()

        if choice == "back":
            return current
        elif choice == "all":
            filter_letter = None
            console.clear()
            god_banner()
        elif choice in string.ascii_lowercase:
            filter_letter = choice
            console.clear()
            god_banner()
        elif choice == "tree":
            console.print(god_tier_tree())
        elif choice == "bench":
            console.print(god_benchmark())
        elif choice.startswith("info"):
            parts = choice.split()
            if len(parts) > 1:
                god_model_card(parts[1])
            else:
                god_model_card(current)
        elif choice.isdigit():
            idx = int(choice) - 1
            all_m = get_all_model_ids()
            if filter_letter:
                all_m = [m for m in all_m if m[5:].startswith(filter_letter)]
            if 0 <= idx < len(all_m):
                current = all_m[idx]
                log_event("SELECT model=" + current)
                console.print("[bold " + GOD.NEON + "]Selected: " + current + "[/]")
            else:
                console.print("[bold " + GOD.RED + "]Invalid index[/]")
        elif choice.startswith("kimi-") or choice in KIMINI_MODELS:
            resolved = resolve_model(choice)
            if resolved:
                current = resolved
                log_event("SELECT model=" + current)
                console.print("[bold " + GOD.NEON + "]Selected: " + current + "[/]")
            else:
                console.print("[bold " + GOD.RED + "]Unknown: " + choice + "[/]")
        else:
            console.print("[" + GOD.DIM + "]Try a-z, all, number, name, info, tree, bench, back[/]")


# ============================================================
#  GODLIKE: RESPONSE SIMULATION
# ============================================================

def god_response(model_id, prompt):
    m = KIMINI_MODELS[model_id]
    c = TIER_GLOW.get(m["tier"], GOD.WHITE)
    s = TIER_SIGIL.get(m["tier"], ">>")
    word_count = max(10, min(len(prompt) * 3, m["context"] // 4) // 5)

    resp = Table(show_header=False, box=None, padding=(0, 0))
    resp.add_column("K", style="bold " + GOD.CYAN, width=18)
    resp.add_column("V", style="bold " + GOD.WHITE, width=42)

    resp.add_row("Model",        "[bold " + c + "]" + model_id + "[/]")
    resp.add_row("Tier",         "[" + c + "]" + s + " " + m["tier"].upper() + "[/]")
    resp.add_row("Context",      str(m["context"]) + " tokens " + ctx_bar(m["context"]))
    resp.add_row("Speed",        speed_bar(m["speed"]) + " " + m["speed"])
    resp.add_row("Capabilities", ", ".join(m["caps"]))
    resp.add_row("Tokens",       "[bold " + GOD.NEON + "]UNLIMITED[/]")
    resp.add_row("Prompt",       str(len(prompt)) + " chars")
    resp.add_row("Output",       "~" + str(word_count) + " tokens")
    resp.add_row("Efficiency",   "[bold " + GOD.GOLD + "]9329423949324932942394329429%[/]")

    console.print(
        Panel(
            resp,
            title="[bold " + c + "]>> RESPONSE <<[/]",
            border_style=c,
            box=box.HEAVY,
            padding=(1, 2),
        )
    )
    log_event("PROMPT model=" + model_id + " len=" + str(len(prompt)))


# ============================================================
#  GODLIKE: INTERACTIVE LAUNCH
# ============================================================

def god_chat_header(model_id):
    """Show the chat header panel with model info."""
    m = KIMINI_MODELS[model_id]
    c = TIER_GLOW.get(m["tier"], GOD.WHITE)
    s = TIER_SIGIL.get(m["tier"], ">>")

    info = Table(show_header=False, box=None, padding=(0, 0))
    info.add_column("K", style="bold " + GOD.CYAN, width=12)
    info.add_column("V", style="bold " + GOD.WHITE, width=28)

    info.add_row("Model",    "[bold " + c + "]" + model_id + "[/]")
    info.add_row("Tier",     "[" + c + "]" + s + " " + m["tier"].upper() + "[/]")
    info.add_row("Context",  str(m["context"]) + " tokens")
    info.add_row("Speed",    m["speed"])
    info.add_row("Tokens",   "[bold " + GOD.NEON + "]UNLIMITED[/]")

    console.print(
        Panel(
            info,
            title="[bold " + c + "]>> " + model_id.upper() + " <<[/]",
            border_style=c,
            box=box.HEAVY,
            padding=(0, 2),
        )
    )


def god_chat_help():
    """Show chat commands help."""
    help_table = Table(
        show_header=True,
        header_style="bold " + GOD.CYAN,
        box=box.HEAVY,
        border_style=GOD.CYAN,
        title="[bold " + GOD.CYAN + "]>> CHAT COMMANDS <<[/]",
        padding=(0, 1),
        expand=False,
    )
    help_table.add_column("CMD", style="bold " + GOD.WHITE, width=22)
    help_table.add_column("DOES", style=GOD.DIM, width=38)

    help_table.add_row("[cyan]/exit, /quit, /q[/]",  "Exit chat")
    help_table.add_row("[cyan]/use <model>[/]",       "Switch to a different model")
    help_table.add_row("[cyan]/info[/]",              "Show current model details")
    help_table.add_row("[cyan]/models[/]",            "List all 56 models")
    help_table.add_row("[cyan]/select[/]",            "Open visual model picker")
    help_table.add_row("[cyan]/bench[/]",             "Run benchmark")
    help_table.add_row("[cyan]/efficiency[/]",        "Performance metrics")
    help_table.add_row("[cyan]/tree[/]",              "Model hierarchy tree")
    help_table.add_row("[cyan]/live[/]",              "Live metrics sparklines")
    help_table.add_row("[cyan]/clear[/]",             "Clear chat history")
    help_table.add_row("[cyan]/history[/]",           "Show chat history")
    help_table.add_row("[cyan]/system[/]",            "Show system info")
    help_table.add_row("[cyan]/help[/]",              "Show this help")

    console.print(help_table)


def god_chat_box(model=None):
    """
    Centered chat box interface with DEEP MEMORY + GODLIKE IMPACT SCORING.
    Like Kilo / OpenCode / Cursor but with persistent memory construction.
    """
    from .deep_memory import DeepMemoryEngine
    from .deep_reasoning import DeepReasoningEngine

    if not model:
        model = DEFAULT_MODEL
    resolved = resolve_model(model)
    if not resolved:
        console.print("[bold " + GOD.RED + "]Unknown model: " + model + "[/]")
        return

    console.clear()

    current_model = resolved
    m = KIMINI_MODELS[current_model]
    c = TIER_GLOW.get(m["tier"], GOD.WHITE)

    memory = DeepMemoryEngine()
    reasoning = DeepReasoningEngine()

    history = []
    msg_count = 0
    total_tokens = 0
    total_impact = 0

    god_chat_header(current_model)
    console.print()

    mem_stats = memory.get_memory_stats()
    console.print(
        Panel(
            Align.center(
                Text.from_markup(
                    "[bold " + GOD.WHITE + "]Type a message to chat with " + current_model + "[/]\n"
                    "[" + GOD.DIM + "]Commands: /use, /info, /models, /select, /bench, /help, /clear, /history, /memory, /knowledge, /impact, /quit[/]"
                )
            ),
            border_style=GOD.DIM,
            box=box.ROUNDED,
            padding=(0, 2),
            title="[bold " + GOD.CYAN + "]>> CHAT <<[/]",
            subtitle="[dim]Deep Memory + Godlike Impact Scoring Enabled | " + str(mem_stats["total_interactions"]) + " memories stored[/]",
        )
    )
    console.print()

    log_event("CHAT_START model=" + current_model)

    while True:
        try:
            user_input = Prompt.ask(
                "[bold " + GOD.CYAN + "]You[/] [dim]>[/]"
            )
        except (EOFError, KeyboardInterrupt):
            console.print("\n[" + GOD.DIM + "]Chat ended.[/]")
            break

        cmd = user_input.strip().lower()

        if not cmd:
            continue

        if cmd in ("/exit", "/quit", "/q"):
            console.print()
            session_stats = reasoning.get_session_stats()
            mem_stats = memory.get_memory_stats()
            console.print(
                Panel(
                    Align.center(
                        Text.from_markup(
                            "[bold " + GOD.WHITE + "]Chat Session Summary[/]\n\n"
                            "[bold " + GOD.CYAN + "]Messages:[/] " + str(msg_count) + "\n"
                            "[bold " + GOD.CYAN + "]Model:[/] " + current_model + "\n"
                            "[bold " + GOD.CYAN + "]Tokens:[/] " + str(total_tokens) + "\n"
                            "[bold " + GOD.CYAN + "]Avg Impact:[/] " + str(session_stats["avg"]) + "/100\n"
                            "[bold " + GOD.CYAN + "]Max Impact:[/] " + str(session_stats["max"]) + "/100\n"
                            "[bold " + GOD.CYAN + "]Total Impact:[/] " + str(round(session_stats["total"], 1)) + "\n"
                            "[bold " + GOD.NEON + "]Godlike Score:[/] " + str(mem_stats["godlike_score"]) + "\n"
                            "[bold " + GOD.NEON + "]Memories:[/] " + str(mem_stats["total_interactions"]) + " stored\n"
                            "[bold " + GOD.NEON + "]Status:[/] SESSION_ENDED"
                        )
                    ),
                    title="[bold " + GOD.GOLD + "]>> GOODBYE <<[/]",
                    border_style=GOD.GOLD,
                    box=box.HEAVY,
                    padding=(1, 4),
                )
            )
            log_event("CHAT_END msgs=" + str(msg_count) + " impact=" + str(round(session_stats["total"], 1)))
            break

        if cmd == "/help":
            god_chat_help()
            continue

        if cmd == "/clear":
            history.clear()
            msg_count = 0
            total_tokens = 0
            total_impact = 0
            console.clear()
            god_chat_header(current_model)
            console.print()
            console.print(
                Panel(
                    Align.center(Text.from_markup("[bold " + GOD.NEON + "]Chat history cleared.[/]")),
                    border_style=GOD.NEON,
                    box=box.ROUNDED,
                    padding=(0, 2),
                )
            )
            console.print()
            continue

        if cmd == "/info":
            console.print(god_model_card(current_model))
            continue

        if cmd == "/models":
            console.print(god_model_selector(current=current_model))
            continue

        if cmd == "/select":
            current_model = god_visual_selector()
            m = KIMINI_MODELS[current_model]
            c = TIER_GLOW.get(m["tier"], GOD.WHITE)
            console.print()
            console.print(
                Panel(
                    Align.center(
                        Text.from_markup("[bold " + GOD.NEON + "]Switched to: " + current_model + "[/]")
                    ),
                    border_style=GOD.NEON,
                    box=box.ROUNDED,
                    padding=(0, 2),
                )
            )
            god_chat_header(current_model)
            console.print()
            log_event("CHAT_SWITCH model=" + current_model)
            continue

        if cmd == "/bench":
            console.print(god_benchmark())
            continue

        if cmd == "/efficiency":
            console.print(god_efficiency())
            continue

        if cmd == "/tree":
            console.print(god_tier_tree())
            continue

        if cmd == "/live":
            console.print(god_live_stats())
            continue

        if cmd == "/memory":
            mem_stats = memory.get_memory_stats()
            mem_table = Table(
                title="[bold " + GOD.GOLD + "]>> DEEP MEMORY STATUS <<[/]",
                box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1),
            )
            mem_table.add_column("METRIC", style="bold " + GOD.CYAN, width=22)
            mem_table.add_column("VALUE", style="bold " + GOD.WHITE, width=35)
            mem_table.add_column("BAR", style=GOD.NEON, width=12)

            mem_table.add_row("Total Interactions", str(mem_stats["total_interactions"]), "")
            mem_table.add_row("Total Tokens", str(mem_stats["total_tokens"]), "")
            mem_table.add_row("Memory Strength", str(mem_stats["memory_strength"]) + "%", "[" + GOD.NEON + "]" + memory.get_memory_strength_bar() + "[/" + GOD.NEON + "]")
            mem_table.add_row("Concepts Learned", str(mem_stats["concept_count"]), "")
            mem_table.add_row("Relations Found", str(mem_stats["relation_count"]), "")
            mem_table.add_row("Avg Impact", str(mem_stats["avg_impact"]) + "/100", "")
            mem_table.add_row("Total Impact", str(mem_stats["total_impact"]), "")
            mem_table.add_row("Reasoning Depth", str(mem_stats["reasoning_depth"]) + "/100", "")
            mem_table.add_row("Godlike Score", str(mem_stats["godlike_score"]) + "/100", "[" + GOD.NEON + "]" + memory.get_godlike_bar() + "[/" + GOD.NEON + "]")

            console.print(mem_table)

            if mem_stats["strongest_concepts"]:
                console.print()
                console.print(
                    "[" + GOD.DIM + "]Strongest Concepts: " +
                    ", ".join(mem_stats["strongest_concepts"][:10]) + "[/]"
                )
            continue

        if cmd == "/knowledge":
            kg = memory.get_knowledge_graph_summary()
            console.print()
            console.print(
                Panel(
                    Align.center(
                        Text.from_markup("[bold " + GOD.WHITE + "]>> KNOWLEDGE GRAPH <<[/]")
                    ),
                    border_style=GOD.MAGENTA,
                    box=box.HEAVY,
                    padding=(0, 2),
                )
            )
            if kg["top_concepts"]:
                concept_table = Table(
                    title="[bold " + GOD.CYAN + "]>> TOP CONCEPTS <<[/]",
                    box=box.ROUNDED, border_style=GOD.CYAN, padding=(0, 1),
                )
                concept_table.add_column("#", style=GOD.DIM, width=3)
                concept_table.add_column("CONCEPT", style="bold " + GOD.WHITE, width=25)
                for i, concept in enumerate(kg["top_concepts"][:15], 1):
                    concept_table.add_row(str(i), concept)
                console.print(concept_table)

            if kg["top_relations"]:
                console.print()
                rel_table = Table(
                    title="[bold " + GOD.MAGENTA + "]>> TOP RELATIONS <<[/]",
                    box=box.ROUNDED, border_style=GOD.MAGENTA, padding=(0, 1),
                )
                rel_table.add_column("FROM", style="bold " + GOD.CYAN, width=18)
                rel_table.add_column("TO", style="bold " + GOD.CYAN, width=18)
                rel_table.add_column("WEIGHT", style=GOD.NEON, width=10)
                for rel in kg["top_relations"][:10]:
                    rel_table.add_row(rel["from"], rel["to"], str(rel["weight"]))
                console.print(rel_table)
            continue

        if cmd == "/impact":
            session_stats = reasoning.get_session_stats()
            console.print()
            console.print(
                Panel(
                    Text.from_markup(
                        "[bold " + GOD.WHITE + "]>> SESSION IMPACT ANALYSIS <<[/]\n\n"
                        "[bold " + GOD.CYAN + "]Messages:[/] " + str(session_stats["count"]) + "\n"
                        "[bold " + GOD.CYAN + "]Avg Impact:[/] " + str(session_stats["avg"]) + "/100\n"
                        "[bold " + GOD.CYAN + "]Max Impact:[/] " + str(session_stats["max"]) + "/100\n"
                        "[bold " + GOD.CYAN + "]Min Impact:[/] " + str(session_stats["min"]) + "/100\n"
                        "[bold " + GOD.CYAN + "]Total Impact:[/] " + str(round(session_stats["total"], 1)) + "\n"
                        "[bold " + GOD.NEON + "]Godlike Score:[/] " + str(session_stats["godlike_avg"]) + "/1000"
                    ),
                    title="[bold " + GOD.GOLD + "]>> IMPACT <<[/]",
                    border_style=GOD.GOLD,
                    box=box.HEAVY,
                    padding=(1, 2),
                )
            )
            continue

        if cmd == "/history":
            if not history:
                console.print("[" + GOD.DIM + "]No messages yet.[/]")
            else:
                console.print()
                console.print(
                    Panel(
                        Align.center(
                            Text.from_markup("[bold " + GOD.WHITE + "]Chat History (" + str(len(history)) + " messages)[/]")
                        ),
                        border_style=GOD.CYAN,
                        box=box.ROUNDED,
                        padding=(0, 2),
                    )
                )
                for entry in history[-20:]:
                    role = entry["role"]
                    content = entry["content"]
                    if role == "user":
                        console.print(
                            Panel(
                                Text.from_markup("[bold " + GOD.WHITE + "]" + content + "[/]"),
                                title="[bold " + GOD.CYAN + "]You[/]",
                                border_style=GOD.CYAN,
                                box=box.ROUNDED,
                                padding=(0, 1),
                            )
                        )
                    else:
                        impact = entry.get("impact", "?")
                        tier = entry.get("godlike_tier", "?")
                        console.print(
                            Panel(
                                Text.from_markup(content),
                                title="[bold " + GOD.NEON + "]" + entry["model"] + "[/] [dim]| Impact: " + str(impact) + " | Tier: " + tier + "[/]",
                                border_style=GOD.NEON,
                                box=box.ROUNDED,
                                padding=(0, 1),
                            )
                        )
            continue

        if cmd == "/system":
            mem_stats = memory.get_memory_stats()
            console.print(
                Panel(
                    Text.from_markup(
                        "[bold " + GOD.WHITE + "]System Information[/]\n\n"
                        "[bold " + GOD.CYAN + "]Platform:[/] Melodie-Kimini GODLIKE v3.1.0\n"
                        "[bold " + GOD.CYAN + "]Model:[/] " + current_model + "\n"
                        "[bold " + GOD.CYAN + "]Tier:[/] " + m["tier"].upper() + "\n"
                        "[bold " + GOD.CYAN + "]Context:[/] " + str(m["context"]) + " tokens\n"
                        "[bold " + GOD.CYAN + "]Speed:[/] " + m["speed"] + "\n"
                        "[bold " + GOD.CYAN + "]Capabilities:[/] " + ", ".join(m["caps"]) + "\n"
                        "[bold " + GOD.CYAN + "]Messages:[/] " + str(msg_count) + "\n"
                        "[bold " + GOD.CYAN + "]Total Tokens:[/] " + str(total_tokens) + "\n"
                        "[bold " + GOD.NEON + "]Deep Memory:[/] " + str(mem_stats["total_interactions"]) + " stored\n"
                        "[bold " + GOD.NEON + "]Godlike Score:[/] " + str(mem_stats["godlike_score"]) + "\n"
                        "[bold " + GOD.NEON + "]Status:[/] ONLINE"
                    ),
                    title="[bold " + GOD.GOLD + "]>> SYSTEM <<[/]",
                    border_style=GOD.GOLD,
                    box=box.HEAVY,
                    padding=(1, 2),
                )
            )
            continue

        if cmd.startswith("/use "):
            new_name = cmd[5:].strip()
            new_resolved = resolve_model(new_name)
            if new_resolved:
                current_model = new_resolved
                m = KIMINI_MODELS[current_model]
                c = TIER_GLOW.get(m["tier"], GOD.WHITE)
                console.print()
                console.print(
                    Panel(
                        Align.center(
                            Text.from_markup("[bold " + GOD.NEON + "]Switched to: " + current_model + "[/]")
                        ),
                        border_style=GOD.NEON,
                        box=box.ROUNDED,
                        padding=(0, 2),
                    )
                )
                god_chat_header(current_model)
                console.print()
                log_event("CHAT_SWITCH model=" + current_model)
            else:
                console.print("[bold " + GOD.RED + "]Unknown model: " + new_name + "[/]")
            continue

        msg_count += 1
        history.append({"role": "user", "content": user_input})

        analysis = reasoning.analyze_interaction(user_input, current_model)
        impact_score = analysis["impact_score"]
        godlike_tier = analysis["godlike_tier"]
        total_impact += impact_score

        related_memory = memory.recall_related(user_input, limit=3)
        concept_context = memory.get_concept_context(user_input)

        m = KIMINI_MODELS[current_model]
        c = TIER_GLOW.get(m["tier"], GOD.WHITE)
        s = TIER_SIGIL.get(m["tier"], ">>")
        word_count = max(10, min(len(user_input) * 3, m["context"] // 4) // 5)
        tokens_used = len(user_input) // 4 + word_count
        total_tokens += tokens_used

        tier_color = reasoning.get_tier_color(godlike_tier)

        resp_content = Table(show_header=False, box=None, padding=(0, 0))
        resp_content.add_column("K", style="bold " + GOD.CYAN, width=16)
        resp_content.add_column("V", style="bold " + GOD.WHITE, width=48)

        resp_content.add_row("Model",       "[bold " + c + "]" + current_model + "[/]")
        resp_content.add_row("Tier",        "[" + c + "]" + s + " " + m["tier"].upper() + "[/]")
        resp_content.add_row("Context",     str(m["context"]) + " tokens " + ctx_bar(m["context"]))
        resp_content.add_row("Speed",       speed_bar(m["speed"]) + " " + m["speed"])
        resp_content.add_row("Tokens",      "[bold " + GOD.NEON + "]UNLIMITED[/]")
        resp_content.add_row("Prompt",      str(len(user_input)) + " chars")
        resp_content.add_row("Output",      "~" + str(word_count) + " tokens")

        console.print(
            Panel(
                resp_content,
                title="[bold " + c + "]>> " + current_model.upper() + " <<[/]",
                border_style=c,
                box=box.HEAVY,
                padding=(1, 2),
            )
        )

        impact_table = Table(show_header=False, box=None, padding=(0, 0))
        impact_table.add_column("K", style="bold " + GOD.CYAN, width=16)
        impact_table.add_column("V", style="bold " + GOD.WHITE, width=30)
        impact_table.add_column("BAR", style=GOD.NEON, width=14)

        impact_table.add_row("Impact Score",   str(impact_score) + "/100", "[" + GOD.NEON + "]" + reasoning.get_impact_bar(impact_score) + "[/" + GOD.NEON + "]")
        impact_table.add_row("Godlike Tier",   "[" + tier_color + "]" + godlike_tier + "[/" + tier_color + "]", "")
        impact_table.add_row("Reasoning",      str(round(analysis["reasoning_depth"], 1)) + "/100", "")
        impact_table.add_row("Concepts",       ", ".join(analysis["concepts"][:5]), "")
        impact_table.add_row("Session Impact", str(round(total_impact, 1)), "")

        if related_memory:
            impact_table.add_row("Memories",   str(len(related_memory)) + " recalled", "")
        if concept_context:
            impact_table.add_row("Knowledge",  str(len(concept_context)) + " concepts", "")

        console.print(
            Panel(
                impact_table,
                title="[bold " + GOD.GOLD + "]>> DEEP IMPACT <<[/]",
                border_style=GOD.GOLD,
                box=box.HEAVY,
                padding=(1, 2),
            )
        )
        console.print()

        memory.remember_interaction(
            user_input, "response_" + str(word_count), current_model,
            impact_score, analysis
        )

        history.append({
            "role": "assistant",
            "model": current_model,
            "content": "[Model: " + current_model + "] ~" + str(word_count) + " tokens generated",
            "impact": impact_score,
            "godlike_tier": godlike_tier,
        })

        log_event("CHAT_MSG model=" + current_model + " len=" + str(len(user_input)) + " impact=" + str(impact_score) + " tier=" + godlike_tier)


def god_interactive(model=None):
    """Legacy interactive mode - redirects to chat box."""
    god_chat_box(model)


# ============================================================
#  GODLIKE: CENTERED INTERACTIVE CLI TOOLBOX
#  Like Gemini CLI, Kilo, GitHub Copilot, Devin, Cursor
# ============================================================

def god_toolbox_header():
    """Show the centered toolbox header with status."""
    console.print()
    console.print(
        Panel(
            Align.center(
                Text(BANNER_LOGO, style="bold " + GOD.CYAN)
            ),
            border_style=GOD.CYAN,
            box=box.HEAVY,
            padding=(0, 0),
            title="[bold " + GOD.GOLD + "]>> M E L O D I E - K I M I N I <<[/]",
            subtitle="[dim]GODLIKE COMMAND CENTER v3.1.0 | " + ts_full() + "[/]",
        )
    )

    status_line = (
        "[bold " + GOD.WHITE + "]56 MODELS  /  UNLIMITED TOKENS  /  "
        "MAXIMUM EFFICIENCY[/]"
    )
    console.print(
        Panel(
            Align.center(Text.from_markup(status_line)),
            border_style=GOD.GOLD,
            box=box.DOUBLE,
            padding=(0, 2),
        )
    )

    try:
        from .proxy import ProxyRouter
        router = ProxyRouter()
        warning = router.get_offline_warning()
        if warning:
            console.print(
                Panel(
                    Align.center(
                        Text.from_markup(
                            "[bold bright_yellow]!! " + warning["warning"] + " !![/]\n"
                            "[bright_yellow]" + warning["detail"] + "[/]"
                        )
                    ),
                    border_style="bright_yellow",
                    box=box.HEAVY,
                    padding=(0, 2),
                    title="[bold bright_yellow]>> OFFLINE MODE <<[/]",
                )
            )
    except Exception:
        pass


def god_toolbox_grid():
    """Show the centered quick action grid + command table side by side."""
    left_actions = Table(show_header=False, box=None, padding=(0, 0), expand=True)
    left_actions.add_column("A", style="bold " + GOD.CYAN, no_wrap=True)
    left_actions.add_row("[" + GOD.CYAN + "]ALT+L[/] [dim]Launch[/]")
    left_actions.add_row("[" + GOD.CYAN + "]ALT+C[/] [dim]Chat[/]")
    left_actions.add_row("[" + GOD.CYAN + "]ALT+M[/] [dim]Models[/]")
    left_actions.add_row("[" + GOD.CYAN + "]ALT+S[/] [dim]Select[/]")
    left_actions.add_row("[" + GOD.CYAN + "]ALT+B[/] [dim]Bench[/]")
    left_actions.add_row("[" + GOD.CYAN + "]ALT+Q[/] [dim]Quit[/]")

    left_stats = Table(show_header=False, box=None, padding=(0, 0))
    left_stats.add_column("K", style="bold " + GOD.CYAN, width=14)
    left_stats.add_column("V", width=22)

    import random
    random.seed(int(time.time()))
    tokens = [random.randint(80, 100) for _ in range(20)]
    latency = [random.randint(1, 5) for _ in range(20)]
    throughput = [random.randint(70, 100) for _ in range(20)]

    left_stats.add_row(
        "[" + GOD.NEON + "]Tokens[/]",
        "[" + GOD.GREEN + "]~~~~~~~~[/] [" + GOD.DIM + "]" + sparkline(tokens) + "[/" + GOD.DIM + "]"
    )
    left_stats.add_row(
        "[" + GOD.YELLOW + "]Latency[/]",
        "[" + GOD.YELLOW + "]~~~~~~~~[/] [" + GOD.DIM + "]" + sparkline(latency, chars="..||") + "[/" + GOD.DIM + "]"
    )
    left_stats.add_row(
        "[" + GOD.CYAN + "]Throughput[/]",
        "[" + GOD.CYAN + "]~~~~~~~~[/] [" + GOD.DIM + "]" + sparkline(throughput) + "[/" + GOD.DIM + "]"
    )

    cmds = Table(
        show_header=True,
        header_style="bold " + GOD.GOLD,
        box=box.HEAVY,
        border_style=GOD.GOLD,
        title="[bold " + GOD.GOLD + "]>> COMMAND CENTER <<[/]",
        title_style="bold " + GOD.GOLD,
        padding=(0, 1),
        expand=False,
    )
    cmds.add_column("KEY", style="bold " + GOD.CYAN, width=5, no_wrap=True)
    cmds.add_column("CMD", style="bold " + GOD.WHITE, width=18, no_wrap=True)
    cmds.add_column("DOES", style=GOD.DIM, width=28, no_wrap=True)
    cmds.add_column("HOTKEY", style="bold " + GOD.YELLOW, width=8, no_wrap=True)

    cmds.add_row("[cyan]1[/]", "launch",    "Launch platform",           "L")
    cmds.add_row("[cyan]2[/]", "chat",      "Interactive chat",          "C")
    cmds.add_row("[cyan]3[/]", "list",      "Show all 56 models",        "M")
    cmds.add_row("[cyan]4[/]", "info",      "Model details",             "I")
    cmds.add_row("[cyan]5[/]", "run",       "Execute prompt",            "R")
    cmds.add_row("[cyan]6[/]", "select",    "Visual model picker",       "S")
    cmds.add_row("[cyan]7[/]", "bench",     "Benchmark all models",      "B")
    cmds.add_row("[cyan]8[/]", "efficiency","Performance metrics",       "E")
    cmds.add_row("[cyan]9[/]", "status",    "Platform status",           "T")
    cmds.add_row("[cyan]0[/]", "quit",      "Exit platform",             "Q")

    console.print(
        Columns(
            [
                Panel(
                    Columns([left_actions, left_stats], padding=(0, 1)),
                    border_style=GOD.CYAN,
                    box=box.ROUNDED,
                    title="[bold " + GOD.CYAN + "]>> QUICK ACCESS[/]",
                    width=48,
                ),
                cmds,
            ],
            padding=(0, 1),
            expand=True,
        )
    )


def god_toolbox_commands():
    """Show all available commands in the toolbox."""
    help_table = Table(
        show_header=True,
        header_style="bold " + GOD.CYAN,
        box=box.HEAVY,
        border_style=GOD.CYAN,
        title="[bold " + GOD.CYAN + "]>> TOOLBOX COMMANDS <<[/]",
        title_style="bold " + GOD.CYAN,
        padding=(0, 1),
        expand=False,
    )
    help_table.add_column("CMD", style="bold " + GOD.WHITE, width=20)
    help_table.add_column("WHAT IT DOES", style=GOD.DIM, width=40)

    help_table.add_row("[cyan]launch[/]",       "Launch the full command center")
    help_table.add_row("[cyan]chat[/]",          "Start interactive chat (Deep Memory)")
    help_table.add_row("[cyan]run <prompt>[/]",  "Execute a prompt with impact score")
    help_table.add_row("[cyan]list[/]",          "Show all 56 models")
    help_table.add_row("[cyan]select[/]",        "Open visual model picker")
    help_table.add_row("[cyan]info[/]",          "Show current model details")
    help_table.add_row("[cyan]bench[/]",         "Run full benchmark")
    help_table.add_row("[cyan]efficiency[/]",    "Show performance metrics")
    help_table.add_row("[cyan]status[/]",        "Platform status overview")
    help_table.add_row("[cyan]memory[/]",        "Deep Memory status & stats")
    help_table.add_row("[cyan]knowledge[/]",     "Knowledge graph view")
    help_table.add_row("[cyan]impact[/]",        "Impact score analysis")
    help_table.add_row("[cyan]karma[/]",         "Score prompt for karma")
    help_table.add_row("[cyan]wallet[/]",        "View MA Token wallet")
    help_table.add_row("[cyan]mine[/]",          "Start crypto mining")
    help_table.add_row("[cyan]combo[/]",         "Combo streak & ascension")
    help_table.add_row("[cyan]plans[/]",         "View subscription plans")
    help_table.add_row("[cyan]enterprise[/]",    "Enterprise business ranking")
    help_table.add_row("[cyan]proxy[/]",         "Proxy routing status")
    help_table.add_row("[cyan]share[/]",         "Social media sharing")
    help_table.add_row("[cyan]help[/]",          "Show this help panel")
    help_table.add_row("[cyan]clear[/]",         "Clear the terminal")
    help_table.add_row("[cyan]quit[/]",          "Exit the toolbox")

    console.print(help_table)


def god_toolbox_input_box():
    """Draw a centered input box with prompt."""
    console.print()
    console.print(
        Panel(
            Align.center(
                Text.from_markup(
                    "[bold " + GOD.WHITE + "]Type a command or prompt below[/]\n"
                    "[" + GOD.DIM + "]Commands: launch, chat, run, list, select, info, bench, "
                    "efficiency, status, memory, knowledge, impact, karma, wallet, mine, "
                    "combo, plans, enterprise, proxy, share, help, clear, quit[/]"
                )
            ),
            border_style=GOD.CYAN,
            box=box.ROUNDED,
            padding=(1, 4),
            title="[bold " + GOD.CYAN + "]>> K I M I N I   T O O L B O X <<[/]",
            subtitle="[dim]Enter 'help' for full command list | 'quit' to exit[/]",
        )
    )


def god_toolbox(model=None):
    """Centered interactive CLI toolbox - like Gemini, Kilo, Copilot, Devin, Cursor."""
    console.clear()
    god_toolbox_header()
    god_toolbox_grid()
    god_toolbox_input_box()
    console.print()

    if not model:
        model = DEFAULT_MODEL
    resolved = resolve_model(model)
    if not resolved:
        console.print("[bold " + GOD.RED + "]Unknown model: " + model + "[/]")
        return

    current_model = resolved
    m = KIMINI_MODELS[current_model]
    c = TIER_GLOW.get(m["tier"], GOD.WHITE)

    log_event("TOOLBOX_LAUNCH model=" + current_model)

    while True:
        try:
            user_input = Prompt.ask(
                "[bold " + GOD.CYAN + "]>> [/][bold " + GOD.GOLD + "]kimini[/] [dim]>[/]"
            )
        except (EOFError, KeyboardInterrupt):
            console.print("\n[" + GOD.DIM + "]Goodbye.[/]")
            break

        cmd = user_input.strip().lower()

        if not cmd:
            continue

        if cmd in ("quit", "exit", "q", "/quit", "/exit", "/q"):
            console.print("[" + GOD.DIM + "]Shutting down...[/]")
            log_event("TOOLBOX_SHUTDOWN")
            break

        if cmd == "clear":
            console.clear()
            god_toolbox_header()
            god_toolbox_grid()
            god_toolbox_input_box()
            console.print()
            continue

        if cmd == "help":
            god_toolbox_commands()
            continue

        if cmd == "launch":
            console.clear()
            god_toolbox_header()
            god_toolbox_grid()
            god_toolbox_input_box()
            console.print()
            continue

        if cmd == "chat":
            god_interactive(current_model)
            console.clear()
            god_toolbox_header()
            god_toolbox_grid()
            god_toolbox_input_box()
            console.print()
            continue

        if cmd == "list":
            console.clear()
            god_banner()
            god_letter_bar()
            console.print()
            console.print(god_model_selector(current=current_model))
            console.print()
            god_toolbox_input_box()
            console.print()
            continue

        if cmd == "select":
            current_model = god_visual_selector()
            m = KIMINI_MODELS[current_model]
            c = TIER_GLOW.get(m["tier"], GOD.WHITE)
            console.print("[bold " + GOD.NEON + "]Switched to: " + current_model + "[/]")
            log_event("TOOLBOX_SWITCH model=" + current_model)
            continue

        if cmd == "info":
            console.print(god_model_card(current_model))
            continue

        if cmd == "bench":
            console.print(god_benchmark())
            continue

        if cmd == "efficiency":
            console.print(god_efficiency())
            continue

        if cmd == "status":
            console.clear()
            god_full_layout()
            console.print()
            god_toolbox_input_box()
            console.print()
            continue

        if cmd == "tree":
            console.print(god_tier_tree())
            continue

        if cmd == "live":
            console.print(god_live_stats())
            continue

        if cmd == "karma":
            console.print("[" + GOD.DIM + "]Usage: run <prompt> to score karma[/]")
            continue

        if cmd == "memory":
            try:
                from .deep_memory import DeepMemoryEngine
                mem = DeepMemoryEngine()
                stats = mem.get_memory_stats()
                table = Table(title="[bold " + GOD.GOLD + "]>> DEEP MEMORY <<[/]", box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1))
                table.add_column("METRIC", style="bold " + GOD.CYAN, width=22)
                table.add_column("VALUE", style="bold " + GOD.WHITE, width=30)
                table.add_column("BAR", style=GOD.NEON, width=12)
                table.add_row("Interactions", str(stats["total_interactions"]), "")
                table.add_row("Tokens", str(stats["total_tokens"]), "")
                table.add_row("Strength", str(stats["memory_strength"]) + "%", "[" + GOD.NEON + "]" + mem.get_memory_strength_bar() + "[/" + GOD.NEON + "]")
                table.add_row("Concepts", str(stats["concept_count"]), "")
                table.add_row("Relations", str(stats["relation_count"]), "")
                table.add_row("Avg Impact", str(stats["avg_impact"]) + "/100", "")
                table.add_row("Godlike", str(stats["godlike_score"]) + "/100", "[" + GOD.NEON + "]" + mem.get_godlike_bar() + "[/" + GOD.NEON + "]")
                console.print(table)
                if stats["strongest_concepts"]:
                    console.print("[" + GOD.DIM + "]Top: " + ", ".join(stats["strongest_concepts"][:8]) + "[/]")
            except Exception as e:
                console.print("[bold " + GOD.RED + "]Error: " + str(e) + "[/]")
            continue

        if cmd == "knowledge":
            try:
                from .deep_memory import DeepMemoryEngine
                mem = DeepMemoryEngine()
                kg = mem.get_knowledge_graph_summary()
                console.print(Panel(Align.center(Text.from_markup("[bold " + GOD.WHITE + "]>> KNOWLEDGE GRAPH <<[/]")), border_style=GOD.MAGENTA, box=box.HEAVY, padding=(0, 2)))
                if kg["top_concepts"]:
                    ct = Table(title="[bold " + GOD.CYAN + "]CONCEPTS[/]", box=box.ROUNDED, border_style=GOD.CYAN, padding=(0, 1))
                    ct.add_column("#", style=GOD.DIM, width=3)
                    ct.add_column("CONCEPT", style="bold " + GOD.WHITE, width=25)
                    for i, concept in enumerate(kg["top_concepts"][:10], 1):
                        ct.add_row(str(i), concept)
                    console.print(ct)
                if kg["top_relations"]:
                    rt = Table(title="[bold " + GOD.MAGENTA + "]RELATIONS[/]", box=box.ROUNDED, border_style=GOD.MAGENTA, padding=(0, 1))
                    rt.add_column("FROM", style="bold " + GOD.CYAN, width=18)
                    rt.add_column("TO", style="bold " + GOD.CYAN, width=18)
                    rt.add_column("W", style=GOD.NEON, width=8)
                    for rel in kg["top_relations"][:8]:
                        rt.add_row(rel["from"], rel["to"], str(rel["weight"]))
                    console.print(rt)
            except Exception as e:
                console.print("[bold " + GOD.RED + "]Error: " + str(e) + "[/]")
            continue

        if cmd == "impact":
            try:
                from .deep_reasoning import DeepReasoningEngine
                reason = DeepReasoningEngine()
                stats = reason.get_session_stats()
                console.print(Panel(
                    Text.from_markup(
                        "[bold " + GOD.WHITE + "]>> IMPACT ANALYSIS <<[/]\n\n"
                        "[bold " + GOD.CYAN + "]Session Messages:[/] " + str(stats["count"]) + "\n"
                        "[bold " + GOD.CYAN + "]Avg Impact:[/] " + str(stats["avg"]) + "/100\n"
                        "[bold " + GOD.CYAN + "]Max Impact:[/] " + str(stats["max"]) + "/100\n"
                        "[bold " + GOD.CYAN + "]Total Impact:[/] " + str(round(stats["total"], 1)) + "\n"
                        "[bold " + GOD.NEON + "]Godlike Score:[/] " + str(stats["godlike_avg"]) + "/1000"
                    ),
                    title="[bold " + GOD.GOLD + "]>> IMPACT <<[/]",
                    border_style=GOD.GOLD, box=box.HEAVY, padding=(1, 2),
                ))
            except Exception as e:
                console.print("[bold " + GOD.RED + "]Error: " + str(e) + "[/]")
            continue

        if cmd == "wallet":
            try:
                from .ma_token import MATokenWallet
                w = MATokenWallet()
                wd = w.get_wallet("default")
                est_daily = w.estimate_daily_earn("default")
                wall = Table(show_header=False, box=None, padding=(0, 0))
                wall.add_column("K", style="bold " + GOD.CYAN, width=18)
                wall.add_column("V", style="bold " + GOD.WHITE, width=35)
                wall.add_row("Balance",      "[" + GOD.GOLD + "]" + str(round(wd["balance"], 2)) + " MA[/]")
                wall.add_row("Staked",       "[" + GOD.CYAN + "]" + str(round(wd["staked"], 2)) + " MA[/]")
                wall.add_row("Total Earned", str(round(wd["total_earned"], 2)) + " MA")
                wall.add_row("Streak",       str(wd["streak"]) + " days")
                wall.add_row("Est. Daily",   "[" + GOD.NEON + "]" + str(est_daily) + " MA/day[/]")
                console.print(Panel(wall, title="[bold " + GOD.GOLD + "]>> MA TOKEN WALLET <<[/]", border_style=GOD.GOLD, box=box.HEAVY, padding=(1, 2)))
            except Exception as e:
                console.print("[bold " + GOD.RED + "]Error: " + str(e) + "[/]")
            continue

        if cmd == "mine":
            try:
                from .mining import MiningEngine
                mining = MiningEngine()
                block = mining.mine_block("default")
                status = block.get("status", "unknown")
                earned = block.get("earned", 0)
                if status == "not_mining":
                    console.print("[" + GOD.YELLOW + "]Not mining. Start with: mine start[/]")
                elif status == "blocked":
                    console.print("[" + GOD.RED + "]Mining blocked: " + block.get("reason", "unknown") + "[/]")
                elif status == "rate_limited":
                    console.print("[" + GOD.YELLOW + "]Rate limited. Wait a moment.[/]")
                else:
                    console.print("[bold " + GOD.NEON + "]Mined block! Earned: " + str(earned) + " MA[/]")
            except Exception as e:
                console.print("[bold " + GOD.RED + "]Error: " + str(e) + "[/]")
            continue

        if cmd == "combo":
            try:
                from .combo import ComboEngine
                combo = ComboEngine()
                cs = combo.get_user("default")
                streak = cs.get("streak", 0)
                rank = cs.get("ascension_rank", "Bronze")
                mult = cs.get("multiplier", 1.0)
                console.print("[bold " + GOD.CYAN + "]Combo Streak:[/] " + str(streak) + " hits")
                console.print("[bold " + GOD.GOLD + "]Ascension Rank:[/] " + rank)
                console.print("[bold " + GOD.NEON + "]Multiplier:[/] x" + str(mult))
            except Exception as e:
                console.print("[bold " + GOD.RED + "]Error: " + str(e) + "[/]")
            continue

        if cmd == "plans":
            try:
                from .subscription import SubscriptionEngine
                sub = SubscriptionEngine()
                comparison = sub.get_plan_comparison()
                table = Table(title="[bold " + GOD.GOLD + "]>> SUBSCRIPTION PLANS <<[/]", box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1))
                table.add_column("PLAN", width=14, style="bold")
                table.add_column("MONTHLY", width=12)
                table.add_column("LIFETIME", width=12)
                table.add_column("FEATURES", width=10)
                for p in comparison:
                    c = p["color"]
                    price_m = "$" + str(round(p["price"], 2)) + "/mo" if p["price"] > 0 else "FREE"
                    price_l = "$" + str(int(p["lifetime"])) + " once" if p["lifetime"] > 0 else "-"
                    table.add_row("[" + c + "]" + p["icon"] + " " + p["name"] + "[/" + c + "]", "[" + c + "]" + price_m + "[/" + c + "]", "[" + c + "]" + price_l + "[/" + c + "]", str(p["features_count"]))
                console.print(table)
            except Exception as e:
                console.print("[bold " + GOD.RED + "]Error: " + str(e) + "[/]")
            continue

        if cmd == "enterprise":
            try:
                from .enterprise import EnterpriseScorer
                ent = EnterpriseScorer()
                rankings = ent.get_global_rankings(limit=10)
                table = Table(title="[bold " + GOD.GOLD + "]>> ENTERPRISE RANKINGS <<[/]", box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1))
                table.add_column("RANK", style="bold " + GOD.CYAN, width=6)
                table.add_column("NAME", style="bold " + GOD.WHITE, width=30)
                table.add_column("KARMA", style=GOD.NEON, width=12)
                table.add_column("TIER", style=GOD.GOLD, width=15)
                for i, r in enumerate(rankings, 1):
                    table.add_row(str(i), r["name"], str(round(r.get("crypto_karma", 0), 1)), r.get("rank", "N/A"))
                console.print(table)
            except Exception as e:
                console.print("[bold " + GOD.RED + "]Error: " + str(e) + "[/]")
            continue

        if cmd == "proxy":
            try:
                from .proxy import ProxyRouter
                router = ProxyRouter()
                status = router.get_status()
                table = Table(title="[bold " + GOD.CYAN + "]>> PROXY STATUS <<[/]", box=box.HEAVY, border_style=GOD.CYAN, padding=(0, 1))
                table.add_column("METRIC", style="bold " + GOD.WHITE, width=20)
                table.add_column("VALUE", style=GOD.NEON, width=30)
                is_on = status.get("is_online", False)
                table.add_row("Mode", status.get("mode", "UNKNOWN"))
                table.add_row("Online", "[green]YES[/]" if is_on else "[yellow]NO (Offline Mode)[/]")
                table.add_row("Platforms Online", str(status.get("platforms_online", 0)))
                table.add_row("Platforms Tracked", str(status.get("platforms_tracked", 0)))
                console.print(table)
            except Exception as e:
                console.print("[bold " + GOD.RED + "]Error: " + str(e) + "[/]")
            continue

        if cmd == "share":
            try:
                from .social import SOCIAL_PLATFORMS
                table = Table(title="[bold " + GOD.MAGENTA + "]>> SOCIAL PLATFORMS <<[/]", box=box.HEAVY, border_style=GOD.MAGENTA, padding=(0, 1))
                table.add_column("PLATFORM", style="bold " + GOD.WHITE, width=20)
                table.add_column("CHARS", style=GOD.CYAN, width=10)
                table.add_column("TYPE", style=GOD.DIM, width=15)
                for pid, pdata in SOCIAL_PLATFORMS.items():
                    table.add_row(pdata["name"], str(pdata.get("max_chars", "N/A")), pdata.get("type", "social"))
                console.print(table)
            except Exception as e:
                console.print("[bold " + GOD.RED + "]Error: " + str(e) + "[/]")
            continue

        if cmd.startswith("run "):
            prompt_text = user_input.strip()[4:]
            if prompt_text:
                try:
                    from .deep_reasoning import DeepReasoningEngine
                    from .deep_memory import DeepMemoryEngine
                    reason = DeepReasoningEngine()
                    mem = DeepMemoryEngine()
                    analysis = reason.analyze_interaction(prompt_text, current_model)
                    impact_score = analysis["impact_score"]
                    godlike_tier = analysis["godlike_tier"]
                    tier_color = reason.get_tier_color(godlike_tier)

                    god_response(current_model, prompt_text)

                    impact_table = Table(show_header=False, box=None, padding=(0, 0))
                    impact_table.add_column("K", style="bold " + GOD.CYAN, width=16)
                    impact_table.add_column("V", style="bold " + GOD.WHITE, width=30)
                    impact_table.add_column("BAR", style=GOD.NEON, width=14)
                    impact_table.add_row("Impact Score", str(impact_score) + "/100", "[" + GOD.NEON + "]" + reason.get_impact_bar(impact_score) + "[/" + GOD.NEON + "]")
                    impact_table.add_row("Godlike Tier", "[" + tier_color + "]" + godlike_tier + "[/" + tier_color + "]", "")
                    impact_table.add_row("Reasoning", str(round(analysis["reasoning_depth"], 1)) + "/100", "")
                    impact_table.add_row("Concepts", ", ".join(analysis["concepts"][:5]), "")

                    console.print(Panel(impact_table, title="[bold " + GOD.GOLD + "]>> DEEP IMPACT <<[/]", border_style=GOD.GOLD, box=box.HEAVY, padding=(1, 2)))

                    mem.remember_interaction(prompt_text, "response", current_model, impact_score, analysis)
                except Exception as e:
                    god_response(current_model, prompt_text)
            else:
                console.print("[" + GOD.DIM + "]Usage: run <your prompt>[/]")
            continue

        if cmd.startswith("/use "):
            new_name = cmd[5:].strip()
            new_resolved = resolve_model(new_name)
            if new_resolved:
                current_model = new_resolved
                m = KIMINI_MODELS[current_model]
                c = TIER_GLOW.get(m["tier"], GOD.WHITE)
                console.print("[bold " + GOD.NEON + "]Switched to: " + current_model + "[/]")
                log_event("TOOLBOX_SWITCH model=" + current_model)
            else:
                console.print("[bold " + GOD.RED + "]Unknown model: " + new_name + "[/]")
            continue

        god_response(current_model, user_input)


# ============================================================
#  CLICK CLI GROUP
# ============================================================

@click.group()
@click.version_option(version="3.1.0", prog_name="Melodie-Kimini")
def cli():
    """Melodie-Kimini GODLIKE Command Center - 56 Models, Unlimited Tokens"""
    pass


@cli.command()
@click.option("--model", "-m", default=None, help="Model to launch")
def launch(model):
    """Launch the godlike command center with centered CLI toolbox."""
    god_toolbox(model)


@cli.command()
@click.option("--model", "-m", default=DEFAULT_MODEL, help="Model to chat with")
def chat(model):
    """Start godlike interactive chat."""
    god_interactive(model)


@cli.command("list-models")
@click.option("--tier", "-t", default=None, help="Filter by tier")
@click.option("--version", "-v", default=None, help="Filter by version")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--user", "-u", default="default", help="User ID for plan lock display")
def list_models(tier, version, as_json, user):
    """List all 56 models with godlike visuals."""
    models = KIMINI_MODELS.copy()
    if tier:
        models = {k: v for k, v in models.items() if v["tier"] == tier}
    if version:
        models = {k: v for k, v in models.items() if v["version"] == version}

    if as_json:
        click.echo(json.dumps(models, indent=2))
        return

    from .subscription import SubscriptionEngine
    sub = SubscriptionEngine()
    allowed = sub.get_allowed_tiers(user)

    console.clear()
    god_banner()
    console.print()
    god_letter_bar()
    console.print()

    table = Table(
        title="[bold " + GOD.GOLD + "]>> MODEL SELECTOR <<[/]",
        box=box.HEAVY, border_style=GOD.MAGENTA,
        padding=(0, 0),
    )
    table.add_column("#", style=GOD.DIM, width=3)
    table.add_column("MODEL ID", style="bold " + GOD.WHITE, width=30)
    table.add_column("TIER", width=14)
    table.add_column("V", width=4)
    table.add_column("CTX", style=GOD.CYAN, width=12)
    table.add_column("STATUS", width=10)

    for idx, (mid, mdata) in enumerate(models.items(), 1):
        c = TIER_GLOW.get(mdata["tier"], GOD.WHITE)
        s = TIER_SIGIL.get(mdata["tier"], ">>")
        locked = mdata["tier"] not in allowed
        status = "[bright_red]LOCKED[/]" if locked else "[bright_green]ACCESS[/]"
        table.add_row(
            "[" + GOD.DIM + "]" + str(idx) + "[/" + GOD.DIM + "]",
            mid,
            "[" + c + "]" + s + " " + mdata["tier"].upper() + "[/]",
            mdata["version"],
            str(mdata["context"]),
            status,
        )

    console.print(table)
    console.print()
    god_status_dock()
    log_event("LIST_MODELS count=" + str(len(models)))


@cli.command("model-info")
@click.argument("model_id")
def model_info(model_id):
    """Show godlike model info card."""
    resolved = resolve_model(model_id)
    if not resolved:
        console.print("[bold " + GOD.RED + "]Unknown model: " + model_id + "[/]")
        sys.exit(1)
    god_model_card(resolved)
    log_event("MODEL_INFO id=" + resolved)


@cli.command()
@click.argument("prompt")
@click.option("--model", "-m", default=DEFAULT_MODEL, help="Model to use")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--user", "-u", default="default", help="User ID for subscription check")
def run(prompt, model, as_json, user):
    """Run a prompt with godlike visual output."""
    resolved = resolve_model(model)
    if not resolved:
        console.print("[bold " + GOD.RED + "]Unknown model: " + model + "[/]")
        sys.exit(1)

    model_tier = KIMINI_MODELS[resolved]["tier"]
    from .subscription import SubscriptionEngine
    sub = SubscriptionEngine()
    if not sub.can_access_model(user, model_tier):
        allowed = sub.get_allowed_tiers(user)
        console.print("[bold " + GOD.RED + "]PLAN RESTRICTED[/] Your plan does NOT include " + model_tier.upper() + " tier models.")
        console.print("[" + GOD.DIM + "]Allowed tiers: " + ", ".join(allowed).upper() + "[/]")
        console.print("[" + GOD.DIM + "]Upgrade: Melodie-Kimini upgrade-plan[/]")
        log_event("PLAN_RESTRICTED model=" + resolved + " user=" + user)
        sys.exit(1)

    if as_json:
        m = KIMINI_MODELS[resolved]
        click.echo(json.dumps({
            "model": resolved, "tier": m["tier"], "version": m["version"],
            "context": m["context"], "tokens": "unlimited", "prompt": prompt,
            "response": "Processed by " + resolved + " with unlimited tokens",
            "efficiency": "9329423949324932942394329429%", "timestamp": ts_full(),
        }, indent=2))
    else:
        god_response(resolved, prompt)
    log_event("RUN model=" + resolved + " prompt_len=" + str(len(prompt)))


@cli.command()
def status():
    """Show godlike platform status."""
    console.clear()
    god_full_layout()
    log_event("STATUS")


@cli.command()
def select():
    """Open the godlike visual model selector."""
    selected = god_visual_selector()
    console.print()
    console.print(
        Panel(
            Text.from_markup(
                "[bold " + GOD.NEON + "]>> FINAL SELECTION: " + selected + " <<[/]\n\n"
                "[" + GOD.DIM + "]Launch with: [bold " + GOD.CYAN + "]Melodie-Kimini launch -m " + selected + "[/][/]"
            ),
            border_style=GOD.NEON,
            box=box.HEAVY,
        )
    )


@cli.command()
def bench():
    """Run godlike model benchmark."""
    console.clear()
    god_banner()
    console.print()
    console.print(god_benchmark())
    console.print()
    god_status_dock()
    log_event("BENCHMARK")


@cli.command()
def efficiency():
    """Show godlike performance metrics."""
    console.clear()
    console.print(god_efficiency())
    console.print()
    god_status_dock()
    log_event("EFFICIENCY")


@cli.command()
def tree():
    """Show godlike model hierarchy tree."""
    console.clear()
    console.print(god_tier_tree())
    console.print()
    god_status_dock()
    log_event("TREE")


@cli.command()
@click.option("--dir", default=".", help="Installation directory")
def setup(dir):
    """Initialize platform directories."""
    dirs = [os.path.join(dir, d) for d in ["logs", "config", "cache", "models"]]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        console.print("[" + GOD.NEON + "]Created:[/] " + d)

    config_path = os.path.join(dir, "config", "kimini.json")
    if not os.path.exists(config_path):
        config = {
            "platform": "melodie-kimini", "version": "3.1.0",
            "default_model": DEFAULT_MODEL, "token_mode": "unlimited",
            "total_models": 56, "tiers": get_tiers(),
            "versions": get_versions(),
            "efficiency": "9329423949324932942394329429%",
            "created": ts_full(),
        }
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        console.print("[" + GOD.NEON + "]Config:[/] " + config_path)

    console.print(
        Panel(
            Text.from_markup(
                "[bold " + GOD.NEON + "]>> SETUP COMPLETE <<[/]\n\n"
                "[" + GOD.DIM + "]Run [bold " + GOD.CYAN + "]Melodie-Kimini launch[/] to start\n"
                "Or: [bold " + GOD.CYAN + "]Melodie-Kimini select[/] for visual picker[/]"
            ),
            border_style=GOD.NEON,
            box=box.HEAVY,
        )
    )
    log_event("SETUP_COMPLETE")


# ============================================================
#  KARMA POWER COMMANDS
# ============================================================

@cli.command()
@click.argument("prompt")
@click.option("--user", "-u", default="default", help="User ID")
def karma(prompt, user):
    """Score a prompt for positive/negative impact and earn Karma Power Points."""
    from .karma import KarmaScorer
    from .impact import score_to_visual
    from .combo import ComboEngine, get_ascension_rank
    from .hype import render_impact_hype_popup, render_level_up_popup, render_mini_hype_line
    from .time_earn import TimeEarnEngine

    scorer = KarmaScorer()
    combo_eng = ComboEngine()
    time_eng = TimeEarnEngine()
    result = scorer.score_prompt(prompt, user)
    vis = score_to_visual(result["total_score"], result["is_positive"], result["is_negative"], result["dimensions"])

    if result["is_negative"]:
        bar_c = "bright_red"
        label_c = "bright_red"
        border_c = GOD.RED
    elif result["is_positive"]:
        bar_c = "bright_green"
        label_c = "bright_green"
        border_c = GOD.NEON
    else:
        bar_c = GOD.WHITE
        label_c = GOD.WHITE
        border_c = GOD.DIM

    console.print()

    impact = Table(show_header=False, box=None, padding=(0, 0))
    impact.add_column("K", style="bold " + GOD.CYAN, width=18)
    impact.add_column("V", style="bold " + GOD.WHITE, width=40)

    impact.add_row("Prompt",        prompt[:60])
    impact.add_row("Impact",        "[" + label_c + "]" + vis["label"] + "[/]")
    impact.add_row("Score",         "[" + bar_c + "]" + str(result["total_score"]) + "[/]")
    impact.add_row("Visual",        "[" + bar_c + "]" + vis["bar"] + "[/]")
    impact.add_row("User",          user)
    impact.add_row("Level",         str(scorer.get_user(user)["level"]))

    for dim in vis["dimensions"][:6]:
        impact.add_row(
            "[" + dim["color"] + "]" + dim["icon"] + " " + dim["name"] + "[/]",
            "[" + dim["color"] + "]" + dim["bar"] + "[/] " + str(dim["score"]),
        )

    console.print(
        Panel(
            impact,
            title="[bold " + border_c + "]>> KARMA POWER POINTS <<[/]",
            border_style=border_c,
            box=box.HEAVY,
            padding=(1, 2),
        )
    )

    user_data = scorer.get_user(user)
    ku = user_data
    karma_val = ku["karma"]

    time_result = time_eng.record_action(user, abs(result["total_score"]))

    if result["is_positive"] and result["total_score"] > 0:
        combo_data = combo_eng.record_positive(user, abs(result["total_score"]), result["total_score"])
        rank = get_ascension_rank(karma_val)
        console.print(render_impact_hype_popup(
            prompt, result["total_score"], rank["name"],
            combo_data["combo"], karma_val,
        ))
        if time_result["boost_pct"] > 0:
            console.print(
                "  [" + time_result["tier_color"] + "]>> TIME BOOST: +" +
                str(time_result["boost_pct"]) + "% (" + time_result["tier_label"] + ")[/]"
            )

    console.print(
        "  [" + GOD.DIM + "]Karma: " + str(karma_val) +
        " | Level: " + str(ku["level"]) +
        " | Title: " + ku["title"] + "[/]"
    )
    console.print("  " + render_mini_hype_line(
        combo_eng.get_user(user)["combo"],
        combo_eng.get_user(user)["tier"],
        ku["title"],
        karma_val,
    ))
    log_event("KARMA score=" + str(result["total_score"]) + " user=" + user)


@cli.command()
@click.option("--user", "-u", default="default", help="User ID")
def karma_profile(user):
    """View your Karma Power Points profile and achievements."""
    from .karma import KarmaScorer

    scorer = KarmaScorer()
    u = scorer.get_user(user)

    prof = Table(show_header=False, box=None, padding=(0, 0))
    prof.add_column("K", style="bold " + GOD.CYAN, width=18)
    prof.add_column("V", style="bold " + GOD.WHITE, width=40)

    prof.add_row("User",            user)
    prof.add_row("Karma",           str(u["karma"]))
    prof.add_row("Level",           str(u["level"]))
    prof.add_row("Title",           "[" + GOD.GOLD + "]" + u["title"] + "[/]")
    prof.add_row("Sessions",        str(u["total_sessions"]))
    prof.add_row("Positive",        "[" + GOD.NEON + "]" + str(u["positive_count"]) + "[/]")
    prof.add_row("Negative",        "[" + GOD.RED + "]" + str(u["negative_count"]) + "[/]")
    prof.add_row("Achievements",    ", ".join(u["achievements"]) if u["achievements"] else "None yet")

    console.print(
        Panel(
            prof,
            title="[bold " + GOD.GOLD + "]>> KARMA PROFILE <<[/]",
            border_style=GOD.GOLD,
            box=box.HEAVY,
            padding=(1, 2),
        )
    )
    log_event("KARMA_PROFILE user=" + user)


# ============================================================
#  MA TOKEN COMMANDS
# ============================================================

@cli.command()
@click.option("--user", "-u", default="default", help="User ID")
def wallet(user):
    """View your MA Token wallet balance and stats."""
    from .ma_token import MATokenWallet

    w = MATokenWallet()
    wd = w.get_wallet(user)
    est_daily = w.estimate_daily_earn(user)

    wall = Table(show_header=False, box=None, padding=(0, 0))
    wall.add_column("K", style="bold " + GOD.CYAN, width=18)
    wall.add_column("V", style="bold " + GOD.WHITE, width=35)

    wall.add_row("User",            user)
    wall.add_row("Balance",         "[" + GOD.GOLD + "]" + str(round(wd["balance"], 2)) + " MA[/]")
    wall.add_row("Staked",          "[" + GOD.CYAN + "]" + str(round(wd["staked"], 2)) + " MA[/]")
    wall.add_row("Total Earned",    str(round(wd["total_earned"], 2)) + " MA")
    wall.add_row("Total Spent",     str(round(wd["total_spent"], 2)) + " MA")
    wall.add_row("Daily Earned",    str(round(wd["daily_earned"], 2)) + " MA")
    wall.add_row("Streak",          str(wd["streak"]) + " days")
    wall.add_row("Transactions",    str(wd["transactions"]))
    wall.add_row("Est. Daily",      "[" + GOD.NEON + "]" + str(est_daily) + " MA/day[/]")

    console.print(
        Panel(
            wall,
            title="[bold " + GOD.GOLD + "]>> MA TOKEN WALLET <<[/]",
            border_style=GOD.GOLD,
            box=box.HEAVY,
            padding=(1, 2),
        )
    )

    g = w.get_global()
    console.print(
        "  [" + GOD.DIM + "]Supply: " + str(round(g["total_supply"], 2)) +
        " MA | Staked: " + str(round(g["total_staked"], 2)) + " MA | Rate: 10 MA = 1 Karma[/]"
    )
    log_event("WALLET user=" + user)


@cli.command()
@click.argument("karma_pts", type=float)
@click.option("--user", "-u", default="default", help="User ID")
def convert(karma_pts, user):
    """Convert Karma Power Points to MA Tokens (10 MA per 1 Karma)."""
    from .ma_token import MATokenWallet, CONVERSION_RATE

    w = MATokenWallet()
    tx = w.convert_karma(user, karma_pts)

    console.print()
    console.print(
        Panel(
            Text.from_markup(
                "[bold " + GOD.GOLD + "]>> KARMA TO MA TOKEN CONVERSION <<[/]\n\n"
                "[" + GOD.WHITE + "]Karma Points  : [/]" + str(karma_pts) + "\n"
                "[" + GOD.WHITE + "]Conversion    : [/]1 Karma = " + str(CONVERSION_RATE) + " MA\n"
                "[" + GOD.WHITE + "]MA Earned     : [/][bold " + GOD.NEON + "]" + str(tx["amount"]) + " MA[/]\n"
                "[" + GOD.WHITE + "]New Balance   : [/][bold " + GOD.GOLD + "]" + str(tx["balance_after"]) + " MA[/]"
            ),
            border_style=GOD.GOLD,
            box=box.HEAVY,
            padding=(1, 2),
        )
    )
    log_event("CONVERT karma=" + str(karma_pts) + " ma=" + str(tx["amount"]) + " user=" + user)


@cli.command()
@click.argument("amount", type=float)
@click.option("--user", "-u", default="default", help="User ID")
def stake(amount, user):
    """Stake MA Tokens for 12% APY rewards."""
    from .ma_token import MATokenWallet, STAKING_APY

    w = MATokenWallet()
    result = w.stake(user, amount)

    if result is None:
        console.print("[bold " + GOD.RED + "]Insufficient balance to stake " + str(amount) + " MA[/]")
        return

    daily_reward = w.calc_staking_reward(user)
    console.print()
    console.print(
        Panel(
            Text.from_markup(
                "[bold " + GOD.CYAN + "]>> MA TOKEN STAKING <<[/]\n\n"
                "[" + GOD.WHITE + "]Staked        : [/][bold " + GOD.CYAN + "]" + str(amount) + " MA[/]\n"
                "[" + GOD.WHITE + "]APY           : [/]" + str(STAKING_APY * 100) + "%\n"
                "[" + GOD.WHITE + "]Daily Reward  : [/][bold " + GOD.NEON + "]" + str(daily_reward) + " MA/day[/]\n"
                "[" + GOD.WHITE + "]Balance       : [/]" + str(round(result["balance"], 2)) + " MA"
            ),
            border_style=GOD.CYAN,
            box=box.HEAVY,
            padding=(1, 2),
        )
    )
    log_event("STAKE amount=" + str(amount) + " user=" + user)


@cli.command()
@click.option("--user", "-u", default=None, help="Filter by user")
@click.option("--limit", "-l", default=10, help="Number of transactions")
def tx_history(user, limit):
    """View MA Token transaction history."""
    from .ma_token import MATokenWallet

    w = MATokenWallet()
    txs = w.get_transactions(user, limit)

    table = Table(
        show_header=True, header_style="bold " + GOD.CYAN,
        box=box.HEAVY, border_style=GOD.CYAN,
        title="[bold " + GOD.CYAN + "]>> MA TOKEN TRANSACTIONS <<[/]",
        padding=(0, 1),
    )
    table.add_column("TIME", style=GOD.DIM, width=20)
    table.add_column("CATEGORY", width=18)
    table.add_column("AMOUNT", width=12)
    table.add_column("BALANCE", width=12)
    table.add_column("DESC", style=GOD.DIM, width=25)

    for tx in reversed(txs):
        amt = tx["amount"]
        if amt >= 0:
            amt_str = "[" + GOD.NEON + "]+" + str(round(amt, 2)) + "[/]"
        else:
            amt_str = "[" + GOD.RED + "]" + str(round(amt, 2)) + "[/]"
        table.add_row(
            tx["timestamp"][:19],
            tx["category"],
            amt_str,
            str(round(tx["balance_after"], 2)),
            tx["desc"][:25],
        )

    console.print(table)


# ============================================================
#  LEADERBOARD COMMANDS
# ============================================================

@cli.command()
def leaderboard():
    """Show global leaderboards for positive impact."""
    from .leaderboard import Leaderboard

    lb = Leaderboard()
    top_users = lb.get_top_users(10)
    top_projects = lb.get_top_projects(10)

    user_table = Table(
        show_header=True, header_style="bold " + GOD.GOLD,
        box=box.HEAVY, border_style=GOD.GOLD,
        title="[bold " + GOD.GOLD + "]>> TOP USERS <<[/]",
        padding=(0, 1),
    )
    user_table.add_column("RANK", style="bold " + GOD.YELLOW, width=6)
    user_table.add_column("USER", style="bold " + GOD.WHITE, width=20)
    user_table.add_column("KARMA", style="bold " + GOD.NEON, width=12)
    user_table.add_column("CONTRIBS", width=10)

    medals = ["[bright_yellow]#1 GOLD[/]", "[white]#2 SLVR[/]", "[bright_red]#3 BRNZ[/]"]
    for i, (uid, data) in enumerate(top_users):
        rank = medals[i] if i < 3 else "[" + GOD.DIM + "]#" + str(i+1) + "[/]"
        user_table.add_row(rank, uid, str(round(data["total_karma"], 2)), str(data["total_contributions"]))

    proj_table = Table(
        show_header=True, header_style="bold " + GOD.NEON,
        box=box.HEAVY, border_style=GOD.NEON,
        title="[bold " + GOD.NEON + "]>> TOP PROJECTS <<[/]",
        padding=(0, 1),
    )
    proj_table.add_column("RANK", style="bold " + GOD.YELLOW, width=6)
    proj_table.add_column("PROJECT", style="bold " + GOD.WHITE, width=28)
    proj_table.add_column("KARMA", style="bold " + GOD.NEON, width=12)
    proj_table.add_column("CONTRIBS", width=10)
    proj_table.add_column("CAT", width=12)

    for i, (pid, data) in enumerate(top_projects):
        rank = medals[i] if i < 3 else "[" + GOD.DIM + "]#" + str(i+1) + "[/]"
        proj_table.add_row(rank, data["name"][:28], str(round(data["karma_generated"], 2)), str(data["contributions"]), data["category"])

    console.print()
    console.print(user_table)
    console.print()
    console.print(proj_table)
    console.print()
    log_event("LEADERBOARD")


@cli.command()
@click.argument("project_id")
@click.option("--user", "-u", default="default", help="User ID")
def contribute(project_id, user):
    """Contribute to a positive impact project."""
    from .leaderboard import Leaderboard
    from .karma import KarmaScorer

    lb = Leaderboard()
    proj = lb.get_project(project_id)
    if not proj:
        console.print("[bold " + GOD.RED + "]Project not found: " + project_id + "[/]")
        return

    scorer = KarmaScorer()
    fake_karma = 10.0
    result = lb.contribute(user, project_id, fake_karma)

    console.print()
    console.print(
        Panel(
            Text.from_markup(
                "[bold " + GOD.NEON + "]>> PROJECT CONTRIBUTION <<[/]\n\n"
                "[" + GOD.WHITE + "]Project       : [/][bold " + GOD.CYAN + "]" + result["name"] + "[/]\n"
                "[" + GOD.WHITE + "]Category      : [/]" + result["category"] + "\n"
                "[" + GOD.WHITE + "]Contributions : [/]" + str(result["contributions"]) + "\n"
                "[" + GOD.WHITE + "]Total Karma   : [/][bold " + GOD.NEON + "]" + str(round(result["karma_generated"], 2)) + "[/]\n"
                "[" + GOD.WHITE + "]Contributors  : [/]" + str(len(result["contributors"])) + "\n"
                "[" + GOD.WHITE + "]Your Karma    : [/][bold " + GOD.GOLD + "]+" + str(fake_karma) + "[/]"
            ),
            border_style=GOD.NEON,
            box=box.HEAVY,
            padding=(1, 2),
        )
    )
    log_event("CONTRIBUTE project=" + project_id + " user=" + user)


@cli.command("project-list")
def project_list():
    """List all positive impact projects."""
    from .leaderboard import Leaderboard

    lb = Leaderboard()
    projects = lb.get_all_projects()

    table = Table(
        show_header=True, header_style="bold " + GOD.NEON,
        box=box.HEAVY, border_style=GOD.NEON,
        title="[bold " + GOD.NEON + "]>> IMPACT PROJECTS <<[/]",
        padding=(0, 1),
    )
    table.add_column("ID", style="bold " + GOD.CYAN, width=18)
    table.add_column("NAME", style="bold " + GOD.WHITE, width=30)
    table.add_column("CATEGORY", width=14)
    table.add_column("CONTRIBS", width=10)
    table.add_column("KARMA", style=GOD.NEON, width=10)
    table.add_column("GOAL", width=8)

    for pid, data in projects.items():
        pct = min(100, int(data["karma_generated"] / max(data["goal"], 1) * 100))
        bar = "#" * (pct // 10) + "." * (10 - pct // 10)
        table.add_row(pid, data["name"][:30], data["category"], str(data["contributions"]),
                       "[" + GOD.NEON + "]" + bar + "[/] " + str(round(data["karma_generated"], 1)),
                       str(data["goal"]))

    console.print(table)


# ============================================================
#  MINING COMMANDS
# ============================================================

@cli.command()
@click.option("--user", "-u", default="default", help="User ID")
@click.option("--pool", "-p", default="karma_pool", help="Mining pool")
@click.option("--difficulty", "-d", default="medium", help="Difficulty: easy/medium/hard/extreme")
def mine(user, pool, difficulty):
    """Start legal positive impact crypto mining for MA Tokens."""
    from .mining import MiningEngine, MINING_POOLS, DIFFICULTY_LEVELS

    engine = MiningEngine()
    info = engine.start_mining(user, pool, difficulty)

    if not info:
        console.print("[bold " + GOD.RED + "]Invalid pool: " + pool + "[/]")
        return

    console.print()
    pool_table = Table(show_header=False, box=None, padding=(0, 0))
    pool_table.add_column("K", style="bold " + GOD.CYAN, width=18)
    pool_table.add_column("V", style="bold " + GOD.WHITE, width=35)

    pool_table.add_row("User",         user)
    pool_table.add_row("Pool",         "[" + GOD.CYAN + "]" + info["pool_desc"] + "[/]")
    pool_table.add_row("Difficulty",   info["difficulty"])
    pool_table.add_row("Hashrate",     str(info["hashrate"]) + " H/s")
    pool_table.add_row("Multiplier",   "x" + str(info["multiplier"]))
    pool_table.add_row("Block Chance", str(int(info["chance"] * 100)) + "%")
    pool_table.add_row("Status",       "[" + GOD.NEON + "]ACTIVE MINING[/]")

    console.print(
        Panel(
            pool_table,
            title="[bold " + GOD.NEON + "]>> CRYPTO MINING ACTIVE <<[/]",
            border_style=GOD.NEON,
            box=box.HEAVY,
            padding=(1, 2),
        )
    )

    console.print("  [" + GOD.DIM + "]Mining blocks... Run 'Melodie-Kimini mine-block' to collect[/]")
    log_event("MINE_START user=" + user + " pool=" + pool + " diff=" + difficulty)


@cli.command()
@click.option("--user", "-u", default="default", help="User ID")
def mine_block(user):
    """Mine a single block for MA Token rewards."""
    from .mining import MiningEngine

    engine = MiningEngine()
    result = engine.mine_block(user)

    if result["status"] == "not_mining":
        console.print("[bold " + GOD.RED + "]Not mining. Start with: Melodie-Kimini mine[/]")
        return

    if result["status"] == "success":
        console.print(
            "[bold " + GOD.NEON + "]BLOCK FOUND![/] " +
            "[bold " + GOD.GOLD + "]+" + str(result["earned"]) + " MA[/] " +
            "[dim]hash:" + result["block"]["hash"][:12] + "[/]"
        )
        log_event("MINE_BLOCK success earned=" + str(result["earned"]) + " user=" + user)
    else:
        console.print("[" + GOD.DIM + "]No block found. Keep mining...[/]")
        log_event("MINE_BLOCK miss user=" + user)


@cli.command()
@click.option("--user", "-u", default="default", help="User ID")
def mining_stats(user):
    """View mining statistics and pool activity."""
    from .mining import MiningEngine

    engine = MiningEngine()
    stats = engine.get_miner_stats(user)
    global_stats = engine.get_global_stats()
    pool_stats = engine.get_pool_stats()

    ms = Table(show_header=False, box=None, padding=(0, 0))
    ms.add_column("K", style="bold " + GOD.CYAN, width=18)
    ms.add_column("V", style="bold " + GOD.WHITE, width=35)

    ms.add_row("User",           user)
    ms.add_row("Active",         "[" + GOD.NEON + "]" + str(stats.get("active", False)) + "[/]")
    ms.add_row("Pool",           str(stats.get("pool", "None")))
    ms.add_row("Difficulty",     str(stats.get("difficulty", "None")))
    ms.add_row("Total Mined",    "[" + GOD.GOLD + "]" + str(stats.get("total_mined", 0)) + " MA[/]")
    ms.add_row("Blocks Found",   str(stats.get("blocks_found", 0)))
    ms.add_row("Sessions",       str(stats.get("sessions", 0)))
    ms.add_row("Global Mined",   str(round(global_stats.get("total_mined", 0), 2)) + " MA")
    ms.add_row("Global Blocks",  str(global_stats.get("total_blocks", 0)))

    console.print(
        Panel(
            ms,
            title="[bold " + GOD.CYAN + "]>> MINING STATS <<[/]",
            border_style=GOD.CYAN,
            box=box.HEAVY,
            padding=(1, 2),
        )
    )

    pool_table = Table(
        show_header=True, header_style="bold " + GOD.YELLOW,
        box=box.HEAVY, border_style=GOD.YELLOW,
        title="[bold " + GOD.YELLOW + "]>> POOL ACTIVITY <<[/]",
        padding=(0, 1),
    )
    pool_table.add_column("POOL", style="bold " + GOD.WHITE, width=22)
    pool_table.add_column("HASHRATE", width=10)
    pool_table.add_column("RATE", width=8)
    pool_table.add_column("BLOCKS", width=8)
    pool_table.add_column("REWARDS", style=GOD.NEON, width=10)

    for pid, data in pool_stats.items():
        pool_table.add_row(
            data["desc"][:22], str(data["hashrate"]) + " H/s",
            str(data["reward_rate"]), str(data["blocks"]),
            str(round(data["total_reward"], 2)) + " MA",
        )

    console.print(pool_table)
    log_event("MINING_STATS user=" + user)


@cli.command()
@click.option("--user", "-u", default="default", help="User ID")
@click.option("--minutes", "-m", default=5, help="Duration in minutes")
def mine_estimate(user, minutes):
    """Estimate mining earnings for a session."""
    from .mining import MiningEngine

    engine = MiningEngine()
    est = engine.estimate_session(user, minutes)

    console.print()
    console.print(
        Panel(
            Text.from_markup(
                "[bold " + GOD.GOLD + "]>> MINING ESTIMATE <<[/]\n\n"
                "[" + GOD.WHITE + "]Duration         : [/]" + str(minutes) + " minutes\n"
                "[" + GOD.WHITE + "]Expected Blocks  : [/]" + str(est["expected_blocks"]) + "\n"
                "[" + GOD.WHITE + "]Expected Success : [/]" + str(est["expected_success"]) + "\n"
                "[" + GOD.WHITE + "]Estimated Earn   : [/][bold " + GOD.NEON + "]" + str(est["estimated_earn"]) + " MA[/]"
            ),
            border_style=GOD.GOLD,
            box=box.HEAVY,
            padding=(1, 2),
        )
    )


# ============================================================
#  ECOSYSTEM OVERVIEW
# ============================================================

@cli.command()
def ecosystem():
    """Show the full Karma Power + MA Token ecosystem overview."""
    from .karma import KarmaScorer
    from .ma_token import MATokenWallet
    from .leaderboard import Leaderboard
    from .mining import MiningEngine

    scorer = KarmaScorer()
    w = MATokenWallet()
    lb = Leaderboard()
    engine = MiningEngine()

    g_karma = scorer.get_global_stats()
    g_wallet = w.get_global()
    g_mining = engine.get_global_stats()
    top_users = lb.get_top_users(5)

    console.clear()

    console.print(
        Panel(
            Align.center(
                Text.from_markup(
                    "[bold " + GOD.GOLD + "]KARMA POWER ECOSYSTEM[/]\n"
                    "[" + GOD.DIM + "]Positive Impact -> Karma Points -> MA Tokens -> Crypto[/]"
                )
            ),
            border_style=GOD.GOLD,
            box=box.DOUBLE,
            padding=(1, 2),
        )
    )

    stats = Table(show_header=False, box=None, padding=(0, 0))
    stats.add_column("K", style="bold " + GOD.CYAN, width=22)
    stats.add_column("V", style="bold " + GOD.WHITE, width=35)
    stats.add_column("K2", style="bold " + GOD.CYAN, width=22)
    stats.add_column("V2", style="bold " + GOD.WHITE, width=25)

    stats.add_row(
        "Global Karma",     "[" + GOD.NEON + "]" + str(round(g_karma["total_karma"], 2)) + "[/]",
        "Total Supply",     "[" + GOD.GOLD + "]" + str(round(g_wallet["total_supply"], 2)) + " MA[/]",
    )
    stats.add_row(
        "Total Prompts",    str(g_karma["total_prompts"]),
        "Total Staked",     "[" + GOD.CYAN + "]" + str(round(g_wallet["total_staked"], 2)) + " MA[/]",
    )
    stats.add_row(
        "Blocks Mined",     str(g_mining["total_blocks"]),
        "MA Mined",         "[" + GOD.NEON + "]" + str(round(g_mining["total_mined"], 2)) + " MA[/]",
    )
    stats.add_row(
        "Conversion Rate",  "1 Karma = 10 MA",
        "Staking APY",      "12%",
    )

    console.print(
        Panel(
            stats,
            title="[bold " + GOD.NEON + "]>> GLOBAL STATS <<[/]",
            border_style=GOD.NEON,
            box=box.HEAVY,
            padding=(1, 1),
        )
    )

    user_table = Table(
        show_header=True, header_style="bold " + GOD.GOLD,
        box=box.HEAVY, border_style=GOD.GOLD,
        title="[bold " + GOD.GOLD + "]>> TOP KARMA LEADERS <<[/]",
        padding=(0, 1),
    )
    user_table.add_column("RANK", width=6)
    user_table.add_column("USER", style="bold " + GOD.WHITE, width=20)
    user_table.add_column("KARMA", style="bold " + GOD.NEON, width=12)
    user_table.add_column("CONTRIBS", width=10)

    medals = ["[bright_yellow]#1[/]", "[white]#2[/]", "[bright_red]#3[/]"]
    for i, (uid, data) in enumerate(top_users):
        rank = medals[i] if i < 3 else "[" + GOD.DIM + "]#" + str(i+1) + "[/]"
        user_table.add_row(rank, uid, str(round(data["total_karma"], 2)), str(data["total_contributions"]))

    console.print(user_table)

    console.print()
    console.print(
        "[" + GOD.DIM + "]Commands: [bold " + GOD.CYAN + "]karma[/] score | [bold " + GOD.CYAN + "]wallet[/] balance | "
        "[bold " + GOD.CYAN + "]leaderboard[/] rankings | [bold " + GOD.CYAN + "]mine[/] crypto | "
        "[bold " + GOD.CYAN + "]convert[/] karma->MA | [bold " + GOD.CYAN + "]stake[/] earn APY | "
        "[bold " + GOD.CYAN + "]project-list[/] projects | [bold " + GOD.CYAN + "]contribute[/] impact[/]"
    )
    log_event("ECOSYSTEM_OVERVIEW")


# ============================================================
#  COMBO + ASCENSION COMMANDS
# ============================================================

@cli.command()
@click.argument("prompt")
@click.option("--user", "-u", default="default", help="User ID")
def combo(prompt, user):
    """Score a prompt and trigger combo multiplier chain."""
    from .karma import KarmaScorer
    from .combo import ComboEngine
    from .effects import (
        render_combo_counter, render_combo_hit, render_combo_broken,
        render_combo_panel, render_rank_card, render_rank_up,
        render_achievement_popup, render_combo_progress,
    )

    scorer = KarmaScorer()
    combo_eng = ComboEngine()
    result = scorer.score_prompt(prompt, user)

    if result.get("error"):
        console.print("[bold " + GOD.RED + "]" + result["error"] + "[/]")
        return

    base_earned = abs(result["total_score"])
    if result["is_negative"]:
        broken = combo_eng.record_negative(user)
        if broken["combo_broken"] > 0:
            console.print(render_combo_broken(broken["combo_broken"], broken["was_tier"]))
            console.print("[bold " + GOD.RED + "]COMBO LOST! Score negative = no earning.[/]")
        else:
            console.print("[bold " + GOD.RED + "]Negative impact. No combo. No earning.[/]")
        return

    combo_data = combo_eng.record_positive(user, base_earned, result["total_score"])

    console.print(render_combo_panel(combo_data, result["total_score"]))

    if combo_data["combo"] > 1:
        console.print(render_combo_hit(
            combo_data["combo"], combo_data["tier"],
            base_earned, combo_data["bonus_earned"],
            combo_data["total_earned"], combo_data["multiplier"],
        ))

    if combo_data["rank_up"]:
        console.print(render_rank_up(
            combo_data["prev_rank"], combo_data["rank"],
            combo_data["rank_icon"], combo_data["rank_color"], combo_data["rank_title"],
        ))

    for ach in combo_data.get("achievements", []):
        console.print(render_achievement_popup(ach, combo_data["combo"], combo_data["rank"]))

    console.print("  [" + GOD.DIM + "]Combo: " + str(combo_data["combo"]) +
                  " | Tier: " + combo_data["tier"] +
                  " | Mult: x" + str(combo_data["multiplier"]) +
                  " | Rank: " + combo_data["rank"] + "[/]")
    log_event("COMBO user=" + user + " combo=" + str(combo_data["combo"]))


@cli.command()
@click.option("--user", "-u", default="default", help="User ID")
def combo_status(user):
    """View your combo streak and ascension rank."""
    from .combo import ComboEngine, get_combo_tier, get_ascension_rank, get_next_rank, COMBO_TIERS, ASCENSION_RANKS
    from .karma import KarmaScorer

    combo_eng = ComboEngine()
    scorer = KarmaScorer()
    cu = combo_eng.get_user(user)
    ku = scorer.get_user(user)
    karma = ku["karma"]

    combo = cu["combo"]
    tier = get_combo_tier(combo)
    rank = get_ascension_rank(karma)
    next_rank = get_next_rank(karma)

    next_thresh = None
    for t in sorted(COMBO_TIERS.keys()):
        if t > combo:
            next_thresh = t
            break

    tc = tier.get("color", "dim")
    rc = rank.get("color", "dim")

    t = Table(show_header=False, box=None, padding=(0, 1))
    t.add_column("K", width=12)
    t.add_column("V", width=50)
    t.add_row("Tier", f"[{tc}]{tier['name']}[/{tc}]")
    t.add_row("Combo", f"[{tc}]{combo}[/{tc}]")
    t.add_row("Multiplier", f"[{tc}]x{tier['mult']}[/{tc}]")
    t.add_row("Rank", f"[{rc}]{rank['icon']} {rank['name']}[/{rc}]")
    t.add_row("Title", f"[{rc}]{rank['title']}[/{rc}]")
    if next_thresh:
        progress = min(100, int((combo / next_thresh) * 100)) if next_thresh > 0 else 0
        bar = "#" * (progress // 5) + "." * (20 - progress // 5)
        t.add_row("Next Tier", f"{bar} {progress}% -> {next_thresh}")
    console.print(t)

    if next_rank:
        needed = next_rank["min_karma"] - karma
        prog = min(100, int((karma / next_rank["min_karma"]) * 100)) if next_rank["min_karma"] > 0 else 0
        bar2 = "#" * (prog // 5) + "." * (20 - prog // 5)
        console.print(f"  Next Rank: [{rc}]{next_rank['name']}[/{rc}]  {bar2} {prog}%  ({needed:.0f} karma needed)")
    else:
        console.print(f"  [{FX.GOLD if 'FX' in dir() else 'bright_yellow'}]MAX RANK ACHIEVED[/]")

    console.print(f"  Max Combo: {cu['max_combo']} | Positive: {cu['total_positive']} | Resets: {cu['combo_resets']}")
    log_event("COMBO_STATUS user=" + user)


@cli.command("ascension-path")
def ascension_path_cmd():
    """Show the full ascension rank hierarchy."""
    from .combo import ASCENSION_RANKS

    table = Table(
        title="[bold " + GOD.GOLD + "]>> ASCENSION PATH <<[/]",
        box=box.HEAVY, border_style=GOD.GOLD,
        padding=(0, 1),
    )
    table.add_column("RANK", width=18, style="bold")
    table.add_column("TITLE", width=28)
    table.add_column("KARMA REQ", width=12)
    table.add_column("BONUS", width=8)
    table.add_column("ICON", width=6)

    for r in ASCENSION_RANKS:
        color = r["color"]
        table.add_row(
            f"[{color}]{r['name']}[/{color}]",
            f"[{color}]{r['title']}[/{color}]",
            str(r["min_karma"]),
            f"x{r['bonus_mult']}",
            r["icon"],
        )

    console.print(table)
    log_event("ASCENSION_PATH")


# ============================================================
#  ANTI-CHEAT STATUS COMMAND
# ============================================================

@cli.command("anti-cheat-status")
def anti_cheat_status_cmd():
    """View anti-cheat system status and violations."""
    from .anticheat import anticheat
    from .security import get_tamper_log

    status = anticheat.get_system_status()
    tamper = get_tamper_log()

    t = Table(
        title="[bold " + GOD.NEON + "]>> ANTI-CHEAT SYSTEM STATUS <<[/]",
        box=box.HEAVY, border_style=GOD.NEON,
        padding=(0, 1),
    )
    t.add_column("METRIC", style="bold " + GOD.CYAN, width=24)
    t.add_column("VALUE", style="bold " + GOD.WHITE, width=30)

    t.add_row("Behavior Profiles", str(status["behavior_profiles"]))
    t.add_row("Anomaly Alerts", str(status["anomaly_alerts"]))
    t.add_row("Violations", str(status["violations"]))
    t.add_row("Blocked Users", str(status["blocked_users"]))
    t.add_row("Replay Entries", str(status["replay_entries"]))
    t.add_row("Collusion Pairs", str(status["collusion_pairs"]))
    t.add_row("Velocity Tracked", str(status["velocity_tracked_users"]))
    t.add_row("Machine ID", status["machine_id"])
    t.add_row("Tamper Events", str(len(tamper)))
    t.add_row("Status", "[" + GOD.NEON + "]ACTIVE - 10 LAYERS[/]")
    t.add_row("Protection", "HMAC+RateLimit+PoW+Anomaly+Behavior+Velocity+Collusion+MemoryLock+ReplayGuard+SelfHeal")

    console.print(t)

    if tamper:
        vt = Table(
            title="[bold " + GOD.RED + "]>> TAMPER LOG <<[/]",
            box=box.HEAVY, border_style=GOD.RED,
            padding=(0, 1),
        )
        vt.add_column("FILE", width=20)
        vt.add_column("REASON", width=20)
        vt.add_column("TIME", width=20)
        for e in tamper[-10:]:
            vt.add_row(e.get("file", ""), e.get("reason", ""), e.get("time", "")[:19])
        console.print(vt)

    violations = anticheat.get_violations(10)
    if violations:
        vvt = Table(
            title="[bold " + GOD.RED + "]>> VIOLATION LOG <<[/]",
            box=box.HEAVY, border_style=GOD.RED,
            padding=(0, 1),
        )
        vvt.add_column("USER", width=16)
        vvt.add_column("ACTION", width=18)
        vvt.add_column("REASON", width=20)
        vvt.add_column("TIME", width=20)
        for v in violations:
            vvt.add_row(v.get("user_id", ""), v.get("action", ""), v.get("reason", ""), v.get("time", "")[:19])
        console.print(vvt)

    log_event("ANTI_CHEAT_STATUS")


# ============================================================
#  TIME-BASED EARNING COMMANDS
# ============================================================

@cli.command("time-earn")
@click.option("--user", "-u", default="default", help="User ID")
def time_earn_cmd(user):
    """View time-based earning boost status and session stats."""
    from .time_earn import TimeEarnEngine, TIME_TIERS

    engine = TimeEarnEngine()
    status = engine.get_session_status(user)
    stats = engine.get_user_stats(user)
    global_stats = engine.get_global_stats()

    t = Table(
        title="[bold " + GOD.CYAN + "]>> TIME-BASED EARNING <<[/]",
        box=box.HEAVY, border_style=GOD.CYAN,
        padding=(0, 1),
    )
    t.add_column("METRIC", style="bold " + GOD.CYAN, width=24)
    t.add_column("VALUE", style="bold " + GOD.WHITE, width=35)

    if status["active"]:
        t.add_row("Session",        "[" + GOD.NEON + "]ACTIVE[/]")
        t.add_row("Time",           str(status["session_minutes"]) + " minutes")
        t.add_row("Current Tier",   "[" + status["tier_color"] + "]" + status["tier_label"] + "[/]")
        t.add_row("Current Boost",  "[" + GOD.NEON + "]+" + str(status["boost_pct"]) + "%[/]")
        t.add_row("Actions",        str(status["actions"]))
    else:
        t.add_row("Session",        "[" + GOD.DIM + "]INACTIVE[/]")
        t.add_row("Start",          "Run any command to begin tracking")

    t.add_row("Total Time",        str(round(stats["total_time_minutes"], 1)) + " min")
    t.add_row("Total Sessions",    str(stats["total_sessions"]))
    t.add_row("Longest Session",   str(round(stats["longest_session"], 1)) + " min")
    t.add_row("Total Boost MA",    "[" + GOD.NEON + "]" + str(round(stats["total_boost_earned"], 2)) + " MA[/]")
    t.add_row("Global Sessions",   str(global_stats["total_sessions"]))

    console.print(t)

    tiers_t = Table(
        title="[bold " + GOD.GOLD + "]>> TIME BOOST TIERS <<[/]",
        box=box.HEAVY, border_style=GOD.GOLD,
        padding=(0, 1),
    )
    tiers_t.add_column("TIER", width=14, style="bold")
    tiers_t.add_column("TIME", width=16)
    tiers_t.add_column("BOOST", width=10)
    tiers_t.add_column("DESCRIPTION", width=28)

    for tier in TIME_TIERS:
        tc = tier["color"]
        tiers_t.add_row(
            f"[{tc}]{tier['label']}[/{tc}]",
            f"{tier['min_minutes']}-{tier['max_minutes']} min",
            f"[{tc}]+{tier['boost_pct']}%[/{tc}]",
            f"{'Base rate' if tier['boost_pct'] == 0 else '+' + str(tier['boost_pct']) + '% earning bonus'}",
        )
    console.print(tiers_t)
    log_event("TIME_EARN user=" + user)


@cli.command("hype")
@click.argument("prompt")
@click.option("--user", "-u", default="default", help="User ID")
def hype_cmd(prompt, user):
    """Show positive impact hype popup for a concept."""
    from .hype import render_impact_hype_popup
    from .combo import ComboEngine, get_ascension_rank
    from .karma import KarmaScorer

    scorer = KarmaScorer()
    combo_eng = ComboEngine()
    ku = scorer.get_user(user)
    cu = combo_eng.get_user(user)
    rank = get_ascension_rank(ku["karma"])

    console.print(render_impact_hype_popup(
        prompt, 0, rank["name"], cu["combo"], ku["karma"],
    ))
    log_event("HYPE user=" + user)


@cli.command("session-end")
@click.option("--user", "-u", default="default", help="User ID")
def session_end_cmd(user):
    """End current session and show time-earn summary."""
    from .time_earn import TimeEarnEngine
    from .hype import render_earning_boost_popup

    engine = TimeEarnEngine()
    result = engine.end_session(user)
    stats = engine.get_user_stats(user)

    if result["session_minutes"] > 0:
        console.print(render_earning_boost_popup(
            0, result["session_minutes"], round(stats["total_boost_earned"], 2),
        ))
    else:
        console.print("[" + GOD.DIM + "]No active session.[/]")
    log_event("SESSION_END user=" + user)


@cli.command("combo-board")
def combo_board_cmd():
    """Show combo leaderboard - top 30 ranked by ascension."""
    from .combo import ComboEngine

    combo_eng = ComboEngine()
    board = combo_eng.get_leaderboard(limit=30)

    table = Table(
        title="[bold " + GOD.GOLD + "]>> ASCENSION LEADERBOARD - TOP 30 <<[/]",
        box=box.HEAVY, border_style=GOD.GOLD,
        padding=(0, 1),
    )
    table.add_column("RANK", width=6)
    table.add_column("USER", style="bold " + GOD.WHITE, width=20)
    table.add_column("ASCENSION", width=16)
    table.add_column("COMBO", width=8)
    table.add_column("TIER", width=12)
    table.add_column("POSITIVE", width=10)

    medals = ["[bright_yellow]#1 GOLD[/]", "[white]#2 SLVR[/]", "[bright_red]#3 BRNZ[/]"]
    for i, entry in enumerate(board):
        rank_label = medals[i] if i < 3 else "[" + GOD.DIM + "]#" + str(i+1) + "[/]"
        from .combo import ASCENSION_RANKS
        rank_info = next((r for r in ASCENSION_RANKS if r["name"] == entry["rank"]), ASCENSION_RANKS[0])
        rc = rank_info["color"]
        table.add_row(
            rank_label,
            entry["user_id"],
            f"[{rc}]{rank_info['icon']} {entry['rank']}[/{rc}]",
            str(entry["combo"]),
            entry["tier"],
            str(entry["total_positive"]),
        )

    console.print(table)
    log_event("COMBO_BOARD")


# ============================================================
#  SUBSCRIPTION PLAN COMMANDS
# ============================================================

@cli.command()
def plans():
    """Show all subscription plans and pricing."""
    from .subscription import SubscriptionEngine, PLAN_FEATURES, PLAN_ORDER

    sub = SubscriptionEngine()
    comparison = sub.get_plan_comparison()

    table = Table(
        title="[bold " + GOD.GOLD + "]>> SUBSCRIPTION PLANS <<[/]",
        box=box.HEAVY, border_style=GOD.GOLD,
        padding=(0, 1),
    )
    table.add_column("PLAN", width=14, style="bold")
    table.add_column("MONTHLY", width=12)
    table.add_column("LIFETIME", width=12)
    table.add_column("FEATURES", width=10)
    table.add_column("PERKS", width=30)

    for p in comparison:
        c = p["color"]
        price_m = f"${p['price']:.2f}" if p['price'] > 0 else "FREE"
        price_l = f"${p['lifetime']:.0f}" if p['lifetime'] > 0 else "-"
        perks = {
            "free": "10 models, basic karma",
            "starter": "25 models, advanced karma",
            "pro": "ALL 56 models, premium everything",
            "ultimate": "Priority access, custom models",
            "enterprise": "White-label, dedicated support",
        }
        table.add_row(
            f"[{c}]{p['icon']} {p['name']}[/{c}]",
            f"[{c}]{price_m}/mo[/{c}]",
            f"[{c}]{price_l} once[/{c}]",
            str(p["features_count"]),
            perks.get(p["id"], ""),
        )
    console.print(table)
    log_event("PLANS")


@cli.command()
@click.option("--user", "-u", default="default", help="User ID")
def my_plan(user):
    """View your current subscription plan and features."""
    from .subscription import SubscriptionEngine, PLAN_FEATURES

    sub = SubscriptionEngine()
    user_data = sub.get_user_plan(user)
    plan = PLAN_FEATURES[user_data["plan"]]
    c = plan["color"]

    t = Table(
        title=f"[bold {c}]>> YOUR PLAN: {plan['name']} <<[/]",
        box=box.DOUBLE_EDGE, border_style=c,
        padding=(0, 1),
    )
    t.add_column("METRIC", style="bold " + GOD.CYAN, width=20)
    t.add_column("VALUE", style="bold " + GOD.WHITE, width=40)

    t.add_row("Plan", f"[{c}]{plan['icon']} {plan['name']}[/{c}]")
    t.add_row("Badge", f"[{c}]{plan['badge']}[/{c}]")
    t.add_row("Price", f"${plan['price_monthly']:.2f}/mo or ${plan['price_lifetime']:.0f} lifetime")
    t.add_row("Features", f"[{c}]{len(plan['features'])} features[/{c}]")
    t.add_row("Lifetime", "YES" if user_data["is_lifetime"] else "NO (monthly)")
    if user_data["subscribed_at"]:
        t.add_row("Since", user_data["subscribed_at"][:10])
    if user_data["expires_at"]:
        t.add_row("Renews", user_data["expires_at"][:10])
    t.add_row("Total Spent", f"${user_data['total_spent']:.2f}")

    console.print(t)

    ft = Table(
        title=f"[bold {c}]>> TOP 10 FEATURES <<[/]",
        box=box.HEAVY, border_style=c,
        padding=(0, 1),
    )
    ft.add_column("#", width=4)
    ft.add_column("FEATURE", width=55)
    for i, feat in enumerate(plan["features"][:10], 1):
        ft.add_row(str(i), f"[{c}]{feat}[/{c}]")
    if len(plan["features"]) > 10:
        ft.add_row("...", f"[{GOD.DIM}]... and {len(plan['features']) - 10} more features[/{GOD.DIM}]")
    console.print(ft)
    log_event("MY_PLAN user=" + user)


@cli.command()
@click.argument("plan_name")
@click.option("--user", "-u", default="default", help="User ID")
@click.option("--lifetime", "-l", is_flag=True, help="Purchase lifetime access")
def subscribe(plan_name, user, lifetime):
    """Subscribe to a plan (free/starter/pro/ultimate/enterprise)."""
    from .subscription import SubscriptionEngine, PLAN_FEATURES

    sub = SubscriptionEngine()
    result = sub.subscribe(user, plan_name.lower(), is_lifetime=lifetime)

    if result.get("error"):
        console.print("[bold " + GOD.RED + "]" + result["error"] + "[/]")
        return

    c = result["color"]
    t = Table(
        title=f"[bold {c}]>> SUBSCRIPTION ACTIVATED <<[/]",
        box=box.DOUBLE_EDGE, border_style=c,
        padding=(0, 2),
    )
    t.add_column("METRIC", style="bold " + GOD.CYAN, width=20)
    t.add_column("VALUE", style="bold " + GOD.WHITE, width=40)
    t.add_row("Plan", f"[{c}]{result['icon']} {result['plan_name']}[/{c}]")
    t.add_row("Type", "LIFETIME" if result["lifetime"] else "MONTHLY")
    t.add_row("Price", f"[{c}]${result['price']:.2f}[/{c}]")
    t.add_row("Features", f"[{c}]{result['features_count']} features[/{c}]")
    t.add_row("Badge", f"[{c}]{result['badge']}[/{c}]")
    t.add_row("Status", f"[{GOD.NEON}]ACTIVE[/]")
    console.print(t)
    log_event("SUBSCRIBE user=" + user + " plan=" + plan_name + " lifetime=" + str(lifetime))


@cli.command()
@click.option("--user", "-u", default="default", help="User ID")
def upgrade_plan(user):
    """Upgrade to the next subscription tier."""
    from .subscription import SubscriptionEngine

    sub = SubscriptionEngine()
    user_data = sub.get_user_plan(user)
    result = sub.upgrade(user)

    if result.get("error"):
        console.print("[bold " + GOD.RED + "]" + result["error"] + "[/]")
        return

    c = result["color"]
    console.print(
        "[bold " + c + "]UPGRADED from " + user_data["plan"].upper() +
        " to " + result["plan_name"].upper() + "![/] " +
        "[$" + str(result["price"]) + "] " +
        str(result["features_count"]) + " features"
    )
    log_event("UPGRADE user=" + user)


@cli.command("feature-check")
@click.argument("feature")
@click.option("--user", "-u", default="default", help="User ID")
def feature_check_cmd(feature, user):
    """Check if your plan includes a specific feature."""
    from .subscription import SubscriptionEngine

    sub = SubscriptionEngine()
    has = sub.has_feature(user, feature)
    user_data = sub.get_user_plan(user)
    plan_name = user_data["plan"]

    if has:
        console.print("[bold " + GOD.NEON + "]YES[/] - Your " + plan_name.upper() + " plan includes: " + feature)
    else:
        console.print("[bold " + GOD.RED + "]NO[/] - Your " + plan_name.upper() + " plan does NOT include: " + feature)
        idx = ["free", "starter", "pro", "ultimate", "enterprise"].index(plan_name) if plan_name in ["free", "starter", "pro", "ultimate", "enterprise"] else 0
        if idx < 4:
            console.print("  [" + GOD.DIM + "]Upgrade with: Melodie-Kimini subscribe " + ["starter", "pro", "ultimate", "enterprise"][idx] + "[/]")
    log_event("FEATURE_CHECK user=" + user + " feature=" + feature)


# ============================================================
#  ULTIMATE SOCIAL MEDIA SHARE REPORT
# ============================================================

@cli.command("share-report")
@click.option("--user", "-u", default="default", help="User ID")
@click.option("--platform", "-p", default=None, help="Direct share to platform (twitter, facebook, etc.)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def share_report(user, platform, as_json):
    """Generate ultimate profile report with social media share buttons."""
    from .social import (
        collect_user_data, generate_share_text, generate_share_url,
        SOCIAL_PLATFORMS, record_share, get_share_stats,
    )

    data = collect_user_data(user)
    kd = data["karma"]
    cd = data["combo"]
    td = data["tokens"]
    te = data["time_earn"]
    lb = data["leaderboard"]
    sub = data["subscription"]
    totals = data["totals"]

    if as_json:
        click.echo(json.dumps(data, indent=2))
        return

    console.clear()

    plan_badge = {"free": "--", "starter": ">>", "pro": "**", "ultimate": "##+", "enterprise": "@@+"}
    plan_color = {"free": "dim", "starter": "bright_cyan", "pro": "yellow", "ultimate": "bright_red", "enterprise": "bright_magenta"}
    pc = plan_color.get(sub["plan"], "dim")
    pb = plan_badge.get(sub["plan"], "--")

    header = Table(show_header=False, box=None, padding=(0, 0))
    header.add_column("K", style="bold " + GOD.CYAN, width=20)
    header.add_column("V", style="bold " + GOD.WHITE, width=50)
    header.add_row("User", "[bold " + GOD.WHITE + "]" + user + "[/]")
    header.add_row("Plan", f"[{pc}]{pb} {sub['plan'].upper()}[/{pc}]" + (" LIFETIME" if sub["is_lifetime"] else ""))
    header.add_row("Report Time", "[" + GOD.DIM + "]" + data["timestamp"][:19] + "[/]")

    console.print(Panel(
        Align.center(header),
        title="[bold " + GOD.GOLD + "]>> ULTIMATE PROFILE REPORT <<[/]",
        subtitle="[dim]" + user + " | " + sub["plan"].upper() + " MEMBER | " + str(totals["days_active"]) + " DAYS ACTIVE[/]",
        border_style=GOD.GOLD, box=box.DOUBLE_EDGE, padding=(1, 2),
    ))

    karma_table = Table(
        title="[bold " + GOD.NEON + "]>> KARMA POWER <<[/]",
        box=box.HEAVY, border_style=GOD.NEON, padding=(0, 1),
    )
    karma_table.add_column("METRIC", style="bold " + GOD.CYAN, width=18)
    karma_table.add_column("VALUE", style="bold " + GOD.WHITE, width=20)
    karma_table.add_column("BAR", width=20)
    karma_table.add_column("DETAIL", style=GOD.DIM, width=22)

    karma_table.add_row("Score", "[bold " + GOD.NEON + "]" + str(kd['score']) + "[/]", _karma_bar(kd['score']), "Lvl " + str(kd['level']))
    karma_table.add_row("Title", "[bold " + GOD.GOLD + "]" + str(kd['title']) + "[/]", "", "Achievements: " + str(len(kd['achievements'])))
    karma_table.add_row("Sessions", str(kd['sessions']), "", "Positive: " + str(kd['positive']))
    karma_table.add_row("Positive %", "[bright_green]" + str(totals['positive_ratio']) + "%[/]", "", "Negative: " + str(kd['negative']))
    karma_table.add_row("Total All Sources", "[bold " + GOD.GOLD + "]" + str(totals['total_karma']) + "[/]", "", "Karma + Tokens + Combo")
    console.print(karma_table)

    combo_table = Table(
        title="[bold " + GOD.SCARLET + "]>> COMBO & ASCENSION <<[/]",
        box=box.HEAVY, border_style=GOD.SCARLET, padding=(0, 1),
    )
    combo_table.add_column("METRIC", style="bold " + GOD.CYAN, width=18)
    combo_table.add_column("VALUE", style="bold " + GOD.WHITE, width=20)
    combo_table.add_column("BAR", width=20)
    combo_table.add_column("DETAIL", style=GOD.DIM, width=22)

    combo_table.add_row("Combo Streak", "[bold " + GOD.SCARLET + "]x" + str(cd['combo']) + "[/]", _combo_bar(cd['combo']), "Tier: " + str(cd['tier']))
    combo_table.add_row("Divine Rank", "[bold " + GOD.GOLD + "]" + str(cd['rank']) + "[/]", "", "Total Earned: " + str(cd['total_earned']))
    console.print(combo_table)

    token_table = Table(
        title="[bold " + GOD.GOLD + "]>> MA TOKEN ECONOMY <<[/]",
        box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1),
    )
    token_table.add_column("METRIC", style="bold " + GOD.CYAN, width=18)
    token_table.add_column("VALUE", style="bold " + GOD.WHITE, width=20)
    token_table.add_column("BAR", width=20)
    token_table.add_column("DETAIL", style=GOD.DIM, width=22)

    token_table.add_row("Balance", "[bold " + GOD.GOLD + "]" + str(td['balance']) + " MA[/]", _token_bar(td['balance']), "1 Karma = 10 MA")
    token_table.add_row("Total Earned", str(td['total_earned']) + " MA", "", "Spent: " + str(td['total_spent']) + " MA")
    token_table.add_row("Time Earned", str(te['total_earned']) + " MA", "", "Tier: " + str(te['time_tier']))
    token_table.add_row("Mining Sessions", str(te['total_minutes']) + " min", "", "Staked: 12% APY")
    console.print(token_table)

    lb_table = Table(
        title="[bold " + GOD.PURPLE + "]>> LEADERBOARD <<[/]",
        box=box.HEAVY, border_style=GOD.PURPLE, padding=(0, 1),
    )
    lb_table.add_column("METRIC", style="bold " + GOD.CYAN, width=18)
    lb_table.add_column("VALUE", style="bold " + GOD.WHITE, width=20)
    lb_table.add_column("BAR", width=20)
    lb_table.add_column("DETAIL", style=GOD.DIM, width=22)

    rank_str = f"#{lb['rank']}" if lb['rank'] > 0 else "Unranked"
    lb_table.add_row("Global Rank", "[bold " + GOD.PURPLE + "]" + rank_str + "[/]", "", "Contributions: " + str(lb['contributions']))
    lb_table.add_row("Projects", str(len(lb['projects'])), "", "Joined: " + ", ".join(lb['projects'][:3]) if lb['projects'] else "None yet")
    lb_table.add_row("Karma Generated", str(lb['total_karma']), "", "From contributions")
    console.print(lb_table)

    overall = Table(show_header=False, box=None, padding=(0, 0))
    overall.add_column("K", style="bold " + GOD.GOLD, width=20)
    overall.add_column("V", style="bold " + GOD.WHITE, width=50)
    overall.add_row("Overall Score", "[bold " + GOD.GOLD + "]" + str(totals['total_karma']) + " points[/]")
    overall.add_row("Total Prompts", str(totals['total_prompts']))
    overall.add_row("Days Active", str(totals['days_active']))
    overall.add_row("Achievements", str(len(kd['achievements'])))
    console.print(Panel(
        Align.center(overall),
        title="[bold " + GOD.GOLD + "]>> OVERALL RANKING <<[/]",
        border_style=GOD.GOLD, box=box.HEAVY, padding=(0, 2),
    ))

    if platform and platform in SOCIAL_PLATFORMS:
        _show_single_share(platform, data, user)
    else:
        _show_share_grid(data, user)

    log_event("SHARE_REPORT user=" + user)


def _karma_bar(score):
    n = min(16, int(score / 100))
    filled = "#" * n
    empty = "." * (16 - n)
    return f"[bright_green]{'#' * n}{'.' * (16 - n)}[/] {score}"


def _combo_bar(combo):
    n = min(16, combo // 5)
    filled = "#" * n
    empty = "." * (16 - n)
    return f"[bright_red]{'#' * n}{'.' * (16 - n)}[/] x{combo}"


def _token_bar(balance):
    n = min(16, int(balance / 50))
    filled = "#" * n
    empty = "." * (16 - n)
    return f"[bright_yellow]{'#' * n}{'.' * (16 - n)}[/] {balance}"


def _show_single_share(platform_id, data, user):
    from .social import generate_share_text, generate_share_url, record_share, SOCIAL_PLATFORMS

    platform = SOCIAL_PLATFORMS[platform_id]
    text = generate_share_text(platform_id, data)
    url = generate_share_url(platform_id, data)
    c = platform["color"]

    t = Table(
        title=f"[bold {c}]>> SHARE ON {platform['name'].upper()} <<[/]",
        box=box.DOUBLE_EDGE, border_style=c, padding=(0, 1),
    )
    t.add_column("METRIC", style="bold " + GOD.CYAN, width=18)
    t.add_column("VALUE", style="bold " + GOD.WHITE, width=60)
    t.add_row("Platform", f"[{c}]{platform['icon']} {platform['name']}[/{c}]")
    t.add_row("Chars", str(len(text)) + " / " + str(platform["max_chars"]))
    t.add_row("Text", text[:80] + "..." if len(text) > 80 else text)
    if url:
        t.add_row("URL", url[:90])
    console.print(t)

    if url:
        console.print("[bright_green]>> SHARE URL READY[/]")
        console.print("[dim]" + url[:120] + "[/]")
    else:
        console.print("[bright_yellow]>> COPY THIS TEXT TO SHARE:[/]")
        console.print("[bright_white]" + text + "[/]")

    record_share(user, platform_id)
    console.print("[bright_green]>> Share recorded![/]")


def _show_share_grid(data, user):
    from .social import SOCIAL_PLATFORMS, record_share, generate_share_url, generate_share_text

    console.print()
    console.print("[bold " + GOD.GOLD + "]>> SOCIAL MEDIA SHARE BUTTONS <<[/]")
    console.print("[dim]Click or copy the URL to share your ultimate report[/]")
    console.print()

    grid = Table(show_header=True, box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1))
    grid.add_column("#", width=3, style=GOD.DIM)
    grid.add_column("PLATFORM", width=18, style="bold " + GOD.WHITE)
    grid.add_column("STATUS", width=12)
    grid.add_column("ACTION", width=50)

    for idx, (pid, platform) in enumerate(SOCIAL_PLATFORMS.items(), 1):
        c = platform["color"]
        url = generate_share_url(pid, data) if platform["url_template"] else ""
        if url:
            status = "[bright_green]READY[/]"
            action = url[:65] + "..." if len(url) > 65 else url
        else:
            status = "[bright_yellow]COPY[/]"
            action = "Copy text below to share"

        grid.add_row(
            str(idx),
            f"[{c}]{platform['icon']} {platform['name']}[/{c}]",
            status,
            "[dim]" + action + "[/]",
        )

    console.print(grid)

    preview = Table(
        title="[bold " + GOD.CYAN + "]>> SHARE TEXT PREVIEW (Twitter) <<[/]",
        box=box.HEAVY, border_style=GOD.CYAN, padding=(0, 1),
    )
    preview.add_column("CONTENT", style="bright_white", width=70)
    tw = generate_share_text("twitter", data)
    for line in tw.split("\n"):
        preview.add_row(line)
    console.print(preview)

    console.print("[bright_green]>> " + str(len(SOCIAL_PLATFORMS)) + " platforms ready![/]")
    console.print("[dim]Use: Melodie-Kimini share-report --platform twitter[/]")


@cli.command("share-stats")
def share_stats():
    """Show global sharing statistics."""
    from .social import get_share_stats

    stats = get_share_stats()
    t = Table(
        title="[bold " + GOD.GOLD + "]>> SHARE STATISTICS <<[/]",
        box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1),
    )
    t.add_column("PLATFORM", width=20, style="bold " + GOD.WHITE)
    t.add_column("SHARES", width=10, style="bold " + GOD.NEON)

    t.add_row("[bold " + GOD.GOLD + "]TOTAL", str(stats["total"]))
    for platform, count in sorted(stats.get("by_platform", {}).items(), key=lambda x: -x[1]):
        t.add_row(platform, str(count))
    console.print(t)
    log_event("SHARE_STATS")


# ============================================================
#  PROXY ROUTING & OFFLINE MODE
# ============================================================

@cli.command("proxy-status")
@click.option("--user", "-u", default="default", help="User ID")
def proxy_status(user):
    """Show proxy routing status and online/offline mode."""
    from .proxy import ProxyRouter

    router = ProxyRouter(user)
    status = router.get_status()
    warning = router.get_offline_warning()

    if warning:
        console.print("[bold bright_yellow]!! " + warning["warning"] + " !![/]")
        console.print("[bright_yellow]" + warning["detail"] + "[/]")
        console.print("[bright_yellow]" + str(warning["queued"]) + " operations queued for sync[/]")
        console.print()

    t = Table(
        title="[bold " + GOD.GOLD + "]>> PROXY ROUTING STATUS <<[/]",
        box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1),
    )
    t.add_column("METRIC", style="bold " + GOD.CYAN, width=22)
    t.add_column("VALUE", style="bold " + GOD.WHITE, width=30)

    mode_color = GOD.NEON if status["is_online"] else GOD.SCARLET
    mode_text = "ONLINE" if status["is_online"] else "LOCAL"
    t.add_row("Mode", "[" + mode_color + "]" + mode_text + "[/]")
    t.add_row("Network", "[bright_green]CONNECTED[/]" if status["is_online"] else "[bright_yellow]OFFLINE[/]")
    t.add_row("Platforms Tracked", str(status["platforms_tracked"]))
    t.add_row("Platforms Configured", str(status["platforms_online"]))
    t.add_row("Total Requests", str(status["stats"].get("total_requests", 0)))
    t.add_row("Local Served", str(status["stats"].get("local_served", 0)))
    t.add_row("Online Served", str(status["stats"].get("online_served", 0)))
    t.add_row("Syncs Completed", str(status["stats"].get("syncs_completed", 0)))
    console.print(t)
    log_event("PROXY_STATUS user=" + user)


@cli.command("proxy-platforms")
@click.option("--user", "-u", default="default", help="User ID")
def proxy_platforms(user):
    """List all tracked platforms and their local/online status."""
    from .proxy import ProxyRouter

    router = ProxyRouter(user)
    platforms = router.get_all_platforms()

    t = Table(
        title="[bold " + GOD.GOLD + "]>> PLATFORM DATA ANALYSIS <<[/]",
        box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1),
    )
    t.add_column("#", width=3, style=GOD.DIM)
    t.add_column("PLATFORM", width=16, style="bold " + GOD.WHITE)
    t.add_column("MODE", width=10)
    t.add_column("REQUESTS", width=10)
    t.add_column("LOCAL", width=8)
    t.add_column("ONLINE", width=8)
    t.add_column("SYNC", width=10)

    for idx, p in enumerate(platforms, 1):
        c = p["color"]
        local_cap = "[bright_green]YES[/]" if p["offline_capable"] else "[bright_red]NO[/]"
        sync_c = GOD.NEON if p["sync_status"] == "synced" else GOD.DIM
        t.add_row(
            str(idx),
            "[" + c + "]" + p["icon"] + " " + p["name"] + "[/]",
            "[bright_yellow]LOCAL[/]",
            str(p["total_requests"]),
            str(p["local_requests"]),
            str(p["online_requests"]),
            "[" + sync_c + "]" + p["sync_status"] + "[/]",
        )
    console.print(t)
    log_event("PROXY_PLATFORMS user=" + user)


@cli.command("offline-project")
@click.argument("project_name")
@click.option("--user", "-u", default="default", help="User ID")
@click.option("--task", "-t", default="general", help="Task type")
def offline_project(project_name, user, task):
    """Work on a project in offline mode with yellow warning."""
    from .proxy import ProxyRouter

    router = ProxyRouter(user)
    warning = router.get_offline_warning()
    status = router.get_status()

    console.print("[bold bright_yellow]!! OFFLINE PROJECT MODE !![/]")
    if warning:
        console.print("[bright_yellow]>> WARNING: You are OFFLINE[/]")
        console.print("[bright_yellow]>> " + warning["detail"] + "[/]")
        console.print("[bright_yellow]>> " + str(warning["queued"]) + " operations queued[/]")
    else:
        console.print("[bright_green]>> ONLINE -- Network available[/]")
    console.print()

    t = Table(
        title="[bold " + GOD.GOLD + "]>> PROJECT: " + project_name.upper() + " <<[/]",
        box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1),
    )
    t.add_column("METRIC", style="bold " + GOD.CYAN, width=20)
    t.add_column("VALUE", style="bold " + GOD.WHITE, width=40)
    t.add_row("Project", "[bold " + GOD.WHITE + "]" + project_name + "[/]")
    t.add_row("Task", task)
    t.add_row("Mode", "[bright_yellow]LOCAL[/]" if not status["is_online"] else "[bright_green]ONLINE[/]")
    t.add_row("User", user)
    t.add_row("Status", "[bright_yellow]WORKING LOCALLY[/]")
    console.print(t)

    router.record_event("offline_project", detail=project_name + ":" + task)
    log_event("OFFLINE_PROJECT name=" + project_name + " task=" + task)


@cli.command("proxy-queue")
@click.option("--user", "-u", default="default", help="User ID")
def proxy_queue(user):
    """Show queued operations waiting for sync."""
    from .proxy import ProxyRouter

    router = ProxyRouter(user)
    queue = router.get_queue()

    t = Table(
        title="[bold " + GOD.GOLD + "]>> SYNC QUEUE (" + str(len(queue)) + " items) <<[/]",
        box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1),
    )
    t.add_column("#", width=4, style=GOD.DIM)
    t.add_column("PLATFORM", width=16, style="bold " + GOD.WHITE)
    t.add_column("TYPE", width=12)
    t.add_column("TIME", width=20)
    t.add_column("STATUS", width=10)

    for idx, item in enumerate(queue[-20:], 1):
        t.add_row(
            str(idx),
            item.get("platform", "unknown"),
            item.get("type", "unknown"),
            item.get("time", "")[:19],
            "[bright_yellow]QUEUED[/]",
        )
    if not queue:
        t.add_row("--", "[dim]No queued operations[/]", "", "", "")
    console.print(t)
    log_event("PROXY_QUEUE user=" + user)


@cli.command("proxy-flush")
@click.option("--user", "-u", default="default", help="User ID")
def proxy_flush(user):
    """Flush queued operations (requires online)."""
    from .proxy import ProxyRouter

    router = ProxyRouter(user)
    result = router.flush_queue()

    if result["flushed"] > 0:
        console.print("[bright_green]>> Flushed " + str(result["flushed"]) + " queued operations![/]")
    else:
        console.print("[bright_yellow]>> " + result["reason"] + "[/]")
    log_event("PROXY_FLUSH user=" + user + " flushed=" + str(result["flushed"]))


@cli.command("proxy-history")
@click.option("--user", "-u", default="default", help="User ID")
@click.option("--limit", "-l", default=15, help="Number of entries")
def proxy_history(user, limit):
    """Show proxy routing event history."""
    from .proxy import ProxyRouter

    router = ProxyRouter(user)
    history = router.get_history(limit)

    t = Table(
        title="[bold " + GOD.GOLD + "]>> PROXY HISTORY <<[/]",
        box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1),
    )
    t.add_column("TIME", width=19, style=GOD.DIM)
    t.add_column("EVENT", width=16, style="bold " + GOD.WHITE)
    t.add_column("PLATFORM", width=14)
    t.add_column("MODE", width=8)
    t.add_column("DETAIL", width=25)

    for entry in reversed(history):
        mode_c = GOD.NEON if entry.get("mode") == "ONLINE" else GOD.SCARLET
        t.add_row(
            entry.get("timestamp", "")[:19],
            entry.get("type", "unknown"),
            entry.get("platform", "--"),
            "[" + mode_c + "]" + entry.get("mode", "?") + "[/]",
            entry.get("detail", "")[:25],
        )
    if not history:
        t.add_row("--", "[dim]No history yet[/]", "", "", "")
    console.print(t)
    log_event("PROXY_HISTORY user=" + user)


# ============================================================
#  ENTERPRISE BUSINESS RANKING & CRYPTO KARMA
# ============================================================

@cli.command("enterprise-score")
@click.argument("name")
@click.option("--category", "-c", required=True, help="Enterprise category")
@click.option("--revenue", "-r", default=0, type=float, help="Revenue impact score (0-100)")
@click.option("--jobs", "-j", default=0, type=float, help="Job creation score (0-100)")
@click.option("--innovation", "-i", default=50, type=float, help="Innovation index (0-100)")
@click.option("--esg", "-e", default=50, type=float, help="ESG score (0-100)")
@click.option("--compliance", default=50, type=float, help="Compliance rating (0-100)")
@click.option("--security", "-s", default=50, type=float, help="Security audit score (0-100)")
@click.option("--customer", default=50, type=float, help="Customer satisfaction (0-100)")
@click.option("--disruption", default=50, type=float, help="Market disruption (0-100)")
@click.option("--sustainability", default=50, type=float, help="Sustainability impact (0-100)")
@click.option("--social", default=50, type=float, help="Social responsibility (0-100)")
@click.option("--user", "-u", default="default", help="User ID")
def enterprise_score(name, category, revenue, jobs, innovation, esg, compliance, security, customer, disruption, sustainability, social, user):
    """Score an enterprise project for crypto karma impact."""
    from .enterprise import EnterpriseScorer, ENTERPRISE_CATEGORIES

    scorer = EnterpriseScorer()
    if category not in ENTERPRISE_CATEGORIES:
        cats = ", ".join(ENTERPRISE_CATEGORIES.keys())
        console.print("[bold bright_red]Unknown category![/] Use one of: " + cats)
        return

    eid = name.lower().replace(" ", "-")[:30]
    dimensions = {
        "REVENUE_IMPACT": revenue, "JOB_CREATION": jobs,
        "INNOVATION_INDEX": innovation, "ESG_SCORE": esg,
        "COMPLIANCE_RATING": compliance, "SECURITY_AUDIT": security,
        "CUSTOMER_SATISFACTION": customer, "MARKET_DISRUPTION": disruption,
        "SUSTAINABILITY_IMPACT": sustainability, "SOCIAL_RESPONSIBILITY": social,
    }
    result = scorer.score_enterprise(eid, name, category, dimensions, user)

    if result.get("error"):
        console.print("[bold bright_red]" + result["error"] + "[/]")
        return

    cat = ENTERPRISE_CATEGORIES[category]
    c = cat["color"]
    rc = result.get("rank", "Startup")

    header = Table(show_header=False, box=None, padding=(0, 0))
    header.add_column("K", style="bold " + GOD.CYAN, width=20)
    header.add_column("V", style="bold " + GOD.WHITE, width=40)
    header.add_row("Enterprise", "[bold " + GOD.WHITE + "]" + name + "[/]")
    header.add_row("Category", "[" + c + "]" + cat["icon"] + " " + cat["name"] + "[/]")
    header.add_row("Rank", "[bold " + GOD.GOLD + "]" + rc + "[/]")
    header.add_row("Crypto Karma", "[bold " + GOD.NEON + "]" + str(result["crypto_karma"]) + " points[/]")
    console.print(Panel(
        Align.center(header),
        title="[bold " + GOD.GOLD + "]>> ENTERPRISE CRYPTO KARMA SCORE <<[/]",
        border_style=GOD.GOLD, box=box.DOUBLE_EDGE, padding=(1, 2),
    ))

    dim_table = Table(
        title="[bold " + GOD.CYAN + "]>> SCORING DIMENSIONS <<[/]",
        box=box.HEAVY, border_style=GOD.CYAN, padding=(0, 1),
    )
    dim_table.add_column("DIMENSION", width=22, style="bold " + GOD.WHITE)
    dim_table.add_column("RAW", width=8)
    dim_table.add_column("SCORE", width=8)
    dim_table.add_column("WEIGHTED", width=10)
    dim_table.add_column("BAR", width=20)

    for dim_key, dim_data in result["dimension_scores"].items():
        raw = dim_data["raw"]
        sc = dim_data["score"]
        w = dim_data["weighted"]
        bar_n = min(16, int(sc / 7))
        bar = "[bright_green]" + "#" * bar_n + "." * (16 - bar_n) + "[/]"
        dim_table.add_row(dim_key, str(raw), str(sc), str(w), bar)
    console.print(dim_table)

    if result["negative_flags"]:
        console.print("[bright_red]!! FLAGS: " + ", ".join(result["negative_flags"]) + " !![/]")

    from .karma import KarmaScorer
    ks = KarmaScorer()
    ku = ks.get_user(user)
    new_karma = round(ku["karma"] + abs(result["crypto_karma"]), 2)
    console.print("[bright_green]>> Crypto Karma +" + str(result["crypto_karma"]) + " added to " + user + "[/]")
    console.print("[bright_green]>> Total Karma: " + str(new_karma) + " (Lvl " + str(ku.get("level", 1)) + ")[/]")

    log_event("ENTERPRISE_SCORE name=" + name + " cat=" + category + " karma=" + str(result["crypto_karma"]))


@cli.command("enterprise-rankings")
@click.option("--category", "-c", default=None, help="Filter by category")
@click.option("--limit", "-l", default=20, help="Number of entries")
def enterprise_rankings(category, limit):
    """Show enterprise global or category rankings."""
    from .enterprise import EnterpriseScorer, ENTERPRISE_CATEGORIES

    scorer = EnterpriseScorer()
    if category:
        entries = scorer.get_category_rankings(category, limit)
        title = ">> " + category.upper() + " RANKINGS <<"
    else:
        entries = scorer.get_global_rankings(limit)
        title = ">> GLOBAL ENTERPRISE RANKINGS <<"

    t = Table(
        title="[bold " + GOD.GOLD + "]" + title + "[/]",
        box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1),
    )
    t.add_column("RANK", width=6)
    t.add_column("ENTERPRISE", width=25, style="bold " + GOD.WHITE)
    t.add_column("CATEGORY", width=14)
    t.add_column("CRYPTO KARMA", width=14, style="bold " + GOD.NEON)
    t.add_column("RANK", width=16)

    medals = ["[bright_yellow]#1[/]", "[bright_white]#2[/]", "[bright_red]#3[/]"]
    for i, entry in enumerate(entries):
        rc = medals[i] if i < 3 else "[" + GOD.DIM + "]#" + str(i+1) + "[/]"
        cat_info = ENTERPRISE_CATEGORIES.get(entry.get("category", ""), {})
        cat_c = cat_info.get("color", "dim")
        cat_icon = cat_info.get("icon", "--")
        t.add_row(
            rc,
            entry.get("name", "?"),
            "[" + cat_c + "]" + cat_icon + " " + entry.get("category", "?") + "[/]",
            "[bold " + GOD.NEON + "]" + str(entry.get("crypto_karma", 0)) + "[/]",
            entry.get("rank", "Startup"),
        )
    if not entries:
        t.add_row("--", "[dim]No enterprises scored yet[/]", "", "", "")
    console.print(t)
    total = scorer.get_crypto_karma_total()
    console.print("[bright_green]>> Total Crypto Karma in System: " + str(total) + "[/]")
    log_event("ENTERPRISE_RANKINGS cat=" + str(category))


@cli.command("enterprise-templates")
def enterprise_templates():
    """Show massive structured enterprise project templates."""
    from .enterprise import EnterpriseScorer, ENTERPRISE_CATEGORIES

    scorer = EnterpriseScorer()
    templates = scorer.get_templates()

    for tmpl in templates:
        cat = ENTERPRISE_CATEGORIES.get(tmpl["category"], {})
        c = cat.get("color", "dim")
        icon = cat.get("icon", "--")

        dim_table = Table(show_header=False, box=None, padding=(0, 0))
        dim_table.add_column("K", style="bold " + GOD.CYAN, width=20)
        dim_table.add_column("V", style="bold " + GOD.WHITE, width=35)
        dim_table.add_row("Name", "[bold " + GOD.WHITE + "]" + tmpl["name"] + "[/]")
        dim_table.add_row("Category", "[" + c + "]" + icon + " " + cat.get("name", tmpl["category"]) + "[/]")
        dim_table.add_row("Description", "[dim]" + tmpl["description"][:50] + "[/]")
        dim_table.add_row("Revenue", tmpl["revenue_range"])
        dim_table.add_row("Employees", tmpl["employees"])
        dim_table.add_row("Crypto Karma Bonus", "[bold " + GOD.NEON + "]" + str(tmpl["crypto_karma_bonus"]) + "[/]")
        dim_table.add_row("Compliance", ", ".join(tmpl["compliance"][:4]))

        console.print(Panel(
            dim_table,
            title="[bold " + c + "]>> " + tmpl["name"][:50] + " <<[/]",
            border_style=c, box=box.HEAVY, padding=(0, 1),
        ))

    console.print("[bright_green]>> " + str(len(templates)) + " enterprise templates available[/]")
    console.print("[dim]Use: Melodie-Kimini enterprise-score --name NAME --category CATEGORY[/]")
    log_event("ENTERPRISE_TEMPLATES")


@cli.command("enterprise-categories")
def enterprise_categories():
    """Show all enterprise categories and scoring multipliers."""
    from .enterprise import ENTERPRISE_CATEGORIES

    t = Table(
        title="[bold " + GOD.GOLD + "]>> ENTERPRISE CATEGORIES <<[/]",
        box=box.HEAVY, border_style=GOD.GOLD, padding=(0, 1),
    )
    t.add_column("#", width=3, style=GOD.DIM)
    t.add_column("CATEGORY", width=18, style="bold " + GOD.WHITE)
    t.add_column("MULTIPLIER", width=12)
    t.add_column("COMPLIANCE", width=25)
    t.add_column("DESCRIPTION", width=30)

    for idx, (cid, cat) in enumerate(ENTERPRISE_CATEGORIES.items(), 1):
        c = cat["color"]
        t.add_row(
            str(idx),
            "[" + c + "]" + cat["icon"] + " " + cat["name"] + "[/]",
            "[bold " + GOD.NEON + "]x" + str(cat["base_multiplier"]) + "[/]",
            ", ".join(cat["compliance_required"][:3]),
            cat["description"][:30],
        )
    console.print(t)
    log_event("ENTERPRISE_CATEGORIES")


def main():
    """Entry point for Melodie-Kimini GODLIKE CLI."""
    cli()


if __name__ == "__main__":
    main()
