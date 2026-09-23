# CLAUDE.md — Working in SmartCon

This repository is a **smart-contract bug bounty methodology and toolkit**. When you
(Claude Code) are asked to audit, review, or hunt for vulnerabilities in an EVM smart
contract in this repo, follow the SmartCon methodology below rather than ad-hoc reading.

## The prime directive

**Process over tools. Impact first. Prove, don't claim.** Automated scanners catch
known patterns; the high-value bugs are in business logic and require the disciplined
manual pass. Every High/Critical finding must ship with a runnable PoC that reproduces
the exploit and quantifies the loss.

## Run every engagement through the six phases

Full detail in [`methodology/phases.md`](methodology/phases.md). Do not skip ahead.

1. **Recon** — read docs; write the protocol's intended invariants in plain language;
   map architecture and money flow. Output → contract inventory + invariants.
2. **Attack surface** — enumerate every `external`/`public` function (caller, effect,
   value moved, assumptions); map trust boundaries and external calls.
3. **Automated analysis** — run [`tools/scan.sh <target>`](tools/scan.sh) (add
   `MYTHRIL=1` for slow per-file symbolic execution); triage each signal (TP / FP /
   needs-check) and map it to a checklist item ID.
4. **Manual deep review** — copy [`templates/coverage-matrix.md`](templates/coverage-matrix.md)
   into the engagement, then dispatch the six hunter briefs in
   [`templates/hunters/`](templates/hunters/README.md) as parallel read-only sub-agents
   (same packet: target, scope, Phase 1 invariants, Phase 2 attack surface, Phase 3
   signals), merge their hypotheses by root cause, re-dispatch cross-cluster leads, and
   paste their coverage rows into the matrix. Tag every hypothesis with the item ID
   behind it. Alone, walk the six briefs in turn.
5. **Proof of concept** — prove it. Start from [`templates/poc/`](templates/poc/); fork
   or mock; assert quantified impact.
5b. **Verify** — hand each finding, its PoC and the in-scope source to a fresh sub-agent
   with [`templates/verify.md`](templates/verify.md) whose job is to *demote* it
   (reachability, preconditions and actors, capital and cost, PoC quality, known issues,
   independent severity, fix validity). Verdicts: CONFIRMED / DOWNGRADED / REJECTED.
   Nothing reaches Phase 6 without a verdict; downgraded findings are rewritten first.
6. **Reporting** — write it up from [`templates/report.md`](templates/report.md); rate
   severity with [`methodology/severity-classification.md`](methodology/severity-classification.md);
   cite the checklist IDs and the verification verdict.

Keep running notes in a copy of [`templates/audit-notes.md`](templates/audit-notes.md).

## The checklist is the spine

[`methodology/checklist.md`](methodology/checklist.md) has 17 categories. Each holds
SmartCon's core questions (`SC-*`) and the extended items imported from the Cyfrin /
Solodit checklist (`SOL-*`), followed by an appendix of compiler- and library-version
checks; every ID links to its description, remediation, Solodit references and the real
hacks in [`knowledge-base/case-studies/`](knowledge-base/case-studies/README.md) that
cite it ([`methodology/checklist-reference.md`](methodology/checklist-reference.md)).
Each category is linked to a deep-dive in
[`knowledge-base/vulnerabilities/`](knowledge-base/vulnerabilities/). During phases 3–4,
apply every core item to every entry point and the extended items of every category the
protocol's shape makes relevant. An unanswered checklist question is an open lead, not a
pass.

**Generated files, never edit by hand:** `methodology/checklist.md`, `checklist.json`,
`checklist-reference.md`, `templates/coverage-matrix.md`, `templates/hunters/*.md`,
`knowledge-base/case-studies/README.md`. Change
[`methodology/checklist-map.json`](methodology/checklist-map.json) (core questions,
placement of upstream items, hunter clustering) or add a case study from
[`knowledge-base/case-studies/TEMPLATE.md`](knowledge-base/case-studies/TEMPLATE.md), then
run `python3 tools/build-checklist.py`. `--check` must pass before committing.

## Tooling notes for this environment

- **Foundry** is the default for PoCs and fuzzing. [`tools/setup.sh`](tools/setup.sh)
  installs it. On restricted networks (e.g. Claude Code on the web) the Foundry/native-
  solc downloads may be blocked — see the fallback below.
- **Slither** (Phase 3) needs a `solc`. If no native solc is available, use the
  `solc-js`-backed shim demonstrated in
  [`examples/reentrancy-demo/offline-solc/`](examples/reentrancy-demo/offline-solc/):
  `PATH="$PWD/offline-solc:$PATH" slither <target> --solc-standard-json`.
- **Executing a PoC without Foundry:** compile with the `solc` npm package and run on
  `@ethereumjs/vm`, as shown in
  [`examples/reentrancy-demo/exploit.mjs`](examples/reentrancy-demo/exploit.mjs).

## Worked example to imitate

[`examples/reentrancy-demo/`](examples/reentrancy-demo/) runs Phase 3 (Slither) + Phase 5
(executed exploit) end to end via `./run.sh`, and records a real Phase 4 hunter run with
its merged result in `phase4-hunters-run.md`. Use it as the reference shape for new
findings, including the write-up in `finding-01-reentrancy.md`. The case studies under
[`knowledge-base/case-studies/`](knowledge-base/case-studies/README.md) show, for real
incidents, which checklist question would have caught the bug; read the matching one
before building a PoC for a similar hypothesis.

## Ground rules

- Only test contracts you are authorized to test (a program's scope, a contest repo, a
  testnet, or a local fork). Never run exploits against live mainnet outside a program.
- Keep per-target work under `engagements/` (git-ignored). Never commit a target's
  source or unpublished findings.
- Be honest about severity and about what a PoC does or doesn't prove.
