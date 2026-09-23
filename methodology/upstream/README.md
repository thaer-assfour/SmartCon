# Upstream checklists (vendored)

This directory holds verbatim copies of third-party checklists that
[`tools/build-checklist.py`](../../tools/build-checklist.py) merges into SmartCon's
[checklist](../checklist.md). Never edit these files by hand; refresh them with the
build script and commit the result together with the regenerated outputs.

| File | What it is | Refresh |
|------|------------|---------|
| `cyfrin-audit-checklist.json` | The Cyfrin / Solodit aggregated audit checklist (370 items, each with an ID, question, description, remediation and links to real Solodit findings). Hosted at <https://solodit.cyfrin.io/checklist>, source <https://github.com/Cyfrin/audit-checklist>. | `python3 tools/build-checklist.py --fetch` |
| `cyfrin-audit-checklist.meta.json` | Provenance written by `--fetch`: retrieval date, SHA-256, item count. | automatic |

## Attribution

The Cyfrin checklist is community-maintained and credits the individual auditors whose
lists it aggregates (Beirao, Decurity, Hans, Rareskills and others; see the upstream
readme). SmartCon keeps every upstream item ID (`SOL-*`) unchanged so findings and
reports can cite the original item, and every generated page links back to the
upstream source. The upstream repository publishes no LICENSE file at the time of
vendoring; treat the content as Cyfrin's and keep the attribution when redistributing.

## How the merge works

`methodology/checklist-map.json` maps each upstream category path (for example
`Defi > Lending`) to one of SmartCon's 17 categories, with per-item overrides where a
single upstream section spans several SmartCon categories. Compiler and library
version issues are collected into an appendix instead of a category. Run
`python3 tools/build-checklist.py --check` to verify that every upstream item is mapped
and that the generated files are current.
