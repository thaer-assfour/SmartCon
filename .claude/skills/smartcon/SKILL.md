---
name: smartcon
description: Audit an EVM smart contract for vulnerabilities using the SmartCon six-phase methodology. Use whenever the user asks to audit, review, or find bugs/vulnerabilities in a Solidity/Vyper smart contract, wants a security review of on-chain code, mentions reentrancy/oracle/flash-loan/access-control/upgradeability bugs, is doing smart-contract bug bounty or audit-contest work (Immunefi, Code4rena, Sherlock, Cantina), or wants to write a smart-contract vulnerability PoC or report. Also triggers on "audit this contract", "is this contract safe", "check this Solidity for bugs".
---

# SmartCon — Smart Contract Audit

Run a disciplined, category-driven vulnerability hunt on an EVM smart contract and, for
each real finding, produce a runnable proof-of-concept and an impact-first report.

**Principles:** process over tools; impact first; prove, don't claim. Automated scanners
find known patterns — the high-value bugs are in business logic and need the manual pass.

## Inputs

The target may be: a path/address the user gives, contracts in `engagements/`, a pasted
snippet, or a repo. If the target is unclear, ask which contract(s) are in scope and
which network/commit. Also ask for the program's rules (scope, known issues, PoC
location) if this is a live bounty/contest.

## Procedure — the six phases

Work these in order. Reference files are in this repository.

1. **Recon** (`methodology/phases.md`). Read available docs/source. Write the protocol's
   **intended invariants** in plain language and map the money flow. Do not proceed until
   you can state what the contract is *supposed* to guarantee.
2. **Attack surface.** Enumerate every `external`/`public` function into a table: caller,
   effect, value moved, assumptions. Flag privileged functions and every external call.
   `slither <target> --print function-summary` helps.
3. **Automated analysis.** Run `tools/scan.sh <target>` (Slither + Aderyn + Semgrep;
   add `MYTHRIL=1` for slow per-file symbolic execution). If no native `solc`, use the
   `solc-js` shim: `PATH="$PWD/.../offline-solc:$PATH" slither <target>
   --solc-standard-json` (see `examples/reentrancy-demo/offline-solc/`). Triage every
   signal: true positive / false positive / needs-check, mapped to a checklist item ID.
4. **Manual deep review.** Copy `templates/coverage-matrix.md` into the engagement and
   walk `methodology/checklist.md` against the attack surface: first the `SC-*` core
   questions of all 17 categories, then the `SOL-*` extended items (imported from the
   Cyfrin/Solodit checklist) of every category the protocol's shape makes relevant, and
   Appendix A for the compiler/library versions in use. For each category open the
   linked `knowledge-base/vulnerabilities/*.md`, and read the linked case studies in
   `knowledge-base/case-studies/` to see what the question looked like in a real hack.
   `methodology/checklist-reference.md` has the description, remediation and Solodit
   references for every ID. Record an answer with evidence for every item in the matrix;
   `?` is an open lead, not a pass. For each invariant from Phase 1, actively construct a
   state that violates it. Log hypotheses with the item ID that produced them.
5. **Proof of concept.** For each credible hypothesis, prove it. Prefer a Foundry test
   (`templates/poc/`) against a fork; if Foundry is unavailable, compile with the `solc`
   npm package and execute on `@ethereumjs/vm` (pattern in
   `examples/reentrancy-demo/exploit.mjs`). Assert quantified impact (funds moved /
   invariant broken).
5b. **Verify (adversarial self-review).** Before writing anything up, try to demote every
   finding using `templates/verify.md`. Do this with a **fresh sub-agent** (Agent tool)
   that did not find the bug: give it the draft finding, the PoC, the in-scope source and
   the program rules, and instruct it to fill the rubric and return a verdict of
   CONFIRMED, DOWNGRADED (with the new severity) or REJECTED, with evidence for each
   section (reachability, preconditions and actors, capital and cost, PoC quality, known
   issues and duplicates, independent severity, fix validity). If no sub-agent is
   available, fill the rubric yourself *after* a break from the finding and answer every
   row from the code, not from memory. Only CONFIRMED findings proceed at their claimed
   severity; DOWNGRADED ones are rewritten first; REJECTED ones are recorded in the
   audit notes so the hypothesis is not re-opened. Store the record next to the finding.
6. **Report.** Write each confirmed finding from `templates/report.md`, severity per
   `methodology/severity-classification.md`. Lead with impact; include the PoC, the fix,
   the checklist item IDs that surfaced the bug and the verification verdict.

Track everything in a copy of `templates/audit-notes.md` under `engagements/<target>/`.

## Output

- A short summary: contracts reviewed, categories covered, and findings by severity.
- For each finding: a filled `report.md` and a runnable PoC.
- Be explicit about coverage: attach the filled coverage matrix (which items were
  answered for which contracts, and what was not covered for lack of time or scope). Do
  not imply completeness you didn't achieve.
- For every finding, the verification record (`templates/verify.md`) and its verdict.

## Rules of engagement

Only audit contracts the user is authorized to test. Never run exploits against live
mainnet outside an authorized program. Keep target source and unpublished findings under
`engagements/` (git-ignored). Rate severity honestly.

## Reference example

`examples/reentrancy-demo/` is a complete worked run (Phase 3 Slither detection + Phase 5
executed exploit + Phase 6 report). Imitate its shape. `knowledge-base/case-studies/`
holds post-mortems of real hacks mapped to checklist IDs; when a hypothesis resembles one,
read it before building the PoC.

## Maintaining the checklist

`methodology/checklist.md`, `checklist.json`, `checklist-reference.md`,
`templates/coverage-matrix.md` and `knowledge-base/case-studies/README.md` are generated.
Edit `methodology/checklist-map.json` (core questions, placement of upstream items) or add
a case study, then run `python3 tools/build-checklist.py`; `--check` verifies everything
is current and every case study cites valid categories and IDs.
