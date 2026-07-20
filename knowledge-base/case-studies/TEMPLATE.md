# Case Study: <Protocol> — <Short Name of Bug>

Use this template to document real exploits (historical hacks or your own findings).
Re-deriving how a known hack worked is one of the fastest ways to sharpen the
methodology — treat each as an exercise: read the post-mortem *after* you try to
find the bug yourself in the code.

---

## Summary
- **Protocol:** 
- **Date:** 
- **Loss:** $ / tokens
- **Vulnerability class:** (link to the relevant [knowledge-base](../vulnerabilities/) file)
- **Root cause in one sentence:** 

## Background
What the protocol does, and the intended invariant that was broken.

## The vulnerability
The specific flawed code / logic. Include the relevant snippet and file/line if available.

```solidity
// vulnerable code
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
// fixed code
```

## Lessons for the checklist
- Which [checklist](../../methodology/checklist.md) items would have caught this?
- Is there a new question we should add to the checklist?

## References
- Post-mortem:
- Transaction(s):
- Related audits:
