"""
POSITIVE IMPACT HYPE POPUP SYSTEM
Non-intrusive visual popups that celebrate positive impact with ranking comments.
Boosts user motivation and platform engagement.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

# ============================================================
#  HYPE COMMENT DATABASE
# ============================================================

HYPE_BY_CATEGORY = {
    "education": [
        "Knowledge is the ultimate currency -- you're minting futures!",
        "Every lesson plants a forest of possibilities.",
        "Teaching is the highest form of alchemy: turning thought into gold.",
        "You're not just educating -- you're rewiring the world.",
        "The ripple of one lesson reaches across oceans.",
    ],
    "health": [
        "Healing the body heals the soul -- you're doing both!",
        "Wellness is the foundation of every revolution.",
        "Your impact saves lives before they even know it.",
        "Health is wealth, and you're building empires.",
        "Every healthy choice echoes through generations.",
    ],
    "environment": [
        "The planet breathes easier because of you.",
        "Green isn't just a color -- it's a legacy.",
        "You're planting forests that will outlive empires.",
        "Clean oceans start with one brave choice.",
        "Nature doesn't forget its guardians.",
    ],
    "community": [
        "Together we rise -- and you're lifting everyone.",
        "Community is the original superpower.",
        "Your service creates bonds that time cannot break.",
        "One act of kindness ripples through eternity.",
        "You're the bridge between where we are and where we belong.",
    ],
    "innovation": [
        "The future doesn't just arrive -- you're building it!",
        "Innovation is courage with a blueprint.",
        "Every prototype is a step toward the impossible.",
        "You're not solving problems -- you're dissolving them.",
        "The world needs your weird ideas. Never stop creating.",
    ],
    "arts": [
        "Art is the language the universe speaks fluently.",
        "Creativity is the spark that lights entire civilizations.",
        "Your art will outlast stone and steel.",
        "Culture is the soul of humanity -- you're keeping it alive.",
        "Every brushstroke is a rebellion against the ordinary.",
    ],
    "charity": [
        "Giving is the only act that multiplies by division.",
        "Your generosity writes chapters in strangers' stories.",
        "True wealth is measured in lives touched.",
        "Charity is the rent we pay for occupying this planet.",
        "You're not giving away -- you're building forever.",
    ],
    "sustainability": [
        "Sustainability isn't sacrifice -- it's wisdom in action.",
        "You're not just going green -- you're going eternal.",
        "Future generations will know your name through clean air.",
        "Every sustainable choice is a vote for eternity.",
        "The Earth remembers its protectors.",
    ],
    "research": [
        "Discovery is the oldest adventure -- and you're on the frontier.",
        "Every question is a door. You're building keys.",
        "Research turns curiosity into civilization.",
        "You're not just studying the universe -- you're teaching it about itself.",
        "Knowledge gained today becomes the foundation of tomorrow.",
    ],
    "mentorship": [
        "A mentor doesn't create followers -- they create leaders.",
        "You're not just guiding -- you're igniting.",
        "The best mentors plant seeds they'll never see grow.",
        "Your wisdom echoes in every person you uplift.",
        "Mentorship is the ultimate long-term investment.",
    ],
    "open_source": [
        "Open source is the democracy of knowledge.",
        "You're not just sharing code -- you're sharing freedom.",
        "Collaboration is humanity's oldest superpower.",
        "Your contribution multiplies across every mind it touches.",
        "The commons grows because of people like you.",
    ],
    "accessibility": [
        "Inclusion isn't a feature -- it's the foundation.",
        "You're building bridges where others see walls.",
        "Accessibility is the truest form of innovation.",
        "Everyone deserves access. You're making it real.",
        "Your work opens doors that were never supposed to be closed.",
    ],
}

HYPE_BY_RANK = {
    "Mortal":         "Every journey starts with a single step. Yours has begun.",
    "Acolyte":        "The path reveals itself to those who walk it.",
    "Monk":           "Your discipline is shaping something extraordinary.",
    "Sage":           "Wisdom earned is wisdom that transforms the world.",
    "Buddha":         "Enlightenment isn't the end -- it's the beginning of true service.",
    "Demigod":        "You walk between worlds, building bridges for humanity.",
    "God":            "Your vision shapes reality. The universe bends to your purpose.",
    "Archangel":      "Heaven's champion -- your light guides millions.",
    "Seraphim":       "Six wings of pure impact. You've transcended the ordinary.",
    "Cosmic Overlord":"You don't just change the game -- you ARE the game.",
}

HYPE_BY_COMBO = {
    0:   "Every positive action counts. Start your streak!",
    5:   "Bronze streak! You're building momentum!",
    15:  "Silver streak! The impact is compounding!",
    30:  "Gold streak! You're unstoppable!",
    50:  "Platinum streak! Legendary energy!",
    75:  "Diamond streak! You're a force of nature!",
    100: "LEGENDARY STREAK! The universe is taking notes!",
    150: "MYTHIC STREAK! You've broken the scale!",
}

HYPE_BY_KARMA = {
    0:     "Your journey of impact starts now. Every word matters.",
    50:    "50 karma! You're making ripples in the cosmos.",
    100:   "100 karma! A Positive Force has awakened.",
    200:   "200 karma! Impact Maker status achieved.",
    500:   "500 karma! You're a Community Leader.",
    1000:  "1000 karma! WORLD CHANGER detected.",
    2500:  "2500 karma! Planetary Hero level unlocked.",
    5000:  "5000 karma! Universal Sage -- your wisdom echoes.",
    10000: "10000 karma! COSMIC GUARDIAN. You are the light.",
}


# ============================================================
#  CONCEPT ANALYZER
# ============================================================

CONCEPT_KEYWORDS = {
    "education":     ["learn", "teach", "school", "university", "course", "tutorial", "book", "knowledge", "study", "student"],
    "health":        ["health", "medical", "cure", "therapy", "wellness", "exercise", "nutrition", "mental health", "hospital"],
    "environment":   ["green", "renewable", "carbon", "ocean", "forest", "wildlife", "recycle", "sustainable", "plant"],
    "community":     ["volunteer", "community", "help", "support", "neighbor", "local", "together", "serve", "group"],
    "innovation":    ["invent", "create", "build", "design", "develop", "prototype", "solution", "engineer", "tech"],
    "arts":          ["art", "music", "paint", "write", "poetry", "theater", "creative", "culture", "design"],
    "charity":       ["donate", "give", "fund", "charity", "nonprofit", "aid", "relief", "sponsor", "help"],
    "sustainability":["sustainable", "eco", "organic", "zero waste", "compost", "energy efficient", "green"],
    "research":      ["research", "study", "experiment", "discover", "analyze", "investigate", "science"],
    "mentorship":    ["mentor", "guide", "coach", "teach", "lead", "inspire", "empower", "wisdom"],
    "open_source":   ["open source", "contribute", "collaborate", "share", "public", "free", "community"],
    "accessibility": ["accessible", "inclusive", "disability", "universal", "equitable", "diverse"],
}


def analyze_concept(prompt):
    """Analyze prompt for impact concepts."""
    prompt_lower = prompt.lower()
    found = []
    for cat, keywords in CONCEPT_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in prompt_lower)
        if matches > 0:
            found.append({"category": cat, "matches": matches})
    found.sort(key=lambda x: x["matches"], reverse=True)
    return found


def get_hype_comment(category, rank="Mortal", combo=0, karma=0):
    """Get a contextual hype comment."""
    import random
    comments = HYPE_BY_CATEGORY.get(category, ["Your positive impact matters. Keep going!"])
    comment = random.choice(comments)
    rank_comment = HYPE_BY_RANK.get(rank, "")
    combo_val = 0
    for threshold in sorted(HYPE_BY_COMBO.keys(), reverse=True):
        if combo >= threshold:
            combo_val = threshold
            break
    combo_comment = HYPE_BY_COMBO.get(combo_val, "")
    karma_val = 0
    for threshold in sorted(HYPE_BY_KARMA.keys(), reverse=True):
        if karma >= threshold:
            karma_val = threshold
            break
    karma_comment = HYPE_BY_KARMA.get(karma_val, "")
    return comment, rank_comment, combo_comment, karma_comment


# ============================================================
#  POPUP RENDERER
# ============================================================

def render_impact_hype_popup(prompt, karma_score, rank="Mortal", combo=0, total_karma=0):
    """Render a non-intrusive positive impact hype popup."""
    concepts = analyze_concept(prompt)
    if not concepts:
        concepts = [{"category": "innovation", "matches": 1}]

    top_cat = concepts[0]["category"]
    comment, rank_comment, combo_comment, karma_comment = get_hype_comment(top_cat, rank, combo, total_karma)

    cat_display = top_cat.upper()
    score_color = "bright_green" if karma_score > 0 else "bright_red" if karma_score < 0 else "white"

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("K", width=16, style="bold bright_cyan")
    table.add_column("V", width=54)

    table.add_row("Concept", f"[bold bright_yellow]{cat_display}[/]")
    table.add_row("Score", f"[bold {score_color}]+{karma_score}[/]")
    table.add_row("", "")
    table.add_row("Impact", f"[bright_green]{comment}[/]")
    if rank_comment:
        table.add_row("Rank", f"[bright_cyan]{rank_comment}[/]")
    if combo_comment and combo > 0:
        table.add_row("Combo", f"[bright_magenta]{combo_comment}[/]")
    if karma_comment:
        table.add_row("Journey", f"[bright_yellow]{karma_comment}[/]")

    concepts_str = " > ".join([f"[bright_white]{c['category'].upper()}[/]" for c in concepts[:3]])
    table.add_row("Dimensions", concepts_str)

    panel = Panel(
        table,
        title=f"[bold bright_green]>> POSITIVE IMPACT DETECTED <<[/]",
        border_style="bright_green",
        box=box.DOUBLE_EDGE,
        padding=(1, 1),
    )
    return panel


def render_streak_hype_popup(streak_days, bonus_ma):
    """Render a streak milestone popup."""
    if streak_days < 3:
        return None

    milestones = {
        3:  "Three-day streak! Consistency is power.",
        7:  "One week strong! You're building a habit of impact.",
        14: "Two weeks! Your dedication inspires others.",
        30: "One month! You're a pillar of the community.",
        60: "Two months! Legendary consistency.",
        90: "Three months! You've ascended beyond ordinary.",
        180: "Half a year! The universe recognizes your commitment.",
        365: "ONE YEAR! You are a monument to positive impact.",
    }

    msg = milestones.get(streak_days, f"{streak_days}-day streak! Keep rising!")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("K", width=16, style="bold bright_yellow")
    table.add_column("V", width=50)
    table.add_row("Streak", f"[bold bright_green]{streak_days} days[/]")
    table.add_row("Bonus", f"[bold bright_yellow]+{bonus_ma} MA[/]")
    table.add_row("Message", f"[bright_cyan]{msg}[/]")

    return Panel(
        table,
        title=f"[bold bright_green]>> STREAK MILESTONE <<[/]",
        border_style="bright_green",
        box=box.DOUBLE_EDGE,
        padding=(1, 1),
    )


def render_level_up_popup(old_level, new_level, old_title, new_title, karma):
    """Render a level-up popup."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("K", width=16, style="bold bright_yellow")
    table.add_column("V", width=50)
    table.add_row("Level Up", f"[bold bright_green]{old_level} >> {new_level}[/]")
    table.add_row("Title", f"[bold bright_yellow]{new_title}[/]")
    table.add_row("Karma", f"[bright_cyan]{karma}[/]")
    table.add_row("Message", f"[bright_green]You've grown stronger. The impact deepens.[/]")

    return Panel(
        table,
        title=f"[bold bright_yellow]>> LEVEL UP <<[/]",
        border_style="bright_yellow",
        box=box.DOUBLE_EDGE,
        padding=(1, 1),
    )


