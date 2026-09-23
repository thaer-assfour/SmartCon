# Case Study: Hundred Finance — Empty-Market Exchange-Rate Inflation and Redeem Rounding

## Summary
- **Protocol:** Hundred Finance (Compound v2 fork)
- **Date:** 2023-04-15
- **Chain:** Optimism
- **Loss:** ~$7M
- **Vulnerability class:** [Arithmetic & Precision](../vulnerabilities/arithmetic-and-precision.md)
- **Checklist categories:** arithmetic-and-precision, defi-logic
- **Checklist items:** SC-MATH-3, SC-MATH-4, SC-MATH-7, SOL-Basics-Math-5, SOL-Defi-General-4, SOL-Heuristics-10
- **Root cause in one sentence:** an empty cToken market let the attacker shrink `totalSupply` to 2 wei, donate underlying to inflate the exchange rate to an enormous value, borrow against that inflated collateral, and then exploit `redeemUnderlying`'s round-down of burned shares to reclaim the donation, so the borrow was effectively free.
- **Attack tx:** https://optimistic.etherscan.io/tx/0x6e9ebcdebbabda04fa9f2e3bc21ea8b2e4fb4bf4f4670cb8483e2f0b2604f451
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/HundredFinance_2_exp.sol

## Background
Hundred Finance is a Compound v2 fork. Each market is a cToken (here `hWBTC`, `hUSDC`, etc.). The
exchange rate that converts cTokens to underlying is, from `CToken.exchangeRateStoredInternal`:

```solidity
if (_totalSupply == 0) return initialExchangeRateMantissa;
uint cashPlusBorrowsMinusReserves = totalCash + totalBorrows - totalReserves;
uint exchangeRate = cashPlusBorrowsMinusReserves * expScale / _totalSupply;   // cash / supply
```

The intended invariant is that a cToken's value tracks the pool's assets proportionally. Compound
avoids the edge cases below in practice because its markets are seeded and never drained to near-zero
supply. Hundred's `hWBTC` market on Optimism was effectively empty, which re-opened both edges:
`exchangeRate = cash / totalSupply` is manipulable when `totalSupply` is tiny, and `redeemUnderlying`
rounds the burned share count down.

## The vulnerability
Two arithmetic facts combine. First, with a tiny `totalSupply`, a direct token transfer ("donation")
into the market inflates `totalCash`, so `exchangeRate = cash / totalSupply` explodes: a few wei of
supply backing a large cash balance means each cToken is "worth" a huge amount of underlying, and
therefore a huge amount of borrowing power. Second, `redeemFresh` computes burned shares by dividing,
which truncates toward zero (`CToken.redeemFresh`, simplified):

```solidity
if (redeemTokensIn > 0) {                       // redeem(shares)
    redeemTokens  = redeemTokensIn;
    redeemAmount  = mul_ScalarTruncate(exchangeRate, redeemTokensIn);
} else {                                         // redeemUnderlying(amount)
    redeemTokens  = div_(redeemAmountIn, exchangeRate);   // <-- rounds DOWN
    redeemAmount  = redeemAmountIn;
}
```

When `exchangeRate` is enormous, `redeemAmountIn / exchangeRate` rounds down so far that the attacker
withdraws nearly all donated underlying while burning almost no shares, keeping the inflated collateral
that backs an already-taken borrow.

