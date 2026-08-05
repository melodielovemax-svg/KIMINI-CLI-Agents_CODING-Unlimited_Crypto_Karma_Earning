"""Karma Ecosystem automation engine.

Turns the whole loop into one system:

  register subscriber ─▶ creates wallet + encrypted private vault record
  subscribe ──────────▶ real on-chain payment tx (hash) with fee split:
                         treasury fee (automation revenue fee) + protocol share
  good deed ──────────▶ real on-chain deed tx -> KARMA minted to doer
  treasury ───────────▶ keeper automation pays coding agents (hashed payouts)
  verify ─────────────▶ any tx hash -> receipt, block, status

The engine is chain-agnostic: identical code runs on the embedded EVM
(local), Sepolia, or Polygon Amoy — only the RPC differs.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass

from eth_account import Account
from web3 import Web3
from web3.exceptions import TransactionNotFound

from . import __version__
from .networks import NETWORKS, get_network
from .vault import Vault, VaultRecord
from .wallet import Wallet, create_wallet

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "contracts", "build")
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Default "Ultimate Pays" subscription plans for app builder / coding agents.
DEFAULT_PLANS = [
    {"name": "Builder",    "price_eth": 0.01, "duration_days": 30, "desc": "Starter access for solo app builders"},
    {"name": "Pro",        "price_eth": 0.05, "duration_days": 30, "desc": "Full coding-agent toolkit + priority rewards"},
    {"name": "Ultimate",   "price_eth": 0.25, "duration_days": 90, "desc": "Ultimate Pays: all agents, treasury payouts, 3x karma"},
]

TREASURY_FEE_BPS = 2000  # 20% automation revenue fee (configurable on-chain)


def _load_artifact(name: str) -> dict:
    with open(os.path.join(ARTIFACTS_DIR, f"{name}.json")) as f:
        return json.load(f)


@dataclass
class Deployment:
    network: str
    chain_id: int
    karma_token: str
    treasury: str
    subscription: str
    good_deeds: str
    protocol_wallet: str
    deployed_at: float
    ma_token: str = ""
    wusdt: str = ""
    wbtc: str = ""
    swap: str = ""
    mining_rig: str = ""


class KarmaEcosystemEngine:
    def __init__(self, network_id: str = "local", data_dir: str | None = None):
        self.network = get_network(network_id)
        self.data_dir = data_dir or DEFAULT_DATA_DIR
        os.makedirs(self.data_dir, exist_ok=True)
        self.deploy_file = os.path.join(self.data_dir, "deployment.json")
        self.state_file = os.path.join(self.data_dir, "state.json")
        self.w3 = self._connect()
        self.deployment = self._load_deployment()
        self.faucet_account = None
        self._local_admin = None
        self.state = self._load_state()

    @staticmethod
    def _hx(h) -> str:
        """Normalize a hex hash to 0x-prefixed lowercase hex."""
        return Web3.to_hex(h) if isinstance(h, bytes) else ("0x" + h if not h.startswith("0x") else h)

    # ------------------------------------------------------------------ chain
    def _connect(self) -> Web3:
        if self.network.rpc_url is None:
            from web3.providers.eth_tester import EthereumTesterProvider
            return Web3(EthereumTesterProvider())
        return Web3(Web3.HTTPProvider(self.network.rpc_url, request_kwargs={"timeout": 20}))

    def _load_deployment(self) -> Deployment | None:
        if os.path.exists(self.deploy_file):
            d = json.load(open(self.deploy_file))
            if d.get("network") == self.network.id:
                return Deployment(**d)
        return None

    def _save_deployment(self, dep: Deployment) -> None:
        json.dump(dep.__dict__, open(self.deploy_file, "w"), indent=2)

    def _load_state(self) -> dict:
        if os.path.exists(self.state_file):
            return json.load(open(self.state_file))
        return {"agents": {}, "agent_weights": {}, "autorenew": True}

    def _save_state(self) -> None:
        json.dump(self.state, open(self.state_file, "w"), indent=2)

    @property
    def chain_id(self) -> int:
        return int(self.w3.eth.chain_id)

    def status(self) -> dict:
        return {
            "system": f"Karma Ecosystem v{__version__}",
            "network": self.network.name,
            "chain_id": self.chain_id,
            "client": self.w3.client_version if self.network.rpc_url else "embedded EVM (EthereumTesterProvider)",
            "connected": self.w3.is_connected(),
            "block": self.w3.eth.block_number,
            "deployed": self.deployment is not None,
            "gas_price_wei": int(self.w3.eth.gas_price) if self.w3.is_connected() else 0,
        }

    # ---------------------------------------------------------------- deploy
    def deploy(self, plan_prices_eth: list[float] | None = None) -> Deployment:
        if self.deployment is not None:
            return self.deployment

        acct = self._admin_account()
        token_art = _load_artifact("KarmaToken")
        treas_art = _load_artifact("KarmaTreasury")
        sub_art = _load_artifact("KarmaSubscription")
        deeds_art = _load_artifact("GoodDeedRegistry")

        token = self._deploy(token_art, acct, [])
        treas = self._deploy(treas_art, acct, [acct.address])
        sub = self._deploy(sub_art, acct, [treas.address, acct.address, acct.address])
        deeds = self._deploy(deeds_art, acct, [token.address, acct.address])

        # wire roles: registry may mint KARMA; keepers may automate treasury
        self._tx(token, "grantRole", [Web3.keccak(text="MINTER_ROLE"), deeds.address], acct)
        self._tx(treas, "grantAutomator", [acct.address], acct)
        self._tx(treas, "setRevenueFeeBps", [TREASURY_FEE_BPS], acct)

        dep = Deployment(
            network=self.network.id,
            chain_id=self.chain_id,
            karma_token=token.address,
            treasury=treas.address,
            subscription=sub.address,
            good_deeds=deeds.address,
            protocol_wallet=acct.address,
            deployed_at=time.time(),
        )
        self.deployment = dep
        self._save_deployment(dep)

        # create the default Ultimate Pays plans on-chain
        prices = plan_prices_eth or [p["price_eth"] for p in DEFAULT_PLANS]
        sub_contract = self._contract("KarmaSubscription", sub.address)
        for i, price_eth in enumerate(prices):
            price_wei = Web3.to_wei(price_eth, "ether")
            days = DEFAULT_PLANS[i]["duration_days"] if i < len(DEFAULT_PLANS) else 30
            self._tx(sub_contract, "createPlan", [price_wei, days * 86400], acct)

        # ---- economy layer: MA token, pegged BTC/USDT, swap router, mining rig
        ma_art = _load_artifact("MAToken")
        peg_art = _load_artifact("PeggedToken")
        swap_art = _load_artifact("KarmaSwap")
        rig_art = _load_artifact("MiningRig")

        ma_token = self._deploy(ma_art, acct, [])
        wusdt = self._deploy(peg_art, acct, ["Wrapped USDT", "USDT"])
        wbtc = self._deploy(peg_art, acct, ["Wrapped Bitcoin", "BTC"])

        # swap rates: 1 MA -> 0.00001 ETH | 0.0001 USDT | 0.00000005 BTC
        rate_eth = 10_000_000_000_000        # wei
        rate_usdt = 100_000_000_000_000      # 1e18 units
        rate_btc = 50_000_000_000            # 1e18 units
        swap = self._deploy(swap_art, acct,
                            [ma_token.address, wusdt.address, wbtc.address,
                             rate_eth, rate_usdt, rate_btc, acct.address])
        rig = self._deploy(rig_art, acct, [ma_token.address, acct.address])

        # role wiring: bridge + mining may mint MA; keeper may batch-mine
        minter = Web3.keccak(text="MINTER_ROLE")
        keeper = Web3.keccak(text="KEEPER_ROLE")
        self._tx(ma_token, "grantRole", [minter, acct.address], acct)
        self._tx(ma_token, "grantRole", [minter, rig.address], acct)
        self._tx(rig, "grantRole", [keeper, acct.address], acct)

        # seed the swap pools from the treasury/admin (liquidity automation)
        peg_minter = Web3.keccak(text="MINTER_ROLE")
        self._tx(wusdt, "grantRole", [peg_minter, acct.address], acct)
        self._tx(wbtc, "grantRole", [peg_minter, acct.address], acct)
        self._tx(wusdt, "mint", [acct.address, Web3.to_wei(100, "ether")], acct)   # 100 USDT
        self._tx(wbtc, "mint", [acct.address, Web3.to_wei(0.02, "ether")], acct)   # 0.02 BTC
        self._tx(wusdt, "approve", [swap.address, Web3.to_wei(100, "ether")], acct)
        self._tx(wbtc, "approve", [swap.address, Web3.to_wei(0.02, "ether")], acct)
        swap_c = self._contract("KarmaSwap", swap.address)
        self._tx(swap_c, "refill", [Web3.to_wei(0.5, "ether"), Web3.to_wei(100, "ether"),
                                    Web3.to_wei(0.02, "ether")], acct, value_wei=Web3.to_wei(0.5, "ether"))

        dep.ma_token = ma_token.address
        dep.wusdt = wusdt.address
        dep.wbtc = wbtc.address
        dep.swap = swap.address
        dep.mining_rig = rig.address
        self._save_deployment(dep)
        return dep

    # Ganache/hardhat dev mnemonic account 0 (localnode only, dev key).
    LOCALNODE_DEV_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

    def _admin_account(self) -> Account:
        if self.network.id == "localnode":
            return Account.from_key(self.LOCALNODE_DEV_KEY)
        if self.network.rpc_url is None:
            # Embedded EVM: create a fresh, known deployer key, register it with
            # the tester and fund it from the genesis account.
            if self._local_admin is None:
                tester = self.w3.provider.ethereum_tester  # type: ignore[attr-defined]
                key = os.urandom(32)
                tester.add_account(key.hex())  # eth-tester expects hex text
                acct = Account.from_key(key)
                genesis = self.w3.eth.accounts[0]
                self.w3.eth.send_transaction({
                    "from": genesis,
                    "to": acct.address,
                    "value": Web3.to_wei(500, "ether"),
                })
                self._local_admin = acct
            return self._local_admin
        key = os.environ.get("KARMA_DEPLOYER_KEY")
        if not key:
            raise RuntimeError(
                "remote chain requires KARMA_DEPLOYER_KEY in environment "
                "(private key of the deploying wallet)"
            )
        return Account.from_key(key)

    def _contract(self, name: str, address: str):
        art = _load_artifact(name)
        return self.w3.eth.contract(address=Web3.to_checksum_address(address), abi=art["abi"])

    def _deploy(self, artifact: dict, acct: Account, args: list) -> object:
        Contract = self.w3.eth.contract(abi=artifact["abi"], bytecode="0x" + artifact["bytecode"])
        tx = Contract.constructor(*args).build_transaction({"from": acct.address})
        receipt = self._send_signed(tx, acct)
        return self.w3.eth.contract(
            address=receipt.contractAddress, abi=artifact["abi"]
        )

    def _send_signed(self, tx: dict, acct: Account, value_wei: int = 0):
        tx = dict(tx)
        tx["from"] = acct.address
        if value_wei:
            tx["value"] = value_wei
        # Some providers (eth-tester) omit nonce during fill defaults.
        tx.setdefault("nonce", self.w3.eth.get_transaction_count(acct.address))
        signed = self.w3.eth.account.sign_transaction(tx, acct.key)
        h = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        return self.w3.eth.wait_for_transaction_receipt(h)

    def _tx(self, contract, fn: str, args: list, acct: Account, value_wei: int = 0):
        tx_in = {"from": acct.address}
        if value_wei:
            tx_in["value"] = value_wei  # needed for gas estimation of payable calls
        built = getattr(contract.functions, fn)(*args).build_transaction(tx_in)
        return self._send_signed(built, acct, value_wei)

    # ----------------------------------------------------------------- plans
    def _plan_ids(self) -> list[int]:
        sub = self._contract("KarmaSubscription", self.deployment.subscription)
        n = sub.functions.planCount().call()
        return list(range(n))

    def list_plans(self) -> list[dict]:
        sub = self._contract("KarmaSubscription", self.deployment.subscription)
        out = []
        for i in self._plan_ids():
            p = sub.functions.plans(i).call()
            out.append({
                "id": i,
                "name": DEFAULT_PLANS[i]["name"] if i < len(DEFAULT_PLANS) else f"Plan {i}",
                "price_eth": float(Web3.from_wei(p[0], "ether")),
                "duration_days": p[1] // 86400,
                "active": p[2],
            })
        return out

    # ------------------------------------------------------------ subscribers
    def register_subscriber(self, name: str, email: str, plan_id: int, password: str,
                            vault: Vault) -> dict:
        wallet = create_wallet(password, name)
        sub_id = "sub_" + uuid.uuid4().hex[:12]
        record = VaultRecord(
            subscriber_id=sub_id,
            name=name,
            email=email,
            plan_id=plan_id,
            address=wallet.address,
            keystore=wallet.keystore,
            created_at=time.time(),
        )
        vault.upsert(record)
        # fund the new wallet so it can pay gas + plan price (local chains only)
        if self.network.faucet:
            self._faucet(wallet.address)
        return {
            "subscriber_id": sub_id,
            "address": wallet.address,
            "plan_id": plan_id,
            "private_key_kept_in_memory_only": True,
            "keystore_encrypted": True,
            "vault_document": vault.path,
        }

    def _faucet(self, address: str, amount_eth: float = 1.0) -> str:
        """Local chains only: fund a wallet from the deployer faucet."""
        if not self.network.faucet:
            raise RuntimeError("faucet is only available on local networks")
        acct = self._admin_account()
        tx = {
            "from": acct.address,
            "to": Web3.to_checksum_address(address),
            "value": Web3.to_wei(amount_eth, "ether"),
        }
        h = self.w3.eth.send_transaction(tx)
        return self._hx(self.w3.eth.wait_for_transaction_receipt(h).transactionHash)

    # ----------------------------------------------------------- payments
    def subscribe(self, subscriber_id: str, vault: Vault, plan_id: int | None = None,
                  password: str | None = None) -> dict:
        rec = self._require_record(vault, subscriber_id)
        plan_id = plan_id if plan_id is not None else rec.plan_id
        plans = self.list_plans()
        plan = next((p for p in plans if p["id"] == plan_id), None)
        if plan is None:
            raise ValueError(f"no such plan {plan_id}")
        key = Account.decrypt(rec.keystore, password) if password else self._remembered_key(subscriber_id, rec)
        acct = Account.from_key(key)
        sub = self._contract("KarmaSubscription", self.deployment.subscription)
        price_wei = Web3.to_wei(float(plan["price_eth"]), "ether")
        # balance check
        bal = self.w3.eth.get_balance(acct.address)
        if bal < price_wei:
            raise RuntimeError(
                f"wallet {acct.address} has {float(Web3.from_wei(bal, 'ether'))} {self.network.currency}; "
                f"needs {plan['price_eth']} to subscribe — fund it first (local chain auto-funds on register)"
            )
        receipt = self._tx(sub, "subscribe", [plan_id], acct, value_wei=price_wei)
        event = sub.events.Subscribed().process_receipt(receipt)[0]
        args = dict(event["args"])
        rec.active_until = args["activeUntilTimestamp"]
        rec.plan_id = plan_id
        vault.upsert(rec)
        return {
            "subscriber_id": subscriber_id,
            "plan": plan["name"],
            "amount_eth": plan["price_eth"],
            "fee_eth": float(Web3.from_wei(args["feeWei"], "ether")),
            "active_until": args["activeUntilTimestamp"],
            "tx_hash": self._hx(receipt.transactionHash),
            "explorer": (self.network.block_explorer or "") + self._hx(receipt.transactionHash),
        }

    # ------------------------------------------------------------ good deeds
    def good_deed(self, subscriber_id: str, vault: Vault, service: str, category: str,
                  impact: int, beneficiary: str, password: str | None = None) -> dict:
        rec = self._require_record(vault, subscriber_id)
        key = Account.decrypt(rec.keystore, password) if password else self._remembered_key(subscriber_id, rec)
        acct = Account.from_key(key)
        deeds = self._contract("GoodDeedRegistry", self.deployment.good_deeds)
        receipt = self._tx(deeds, "registerGoodDeed",
                           [Web3.to_checksum_address(beneficiary), service, category, impact], acct)
        ev = deeds.events.DeedRegistered().process_receipt(receipt)[0]
        args = dict(ev["args"])
        rec.deeds += 1
        vault.upsert(rec)
        return {
            "deed_id": args["deedId"],
            "doer": args["doer"],
            "beneficiary": args["beneficiary"],
            "service": args["service"],
            "impact": args["impactScore"],
            "karma_reward": float(Web3.from_wei(args["karmaReward"], "ether")),
            "tx_hash": self._hx(receipt.transactionHash),
            "explorer": (self.network.block_explorer or "") + self._hx(receipt.transactionHash),
        }

    def _remembered_key(self, subscriber_id: str, rec: VaultRecord) -> bytes | None:
        """Session key cache (memory only). Falls back to requiring password."""
        key = self.state.setdefault("_session_keys", {}).get(subscriber_id)
        return bytes.fromhex(key) if key else None

    def remember_key(self, subscriber_id: str, password: str, vault: Vault) -> None:
        rec = self._require_record(vault, subscriber_id)
        key = Account.decrypt(rec.keystore, password)
        self.state.setdefault("_session_keys", {})[subscriber_id] = key.hex()
        self._save_state()

    # ----------------------------------------------------------------- wallet
    def wallet_info(self, subscriber_id: str, vault: Vault) -> dict:
        rec = self._require_record(vault, subscriber_id)
        addr = Web3.to_checksum_address(rec.address)
        native = self.w3.eth.get_balance(addr)
        token = self._contract("KarmaToken", self.deployment.karma_token)
        karma = token.functions.balanceOf(addr).call()
        sub = self._contract("KarmaSubscription", self.deployment.subscription)
        active_until = sub.functions.getActiveUntil(addr).call()
        out = {
            "subscriber_id": rec.subscriber_id,
            "name": rec.name,
            "address": rec.address,
            f"native_{self.network.currency}": float(Web3.from_wei(native, "ether")),
            "karma_tokens": float(Web3.from_wei(karma, "ether")),
            "deeds": rec.deeds,
            "active_until": active_until,
            "active": active_until > time.time(),
        }
        if self.deployment.ma_token:
            ma = self._contract("MAToken", self.deployment.ma_token)
            out["ma_tokens"] = float(Web3.from_wei(ma.functions.balanceOf(addr).call(), "ether"))
        if self.deployment.wusdt:
            usdt = self._contract("PeggedToken", self.deployment.wusdt)
            out["usdt_pegged"] = float(Web3.from_wei(usdt.functions.balanceOf(addr).call(), "ether"))
        if self.deployment.wbtc:
            btc = self._contract("PeggedToken", self.deployment.wbtc)
            out["btc_pegged"] = float(Web3.from_wei(btc.functions.balanceOf(addr).call(), "ether"))
        if self.deployment.mining_rig:
            rig = self._contract("MiningRig", self.deployment.mining_rig)
            out["mined_total_ma"] = float(Web3.from_wei(rig.functions.totalMined().call(), "ether"))
        return out

    # ------------------------------------------------------------- economy
    def convert_karma_to_ma(self, subscriber_id: str, vault: Vault, karma_amount: float,
                            password: str | None = None) -> dict:
        """Karma Power -> MA tokens (1 KARMA = 10 MA). Real burn + mint txs."""
        rec = self._require_record(vault, subscriber_id)
        acct = Account.from_key(Account.decrypt(rec.keystore, password))
        addr = acct.address
        karma_wei = Web3.to_wei(karma_amount, "ether")
        token = self._contract("KarmaToken", self.deployment.karma_token)
        balance = token.functions.balanceOf(addr).call()
        if balance < karma_wei:
            raise RuntimeError(f"KARMA balance {float(Web3.from_wei(balance, 'ether'))} < {karma_amount}")
        r1 = self._tx(token, "burn", [karma_wei], acct)
        ma = self._contract("MAToken", self.deployment.ma_token)
        ma_amount_wei = karma_wei * 10
        admin = self._admin_account()
        r2 = self._tx(ma, "mint", [addr, ma_amount_wei], admin)
        return {
            "subscriber": rec.subscriber_id,
            "karma_burned": karma_amount,
            "ma_minted": karma_amount * 10,
            "burn_tx": self._hx(r1.transactionHash),
            "mint_tx": self._hx(r2.transactionHash),
        }

    def swap_ma(self, subscriber_id: str, vault: Vault, target: str, ma_amount: float,
                password: str | None = None) -> dict:
        """Swap MA -> ETH / USDT / BTC through KarmaSwap (real txs)."""
        target = target.lower()
        if target not in ("eth", "usdt", "btc"):
            raise ValueError("target must be eth | usdt | btc")
        rec = self._require_record(vault, subscriber_id)
        acct = Account.from_key(Account.decrypt(rec.keystore, password))
        addr = acct.address
        ma = self._contract("MAToken", self.deployment.ma_token)
        swap = self._contract("KarmaSwap", self.deployment.swap)
        amount_wei = Web3.to_wei(ma_amount, "ether")
        if ma.functions.balanceOf(addr).call() < amount_wei:
            raise RuntimeError("not enough MA - convert karma or mine first")
        r1 = self._tx(ma, "approve", [swap.address, amount_wei], acct)
        fn = {"eth": "swapMaToEth", "usdt": "swapMaToUsdt", "btc": "swapMaToBtc"}[target]
        r2 = self._tx(swap, fn, [amount_wei], acct)
        swap_contract = self._contract("KarmaSwap", self.deployment.swap)
        ev = getattr(swap_contract.events, f"SwappedTo{target.capitalize()}").process_receipt(r2)[0]
        out_amount = float(Web3.from_wei(dict(ev["args"])[f"{target}Out"], "ether"))
        return {
            "subscriber": rec.subscriber_id,
            "ma_in": ma_amount,
            f"{target}_out": out_amount,
            "approve_tx": self._hx(r1.transactionHash),
            "swap_tx": self._hx(r2.transactionHash),
            "explorer": (self.network.block_explorer or "") + self._hx(r2.transactionHash),
        }

    def mine(self, subscriber_id: str, vault: Vault, password: str | None = None) -> dict:
        """Mine crypto: real MiningRig tx, MA minted to the subscriber wallet."""
        rec = self._require_record(vault, subscriber_id)
        acct = Account.from_key(Account.decrypt(rec.keystore, password))
        rig = self._contract("MiningRig", self.deployment.mining_rig)
        r = self._tx(rig, "mine", [], acct)
        ev = rig.events.Mined().process_receipt(r)[0]
        reward = float(Web3.from_wei(dict(ev["args"])["reward"], "ether"))
        return {
            "subscriber": rec.subscriber_id,
            "reward_ma": reward,
            "block": r.blockNumber,
            "tx_hash": self._hx(r.transactionHash),
            "explorer": (self.network.block_explorer or "") + self._hx(r.transactionHash),
        }

    def mine_all(self, vault: Vault) -> dict:
        """Keeper automation: batch-mine for every subscriber in one tx."""
        rig = self._contract("MiningRig", self.deployment.mining_rig)
        addrs = [Web3.to_checksum_address(r.address) for r in vault.list()]
        if not addrs:
            return {"mined": 0, "note": "no subscribers in vault"}
        admin = self._admin_account()
        r = self._tx(rig, "mineBatch", [addrs], admin)
        return {
            "miners": len(addrs),
            "tx_hash": self._hx(r.transactionHash),
            "block": r.blockNumber,
        }

    def sweep(self, subscriber_id: str, vault: Vault, to_address: str,
              token: str = "ma", password: str | None = None) -> dict:
        """Transfer earnings to any external wallet (e.g. your MetaMask)."""
        token = token.lower()
        rec = self._require_record(vault, subscriber_id)
        acct = Account.from_key(Account.decrypt(rec.keystore, password))
        to = Web3.to_checksum_address(to_address)
        if token == "ma":
            ma = self._contract("MAToken", self.deployment.ma_token)
            rig = self._contract("MiningRig", self.deployment.mining_rig)
            bal = ma.functions.balanceOf(acct.address).call()
            if bal <= 0:
                raise RuntimeError("no MA balance to sweep")
            r0 = self._tx(ma, "approve", [rig.address, bal], acct)
            r = self._tx(rig, "sweep", [to], acct)
            ev = rig.events.Swept().process_receipt(r)[0]
            amount = float(Web3.from_wei(dict(ev["args"])["amount"], "ether"))
            symbol = "MA"
        elif token == "karma":
            k = self._contract("KarmaToken", self.deployment.karma_token)
            bal = k.functions.balanceOf(acct.address).call()
            r = self._tx(k, "transfer", [to, bal], acct)
            amount = float(Web3.from_wei(bal, "ether"))
            symbol = "KARMA"
        elif token in ("eth", "native"):
            bal = self.w3.eth.get_balance(acct.address)
            gas = self.w3.eth.gas_price * 21000
            value = bal - gas
            if value <= 0:
                raise RuntimeError("no spendable ETH balance")
            tx = {"from": acct.address, "to": to, "value": value}
            r = self._send_signed(tx, acct)
            amount = float(Web3.from_wei(value, "ether"))
            symbol = self.network.currency
        else:
            raise ValueError("token must be ma | karma | eth")
        out = {
            "subscriber": rec.subscriber_id,
            "to": to_address,
            f"{symbol}_sent": amount,
            "tx_hash": self._hx(r.transactionHash),
            "explorer": (self.network.block_explorer or "") + self._hx(r.transactionHash),
        }
        if token == "ma":
            out["approve_tx"] = self._hx(r0.transactionHash)
        return out

    def tokenomics(self) -> dict:
        """MA tokenomics snapshot: supply, allocations, swap rates, pools."""
        ma = self._contract("MAToken", self.deployment.ma_token)
        swap = self._contract("KarmaSwap", self.deployment.swap)
        rig = self._contract("MiningRig", self.deployment.mining_rig)
        total = ma.functions.totalSupply().call()
        return {
            "token": "MA",
            "total_supply": float(Web3.from_wei(total, "ether")),
            "hard_cap": 1_000_000_000.0,
            "allocations": {
                "mining_rewards_40pct": 400_000_000.0,
                "karma_good_deeds_25pct": 250_000_000.0,
                "treasury_reserve_20pct": 200_000_000.0,
                "team_partners_10pct": 100_000_000.0,
                "ecosystem_reserve_5pct": 50_000_000.0,
            },
            "swap_rates": {
                "eth_per_ma": float(Web3.from_wei(swap.functions.rateEthPerMa().call(), "ether")),
                "usdt_per_ma": float(Web3.from_wei(swap.functions.rateUsdtPerMa().call(), "ether")),
                "btc_per_ma": float(Web3.from_wei(swap.functions.rateBtcPerMa().call(), "ether")),
            },
            "swap_totals": {
                "ma_burned": float(Web3.from_wei(swap.functions.totalMaBurned().call(), "ether")),
                "to_eth": float(Web3.from_wei(swap.functions.totalSwappedToEth().call(), "ether")),
                "to_usdt": float(Web3.from_wei(swap.functions.totalSwappedToUsdt().call(), "ether")),
                "to_btc": float(Web3.from_wei(swap.functions.totalSwappedToBtc().call(), "ether")),
            },
            "mining": {
                "reward_per_mine_ma": float(Web3.from_wei(rig.functions.rewardPerMine().call(), "ether")),
                "cooldown_seconds": rig.functions.cooldownSeconds().call(),
                "total_mined_ma": float(Web3.from_wei(rig.functions.totalMined().call(), "ether")),
                "mine_count": rig.functions.mineCount().call(),
            },
            "pool_balances": {
                "eth_pool": float(Web3.from_wei(self.w3.eth.get_balance(swap.address), "ether")),
                "usdt_pool": float(Web3.from_wei(
                    self._contract("PeggedToken", self.deployment.wusdt).functions.balanceOf(swap.address).call(), "ether")),
                "btc_pool": float(Web3.from_wei(
                    self._contract("PeggedToken", self.deployment.wbtc).functions.balanceOf(swap.address).call(), "ether")),
            },
        }

    # --------------------------------------------------------------- treasury
    def treasury_info(self) -> dict:
        treas = self._contract("KarmaTreasury", self.deployment.treasury)
        sub = self._contract("KarmaSubscription", self.deployment.subscription)
        balance = self.w3.eth.get_balance(Web3.to_checksum_address(self.deployment.treasury))
        return {
            "treasury_address": self.deployment.treasury,
            "balance_eth": float(Web3.from_wei(balance, "ether")),
            "revenue_fee_bps": treas.functions.revenueFeeBps().call(),
            "total_collected_eth": float(Web3.from_wei(treas.functions.totalCollected().call(), "ether")),
            "total_distributed_eth": float(Web3.from_wei(treas.functions.totalDistributed().call(), "ether")),
            "total_subscriptions": sub.functions.totalSubscriptions().call(),
            "total_revenue_eth": float(Web3.from_wei(sub.functions.totalRevenueWei().call(), "ether")),
            "total_fees_eth": float(Web3.from_wei(sub.functions.totalFeesCollectedWei().call(), "ether")),
        }

    def register_agent(self, agent_name: str, address: str, weight: int = 1) -> dict:
        self.state["agents"][agent_name] = Web3.to_checksum_address(address)
        self.state["agent_weights"][agent_name] = max(1, weight)
        self._save_state()
        return {"agent": agent_name, "address": address, "weight": weight}

    def distribute_to_agents(self, split_pct: int = 100) -> dict:
        """Keeper automation: pay registered coding agents from treasury."""
        if not self.state["agents"]:
            raise RuntimeError("no agents registered — use register-agent first")
        treas = self._contract("KarmaTreasury", self.deployment.treasury)
        balance = self.w3.eth.get_balance(Web3.to_checksum_address(self.deployment.treasury))
        if balance == 0:
            return {"distributed": 0, "note": "treasury empty — nothing to distribute"}
        pool = balance * min(100, split_pct) // 100
        agents = list(self.state["agents"].items())
        weights = [self.state["agent_weights"][n] for n, _ in agents]
        total_w = sum(weights)
        addresses = [a for _, a in agents]
        amounts = [pool * w // total_w for w in weights]
        # leave dust in treasury
        amounts[-1] += pool - sum(amounts)
        acct = self._admin_account()
        receipt = self._tx(treas, "automatePayout", [addresses, amounts], acct)
        payout_id = treas.events.Payout().process_receipt(receipt)[0]["args"]["payoutId"]
        return {
            "distributed_eth": float(Web3.from_wei(pool, "ether")),
            "to": [f"{n} -> {float(Web3.from_wei(a, 'ether'))} ETH" for n, a in zip(agents, amounts)],
            "payout_id_hex": payout_id.hex(),
            "tx_hash": self._hx(receipt.transactionHash),
            "explorer": (self.network.block_explorer or "") + self._hx(receipt.transactionHash),
        }

    # ----------------------------------------------------------------- keeper
    def auto_renew(self, vault: Vault, password: str | None = None) -> list[dict]:
        """Automation loop: renew every expired-but-enrolled subscription."""
        if not self.state.get("autorenew", True):
            return [{"note": "auto-renew disabled in state"}]
        renewed = []
        for rec in vault.list():
            if rec.active_until and rec.active_until < time.time():
                try:
                    r = self.subscribe(rec.subscriber_id, vault, password=password)
                    renewed.append({"subscriber_id": rec.subscriber_id, **r})
                except Exception as e:  # noqa: BLE001
                    renewed.append({"subscriber_id": rec.subscriber_id, "error": str(e)})
        return renewed

    # --------------------------------------------------------------- verify
    def verify_tx(self, tx_hash: str) -> dict:
        tx_hash = self._hx(tx_hash)
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        except TransactionNotFound:
            return {"tx_hash": tx_hash, "found": False}
        tx = self.w3.eth.get_transaction(tx_hash)
        return {
            "tx_hash": tx_hash,
            "found": True,
            "status": "SUCCESS" if receipt.status == 1 else "FAILED",
            "block": receipt.blockNumber,
            "from": tx["from"],
            "to": tx["to"],
            "value_eth": float(Web3.from_wei(tx["value"], "ether")),
            "gas_used": receipt.gasUsed,
            "logs": len(receipt.logs),
            "explorer": (self.network.block_explorer or "") + tx_hash,
        }

    # --------------------------------------------------------------- helpers
    def _require_record(self, vault: Vault, subscriber_id: str) -> VaultRecord:
        rec = vault.get(subscriber_id)
        if rec is None:
            raise KeyError(f"no subscriber {subscriber_id} in vault")
        return rec

    def open_vault(self, password: str) -> Vault:
        return Vault.open_or_create(os.path.join(self.data_dir, "vault.karma"), password)
