# Case Study: Umbrella Network — Unchecked Subtraction in StakingRewards.withdraw

## Summary
- **Protocol:** Umbrella Network (StakingRewards, a Synthetix-style staking fork)
- **Date:** 2022-03-20
- **Chain:** Ethereum (also exploited on BSC)
- **Loss:** ~$700K
- **Vulnerability class:** [Arithmetic & Precision](../vulnerabilities/arithmetic-and-precision.md)
- **Checklist categories:** arithmetic-and-precision
- **Checklist items:** SC-MATH-1, SOL-Basics-Math-7, SOL-Basics-Math-12
- **Root cause in one sentence:** `withdraw` subtracted the requested amount from the caller's balance without SafeMath in a pre-0.8 contract, so requesting more than staked underflowed `_balances[user]` to a near-`2**256` value instead of reverting, and the contract then transferred out staking tokens the attacker never deposited.
- **Attack tx:** https://etherscan.io/tx/0x33479bcfbc792aa0f8103ab0d7a3784788b5b0e1467c81ffbed1b7682660b4fa (Ethereum); https://bscscan.com/tx/0x784b68dc7d06ee181f3127d5eb5331850b5e690cc63dd099cd7b8dc863204bf6 (BSC)
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-03/Umbrella_exp.sol

## Background
Umbrella's `StakingRewards` (contract `0xB3FB1D01B07A706736Ca175f827e4F56021b85dE`) is a fork of the
widely used Synthetix `StakingRewards`: users stake a Uniswap LP token
(`0xB1BbeEa2dA2905E6B0A30203aEf55c399C53D042`), accrue rewards, and later withdraw the same LP. The
core invariant is trivial and universal: `withdraw(amount)` must never return more than the caller
staked, because `_balances[user]` is meant to be a floor of zero. The Synthetix original enforces this
with SafeMath's `.sub`, whose subtraction reverts on underflow. Umbrella's fork removed that guard.

## The vulnerability
The deployed `_withdraw` subtracted without SafeMath, with a comment asserting it was safe (from the
PoC's quoted snippet of the vulnerable source):

```solidity
function _withdraw(uint256 amount, address user, address recipient)
    internal nonReentrant updateReward(user)
{
    require(amount != 0, "Cannot withdraw 0");
    // not using safe math, because there is no way to overflow if stake tokens not overflow
    _totalSupply    = _totalSupply - amount;
    _balances[user] = _balances[user] - amount;   // <-- underflows when amount > balance
    // ... stakingToken.transfer(recipient, amount);   // sends out `amount` LP tokens
}
```

The contract is compiled with Solidity < 0.8, so arithmetic wraps silently rather than reverting.
With `_balances[user] == 0` and a large `amount`, `_balances[user] - amount` does not revert; it
becomes an enormous positive number. The only guard, `require(amount != 0)`, does nothing to stop an
over-withdrawal. Execution proceeds to the LP `transfer(recipient, amount)`, paying out tokens the
attacker never deposited. The author's comment is the bug: it reasons about overflow of the stake
total while ignoring that a subtraction from a zero balance underflows.

## The exploit, step by step
1. From an attack contract with zero staked balance, call `StakingRewards.withdraw(8792873290680252648282)`
   (about 8,792 LP tokens in wei).
2. `_balances[msg.sender] - amount` underflows to a value near `2**256`, so no revert occurs and the
   internal accounting is silently corrupted rather than rejecting the call.
3. The function transfers `amount` of the Uniswap LP token from the pool to the attacker, draining the
   staked LP without any prior deposit.
4. Unwrap / sell the LP for the underlying assets. The same flawed contract existed on BSC and was
   drained by an equivalent transaction. Total ~$700K.

## Why it worked
Under Solidity < 0.8, an unchecked subtraction is a wrapping operation, not a safe one. Synthetix's
original code is safe precisely because it uses `SafeMath.sub`; the fork's hand-optimization ("no way
to overflow") replaced a reverting subtraction with a wrapping one and removed the implicit
`amount <= balance` guard that `.sub` provides. A single line comment reveals the mistaken mental
model. Because the code compiles and passes normal-path tests (honest users never withdraw more than
they staked), the flaw only appears when someone deliberately supplies `amount > balance`, which
adversarial input or a simple fuzz of `withdraw` would find instantly.

## The fix
On pre-0.8 code, restore SafeMath; on 0.8+, the built-in checked subtraction reverts on underflow, so
the same code would have been safe:

```solidity
// pre-0.8: revert on underflow
_balances[user] = _balances[user].sub(amount);   // SafeMath: reverts if amount > balance
// 0.8+: checked arithmetic reverts automatically, or make the guard explicit
require(amount <= _balances[user], "withdraw exceeds balance");
_balances[user] -= amount;
```

## Lessons for the checklist
- **SC-MATH-1** (reachable unchecked over/underflow): the subtraction is reachable with attacker-chosen
  `amount > balance`; asking "is this underflow reachable?" answers yes and ends the audit of this
  function.
- **SOL-Basics-Math-7** (under/overflow behavior, including that 0.8+ reverts): flags every add/sub for
  how it behaves on boundary values; here it shows the pre-0.8 subtraction wraps silently instead of
  reverting, which the same code would not do on 0.8+.
- **SOL-Basics-Math-12** (subtractions guarded against underflow / SafeMath usage on arithmetic):
  directly targets the removed SafeMath call; the deviation from the Synthetix reference is the finding.
- **Proposed new question:** "In any pre-0.8 contract or `unchecked` block, does every subtraction have
  an explicit `a >= b` guard (or SafeMath), and does a code comment claiming an operation 'cannot
  overflow' actually hold for the underflow direction too?"

## References
- Post-mortem: Uno Re "Umbrella Network hacked, $700k lost" (Medium).
- Transaction(s): Ethereum 0x33479bcfbc792aa0f8103ab0d7a3784788b5b0e1467c81ffbed1b7682660b4fa;
  BSC 0x784b68dc7d06ee181f3127d5eb5331850b5e690cc63dd099cd7b8dc863204bf6. Attacker
  0x1751e3e1aaf1a3e7b973c889b7531f43fc59f7d0; attack contract
  0x89767960b76b009416bc7ff4a4b79051eed0a9ee.
- Related audits / similar incidents: a recurring "fork removed SafeMath" class in pre-0.8 forks;
  the safest posture is to diff a fork against its reference implementation for stripped guards.
