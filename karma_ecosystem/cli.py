"""karma-eco — command-line front end for the Karma Ecosystem automation.

End-to-end automation in one tool:

    karma-eco init                     deploy contracts + create plans
    karma-eco status                    network / deployment / block info
    karma-eco plans                     list subscription plans
    karma-eco register NAME --email .. --plan 1 --password ..
    karma-eco subscribe SUB_ID --plan 1 --password ..
    karma-eco deed SUB_ID --service .. --impact 5 --beneficiary 0x..
    karma-eco wallet SUB_ID
    karma-eco treasury
    karma-eco register-agent NAME 0xADDR --weight 1
    karma-eco distribute --split 100
    karma-eco verify 0xHASH
    karma-eco keeper --password ..     automation loop: auto-renew expired
    karma-eco export --password .. --out private_doc.bin
    karma-eco unlock SUB_ID --password ..   (remember key in memory only)
"""
from __future__ import annotations

import json
import os
import time

import click

from .engine import KarmaEcosystemEngine, DEFAULT_PLANS
from .vault import Vault

def _engine(network: str) -> KarmaEcosystemEngine:
    return KarmaEcosystemEngine(network_id=network)

def _vault(engine, password) -> Vault:
    return engine.open_vault(password)

def _dump(obj: dict) -> None:
    click.echo(json.dumps(obj, indent=2, default=str))


@click.group()
@click.option("--network", type=click.Choice(["local", "localnode", "sepolia", "polygon_amoy"]),
              default="localnode", show_default=True,
              help="local (embedded, per-command) | localnode (persistent Ganache) | sepolia | polygon_amoy")
@click.pass_context
def cli(ctx, network):
    """Karma Ecosystem — rewards, subscriptions & treasury on the blockchain."""
    ctx.ensure_object(dict)
    ctx.obj["network"] = network


@cli.command()
@click.pass_obj
def status(obj):
    """Show network, chain and deployment status."""
    eng = _engine(obj["network"])
    _dump(eng.status())


@cli.command()
@click.pass_obj
def init(obj):
    """Deploy contracts, wire roles, create the Ultimate Pays plans."""
    eng = _engine(obj["network"])
    dep = eng.deploy()
    click.echo("Deployed:")
    _dump({
        "network": dep.network,
        "chain_id": dep.chain_id,
        "karma_token": dep.karma_token,
        "treasury": dep.treasury,
        "subscription": dep.subscription,
        "good_deed_registry": dep.good_deeds,
        "protocol_wallet": dep.protocol_wallet,
        "plans": eng.list_plans(),
    })


@cli.command()
@click.pass_obj
def plans(obj):
    """List subscription plans (real on-chain data)."""
    eng = _engine(obj["network"])
    if eng.deployment is None:
        raise click.ClickException("not deployed yet — run `karma-eco init` first")
    _dump({"plans": eng.list_plans()})


@cli.command()
@click.option("--name", required=True)
@click.option("--email", default="subscriber@karma.eco")
@click.option("--plan", "plan_id", type=int, default=1, help="plan id (0 Builder, 1 Pro, 2 Ultimate)")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.pass_obj
def register(obj, name, email, plan_id, password):
    """Create a new subscriber: fresh wallet + encrypted private vault record."""
    eng = _engine(obj["network"])
    if eng.deployment is None:
        eng.deploy()
    vault = _vault(eng, password)
    out = eng.register_subscriber(name, email, plan_id, password, vault)
    _dump(out)


@cli.command()
@click.argument("subscriber_id")
@click.option("--plan", "plan_id", type=int, default=None)
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
def subscribe(obj, subscriber_id, plan_id, password):
    """Pay for a plan with a real blockchain transaction (hash)."""
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    _dump(eng.subscribe(subscriber_id, vault, plan_id=plan_id, password=password))


@cli.command("deed")
@click.argument("subscriber_id")
@click.option("--service", required=True, help="e.g. 'code review' or 'community support'")
@click.option("--category", default="service")
@click.option("--impact", type=click.IntRange(1, 10), default=5)
@click.option("--beneficiary", required=True, help="0x address that benefited")
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
def deed(obj, subscriber_id, service, category, impact, beneficiary, password):
    """Register a good deed — KARMA reward minted on-chain."""
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    _dump(eng.good_deed(subscriber_id, vault, service, category, impact, beneficiary,
                        password=password))


@cli.command()
@click.argument("subscriber_id")
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
def wallet(obj, subscriber_id, password):
    """Show a subscriber's on-chain balances (native + KARMA)."""
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    _dump(eng.wallet_info(subscriber_id, vault))


@cli.command()
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
def unlock(obj, password):
    """Unlock the vault and cache subscriber keys (memory only, not saved)."""
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    for rec in vault.list():
        eng.remember_key(rec.subscriber_id, password, vault)
    click.echo(f"unlocked {len(vault.list())} subscriber(s) for this session")


@cli.command()
@click.pass_obj
def treasury(obj):
    """Show treasury balances, collected fees and subscription totals."""
    eng = _engine(obj["network"])
    if eng.deployment is None:
        raise click.ClickException("not deployed yet — run `karma-eco init` first")
    _dump(eng.treasury_info())


@cli.command("register-agent")
@click.argument("name")
@click.argument("address")
@click.option("--weight", type=int, default=1)
@click.pass_obj
def register_agent(obj, name, address, weight):
    """Register a coding agent / app builder to receive treasury payouts."""
    eng = _engine(obj["network"])
    _dump(eng.register_agent(name, address, weight))


@cli.command()
@click.option("--split", type=click.IntRange(1, 100), default=100,
              help="% of treasury balance to distribute this run")
