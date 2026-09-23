#!/usr/bin/env python3
"""
Build SmartCon's review checklist from its sources.

Sources (edit these):
  methodology/checklist-map.json                 SmartCon's 17 categories, core questions (SC-*),
                                                 and the placement rules for upstream items.
  methodology/upstream/cyfrin-audit-checklist.json
                                                 Vendored Cyfrin / Solodit checklist (SOL-*). Refresh
                                                 with --fetch; never edit by hand.
  knowledge-base/case-studies/*.md               Hand-written post-mortems whose Summary block names
                                                 the categories and item IDs that would have caught
                                                 the bug.

Generated (never edit by hand):
  methodology/checklist.json                     Merged, machine-readable checklist.
  methodology/checklist.md                       The checklist auditors walk in Phase 4.
  methodology/checklist-reference.md             Per-item detail: description, remediation, references,
                                                 case studies citing the item.
  templates/coverage-matrix.md                   Per-engagement coverage table (copy into engagements/).
  knowledge-base/case-studies/README.md          Index of case studies.

Usage:
  python3 tools/build-checklist.py            # regenerate everything
  python3 tools/build-checklist.py --check    # exit 1 if any generated file is stale or a source is invalid
  python3 tools/build-checklist.py --fetch    # refresh the vendored upstream checklist, then regenerate

Only the Python standard library is used.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

MAP_PATH = "methodology/checklist-map.json"
OUT_JSON = "methodology/checklist.json"
OUT_MD = "methodology/checklist.md"
OUT_REF = "methodology/checklist-reference.md"
OUT_COV = "templates/coverage-matrix.md"
OUT_CS_INDEX = "knowledge-base/case-studies/README.md"
CS_DIR = "knowledge-base/case-studies"

GENERATED_BANNER = (
    "<!-- GENERATED FILE. Do not edit by hand.\n"
    "     Sources: methodology/checklist-map.json (SmartCon core questions and placement rules)\n"
    "              methodology/upstream/cyfrin-audit-checklist.json (Cyfrin / Solodit items)\n"
    "              knowledge-base/case-studies/*.md (post-mortems citing checklist items)\n"
    "     Regenerate: python3 tools/build-checklist.py -->\n"
)

SUMMARY_LABELS = [
    "Protocol", "Date", "Chain", "Loss", "Vulnerability class", "Checklist categories",
    "Checklist items", "Root cause in one sentence", "Attack tx", "Reproduction",
]


class BuildError(Exception):
    pass


# --------------------------------------------------------------------------- helpers
def rpath(rel: str) -> str:
    return os.path.join(ROOT, rel)


def read_json(rel: str):
    with open(rpath(rel), encoding="utf-8") as fh:
        return json.load(fh)


def anchor(text: str) -> str:
    """GitHub-style heading anchor."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\- ]+", "", text)
    return text.replace(" ", "-")


def cell(text: str) -> str:
    """Make text safe inside a Markdown table cell."""
    return re.sub(r"\s+", " ", str(text)).replace("|", "\\|").strip()


def rel_link(from_rel: str, to_rel: str) -> str:
    """Relative link from one repo file to another."""
    return os.path.relpath(rpath(to_rel), os.path.dirname(rpath(from_rel))).replace(os.sep, "/")


# --------------------------------------------------------------------------- upstream
def flatten_upstream(data) -> list[dict]:
    items: list[dict] = []

    def walk(node, path):
        for child in node.get("data", []):
            if "id" in child:
                entry = dict(child)
                entry["path"] = list(path)
                items.append(entry)
            elif "data" in child:
                walk(child, path + [child["category"]])

    for top in data:
        walk(top, [top["category"]])
    return items


def fetch_upstream(cfg: dict) -> None:
    meta = read_json(cfg["meta"])
    url = meta["source_file"]
    print(f"[build-checklist] fetching {url}")
    raw = None
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310 (fixed https url)
            raw = resp.read()
    except Exception as exc:  # fall back to curl, which honours the environment's proxy/CA setup
        print(f"[build-checklist] urllib failed ({exc}); trying curl")
        raw = subprocess.check_output(["curl", "-sSL", url])
    data = json.loads(raw)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    with open(rpath(cfg["source"]), "w", encoding="utf-8") as fh:
        fh.write(text)
    meta.update({
        "retrieved_at": _dt.date.today().isoformat(),
        "sha256_of_original_download": hashlib.sha256(raw).hexdigest(),
        "sha256_of_vendored_file": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "item_count": len(flatten_upstream(data)),
        "top_level_categories": [c["category"] for c in data],
    })
    with open(rpath(cfg["meta"]), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
        fh.write("\n")
    print(f"[build-checklist] vendored {meta['item_count']} items (sha256 {meta['sha256_of_vendored_file'][:12]}…)")


# --------------------------------------------------------------------------- case studies
def parse_case_study(rel: str) -> dict:
    with open(rpath(rel), encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    cs: dict = {"file": rel, "name": os.path.basename(rel)}
    title = next((l for l in lines if l.startswith("# ")), None)
    if not title:
        raise BuildError(f"{rel}: missing '# Case Study: ...' title")
    cs["title"] = re.sub(r"^#\s*Case Study:\s*", "", title).strip()
    for label in SUMMARY_LABELS:
        pat = re.compile(r"^\s*-\s*\*\*" + re.escape(label) + r":\*\*\s*(.*)$")
        val = None
        for l in lines:
            m = pat.match(l)
            if m:
                val = m.group(1).strip()
                break
        if val is None:
            raise BuildError(f"{rel}: Summary block is missing '- **{label}:**'")
        cs[label] = val
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", cs["Date"]):
        raise BuildError(f"{rel}: Date must be YYYY-MM-DD, got {cs['Date']!r}")
    cs["categories"] = [s.strip() for s in re.split(r"[,\s]+", cs["Checklist categories"]) if s.strip()]
    cs["items"] = [s.strip().rstrip(".") for s in re.split(r"[,\s]+", cs["Checklist items"]) if s.strip()]
    return cs


def load_case_studies(valid_slugs: set[str], valid_ids: set[str]) -> list[dict]:
    out = []
    for name in sorted(os.listdir(rpath(CS_DIR))):
        if not name.endswith(".md") or name in ("TEMPLATE.md", "README.md"):
            continue
        cs = parse_case_study(f"{CS_DIR}/{name}")
        bad = [s for s in cs["categories"] if s not in valid_slugs]
        if bad:
            raise BuildError(f"{cs['file']}: unknown checklist category slug(s) {bad}")
        bad = [i for i in cs["items"] if i not in valid_ids]
        if bad:
            raise BuildError(f"{cs['file']}: unknown checklist item id(s) {bad}")
        out.append(cs)
    out.sort(key=lambda c: c["Date"], reverse=True)
    return out


# --------------------------------------------------------------------------- model
def build_model() -> dict:
    cfg = read_json(MAP_PATH)
    upstream_meta = read_json(cfg["cyfrin"]["meta"])
    upstream = flatten_upstream(read_json(cfg["cyfrin"]["source"]))

    cats = {c["slug"]: dict(c, core=list(c["items"]), extended=[], case_studies=[]) for c in cfg["categories"]}
    apps = {a["slug"]: dict(a, extended=[], case_studies=[]) for a in cfg["appendices"]}
    by_path = cfg["cyfrin"]["by_path"]
    by_id = cfg["cyfrin"]["by_id"]

    unmapped, unused_paths = [], set(by_path)
    for item in upstream:
        path_str = " > ".join(item["path"])
        target = by_id.get(item["id"])
        if target is None:
            best = None
            for prefix, slug in by_path.items():
                if path_str == prefix or path_str.startswith(prefix + " > "):
                    if best is None or len(prefix) > len(best[0]):
                        best = (prefix, slug)
            if best:
                unused_paths.discard(best[0])
                target = best[1]
        if target is None:
            unmapped.append(f"{item['id']} ({path_str})")
            continue
        entry = {
            "id": item["id"],
            "source": "cyfrin",
            "upstream_path": item["path"],
            "question": item.get("question", "").strip(),
            "description": (item.get("description") or "").strip(),
            "remediation": (item.get("remediation") or "").strip(),
            "references": item.get("references") or [],
            "tags": item.get("tags") or [],
        }
        if target in cats:
            cats[target]["extended"].append(entry)
        elif target in apps:
            apps[target]["extended"].append(entry)
        else:
            raise BuildError(f"placement rule for {item['id']} points at unknown slug {target!r}")
    if unmapped:
        raise BuildError("unmapped upstream items (add a by_path or by_id rule):\n  " + "\n  ".join(unmapped))
    bad_ids = [i for i in by_id if i not in {u['id'] for u in upstream}]
    if bad_ids:
        raise BuildError(f"by_id rules reference unknown upstream ids: {bad_ids}")
    if unused_paths:
        print(f"[build-checklist] note: by_path rules matching nothing: {sorted(unused_paths)}", file=sys.stderr)

    for c in cats.values():
        for it in c["core"]:
            it["source"] = "smartcon"

    valid_ids = {it["id"] for c in cats.values() for it in c["core"] + c["extended"]}
    valid_ids |= {it["id"] for a in apps.values() for it in a["extended"]}
    case_studies = load_case_studies(set(cats), valid_ids)

    cited_by: dict[str, list[dict]] = {}
    for cs in case_studies:
        for slug in cs["categories"]:
            cats[slug]["case_studies"].append(cs)
        for iid in cs["items"]:
            cited_by.setdefault(iid, []).append(cs)

    return {
        "cfg": cfg,
        "upstream_meta": upstream_meta,
        "categories": [cats[c["slug"]] for c in cfg["categories"]],
        "appendices": [apps[a["slug"]] for a in cfg["appendices"]],
        "case_studies": case_studies,
        "cited_by": cited_by,
    }


# --------------------------------------------------------------------------- renderers
def short(text: str, limit: int) -> str:
    """First clause of a Summary field (before ';', ' (' or ', a'), capped at `limit` chars."""
    text = re.sub(r"\s+", " ", text).strip()
    text = re.split(r";| \(|, (?:a |an |the )| across | attributed | in the | drained | protocol loss| total", text, maxsplit=1)[0].strip().rstrip(",.")
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def cs_label(cs: dict) -> str:
    return f"{cs['Date']} {short(cs['Protocol'], 40)} ({short(cs['Loss'], 32)})"


def cat_anchor(c: dict) -> str:
    return anchor(f"{c['number']}. {c['name']}")


def render_checklist_md(m: dict) -> str:
    meta = m["upstream_meta"]
    ref = rel_link(OUT_MD, OUT_REF)
    o: list[str] = []
    o.append("# Review Checklist\n")
    o.append(GENERATED_BANNER)
    o.append(
        "The spine of SmartCon. Apply it during Phases 3–4, category by category, against\n"
        "every entry point in your attack-surface map. Each item is phrased as a question:\n"
        "answer it with evidence from the code, not from assumption. An unanswered question is\n"
        "an open lead, not a pass.\n"
    )
    o.append(
        "**How to read an item.** `SC-*` items are SmartCon's core questions; walk all of them on\n"
        "every in-scope contract. `SOL-*` items are the extended set, imported verbatim from the\n"
        f"[Cyfrin / Solodit audit checklist]({meta['hosted_at']}) ({meta['item_count']} items, retrieved\n"
        f"{meta['retrieved_at']}) and placed under the SmartCon category they belong to; each one is\n"
        "distilled from real, paid findings. Every ID links to its entry in\n"
        f"[`checklist-reference.md`]({ref}) (description, remediation, Solodit references and the\n"
        "case studies that cite it). Track coverage per engagement with\n"
        f"[`templates/coverage-matrix.md`]({rel_link(OUT_MD, OUT_COV)}).\n"
    )
    o.append("## Overview\n")
    o.append("| # | Category | Core | Extended | Case studies | Knowledge base |")
    o.append("|---|----------|-----:|---------:|-------------:|----------------|")
    tot_core = tot_ext = 0
    for c in m["categories"]:
        kb = f"[{os.path.basename(c['kb'])}]({rel_link(OUT_MD, c['kb'])})" if c.get("kb") else "—"
        o.append(f"| {c['number']} | [{c['name']}](#{cat_anchor(c)}) | {len(c['core'])} | {len(c['extended'])} | {len(c['case_studies'])} | {kb} |")
        tot_core += len(c["core"])
        tot_ext += len(c["extended"])
    for a in m["appendices"]:
        head = f"Appendix {a['letter']}. {a['name']}"
        o.append(f"| {a['letter']} | [{a['name']}](#{anchor(head)}) | 0 | {len(a['extended'])} | 0 | — |")
        tot_ext += len(a["extended"])
    o.append(f"| | **Total** | **{tot_core}** | **{tot_ext}** | **{len(m['case_studies'])}** | |")
    o.append("")
    o.append("---\n")

    for c in m["categories"]:
        o.append(f"## {c['number']}. {c['name']}\n")
        bits = []
        if c.get("kb"):
            bits.append(f"Notes: [`{c['kb']}`]({rel_link(OUT_MD, c['kb'])})")
        if c["case_studies"]:
            links = ", ".join(f"[{cs_label(cs)}]({rel_link(OUT_MD, cs['file'])})" for cs in c["case_studies"])
            bits.append(f"Case studies: {links}")
        if bits:
            o.append(" · ".join(bits) + "\n")
        o.append("**Core**\n")
        for it in c["core"]:
            o.append(f"- [ ] **[{it['id']}]({ref}#{anchor(it['id'])})** {it['question']}")
        o.append("")
        if c["extended"]:
            o.append("**Extended (Cyfrin / Solodit)**\n")
            last_path = None
            for it in c["extended"]:
                p = " › ".join(it["upstream_path"])
                if p != last_path:
                    if last_path is not None:
                        o.append("")
                    o.append(f"*{p}*")
                    o.append("")
                    last_path = p
                o.append(f"- [ ] **[{it['id']}]({ref}#{anchor(it['id'])})** {it['question']}")
            o.append("")
    for a in m["appendices"]:
        o.append(f"## Appendix {a['letter']}. {a['name']}\n")
        o.append(a["description"] + "\n")
        last_path = None
        for it in a["extended"]:
            p = " › ".join(it["upstream_path"])
            if p != last_path:
                if last_path is not None:
                    o.append("")
                o.append(f"### {it['upstream_path'][-1]}\n")
                last_path = p
            o.append(f"- [ ] **[{it['id']}]({ref}#{anchor(it['id'])})** {it['question']}")
        o.append("")
    o.append("---\n")
    o.append("## Coverage tracking\n")
    o.append(
        f"Copy [`templates/coverage-matrix.md`]({rel_link(OUT_MD, OUT_COV)}) into\n"
        "`engagements/<target>/` and record, per contract, the answer to every item. The goal is\n"
        "not to \"pass\": it is to have consciously *looked* at every category on every entry point\n"
        "and recorded what you found. Cite item IDs in hypotheses, PoCs and reports so a reader\n"
        "can trace a finding back to the question that produced it.\n"
    )
    return "\n".join(o)


def render_reference_md(m: dict) -> str:
    meta = m["upstream_meta"]
    o: list[str] = []
    o.append("# Checklist Reference\n")
    o.append(GENERATED_BANNER)
    o.append(
        "One entry per checklist item, in the same order as [`checklist.md`]"
        f"({rel_link(OUT_REF, OUT_MD)}). `SC-*` entries are SmartCon's own; `SOL-*` entries carry the\n"
        f"description, remediation and Solodit references from the [Cyfrin / Solodit checklist]({meta['source_repo']})\n"
        f"(retrieved {meta['retrieved_at']}). \"Cited by\" lists the case studies whose Summary names the item.\n"
    )

    def entry(it: dict, kb: str | None):
        o.append(f"### {it['id']}\n")
        o.append(f"**Question.** {it['question']}\n")
        if it["source"] == "smartcon":
            src = "SmartCon core question"
            if kb:
                src += f" · knowledge base: [`{kb}`]({rel_link(OUT_REF, kb)})"
            if it.get("added_from"):
                src += f" · added from: {it['added_from']}"
            o.append(src + "\n")
        else:
            o.append(f"Source: Cyfrin / Solodit · upstream path: *{' › '.join(it['upstream_path'])}*\n")
            if it["description"]:
                o.append(f"**Description.** {it['description']}\n")
            if it["remediation"]:
                o.append(f"**Remediation.** {it['remediation']}\n")
            if it["references"]:
                o.append("**References.**")
                for r in it["references"]:
                    o.append(f"- <{r}>")
                o.append("")
            if it["tags"]:
                o.append(f"Tags: {', '.join(it['tags'])}\n")
        cited = m["cited_by"].get(it["id"], [])
        if cited:
            o.append("**Cited by.** " + "; ".join(f"[{cs_label(cs)}]({rel_link(OUT_REF, cs['file'])})" for cs in cited) + "\n")

    for c in m["categories"]:
        o.append(f"## {c['number']}. {c['name']}\n")
        for it in c["core"]:
            entry(it, c.get("kb"))
        for it in c["extended"]:
            entry(it, None)
    for a in m["appendices"]:
        o.append(f"## Appendix {a['letter']}. {a['name']}\n")
        for it in a["extended"]:
            entry(it, None)
    return "\n".join(o)


def render_coverage_md(m: dict) -> str:
    ref = rel_link(OUT_COV, OUT_REF)
    o: list[str] = []
    o.append("# Coverage Matrix — <Target>\n")
    o.append(GENERATED_BANNER)
    o.append(
        "Copy this file to `engagements/<target>/coverage-matrix.md` at the start of Phase 4 and\n"
        "fill it in as you go. It is the evidence that every category was applied to every entry\n"
        "point; it also tells you, at any moment, what you have *not* looked at yet.\n\n"
        "- **Status** per category: `☐` not started · `◐` partial · `☑` every item answered for every in-scope contract.\n"
        "- **Answer** per item: `N` checked, not applicable or not present · `Y` the pattern is present → log a\n"
        "  hypothesis in audit-notes · `?` open lead, still to investigate.\n"
        "- **Evidence** is a file:line or a one-line reason. \"Looked, seems fine\" is not evidence.\n"
        f"- Item IDs link to [`checklist-reference.md`]({ref}).\n"
    )
    o.append("## Category coverage\n")
    o.append("| # | Category | Core | Extended | Contracts reviewed | Status | Open leads |")
    o.append("|---|----------|-----:|---------:|--------------------|--------|------------|")
    for c in m["categories"]:
        o.append(f"| {c['number']} | {c['name']} | {len(c['core'])} | {len(c['extended'])} | | ☐ | |")
    for a in m["appendices"]:
        o.append(f"| {a['letter']} | {a['name']} | 0 | {len(a['extended'])} | | ☐ | |")
    o.append("")
    o.append("## Item coverage\n")
    for c in m["categories"]:
        o.append(f"### {c['number']}. {c['name']}\n")
        o.append("| ID | Question | Contract(s) | Answer | Evidence / notes |")
        o.append("|----|----------|-------------|--------|------------------|")
        for it in c["core"] + c["extended"]:
            o.append(f"| [{it['id']}]({ref}#{anchor(it['id'])}) | {cell(it['question'])} | | | |")
        o.append("")
    for a in m["appendices"]:
        o.append(f"### Appendix {a['letter']}. {a['name']}\n")
        o.append("Only the rows whose version range matches the target's compiler / library versions apply.\n")
        o.append("| ID | Question | Applies? | Answer | Evidence / notes |")
        o.append("|----|----------|----------|--------|------------------|")
        for it in a["extended"]:
            o.append(f"| [{it['id']}]({ref}#{anchor(it['id'])}) | {cell(it['question'])} | | | |")
        o.append("")
    return "\n".join(o)


def render_case_index_md(m: dict) -> str:
    o: list[str] = []
    o.append("# Case Studies\n")
    o.append(GENERATED_BANNER.replace("Do not edit by hand.", "This index is generated; the case-study files themselves are hand-written."))
    o.append(
        "Real exploits, re-derived as exercises for the methodology. Each file follows\n"
        f"[`TEMPLATE.md`](TEMPLATE.md); its Summary block names the checklist categories and item IDs that\n"
        "would have caught the bug, and the build script links every case study into the\n"
        f"[checklist]({rel_link(OUT_CS_INDEX, OUT_MD)}) and the\n"
        f"[reference]({rel_link(OUT_CS_INDEX, OUT_REF)}) next to those items. Reproductions point at\n"
        "[DeFiHackLabs](https://github.com/SunWeb3Sec/DeFiHackLabs) Foundry tests.\n\n"
        "How to use them: pick one, read only the **Background** section, try to find the bug in the\n"
        "protocol's code yourself, then read the rest. Add a new case study whenever a checklist item\n"
        "fails to explain an incident you read about: that is a gap in the checklist, and the\n"
        "\"Lessons for the checklist\" section is where the new question gets proposed.\n"
    )
    o.append(f"{len(m['case_studies'])} case studies, newest first.\n")
    o.append("| Date | Protocol | Chain | Loss | Categories | Checklist items | Case study |")
    o.append("|------|----------|-------|------|------------|-----------------|------------|")
    slug_to_cat = {c["slug"]: c for c in m["categories"]}
    for cs in m["case_studies"]:
        md_link = rel_link(OUT_CS_INDEX, OUT_MD)
        cats = ", ".join(
            f"[{slug_to_cat[s]['number']}]({md_link}#{cat_anchor(slug_to_cat[s])})" for s in cs["categories"]
        )
        items = ", ".join(f"[{i}]({rel_link(OUT_CS_INDEX, OUT_REF)}#{anchor(i)})" for i in cs["items"])
        o.append(f"| {cs['Date']} | {cell(short(cs['Protocol'], 48))} | {cell(short(cs['Chain'], 24))} | {cell(short(cs['Loss'], 40))} | {cats} | {items} | [{cell(cs['title'])}]({cs['name']}) |")
    o.append("")
    o.append("## By category\n")
    for c in m["categories"]:
        if not c["case_studies"]:
            continue
        o.append(f"- **{c['number']}. {c['name']}**: " + "; ".join(f"[{cs_label(cs)}]({cs['name']})" for cs in c["case_studies"]))
    o.append("")
    return "\n".join(o)


def build_json(m: dict) -> str:
    meta = m["upstream_meta"]

    def cs_brief(cs: dict) -> dict:
        return {"file": cs["file"], "title": cs["title"], "date": cs["Date"], "protocol": cs["Protocol"],
                "chain": cs["Chain"], "loss": cs["Loss"], "categories": cs["categories"], "items": cs["items"],
                "attack_tx": cs["Attack tx"], "reproduction": cs["Reproduction"]}

    def item_out(it: dict) -> dict:
        d = {k: v for k, v in it.items() if k in ("id", "source", "question", "description", "remediation",
                                                   "references", "tags", "upstream_path", "added_from")}
        d["cited_by"] = [cs["file"] for cs in m["cited_by"].get(it["id"], [])]
        return d

    out = {
        "generated_by": "tools/build-checklist.py",
        "sources": {
            "map": MAP_PATH,
            "upstream": {k: meta[k] for k in ("name", "source_repo", "source_file", "hosted_at", "retrieved_at",
                                              "sha256_of_vendored_file", "item_count")},
        },
        "categories": [
            {
                "number": c["number"], "slug": c["slug"], "id": c["id"], "name": c["name"], "kb": c.get("kb"),
                "items": [item_out(it) for it in c["core"] + c["extended"]],
                "case_studies": [cs["file"] for cs in c["case_studies"]],
            }
            for c in m["categories"]
        ],
        "appendices": [
            {"letter": a["letter"], "slug": a["slug"], "name": a["name"], "description": a["description"],
             "items": [item_out(it) for it in a["extended"]]}
            for a in m["appendices"]
        ],
        "case_studies": [cs_brief(cs) for cs in m["case_studies"]],
    }
    return json.dumps(out, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------- main
def outputs(m: dict) -> dict[str, str]:
    return {
        OUT_JSON: build_json(m),
        OUT_MD: render_checklist_md(m),
        OUT_REF: render_reference_md(m),
        OUT_COV: render_coverage_md(m),
        OUT_CS_INDEX: render_case_index_md(m),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="verify sources and that generated files are current")
    ap.add_argument("--fetch", action="store_true", help="refresh the vendored upstream checklist first")
    args = ap.parse_args(argv)

    try:
        if args.fetch:
            fetch_upstream(read_json(MAP_PATH)["cyfrin"])
        m = build_model()
        gen = outputs(m)
    except BuildError as exc:
        print(f"[build-checklist] ERROR: {exc}", file=sys.stderr)
        return 1

    n_core = sum(len(c["core"]) for c in m["categories"])
    n_ext = sum(len(c["extended"]) for c in m["categories"]) + sum(len(a["extended"]) for a in m["appendices"])
    summary = f"{n_core} core + {n_ext} extended items, {len(m['case_studies'])} case studies"

    if args.check:
        stale = []
        for rel, text in gen.items():
            try:
                with open(rpath(rel), encoding="utf-8") as fh:
                    current = fh.read()
            except FileNotFoundError:
                current = None
            if current != text:
                stale.append(rel)
        if stale:
            print("[build-checklist] STALE (run python3 tools/build-checklist.py):\n  " + "\n  ".join(stale), file=sys.stderr)
            return 1
        print(f"[build-checklist] OK: sources valid, generated files current ({summary})")
        return 0

    for rel, text in gen.items():
        with open(rpath(rel), "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"[build-checklist] wrote {rel}")
    print(f"[build-checklist] done: {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
