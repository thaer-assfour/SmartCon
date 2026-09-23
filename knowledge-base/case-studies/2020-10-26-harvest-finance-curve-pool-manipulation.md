# Case Study: Harvest Finance — Curve Y-Pool Share-Price Manipulation

## Summary
- **Protocol:** Harvest Finance fUSDC / fUSDT vaults
- **Date:** 2020-10-26
- **Chain:** Ethereum
- **Loss:** ~$33.8M drained from the fUSDC/fUSDT pools; the attacker returned ~$2.5M, leaving roughly $24M net taken (per The Block / Harvest post-mortem).
- **Vulnerability class:** [Oracle & Price Manipulation](../vulnerabilities/oracle-and-price-manipulation.md)
- **Checklist categories:** oracle-and-price-manipulation, flash-loans
- **Checklist items:** SC-ORACLE-1, SC-ORACLE-6, SC-FLASH-1, SOL-AM-PMA-2, SOL-Defi-FlashLoan-1
- **Root cause in one sentence:** Harvest priced vault shares from the Curve Y pool's instantaneous value (via `calc_withdraw_one_coin`/`get_virtual_price`-family accounting on live pool balances), so a flash-loan swap that skewed the pool let the attacker deposit at a deflated share price and, after reversing the skew, withdraw at an inflated one, repeated in a single block.
- **Attack tx:** https://etherscan.io/tx/0x35f8d2f572fceaac9288e5d462117850ef2694786992a8c3f6d02612277b0877
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2020-10/HarvestFinance_exp.sol

## Background
Harvest's stablecoin vaults deposit user funds into the Curve `yDAI+yUSDC+yUSDT+yTUSD`
("Y") pool via a strategy and mint vault shares (fUSDC, fUSDT). Shares are priced by
`getPricePerFullShare()`, which divides the vault's total invested underlying by total
supply. The invariant: a share must be worth the same underlying whether you are
depositing or withdrawing in the same block, so deposit/withdraw round-trips are not
profitable. That share value ultimately traces into the Curve Y pool's own pricing,
which is a function of the pool's current (manipulable) balances.

## The vulnerability
The vault's `_deposit` and `withdraw` both read `getPricePerFullShare()`:

```solidity
// Vault (deployed, simplified)
function getPricePerFullShare() public view returns (uint256) {
    return totalSupply() == 0 ? underlyingUnit()
        : underlyingUnit().mul(underlyingBalanceWithInvestment()).div(totalSupply());
}
// underlyingBalanceWithInvestment() -> strategy.investedUnderlyingBalance()
//   -> underlyingValueFromYCrv(...) -> PriceConvertor.yCrvToUnderlying(...)
//   -> Curve zap.calc_withdraw_one_coin(amount, i)   // live pool state
```

`investedUnderlyingBalance` values the strategy's Curve LP with
`calc_withdraw_one_coin` on the Y pool's deposit zap, a spot function of the pool's
coin balances, in the same family as `get_virtual_price`. Skew the pool and the share
price moves. The only same-block guard, the `defense` modifier, merely greylists
contract callers and is bypassed by calling from an EOA-shaped path; deposits and
withdrawals were allowed in the same block (`depositArbCheck` only tolerates a small
`arbTolerance`, which the attacker stayed within by reversing the skew before pricing).

## The exploit, step by step
1. Flash-loan ~50,000,000 USDC (and cascade ~17,300,000 USDT) from Uniswap pairs
   (`uniswapV2Call`).
2. `curveY.exchange_underlying(USDT -> USDC)` with a large amount, deflating USDC's
   effective price inside the Y pool and thus depressing Harvest's USDC share price.
3. `harvest.deposit(USDC)` at the depressed share price, minting more fUSDC than the
   USDC is really worth.
4. `curveY.exchange_underlying(USDC -> USDT)` to reverse the skew, restoring (and
   overshooting) the pool so the share price rises above where it was minted.
5. `harvest.withdraw(fUSDC)` at the inflated share price, redeeming more USDC than was
   deposited. The delta is profit.
6. Loop the deposit/withdraw cycle many times (roughly 17 iterations against the USDC
   vault, then the USDT vault) within a few minutes, then repay the flash loans.

## Why it worked
Share pricing was chained to a value an attacker can move atomically: the Curve Y
pool's instantaneous state. Because deposit and withdraw both read that same live
price *and both were permitted in one block*, the round-trip that should net zero
instead netted the manipulation gap each cycle. `depositArbCheck`'s narrow tolerance
was defeated by pricing only after the skew had been reversed. This was among the
first large flash-loan "economic" attacks, and it predates most tooling for it; a
grep for pool-derived pricing plus the question "is a same-block deposit+withdraw
profitable?" would have surfaced it.

## The fix
Break the atomic round-trip and stop trusting instantaneous pool pricing:

```solidity
// (1) forbid deposit and withdraw in the same block for an account
require(lastActionBlock[msg.sender] < block.number, "same block");
lastActionBlock[msg.sender] = block.number;

// (2) value shares off a manipulation-resistant price (Chainlink / long TWAP),
//     not calc_withdraw_one_coin / get_virtual_price read at spot;
// (3) tighten the arb check to reject the deposit when pool price deviates from a
//     trusted reference beyond a strict bound.
```

Harvest tightened the arbitrage check and moved to guard same-block deposit/withdraw
interactions; the durable rule is never to let one metric drive both sides of a
round-trip when that metric is atomically movable.

## Lessons for the checklist
- **SC-ORACLE-1 / SOL-AM-PMA-2** (spot price from an AMM): asking "does share pricing
  read a live Curve/AMM value?" flags `investedUnderlyingBalance`.
- **SC-ORACLE-6** (price derived from a pool a flash loan can inflate,
  `get_virtual_price`/`calc_withdraw`): named exactly; the strategy's valuation is it.
- **SC-FLASH-1** (invariant breakable in one tx): asking "is a same-tx
  deposit+withdraw profitable under a moved pool?" breaks the round-trip invariant.
- **SOL-Defi-FlashLoan-1** (withdraw not disabled in same block): the same-block
  deposit/withdraw is precisely this finding.
- Proposed new checklist question: *"Can an account deposit and withdraw in the same
  block, and does the share price on both sides derive from a pool value a flash loan
  can move between them?"*

## References
- Post-mortems: Harvest Finance flashloan economic attack post-mortem; SlowMist
  analysis; rekt.news/harvest-finance-rekt; The Block coverage of the $33.8M drain and
  $2.5M return.
- Transaction: https://etherscan.io/tx/0x35f8d2f572fceaac9288e5d462117850ef2694786992a8c3f6d02612277b0877
- Related: PancakeBunny (2021-05-19); Cream Finance (2021-10-27); Value DeFi; any vault
  pricing shares off a live Curve pool.
