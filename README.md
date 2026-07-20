# SmartCon — Smart Contract Bug Bounty Methodology

A structured, repeatable methodology and toolkit for discovering vulnerabilities
in EVM smart contracts. SmartCon is not a single scanner — it is an end-to-end
**pipeline** that takes a target protocol and produces a verified, well-written
vulnerability report.

> Automated tools find *known* bug patterns. The high-value money is in the
> *business logic* — and that only surfaces through disciplined manual review.
> SmartCon exists to make both halves systematic.

---

## Philosophy

1. **Process over tools.** Any single tool has blind spots. A phased process with
   a category-driven checklist does not.
2. **Impact first.** A finding is only worth writing up if you can articulate a
   concrete loss of funds or broken invariant — and ideally prove it with a PoC.
3. **Prove, don't claim.** Every High/Critical finding ships with a runnable
   Foundry proof-of-concept that reproduces the exploit against a fork or mock.
4. **Repeatable.** The same steps apply to every engagement, so quality does not
   depend on memory or mood.

---

## The methodology at a glance

Six phases, each feeding the next. Full detail in [`methodology/phases.md`](methodology/phases.md).

| # | Phase | Goal | Output |
|---|-------|------|--------|
| 1 | **Recon** | Understand the protocol: docs, architecture, money flow, TVL | Architecture map + contract inventory |
| 2 | **Attack Surface Mapping** | Enumerate entry points, privileges, external calls, value flows | Attack-surface map |
| 3 | **Automated Analysis** | Run static/dynamic tooling to catch known patterns | Triaged signal list |
| 4 | **Manual Deep Review** | Hunt business-logic flaws, edge cases, broken invariants | Vulnerability hypotheses |
| 5 | **Proof of Concept** | Prove exploitability with a Foundry test | Runnable PoC |
| 6 | **Reporting** | Impact, exploit scenario, fix, severity | Submission-ready report |

The [checklist](methodology/checklist.md) is applied during phases 3–4 and is the
spine of the whole project.

---

## Repository layout

```
SmartCon/
├── README.md                         # You are here
├── methodology/
│   ├── phases.md                     # The 6 phases in detail
│   ├── checklist.md                  # Full category-driven review checklist
│   └── severity-classification.md    # How to rate impact (Immunefi-aligned)
├── knowledge-base/
│   ├── vulnerabilities/              # One file per vulnerability class (16)
│   │   ├── reentrancy.md
│   │   ├── access-control.md
│   │   ├── arithmetic-and-precision.md
│   │   ├── oracle-and-price-manipulation.md
│   │   ├── flash-loans.md
│   │   ├── defi-logic.md
│   │   ├── upgradeability.md
│   │   ├── signatures.md
│   │   ├── denial-of-service.md
│   │   ├── token-integration.md
│   │   ├── front-running-mev.md
│   │   ├── randomness.md
│   │   ├── governance.md
│   │   ├── bridges-cross-chain.md
│   │   ├── low-level-calls.md
│   │   └── input-validation.md
│   └── case-studies/
│       └── TEMPLATE.md               # Structure for post-mortem write-ups
├── tools/
│   ├── setup.sh                      # Install Foundry, Slither, Aderyn, ...
│   └── scan.sh                       # Run the automated toolchain over a target
├── scripts/
│   └── recon.sh                      # Pull verified source for an on-chain address
├── templates/
│   ├── poc/                          # Ready-to-run Foundry PoC scaffold
│   ├── report.md                     # Vulnerability report template
│   └── audit-notes.md                # Per-engagement working notes
├── examples/
│   └── reentrancy-demo/              # Runnable worked example (Phase 3 + Phase 5)
└── engagements/                      # Per-target work (git-ignored for privacy)
```

---

## Worked example

[`examples/reentrancy-demo/`](examples/reentrancy-demo/) is a runnable, end-to-end
demonstration against a deliberately vulnerable vault. `./run.sh` performs **Phase 3**
(Slither flags the reentrancy) and **Phase 5** (a real EVM executes the exploit and
drains the vault — attacker stakes 1 ETH and walks away with 16). It needs no native
`solc`: a bundled `solc-js` shim covers restricted networks.

---

## Quick start

```bash
# 1. Install the toolchain (Foundry, Slither, Aderyn, Semgrep rules)
./tools/setup.sh

# 2. Pull verified source for an on-chain target (needs an Etherscan API key)
export ETHERSCAN_API_KEY=your_key
./scripts/recon.sh 0xTargetContractAddress ./engagements/my-target

# 3. Run the automated toolchain and collect a combined report
./tools/scan.sh ./engagements/my-target

# 4. Work the checklist manually, then write your PoC from templates/poc/

# 5. Draft the finding
cp templates/report.md engagements/my-target/finding-01.md
```

---

## Scope

- **Chains:** EVM first (Ethereum, Arbitrum, Optimism, Base, BSC, Polygon).
- **Languages:** Solidity primary; Vyper secondary.
- **Targets:** Any smart-contract bounty or audit contest (Immunefi, Code4rena,
  Sherlock, Cantina, HackenProof). The methodology is platform-agnostic.

Out of scope: Web2 assets (web apps, APIs, infra) attached to a protocol — those
follow a different methodology entirely.

---

## Ethics & rules of engagement

Only test contracts you are authorized to test — a public bounty program's scope,
a contest repo, a testnet, or a local fork you control. Never run exploits against
live mainnet contracts outside an authorized program. Follow each program's rules
on PoC location (testnet vs. fork), disclosure, and KYC. See
[`methodology/phases.md`](methodology/phases.md#phase-6--reporting) for responsible
disclosure guidance.

---

## Practice grounds

Sharpen the methodology on deliberately vulnerable targets before live programs:

- [Damn Vulnerable DeFi](https://www.damnvulnerabledefi.xyz/)
- [Ethernaut](https://ethernaut.openzeppelin.com/)
- [Capture the Ether](https://capturetheether.com/)
- Past [Code4rena](https://code4rena.com/reports) and [Sherlock](https://audits.sherlock.xyz/contests) reports (read the findings, then re-derive them).
