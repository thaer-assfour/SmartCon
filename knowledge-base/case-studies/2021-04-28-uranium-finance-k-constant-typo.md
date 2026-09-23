# Case Study: Uranium Finance — Fork Left the K Constant at `1000**2`

## Summary
- **Protocol:** Uranium Finance (Uniswap v2 fork, "v2" pair)
- **Date:** 2021-04-28
- **Chain:** BSC
- **Loss:** ~$50M
- **Vulnerability class:** [DeFi Business Logic](../vulnerabilities/defi-logic.md)
- **Checklist categories:** general-hygiene, defi-logic, arithmetic-and-precision
- **Checklist items:** SC-HYG-6, SC-DEFI-2, SOL-Defi-AS-4, SOL-Defi-AS-5, SOL-Heuristics-16
- **Root cause in one sentence:** The fork raised the fee-scaling factor in `balanceAdjusted` from 1000 to 10000 but left the constant-product invariant check multiplying reserves by `1000**2`, so the required post-swap K was 100x too small and a swap could drain almost the entire reserve.
- **Attack tx:** https://bscscan.com/tx/0x5a504fe72ef7fc76dfeb4d979e533af4e23fe37e90b5516186d5787893c37991
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-04/Uranium_exp.sol

## Background
Uranium Finance was a Uniswap v2 fork on BSC. A v2 pair enforces its constant-product
invariant at the end of `swap`: after accounting for the swap fee, the product of the
adjusted balances must be at least the product of the pre-swap reserves. The intended
invariant is `x * y = k` (never decreasing after fees). Uranium's fork changed the fee
math to use a scale of 10000 (allowing finer-grained fees, e.g. 0.16% as `16/10000`) but
did not update the matching constant on the right-hand side of the K check. The result is
not a subtle rounding issue: the invariant is loosened by exactly 100x, so the pool will
accept a swap that removes essentially all of one reserve.

## The vulnerability
Compare the canonical Uniswap v2 check with Uranium's. The Uniswap v2 source (verified
here against `UniswapV2Pair.sol`) uses a 1000 scale on both sides:

```solidity
// Uniswap v2 (reference): scale 1000 on BOTH sides, 0.3% fee = 3/1000
uint balance0Adjusted = balance0.mul(1000).sub(amount0In.mul(3));
uint balance1Adjusted = balance1.mul(1000).sub(amount1In.mul(3));
require(balance0Adjusted.mul(balance1Adjusted)
        >= uint(_reserve0).mul(_reserve1).mul(1000**2), 'UniswapV2: K');
```

Uranium's pair (quoted verbatim in the PoC header) scaled the balances by 10000 but kept
`1000**2` on the reserve side:

```solidity
// Uranium (vulnerable): scale 10000 on the LEFT, but 1000**2 on the RIGHT
uint balance0Adjusted = balance0.mul(10000).sub(amount0In.mul(16));
uint balance1Adjusted = balance1.mul(10000).sub(amount1In.mul(16));
require(balance0Adjusted.mul(balance1Adjusted)
        >= uint(_reserve0).mul(_reserve1).mul(1000**2), 'UraniumSwap: K'); // BUG: should be 10000**2
```

With no swap in progress (`amountIn = 0`, `balance ~= reserve`) the left side is
`reserve0 * 10000 * reserve1 * 10000 = reserve0 * reserve1 * 10^8`, while the right side is
`reserve0 * reserve1 * 10^6`. The check therefore holds with a factor of 100 to spare. An
attacker can withdraw output tokens until the post-swap product falls to `1/100` of the
pre-swap product and the require still passes, i.e. take out roughly 99% of a reserve while
sending in a negligible amount.

## The exploit, step by step
The PoC (`takeFunds`) is almost trivially small:
1. Wrap 1 BNB to WBNB to have a dust input.
2. For a target pair, transfer a tiny `amount` (1 wei class) of `token0` into the pair.
3. Compute `amountOut = balanceOf(pair, token1) * 99 / 100` and call `pair.swap(...)` to
   pull out 99% of `token1`. The broken K check accepts it.
4. Repeat across pairs / both directions (`takeFunds(wbnb, busd, ...)` then
   `takeFunds(busd, wbnb, ...)`) to sweep reserves.

Across Uranium's pools this drained on the order of $50M.

## Why it worked
This is a copied-code constant that was edited on one side of an equation and not the
other (SC-HYG-6, SOL-Heuristics-16). The code compiles, passes ordinary swap tests
(normal-sized swaps still satisfy a 100x-looser invariant), and only a swap that
deliberately empties the pool reveals that the invariant is not actually enforced. A diff
against the upstream Uniswap v2 pair would have flagged the mismatched `1000**2` against
the changed `10000` scale immediately; a fuzz test asserting "product of reserves is
non-decreasing after fees" would have failed at once (SC-DEFI-2, SOL-Defi-AS-5). Generic
scanners have no notion of the AMM invariant, so they saw nothing.

## The fix
Make both sides of the invariant use the same scale.

```solidity
require(balance0Adjusted.mul(balance1Adjusted)
        >= uint(_reserve0).mul(_reserve1).mul(10000**2), 'UraniumSwap: K'); // matched scale
```

More robustly: derive the scale from a single named constant so the fee scale and the K
constant cannot drift apart, and keep a differential test against the upstream pair.

## Lessons for the checklist
- **SC-HYG-6** (forked/copied code: constants, fee denominators and formulas diffed line by
  line against upstream): a line-by-line diff of the pair against Uniswap v2 surfaces the
  `1000**2` versus `10000` mismatch directly.
- **SC-DEFI-2** (AMM invariant/fees/reserves updated correctly): asks whether `x*y=k` holds
  after fees, which a single adversarial swap answers "no".
- **SOL-Defi-AS-4** (AMM uses forked code) and **SOL-Defi-AS-5** (rounding in constant
  product): both point the reviewer at the exact check that was miscalibrated.
- **SOL-Heuristics-16** (code asymmetries): the asymmetry between the 10000-scaled left side
  and the 1000-scaled right side is the tell.
- Proposed new question: *"In every forked AMM, is the constant-product K check's scale
  constant derived from the same source as the fee scale, and does a fuzz test assert the
  reserve product is non-decreasing after fees for adversarial swap sizes?"*

## References
- Post-mortem: Immunefi, "Building a PoC for the Uranium Heist" (medium.com/immunefi/building-a-poc-for-the-uranium-heist-ec83fbd83e9f); not reachable from this environment; the vulnerable code is quoted in the PoC header.
- Transaction(s): attack `0x5a504fe72ef7fc76dfeb4d979e533af4e23fe37e90b5516186d5787893c37991`; attack contract `0x2b528a28451e9853f51616f3b0f6d82af8bea6ae`; factory `0xA943eA143cd7E79806d670f4a7cf08F8922a454F`.
- Related audits / similar incidents: any Uniswap v2/v3 fork that edited fee math; general class of "changed a magic number on one side of the invariant only".
