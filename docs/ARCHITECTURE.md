# Karma Ecosystem — System Architecture

```
                        ┌─────────────────────────────────────────────┐
                        │   karma-eco CLI  (click)                     │
                        │   init · status · register · subscribe ·    │
                        │   deed · convert · swap · mine · sweep ·    │
                        │   treasury · tokenomics · verify · bot ·    │
                        │   keeper · export                            │
                        └───────────────┬─────────────────────────────┘
                                        │
                                        ▼
                    ┌─────────────────────────────────────────────┐
                    │  KarmaEcosystemEngine (automation core)      │
                    │  wallet · vault · chain · keeper · swap      │
                    └───────┬─────────────────────┬───────────────┘
                            │                     │
              ┌─────────────▼───────────┐   ┌─────▼──────────────────┐
              │  Web3 (real RPC)        │   │  BotRevenueAutomation  │
              │  Embedded EVM (local)   │   │  task DAG · A-Z phases │
              │  Sepolia / Amoy (RPC)   │   │  release · offerings   │
              └─────────────┬───────────┘   └─────┬──────────────────┘
                            │                     │
                            ▼                     ▼
┌────────────────────────────────────────┐   ┌──────────────────────────┐
│  ON-CHAIN (Solidity 0.8, OZ 5)         │   │  PRIVATE STORAGE          │
│  KarmaToken   — KARMA rewards          │   │  data/vault.karma         │
│  MAToken      — MA token (1B cap)      │   │   AES-256-GCM + scrypt    │
│  GoodDeedRegistry — deeds -> KARMA     │   │   + SHA-256 tamper digest │
│  KarmaSubscription — plans + fee split │   │  data/deployment.json     │
│  KarmaTreasury — fees + agent payouts  │   │  data/state.json          │
│  KarmaSwap     — MA -> ETH/USDT/BTC    │   │  data/automation/*        │
│  MiningRig     — mining + sweep        │   │   offerings/version/logs  │
│  PeggedToken   — wUSDT / wBTC (demo)   │   └──────────────────────────┘
└────────────────────────────────────────┘
```

## Flow: reward → swap → payout

1. **Good deed / service** → `GoodDeedRegistry.registerGoodDeed` mints KARMA
   to the doer (real tx, hash H1).
2. **Convert** KARMA → MA 1:10 (burn H2 + mint H3).
3. **Mine** → `MiningRig.mine` / `mineBatch` mints MA (H4).
4. **Swap** MA → ETH/USDT/BTC via `KarmaSwap` (approve H5 + swap H6, MA
   burned, payout from treasury-funded pools).
5. **Sweep** earnings to any wallet / MetaMask (H7).
6. **Subscriptions** → payment splits 20% treasury / 80% protocol (H8), then
   `KarmaTreasury.automatePayout` pays coding agents (H9) — all hashes
   verifiable with `karma-eco verify`.

## Bot Revenue Automation (A-Z workflow)

The `bot` command runs a dependency-ordered task DAG across 26 phases
(ALPHA..OMEGA): foundation → on-chain → tokenomics → mining → billing →
karma → sales → catalog → payouts → cloud → telemetry → wallets → security →
compliance → governance → community → relay → **self-release** → backup →
testing → monitoring → transparency → risk → bridges → scale → equilibrium.

Every run appends `execution_log.json`; every `bot release` bumps the version,
refreshes the products & services offering manifest and appends `CHANGELOG.md`.

## Security model

- Keys: per-subscriber Web3 JSON keystores (AES-128-CTR) inside the
  AES-256-GCM vault envelope; scrypt master key derivation.
- Tamper detection: vault SHA-256 digest compared on open.
- Roles: `MINTER_ROLE` / `KEEPER_ROLE` / `FILLER_ROLE` / `AUTOMATOR_ROLE`
  restrict minting, mining and payouts on-chain.
- Compliance: see [LEGAL_NEXUS.md](LEGAL_NEXUS.md).

## Layout

```
karma_ecosystem/
  contracts/*.sol          # Solidity contracts + compile.js + build/*.json
  engine.py                # chain-agnostic automation engine
  automation.py            # bot revenue automation workflow engine
  vault.py                 # AES-256-GCM encrypted private document
  wallet.py                # Web3 keystore creation
  networks.py              # local / sepolia / polygon_amoy presets
  cli.py                   # karma-eco command line
  data/                    # runtime state (gitignored)
docs/                      # architecture, tokenomics, legal nexus, 1000 TODOs
scripts/generate_1000_todos.py
```
