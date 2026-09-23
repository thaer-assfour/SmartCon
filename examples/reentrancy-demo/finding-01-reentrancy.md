# [Critical] Reentrancy in `VulnerableVault.withdraw()` drains all deposits

> Example finding produced from [templates/report.md](../../templates/report.md) to
> show what a Phase 6 write-up looks like end to end.

## Summary
`VulnerableVault.withdraw()` sends ETH to the caller **before** zeroing their recorded
balance. A malicious contract re-enters `withdraw()` from its `receive()` hook while its
balance is still non-zero, withdrawing repeatedly until the vault is empty. Any user can
drain **100% of all deposited funds** for the cost of a single 1-wei-scale deposit.

## Severity
**Critical** — direct theft of the entire pool of user funds, callable by anyone, with
no special preconditions. See
[severity-classification.md](../../methodology/severity-classification.md).

## Affected code
- **Contract / file:** `contracts/Vault.sol`
- **Function:** `withdraw()`
- **Lines:** `21–29`

```solidity
function withdraw() external {
    uint256 amount = balances[msg.sender];
    require(amount > 0, "nothing to withdraw");

    (bool ok, ) = msg.sender.call{value: amount}(""); // <-- interaction FIRST
    require(ok, "transfer failed");

    balances[msg.sender] = 0;                          // <-- effect TOO LATE
}
```

## Vulnerability details
Checks-Effects-Interactions is violated: the external call (`msg.sender.call{value:}`)
executes before `balances[msg.sender]` is set to zero. Because the call hands control to
attacker code, the attacker re-enters `withdraw()` while their recorded balance is still
the original amount, so the `require(amount > 0)` check passes again and another transfer
is made. This repeats until the vault's ETH is exhausted.

Class: [reentrancy](../../knowledge-base/vulnerabilities/reentrancy.md),
[checklist §1](../../methodology/checklist.md#1-reentrancy--notes).

## Exploit scenario (step by step)
1. Honest users deposit (in the PoC: 15 ETH total).
2. Attacker deploys `Attacker` with a 1 ETH stake and calls `attack()`.
3. `attack()` deposits 1 ETH, then calls `withdraw()`.
4. The vault sends 1 ETH to the attacker; the attacker's `receive()` re-enters
   `withdraw()` before the balance is zeroed.
5. Reentry repeats until the vault is drained. Attacker ends with the whole pool.

## Proof of Concept
Runnable, executed on a real in-process EVM (`@ethereumjs/vm`):

```bash
node exploit.mjs
```

```
Vault balance   : 15 ETH  ->  0 ETH
Attacker balance: 1 ETH  ->  16 ETH
Attacker net gain: 15 ETH (staked 1 ETH, walked away with the vault)
EXPLOIT CONFIRMED: reentrancy drained the vault. Severity: Critical.
```

**Measured impact:** attacker net profit = 15 ETH from a 1 ETH stake; 100% of deposits
stolen.

## Recommended fix
Apply Checks-Effects-Interactions (update state before the call) and add a reentrancy
guard:

```solidity
function withdraw() external nonReentrant {
    uint256 amount = balances[msg.sender];
    require(amount > 0, "nothing to withdraw");

    balances[msg.sender] = 0;                          // effect BEFORE interaction
    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok, "transfer failed");
}
```

- Zero the balance before sending (CEI).
- Inherit OpenZeppelin `ReentrancyGuard` and mark state-changing functions `nonReentrant`.

## References
- Checklist items: `SC-REEN-1` (external call before state update), `SC-REEN-4`
  (`receive()` callback window), `SOL-EC-13` (checks-effects-interactions);
  see [checklist-reference.md](../../methodology/checklist-reference.md).
- Similar incidents: [Rari Capital / Fei Fuse, 2022-04-30](../../knowledge-base/case-studies/2022-04-30-rari-fei-fuse-reentrancy.md)
  (the same inverted ordering in a Compound fork's `borrow`).
- [Reentrancy knowledge base](../../knowledge-base/vulnerabilities/reentrancy.md)
- Slither confirmed this automatically (`reentrancy-eth`) — see `slither-report.txt`.