@click.pass_obj
def distribute(obj, split):
    """Automation: pay registered coding agents from the treasury."""
    eng = _engine(obj["network"])
    if eng.deployment is None:
        raise click.ClickException("not deployed yet — run `karma-eco init` first")
    _dump(eng.distribute_to_agents(split_pct=split))


@cli.command()
@click.argument("tx_hash")
@click.pass_obj
def verify(obj, tx_hash):
    """Verify any transaction hash on the chain."""
    eng = _engine(obj["network"])
    _dump(eng.verify_tx(tx_hash))


@cli.command()
@click.option("--password", prompt=True, hide_input=True)
@click.option("--out", default=None, help="output file for the exported private document")
@click.pass_obj
def export(obj, password, out):
    """Export the encrypted private vault document (all account data)."""
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    path = out or os.path.join(os.getcwd(), "karma_private_document.bin")
    vault.export_document(path)
    click.echo(f"private document exported -> {path} (AES-256-GCM, sha256: {path}.sha256)")


@cli.command()
@click.option("--once", is_flag=True, help="run one renewal pass instead of a loop")
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
def keeper(obj, once, password):
    """Automation keeper loop: renew expired subscriptions, then repeat."""
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    if once:
        _dump({"renewals": eng.auto_renew(vault, password)})
        return
    click.echo("keeper running (Ctrl-C to stop) ...")
    while True:
        try:
            result = eng.auto_renew(vault, password)
            if result:
                _dump({"renewals": result})
        except Exception as e:  # noqa: BLE001
            click.echo(f"keeper error: {e}", err=True)
        time.sleep(30)




# ---------------------------------------------------------------- economy CLI
@cli.command()
@click.argument("subscriber_id")
@click.option("--karma", "karma_amount", type=float, required=True)
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
def convert(obj, subscriber_id, karma_amount, password):
    """Convert Karma Power -> MA tokens (1 KARMA = 10 MA, real burn+mint)."""
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    _dump(eng.convert_karma_to_ma(subscriber_id, vault, karma_amount, password=password))


@cli.command()
@click.argument("subscriber_id")
@click.option("--target", type=click.Choice(["eth", "usdt", "btc"]), required=True)
@click.option("--ma", "ma_amount", type=float, required=True)
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
def swap(obj, subscriber_id, target, ma_amount, password):
    """Swap MA -> ETH / USDT / BTC through KarmaSwap (real transactions)."""
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    _dump(eng.swap_ma(subscriber_id, vault, target, ma_amount, password=password))


@cli.command()
@click.argument("subscriber_id")
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
def mine(obj, subscriber_id, password):
    """Mine crypto on-chain: MA minted to the subscriber wallet (real hash)."""
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    _dump(eng.mine(subscriber_id, vault, password=password))


@cli.command("mine-all")
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
def mine_all(obj, password):
    """Keeper automation: batch-mine for every subscriber in ONE transaction."""
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    _dump(eng.mine_all(vault))


@cli.command()
@click.argument("subscriber_id")
@click.option("--to", "to_address", required=True, help="external wallet, e.g. your MetaMask address")
@click.option("--token", type=click.Choice(["ma", "karma", "eth"]), default="ma")
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
def sweep(obj, subscriber_id, to_address, token, password):
    """Send earnings to any wallet (MetaMask) — real transfer transaction."""
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    _dump(eng.sweep(subscriber_id, vault, to_address, token=token, password=password))


@cli.command()
@click.pass_obj
def tokenomics(obj):
    """MA tokenomics: supply, allocations, swap rates, mining, pools."""
    eng = _engine(obj["network"])
    if eng.deployment is None:
        raise click.ClickException("not deployed yet — run `karma-eco init` first")
    _dump(eng.tokenomics())


# ------------------------------------------------------------------ bot CLI
@cli.group()
@click.pass_obj
def bot(obj):
    """Bot Revenue Automation System — self-running revenue workflows."""


@bot.command()
@click.option("--pipeline", default="full", help="task ids or 'full'")
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
def run(obj, pipeline, password):
    """Execute the A-Z tasklist process workflow (real automation)."""
    from .automation import BotRevenueAutomation
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    bot = BotRevenueAutomation(eng, vault)
    ids = None if pipeline == "full" else [x.strip() for x in pipeline.split(",")]
    _dump(bot.run(ids))


@bot.command()
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
def status(obj, password):
    """Bot version, phases, task count and release info."""
    from .automation import BotRevenueAutomation
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    bot = BotRevenueAutomation(eng, vault)
    _dump(bot.status())


@bot.command("tasks")
@click.pass_obj
def bot_tasks(obj):
    """List every task in the process execution workflow."""
    from .automation import BotRevenueAutomation
    eng = _engine(obj["network"])
    vault = _vault(eng, "x")  # tasks are static; no vault access needed
    bot = BotRevenueAutomation(eng, vault)
    _dump({"tasks": bot.list_tasks()})


@bot.command()
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
def release(obj, password):
    """Automatically release a new bot revenue system version."""
    from .automation import BotRevenueAutomation
    eng = _engine(obj["network"])
    vault = _vault(eng, password)
    bot = BotRevenueAutomation(eng, vault)
    _dump(bot.release(agent="cli"))


@bot.command()
@click.pass_obj
def timeline(obj):
    """Quantum fractal workflow timeline: A-Z phases with est times."""
    from .automation import BotRevenueAutomation
    eng = _engine(obj["network"])
    vault = _vault(eng, "x")
    bot = BotRevenueAutomation(eng, vault)
    _dump(bot.timeline())


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
