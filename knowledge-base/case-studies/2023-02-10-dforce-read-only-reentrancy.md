# Case Study: dForce — Read-Only Reentrancy in a Curve LP Oracle

## Summary
- **Protocol:** dForce (lending market + wstETH/ETH Curve LP collateral)
- **Date:** 2023-02-10
- **Chain:** Arbitrum and Optimism
- **Loss:** ~$3.65M total (~$1.9M Arbitrum, ~$1.73M Optimism); all funds later returned by the attacker
- **Vulnerability class:** [Reentrancy](../vulnerabilities/reentrancy.md)
- **Checklist categories:** reentrancy, oracle-and-price-manipulation
- **Checklist items:** SC-REEN-3, SC-ORACLE-6, SOL-AM-ReentrancyAttack-1, SOL-Defi-Oracle-13
- **Root cause in one sentence:** dForce priced its wstETHCRV gauge collateral from the Curve pool's `get_virtual_price()`, which returns a transiently inflated value *during* the pool's `remove_liquidity` ETH-refund callback, and the attacker re-entered dForce's liquidation path inside that callback to seize collateral at a manipulated price.
- **Attack tx:** https://arbiscan.io/tx/0x5db5c2400ab56db697b3cc9aa02a05deab658e1438ce2f8692ca009cc45171dd
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/dForce_exp.sol

## Background
dForce accepted the Curve wstETH/ETH LP (via a `wstETHCRV-gauge` vault token,
`VWSTETHCRVGAUGE`) as collateral. Its price oracle valued that collateral through the
Curve pool's `get_virtual_price()`. The intended invariant: the reported collateral
price equals the honest per-LP value of the underlying pool assets, so a borrower can
only be liquidated when genuinely under-collateralised. Curve's `get_virtual_price`
is often assumed manipulation-resistant because it is an accounting ratio rather than
a spot reserve ratio. That assumption is false *mid-transaction*: Curve's
`remove_liquidity` sends ETH to the caller (a callback) **after** it has burned LP
but while `D`/`totalSupply` are momentarily inconsistent, so any `view` read during
the callback is stale. This is classic read-only reentrancy.

## The vulnerability
Curve StableSwap `remove_liquidity` updates balances and then transfers each coin
out. For an ETH pool the transfer is a value-bearing call that yields control to the
receiver before the function returns, and `get_virtual_price()` read at that instant
does not reflect the completed state. dForce's oracle consumed that number directly:

```solidity
// dForce collateral oracle (simplified): LP priced off the live Curve accounting ratio
function getUnderlyingPrice(address vToken) external view returns (uint256) {
    // ... resolves to the Curve pool for wstETH/ETH ...
    uint256 vp = ICurvePool(curvePool).get_virtual_price();   // stale during remove_liquidity callback
    return vp * underlyingUsdPrice / 1e18;                    // trusted for liquidation math
}
```

Because `get_virtual_price` is a `view`, dForce wrote no bad state itself. The victim
was dForce's own liquidation logic, which trusted a value another contract briefly
mis-reported.

## The exploit, step by step
1. Chain flash loans (Balancer, Aave v3, Radiant, Uniswap v3, three Sushi pairs,
   Zyber, a Saddle-style `SwapFlashLoan`) to assemble a large WETH position with no
   capital of its own.
2. `curvePool.add_liquidity{value: ETH}([ETH, 0], 0)` to mint wstETHCRV, and via a
   helper `Borrower` deposit wstETHCRV into the gauge and into dForce, borrowing USX
   against it (establishing a controlled, borderline position).
3. Call `curvePool.remove_liquidity(burnAmount, [0, 0])`. Curve burns the LP, then
   refunds ETH to the attacker contract, entering its `fallback()`.
4. **Inside that fallback**, `PriceOracle.getUnderlyingPrice(VWSTETHCRVGAUGE)` now
   reads the inflated `get_virtual_price`. The attacker calls
   `dForceContract.liquidateBorrow(...)` against its own `Borrower` and against a real
   victim (`0x9167...b26D`), seizing gauge collateral valued at the manipulated price.
5. Redeem the seized `VWSTETHCRVGAUGE` to `wstETHCRV`, withdraw from the gauge,
   `remove_liquidity` again, swap wstETH to ETH, repay every flash loan, and swap the
   residual USX -> USDC -> WETH as profit.

## Why it worked
The oracle treated a Curve accounting function as if it were always consistent. It
was, except during the pool's own external calls, and Curve's ETH `remove_liquidity`
makes exactly such a call. No detector flags this from dForce's source alone: the
`view` function looks pure and side-effect free, and the reentrancy lives in a
*different* contract's control flow. This is the same class that hit Midas Capital
and Market.xyz earlier; the general lesson (Curve read-only reentrancy) was public
before this incident.

## The fix
Never read a pool's price while that pool may be mid-callback. Curve exposes the
lock; integrators must check it:

```solidity
// Safe read: assert the Curve pool is not executing (reentrancy lock is free)
ICurvePoolLock(curvePool).claim_admin_fees();   // reverts if locked, one common guard
// or, on newer pools:
require(ICurvePool(curvePool).get_reentrancy_status() == false, "curve locked");
uint256 vp = ICurvePool(curvePool).get_virtual_price();
```

dForce paused the affected markets, and the ecosystem guidance hardened: wrap the
oracle read behind Curve's `remove_liquidity([0,0])` no-op lock-check or a
`nonReentrant`-style probe so any read during a live callback reverts instead of
returning a stale value.

## Lessons for the checklist
- **SC-REEN-3** (read-only reentrancy): asking "does any external `view` we trust
  return inconsistent state mid-callback?" points directly at `get_virtual_price`.
- **SC-ORACLE-6** (price derived from a pool a flash loan can inflate in the same tx):
  `get_virtual_price` is named explicitly in this item; asking it flags the collateral
  oracle immediately.
- **SOL-AM-ReentrancyAttack-1** (view returns stale value during interactions): the
  attack is the textbook instance of this finding.
- **SOL-Defi-Oracle-13** (spot price manipulation): even an accounting ratio behaves
  like a manipulable spot value when read during the source's own callback.
- Proposed new checklist question: *"For every third-party `view` used as a price
  (especially Curve `get_virtual_price` / `calc_withdraw_one_coin`), do we assert the
  source pool's reentrancy lock is free before trusting the value?"*

## References
- Analyses: SlowMist (twitter.com/SlowMist_Team/status/1623956763598000129), BlockSec
  (twitter.com/BlockSecTeam/status/1623901011680333824), PeckShield
  (twitter.com/peckshield/status/1623910257033617408).
- Transaction (Arbitrum): https://arbiscan.io/tx/0x5db5c2400ab56db697b3cc9aa02a05deab658e1438ce2f8692ca009cc45171dd
- Related: Midas Capital and Market.xyz Curve read-only-reentrancy incidents; the
  general Curve read-only reentrancy disclosures of 2022.
