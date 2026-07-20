# Review Checklist

The spine of SmartCon. Apply it during Phases 3–4, category by category, against
every entry point in your attack-surface map. Each item is phrased as a question —
answer it with evidence from the code, not from assumption.

Deep-dive notes for each category live in [`../knowledge-base/vulnerabilities/`](../knowledge-base/vulnerabilities/).

How to use: for each in-scope contract, go category → question → find the code that
answers it → record the answer in your audit notes. An unanswered question is an
open lead, not a pass.

---

## 1. Reentrancy — [notes](../knowledge-base/vulnerabilities/reentrancy.md)

- [ ] Does any function make an external call (token transfer, `call`, callback)
      *before* updating state? (Checks-Effects-Interactions violation)
- [ ] Are there cross-function reentrancy paths that share state but not a guard?
- [ ] Is there **read-only reentrancy**: a view function returning stale state that
      other protocols trust mid-callback?
- [ ] Do ERC-777 / ERC-721 / ERC-1155 hooks or `receive()`/`fallback()` give the
      attacker a callback window?
- [ ] Is `nonReentrant` applied consistently across *all* functions touching the
      same state, including cross-contract entry points?

## 2. Access Control — [notes](../knowledge-base/vulnerabilities/access-control.md)

- [ ] Is every state-changing/privileged function gated by the correct modifier?
- [ ] Any function that *should* be `onlyOwner`/role-gated but is public?
- [ ] Is `tx.origin` used for authorization? (phishable — should be `msg.sender`)
- [ ] Are initializers protected against being called twice / by anyone?
- [ ] Are role admins set correctly? Can a role escalate itself?
- [ ] Is there a default-admin or emergency backdoor that concentrates too much power?

## 3. Arithmetic & Precision — [notes](../knowledge-base/vulnerabilities/arithmetic-and-precision.md)

- [ ] Any `unchecked` blocks where overflow/underflow is actually reachable?
- [ ] Does division happen before multiplication, losing precision?
- [ ] What direction does rounding go, and who profits? Can it be repeated to drain?
- [ ] First-depositor / share-inflation: can a tiny first deposit + donation make
      shares mis-price for later depositors? (ERC-4626 classic)
- [ ] Are decimals normalized across tokens of different precision?
- [ ] Any casts (`uint256`→`uint128`, signed↔unsigned) that silently truncate?

## 4. Oracle & Price Manipulation — [notes](../knowledge-base/vulnerabilities/oracle-and-price-manipulation.md)

- [ ] Does pricing use a **spot price** from an AMM reserve/`getReserves`/`balanceOf`?
      (manipulable in one tx via flash loan)
- [ ] For Chainlink: are `updatedAt` staleness and `answeredInRound` checked? Is a
      zero/negative price handled? Are min/max bounds considered?
- [ ] Is a TWAP used, and is its window long enough to resist manipulation?
- [ ] Does the protocol trust `token.balanceOf(pair)` for accounting? (donation-manipulable)
- [ ] What happens if the oracle reverts or returns stale data — fail open or closed?

## 5. Flash Loans & Atomic Composition — [notes](../knowledge-base/vulnerabilities/flash-loans.md)

- [ ] Can any invariant be broken *within a single transaction* using borrowed capital?
- [ ] Are governance votes / share prices / collateral ratios read at a point an
      attacker can inflate atomically?
- [ ] Does the protocol assume "an attacker can't have $100M"? (they can, for one block)

## 6. DeFi Business Logic — [notes](../knowledge-base/vulnerabilities/defi-logic.md)

- [ ] Lending: are collateral factor, health factor, and liquidation math correct at
      the boundaries? Can a position be made unliquidatable, or self-liquidated for profit?
- [ ] AMM: are the swap invariant (`x*y=k`), fees, and reserves updated atomically
      and in the right order?
- [ ] Staking/rewards: can rewards be double-claimed, claimed after unstake, or
      diluted/inflated via deposit timing?
- [ ] Vaults (ERC-4626): does `deposit`/`mint`/`withdraw`/`redeem` round in the
      protocol's favor? Is the first-deposit inflation attack mitigated?
- [ ] Fee logic: can fees be bypassed, set to values that break accounting, or
      round to zero?
- [ ] Slippage / deadline: are user-supplied `minOut` and `deadline` enforced?

## 7. Upgradeability & Proxies — [notes](../knowledge-base/vulnerabilities/upgradeability.md)

- [ ] Storage layout: does an upgrade risk a **storage collision** with the old layout?
- [ ] Is the implementation contract left **uninitialized** (attacker can init & self-destruct/`delegatecall`)?
- [ ] `delegatecall` to untrusted targets? Function-selector clashes between proxy and impl?
- [ ] Are `__gap` slots reserved in upgradeable base contracts?
- [ ] Who can upgrade, and is that authority appropriately decentralized/timelocked?

## 8. Signatures & Replay — [notes](../knowledge-base/vulnerabilities/signatures.md)

- [ ] Is every signed message bound to a **nonce**, and is the nonce consumed?
- [ ] Is the signature bound to `chainId` and the contract address (EIP-712 domain)?
- [ ] Is `ecrecover` checked against `address(0)` (malleability / invalid sig)?
- [ ] Can a signature be replayed across chains, forks, or contract instances?
- [ ] Are `v/r/s` malleability and signature-uniqueness assumptions safe?

## 9. Denial of Service — [notes](../knowledge-base/vulnerabilities/denial-of-service.md)

- [ ] Unbounded loops over user-growable arrays (can exceed block gas limit)?
- [ ] Does a single failing external call (e.g. one recipient's transfer reverting)
      block a whole batch / the whole protocol? (push vs. pull payments)
- [ ] Can an attacker grief by forcing gas costs, filling a queue, or locking funds?
- [ ] Does the protocol handle a token that reverts on zero-value transfer?

## 10. Token Integration Quirks — [notes](../knowledge-base/vulnerabilities/token-integration.md)

- [ ] **Fee-on-transfer**: does the code assume received == sent amount?
- [ ] **Rebasing tokens**: does cached balance drift from actual balance?
- [ ] **Missing return value** ERC-20s (USDT): is `SafeERC20`/`safeTransfer` used?
- [ ] **ERC-777** hooks enabling reentrancy on transfer?
- [ ] **Non-standard decimals** (e.g. USDC=6, WBTC=8) handled?
- [ ] **Approval race** / double-spend on non-zero→non-zero approve?

## 11. Front-running / MEV

- [ ] Can a pending tx be sandwiched for profit at the user's expense?
- [ ] Is there a commit-reveal or slippage guard where ordering matters?
- [ ] Can an attacker front-run initialization, a first deposit, or a claim?

## 12. General Solidity Hygiene

- [ ] Uninitialized storage pointers; `delete` on structs with mappings.
- [ ] `block.timestamp` / `blockhash` used as randomness? (miner/validator-influenced)
- [ ] Return values of low-level `call`/`send` checked?
- [ ] Correct handling of `address(this).balance` vs. accounting variables.
- [ ] Events emitted for every state change (for off-chain integrity)?

---

## Coverage tracking

For each engagement, copy this checklist into your audit notes and mark each item
per contract. The goal is not to "pass" — it is to have consciously *looked* at
every category on every entry point, and recorded what you found.