## The exploit, step by step
The PoC deploys per-market CREATE2 "drain" contracts; each runs the same routine (values from the
PoC's own logs), funded by a 500 WBTC Aave v3 flash loan:

1. Into the empty `hWBTC` market, `mint(4 * 1e8)` (4 WBTC) to obtain shares.
2. `redeem(totalSupply - 2)`, leaving `totalSupply == 2` wei of hWBTC and a minimal WBTC balance in
   the market. The market is now at the fragile edge.
3. Transfer (donate) a large amount of WBTC directly to the `hWBTC` contract. `exchangeRate` jumps
   from its pre-manipulation value to an enormous one, because cash rose while supply stayed at 2 wei.
4. `enterMarkets([hWBTC])` and `borrow(getCash() - 1)` on a target market (ETH, SNX, USDC, DAI, USDT,
   sUSD, FRAX in turn). The inflated collateral value clears the borrow, and the borrowed tokens are
   sent to the exploiter.
5. `redeemUnderlying(donationAmount [- 1])`. Because `redeemTokens = redeemAmountIn / exchangeRate`
   rounds down, the attacker pulls back essentially the whole donation while burning a negligible
   number of shares, so the collateral backing step 4 is never really surrendered.
6. The parent contract `liquidateBorrow`s the drain contract's leftover position to seize the small
   hWBTC collateral and `redeem(1)` the remainder, cleaning up. Repeat per market; repay the flash loan.

## Why it worked
Compound v2's math is safe only under the operational assumption that markets carry meaningful,
non-manipulable supply. An empty market breaks that assumption: `exchangeRate = cash / totalSupply`
becomes an attacker-controlled dial, and the round-down in `redeemUnderlying` becomes a leak in the
attacker's favor. Neither piece is a "bug" in isolation, which is why the fork inherited them without
comment. A scanner sees standard, audited Compound code. Only reasoning about the `totalSupply -> 0`
boundary, and asking which way each division rounds and who benefits, reveals that a first/only
depositor can inflate the rate and farm the rounding. This is the same class that hit Sonne Finance
on 2024-05-14 (~$20M) and numerous other Compound forks.

## The fix
Never let a market's supply reach a manipulable floor, and neutralize donation inflation:

```solidity
// Seed each new market with a burned initial mint so totalSupply can never approach 0,
// and/or list markets with collateralFactor = 0 until liquidity is established.
// Track cash via internal accounting instead of raw balanceOf so a direct transfer
// (donation) cannot move the exchange rate.
```

The durable mitigations are: seed and burn an initial deposit at market creation (dead shares), keep
new markets at zero collateral factor until seeded, and use internal accounting rather than
`balanceOf` for cash so raw transfers cannot inflate the rate.

## Lessons for the checklist
- **SC-MATH-7** (empty-market / totalSupply-zero edge; Compound redeem rounding): directly asks what
  the exchange rate and rounding do when supply is 0 or tiny. That is the entire setup here.
- **SC-MATH-4** (first-depositor share inflation): the attacker is the only supplier and donates to
  inflate share value, the canonical inflation attack.
- **SC-MATH-3** (rounding direction, who profits, repeatable): `redeemUnderlying` rounds burned shares
  down in the redeemer's favor, and it is repeatable across every market.
- **SOL-Basics-Math-5** (rounding direction): the same question in Cyfrin's basics; the div in
  `redeemFresh` rounds toward the user.
- **SOL-Defi-General-4** (initial deposit issues): flags the un-seeded market as the enabling
  condition.
- **SOL-Heuristics-10** (rounding errors amplified): a per-call truncation, amplified by an inflated
  exchange rate, becomes a full drain rather than dust.
- **Proposed new question:** "For every cToken/vault market, is `totalSupply` prevented from reaching
  a tiny value (seeded dead shares, minimum liquidity) and is the exchange rate computed from internal
  accounting rather than `balanceOf`, so a donation cannot inflate it?"

## References
- Post-mortem: Hundred Finance hack post-mortem (blog.hundred.finance, 2023-04-15); analysis threads
  by PeckShield, danielvf, and Hexagate linked in the PoC header.
- Transaction(s): 0x6e9ebcdebbabda04fa9f2e3bc21ea8b2e4fb4bf4f4670cb8483e2f0b2604f451 (Optimism).
- Related audits / similar incidents: Sonne Finance 2024-05-14 (~$20M), same empty-market /
  donation-inflation class across many Compound v2 forks; also the ERC-4626 first-deposit family.
