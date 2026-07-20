# The Six Phases

This is the backbone of SmartCon. Every engagement runs through these phases in
order. Earlier phases produce artifacts that later phases consume, so do not skip
ahead — a weak attack-surface map produces a shallow review.

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
  rules over the target.
- Triage every finding: **true positive**, **false positive**, or **needs manual
  confirmation**. Do not trust or dismiss blindly — each detector output is a
  *lead*, not a verdict.
- Stand up property-based fuzzing where invariants are known (Foundry invariant
  tests, Echidna/Medusa) to try to break the invariants you wrote down in Phase 1.

**Output:** A triaged list of signals, each mapped to a checklist category and
marked with a confidence level.

**Tools:** Slither, Aderyn, Semgrep, Foundry (`forge test`, invariant testing),
Echidna / Medusa, Mythril (targeted symbolic execution).

> Automated tools are necessary but never sufficient. Their real value here is
> *coverage of the boring stuff* so your attention is free for the interesting stuff.

---

## Phase 4 — Manual Deep Review

**Goal:** Find the business-logic and edge-case bugs that tools cannot. This is
where Critical findings come from.

**Do:**

- Walk the [checklist](checklist.md) category by category against the attack-surface
  map. For each entry point, ask the category's questions explicitly.
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

**Output:** A ranked list of vulnerability hypotheses, each with a rough impact and
a plan to prove it.

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

## Phase 6 — Reporting

**Goal:** Communicate the finding so a triager can validate it in minutes and a
developer can fix it correctly.

**Do:**

- Use [`templates/report.md`](../templates/report.md). Lead with **impact**, then
  the vulnerable code, the step-by-step exploit, the PoC, and a concrete fix.
- Assign severity using [`severity-classification.md`](severity-classification.md).
  Be honest — over-claiming severity burns credibility.
- Include the exact file, function, and line references, and the commit/deployment
  you reviewed.
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
                                              Phase 6 Report (impact-first)
```
