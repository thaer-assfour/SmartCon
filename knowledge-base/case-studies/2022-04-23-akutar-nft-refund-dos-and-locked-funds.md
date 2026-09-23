# Case Study: Akutars (Aku Dreams) — Refund DoS and Permanently Locked Auction Proceeds

## Summary
- **Protocol:** Akutars / Aku Dreams NFT Dutch auction
- **Date:** 2022-04-23
- **Chain:** Ethereum
- **Loss:** 11,539.5 ETH (~$34M) locked forever, plus a demonstrable griefing DoS of all bidder refunds
- **Vulnerability class:** [Denial of Service](../vulnerabilities/denial-of-service.md)
- **Checklist categories:** denial-of-service
- **Checklist items:** SC-DOS-2, SC-DOS-5, SC-DOS-3, SOL-AM-DOSA-1, SOL-Basics-Payment-1, SOL-Basics-AL-12
- **Root cause in one sentence:** Refunds were pushed in a loop with a `require`-checked low-level call so one reverting bidder contract froze everyone's refund, and `claimProjectFunds` gated the proceeds on a counter comparison (`refundProgress >= totalBids`) that mixed bid-entry counts with bid-quantity counts and could never become true.
- **Attack tx:** contract at https://etherscan.io/address/0xf42c318dbfbaab0eee040279c6a2588fa01a961d (no drain tx; a whitehat demonstrated the refund DoS, and the proceeds locked themselves by design flaw)
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-04/AkutarNFT_exp.sol

## Background
Akutars ran a Dutch-auction mint. Bidders called `bid(uint8 amount)` sending ETH at
the current clearing price. After the auction the contract owed each bidder a refund
of the difference between what they paid and the final clearing price, paid by
`processRefunds()`. Once refunds were done, the team would withdraw the sale proceeds
via `claimProjectFunds()`. The intended invariant: every bidder is refunded the
overpayment, then and only then the project sweeps the remaining balance, and neither
step can be blocked by a third party.

Two independent flaws broke that invariant. One let any single bidder freeze all
refunds. The other made the proceeds withdrawal permanently unreachable, stranding
11,539.5 ETH in the contract.

## The vulnerability
The two defects sit in the refund loop and in the claim gate. The snippets below are a
simplified reconstruction from the DeFiHackLabs PoC header and the public post-mortem;
the deployed source was not fetched here, so treat the exact field names as indicative.

```solidity
// (simplified) push refunds in a loop, require each call to succeed
function processRefunds() external {
    uint256 i = refundProgress;
    uint256 end = bidIndex;                 // number of bid ENTRIES recorded
    while (i < end) {
        Bid storage b = bids[i];
        uint256 owed = (b.price - finalPrice) * b.quantity;
        (bool ok, ) = b.bidder.call{value: owed}("");   // push payment
        require(ok, "refund failed");        // BUG: one revert blocks the whole loop
        refundProgress = ++i;
    }
}

// (simplified) proceeds gated on a counter that can never reach the target
function claimProjectFunds() external onlyOwner {
    require(refundProgress >= totalBids, "refunds not done"); // BUG: mismatched counters
    (bool ok, ) = msg.sender.call{value: address(this).balance}("");
    require(ok);
}
```

Bug 1 (griefing DoS, SC-DOS-2). Refunds are *pushed*: the contract calls each bidder
and `require(ok)`. A bidder that is a contract with a reverting `receive`/`fallback`
makes that call fail, so `processRefunds()` reverts. Because the loop resumes from
`refundProgress`, every bidder queued after the malicious one is blocked forever until
the griefer relents. The PoC models exactly this: the attacker bids from a contract
whose `fallback` does `revert("CAUSE REVERT !!!")`, then shows an honest bidder who bid
*after* it never gets refunded.

