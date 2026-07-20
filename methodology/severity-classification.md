# Severity Classification

Severity is a function of **impact** and **likelihood**. This model is aligned with
the [Immunefi Vulnerability Severity Classification System](https://immunefi.com/immunefi-vulnerability-severity-classification-system-v2-3/),
which most Web3 programs use, but always defer to the specific program's own rules.

The single most important discipline: **do not over-claim.** A well-argued Medium
builds trust; an inflated "Critical" that triages down to Low burns it.

---

## Severity levels (smart contracts)

| Severity | Typical impact |
|----------|----------------|
| **Critical** | Direct theft or permanent freezing of a material amount of user/protocol funds; insolvency; unauthorized minting; governance takeover. |
| **High** | Theft/freezing of funds under specific (but realistic) conditions; theft of unclaimed yield/rewards; temporary freezing that requires intervention. |
| **Medium** | Griefing with no direct profit but real cost to users/protocol; smart-contract-level DoS; miscalculations that don't (yet) drain funds. |
| **Low** | Minor issues, small rounding leaks, missing events, best-practice deviations with limited impact. |
| **Informational** | No security impact: style, gas, documentation, defense-in-depth. |

---

## Impact-in-Scope (the two axes)

Most programs define severity by the **impact** you can demonstrate, gated by
**likelihood** (preconditions, cost, and who can trigger it).

**Impact** — what actually goes wrong:
- Funds: stolen, frozen, or lost. How much? Whose?
- Invariant: which protocol guarantee breaks, and what follows from breaking it?
- Availability: is the protocol or a core function unusable?

**Likelihood** — how realistic is the exploit:
- Preconditions: does it need a specific state, a privileged actor, an unusual token?
- Cost: is it profitable after gas and capital? (flash-loan capital is ~free)
- Access: can *anyone* trigger it, or only a trusted/limited party?

A large impact with a trivial trigger is Critical. The same impact requiring an
unrealistic precondition drops in severity.

---

## Rating workflow

1. **State the impact concretely.** "An attacker drains the lending pool's entire
   USDC reserve" — not "reentrancy exists."
2. **State the preconditions and cost.** What must be true, and what does the
   attacker spend?
3. **Map to the table**, then sanity-check against the program's own severity page.
4. **Quantify** where possible: dollar value at risk, % of TVL, number of users.
5. **Down-rate honestly** if the exploit needs an unrealistic assumption (e.g. "the
   admin is malicious" is usually out of scope unless the program says otherwise).

---

## Common down-rating traps (usually out of scope)

- Assuming a **trusted/admin role is malicious** (unless the program includes
  "malicious governance" in scope).
- Requiring the **victim to do something irrational** (approve infinite to a random
  contract, sign an obviously malicious payload).
- Theoretical issues with **no reachable code path** or no realizable impact.
- **Known issues** listed in the program scope or prior audits.
- Gas optimizations and style nits (Informational at best).

---

## What a strong finding proves

A finding rated High/Critical should answer all of:

- **Who** can trigger it (any user? a specific role?)
- **What** they gain / what breaks (quantified)
- **How** — a runnable PoC that reproduces it (Phase 5)
- **Why** the fix works (Phase 6)

If you cannot answer "how much" and "who", the severity is probably lower than it feels.