def render_earning_boost_popup(boost_pct, session_minutes, total_ma):
    """Render a time-based earning boost popup."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("K", width=16, style="bold bright_cyan")
    table.add_column("V", width=50)
    table.add_row("Session", f"[bright_white]{session_minutes} minutes[/]")
    table.add_row("Boost", f"[bold bright_green]+{boost_pct}%[/]")
    table.add_row("Earned", f"[bold bright_yellow]{total_ma} MA[/]")
    table.add_row("Message", f"[bright_green]Time spent = more impact. You're earning more![/]")

    return Panel(
        table,
        title=f"[bold bright_cyan]>> TIME BOOST ACTIVE <<[/]",
        border_style="bright_cyan",
        box=box.DOUBLE_EDGE,
        padding=(1, 1),
    )


def render_mini_hype_line(combo, tier, rank, karma):
    """Single-line hype bar for the bottom of commands."""
    from .combo import get_combo_tier, get_ascension_rank
    tier_info = get_combo_tier(combo)
    rank_info = get_ascension_rank(karma)
    tc = tier_info.get("color", "dim")
    rc = rank_info.get("color", "dim")
    line = (
        f"[dim]>>[/] [{tc}]{tier}[/] x{tier_info['mult']} | "
        f"[{rc}]{rank_info['icon']} {rank}[/] | "
        f"[bright_yellow]Karma: {karma}[/]"
    )
    return line
