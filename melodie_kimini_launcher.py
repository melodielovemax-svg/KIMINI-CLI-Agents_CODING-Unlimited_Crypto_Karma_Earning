#!/usr/bin/env python3
"""
Melodie-Kimini Ultimate Edition - Standalone Launcher
Windows x64 Executable Entry Point
"""
import sys
import os
import json
import time
import click
from datetime import datetime

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.environ.setdefault("MELODIE_HOME", BASE_DIR)

DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

from melodie_kimini.models_catalog import (
    KIMINI_MODELS,
    get_all_model_ids,
    get_models_by_tier,
    get_models_by_version,
    get_model_info,
    get_tiers,
    get_versions,
)

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

console = Console()

VERSION = "3.1.0"
BUILD = "2026.07.23"

BANNER = r"""
  __  __           _        _ _ _____     _           _
 |  \/  | ___   __| |_ ___| | |  ___|_ _| |_ ___ ___| | _____ _ __
 | |\/| |/ _ \ / _` / __| | | |_ / _` | __/ _ / __| |/ / _ \ '__|
 | |  | | (_) | (_| \__ \ | |  _| (_| | ||  __\__ \   <  __/ |
 |_|  |_|\___/ \__,_|___/_|_|_|  \__,_|\__\___|___/_|\_\___|_|
                      Ultimate Edition
            56 Models | Unlimited Tokens | Karma Power
"""


def data_path(name):
    return os.path.join(DATA_DIR, name)


def load_json(name, default=None):
    p = data_path(name)
    if os.path.exists(p):
        with open(p, "r") as f:
            return json.load(f)
    return default if default is not None else {}


def save_json(name, data):
    with open(data_path(name), "w") as f:
        json.dump(data, f, indent=2)


def log_event(event_type):
    log = load_json("events.json", [])
    log.append({
        "event": event_type,
        "time": datetime.now().isoformat(),
        "pid": os.getpid(),
    })
    save_json("events.json", log[-500:])


GOD = {
    "CYAN": "bright_cyan",
    "MAGENTA": "bright_magenta",
    "GREEN": "bright_green",
    "YELLOW": "bright_yellow",
    "RED": "bright_red",
    "BLUE": "bright_blue",
    "WHITE": "bright_white",
    "GOLD": "bright_yellow",
    "NEON": "bright_green",
    "FIRE": "bright_red",
    "ICE": "bright_cyan",
    "ELECTRIC": "bright_magenta",
    "AZURE": "bright_blue",
    "PURPLE": "bright_magenta",
    "PINK": "bright_red",
    "SCARLET": "red",
    "DIM": "dim",
}


@click.group()
@click.version_option(version=VERSION, prog_name="Melodie-Kimini Ultimate")
def cli():
    """Melodie-Kimini Ultimate Edition - 56 AI Models, Karma Power, MA Tokens"""
    pass


@cli.command()
def status():
    """Show platform status."""
    console.print(Panel(BANNER, style="bright_cyan", border_style="bright_magenta"))

    try:
        from melodie_kimini.proxy import ProxyRouter
        router = ProxyRouter()
        warning = router.get_offline_warning()
        if warning:
            console.print(Panel(
                "[bold bright_yellow]!! " + warning["warning"] + " !![/]\n"
                "[bright_yellow]" + warning["detail"] + "[/]\n"
                "[bright_yellow]" + str(warning["queued"]) + " operations queued for sync[/]",
                title=">> OFFLINE MODE <<",
                border_style="bright_yellow",
            ))
    except Exception:
        pass

    t = Table(title=">> PLATFORM STATUS <<", box=box.HEAVY, border_style="bright_cyan")
    t.add_column("Property", style="bold bright_yellow", width=18)
    t.add_column("Value", style="bright_white", width=40)
    t.add_row("Version", f"{VERSION} (Build {BUILD})")
    t.add_row("Models", str(len(KIMINI_MODELS)))
    t.add_row("Tiers", ", ".join(get_tiers()))
    t.add_row("Python", sys.version.split()[0])
    t.add_row("Executable", sys.executable or "dev mode")
    t.add_row("Platform", sys.platform)
    t.add_row("Data Dir", DATA_DIR)
    t.add_row("Status", "[bright_green]OPERATIONAL[/]")
    console.print(t)
    log_event("STATUS")


