# Case Study: LuckyTiger NFT — Predictable On-Chain "Randomness"

## Summary
- **Protocol:** LuckyTiger NFT mint
- **Date:** 2022-08-24
- **Chain:** Ethereum
- **Loss:** small and not precisely documented; impact is that the attacker mints only the winning/rare outcomes at will, defeating the mint's fairness (see note)
- **Vulnerability class:** [Weak Randomness](../vulnerabilities/randomness.md)
- **Checklist categories:** randomness
- **Checklist items:** SC-RAND-1, SC-RAND-2, SC-RAND-3, SOL-AM-MA-2
- **Root cause in one sentence:** The mint's win/rarity outcome was derived from on-chain block values (`block.difficulty`/`block.timestamp`) that the caller can read in the same transaction, so an attacker contract computes the result up front and reverts whenever it is unfavourable, letting only winning mints land.
- **Attack tx:** https://etherscan.io/tx/0x804ff3801542bff435a5d733f4d8a93a535d73d0de0f843fd979756a7eab26af
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-08/LuckyTiger_exp.sol

## Background
LuckyTiger issued NFTs through a `publicMint()` that paid out or granted a favourable
outcome based on a pseudo-random draw computed from block properties. The intended
invariant: each mint is an independent, unpredictable gamble, so a minter cannot choose to
receive only rare or paying outcomes. On a deterministic, transparent VM that invariant
cannot hold when the "randomness" is any value the caller can observe before committing.
Everything the mint used to draw a result is readable inside the same call.

## The vulnerability
The outcome is a parity check over `block.difficulty` and `block.timestamp`. The PoC and
the companion `luckyHack.sol` both reproduce the exact predicate:

```solidity
// (from the PoC / luckyHack.sol) the "random" draw the mint relied on
function getRandom() public view returns (uint256) {
    if (uint256(keccak256(abi.encodePacked(block.difficulty, block.timestamp))) % 2 == 0)
        return 0;   // lose
    else
        return 1;   // win
}
```

Two properties make this exploitable. First, `block.difficulty` and `block.timestamp` are
fixed for the whole block and readable by any contract executing in it, so the result is
known before any state-changing call is made (SC-RAND-1, SOL-AM-MA-2). Second, the mint
reverts cleanly on failure conditions, so a wrapper contract can *gate* its own mint on the
draw and abort the entire transaction when it would lose, paying only gas.

## The exploit, step by step
From `testExploit()`:
1. In the attacker contract, recompute the draw for the current block:
   `keccak256(abi.encodePacked(block.difficulty, block.timestamp)) % 2`.
2. If the value is the losing one, `revert("Not lucky")`. The whole transaction unwinds
   with no mint and no cost beyond gas (SC-RAND-2).
3. If it is the winning one, loop and call `nftAddress.publicMint{value: 0.01 ether}()`
   `amount` times (the PoC uses 10), harvesting only favourable mints; `luckyHack.sol` also
   short-circuits with `"rug away!"` once the NFT contract's balance is drained.
4. Because the attacker only ever transacts in blocks that satisfy the win condition, every
   landed mint is a win.

## Why it worked
On-chain randomness from block variables is not random to the caller: it is a public input
to their transaction. The "atomic revert on loss" trick (SC-RAND-2) turns even a fair-looking
50/50 draw into a guaranteed win, because the losing branch is simply never committed. No
external adversary or oracle is needed; the minter is the adversary. Reviewers sometimes
accept block-value randomness as "good enough for a low-value NFT", but the same trick
applies regardless of stake size, and the fairness invariant is broken either way.

Note on loss: the demonstrable harm is qualitative (the mint's rarity/payout gating is
fully controllable by the attacker). A precise dollar figure was not verifiable from a
reachable primary source in this environment; the PoC mints at 0.01 ETH each.

## The fix
Never derive a value-bearing outcome from block properties.

```solidity
// Use a verifiable, asynchronous randomness source (Chainlink VRF)
function requestMint() external returns (uint256 requestId) {
    requestId = COORDINATOR.requestRandomWords(keyHash, subId, confs, gasLimit, 1);
}
function fulfillRandomWords(uint256, uint256[] memory words) internal override {
    _finalizeMint(_requester[/*id*/], words[0]);   // delivered in a later block; cannot be gamed atomically
}
```

VRF (or a sound commit-reveal where the reveal cannot be withheld for advantage) delivers
the result in a separate transaction the caller cannot pre-check and abort, closing both the
prediction and the revert-on-loss vectors (SC-RAND-3).

## Lessons for the checklist
- **SC-RAND-1** (block vars as randomness for a value-bearing outcome): names the exact
  `block.difficulty`/`block.timestamp` draw the mint used.
- **SC-RAND-2** (caller can precompute the result in the same tx and revert on a loss):
  describes the wrapper-contract revert trick that guarantees only wins land.
- **SC-RAND-3** (VRF/commit-reveal used instead): the corrective control whose absence is
  the root cause.
- **SOL-AM-MA-2** (block properties for randomness): flags any use of block properties as a
  randomness source.
- Proposed new question: *"For any 'random' outcome, can a contract caller compute it before
  committing and abort the transaction on an unfavourable result, and is the source delivered
  in a later block it cannot pre-read?"*

## References
- Post-mortem: @1nf0s3cpt thread (twitter.com/1nf0s3cpt/status/1576117129589317633); not reachable from this environment; mechanism taken from the PoC and the referenced `0xNezha/luckyHack` source.
- Transaction(s): attack `0x804ff3801542bff435a5d733f4d8a93a535d73d0de0f843fd979756a7eab26af`; NFT contract `0x9c87A5726e98F2f404cdd8ac8968E9b2C80C0967`.
- Related audits / similar incidents: numerous NFT mints with block-hash "rarity" gamed by minting from a contract that reverts unless the traits are rare; on-chain lotteries drained by precomputing a blockhash draw.
