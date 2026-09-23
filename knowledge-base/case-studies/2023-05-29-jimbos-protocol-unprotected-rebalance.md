# Case Study: Jimbo's Protocol — Unprotected Liquidity Rebalance (`shift`)

## Summary
- **Protocol:** Jimbo's Protocol (JIMBO), a Trader Joe v2 (Liquidity Book) floor-price token
- **Date:** 2023-05-29
- **Chain:** Arbitrum
- **Loss:** ~4,090 ETH (~$7.5M; DeFiHackLabs records ~$8M)
- **Vulnerability class:** [Front-running / MEV](../vulnerabilities/front-running-mev.md)
- **Checklist categories:** front-running-mev, oracle-and-price-manipulation
- **Checklist items:** SC-MEV-5, SC-MEV-1, SC-MEV-4, SOL-AM-SandwichAttack-1, SOL-Defi-AS-11
- **Root cause in one sentence:** The permissionless `shift()` repositioned the protocol's own liquidity bins around the *current* pool price with no slippage or price-band check, so an attacker who first pumped JIMBO could make the protocol move its liquidity to the manipulated price and then dump into it.
- **Attack tx:** https://arbiscan.io/tx/0xf9baf8cee8973cf9700ae1b1f41c625d7a2abdbcbc222582d24a8f2f790d0b5a
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-05/Jimbo_exp.sol

## Background
Jimbo's Protocol held its liquidity as protocol-owned liquidity (POL) in a Trader Joe v2
Liquidity Book (LB) JIMBO/WETH pair. LB liquidity lives in discrete price *bins*; the
active bin is the current price. Jimbo concentrated most WETH in a "floor" region and JIMBO
in higher "anchor" bins, and exposed a keeper-style `JimboController.shift()` that
rebalanced those bins in response to price moving above a `triggerBin` (and `reset()` /
`anchorBin` for the reverse). The intended invariant: `shift()` keeps liquidity productive
around a fair price. The fatal assumption: that the price at the moment `shift()` runs is
fair, rather than something a caller can set atomically.

Because `shift()` reads live pool state and can be called by anyone in the same
transaction as a swap, the protocol's own rebalance becomes a swap with `minAmountOut = 0`:
a protocol-executed trade with no slippage protection (SC-MEV-5).

## The vulnerability
The controller rebalances against `pair.getActiveId()` (the live active bin) with no bound
on how far that price may have been pushed within the current transaction.

```solidity
// (simplified) the shape of the flaw
function shift() external {                     // permissionless, no price band
    uint24 active = pair.getActiveId();         // live, attacker-movable price
    // withdraw protocol liquidity and re-add it centered on `active`
    _pullProtocolLiquidity();
    _addLiquidityAround(active);                // follows a manipulated price
    // no check: |active - anchorBin| within tolerance? no TWAP? no minOut on the moves?
}
```

Nothing anchors `active` to a manipulation-resistant reference (a TWAP, a hard price band,
or the protocol's own floor). An attacker who moves `active` up before calling `shift()`
gets the protocol to relocate its WETH-heavy liquidity to that inflated price, then sells
JIMBO back through the freshly repositioned bins at the attacker's advantage.

## The exploit, step by step
From the PoC (`executeOperation`, Aave flash-loan callback):
1. Flash-loan 10,000 WETH from Aave v3.
2. Seed a high bin and buy JIMBO up through the bins until `getActiveId() > triggerBin`,
   pushing the active price above the shift threshold (PoC Steps 1-2).
3. Call `controller.shift()` (Step 3). The protocol pulls its POL and re-adds it centered
   on the attacker-inflated active bin.
4. Buy out the remaining "normal" JIMBO bins, driving the active id to the LB maximum
   `8_388_607` (Step 4), then `shift()` again and `reset()` to walk liquidity back down
   while the attacker sits on the other side of every move (Steps 5-6).
5. Rebuy high, `shift()` once more, then swap all held JIMBO back to WETH through the
   protocol's relocated liquidity (Steps 7-9).
6. Repay the flash loan and keep the difference: about 4,090 ETH. The follow-on txs
   `0xfda5464e...`, `0x3c6e053f...`, and `0x44a0f565...` complete the extraction.

## Why it worked
This is a sandwich, but the "victim" in the middle is the protocol itself. Automated MEV
protection tooling looks for user swaps with weak `minAmountOut`; here the exploitable swap
is the protocol's own rebalance, which no `minAmountOut` guarded because the team never
modeled `shift()` as a trade (SC-MEV-5). The oracle for "where is fair price" was the
instantaneous active bin, which is manipulable within a single transaction with borrowed
capital (the oracle-and-price-manipulation angle). Fuzzing the token in isolation would not
reveal it; you have to ask "if I control the price when this protocol-owned operation runs,
what does it do for me?"

## The fix
Treat every protocol-executed swap or liquidity move as a slippage-sensitive trade:
- Gate `shift()`/`reset()` on a manipulation-resistant price (an LB or external TWAP, or a
  hard band around the floor), and revert if the live active id deviates too far.
- Enforce real `minAmountOut` / bin-slippage bounds on the internal add/remove-liquidity
  and any swaps they perform (SC-MEV-4, SOL-Defi-AS-11).
- Restrict who can trigger a rebalance, or require it to run outside the caller's swap
  transaction, so the price cannot be set atomically by the triggerer.

## Lessons for the checklist
- **SC-MEV-5** (protocol-owned/automated operations executing swaps without slippage
  bounds): describes `shift()` exactly and is the single question that catches this class.
- **SC-MEV-1** (sandwichable pending tx): reframed for a protocol action, it asks whether
  ordering a swap around the rebalance is profitable.
- **SC-MEV-4** (minAmountOut and deadline on every swap path): the internal moves had
  neither, so the question flags them.
- **SOL-AM-SandwichAttack-1** (explicit slippage protection) and **SOL-Defi-AS-11**
  (minAmountOut before swap): both demand the bound whose absence is the root cause.
- Proposed new question: *"For every protocol-triggered rebalance, fee conversion, or
  liquidity shift, is the price it acts on taken from a manipulation-resistant source, and
  can the caller move that price in the same transaction?"*

## References
- Post-mortem: docs.jimbosprotocol.xyz/protocol/liquidity-rebalancing-scenarios (rebalance design; not reachable from this environment). Analyses: @cryptofishx and @yicunhui2 threads (linked in the PoC).
- Transaction(s): `0xf9baf8cee8973cf9700ae1b1f41c625d7a2abdbcbc222582d24a8f2f790d0b5a` and follow-ons `0xfda5464e97043a2d0093cbed6d0a64f6a86049f5e9608c014396a7390188670e`, `0x3c6e053faecd331883641c1d23c9d9d37d065e4f9c4086e94a3c34bf8702618a`, `0x44a0f5650a038ab522087c02f734b80e6c748afb207995e757ed67ca037a5eda`.
- Related audits / similar incidents: **SushiSwap / Badger DAO DIGG (2021-01-25, 81.68 ETH)** is the small classic of the same class: `SushiMaker.convert()` is a permissionless fee-conversion that swaps accumulated fees to SUSHI with no slippage bound. Because DIGG/WBTC had no configured bridge, `convert` routed DIGG through a DIGG/WETH pair the attacker had created and could sandwich; `onlyEOA` blocked flash loans but not the sandwich itself. PoC `src/test/2021-01/Sushi_Badger_Digg_exp.sol`; analysis cmichel.io/replaying-ethereum-hacks-sushiswap-badger-dao-digg.