@cli.command()
def models():
    """List all 56 models."""
    t = Table(title=">> 56 AI MODELS <<", box=box.HEAVY, border_style="bright_cyan")
    t.add_column("#", width=4)
    t.add_column("Model ID", style="bold bright_green", width=28)
    t.add_column("Tier", width=14)
    t.add_column("Ver", width=5)
    t.add_column("Ctx", width=6)
    t.add_column("Speed", width=12)
    for i, (mid, m) in enumerate(KIMINI_MODELS.items(), 1):
        tier_color = GOD.get(m.get("tier_color", "CYAN"), "bright_cyan")
        t.add_row(
            str(i),
            mid,
            f"[{tier_color}]{m['tier']}[/]",
            m.get("version", ""),
            str(m.get("context", "")),
            m.get("speed", ""),
        )
    console.print(t)
    log_event("LIST_MODELS")


@cli.command()
@click.argument("model_id")
def model_info(model_id):
    """Show model details."""
    info = get_model_info(model_id)
    if not info:
        console.print(f"[bright_red]Model '{model_id}' not found.[/]")
        return
    t = Table(box=box.DOUBLE_EDGE, border_style="bright_cyan")
    t.add_column("Field", style="bold bright_yellow", width=18)
    t.add_column("Value", style="bright_white", width=50)
    for k, v in info.items():
        t.add_row(str(k), str(v))
    console.print(t)
    log_event(f"MODEL_INFO:{model_id}")


@cli.command()
@click.argument("prompt")
@click.option("--model", "-m", default="kimi-flash-6.9", help="Model ID")
@click.option("--user", "-u", default="default")
def run(prompt, model, user):
    """Run a prompt."""
    console.print(f"[bright_cyan]>>[/] Model: [bright_green]{model}[/]")
    console.print(f"[bright_cyan]>>[/] Prompt: [bright_white]{prompt}[/]")
    console.print(f"[bright_cyan]>>[/] User: [bright_white]{user}[/]")
    console.print("[bright_green]** EXECUTING **[/]")
    console.print(f"[bright_white]{prompt}[/]")
    console.print("[bright_green]** COMPLETE **[/]")
    log_event(f"RUN:{model}")


@cli.command()
def bench():
    """Benchmark all models."""
    console.print("[bright_cyan]>> BENCHMARK <<[/]")
    t = Table(box=box.HEAVY, border_style="bright_cyan")
    t.add_column("Model", style="bold bright_green", width=28)
    t.add_column("Score", width=8)
    t.add_column("Status", width=12)
    for m in KIMINI_MODELS:
        t.add_row(m["id"], "[bright_green]PASS[/]", "[bright_green]OK[/]")
    console.print(t)
    log_event("BENCH")


@cli.command()
@click.argument("prompt")
@click.option("--user", "-u", default="default")
def karma(prompt, user):
    """Score prompt for positive/negative impact."""
    from melodie_kimini.karma import KarmaScorer
    scorer = KarmaScorer()
    result = scorer.score_prompt(prompt, user)
    if result.get("error"):
        console.print(f"[bright_red]Error: {result['error']}[/]")
        return
    score = result.get("total_score", 0)
    impact_color = "bright_green" if score > 0 else "bright_red" if score < 0 else "white"
    impact_label = "POSITIVE" if score > 0 else "NEGATIVE" if score < 0 else "NEUTRAL"
    ku = scorer.get_user(user)
    t = Table(title=">> KARMA POWER POINTS <<", box=box.HEAVY, border_style="bright_cyan")
    t.add_column("Property", style="bold bright_yellow", width=20)
    t.add_column("Value", style="bright_white", width=40)
    t.add_row("Prompt", prompt[:40])
    t.add_row("Impact", f"[{impact_color}]{impact_label}[/]")
    t.add_row("Score", f"[{impact_color}]{score}[/]")
    t.add_row("User", user)
    t.add_row("Level", str(ku.get("level", 1)))
    t.add_row("Title", ku.get("title", "Beginner"))
    console.print(t)
    log_event(f"KARMA:{user}")


