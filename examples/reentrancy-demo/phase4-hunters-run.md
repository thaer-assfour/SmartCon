# Phase 4 — recorded run of the six parallel hunters

A real run of the [hunter briefs](../../templates/hunters/README.md) against
[`contracts/Vault.sol`](contracts/Vault.sol), executed as six parallel read-only
sub-agents from the `/smartcon` skill (branch `claude/web3-audit-github-projects-q8l4z3`,
2026-09-23). Kept here as the reference shape of a merged Phase 4 result: what the
packet looked like, what came back, how it was merged, and what the run taught us about
the briefs. `Attacker.sol` was declared out of scope so the hunters could not read the
answer.

## The packet every hunter received

- **Target:** `contracts/Vault.sol` (`VulnerableVault`, Solidity `^0.8.24`), one contract, no
  known issues, severity per [`severity-classification.md`](../../methodology/severity-classification.md).
- **Phase 1 invariants:** (I1) outside of a call, Σ `balances[user]` equals
  `address(this).balance`; (I2) a user withdraws at most what they deposited; (I3) no admin,
  no upgrade path, no external dependency, ETH is the only asset.
- **Phase 2 attack surface:** `deposit()` payable, anyone, `balances[msg.sender] += msg.value`;
  `withdraw()` anyone with a balance, sends the whole balance with `call` then zeroes it;
  `totalETH()` view; `balances(address)` getter.
- **Phase 3 signals:** Slither `reentrancy-eth` on `withdraw()` (given only to the
  callbacks hunter, whose categories it falls into).
- **Time budget:** about 15 minutes of work per hunter.

## What came back

| Hunter | Hypotheses | Core items answered | `?` left | Leads handed on | Contract honoured |
|--------|-----------:|--------------------:|---------:|----------------:|:-----------------:|
| callbacks-and-liveness | 3 (Critical, Low, Info) | 14 / 14 | 1 | 2 | yes |
| accounting-and-math | 2 (Low, Info) | 14 / 14 | 0 | 4 | yes |
| tokens-and-oracles | 2 (Critical as secondary owner, Info) | 13 / 13 | 0 | 5 | yes |
| privilege-and-upgrade | 0 | 22 / 22 | 0 | 6 | yes |
| economics-and-ordering | 0 | 11 / 11 | 0 | 1 | yes |
| boundaries-and-inputs | 5 (Low ×2, Info ×3) | 19 / 19 | 1 | 6 | yes |

All 93 core items were answered with `file:line` evidence for the single in-scope
contract. The two `?` rows (gas forwarding on the `call`; state written after the
interaction) both resolve into finding F1 below.

## Merged findings (deduplicated by root cause)

| # | Finding | Root cause | Severity | Raised by | Checklist items |
|---|---------|-----------|----------|-----------|-----------------|
| F1 | `withdraw()` sends ETH to `msg.sender` (`Vault.sol:25`) before zeroing the balance (`:28`); a contract's `receive()` re-enters and drains every other depositor's ETH. Two more symptoms of the same ordering fold into it: views are inconsistent mid-callback (read-only reentrancy surface) and a re-deposit made inside the callback is wiped by the absolute `= 0`. | effect after interaction | **Critical** | callbacks (H1), tokens (H1); leads from privilege, economics, accounting, boundaries | SC-REEN-1, SC-REEN-3, SC-REEN-4, SC-TOKEN-4, SOL-EC-13, SOL-AM-ReentrancyAttack-1, SOL-AM-ReentrancyAttack-2, SOL-Heuristics-13, SOL-Heuristics-16, SOL-Basics-Payment-1, SOL-Basics-Payment-5 |
| F2 | No internal total: `totalETH()` returns the raw balance, ETH forced in by `selfdestruct` or block rewards is uncredited and unrecoverable (no sweep, no owner), and I1 cannot be checked on-chain. | balance-based accounting, no rescue path | Informational | tokens (H2), accounting (H1), callbacks (H3), boundaries (H3) | SC-HYG-2, SC-ORACLE-4, SC-DEFI-7, SOL-Basics-Payment-3, SOL-Basics-Payment-7, SOL-Defi-General-3, SOL-AM-DA-1 |
| F3 | A depositor whose account cannot receive ETH locks its own funds: push payment to `msg.sender` only, no recipient parameter, no partial amount. | push-only payout | Low (self-inflicted) | boundaries (H2) | SC-INPUT-6, SOL-Basics-Payment-1, SOL-EC-5 |
| F4 | No events on `deposit()` / `withdraw()`. | missing events | Low | boundaries (H1); leads from privilege, tokens, accounting | SC-HYG-3, SOL-Basics-Event-1 |
| F5 | Floating pragma `^0.8.24` with no `evmVersion` pinned; PUSH0 is emitted, so deployment to a pre-Shanghai chain fails. | build configuration | Informational | boundaries (H4) | SC-HYG-5, SOL-McCc-2, SOL-McCc-3, SOL-McCc-12 |
| F6 | `deposit()` accepts `msg.value == 0` as a silent no-op. | missing zero check | Informational | boundaries (H5); note from accounting | SC-INPUT-2, SOL-Basics-Function-5 |

F1 goes to Phase 5 ([`exploit.mjs`](exploit.mjs) is its PoC) and then to Phase 5b with a
verifier that was not a hunter. F2 to F6 are report footnotes; none moves funds.

## What the run taught us about the briefs

- **The lead mechanism works.** Five hunters that do not own reentrancy still handed the
  CEI defect to the callbacks cluster with the exact lines, so the orchestrator would have
  caught it even if the owning hunter had missed it.
- **Slugs must be given, not remembered.** Three hunters wrote another cluster's slug from
  memory (`callbacks-reentrancy-liveness`, `atomic-capital-ordering-randomness`). The
  briefs now list the exact slugs in the Leads section.
- **Restating another cluster's finding is waste.** One hunter reported the reentrancy
  under Hypotheses "to be safe". The briefs now send cross-cluster bugs to Leads unless one
  of the hunter's own items reveals them; the merge step deduplicates by root cause anyway.
- **Empty results need a shape.** Hunters with nothing to report handled the empty table
  three different ways. The briefs now say to keep the header row and write `None.` with
  one sentence.
- **Cost.** On a 34-line contract each hunter used roughly 70k tokens and two to three
  minutes; the whole Phase 4 ran in under four minutes wall-clock. Real targets will cost
  proportionally more per hunter; the time budget in the packet is what bounds it.
- **Depth beyond reading is fine.** One hunter compiled the contract in memory to confirm
  opcode-level claims (no `DELEGATECALL`, PUSH0 present). "Read-only" means the target and
  the repo are not modified and nothing runs against a live chain, not that a hunter may
  not compile or simulate.
