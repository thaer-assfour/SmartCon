# The Six Phases

This is the backbone of SmartCon. Every engagement runs through these phases in
order. Earlier phases produce artifacts that later phases consume, so do not skip
ahead — a weak attack-surface map produces a shallow review. Between the PoC and the
report sits a mandatory gate, **Phase 5b — Verify**, where a fresh pair of eyes tries
to demote every finding before it is written up.

---

## Phase 1 — Recon

**Goal:** Understand what the protocol is supposed to do, where the value is, and
which contracts hold or move it. You cannot find a logic bug in a system you do
not understand.

**Do:**

- Read the docs, whitepaper, and README. Note the *intended* invariants in plain
  language (e.g. "total shares always equal total deposits", "only the timelock
  can upgrade", "1 share is never worth less than 1 underlying").
- Map the contract architecture: which contract calls which, who owns whom,
  proxy/implementation pairs, factories and their children.
- Identify the **money flow**: where funds enter, where they are stored, where they
  leave, and who is allowed to move them.
- Note the deployment: mainnet addresses, TVL (value at risk), compiler version,
  external dependencies (OpenZeppelin, Solmate, Chainlink, Uniswap).
- Read the program's scope and rules: in-scope contracts, severity model, PoC
  requirements, known issues (do not report these).

**Output:** An architecture map and a contract inventory with a one-line purpose
per contract, plus a written list of intended invariants.

**Tools:** protocol docs, block explorers, `cast`, [`scripts/recon.sh`](../scripts/recon.sh),
Tenderly.

---

## Phase 2 — Attack Surface Mapping

**Goal:** Turn the codebase into a concrete list of things an attacker can touch.

**Do:**

- Enumerate every `external` / `public` function. For each, record: who can call
  it, what it changes, what value it moves, and what it assumes about state.
- Map **trust boundaries**: `onlyOwner` / role-gated functions, and — more
  importantly — functions that are *supposed* to be gated but aren't.
- List every **external call** (`call`, `delegatecall`, token transfers, oracle
  reads, callbacks). These are where reentrancy, untrusted-return-value, and
  price-manipulation bugs live.
- Identify **value-moving paths** end to end: deposit → mint, redeem → transfer,
  liquidate → seize, claim → payout.
- Identify **privileged actors** and ask: what is the worst thing each can do, and
  what happens if their key is compromised or malicious?

**Output:** An attack-surface map — a table of entry points annotated with
caller, effect, value moved, and assumptions. This directly drives the checklist.

**Tools:** `slither --print function-summary`, `slither --print human-summary`,
Solidity Visual Developer, hand-drawn call graphs.

---

## Phase 3 — Automated Analysis

**Goal:** Cheaply catch the *known* patterns so manual time is spent on logic.

**Do:**

- Run [`tools/scan.sh`](../tools/scan.sh): Slither, Aderyn, and Semgrep Solidity
  rules over the target; `MYTHRIL=1` adds per-file Mythril symbolic execution (slow,
  worth it on small cores with arithmetic or access-control complexity).
- Triage every finding: **true positive**, **false positive**, or **needs manual
  confirmation**. Do not trust or dismiss blindly — each detector output is a
  *lead*, not a verdict.
- Stand up property-based fuzzing where invariants are known (Foundry invariant
  tests, Echidna/Medusa) to try to break the invariants you wrote down in Phase 1.

**Output:** A triaged list of signals, each mapped to a checklist item ID
([`checklist.md`](checklist.md)) and marked with a confidence level.

**Tools:** Slither, Aderyn, Semgrep, Foundry (`forge test`, invariant testing),
Echidna / Medusa, Mythril (targeted symbolic execution).

> Automated tools are necessary but never sufficient. Their real value here is
> *coverage of the boring stuff* so your attention is free for the interesting stuff.

---

## Phase 4 — Manual Deep Review

**Goal:** Find the business-logic and edge-case bugs that tools cannot. This is
where Critical findings come from.

**Do:**

- Copy [`templates/coverage-matrix.md`](../templates/coverage-matrix.md) into the
  engagement. Then split the review across the six **hunters** in
  [`templates/hunters/`](../templates/hunters/README.md): each brief owns a cluster of
  related checklist categories (callbacks and liveness; accounting and math; tokens and
  oracles; privilege, upgrades, governance and signatures; atomic capital, ordering and
  randomness; inputs, cross-chain boundaries and hygiene) and carries that cluster's
  `SC-*` core and `SOL-*` extended items, notes and case studies. Give every hunter the
  same packet (target, scope, Phase 1 invariants, Phase 2 attack surface, Phase 3
  signals, time budget) and run them at the same time, as sub-agents or as teammates,
  without letting them see each other's output. Working alone, walk the six briefs in
  turn; the output contract is the same.
- Every hunter answers every core item of its categories for every in-scope contract
  with evidence, walks the extended items the protocol's shape makes relevant, and
  Appendix A for the compiler and library versions in use. A `?` is an open lead.
  [`checklist-reference.md`](checklist-reference.md) carries the description,
  remediation and Solodit references behind every ID, and the linked
  [case studies](../knowledge-base/case-studies/README.md) show what each question
  looked like in a real incident.
- **Merge**: deduplicate hypotheses by root cause (one missing check, one finding),
  rank by impact × confidence, send each "lead for other hunters" to the cluster it
  names, paste every coverage row into the matrix, and close any core item nobody
  answered yourself.
- For each intended invariant from Phase 1, actively try to construct a state that
  violates it. Think like an attacker who controls the calldata, the ordering, and
  can supply malicious tokens/contracts.
- Trace **rounding and precision** through every division. Who benefits from the
  rounding direction? Can it be amplified by repetition or by a tiny first deposit?
- Model **adversarial composition**: flash loans, reentrancy across contracts,
  sandwiching, first-depositor, donation attacks, and integration with weird ERC-20s
  (fee-on-transfer, rebasing, missing return values, ERC-777 hooks).
- Keep a running hypotheses log in [`templates/audit-notes.md`](../templates/audit-notes.md):
  each suspected issue, the assumption it breaks, and how you'd test it.

**Output:** A ranked list of vulnerability hypotheses, each tagged with the checklist
item ID that produced it, a rough impact and a plan to prove it; plus the filled
coverage matrix.

**Tools:** your eyes, the checklist, the knowledge base, `cast`/Tenderly for state
inspection, Foundry for quick experiments.

---

## Phase 5 — Proof of Concept

**Goal:** Prove the finding is real and quantify the impact. A hypothesis without a
PoC is a guess; programs reward proofs.

**Do:**

- Start from [`templates/poc/`](../templates/poc/). Fork the relevant network at a
  pinned block (`vm.createSelectFork`) so you exploit the *real* deployed state, or
  build minimal mocks when forking isn't allowed.
- Write the smallest test that demonstrates the exploit and asserts the damage
  (attacker balance up, protocol invariant broken, victim funds gone).
- Quantify: how much can be stolen/frozen, under what preconditions, and at what
  cost to the attacker.
- Respect program rules: many require the PoC on a testnet or private fork, never
  against live mainnet.

**Output:** A runnable Foundry test that reproduces the exploit and asserts impact,
plus the measured loss.

**Tools:** Foundry (`forge test --fork-url ... -vvvv`), `cast`, Tenderly simulations.

---

## Phase 5b — Verify

**Goal:** Try to kill your own finding before a triager does. Most "Critical" reports
that get closed as Low or Invalid fail on preconditions, on an out-of-scope actor, or on
a PoC that proves less than the report claims. Catching that here costs an hour; on the
platform it costs reputation.

**Do:**

- For every finding with a PoC, fill a copy of [`templates/verify.md`](../templates/verify.md).
  The verifier should be someone (or a fresh agent) who did not find the bug, with only
  the draft finding, the PoC, the in-scope source and the program rules.
- Work the rubric in order: **reachability** in the deployed configuration;
  **preconditions and actors** (trusted role acting maliciously? victim acting
  irrationally? exotic token or market state?); **capital, cost and profit** (is it
  flash-loanable, does profit survive gas and slippage, is it repeatable?); **PoC
  quality** (real state or unmodified in-scope code, quantified assertions, cheat-codes
  only in setup); **known issues and duplicates** (program scope, prior audits, Solodit);
  **severity re-derived independently** from [`severity-classification.md`](severity-classification.md);
  **fix validity** (re-run the PoC against the patch).
- Record the verdict: **CONFIRMED** (proceed as claimed), **DOWNGRADED** (rewrite
  Summary and Severity first) or **REJECTED** (log the reason in the audit notes so the
  hypothesis is not re-opened). New hypotheses discovered while verifying go back to
  Phase 4.

**Output:** One verification record per finding, and a findings list where every
severity has been derived twice.

**Tools:** the rubric, a fresh reviewer or sub-agent, the PoC, the program's scope page.

---

## Phase 6 — Reporting

**Goal:** Communicate the finding so a triager can validate it in minutes and a
developer can fix it correctly.

**Do:**

- Use [`templates/report.md`](../templates/report.md). Lead with **impact**, then
  the vulnerable code, the step-by-step exploit, the PoC, and a concrete fix.
- Assign severity using [`severity-classification.md`](severity-classification.md).
  Be honest — over-claiming severity burns credibility.
- Include the exact file, function, and line references, and the commit/deployment
  you reviewed; cite the checklist item IDs that surfaced the bug and attach the
  Phase 5b verdict.
- Follow **responsible disclosure**: report privately through the program's channel,
  never disclose publicly before a fix, and never exploit beyond what's needed to
  prove the bug. Provide the minimal PoC, not a weaponized exploit.

**Output:** A submission-ready report.

**Tools:** the report template, your PoC, screenshots/traces from `-vvvv` runs.

---

## Flow summary

```
Phase 1 Recon ─────────────► invariants + architecture
        │
Phase 2 Attack Surface ────► entry points + trust boundaries
        │
Phase 3 Automated ─────────► triaged signals ──┐
        │                                       ├──► Phase 4 Manual Review
Phase 1 invariants ────────────────────────────┘        │
                                                          ▼
                                              vulnerability hypotheses
                                                          │
                                              Phase 5 PoC (prove + quantify)
                                                          │
                                              Phase 5b Verify (demote or confirm)
                                                          │
                                              Phase 6 Report (impact-first)
```
