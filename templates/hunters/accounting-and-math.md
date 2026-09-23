# Hunter brief — Accounting & math

<!-- GENERATED FILE. Do not edit by hand.
     Sources: methodology/checklist-map.json (SmartCon core questions and placement rules)
              methodology/upstream/cyfrin-audit-checklist.json (Cyfrin / Solodit items)
              knowledge-base/case-studies/*.md (post-mortems citing checklist items)
     Regenerate: python3 tools/build-checklist.py -->

## Role

You are one of 6 parallel reviewers in SmartCon **Phase 4 (manual deep review)**. You own 2 checklist categories: **3. Arithmetic & Precision**, **6. DeFi Business Logic**. The other hunters own the rest (Callbacks, reentrancy & liveness: 1, 9, 16; Tokens & price sources: 10, 4; Privilege, upgrades, governance & signatures: 2, 7, 14, 8; Atomic capital, ordering & randomness: 5, 11, 13; Inputs, cross-chain boundaries & hygiene: 17, 15, 12); do not spend time on their categories except to hand them a lead. You read and reason; you do not modify the target, you do not fix anything, and you never run an exploit against a live deployment.

**Focus.** Every division, rounding direction, exchange rate, share price and solvency check. Mirror functions (deposit/withdraw, mint/redeem, borrow/repay, normal/emergency paths) must be symmetric; empty or near-empty markets, one-wei remainders and repeated tiny operations must be modelled explicitly.

**Start with.**

1. Table every formula that converts between assets, shares, debt and collateral, with its rounding direction and who profits from it.
2. For every function that reduces collateral or increases debt (including donate/emergency/migrate/rescue helpers), confirm the same post-state solvency check as the primary path.
3. Simulate totalSupply == 0, 1 and 2 wei, and the first depositor after a full exit.

## Inputs you receive from the orchestrator

- **Target:** path to the in-scope source (plus commit or deployment addresses), the program's scope and its known-issues list.
- **Phase 1:** the intended invariants in plain language and the money-flow map.
- **Phase 2:** the attack-surface table (entry point, caller, effect, value moved, assumptions).
- **Phase 3:** the triaged scanner signals that fall into your categories.
- **Time budget** and the exact output contract below.

## Method

1. Read the knowledge-base notes for your categories (linked below) and skim their case studies: they show what each question looked like in a real incident.
2. For every in-scope contract, answer every **core** item below with evidence (`file:line`). An item you could not answer is `?`, never a silent skip.
3. Walk the **extended** items that the protocol's shape makes relevant; mark the rest `N.A.` with a one-word reason.
4. For each Phase 1 invariant that touches your categories, actively construct a state that violates it: you control calldata, ordering, the tokens and contracts you supply, and, for one block, unlimited capital.
5. Write every hypothesis as the attacker would execute it: who calls what, in which order, under which preconditions, and what they walk away with. Quantify roughly.

## Your checklist items

### 3. Arithmetic & Precision

Notes: [`knowledge-base/vulnerabilities/arithmetic-and-precision.md`](../../knowledge-base/vulnerabilities/arithmetic-and-precision.md) · Case studies: [2023-04-15 Hundred Finance (~$7M)](../../knowledge-base/case-studies/2023-04-15-hundred-finance-empty-market-exchange-rate.md), [2022-03-20 Umbrella Network (~$700K)](../../knowledge-base/case-studies/2022-03-20-umbrella-network-staking-underflow.md), [2021-04-28 Uranium Finance (~$50M)](../../knowledge-base/case-studies/2021-04-28-uranium-finance-k-constant-typo.md)

**Core**

- **[SC-MATH-1](../../methodology/checklist-reference.md#sc-math-1)** Any `unchecked` blocks where overflow/underflow is actually reachable?
- **[SC-MATH-2](../../methodology/checklist-reference.md#sc-math-2)** Does division happen before multiplication, losing precision?
- **[SC-MATH-3](../../methodology/checklist-reference.md#sc-math-3)** What direction does rounding go, and who profits? Can it be repeated to drain?
- **[SC-MATH-4](../../methodology/checklist-reference.md#sc-math-4)** First-depositor / share-inflation: can a tiny first deposit + donation make shares mis-price for later depositors? (ERC-4626 classic)
- **[SC-MATH-5](../../methodology/checklist-reference.md#sc-math-5)** Are decimals normalized across tokens of different precision?
- **[SC-MATH-6](../../methodology/checklist-reference.md#sc-math-6)** Any casts (`uint256`→`uint128`, signed↔unsigned) that silently truncate?
- **[SC-MATH-7](../../methodology/checklist-reference.md#sc-math-7)** Empty-market / zero-supply edge: what do exchange rates and rounding do when `totalSupply` is 0 or a few wei (Compound v2 `redeemUnderlying` rounding, first `mint` after a full redeem)?

**Extended (Cyfrin / Solodit)**

- **[SOL-Basics-Math-1](../../methodology/checklist-reference.md#sol-basics-math-1)** Is the mathematical calculation accurate?
- **[SOL-Basics-Math-2](../../methodology/checklist-reference.md#sol-basics-math-2)** Is there any loss of precision in time calculations?
- **[SOL-Basics-Math-3](../../methodology/checklist-reference.md#sol-basics-math-3)** Are you aware that expressions like `1 day` are cast to `uint24`, potentially causing overflows?
- **[SOL-Basics-Math-4](../../methodology/checklist-reference.md#sol-basics-math-4)** Is there any case where dividing is done before multiplication?
- **[SOL-Basics-Math-5](../../methodology/checklist-reference.md#sol-basics-math-5)** Does the rounding direction matter?
- **[SOL-Basics-Math-6](../../methodology/checklist-reference.md#sol-basics-math-6)** Is there a possibility of division by zero?
- **[SOL-Basics-Math-7](../../methodology/checklist-reference.md#sol-basics-math-7)** Even in versions like `>0.8.0`, have you ensured variables won't underflow or overflow leading to reverts?
- **[SOL-Basics-Math-8](../../methodology/checklist-reference.md#sol-basics-math-8)** Are you aware that assigning a negative value to an unsigned integer causes a revert?
- **[SOL-Basics-Math-9](../../methodology/checklist-reference.md#sol-basics-math-9)** Have you properly reviewed all usages of `unchecked{}`?
- **[SOL-Basics-Math-10](../../methodology/checklist-reference.md#sol-basics-math-10)** In comparisons using < or >, should you instead be using ≤ or ≥?
- **[SOL-Basics-Math-11](../../methodology/checklist-reference.md#sol-basics-math-11)** Have you taken into consideration mathematical operations in inline assembly?
- **[SOL-Basics-Math-12](../../methodology/checklist-reference.md#sol-basics-math-12)** What happens for the minimum/maximum values included in the calculation?
- **[SOL-Basics-Type-1](../../methodology/checklist-reference.md#sol-basics-type-1)** Is there a forced type casting?
- **[SOL-Basics-Type-2](../../methodology/checklist-reference.md#sol-basics-type-2)** Does the protocol use time units like `days`?
- **[SOL-Defi-LSD-9](../../methodology/checklist-reference.md#sol-defi-lsd-9)** Does unnecessary precision loss occur in deposit, withdrawal or reward calculations?
- **[SOL-Heuristics-7](../../methodology/checklist-reference.md#sol-heuristics-7)** Are there any off-by-one errors?
- **[SOL-Heuristics-10](../../methodology/checklist-reference.md#sol-heuristics-10)** Are there rounding errors that can be amplified?
- **[SOL-Heuristics-17](../../methodology/checklist-reference.md#sol-heuristics-17)** Does calling a function multiple times with smaller amounts yield the same contract state as calling it once with the aggregate amount?
- **[SOL-Integrations-Uniswap-7](../../methodology/checklist-reference.md#sol-integrations-uniswap-7)** Is `unchecked` used properly with Uniswap's math libraries?
- **[SOL-LL-5](../../methodology/checklist-reference.md#sol-ll-5)** Is there a non-zero check for the denominator?

### 6. DeFi Business Logic

Notes: [`knowledge-base/vulnerabilities/defi-logic.md`](../../knowledge-base/vulnerabilities/defi-logic.md) · Case studies: [2023-04-15 Hundred Finance (~$7M)](../../knowledge-base/case-studies/2023-04-15-hundred-finance-empty-market-exchange-rate.md), [2023-03-13 Euler Finance (~$197M)](../../knowledge-base/case-studies/2023-03-13-euler-finance-donate-to-reserves.md), [2023-02-17 Platypus Finance (~$8.5M)](../../knowledge-base/case-studies/2023-02-17-platypus-emergency-withdraw-solvency.md), [2021-04-28 Uranium Finance (~$50M)](../../knowledge-base/case-studies/2021-04-28-uranium-finance-k-constant-typo.md)

**Core**

- **[SC-DEFI-1](../../methodology/checklist-reference.md#sc-defi-1)** Lending: are collateral factor, health factor, and liquidation math correct at the boundaries? Can a position be made unliquidatable, or self-liquidated for profit?
- **[SC-DEFI-2](../../methodology/checklist-reference.md#sc-defi-2)** AMM: are the swap invariant (`x*y=k`), fees, and reserves updated atomically and in the right order?
- **[SC-DEFI-3](../../methodology/checklist-reference.md#sc-defi-3)** Staking/rewards: can rewards be double-claimed, claimed after unstake, or diluted/inflated via deposit timing?
- **[SC-DEFI-4](../../methodology/checklist-reference.md#sc-defi-4)** Vaults (ERC-4626): does `deposit`/`mint`/`withdraw`/`redeem` round in the protocol's favor? Is the first-deposit inflation attack mitigated?
- **[SC-DEFI-5](../../methodology/checklist-reference.md#sc-defi-5)** Fee logic: can fees be bypassed, set to values that break accounting, or round to zero?
- **[SC-DEFI-6](../../methodology/checklist-reference.md#sc-defi-6)** Slippage / deadline: are user-supplied `minOut` and `deadline` enforced?
- **[SC-DEFI-7](../../methodology/checklist-reference.md#sc-defi-7)** Do "emergency", "donate", "migrate" or "rescue" style functions re-run the same solvency / health / accounting checks as the normal path? (Euler `donateToReserves`, Platypus `emergencyWithdraw`)

**Extended (Cyfrin / Solodit)**

- **[SOL-AM-DA-1](../../methodology/checklist-reference.md#sol-am-da-1)** Does the protocol rely on `balance` or `balanceOf` instead of internal accounting?
- **[SOL-Basics-Payment-3](../../methodology/checklist-reference.md#sol-basics-payment-3)** Are there vulnerabilities related to force-feeding?
- **[SOL-Basics-Payment-4](../../methodology/checklist-reference.md#sol-basics-payment-4)** What is the minimum deposit/withdrawal amount?
- **[SOL-Defi-AS-3](../../methodology/checklist-reference.md#sol-defi-as-3)** Is there a validation check for protocol reserves?
- **[SOL-Defi-AS-4](../../methodology/checklist-reference.md#sol-defi-as-4)** Does the AMM utilize forked code?
- **[SOL-Defi-AS-5](../../methodology/checklist-reference.md#sol-defi-as-5)** Are there rounding issues in product constant formulas?
- **[SOL-Defi-General-2](../../methodology/checklist-reference.md#sol-defi-general-2)** Are there unexpected rewards accruing for user deposited assets?
- **[SOL-Defi-General-3](../../methodology/checklist-reference.md#sol-defi-general-3)** Could direct transfers of funds introduce vulnerabilities?
- **[SOL-Defi-General-4](../../methodology/checklist-reference.md#sol-defi-general-4)** Could the initial deposit introduce any issues?
- **[SOL-Defi-General-7](../../methodology/checklist-reference.md#sol-defi-general-7)** What would happen if only 1 wei remains in the pool?
- **[SOL-Defi-Lending-1](../../methodology/checklist-reference.md#sol-defi-lending-1)** Will the liquidation process function effectively during rapid market downturns?
- **[SOL-Defi-Lending-2](../../methodology/checklist-reference.md#sol-defi-lending-2)** Can a position be liquidated if the loan remains unpaid or if the collateral falls below the required threshold?
- **[SOL-Defi-Lending-3](../../methodology/checklist-reference.md#sol-defi-lending-3)** Is it possible for a user to gain undue profit from self-liquidation?
- **[SOL-Defi-Lending-4](../../methodology/checklist-reference.md#sol-defi-lending-4)** If token transfers or collateral additions are temporarily paused, can a user still be liquidated, even if they intend to deposit more funds?
- **[SOL-Defi-Lending-5](../../methodology/checklist-reference.md#sol-defi-lending-5)** If liquidations are temporarily suspended, what are the implications when they are resumed?
- **[SOL-Defi-Lending-6](../../methodology/checklist-reference.md#sol-defi-lending-6)** Is it possible for users to manipulate the system by front-running and slightly increasing their collateral to prevent liquidations?
- **[SOL-Defi-Lending-7](../../methodology/checklist-reference.md#sol-defi-lending-7)** Are all positions, regardless of size, incentivized adequately for liquidation?
- **[SOL-Defi-Lending-8](../../methodology/checklist-reference.md#sol-defi-lending-8)** Is interest considered during Loan-to-Value (LTV) calculation?
- **[SOL-Defi-Lending-9](../../methodology/checklist-reference.md#sol-defi-lending-9)** Can liquidation and repaying be enabled or disabled simultaneously?
- **[SOL-Defi-Lending-10](../../methodology/checklist-reference.md#sol-defi-lending-10)** Is it possible to lend and borrow the same token within a single transaction?
- **[SOL-Defi-Lending-11](../../methodology/checklist-reference.md#sol-defi-lending-11)** Is there a scenario where a liquidator might receive a lesser amount than anticipated?
- **[SOL-Defi-Lending-12](../../methodology/checklist-reference.md#sol-defi-lending-12)** Is it possible for a user to be in a condition where they cannot repay their loan?
- **[SOL-Defi-LSD-1](../../methodology/checklist-reference.md#sol-defi-lsd-1)** Can a malicious validator front-run setting withdrawal credentials?
- **[SOL-Defi-LSD-4](../../methodology/checklist-reference.md#sol-defi-lsd-4)** Can an arbitrary exchange rate be set when processing queued withdrawals?
- **[SOL-Defi-LSD-6](../../methodology/checklist-reference.md#sol-defi-lsd-6)** Can inter-related storage be corrupted, especially storage related to operators and validators?
- **[SOL-Defi-Staking-1](../../methodology/checklist-reference.md#sol-defi-staking-1)** Can a user amplify another user's time lock duration by stacking tokens on their behalf?
- **[SOL-Defi-Staking-2](../../methodology/checklist-reference.md#sol-defi-staking-2)** Can the distribution of rewards be unduly delayed or prematurely claimed?
- **[SOL-Defi-Staking-3](../../methodology/checklist-reference.md#sol-defi-staking-3)** Are rewards up-to-date in all use-cases?
- **[SOL-Heuristics-12](../../methodology/checklist-reference.md#sol-heuristics-12)** Can functions be invoked multiple times with identical parameters?
- **[SOL-Heuristics-16](../../methodology/checklist-reference.md#sol-heuristics-16)** Are there any code asymmetries?
- **[SOL-Integrations-AC-2](../../methodology/checklist-reference.md#sol-integrations-ac-2)** What happens if the utilization rate is too high, and collateral cannot be retrieved?
- **[SOL-Integrations-AC-3](../../methodology/checklist-reference.md#sol-integrations-ac-3)** What happens if the protocol is paused?
- **[SOL-Integrations-AC-4](../../methodology/checklist-reference.md#sol-integrations-ac-4)** What happens if the pool becomes deprecated?
- **[SOL-Integrations-AC-5](../../methodology/checklist-reference.md#sol-integrations-ac-5)** What happens if assets you lend/borrow are within the same eMode category?
- **[SOL-Integrations-AC-7](../../methodology/checklist-reference.md#sol-integrations-ac-7)** Does the protocol properly implement AAVE/COMP reward claims?
- **[SOL-Integrations-AC-8](../../methodology/checklist-reference.md#sol-integrations-ac-8)** On AAVE, what happens if a user reaches the maximum debt on an isolated asset?
- **[SOL-Integrations-AC-9](../../methodology/checklist-reference.md#sol-integrations-ac-9)** Does borrowing an AAVE siloed asset restrict borrowing other assets?
- **[SOL-Integrations-Balancer-3](../../methodology/checklist-reference.md#sol-integrations-balancer-3)** Does the protocol use Balancer's Boosted Pool?
- **[SOL-Integrations-Uniswap-2](../../methodology/checklist-reference.md#sol-integrations-uniswap-2)** Are there refunds after swaps?
- **[SOL-Integrations-Uniswap-10](../../methodology/checklist-reference.md#sol-integrations-uniswap-10)** Is a hard-coded fee tier parameter being used?

## Output contract

Return exactly these four sections, in this order, as Markdown, with nothing before the first heading. The orchestrator merges them mechanically.

### Hypotheses

| # | Hypothesis (attacker story, one or two sentences) | Checklist item(s) | Entry point (`Contract.function`, `file:line`) | Invariant broken | Preconditions | Rough impact | Confidence | How to prove (PoC sketch) |
|---|---|---|---|---|---|---|---|---|

Rank by impact × confidence (`high` / `medium` / `low`). No hypothesis without a `file:line`. A finding you could not fully confirm still goes here at `low` confidence; the orchestrator decides what reaches Phase 5. If you have none, keep the header row and write `None.` under the table with one sentence on why your categories do not apply. A bug that clearly belongs to another cluster goes under **Leads for other hunters**, not here, unless one of *your* items is what reveals it; the orchestrator deduplicates by root cause, so do not restate another cluster's finding to be safe.

### Coverage

| ID | Contract(s) | Answer (`Y` present → hypothesis above / `N` checked, absent / `?` open lead / `N.A.` not applicable) | Evidence (`file:line` or a one-line reason) |
|---|---|---|---|

One row per **core** item of your categories per in-scope contract (group contracts when the answer and evidence are identical), plus every extended item you examined.

### Not covered

What you did not get to and why (time, missing source, out of scope). An empty list means you claim full coverage of your categories.

### Leads for other hunters

Anything you noticed that belongs to another cluster, one line each in the form `<cluster slug>`: `<item ID>`: what and where (`file:line`). Use these slugs exactly: `callbacks-and-liveness` (Callbacks, reentrancy & liveness), `tokens-and-oracles` (Tokens & price sources), `privilege-and-upgrade` (Privilege, upgrades, governance & signatures), `economics-and-ordering` (Atomic capital, ordering & randomness), `boundaries-and-inputs` (Inputs, cross-chain boundaries & hygiene). Write `None.` if there are none.
