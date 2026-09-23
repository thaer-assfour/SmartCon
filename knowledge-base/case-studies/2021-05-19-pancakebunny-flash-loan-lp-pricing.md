# Case Study: PancakeBunny — Flash-Loan LP Spot-Price Minting

## Summary
- **Protocol:** PancakeBunny (BUNNY yield aggregator / minter)
- **Date:** 2021-05-19
- **Chain:** BNB Smart Chain (BSC)
- **Loss:** ~$45M protocol loss; the attacker minted ~6.97M BUNNY and dumped it for ~114,631 WBNB, and the BUNNY price collapse wiped out roughly $200M of holder value. (Figures per rekt.news / Amber Group; the minted-and-dumped BUNNY is the direct proceed, the $200M is market-value destruction.)
- **Vulnerability class:** [Oracle & Price Manipulation](../vulnerabilities/oracle-and-price-manipulation.md)
- **Checklist categories:** flash-loans, oracle-and-price-manipulation
- **Checklist items:** SC-FLASH-1, SC-FLASH-2, SC-ORACLE-1, SC-ORACLE-6, SOL-AM-PMA-1, SOL-AM-PMA-2
- **Root cause in one sentence:** the BUNNY minter valued the performance-fee LP position from PancakeSwap spot reserves (`WBNB.balanceOf(pair) * 2 / pair.totalSupply()`), so flash-loaning the WBNB/USDT pool out of balance inflated that valuation and minted BUNNY proportional to a fake profit.
- **Attack tx:** https://bscscan.com/tx/0x897c2de73dd55d7701e1b69ffb3a17b0f4801ced88b0c75fe1551c5fcce6a979
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-05/PancakeBunny_exp.sol

## Background
PancakeBunny vaults auto-compound PancakeSwap LP positions. When a vault harvests, it
takes a performance fee, zaps it into the BUNNY-BNB LP, and mints fresh BUNNY to the
depositor proportional to the *BNB value* of that fee. The intended invariant: BUNNY
is minted only in proportion to real yield, so total BUNNY supply tracks real value
captured. The minter learned the fee's value from a price calculator that read
PancakeSwap reserves directly, which a flash loan can move within one block.

## The vulnerability
`PriceCalculatorBSC.valueOfAsset` prices a Cake-LP by doubling one side's *live
balance* and dividing by total supply, a spot reserve read (deployed pre-incident
source):

```solidity
// PriceCalculatorBSC.valueOfAsset (deployed, simplified): spot LP valuation
if (IPancakePair(asset).token0() == WBNB || IPancakePair(asset).token1() == WBNB) {
    valueInBNB = amount
        .mul(IBEP20(WBNB).balanceOf(address(asset)))   // live reserve, flash-loan movable
        .mul(2)
        .div(IPancakePair(asset).totalSupply());
}
```

`BunnyMinterV2.mintFor` fed the performance-fee LP amount into this and minted BUNNY
from the result:

```solidity
(uint valueInBNB,) = priceCalculator.valueOfAsset(BUNNY_BNB, bunnyBNBAmount);
uint contribution = valueInBNB.mul(_performanceFee).div(feeSum);
uint mintBunny = amountBunnyToMint(contribution);  // = contribution * bunnyPerProfitBNB / 1e18
_mint(mintBunny, to);
```

Both the LP valuation and the derived BUNNY mint scale with the manipulated WBNB
reserve, so inflating the pool inflates the mint.

## The exploit, step by step
1. Deposit a small WBNB+USDT LP into a `VaultFlipToFlip` and wait for the keeper's
   `harvest()` so the account has an accrued, mintable performance fee (`earned > 0`).
2. Take eight flash loans: seven WBNB loans cascaded through PancakeSwap pairs
   (`pancakeCall`) plus a ~2,961,750 USDT loan from ForTube Bank (`executeOperation`).
3. Zap 15,000 WBNB into the BUNNY-BNB LP and dump the remaining ~15,000-block of WBNB
   into the WBNB/USDT v1 pool, skewing its reserves so the LP valuation spikes.
4. Call `getReward()`; the minter reads the inflated `valueOfAsset(BUNNY_BNB, ...)`
   and mints ~6.97M BUNNY to the attacker for a performance fee that is mostly
   phantom.
5. Dump BUNNY into the WBNB/BUNNY pool for WBNB, unwind the pool skew, repay all flash
   loans, and keep the WBNB/USDT profit.

## Why it worked
The minter's economics depended on a metric, LP value in BNB, that is a pure
function of instantaneous pool reserves. With flash loans the "attacker cannot move
this pool" assumption is void for one block, and the minter had no manipulation
resistance: no TWAP, no external oracle cross-check, no per-block guard on the
harvest/mint path. A `getReserves`/`balanceOf`-in-pricing grep flags the calculator
in seconds, but the calculator looked like plumbing until traced into the mint math.

## The fix
Price LP tokens with a manipulation-resistant fair-value formula (reserves cannot be
moved profitably because the geometric mean is invariant to same-`k` swaps), and
sanity-bound against an external feed. PancakeBunny's later `PriceCalculatorBSC`
adopted the Alpha Homora fair-LP method:

```solidity
// fair LP price: 2 * sqrt(r0 * r1) / totalSupply * sqrt(p0 * p1), reserves-manipulation resistant
uint sqrtK = HomoraMath.sqrt(r0.mul(r1)).fdiv(totalSupply);
uint fairPriceInBNB = sqrtK.mul(2).mul(HomoraMath.sqrt(px0)).div(2**56)
                            .mul(HomoraMath.sqrt(px1)).div(2**56);
```

with `px0`/`px1` sourced from Chainlink-backed `_oracleValueOf`, so the value no
longer tracks a single-block reserve.

## Lessons for the checklist
- **SC-ORACLE-1 / SOL-AM-PMA-2** (spot price from AMM reserve/`balanceOf`): asking
  "does any valuation read `balanceOf(pair)` or `getReserves`?" flags `valueOfAsset`.
- **SC-ORACLE-6** (price derived from a pool a flash loan can inflate, LP-token
  pricing): the LP valuation is exactly this pattern.
- **SOL-AM-PMA-1** (price from ratio of token balances): the `balanceOf * 2 /
  totalSupply` formula is the named anti-pattern.
- **SC-FLASH-1 / SC-FLASH-2** (invariant breakable in one tx; share/mint math read at
  an atomically inflatable point): asking "can I move this reserve in the same tx I
  mint?" shows capital is no barrier.
- Proposed new checklist question: *"Is any mint/reward amount derived from an LP or
  pool value computed from live reserves, and if so is that value fair-priced
  (sqrt(k)) and bounded by an external oracle?"*

## References
- Post-mortems: Amber Group, "BSC Flash Loan Attack: PancakeBunny"; SlowMist analysis;
  rekt.news/pancakebunny-rekt.
- Transaction: https://bscscan.com/tx/0x897c2de73dd55d7701e1b69ffb3a17b0f4801ced88b0c75fe1551c5fcce6a979
- Related: Harvest Finance (2020-10-26); Cheese Bank; any minter/vault that prices LPs
  off spot reserves.