Bug 2 (locked funds, SC-DOS-5). `claimProjectFunds()` required `refundProgress >= totalBids`.
`refundProgress` advances once per refund step, but `totalBids` was accumulated on a
different basis (bid quantity versus number of bid entries). Because many bidders bought
more than one Akutar, the two counters were on different scales and `refundProgress`
could never catch up to `totalBids`. The require was therefore permanently false and the
withdrawal permanently reverted. This second bug is what actually cost the 11,539.5 ETH:
even with refunds unblocked, the proceeds were unreachable.

## The exploit, step by step
1. A bidder deploys a contract with a reverting fallback and calls `bid()` from it early
   in the ordering (Bug 1). Any later refund attempt reverts on that entry.
2. `processRefunds()` cannot advance past the malicious bidder, so all subsequent honest
   bidders are frozen out of their overpayment refunds (demonstrated, not weaponized: a
   whitehat showed the freeze, then stood down).
3. Independently, `claimProjectFunds()` reverts on `require(refundProgress >= totalBids)`
   no matter what, because the two counters are incommensurable (Bug 2).
4. Net effect: 11,539.5 ETH of proceeds are stranded in the contract with no code path
   that can move them.

## Why it worked
Push payments in a loop hand liveness to the least cooperative recipient: any bidder can
veto the batch by reverting on receipt (SOL-Basics-Payment-1). The locked-funds bug is a
classic counter-mismatch in a settlement gate (SC-DOS-5): the value that increments and
the value it is compared against were defined on different units, so the terminating
condition was unreachable. Neither is a signature that a scanner flags: both require
reading the refund/claim state machine and asking "can this require ever be false forever?"
and "who can make one iteration revert?". The audit and reviewers focused on mint
correctness, not on the settlement-path liveness invariant.

## The fix
Refunds must be pull-based, and settlement gates must compare like with like.

```solidity
// (simplified) pull refunds: isolate one bidder's failure from the rest
mapping(address => uint256) public refundOwed;
function claimRefund() external {
    uint256 amt = refundOwed[msg.sender];
    refundOwed[msg.sender] = 0;
    (bool ok, ) = msg.sender.call{value: amt}("");
    require(ok, "refund failed");            // only the caller can fail their own refund
}

// gate the sweep on the SAME quantity the refund loop advances
require(refundProgress >= bidIndex, "refunds not done");
```

In reality the deployed contract could not be patched. The team raised replacement
capital to make bidders whole, and the 11,539.5 ETH remained locked in the contract.

## Lessons for the checklist
- **SC-DOS-2** (one failing external call blocks a batch, push vs pull): asks directly
  whether one recipient reverting freezes the distribution, which is Bug 1 verbatim.
- **SC-DOS-5** (can a require in a refund/claim/settlement path be made permanently false
  by a counter mismatch): asks whether `claimProjectFunds`'s guard can ever hold, which is
  Bug 2 verbatim.
- **SC-DOS-3** (griefing via gas/queue/locking): the reverting bidder is a queue-locking
  griefer; the question surfaces it.
- **SOL-AM-DOSA-1** (withdrawal pattern): mandates pull over push, which removes Bug 1.
- **SOL-Basics-Payment-1** (receiver can revert): names the exact mechanism the attacker
  used to freeze the loop.
- **SOL-Basics-AL-12** (batch fund transfer loop): flags the unbounded push loop as the
  structure at risk.
- Proposed new question: *"For every settlement gate `require(counterA >= counterB)`, are
  `counterA` and `counterB` incremented on the same unit and in the same code path, so the
  condition is guaranteed to become satisfiable?"*

## References
- Post-mortem: BlockSec, "How Akutar NFT Loses $34M USD" (blocksecteam.medium.com/how-akutar-nft-loses-34m-usd-60d6cb053dff) — not reachable from this environment; mechanism taken from the PoC header.
- Transaction(s): auction-end / refund tx `0x62d280abc60f8b604175ab24896c989e6092e496ac01f2f5399b2a62e9feaacf` (referenced in the PoC); contract `0xf42c318dbfBaab0EEE040279C6a2588Fa01a961d`.
- Related audits / similar incidents: GovernMental and King-of-the-Ether push-payment DoS; any batch airdrop bricked by one reverting recipient.
