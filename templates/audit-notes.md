# Audit Notes — <Target>

Working notes for one engagement. This is your running log across all six phases.
Keep it messy but complete — it becomes the source for your reports.

- **Target:** 
- **Scope (in-scope contracts / commit):** 
- **Program / platform:** 
- **Rules (PoC location, known issues, severity model):** 

---

## Phase 1 — Recon
**Intended invariants (plain language):**
- [ ] 
- [ ] 

**Architecture / money flow:**
- Contracts and one-line purpose:
- Proxy/impl pairs, factories, external deps:
- Where value enters / is stored / exits:

---

## Phase 2 — Attack surface
| Contract.function | Caller (who) | Effect / value moved | Assumptions | Notes |
|-------------------|--------------|----------------------|-------------|-------|
|  |  |  |  |  |

**Privileged actors & worst-case:**

---

## Phase 3 — Automated analysis
Ran `tools/scan.sh`. Triage:

| Signal | Tool | Category | TP / FP / Check | Notes |
|--------|------|----------|-----------------|-------|
|  |  |  |  |  |

---

## Phase 4 — Manual review (checklist coverage)
Coverage lives in a copy of [`coverage-matrix.md`](coverage-matrix.md) next to this file
(one answer with evidence per checklist item per contract). Log hypotheses here, each
with the item ID that produced it:

| # | Hypothesis | Checklist item(s) | Invariant broken | Impact (rough) | How to prove | Status |
|---|------------|-------------------|------------------|----------------|--------------|--------|
| 1 |  |  |  |  |  | open |

---

## Phase 5 — PoCs
| Hypothesis # | PoC file | Result | Measured impact |
|--------------|----------|--------|-----------------|
|  |  |  |  |

---

## Phase 5b — Verification
One [`verify.md`](verify.md) record per finding, filled by someone (or a fresh sub-agent)
who did not find the bug. Nothing reaches Phase 6 without a verdict.

| Hypothesis # | Verifier | Claimed severity | Verified severity | Verdict (CONFIRMED / DOWNGRADED / REJECTED) | Record file |
|--------------|----------|------------------|-------------------|----------------------------------------------|-------------|
|  |  |  |  |  |  |

---

## Phase 6 — Reports
| Finding | Severity | Report file | Submitted? |
|---------|----------|-------------|------------|
|  |  |  |  |
