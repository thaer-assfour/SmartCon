# Case Study: Multichain (Anyswap) — Phantom `permit` on WETH

## Summary
- **Protocol:** Multichain / Anyswap `AnyswapV4Router.anySwapOutUnderlyingWithPermit`
- **Date:** 2022-01-18
- **Chain:** Ethereum
- **Loss:** ~$1.4M in the first exploit tx (PeckShield/DeFiHackLabs); total user losses before Multichain's reimbursement were later put at roughly $3M. Dedaub, who disclosed the bug on 2022-01-10, estimated up to ~$431M in WETH directly stealable and close to $1B at risk across eight affected tokens.
- **Vulnerability class:** [Low-Level Calls & Return Data](../vulnerabilities/low-level-calls.md)
- **Checklist categories:** signatures, token-integration, low-level-calls
- **Checklist items:** SC-TOKEN-7, SC-LL-4, SC-SIG-4, SOL-Token-FE-11, SOL-LL-2
- **Root cause in one sentence:** the router called `permit()` on an attacker-supplied token's `underlying()`, and when that underlying is WETH (which has no `permit`), WETH's payable fallback silently accepts the call and returns success, so the router proceeded to `safeTransferFrom` a victim's pre-existing WETH allowance with no signature ever verified.
- **Attack tx:** https://etherscan.io/tx/0xe50ed602bd916fc304d53c4fed236698b71691a95774ff0aeeb74b699c6227f7
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-01/Anyswap_exp.sol

## Background
Anyswap routers bridge tokens; `anySwapOutUnderlyingWithPermit` is a convenience
entry point that lets a user authorise a pull of the *underlying* token with an
EIP-2612 `permit` signature instead of a prior `approve`. The intended invariant:
funds move out of an account only if that account signed a valid `permit` for this
router. The bug is that the router never confirmed the signature actually did
anything: it assumed a successful `permit()` call meant a verified authorisation.

## The vulnerability
The router takes `token` from the caller, reads its `underlying()`, calls `permit`
on the underlying, then transfers. From `anyswap-v1-core` (`AnyswapV*Router.sol`):

```solidity
function anySwapOutUnderlyingWithPermit(
    address from, address token, address to, uint amount,
    uint deadline, uint8 v, bytes32 r, bytes32 s, uint toChainID
) external {
    address _underlying = AnyswapV1ERC20(token).underlying();       // attacker controls `token`
    IERC20(_underlying).permit(from, address(this), amount, deadline, v, r, s);  // (A)
    IERC20(_underlying).safeTransferFrom(from, token, amount);      // (B) pulls the victim's approval
    AnyswapV1ERC20(token).depositVault(amount, from);
    ...
}
```

`token` is attacker-supplied, so `_underlying` can be WETH. WETH9 implements no
`permit`; a call to that selector falls through to WETH's payable fallback
(`function() public payable { deposit(); }`), which with zero value is an inert no-op
that **returns success**. Line (A) therefore neither reverts nor checks anything.
Line (B) then executes against a real WETH allowance: any account that had previously
approved the router for WETH (routine for bridge users) can have that WETH pulled by
anyone, sent to the attacker's `token` contract, which forwards it out.

## The exploit, step by step
1. Deploy a contract that satisfies the `AnyswapV1ERC20` shape the router calls:
   `underlying()` returns WETH, and `burn`/`depositVault` are no-op stubs.
2. Call `anySwapOutUnderlyingWithPermit(victim, attackerToken, attacker, amount,
   deadline, 0, "0x", "0x", chainId)`; the `v/r/s` are garbage and are never used.
3. The router calls `WETH.permit(...)`; WETH's fallback swallows it and returns
   success. No signature is verified.
4. The router `safeTransferFrom`s `amount` WETH from the victim (who had an existing
   max approval to the router) to the attacker's token contract.
5. The attacker sweeps the WETH out. Repeat against every account holding a
   router WETH allowance.

## Why it worked
Two Solidity facts combine: a low-level call to a contract that lacks the target
selector runs its fallback and reports success (a "phantom function"), and
`safeTransferFrom` will happily spend a *pre-existing* allowance regardless of how it
was authorised. The router conflated "the `permit` call did not revert" with "the
user authorised this transfer." Because the only real gate was the victim's standing
approval, the exploit needed no signature at all. The `SC-SIG-4` (replay) lens is a
weaker fit here: nothing is replayed, the signature is simply never checked, so the
signature-verification family degenerates to "authorisation assumed, never proven."

## The fix
Confirm the token really implements `permit` before trusting it, and verify the
allowance was actually established. The robust patterns:

```solidity
// (1) require real bytecode + a permit that provably moved the nonce / allowance
require(_underlying.code.length > 0, "no code");
uint256 nonceBefore = IERC2612(_underlying).nonces(from);
IERC20(_underlying).permit(from, address(this), amount, deadline, v, r, s);
require(IERC2612(_underlying).nonces(from) == nonceBefore + 1, "permit no-op");
// (2) or drop the permit convenience path entirely and require an explicit approve
```

Multichain removed the vulnerable path, urged users to revoke router approvals, and
reimbursed affected users. The class did **not** die: on 2025-07-29 the same
`AnyswapV4Router` at `0x6b7a87899490EcE95443e979cA9485CBE7E71522` was hit again for
200 WETH (attack tx `0xae79fdcfd7c36ed654d11b352b495340bd3cc47d0849c35ac6ffa1e4859098ec`,
PoC `src/test/2025-07/AnyswapWETHPermit_exp.sol`) against accounts that still held a
stale max approval: the same phantom-permit bug, three and a half years later.

## Lessons for the checklist
- **SC-TOKEN-7** (phantom functions: calling `permit`/optional functions on tokens
  that may not implement them, WETH fallback swallows the call): this item names the
  exact bug; asking it flags line (A) immediately.
- **SC-LL-4 / SOL-LL-2** (call to a codeless / no-matching-signature address treated
  as success): asking "what happens if `_underlying` has no `permit`?" reveals the
  silent-success fallback.
- **SOL-Token-FE-11** (token is ERC2612/permit): asking "is the token guaranteed to
  implement EIP-2612?" exposes the unchecked assumption for arbitrary `underlying`s.
- **SC-SIG-4** (cross-chain/instance replay): a partial fit, since the deeper failure
  is that the signature is never validated at all, which asking "is the signature
  result actually checked?" surfaces.
- Proposed new checklist question: *"When we call `permit` (or any optional token
  method), do we verify the token implements it (via `code.length` plus a
  nonce/allowance delta) rather than trusting that the call did not revert?"*

## References
- Post-mortem: Zengo, "Without Permit: Multichain's exploit explained"; Dedaub,
  "Phantom Functions and the Billion-Dollar No-op" (disclosed 2022-01-10).
- Transactions: https://etherscan.io/tx/0xe50ed602bd916fc304d53c4fed236698b71691a95774ff0aeeb74b699c6227f7
  and (2025 recurrence) https://etherscan.io/tx/0xae79fdcfd7c36ed654d11b352b495340bd3cc47d0849c35ac6ffa1e4859098ec
- Related: DeFiVulnLabs `phantom-permit.sol`; any router/vault that calls `permit` on
  a user-specified token.
