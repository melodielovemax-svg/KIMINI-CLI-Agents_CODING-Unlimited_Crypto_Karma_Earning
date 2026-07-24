"""
GAMING VISUAL EFFECTS ENGINE
Renders combo counters, rank-up animations, and % multiplier displays.
ASCII-safe for Windows cp1252 compatibility.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich import box

console = Console()

# ============================================================
#  COLOR CONSTANTS
# ============================================================

class FX:
    COMBO_BRONZE   = "yellow"
    COMBO_SILVER   = "white"
    COMBO_GOLD     = "bright_yellow"
    COMBO_PLAT     = "bright_cyan"
    COMBO_DIAMOND  = "bright_magenta"
    COMBO_LEGEND   = "bright_red"
    COMBO_MYTHIC   = "bright_green"
    RANK_MORTAL    = "dim"
    RANK_ACOLYTE   = "white"
    RANK_MONK      = "bright_white"
    RANK_SAGE      = "bright_cyan"
    RANK_BUDDHA    = "bright_yellow"
    RANK_DEMIGOD   = "bright_magenta"
    RANK_GOD       = "bright_red"
    RANK_ARCHANGEL = "bright_green"
    RANK_SERAPHIM  = "bright_white"
    RANK_COSMIC    = "bright_yellow"
    GOLD           = "bright_yellow"
    CYAN           = "bright_cyan"
    GREEN          = "bright_green"
    RED            = "bright_red"
    WHITE          = "bright_white"
    DIM            = "dim"
    BONUS          = "bright_green"
    PENALTY        = "bright_red"
    XP             = "bright_cyan"

TIER_STYLE = {
    "NONE":       "dim",
    "BRONZE":     "yellow",
    "SILVER":     "white",
    "GOLD":       "bright_yellow",
    "PLATINUM":   "bright_cyan",
    "DIAMOND":    "bright_magenta",
    "LEGENDARY":  "bright_red",
    "MYTHIC":     "bright_green",
}

RANK_STYLE = {
    "Mortal":         "dim",
    "Acolyte":        "white",
    "Monk":           "bright_white",
    "Sage":           "bright_cyan",
    "Buddha":         "bright_yellow",
    "Demigod":        "bright_magenta",
    "God":            "bright_red",
    "Archangel":      "bright_green",
    "Seraphim":       "bright_white",
    "Cosmic Overlord":"bright_yellow",
}


# ============================================================
#  COMBO COUNTER DISPLAY
# ============================================================

def render_combo_counter(combo, tier_name, multiplier, bar, glow):
    style = TIER_STYLE.get(tier_name, "dim")
    combo_str = str(combo)
    if combo >= 100:
        combo_str = f"{combo}!!!"
    elif combo >= 50:
        combo_str = f"{combo}!!"
    elif combo >= 10:
        combo_str = f"{combo}!"

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("K", width=12)
    table.add_column("V", width=50)

    table.add_row(
        f"[{style}]COMBO[/{style}]",
        f"[bold {style}]{combo_str}[/{style}]  [{style}]{glow}[/{style}]  [{style}]{tier_name}[/{style}]",
    )
    table.add_row(
        f"[{style}]MULTIPLIER[/{style}]",
        f"[bold {FX.GOLD}]x{multiplier}[/{FX.GOLD}]  [{style}]{bar}[/{style}]",
    )
    return table


def render_combo_hit(combo, tier_name, base_amount, bonus, total, multiplier):
    style = TIER_STYLE.get(tier_name, "dim")
    table = Table(
        title=f"[bold {style}]>> COMBO x{multiplier} HIT <<[/{style}]",
        box=box.DOUBLE_EDGE, border_style=style,
        show_header=False, padding=(0, 2),
    )
    table.add_column("K", width=16, style="bold")
    table.add_column("V", width=40)
    table.add_row("Combo Count", f"[bold {style}]{combo}[/{style}]")
    table.add_row("Tier", f"[{style}]{tier_name}[/{style}]")
    table.add_row("Base Earn", f"[{FX.WHITE}]{base_amount} MA[/{FX.WHITE}]")
    table.add_row("Bonus", f"[bold {FX.BONUS}]+{bonus} MA[/{FX.BONUS}]  [{style}]({multiplier}x)[/{style}]")
    table.add_row("Total", f"[bold {FX.GOLD}]{total} MA[/{FX.GOLD}]")
    return table


def render_combo_broken(old_combo, was_tier):
    style = TIER_STYLE.get(was_tier, "dim")
    table = Table(
        title=f"[bold {FX.RED}]>> COMBO BROKEN <<[/{FX.RED}]",
        box=box.HEAVY, border_style=FX.RED,
        show_header=False, padding=(0, 2),
    )
    table.add_column("K", width=16, style="bold")
    table.add_column("V", width=40)
    table.add_row("Lost Combo", f"[bold {FX.RED}]{old_combo}[/{FX.RED}]")
    table.add_row("Was Tier", f"[{style}]{was_tier}[/{style}]")
    table.add_row("Status", f"[{FX.RED}]RESET TO 0[/{FX.RED}]")
    return table


# ============================================================
#  ASCENSION RANK DISPLAY
# ============================================================

def render_rank_card(rank_name, rank_icon, rank_color, rank_title, karma, next_rank):
    table = Table(
        title=f"[bold {rank_color}]>> ASCENSION RANK <<[/{rank_color}]",
        box=box.DOUBLE_EDGE, border_style=rank_color,
        show_header=False, padding=(0, 2),
    )
    table.add_column("K", width=16, style="bold")
    table.add_column("V", width=40)
    table.add_row("Rank", f"[bold {rank_color}]{rank_icon} {rank_name}[/{rank_color}]")
    table.add_row("Title", f"[{rank_color}]{rank_title}[/{rank_color}]")
    table.add_row("Karma", f"[{FX.GOLD}]{karma}[/{FX.GOLD}]")
    if next_rank:
        needed = next_rank["min_karma"] - karma
        progress = min(100, (karma / next_rank["min_karma"]) * 100) if next_rank["min_karma"] > 0 else 0
        bar_len = int(progress / 5)
        bar = "|" * bar_len + "." * (20 - bar_len)
        table.add_row("Next Rank", f"[{FX.CYAN}]{next_rank['name']}[/{FX.CYAN}]  [{rank_color}]{bar}[/{rank_color}] {progress:.0f}%")
        table.add_row("Karma Needed", f"[{FX.GOLD}]{needed:.0f}[/{FX.GOLD}]")
    else:
        table.add_row("Status", f"[bold {FX.GOLD}]MAX RANK ACHIEVED[/{FX.GOLD}]")
    return table


def render_rank_up(prev_rank, new_rank, new_icon, new_color, new_title):
    table = Table(
        title=f"[bold {FX.GOLD}]>> ASCENSION UNLOCKED <<[/{FX.GOLD}]",
        box=box.HEAVY, border_style=FX.GOLD,
        show_header=False, padding=(0, 2),
    )
    table.add_column("K", width=16, style="bold")
    table.add_column("V", width=40)
    table.add_row("From", f"[{FX.DIM}]{prev_rank}[/{FX.DIM}]")
    table.add_row("To", f"[bold {new_color}]{new_icon} {new_rank}[/{new_color}]")
    table.add_row("Title", f"[{new_color}]{new_title}[/{new_color}]")
    table.add_row("Bonus", f"[bold {FX.BONUS}]x{new_color} multipliers applied![/{FX.BONUS}]")
    return table


# ============================================================
#  COMBO PROGRESS BAR
# ============================================================

def render_combo_progress(combo, tier_name, next_threshold):
    style = TIER_STYLE.get(tier_name, "dim")
    if next_threshold:
        progress = min(100, (combo / next_threshold) * 100) if next_threshold > 0 else 0
    else:
        progress = 100
    bar_len = int(progress / 5)
    filled = "|" * bar_len
    empty = "." * (20 - bar_len)
    bar = filled + empty

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("K", width=12)
    table.add_column("V", width=50)
    table.add_row(
        f"[{style}]TIER[/{style}]",
        f"[bold {style}]{tier_name} {bar} {progress:.0f}%[/{style}]",
    )
    if next_threshold:
        table.add_row(
            f"[{style}]NEXT[/{style}]",
            f"[{FX.CYAN}]Next: {next_threshold} combos[/{FX.CYAN}]",
        )
    return table


# ============================================================
#  ASCENSION PATH DISPLAY
# ============================================================

def render_ascension_path(current_karma):
    from .combo import ASCENSION_RANKS
    tree = Tree("ASCENSION PATH")
    for r in ASCENSION_RANKS:
        reached = current_karma >= r["min_karma"]
        icon = r["icon"]
        name = r["name"]
        if reached:
            label = f"[{r['color']}]{icon} {name} [ACHIEVED][/{r['color']}]"
        else:
            needed = r["min_karma"] - current_karma
            label = f"{icon} {name}  [{needed} karma needed]"
        tree.add(label)
    return tree


# ============================================================
#  FULL COMBO + RANK PANEL
# ============================================================

def render_combo_panel(combo_data, rank_karma=0):
    combo = combo_data.get("combo", 0)
    tier = combo_data.get("tier", "NONE")
    mult = combo_data.get("multiplier", 1.0)
    bar = combo_data.get("bar", "....................")
    glow = combo_data.get("glow", "")
    rank_name = combo_data.get("rank", "Mortal")
    rank_icon = combo_data.get("rank_icon", "--")
    rank_color = combo_data.get("rank_color", "dim")
    rank_title = combo_data.get("rank_title", "Unawakened Soul")

    style = TIER_STYLE.get(tier, "dim")

    sections = []
    sections.append(f"[bold {style}]COMBO[/{style}]  [bold {FX.GOLD}]x{mult}[/{FX.GOLD}]  [{style}]{tier}[/{style}]  [{style}]{glow}[/{style}]")
    sections.append(f"[bold {rank_color}]RANK[/{rank_color}]  [{rank_color}]{rank_icon} {rank_name}[/{rank_color}]  [{FX.DIM}]{rank_title}[/{FX.DIM}]")

    combo_str = str(combo)
    if combo >= 100:
        combo_str = f"{combo}!!!"
    elif combo >= 50:
        combo_str = f"{combo}!!"
    elif combo >= 10:
        combo_str = f"{combo}!"
    sections.append(f"[bold {FX.XP}]COMBO COUNT[/{FX.XP}]  [bold {style}]{combo_str}[/{style}]")

    content = "\n".join(sections)
    return Panel(
        content,
        title=f"[bold {FX.GOLD}]>> COMBO + RANK <<[/{FX.GOLD}]",
        border_style=style,
        box=box.DOUBLE_EDGE,
    )


# ============================================================
#  ACHIEVEMENT POPUP
# ============================================================

def render_achievement_popup(achievement_name, combo=0, rank=""):
    table = Table(
        title=f"[bold {FX.GOLD}]>> ACHIEVEMENT UNLOCKED <<[/{FX.GOLD}]",
        box=box.HEAVY, border_style=FX.GOLD,
        show_header=False, padding=(0, 2),
    )
    table.add_column("K", width=16, style="bold")
    table.add_column("V", width=40)
    table.add_row("Achievement", f"[bold {FX.GOLD}]{achievement_name}[/{FX.GOLD}]")
    if combo > 0:
        table.add_row("Combo", f"[{FX.CYAN}]{combo}[/{FX.CYAN}]")
    if rank:
        table.add_row("Rank", f"[{FX.GREEN}]{rank}[/{FX.GREEN}]")
    return table
