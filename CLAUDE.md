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
3. **Automated analysis** — run [`tools/scan.sh <target>`](tools/scan.sh); triage each
   signal (TP / FP / needs-check) and map it to a checklist category.
4. **Manual deep review** — walk [`methodology/checklist.md`](methodology/checklist.md)
   category by category against the attack surface; for each invariant, try to break it.
5. **Proof of concept** — prove it. Start from [`templates/poc/`](templates/poc/); fork
   or mock; assert quantified impact.
6. **Reporting** — write it up from [`templates/report.md`](templates/report.md); rate
   severity with [`methodology/severity-classification.md`](methodology/severity-classification.md).

Keep running notes in a copy of [`templates/audit-notes.md`](templates/audit-notes.md).

## The checklist is the spine

[`methodology/checklist.md`](methodology/checklist.md) has 17 categories, each linked to
a deep-dive in [`knowledge-base/vulnerabilities/`](knowledge-base/vulnerabilities/).
During phases 3–4, apply every category to every entry point. An unanswered checklist
question is an open lead, not a pass.

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
(executed exploit) end to end via `./run.sh`. Use it as the reference shape for new
findings, including the write-up in `finding-01-reentrancy.md`.

## Ground rules

- Only test contracts you are authorized to test (a program's scope, a contest repo, a
  testnet, or a local fork). Never run exploits against live mainnet outside a program.
- Keep per-target work under `engagements/` (git-ignored). Never commit a target's
  source or unpublished findings.
- Be honest about severity and about what a PoC does or doesn't prove.
