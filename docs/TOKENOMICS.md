# MA Token — Tokenomics (Karma Ecosystem)

**MA** is the gamified karma token of the Karma Ecosystem, live **on-chain**
(embedded EVM sandbox by default; Sepolia / Polygon Amoy testnets optional).
Every mint, burn, swap and transfer is a **real blockchain transaction with a
real hash**.

> ⚠️ In the default sandbox this is a **synthetic demonstration** of tokenomics
> and cryptography — no fiat or real-crypto value is created. On public
> testnets the same contracts run against real networks (testnet tokens only).

## Supply schedule

| Allocation | % | MA | Minter |
|---|---|---|---|
| Mining rewards | 40% | 400,000,000 | `MiningRig` |
| Karma good-deed rewards | 25% | 250,000,000 | `GoodDeedRegistry` bridge |
| Treasury reserve (liquidity/payouts) | 20% | 200,000,000 | Treasury admin |
| Team & partners (24-mo vesting) | 10% | 100,000,000 | Preminted at deploy |
| Ecosystem reserve (grants/bounties) | 5% | 50,000,000 | Governance |

- **Hard cap:** 1,000,000,000 MA — enforced in `MAToken.mint` (`HARD_CAP`).
- **Emission:** minted only by role-gated contracts; burning on swap keeps
  circulating supply deflationary.

## Earning MA

1. **Good deed / service** → on-chain `GoodDeedRegistry.registerGoodDeed`
   mints KARMA (10 × impact score) to the doer — real tx.
2. **Convert** KARMA → MA at **1 : 10** (burn KARMA + mint MA, two real txs).
3. **Mine** via `MiningRig.mine()` — 100 MA per mine (cooldown 60s), real tx
   per block; `mineBatch` mines every subscriber in **one** transaction.

## Swapping into crypto (ETH / USDT / BTC)

`KarmaSwap` swaps MA for crypto at fixed rates (treasury-administered):

| Asset | Rate (MA → asset) | Example |
|---|---|---|
| ETH (native) | 1 MA = 0.00001 ETH | 100,000 MA = 1 ETH |
| USDT (pegged ERC-20) | 1 MA = 0.0001 USDT | 10,000 MA = 1 USDT |
| BTC (pegged ERC-20) | 1 MA = 0.00000005 BTC | 20,000,000 MA = 1 BTC |

- Swaps **burn** the MA and pay out from treasury-funded pools (seeded at
  deploy: 0.5 ETH / 100 USDT / 0.02 BTC; `refill()` refills them).
- Every swap = 2 real transactions (approve + swap) with explorer links.
- On a production chain the pegged assets are replaced by the **real**
  wrapped assets (WETH, USDT, WBTC) — the contract interface is identical.

## Revenue automation fee

Every subscription payment is split **on-chain** inside
`KarmaSubscription.subscribe`:

- **20% → KarmaTreasury** (automation revenue fee, `revenueFeeBps` = 2000)
- **80% → protocol wallet**
- Treasury then **automatically pays coding agents / app builders**
  (`KarmaTreasury.automatePayout`, keeper role) — payouts are hashed and
  logged on-chain.

## Withdrawal to your own wallet (MetaMask)

`karma-eco sweep <subscriber> --to <0x...> --token ma|karma|eth` sends the
subscriber's balance to **any wallet address** (e.g. your MetaMask) as a real
transfer transaction with hash + explorer link. The subscriber's private key
is held encrypted in a Web3 JSON keystore + the AES-256-GCM private vault —
never in plaintext.

## Verification

`karma-eco tokenomics` prints the live snapshot: total supply, allocations,
swap rates & totals, mining stats, pool balances.
