# Weak Randomness

## What it is
A contract needs an unpredictable value (lottery winner, NFT trait, game outcome)
but derives it from on-chain data that is either public, predictable, or influenceable
by the very actor who profits from the outcome (miners/validators, or the caller).

## Why it happens
Everything on-chain is deterministic and public. `block.timestamp`, `blockhash`,
`block.prevrandao` (post-Merge), `block.number`, and `msg.sender` are all knowable
or grindable at call time. A validator can reorder/withhold, and any caller can
compute the result in the same transaction and revert if they don't like it.

## Vulnerable patterns
```solidity
// 1. Timestamp/blockhash "randomness" — predictable and validator-influenced
uint256 winner = uint256(keccak256(abi.encodePacked(block.timestamp, block.difficulty))) % players.length;

// 2. Caller can precompute and only enter on a win
function play() external {
    uint256 r = uint256(blockhash(block.number - 1)) % 100;   // known within the tx
    if (r < 10) _payout(msg.sender);                          // attacker wraps in a contract, reverts on loss
}
```

## Secure pattern
```solidity
// Use a verifiable, tamper-resistant source: Chainlink VRF (commit + async callback)
function requestRandom() external returns (uint256 requestId) {
    requestId = COORDINATOR.requestRandomWords(keyHash, subId, confs, gasLimit, numWords);
}
function fulfillRandomWords(uint256, uint256[] memory words) internal override {
    winner = players[words[0] % players.length];   // delivered later, cannot be gamed atomically
}
```
- Use **Chainlink VRF** (or an equivalent verifiable randomness beacon) for anything
  with financial stakes.
- If using a commit-reveal scheme, ensure the reveal cannot be withheld for advantage
  and the commit is binding.
- Never use `block.*` values or `blockhash` as randomness for value-bearing outcomes.

## How to detect
- Grep for `blockhash`, `block.timestamp`, `block.prevrandao`, `block.difficulty`,
  `block.number`, `keccak256(...msg.sender...)` used to pick outcomes.
- Ask: can the caller compute the result in the same tx and revert on a loss? Can a
  validator influence it?

## Real-world
- Numerous NFT mints with "random" rarity gamed by minting from a contract that
  reverts unless the traits are rare.
- Multiple on-chain lotteries/games drained by precomputing the blockhash-based draw.

## Checklist mapping
[Checklist §13 — Weak Randomness](../../methodology/checklist.md#13-weak-randomness)
