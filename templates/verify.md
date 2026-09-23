# Verification Record — <Finding title>

> Phase 5b. Fill one copy per finding **before** it is written up. The verifier must not be
> the person (or agent) who found the bug: hand this file, the hypothesis, the PoC and the
> in-scope source to a fresh reviewer whose job is to *demote* the finding. A finding that
> survives this file honestly is worth submitting; one that does not was going to be
> demoted by the program's triager anyway, at the cost of your credibility.

- **Finding:** `engagements/<target>/finding-XX.md` (draft)
- **Claimed severity:** Critical | High | Medium | Low
- **PoC:** `engagements/<target>/test/PoC_XX.t.sol` — command: `forge test --match-test testExploit -vvvv`
- **Verifier:** <name / "independent sub-agent">
- **Date:**

---

## 1. Reachability (is the vulnerable path actually callable?)

| Question | Answer | Evidence (file:line, tx, trace) |
|----------|--------|----------------------------------|
| Is the vulnerable function reachable by an **unprivileged** caller in the *deployed* configuration (roles, whitelists, pause state, initializer values)? | | |
| Does the exploit depend on a constructor / initializer / config value that differs between the test setup and the real deployment? | | |
| Were all modifiers, `require`s and pre-checks on the path traced, including in inherited contracts and libraries? | | |
| Is the code under test the **in-scope commit / deployment**, not a fork, an older version or a simplified copy? | | |

## 2. Preconditions and actors (what must be true first?)

| Question | Answer | Evidence |
|----------|--------|----------|
| Does the exploit need a **trusted role to act maliciously** (owner, admin, keeper, oracle)? If yes, is "malicious admin" explicitly in scope for this program? | | |
| Does it need the **victim to act irrationally** (approve infinite to an unknown contract, sign an obviously malicious payload, ignore an on-screen warning)? | | |
| Does it need a **specific token behaviour** (fee-on-transfer, rebasing, hooks, blacklist) and is such a token actually listed / listable in scope? | | |
| Does it need a **specific market state** (empty pool, near-zero liquidity, exact tick, stale oracle) and how often does that state occur on-chain? | | |
| Does it need a **race** (front-running, specific block position) and is that realistic on the target chain (private mempool, sequencer ordering)? | | |

## 3. Capital, cost and profit (does the attacker actually come out ahead?)

| Question | Answer | Evidence |
|----------|--------|----------|
| Capital required, and is it flash-loanable for this asset on this chain in this size? | | |
| Gas cost at realistic gas prices vs. profit; does profit survive slippage when the loot is *realised* (sold / bridged)? | | |
| Is the profit bounded (fixed amount, one-shot) or repeatable / scalable with TVL? | | |
| If the impact is "freezing" not "theft": how long, for whom, and can the protocol recover without a hard fork or upgrade? | | |

## 4. PoC quality (does the PoC prove what the report claims?)

| Question | Answer | Evidence |
|----------|--------|----------|
| Does the PoC run against **real deployed state** (fork at a pinned block) or an unmodified copy of the in-scope source? Mocks must not remove any check the real code performs. | | |
| Does the PoC **assert quantified damage** (attacker balance up, protocol balance down, invariant violated) rather than merely reaching a line or emitting a log? | | |
| Are cheat-codes limited to *setup*? No `vm.store` on protected slots, no `vm.prank` as a privileged role, no `deal` after the attack starts, unless the report explicitly models that precondition. | | |
| Does the test pass deterministically (re-run twice; no reliance on live RPC state that drifts)? | | |
| Does the measured impact in the PoC match the number in the report's Summary? | | |

## 5. Known issues and duplicates

| Question | Answer | Evidence |
|----------|--------|----------|
| Is the issue listed in the program's **known issues / out-of-scope** list or in a prior audit report for this codebase? | | |
| Has the same root cause already been paid on Solodit / Code4rena / Sherlock for this codebase or an obvious fork? (search the checklist item's references) | | |
| Is it a **duplicate of another finding** in this engagement (same root cause, different symptom)? Merge or split accordingly. | | |

## 6. Severity re-derived independently

Without looking at the claimed severity, rate it from
[`severity-classification.md`](../methodology/severity-classification.md):

- **Impact (concrete):** what is lost / frozen / broken, quantified: 
- **Likelihood:** who can trigger it, preconditions, cost: 
- **Independent rating:** Critical | High | Medium | Low | Informational
- **Program's own severity page says:** 
- **Matches the claimed severity?** yes / no → if no, explain which axis differs.

## 7. Fix validity

| Question | Answer | Evidence |
|----------|--------|----------|
| Does the proposed fix close the root cause (not just the demonstrated symptom)? | | |
| Does it introduce a new failure mode (DoS, griefing, broken invariant, storage layout change on an upgradeable contract)? | | |
| Re-run the PoC against the patched code: does it fail for the *right* reason (the new check), not for an unrelated revert? | | |

---

## Verdict

- [ ] **CONFIRMED** — reachable, realistic preconditions, PoC proves quantified impact, severity re-derived matches. Proceed to Phase 6 at the claimed severity.
- [ ] **DOWNGRADED** to ______ — real but the preconditions, cost or impact do not support the claimed severity. Rewrite the Summary and Severity sections before Phase 6.
- [ ] **REJECTED** — not reachable / needs an out-of-scope actor / duplicate / PoC does not prove the claim. Record why below so the hypothesis is not re-opened later.

**Reasoning (three to six lines, written for the finder):**

**Follow-ups spawned (new hypotheses discovered while verifying):**
- 
