# Case Study: SushiSwap RouteProcessor2 — Unverified Swap Callback Drains Approvals

## Summary
- **Protocol:** SushiSwap `RouteProcessor2` router
- **Date:** 2023-04-09
- **Chain:** Ethereum (and other chains where RouteProcessor2 was deployed)
- **Loss:** >$3.3M (largest single victim 0xSifu; the majority was recovered by whitehats)
- **Vulnerability class:** [Input Validation & Uninitialized State](../vulnerabilities/input-validation.md)
- **Checklist categories:** input-validation, access-control
- **Checklist items:** SC-INPUT-5, SC-INPUT-6, SOL-Defi-AS-12, SOL-Integrations-Uniswap-6, SOL-Defi-AS-6, SOL-EC-5
- **Root cause in one sentence:** `processRoute` let the caller name the Uniswap V3 pool inside `route`, and `uniswapV3SwapCallback` trusted its `msg.sender` as that just-called pool, so a fake pool contract could invoke the callback and make the router `transferFrom` any user who had approved RouteProcessor2.
- **Attack tx:** https://etherscan.io/tx/0x04b166e7b4ab5105a8e9c85f08f6346de1c66368687215b0e0b58d6e5002bc32
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/Sushi_Router_exp.sol

## Background
`RouteProcessor2` is SushiSwap's swap router. Users grant it an ERC-20 approval and call
`processRoute(tokenIn, amountIn, tokenOut, amountOutMin, to, route)`; the router decodes the
`route` bytes into a sequence of pool hops and, for Uniswap V3-style pools, calls
`pool.swap(...)`. The V3 pool then calls back into the router's `uniswapV3SwapCallback` to
collect the input tokens, and the router pays by pulling them (via `transferFrom`) from the
user who initiated the route. The intended invariant: the router only ever pulls a user's
approved tokens to pay for that user's own swap, and only in response to a callback from a
pool the router itself just called. Both halves of that invariant were unenforced.

## The vulnerability
The pool address is caller-supplied in `route`, and the callback does not verify that its
caller is a pool the router actually invoked. The PoC demonstrates the two pieces:

```solidity
// (simplified) the trust that was missing in RouteProcessor2
function uniswapV3SwapCallback(int256 amount0Delta, int256 amount1Delta, bytes calldata data) external {
    // BUG: msg.sender is assumed to be the pool we just called; not checked against a recorded pool
    (address tokenIn, address payer) = abi.decode(data, (address, address));
    IERC20(tokenIn).transferFrom(payer, msg.sender, uint256(amount0Delta)); // pulls the PAYER's approval
}
```

In the exploit the attacker sets `pool = address(this)` in the `route` (a contract that
merely implements `swap`). `processRoute` calls the attacker's fake `swap`, which turns
around and calls `processor.uniswapV3SwapCallback(100e18, 0, abi.encode(WETH, victim))`.
The router's callback trusts the caller as the legitimate pool (SC-INPUT-5, SOL-Defi-AS-12),
decodes the attacker-chosen `payer = victim`, and executes `transferFrom` pulling the
victim's WETH to the attacker-controlled pool (SC-INPUT-6, SOL-Defi-AS-6). Because the pool
and the calldata are user input, the router becomes a generic "move any approving user's
tokens" primitive (SOL-Integrations-Uniswap-6, SOL-EC-5).

## The exploit, step by step
From `testExp()`:
1. Deploy an attacker contract that implements `IUniswapV3Pool.swap`.
2. Build a `route` whose pool field is the attacker contract's address, and call
   `processRoute(0xEeee..native, 0, 0xEeee.., 0, address(0), route)` with zero amounts so no
   real swap economics are needed.
3. `RouteProcessor2` decodes the route and calls the attacker's `swap(...)`.
4. Inside `swap`, the attacker calls `processor.uniswapV3SwapCallback(100e18, 0, abi.encode(WETH, victim))`.
5. The router's callback trusts `msg.sender` as the pool and `transferFrom`s 100 WETH from
   `victim` (who had approved RouteProcessor2) to the attacker's pool. Repeat per victim /
   per token approval.

## Why it worked
The callback is the security boundary of a router-with-approvals, and it was left open on
both axes a callback must check: *who is calling* (is `msg.sender` a pool the router itself
just invoked?) and *on whose behalf* (is the payer the current route's initiator?). Here the
pool was attacker-supplied and the payer was attacker-supplied, so any address with a live
approval to RouteProcessor2 was drainable. This is not detectable by generic tooling because
the router's code "works" for honest routes; the review question is "can a user-supplied
address end up as the trusted counterparty in a callback, and can that callback move a third
party's approval?".

## The fix
Bind the callback to a pool the router actually called, and to the current payer.

```solidity
// record the pool right before calling it, and verify it in the callback
address private lastCalledPool;
function _swapV3(address pool, ...) internal {
    lastCalledPool = pool;
    IUniswapV3Pool(pool).swap(...);
    lastCalledPool = address(0);
}
function uniswapV3SwapCallback(int256 a0, int256 a1, bytes calldata data) external {
    require(msg.sender == lastCalledPool, "unexpected caller"); // only the pool we just called
    // pay only from the initiator of the current route, never an arbitrary `payer`
}
```

## Lessons for the checklist
- **SC-INPUT-5** (callbacks verify `msg.sender` is the expected pool/lender and the initiator
  is this contract): this is the exact missing check, on both the caller and the initiator.
- **SC-INPUT-6** (can user-supplied address/calldata make the contract perform an arbitrary
  external call, including `transferFrom` of other users' approvals): describes the drain
  primitive precisely.
- **SOL-Defi-AS-12** (callback caller verified) and **SOL-Integrations-Uniswap-6**
  (`pool.swap` used directly): flag the unverified pool call.
- **SOL-Defi-AS-6** (arbitrary calls from user input) and **SOL-EC-5** (called address
  whitelisted): the pool address should never be freely caller-chosen and trusted.
- Proposed new question: *"In every swap/flash-loan callback, does the contract verify both
  that `msg.sender` is a counterparty it itself just called and that funds are pulled only
  from the current operation's initiator, never an address decoded from callback data?"*

## References
- Post-mortem: PeckShield thread (twitter.com/peckshield/status/1644907207530774530) — not reachable from this environment; behaviour confirmed against the PoC (header: "does not check user input `route` carefully").
- Transaction(s): `0x04b166e7b4ab5105a8e9c85f08f6346de1c66368687215b0e0b58d6e5002bc32`; RouteProcessor2 `0x044b75f554b886A065b9567891e45c79542d7357`; example victim `0x31d3243CfB54B34Fc9C73e1CB1137124bD6B13E1`.
- Related audits / similar incidents (same "arbitrary external call from user input" class):
  **Dexible (2023-02-17, ~$1.5M)** — `selfSwap` took a caller-supplied `router` and
  `routerData`, so the attacker passed `router = TRU token` and `routerData = transferFrom(victim, attacker, amount)`
  to drain approvals; tx `0x138daa4cbeaa3db42eefcec26e234fc2c89a4aa17d6b1870fc460b2856fd11a6`,
  PoC `src/test/2023-02/Dexible_exp.sol`.
  **Transit Swap (2022-10-02, >$21M, BSC)** — the swap/claim path (`claimTokens` / `callBytes`)
  performed `transferFrom` with an unverified, caller-supplied owner and target, letting the
  attacker move any prior approver's tokens; tx
  `0x181a7882aac0eab1036eedba25bc95a16e10f61b5df2e99d240a16c334b9b189`, PoC
  `src/test/2022-10/TransitSwap_exp.sol`.
