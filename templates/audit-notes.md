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
Copy the [checklist](../methodology/checklist.md) and mark per contract. Log hypotheses:

| # | Hypothesis | Invariant broken | Impact (rough) | How to prove | Status |
|---|------------|------------------|----------------|--------------|--------|
| 1 |  |  |  |  | open |

---

## Phase 5 — PoCs
| Hypothesis # | PoC file | Result | Measured impact |
|--------------|----------|--------|-----------------|
|  |  |  |  |

---

## Phase 6 — Reports
| Finding | Severity | Report file | Submitted? |
|---------|----------|-------------|------------|
|  |  |  |  |
