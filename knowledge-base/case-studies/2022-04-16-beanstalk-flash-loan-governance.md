# Case Study: Beanstalk Farms — Flash-Loaned Supermajority via emergencyCommit

## Summary
- **Protocol:** Beanstalk Farms (algorithmic stablecoin, on-chain BIP governance over a Diamond)
- **Date:** 2022-04-16
- **Chain:** Ethereum
- **Loss:** ~$182M drained from the protocol (attacker net profit ~$76M / 24,830 ETH)
- **Vulnerability class:** [Governance Attacks](../vulnerabilities/governance.md)
- **Checklist categories:** governance, flash-loans
- **Checklist items:** SC-GOV-1, SC-GOV-2, SC-GOV-3, SC-FLASH-2, SOL-Timelock-1
- **Root cause in one sentence:** `emergencyCommit` executed a BIP one day after proposal once it reached a two-thirds supermajority measured against current Stalk, with no past-block snapshot and no post-pass timelock, so an attacker flash-loaned ~$1B, deposited into the Silo to mint over 67% of voting power atomically, and executed a malicious `diamondCut` that swept the Silo in a single transaction.
- **Attack tx:** https://etherscan.io/tx/0xcd314668aaa9bbfebaf1a0bd2b6553d01dd58899c508d4729fa7311dc5d33ad7 (exploit); https://etherscan.io/tx/0x68cdec0ac76454c3b0f7af0b8a3895db00adf6daaf3b50a99716858c4fa54c6f (BIP-18 proposal)
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-04/Beanstalk_exp.sol

## Background
Beanstalk is governed by BIPs (Beanstalk Improvement Proposals) executed against an EIP-2535 Diamond.
Voting power is Stalk, earned by depositing assets into the Silo. A BIP can be committed either after a
normal voting window or, faster, through `emergencyCommit`, which executes a BIP once it is at least
one day old and has reached a two-thirds supermajority. The intended assumption was economic: acquiring
a two-thirds Stalk majority requires holding a large deposit, which nobody could do briefly and
reversibly. That assumption is exactly what flash loans erase. The invariant that failed: a proposal's
support must reflect durable stake, and execution must leave time for the community to react.

## The vulnerability
Two governance design choices combine into a single-transaction takeover. First, voting weight is read
from current Stalk, which is minted the instant assets are deposited into the Silo, rather than from a
snapshot at a past block. Second, `emergencyCommit` executes immediately upon reaching the supermajority
(subject only to the one-day proposal age), with no post-pass timelock. Conceptually (simplified):

```solidity
function emergencyCommit(uint32 bip) external {
    require(block.timestamp >= proposalTime[bip] + 1 days, "not old enough");   // 1-day age only
    require(isActive(bip) && !executed[bip], "invalid");
    // supermajority measured against CURRENT total Stalk, no snapshot at a past block
    require(votedStalk[bip] * 3 >= totalStalk() * 2, "no supermajority");
    _execute(bip);   // runs the BIP's diamondCut + init: can call ANY facet / move ANY asset
}
```

Because the proposal only needs to be one day old and the supermajority is computed on live Stalk, an
attacker who can mint a majority of Stalk within the committing transaction passes every check at once.
The BIP's execution is an arbitrary `diamondCut` with an init call, so it can transfer the entire Silo.

## The exploit, step by step
1. One day earlier (proposal tx `0x68cdec0a...`), the attacker deposited some BEAN and proposed the
   malicious **BIP-18** (`InitBip18` at `0xE5eCF73603...`), whose init transfers the Silo's assets to
   the attacker. A decoy **BIP-19** (a $250K Ukraine donation, deliberately labeled to resemble BIP-18)
   was proposed as social camouflage. Now the one-day clock is running.
2. In the exploit tx (`0xcd314668...`), flash-loan roughly $1B: 350M DAI, 500M USDC, 150M USDT from
   Aave, plus BEAN and LUSD sourced via Uniswap and SushiSwap.
