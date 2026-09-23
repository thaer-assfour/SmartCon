# Phase 4 hunters

<!-- GENERATED FILE. Do not edit by hand.
     Sources: methodology/checklist-map.json (SmartCon core questions and placement rules)
              methodology/upstream/cyfrin-audit-checklist.json (Cyfrin / Solodit items)
              knowledge-base/case-studies/*.md (post-mortems citing checklist items)
     Regenerate: python3 tools/build-checklist.py -->

Phase 4 is split across parallel **hunters**, one per cluster of related checklist categories. Each brief in this directory is self-contained: role, focus, the cluster's core and extended items, knowledge-base notes, case studies and the exact output contract. Hand a brief to a sub-agent (or a teammate) together with the target and the Phase 1–3 artifacts, run all of them at once, then merge.

| Cluster | Categories | Items (core + extended) | Brief |
|---------|------------|------------------------:|-------|
| **Callbacks, reentrancy & liveness** | 1. Reentrancy, 9. Denial of Service, 16. Low-Level Calls & Return Data | 14 + 38 | [`callbacks-and-liveness.md`](callbacks-and-liveness.md) |
| **Accounting & math** | 3. Arithmetic & Precision, 6. DeFi Business Logic | 14 + 60 | [`accounting-and-math.md`](accounting-and-math.md) |
| **Tokens & price sources** | 10. Token Integration Quirks, 4. Oracle & Price Manipulation | 13 + 63 | [`tokens-and-oracles.md`](tokens-and-oracles.md) |
| **Privilege, upgrades, governance & signatures** | 2. Access Control, 7. Upgradeability & Proxies, 14. Governance, 8. Signatures, Proofs & Replay | 22 + 49 | [`privilege-and-upgrade.md`](privilege-and-upgrade.md) |
| **Atomic capital, ordering & randomness** | 5. Flash Loans & Atomic Composition, 11. Front-running / MEV, 13. Weak Randomness | 11 + 29 | [`economics-and-ordering.md`](economics-and-ordering.md) |
| **Inputs, cross-chain boundaries & hygiene** | 17. Input Validation & Uninitialized State, 15. Bridges & Cross-Chain, 12. General Solidity Hygiene | 19 + 131 | [`boundaries-and-inputs.md`](boundaries-and-inputs.md) |

## Orchestration recipe

1. **Prepare the shared packet** once: target path and commit, scope and known issues, Phase 1 invariants and money flow, the Phase 2 attack-surface table, the Phase 3 triage, and a time budget. Every hunter gets the same packet plus its own brief.
2. **Spawn all hunters in parallel** (in Claude Code: one `Agent` call per brief in a single message, read-only instructions, the brief's path and the packet in the prompt). Do not let a hunter see another hunter's output; independent eyes are the point.
3. **Merge** when they return. Deduplicate hypotheses by root cause, not by symptom: two stories that hinge on the same missing check are one finding, kept at the higher confidence with both entry points listed. Rank by impact × confidence.
4. **Re-dispatch leads**: every line under "Leads for other hunters" goes to the named cluster as a short follow-up question; a lead nobody owns goes to the orchestrator's own review.
5. **Assemble coverage**: paste every Coverage row into `engagements/<target>/coverage-matrix.md`. A core item with no row from any hunter is a gap: answer it yourself or record it under "Not covered" in the audit notes. Never report coverage you did not get.
6. **Hand over to Phase 5** the ranked hypotheses with their checklist IDs; Phase 5b later verifies each PoC with a *fresh* agent that was not a hunter.

## Regenerating the briefs

Briefs are generated from [`methodology/checklist-map.json`](../../methodology/checklist-map.json) (`hunters` block: cluster slug, name, categories, focus, `start_with` steps, optional `include_appendices`) by `python3 tools/build-checklist.py`. Change the clustering there, never in the briefs.