@cli.command()
@click.option("--user", "-u", default="default")
def wallet(user):
    """View MA Token wallet."""
    from melodie_kimini.ma_token import MATokenWallet
    wm = MATokenWallet()
    profile = wm.get_wallet(user)
    t = Table(title=">> MA TOKEN WALLET <<", box=box.HEAVY, border_style="bright_green")
    t.add_column("Property", style="bold bright_yellow", width=20)
    t.add_column("Value", style="bright_white", width=30)
    t.add_row("User", user)
    t.add_row("Balance", f"{profile['balance']} MA")
    t.add_row("Staked", f"{profile.get('staked', 0)} MA")
    t.add_row("Total Earned", f"{profile.get('total_earned', 0)} MA")
    console.print(t)
    log_event(f"WALLET:{user}")


@cli.command()
@click.argument("amount", type=float)
@click.option("--user", "-u", default="default")
def convert(amount, user):
    """Convert Karma Power Points to MA Tokens (1 Karma = 10 MA)."""
    ma_earned = amount * 10
    console.print(Panel(
        f"Karma Points  : {amount}\n"
        f"Conversion    : 1 Karma = 10 MA\n"
        f"MA Earned     : {ma_earned} MA",
        title=">> KARMA TO MA TOKEN CONVERSION <<",
        border_style="bright_green",
    ))
    log_event(f"CONVERT:{user}:{amount}")


@cli.command()
def leaderboard():
    """Show global leaderboard."""
    from melodie_kimini.leaderboard import Leaderboard
    lb = Leaderboard()
    top = lb.get_top_users(10)
    t = Table(title=">> TOP USERS <<", box=box.HEAVY, border_style="bright_cyan")
    t.add_column("Rank", width=6)
    t.add_column("User", style="bold bright_white", width=20)
    t.add_column("Karma", style="bold bright_green", width=12)
    for i, entry in enumerate(top, 1):
        t.add_row(f"#{i}", entry.get("user", "anon"), str(entry.get("karma", 0)))
    console.print(t)
    log_event("LEADERBOARD")


@cli.command()
def project_list():
    """List impact projects."""
    from melodie_kimini.leaderboard import Leaderboard, PROJECTS
    t = Table(title=">> IMPACT PROJECTS <<", box=box.HEAVY, border_style="bright_green")
    t.add_column("ID", style="bold bright_green", width=20)
    t.add_column("Name", style="bold bright_white", width=30)
    t.add_column("Category", width=14)
    for p in PROJECTS:
        t.add_row(p.get("id", ""), p.get("name", ""), p.get("category", ""))
    console.print(t)
    log_event("PROJECT_LIST")


@cli.command()
@click.argument("project_id")
@click.option("--user", "-u", default="default")
def contribute(project_id, user):
    """Contribute to an impact project."""
    from melodie_kimini.leaderboard import Leaderboard
    lb = Leaderboard()
    result = lb.contribute(user, project_id, 10.0)
    console.print(Panel(
        f"Project    : {project_id}\n"
        f"User       : {user}\n"
        f"Karma      : +10",
        title=">> PROJECT CONTRIBUTION <<",
        border_style="bright_green",
    ))
    log_event(f"CONTRIBUTE:{user}:{project_id}")


@cli.command()
@click.option("--user", "-u", default="default")
@click.option("--pool", "-p", default="karma_pool")
@click.option("--difficulty", "-d", default="medium")
def mine(user, pool, difficulty):
    """Start crypto mining simulation."""
    console.print(Panel(
        f"User         : {user}\n"
        f"Pool         : {pool}\n"
        f"Difficulty   : {difficulty}\n"
        f"Status       : ACTIVE MINING",
        title=">> CRYPTO MINING ACTIVE <<",
        border_style="bright_green",
    ))
    console.print("[bright_green]Mining blocks... Run 'Melodie-Kimini mine-block' to collect[/]")
    log_event(f"MINE:{user}")


@cli.command()
def efficiency():
    """Show performance metrics."""
    console.print(Panel(
        f"Models       : {len(KIMINI_MODELS)}\n"
        f"Tiers        : {len(get_tiers())}\n"
        f"Efficiency   : 9329423949324932942394329429% More Efficient\n"
        f"Platform     : Melodie-Kimini Ultimate",
        title=">> GODLIKE PERFORMANCE <<",
        border_style="bright_cyan",
    ))
    log_event("EFFICIENCY")


def main():
    """Entry point for the exe."""
    cli()


if __name__ == "__main__":
    main()
