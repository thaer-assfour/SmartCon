# Governance Attacks

## What it is
On-chain governance lets token holders propose and execute changes. Bugs here let an
attacker seize control of the protocol's treasury or parameters — often the highest-
impact outcome possible (total protocol compromise).

## Why it happens
- Voting power read at a manipulable point (current balance) instead of a past snapshot.
- No/short timelock between a passed proposal and execution.
- Quorum/threshold too low, or reachable with borrowed or flash-loaned tokens.
- Proposal execution that can call arbitrary targets (including the treasury/upgrade).
- Delegation, double-counting, or vote-weight accounting bugs.

## Vulnerable patterns
```solidity
// 1. Voting power = current balance -> flash-loan a majority for one block
function castVote(uint256 id, bool support) external {
    uint256 weight = token.balanceOf(msg.sender);   // manipulable atomically
    _tally(id, support, weight);
}

// 2. No timelock: proposal executes in the same flow it passes
function execute(uint256 id) external { _run(proposals[id].calls); } // instant

// 3. Double-count via transfer between two accounts within a proposal window
```

## Secure pattern
```solidity
// Snapshot voting power at proposal creation (past block) — ERC20Votes checkpoints
uint256 weight = token.getPastVotes(msg.sender, proposal.startBlock);

// Enforce a timelock between success and execution so the community can react
require(block.timestamp >= proposal.eta, "timelocked");
```
- Snapshot vote weight at a **past block** (`ERC20Votes`/`getPastVotes`), defeating
  flash-loan governance.
- Require a **timelock** (e.g. 2–7 days) before execution; consider a guardian veto.
- Set quorum/thresholds meaningfully; account for delegation carefully.
- Scope what proposals can call; protect upgrade/treasury paths behind the timelock.

## How to detect
- Check whether voting power uses `balanceOf`/current supply vs. a past snapshot.
- Check for a timelock between proposal success and execution.
- Model: can I borrow enough tokens (flash loan / large holder) to pass a proposal
  in one or few blocks? (See [flash-loans](flash-loans.md).)
- Look at what `execute` is allowed to call.

## Real-world
- **Beanstalk (2022, ~$182M)** — flash-loaned governance tokens passed a malicious
  proposal that drained the protocol in a single transaction.
- Multiple DAOs with low quorum or no timelock exploited by large/borrowed positions.

## Checklist mapping
[Checklist §14 — Governance](../../methodology/checklist.md#14-governance--notes)
