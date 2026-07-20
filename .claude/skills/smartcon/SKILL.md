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
3. **Automated analysis.** Run `tools/scan.sh <target>` (Slither + Aderyn + Semgrep). If
   no native `solc`, use the `solc-js` shim: `PATH="$PWD/.../offline-solc:$PATH" slither
   <target> --solc-standard-json` (see `examples/reentrancy-demo/offline-solc/`). Triage
   every signal: true positive / false positive / needs-check, mapped to a checklist
   category.
4. **Manual deep review.** Walk `methodology/checklist.md` (17 categories) against the
   attack surface. For each category, open the linked
   `knowledge-base/vulnerabilities/*.md` and ask its questions against the code. For each
   invariant from Phase 1, actively construct a state that violates it. Log hypotheses.
5. **Proof of concept.** For each credible hypothesis, prove it. Prefer a Foundry test
   (`templates/poc/`) against a fork; if Foundry is unavailable, compile with the `solc`
   npm package and execute on `@ethereumjs/vm` (pattern in
   `examples/reentrancy-demo/exploit.mjs`). Assert quantified impact (funds moved /
   invariant broken).
6. **Report.** Write each confirmed finding from `templates/report.md`, severity per
   `methodology/severity-classification.md`. Lead with impact; include the PoC and a fix.

Track everything in a copy of `templates/audit-notes.md` under `engagements/<target>/`.

## Output

- A short summary: contracts reviewed, categories covered, and findings by severity.
- For each finding: a filled `report.md` and a runnable PoC.
- Be explicit about coverage — which checklist categories you examined and what you did
  not have time/scope to cover. Do not imply completeness you didn't achieve.

## Rules of engagement

Only audit contracts the user is authorized to test. Never run exploits against live
mainnet outside an authorized program. Keep target source and unpublished findings under
`engagements/` (git-ignored). Rate severity honestly.

## Reference example

`examples/reentrancy-demo/` is a complete worked run (Phase 3 Slither detection + Phase 5
executed exploit + Phase 6 report). Imitate its shape.