3. Convert the borrowed stables into Curve LP: add liquidity to 3pool, then to the BEAN:3CRV and
   BEAN:LUSD metapools, obtaining large amounts of BEAN3CRV-f and BEANLUSD-f.
4. Deposit those LP tokens into the Silo. This mints a huge amount of Stalk in the same transaction,
   giving the attacker well over the two-thirds threshold (reported around 79% of voting power).
5. Call `emergencyCommit(18)`. The BIP is one day old and now has a supermajority, so it executes: the
   `diamondCut` init sweeps the Silo's assets to the attacker.
6. Withdraw and unwind the LP positions, repay all flash loans with fees, and keep the difference:
   ~$76M (24,830 ETH). Route ~$250K USDC to a Ukraine donation address, launder the rest through
   Tornado Cash.

## Why it worked
Every individual check in `emergencyCommit` passed. The design trusted that a two-thirds Stalk majority
could not be assembled cheaply or transiently, but flash loans provide unlimited transient capital, and
Silo deposits convert that capital into Stalk atomically. With voting weight read live rather than
snapshotted, and with execution firing the moment quorum is met, there is no window in which the
borrowed majority ceases to count. The PoC reproduces this end to end, using its own `sweep()` as the
BIP init to demonstrate the `diamondCut` moving Silo assets out. This is a governance-design failure,
not a coding bug, so no line-level scanner flags it; it surfaces only by modeling "can borrowed capital
reach quorum in one transaction?"

## The fix
Snapshot voting power at a past block and enforce a real timelock between passing and execution:

```solidity
// Snapshot: borrowed tokens deposited AFTER the proposal block carry no weight
uint256 weight = stalk.getPastVotes(voter, proposal.startBlock);   // ERC20Votes-style checkpoint
// Timelock: mandatory delay so the community can react before execution
require(block.timestamp >= proposal.passedAt + TIMELOCK_DELAY, "timelocked");
```

Beanstalk removed on-chain governance after the hack, moving to a multisig, and relaunched later in
2022 following fresh audits (Halborn and Trail of Bits). Snapshot voting plus timelocks are now the
baseline defense against this class.

## Lessons for the checklist
- **SC-GOV-1** (is voting power snapshotted at a past block?): no; it was read from current Stalk, which
  a same-tx Silo deposit inflates. Answering this exposes the flash-loan vector immediately.
- **SC-GOV-2** (timelock between pass and execute?): `emergencyCommit` executed on quorum with only a
  one-day proposal age and no post-pass delay, leaving zero reaction time.
- **SC-GOV-3** (can a flash loan reach quorum atomically?): yes, ~$1B of borrowed capital minted a
  supermajority of Stalk in one transaction.
- **SC-FLASH-2** (are votes/ratios read at an atomically inflatable point?): Stalk is minted on deposit,
  so voting weight is inflatable within the committing transaction.
- **SOL-Timelock-1** (timelocks for important changes): a treasury-moving `diamondCut` had no timelock;
  this item demands one on exactly such changes.
- **Proposed new question:** "Is governance voting weight taken from a snapshot strictly before the
  proposal existed, AND is there a mandatory delay between a proposal passing and its execution, such
  that no deposit or flash loan made during the committing transaction can influence the outcome?"

## References
- Post-mortem: rekt.news "Beanstalk"; CertiK "Revisiting Beanstalk Farms Exploit"; Omniscia
  post-mortem; PeckShield thread.
- Transaction(s): proposal 0x68cdec0ac76454c3b0f7af0b8a3895db00adf6daaf3b50a99716858c4fa54c6f; exploit
  0xcd314668aaa9bbfebaf1a0bd2b6553d01dd58899c508d4729fa7311dc5d33ad7; malicious BIP-18 contract
  0xE5eCF73603D98A0128F05ed30506ac7A663dBb69.
- Related audits / similar incidents: Tornado Cash governance (2023-05-20) is the related case where
  the proposal's code was swapped after review via a metamorphic CREATE2 + selfdestruct contract
  (checklist SC-GOV-5, "can proposal code change between vote and execution"), a different governance
  failure mode worth pairing with this one when reviewing proposal execution paths.
