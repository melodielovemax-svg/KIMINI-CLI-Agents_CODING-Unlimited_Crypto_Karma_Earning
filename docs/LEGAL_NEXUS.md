# LEGAL NEXUS — Total Protection & Compliance Framework

This document is the compliance backbone ("legal nexus") of the Karma
Ecosystem Bot Revenue Automation System. It protects operators, subscribers,
agents and the network.

## 1. Mode declaration (MANDATORY)

The system runs in two modes; every output must be labeled accordingly:

- **Local Simulation Mode (default):** all Karma points, MA balances, mining
  rewards, subscription revenue and swap amounts are **SYNTHETIC demo data**
  on an embedded EVM. No real money, cryptocurrency or financial value is
  created, transferred or stored. Nothing is withdrawable or exchangeable for
  real value.
- **Production Relay / Testnet Mode (opt-in):** requires real API keys and
  funded testnet wallets (`KARMA_DEPLOYER_KEY`). Transactions are real
  **testnet** transactions. Never point production contracts at real funds
  without legal + KYC/AML review.

## 2. No-securities, no-investment-advice clause

MA, KARMA and all ecosystem tokens are **utility/gamification tokens for
services and good deeds** — not securities. Nothing here is an offer of
securities, an investment contract, or financial advice. Token values are
arbitrary and set by the treasury for demonstration.

## 3. Privacy & data protection

- Subscriber account data ("full new information for subscribed plans") is
  stored **only inside the encrypted private vault document**
  (`data/vault.karma`, AES-256-GCM + scrypt KDF + SHA-256 tamper digest).
- Wallet private keys are never stored in plaintext: Web3 JSON keystores are
  individually password-encrypted, then wrapped inside the vault envelope.
- `karma-eco export` copies the encrypted document + integrity digest for
  offline custody. Treat the vault password as the sole secret.
- Apply GDPR/CCPA/Law-25 (Quebec) obligations in production: right to access,
  erasure, and data-processing agreements before storing any real PII.

## 4. KYC / AML / sanctions

In any real-money deployment:
- Gate subscriptions/withdrawals behind KYC (identity verification) and AML
  transaction monitoring; screen against sanctions lists.
- Keep an immutable audit trail of all transactions (the on-chain ledger
  provides this natively).
- The `N-NOVEMBER` phase of the automation bot runs these gates and logs the
  result in `execution_log.json` (see `karma-eco bot run`).

## 5. Treasury & governance

- Treasury revenue fees are enforced by the smart contract (`revenueFeeBps`,
  max 50%), not by manual accounting.
- Payouts to coding agents require the keeper role and are recorded with
  hashed payout ids on-chain.
- Governance changes (fee, rates, plans) are admin-gated; production should
  migrate to multi-sig + on-chain voting.

## 6. Disclaimers (ship these with any public build)

1. SYNTHETIC demo data — no real value.
2. Testnets only without legal review.
3. No securities, no guaranteed returns.
4. Crypto is volatile; use at your own risk.
5. Private keys are your responsibility; keep the vault password safe.
6. This software is provided "as is" without warranty of any kind.

## 7. Audit & transparency

- Every reward, payment, swap, mine and sweep is a **verifiable on-chain
  transaction** with a hash (see `karma-eco verify <txhash>`).
- The automation bot appends an audit log after every run
  (`data/automation/execution_log.json`) and a changelog entry on every
  release (`CHANGELOG.md`).

---
*This document is an operational compliance checklist, not legal advice.
Engage qualified counsel before any real-money deployment.*
