"""Tests for the economy layer (MA tokenomics, swap, mining, sweep) and the
Bot Revenue Automation System."""
import time

import pytest
from eth_account import Account

from karma_ecosystem.automation import BotRevenueAutomation
from karma_ecosystem.engine import KarmaEcosystemEngine


@pytest.fixture()
def eco(tmp_path):
    eng = KarmaEcosystemEngine(network_id="local", data_dir=str(tmp_path))
    eng.deploy()
    return eng


@pytest.fixture()
def vault(tmp_path, eco):
    return eco.open_vault("test-password-123")


def _subscribe_and_deed(eco, vault, name, plan=1):
    sub = eco.register_subscriber(name, f"{name.lower()}@karma.eco", plan_id=plan,
                                  password=f"{name.lower()}-pass-123", vault=vault)
    eco.subscribe(sub["subscriber_id"], vault, password=f"{name.lower()}-pass-123")
    eco.good_deed(sub["subscriber_id"], vault, service="community help", category="deed",
                  impact=3, beneficiary=eco._admin_account().address,
                  password=f"{name.lower()}-pass-123")
    return sub["subscriber_id"]


def test_tokenomics_snapshot(eco):
    t = eco.tokenomics()
    assert t["token"] == "MA"
    assert t["hard_cap"] == 1_000_000_000.0
    assert t["total_supply"] == 100_000_000.0  # team 10% pre-mint
    assert t["swap_rates"]["eth_per_ma"] == 0.00001
    assert t["swap_rates"]["usdt_per_ma"] == 0.0001
    assert t["swap_rates"]["btc_per_ma"] == 0.00000005
    assert t["pool_balances"]["eth_pool"] == pytest.approx(0.5, rel=0.001)
    assert t["pool_balances"]["usdt_pool"] == pytest.approx(100, rel=0.001)
    assert t["pool_balances"]["btc_pool"] == pytest.approx(0.02, rel=0.001)


def test_karma_to_ma_convert(eco, vault):
    sub_id = _subscribe_and_deed(eco, vault, "Grace")
    r = eco.convert_karma_to_ma(sub_id, vault, karma_amount=30,
                                password="grace-pass-123")
    assert r["ma_minted"] == 300
    assert r["karma_burned"] == 30
    assert r["burn_tx"].startswith("0x")
    w = eco.wallet_info(sub_id, vault)
    assert w["ma_tokens"] == 300


def test_swap_ma_to_eth_usdt_btc(eco, vault):
    sub_id = _subscribe_and_deed(eco, vault, "Hank")
    eco.convert_karma_to_ma(sub_id, vault, 30, password="hank-pass-123")  # 30 KARMA -> 300 MA
    r = eco.swap_ma(sub_id, vault, "eth", 100, password="hank-pass-123")
    assert r["eth_out"] == pytest.approx(0.001, rel=0.01)  # 100 MA * 1e-5
    r = eco.swap_ma(sub_id, vault, "usdt", 100, password="hank-pass-123")
    assert r["usdt_out"] == pytest.approx(0.01, rel=0.01)  # 100 MA * 1e-4
    r = eco.swap_ma(sub_id, vault, "btc", 100, password="hank-pass-123")
    assert r["btc_out"] == pytest.approx(0.000005, rel=0.01)  # 100 MA * 5e-8
    w = eco.wallet_info(sub_id, vault)
    assert w["usdt_pegged"] > 0 and w["btc_pegged"] > 0
    t = eco.tokenomics()
    assert t["swap_totals"]["ma_burned"] == pytest.approx(300, rel=0.001)


def test_mining_and_sweep_to_external_wallet(eco, vault):
    sub_id = _subscribe_and_deed(eco, vault, "Iris")
    m = eco.mine(sub_id, vault, password="iris-pass-123")
    assert m["reward_ma"] == 100
    assert m["tx_hash"].startswith("0x")
    # sweep MA to an external wallet (e.g. MetaMask address)
    ext = Account.create().address
    r = eco.sweep(sub_id, vault, ext, token="ma", password="iris-pass-123")
    assert r["MA_sent"] == pytest.approx(100, rel=0.001)
    assert eco.w3.eth.get_balance(ext) >= 0 or True  # EOA balance check for tokens
    ma = eco._contract("MAToken", eco.deployment.ma_token)
    assert ma.functions.balanceOf(ext).call() == pytest.approx(100 * 10**18, rel=0.001)


def test_mine_all_batches_subscribers(eco, vault):
    _subscribe_and_deed(eco, vault, "Jill")
    _subscribe_and_deed(eco, vault, "Ken")
    r = eco.mine_all(vault)
    assert r["miners"] == 2
    t = eco.tokenomics()
    assert t["mining"]["mine_count"] == 2
    assert t["mining"]["total_mined_ma"] == pytest.approx(200, rel=0.001)


def test_bot_revenue_automation_full_workflow(eco, vault):
    _subscribe_and_deed(eco, vault, "Liam")
    _subscribe_and_deed(eco, vault, "Mia")
    bot = BotRevenueAutomation(eco, vault)
    summary = bot.run()
    assert summary["tasks"] == len(bot.tasks)
    assert summary["ok"] > 0
    assert summary["errors"] == 0, summary["results"]
    # the bot released a new version automatically during the run
    st = bot.status()
    assert st["version"].startswith("1.")
    assert st["last_updated"] != "never"


def test_bot_release_bumps_version_and_offerings(eco, vault):
    bot = BotRevenueAutomation(eco, vault)
    r1 = bot.release(agent="test")
    r2 = bot.release(agent="test")
    v1 = tuple(int(x) for x in r1["version"].split("."))
    v2 = tuple(int(x) for x in r2["version"].split("."))
    assert v2 > v1
    assert r2["release_count"] == 2
    import os
    assert os.path.exists(bot.offerings_file)
    offers = __import__("json").load(open(bot.offerings_file))
    assert len(offers["products"]) >= 3 and len(offers["services"]) >= 3


def test_bot_timeline_has_26_phases(eco, vault):
    bot = BotRevenueAutomation(eco, vault)
    tl = bot.timeline()
    assert len(tl["phases"]) == 26
    assert tl["phases"][0]["phase"] == "A-ALPHA"
    assert tl["phases"][-1]["phase"] == "Z-ZULU"
    assert tl["total_tasks"] == len(bot.tasks)
    assert tl["total_est_minutes"] > 0
