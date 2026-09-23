# [SEVERITY] <Concise title of the vulnerability>

> Impact-first. A triager should understand the risk from the first two lines.

## Summary
One or two sentences: what is broken and what an attacker gains. State the concrete
impact (funds stolen/frozen, invariant broken) and who can trigger it.

## Severity
**<Critical | High | Medium | Low>** — justify using
[severity-classification.md](../methodology/severity-classification.md).
State the impact and the likelihood/preconditions explicitly.
Verification (Phase 5b, [verify.md](verify.md)): **CONFIRMED** by <verifier> on <date>
(or DOWNGRADED from X, with the reason).

## Affected code
- **Contract / file:** `path/Contract.sol`
- **Function:** `functionName()`
- **Lines:** `Lxx–Lyy`
- **Commit / deployment reviewed:** `<hash or address @ chain>`

```solidity
// paste the vulnerable code, with a comment pointing at the exact flaw
```

## Vulnerability details
Explain the root cause. Which assumption/invariant is violated and why. Reference the
relevant [knowledge-base](../knowledge-base/vulnerabilities/) class and the checklist
items that surfaced it, e.g. `SC-REEN-1`, `SOL-EC-13`
(see [checklist-reference.md](../methodology/checklist-reference.md)).

## Exploit scenario (step by step)
1. Preconditions (state, actors, capital — note if a flash loan supplies capital).
2. Attacker calls ...
3. ...
4. Result: attacker gains X / protocol loses Y.

## Proof of Concept
A runnable Foundry test that reproduces the exploit and asserts the impact. Include
the command and the relevant trace output.

```
forge test -vvvv --match-test testExploit
```

```solidity
// PoC.t.sol (or link to templates/poc/)
```

**Measured impact:** e.g. attacker profit = 1,240 ETH; % of TVL = 38%.

## Recommended fix
Concrete remediation with corrected code. Explain *why* it closes the hole.

```solidity
// fixed code
```

## References
- Checklist items: `SC-…`, `SOL-…` (the Solodit references behind each ID point at
  paid findings of the same class).
- Similar incidents: link the relevant [case studies](../knowledge-base/case-studies/README.md).
- Related known bugs / CVEs / prior findings.
- Links to the affected transactions or contest scope.
