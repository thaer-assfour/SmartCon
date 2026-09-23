# Case Study: <Protocol> — <Short Name of Bug>

Use this template to document real exploits (historical hacks or your own findings).
Re-deriving how a known hack worked is one of the fastest ways to sharpen the
methodology — treat each as an exercise: read the post-mortem *after* you try to
find the bug yourself in the code.

File name: `YYYY-MM-DD-<protocol>-<short-slug>.md`. The **Summary** block below is
machine-read by [`tools/build-checklist.py`](../../tools/build-checklist.py), which
builds the [case-study index](README.md) and links every case study into the
[checklist](../../methodology/checklist.md) next to the categories and item IDs it
names. Keep the bold labels exactly as written.

---

## Summary
- **Protocol:** 
- **Date:** YYYY-MM-DD
- **Chain:** 
- **Loss:** $ / tokens
- **Vulnerability class:** [<Class>](../vulnerabilities/<file>.md)
- **Checklist categories:** <slug>[, <slug>]  — slugs from `methodology/checklist-map.json` (e.g. `reentrancy, flash-loans`)
- **Checklist items:** <ID>[, <ID>] — SmartCon `SC-*` and/or Cyfrin `SOL-*` IDs that would have caught it
- **Root cause in one sentence:** 
- **Attack tx:** <explorer link>
- **Reproduction:** <link to a runnable PoC, e.g. the DeFiHackLabs test file>

## Background
What the protocol does, and the intended invariant that was broken.

## The vulnerability
The specific flawed code / logic. Include the relevant snippet and file/line if available.
If the snippet is paraphrased rather than copied from the deployed source, say so.

```solidity
// vulnerable code (simplified)
```

## The exploit, step by step
1. 
2. 
3. 

## Why it worked
Which assumption failed, and why the automated tools / audit missed it.

## The fix
What the patch did, and why it closes the hole.

```solidity
// fixed code (simplified)
```

## Lessons for the checklist
- Which [checklist](../../methodology/checklist.md) items would have caught this? (repeat the IDs from the Summary and say *how* each question surfaces the bug)
- Is there a new question we should add to the checklist? Propose it verbatim.

## References
- Post-mortem:
- Transaction(s):
- Related audits / similar incidents:
