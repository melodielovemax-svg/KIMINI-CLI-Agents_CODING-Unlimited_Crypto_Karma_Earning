"""End-to-end tests for the Karma Ecosystem automation system.

Runs the complete lifecycle against the embedded EVM (EthereumTesterProvider):
real contracts, real transactions, real hashes, real blocks.
"""
import os
import time

import pytest
from eth_account import Account
from web3 import Web3

from karma_ecosystem.engine import KarmaEcosystemEngine
from karma_ecosystem.vault import Vault, VaultRecord


@pytest.fixture()
def eco(tmp_path):
    eng = KarmaEcosystemEngine(network_id="local", data_dir=str(tmp_path))
    eng.deploy()
    return eng


@pytest.fixture()
def vault(tmp_path, eco):
    return eco.open_vault("test-password-123")


def test_deploy_creates_all_contracts(eco):
    dep = eco.deployment
    assert dep.karma_token and dep.treasury and dep.subscription and dep.good_deeds
    plans = eco.list_plans()
    assert len(plans) == 3
    assert [p["name"] for p in plans] == ["Builder", "Pro", "Ultimate"]
    assert plans[2]["price_eth"] == 0.25


def test_full_lifecycle_subscribe_deed_treasury(eco, vault):
    sub = eco.register_subscriber("Alice", "alice@karma.eco", plan_id=1,
                                  password="alice-pass-123", vault=vault)
    sub_id = sub["subscriber_id"]
    assert sub_id.startswith("sub_")
    assert Web3.is_address(sub["address"])

    # 1. subscribe — real payment tx with on-chain fee split
    r = eco.subscribe(sub_id, vault, password="alice-pass-123")
    assert r["tx_hash"].startswith("0x")
    assert r["fee_eth"] == pytest.approx(r["amount_eth"] * 0.20, rel=0.01)
    assert r["active_until"] > time.time()

    # 2. good deed — KARMA minted on-chain
    beneficiary = eco._admin_account().address
    d = eco.good_deed(sub_id, vault, service="code review", category="service",
                      impact=7, beneficiary=beneficiary, password="alice-pass-123")
    assert d["impact"] == 7
    assert d["karma_reward"] == 70.0  # 10 KARMA per impact point

    # 3. wallet shows native + KARMA
    w = eco.wallet_info(sub_id, vault)
    assert w["karma_tokens"] == 70.0
    assert w["native_ETH"] > 0

    # 4. treasury collected the automation fee
    t = eco.treasury_info()
    assert t["revenue_fee_bps"] == 2000
    assert t["total_subscriptions"] == 1
    assert t["total_fees_eth"] == pytest.approx(r["fee_eth"], rel=0.001)
    assert t["total_revenue_eth"] == pytest.approx(r["amount_eth"], rel=0.001)


def test_verify_tx_hash(eco, vault):
    sub = eco.register_subscriber("Bob", "bob@karma.eco", plan_id=0,
                                  password="bob-pass-123", vault=vault)
    r = eco.subscribe(sub["subscriber_id"], vault, password="bob-pass-123")
    info = eco.verify_tx(r["tx_hash"])
    assert info["found"] is True
    assert info["status"] == "SUCCESS"
    assert info["block"] > 0
    assert info["logs"] >= 1


def test_treasury_distributes_to_agents(eco, vault):
    # two subscribers pay -> treasury fills
    for name, plan in [("Carol", 1), ("Dave", 2)]:
        sub = eco.register_subscriber(name, f"{name.lower()}@karma.eco", plan_id=plan,
                                      password=f"{name.lower()}-pass-123", vault=vault)
        eco.subscribe(sub["subscriber_id"], vault, password=f"{name.lower()}-pass-123")

    agent1 = Account.create().address
    agent2 = Account.create().address
    eco.register_agent("agent-alpha", agent1, weight=1)
    eco.register_agent("agent-beta", agent2, weight=3)

    before = eco.treasury_info()["balance_eth"]
    assert before > 0
    result = eco.distribute_to_agents(split_pct=100)
    assert result["distributed_eth"] == pytest.approx(before, rel=0.001)
    after = eco.treasury_info()
    assert after["balance_eth"] < 1e-12
    assert after["total_distributed_eth"] == pytest.approx(before, rel=0.001)
    # weighted: beta got ~3x alpha
    b2 = float(Web3.from_wei(eco.w3.eth.get_balance(Web3.to_checksum_address(agent2)), "ether"))
    b1 = float(Web3.from_wei(eco.w3.eth.get_balance(Web3.to_checksum_address(agent1)), "ether"))
    assert b2 > b1 * 2.5


def test_subscription_expiry_and_keeper_autorenew(eco, vault):
    sub = eco.register_subscriber("Erin", "erin@karma.eco", plan_id=0,
                                  password="erin-pass-123", vault=vault)
    r = eco.subscribe(sub["subscriber_id"], vault, password="erin-pass-123")
    # fast-forward expiry in the vault record (keeper reads vault + on-chain)
    rec = vault.get(sub["subscriber_id"])
    rec.active_until = time.time() - 1
    vault.upsert(rec)
    renewals = eco.auto_renew(vault, password="erin-pass-123")
    assert any(x["subscriber_id"] == sub["subscriber_id"] for x in renewals)
    info = eco.wallet_info(sub["subscriber_id"], vault)
    assert info["active"] is True


def test_vault_encryption_roundtrip_and_tamper(tmp_path):
    vpath = str(tmp_path / "vault.karma")
    v1 = Vault.open_or_create(vpath, "master-pass-123")
    v1.upsert(VaultRecord(
        subscriber_id="sub_x", name="X", email="x@x.io", plan_id=2,
        address="0x0000000000000000000000000000000000000001",
        keystore={"crypto": "fake"}, created_at=time.time(),
    ))
    v2 = Vault.open_or_create(vpath, "master-pass-123")
    assert v2.get("sub_x").name == "X"

    # wrong password rejected
    with pytest.raises(ValueError):
        Vault.open_or_create(vpath, "wrong-password")

    # tampering detected by sha256 integrity
    data = bytearray(open(vpath, "rb").read())
    data[20] ^= 0xFF
    with open(vpath, "wb") as f:
        f.write(bytes(data))
    with pytest.raises(ValueError, match="TAMPERED"):
        Vault.open_or_create(vpath, "master-pass-123")


def test_registered_wallet_has_encrypted_keystore(eco, vault):
    sub = eco.register_subscriber("Frank", "frank@karma.eco", plan_id=0,
                                  password="frank-pass-123", vault=vault)
    rec = vault.get(sub["subscriber_id"])
    # keystore is stored (Web3 JSON keystore with encrypted crypto material)
    assert rec.keystore.get("crypto") is not None
    # The raw vault file is a fully encrypted envelope — no plaintext PII leaks.
    raw = open(vault.path, "rb").read()
    for secret in (b"frank-pass-123", b"private_key", b"frank@karma.eco",
                   sub["address"].lower().encode()):
        assert secret not in raw, f"plaintext secret leaked in vault file: {secret!r}"
