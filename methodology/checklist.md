# Review Checklist

<!-- GENERATED FILE. Do not edit by hand.
     Sources: methodology/checklist-map.json (SmartCon core questions and placement rules)
              methodology/upstream/cyfrin-audit-checklist.json (Cyfrin / Solodit items)
              knowledge-base/case-studies/*.md (post-mortems citing checklist items)
     Regenerate: python3 tools/build-checklist.py -->

The spine of SmartCon. Apply it during Phases 3–4, category by category, against
every entry point in your attack-surface map. Each item is phrased as a question:
answer it with evidence from the code, not from assumption. An unanswered question is
an open lead, not a pass.

**How to read an item.** `SC-*` items are SmartCon's core questions; walk all of them on
every in-scope contract. `SOL-*` items are the extended set, imported verbatim from the
[Cyfrin / Solodit audit checklist](https://solodit.cyfrin.io/checklist) (370 items, retrieved
2026-09-23) and placed under the SmartCon category they belong to; each one is
distilled from real, paid findings. Every ID links to its entry in
[`checklist-reference.md`](checklist-reference.md) (description, remediation, Solodit references and the
case studies that cite it). Track coverage per engagement with
[`templates/coverage-matrix.md`](../templates/coverage-matrix.md).

## Overview

| # | Category | Core | Extended | Case studies | Knowledge base |
|---|----------|-----:|---------:|-------------:|----------------|
| 1 | [Reentrancy](#1-reentrancy) | 5 | 8 | 3 | [reentrancy.md](../knowledge-base/vulnerabilities/reentrancy.md) |
| 2 | [Access Control](#2-access-control) | 6 | 22 | 2 | [access-control.md](../knowledge-base/vulnerabilities/access-control.md) |
| 3 | [Arithmetic & Precision](#3-arithmetic--precision) | 7 | 20 | 3 | [arithmetic-and-precision.md](../knowledge-base/vulnerabilities/arithmetic-and-precision.md) |
| 4 | [Oracle & Price Manipulation](#4-oracle--price-manipulation) | 6 | 22 | 5 | [oracle-and-price-manipulation.md](../knowledge-base/vulnerabilities/oracle-and-price-manipulation.md) |
| 5 | [Flash Loans & Atomic Composition](#5-flash-loans--atomic-composition) | 3 | 6 | 5 | [flash-loans.md](../knowledge-base/vulnerabilities/flash-loans.md) |
| 6 | [DeFi Business Logic](#6-defi-business-logic) | 7 | 40 | 4 | [defi-logic.md](../knowledge-base/vulnerabilities/defi-logic.md) |
| 7 | [Upgradeability & Proxies](#7-upgradeability--proxies) | 6 | 12 | 1 | [upgradeability.md](../knowledge-base/vulnerabilities/upgradeability.md) |
| 8 | [Signatures, Proofs & Replay](#8-signatures-proofs--replay) | 5 | 13 | 1 | [signatures.md](../knowledge-base/vulnerabilities/signatures.md) |
| 9 | [Denial of Service](#9-denial-of-service) | 5 | 15 | 1 | [denial-of-service.md](../knowledge-base/vulnerabilities/denial-of-service.md) |
| 10 | [Token Integration Quirks](#10-token-integration-quirks) | 7 | 41 | 2 | [token-integration.md](../knowledge-base/vulnerabilities/token-integration.md) |
| 11 | [Front-running / MEV](#11-front-running--mev) | 5 | 18 | 1 | [front-running-mev.md](../knowledge-base/vulnerabilities/front-running-mev.md) |
| 12 | [General Solidity Hygiene](#12-general-solidity-hygiene) | 6 | 17 | 1 | — |
| 13 | [Weak Randomness](#13-weak-randomness) | 3 | 5 | 0 | [randomness.md](../knowledge-base/vulnerabilities/randomness.md) |
| 14 | [Governance](#14-governance) | 5 | 2 | 2 | [governance.md](../knowledge-base/vulnerabilities/governance.md) |
| 15 | [Bridges & Cross-Chain](#15-bridges--cross-chain) | 6 | 29 | 0 | [bridges-cross-chain.md](../knowledge-base/vulnerabilities/bridges-cross-chain.md) |
| 16 | [Low-Level Calls & Return Data](#16-low-level-calls--return-data) | 4 | 15 | 1 | [low-level-calls.md](../knowledge-base/vulnerabilities/low-level-calls.md) |
| 17 | [Input Validation & Uninitialized State](#17-input-validation--uninitialized-state) | 7 | 18 | 0 | [input-validation.md](../knowledge-base/vulnerabilities/input-validation.md) |
| A | [Version-specific issues (compiler and library bugs)](#appendix-a-version-specific-issues-compiler-and-library-bugs) | 0 | 67 | 0 | — |
| | **Total** | **93** | **370** | **17** | |

---

## 1. Reentrancy

Notes: [`knowledge-base/vulnerabilities/reentrancy.md`](../knowledge-base/vulnerabilities/reentrancy.md) · Case studies: [2023-02-10 dForce (~$3.65M)](../knowledge-base/case-studies/2023-02-10-dforce-read-only-reentrancy.md), [2022-04-30 Rari Capital Fuse pools (~$80M)](../knowledge-base/case-studies/2022-04-30-rari-fei-fuse-reentrancy.md), [2022-03-15 Hundred Finance (~$6.2M)](../knowledge-base/case-studies/2022-03-15-hundred-finance-erc677-hook-reentrancy.md)

**Core**

- [ ] **[SC-REEN-1](checklist-reference.md#sc-reen-1)** Does any function make an external call (token transfer, `call`, callback) *before* updating state? (Checks-Effects-Interactions violation)
- [ ] **[SC-REEN-2](checklist-reference.md#sc-reen-2)** Are there cross-function reentrancy paths that share state but not a guard?
- [ ] **[SC-REEN-3](checklist-reference.md#sc-reen-3)** Is there **read-only reentrancy**: a view function returning stale state that other protocols trust mid-callback?
- [ ] **[SC-REEN-4](checklist-reference.md#sc-reen-4)** Do ERC-777 / ERC-721 / ERC-1155 hooks or `receive()`/`fallback()` give the attacker a callback window?
- [ ] **[SC-REEN-5](checklist-reference.md#sc-reen-5)** Is `nonReentrant` applied consistently across *all* functions touching the same state, including cross-contract entry points?

**Extended (Cyfrin / Solodit)**

*Attacker's Mindset › Reentrancy Attack*

- [ ] **[SOL-AM-ReentrancyAttack-1](checklist-reference.md#sol-am-reentrancyattack-1)** Is there a view function that can return a stale value during interactions?
- [ ] **[SOL-AM-ReentrancyAttack-2](checklist-reference.md#sol-am-reentrancyattack-2)** Is there any state change after interaction to an external contract?

*Defi › Liquid Staking Derivatives*

- [ ] **[SOL-Defi-LSD-3](checklist-reference.md#sol-defi-lsd-3)** Can re-entrancy when ETH is sent during rewards/withdrawals or when NFTs are minted via `_safeMint` (to represent pending withdrawals) be used to drain the protocol's ETH?

*External Call*

- [ ] **[SOL-EC-1](checklist-reference.md#sol-ec-1)** What are the implications if the call reenters a different function?
- [ ] **[SOL-EC-13](checklist-reference.md#sol-ec-13)** Is the check-effect-interaction pattern being utilized?

*Heuristics*

- [ ] **[SOL-Heuristics-4](checklist-reference.md#sol-heuristics-4)** Is the NonReentrant modifier placed before every other modifier?

*Token › Non-fungible : ERC721/1155*

- [ ] **[SOL-Token-NfE1-2](checklist-reference.md#sol-token-nfe1-2)** Is the contract safe from reentrancy attack?
- [ ] **[SOL-Token-NfE1-3](checklist-reference.md#sol-token-nfe1-3)** Is the OpenZeppelin implementation of ERC721 and ERC1155 safeguarded against reentrancy attacks, especially in the `safeTransferFrom` functions?

## 2. Access Control

Notes: [`knowledge-base/vulnerabilities/access-control.md`](../knowledge-base/vulnerabilities/access-control.md) · Case studies: [2022-07-23 Audius (704 ETH)](../knowledge-base/case-studies/2022-07-23-audius-storage-collision-governance.md), [2021-09-03 DAO Maker (~$4M)](../knowledge-base/case-studies/2021-09-03-dao-maker-unprotected-init.md)

**Core**

- [ ] **[SC-AC-1](checklist-reference.md#sc-ac-1)** Is every state-changing/privileged function gated by the correct modifier?
- [ ] **[SC-AC-2](checklist-reference.md#sc-ac-2)** Any function that *should* be `onlyOwner`/role-gated but is public?
- [ ] **[SC-AC-3](checklist-reference.md#sc-ac-3)** Is `tx.origin` used for authorization? (phishable; should be `msg.sender`)
- [ ] **[SC-AC-4](checklist-reference.md#sc-ac-4)** Are initializers protected against being called twice / by anyone?
- [ ] **[SC-AC-5](checklist-reference.md#sc-ac-5)** Are role admins set correctly? Can a role escalate itself?
- [ ] **[SC-AC-6](checklist-reference.md#sc-ac-6)** Is there a default-admin or emergency backdoor that concentrates too much power?

**Extended (Cyfrin / Solodit)**

*Attacker's Mindset › Rug Pull*

- [ ] **[SOL-AM-RP-1](checklist-reference.md#sol-am-rp-1)** Can the admin of the protocol pull assets from the protocol?

*Basics › Access Control*

- [ ] **[SOL-Basics-AC-1](checklist-reference.md#sol-basics-ac-1)** Did you clarify all the actors and their allowed interactions in the protocol?
- [ ] **[SOL-Basics-AC-2](checklist-reference.md#sol-basics-ac-2)** Are there functions lacking proper access controls?
- [ ] **[SOL-Basics-AC-3](checklist-reference.md#sol-basics-ac-3)** Do certain addresses require whitelisting?
- [ ] **[SOL-Basics-AC-4](checklist-reference.md#sol-basics-ac-4)** Does the protocol allow transfer of privileges?
- [ ] **[SOL-Basics-AC-5](checklist-reference.md#sol-basics-ac-5)** What happens during the transfer of privileges?
- [ ] **[SOL-Basics-AC-6](checklist-reference.md#sol-basics-ac-6)** Does the contract inherit others?
- [ ] **[SOL-Basics-AC-7](checklist-reference.md#sol-basics-ac-7)** Does the contract use `tx.origin` in validation?

*Basics › Function*

- [ ] **[SOL-Basics-Function-7](checklist-reference.md#sol-basics-function-7)** Should it be `external`/`public`?
- [ ] **[SOL-Basics-Function-8](checklist-reference.md#sol-basics-function-8)** Does this function need to be called by only EOA or only contracts?
- [ ] **[SOL-Basics-Function-9](checklist-reference.md#sol-basics-function-9)** Does this function need to be restricted for specific callers?

*Basics › Inheritance*

- [ ] **[SOL-Basics-Inheritance-1](checklist-reference.md#sol-basics-inheritance-1)** Is it necessary to limit visibility of parent contract's public functions?

*Centralization Risk*

- [ ] **[SOL-CR-1](checklist-reference.md#sol-cr-1)** What happens to the user accounting in special conditions?
- [ ] **[SOL-CR-2](checklist-reference.md#sol-cr-2)** Is there a pause mechanism?
- [ ] **[SOL-CR-3](checklist-reference.md#sol-cr-3)** Is there a functionality for the admin to withdraw from the protocol?
- [ ] **[SOL-CR-4](checklist-reference.md#sol-cr-4)** Can the admin change critical protocol property immediately?
- [ ] **[SOL-CR-5](checklist-reference.md#sol-cr-5)** Is there any admin setter function missing events?
- [ ] **[SOL-CR-6](checklist-reference.md#sol-cr-6)** How is the ownership/privilege transferred??
- [ ] **[SOL-CR-7](checklist-reference.md#sol-cr-7)** Is there a proper validation in privileged setter functions?

*Defi › Liquid Staking Derivatives*

- [ ] **[SOL-Defi-LSD-5](checklist-reference.md#sol-defi-lsd-5)** Can paused states be bypassed to perform restricted actions even when they should be paused?

*External Call*

- [ ] **[SOL-EC-14](checklist-reference.md#sol-ec-14)** How is the msg.sender handled?

*Integrations › Gnosis Safe*

- [ ] **[SOL-Integrations-GS-1](checklist-reference.md#sol-integrations-gs-1)** Do your modules execute the Guard's hooks?

## 3. Arithmetic & Precision

Notes: [`knowledge-base/vulnerabilities/arithmetic-and-precision.md`](../knowledge-base/vulnerabilities/arithmetic-and-precision.md) · Case studies: [2023-04-15 Hundred Finance (~$7M)](../knowledge-base/case-studies/2023-04-15-hundred-finance-empty-market-exchange-rate.md), [2022-03-20 Umbrella Network (~$700K)](../knowledge-base/case-studies/2022-03-20-umbrella-network-staking-underflow.md), [2021-04-28 Uranium Finance (~$50M)](../knowledge-base/case-studies/2021-04-28-uranium-finance-k-constant-typo.md)

**Core**

- [ ] **[SC-MATH-1](checklist-reference.md#sc-math-1)** Any `unchecked` blocks where overflow/underflow is actually reachable?
- [ ] **[SC-MATH-2](checklist-reference.md#sc-math-2)** Does division happen before multiplication, losing precision?
- [ ] **[SC-MATH-3](checklist-reference.md#sc-math-3)** What direction does rounding go, and who profits? Can it be repeated to drain?
- [ ] **[SC-MATH-4](checklist-reference.md#sc-math-4)** First-depositor / share-inflation: can a tiny first deposit + donation make shares mis-price for later depositors? (ERC-4626 classic)
- [ ] **[SC-MATH-5](checklist-reference.md#sc-math-5)** Are decimals normalized across tokens of different precision?
- [ ] **[SC-MATH-6](checklist-reference.md#sc-math-6)** Any casts (`uint256`→`uint128`, signed↔unsigned) that silently truncate?
- [ ] **[SC-MATH-7](checklist-reference.md#sc-math-7)** Empty-market / zero-supply edge: what do exchange rates and rounding do when `totalSupply` is 0 or a few wei (Compound v2 `redeemUnderlying` rounding, first `mint` after a full redeem)?

**Extended (Cyfrin / Solodit)**

*Basics › Math*

- [ ] **[SOL-Basics-Math-1](checklist-reference.md#sol-basics-math-1)** Is the mathematical calculation accurate?
- [ ] **[SOL-Basics-Math-2](checklist-reference.md#sol-basics-math-2)** Is there any loss of precision in time calculations?
- [ ] **[SOL-Basics-Math-3](checklist-reference.md#sol-basics-math-3)** Are you aware that expressions like `1 day` are cast to `uint24`, potentially causing overflows?
- [ ] **[SOL-Basics-Math-4](checklist-reference.md#sol-basics-math-4)** Is there any case where dividing is done before multiplication?
- [ ] **[SOL-Basics-Math-5](checklist-reference.md#sol-basics-math-5)** Does the rounding direction matter?
- [ ] **[SOL-Basics-Math-6](checklist-reference.md#sol-basics-math-6)** Is there a possibility of division by zero?
- [ ] **[SOL-Basics-Math-7](checklist-reference.md#sol-basics-math-7)** Even in versions like `>0.8.0`, have you ensured variables won't underflow or overflow leading to reverts?
- [ ] **[SOL-Basics-Math-8](checklist-reference.md#sol-basics-math-8)** Are you aware that assigning a negative value to an unsigned integer causes a revert?
- [ ] **[SOL-Basics-Math-9](checklist-reference.md#sol-basics-math-9)** Have you properly reviewed all usages of `unchecked{}`?
- [ ] **[SOL-Basics-Math-10](checklist-reference.md#sol-basics-math-10)** In comparisons using < or >, should you instead be using ≤ or ≥?
- [ ] **[SOL-Basics-Math-11](checklist-reference.md#sol-basics-math-11)** Have you taken into consideration mathematical operations in inline assembly?
- [ ] **[SOL-Basics-Math-12](checklist-reference.md#sol-basics-math-12)** What happens for the minimum/maximum values included in the calculation?

*Basics › Type*

- [ ] **[SOL-Basics-Type-1](checklist-reference.md#sol-basics-type-1)** Is there a forced type casting?
- [ ] **[SOL-Basics-Type-2](checklist-reference.md#sol-basics-type-2)** Does the protocol use time units like `days`?

*Defi › Liquid Staking Derivatives*

- [ ] **[SOL-Defi-LSD-9](checklist-reference.md#sol-defi-lsd-9)** Does unnecessary precision loss occur in deposit, withdrawal or reward calculations?

*Heuristics*

- [ ] **[SOL-Heuristics-7](checklist-reference.md#sol-heuristics-7)** Are there any off-by-one errors?
- [ ] **[SOL-Heuristics-10](checklist-reference.md#sol-heuristics-10)** Are there rounding errors that can be amplified?
- [ ] **[SOL-Heuristics-17](checklist-reference.md#sol-heuristics-17)** Does calling a function multiple times with smaller amounts yield the same contract state as calling it once with the aggregate amount?

*Integrations › Uniswap*

- [ ] **[SOL-Integrations-Uniswap-7](checklist-reference.md#sol-integrations-uniswap-7)** Is `unchecked` used properly with Uniswap's math libraries?

*Low Level*

- [ ] **[SOL-LL-5](checklist-reference.md#sol-ll-5)** Is there a non-zero check for the denominator?

## 4. Oracle & Price Manipulation

Notes: [`knowledge-base/vulnerabilities/oracle-and-price-manipulation.md`](../knowledge-base/vulnerabilities/oracle-and-price-manipulation.md) · Case studies: [2023-05-29 Jimbo's Protocol (~4,090 ETH)](../knowledge-base/case-studies/2023-05-29-jimbos-protocol-unprotected-rebalance.md), [2023-02-10 dForce (~$3.65M)](../knowledge-base/case-studies/2023-02-10-dforce-read-only-reentrancy.md), [2021-10-27 C.R.E.A.M. Finance (~$130M)](../knowledge-base/case-studies/2021-10-27-cream-finance-yusd-price-manipulation.md), [2021-05-19 PancakeBunny (~$45M)](../knowledge-base/case-studies/2021-05-19-pancakebunny-flash-loan-lp-pricing.md), [2020-10-26 Harvest Finance fUSDC / fUSDT vaults (~$33.8M)](../knowledge-base/case-studies/2020-10-26-harvest-finance-curve-pool-manipulation.md)

**Core**

- [ ] **[SC-ORACLE-1](checklist-reference.md#sc-oracle-1)** Does pricing use a **spot price** from an AMM reserve/`getReserves`/`balanceOf`? (manipulable in one tx via flash loan)
- [ ] **[SC-ORACLE-2](checklist-reference.md#sc-oracle-2)** For Chainlink: are `updatedAt` staleness and `answeredInRound` checked? Is a zero/negative price handled? Are min/max bounds considered?
- [ ] **[SC-ORACLE-3](checklist-reference.md#sc-oracle-3)** Is a TWAP used, and is its window long enough to resist manipulation?
- [ ] **[SC-ORACLE-4](checklist-reference.md#sc-oracle-4)** Does the protocol trust `token.balanceOf(pair)` for accounting? (donation-manipulable)
- [ ] **[SC-ORACLE-5](checklist-reference.md#sc-oracle-5)** What happens if the oracle reverts or returns stale data: fail open or closed?
- [ ] **[SC-ORACLE-6](checklist-reference.md#sc-oracle-6)** Is a price or exchange rate derived from a pool or vault that a flash loan can inflate in the same transaction (LP-token pricing, `get_virtual_price`, `pricePerShare`, a cToken `exchangeRate` on a near-empty market)?

**Extended (Cyfrin / Solodit)**

*Attacker's Mindset › Price Manipulation Attack*

- [ ] **[SOL-AM-PMA-1](checklist-reference.md#sol-am-pma-1)** Is the price calculated by the ratio of token balances?
- [ ] **[SOL-AM-PMA-2](checklist-reference.md#sol-am-pma-2)** Is the price calculated from DEX liquidity pool spot prices?

*Defi › General*

- [ ] **[SOL-Defi-General-5](checklist-reference.md#sol-defi-general-5)** Are the protocol token pegged to any other asset?

*Defi › Liquid Staking Derivatives*

- [ ] **[SOL-Defi-LSD-8](checklist-reference.md#sol-defi-lsd-8)** If using a Proof Of Reserves Oracle, does the protocol check for stale data?

*Defi › Oracle*

- [ ] **[SOL-Defi-Oracle-1](checklist-reference.md#sol-defi-oracle-1)** Is the Oracle using deprecated Chainlink functions?
- [ ] **[SOL-Defi-Oracle-2](checklist-reference.md#sol-defi-oracle-2)** Is the returned price validated to be non-zero?
- [ ] **[SOL-Defi-Oracle-3](checklist-reference.md#sol-defi-oracle-3)** Is the price update time validated?
- [ ] **[SOL-Defi-Oracle-4](checklist-reference.md#sol-defi-oracle-4)** Is there a validation to check if the rollup sequencer is running?
- [ ] **[SOL-Defi-Oracle-5](checklist-reference.md#sol-defi-oracle-5)** Is the Oracle's TWAP period appropriately set?
- [ ] **[SOL-Defi-Oracle-6](checklist-reference.md#sol-defi-oracle-6)** Is the desired price feed pair supported across all deployed chains?
- [ ] **[SOL-Defi-Oracle-7](checklist-reference.md#sol-defi-oracle-7)** Is the heartbeat of the price feed suitable for the use case?
- [ ] **[SOL-Defi-Oracle-8](checklist-reference.md#sol-defi-oracle-8)** Are there any inconsistencies with decimal precision when using different price feeds?
- [ ] **[SOL-Defi-Oracle-9](checklist-reference.md#sol-defi-oracle-9)** Is the price feed address hard-coded?
- [ ] **[SOL-Defi-Oracle-10](checklist-reference.md#sol-defi-oracle-10)** What happens if oracle price updates are front-run?
- [ ] **[SOL-Defi-Oracle-11](checklist-reference.md#sol-defi-oracle-11)** How does the system handle potential oracle reverts?
- [ ] **[SOL-Defi-Oracle-12](checklist-reference.md#sol-defi-oracle-12)** Are the price feeds appropriate for the underlying assets?
- [ ] **[SOL-Defi-Oracle-13](checklist-reference.md#sol-defi-oracle-13)** Is the contract vulnerable to oracle manipulation, especially using spot prices from AMMs?
- [ ] **[SOL-Defi-Oracle-14](checklist-reference.md#sol-defi-oracle-14)** How does the system address potential inaccuracies during flash crashes?

*Integrations › Balancer*

- [ ] **[SOL-Integrations-Balancer-2](checklist-reference.md#sol-integrations-balancer-2)** Does the protocol use Balancer's Oracle? (getTimeWeightedAverage)
- [ ] **[SOL-Integrations-Balancer-4](checklist-reference.md#sol-integrations-balancer-4)** Does the protocol use Balancer vault pool liquidity status for any pricing?

*Integrations › Uniswap*

- [ ] **[SOL-Integrations-Uniswap-5](checklist-reference.md#sol-integrations-uniswap-5)** Is there a reliance on pool reserves?
- [ ] **[SOL-Integrations-Uniswap-9](checklist-reference.md#sol-integrations-uniswap-9)** Is `pool.slot0` being used to calculate sensitive information like current price and exchange rates?

## 5. Flash Loans & Atomic Composition

Notes: [`knowledge-base/vulnerabilities/flash-loans.md`](../knowledge-base/vulnerabilities/flash-loans.md) · Case studies: [2022-04-30 Rari Capital Fuse pools (~$80M)](../knowledge-base/case-studies/2022-04-30-rari-fei-fuse-reentrancy.md), [2022-04-16 Beanstalk Farms (~$182M)](../knowledge-base/case-studies/2022-04-16-beanstalk-flash-loan-governance.md), [2021-10-27 C.R.E.A.M. Finance (~$130M)](../knowledge-base/case-studies/2021-10-27-cream-finance-yusd-price-manipulation.md), [2021-05-19 PancakeBunny (~$45M)](../knowledge-base/case-studies/2021-05-19-pancakebunny-flash-loan-lp-pricing.md), [2020-10-26 Harvest Finance fUSDC / fUSDT vaults (~$33.8M)](../knowledge-base/case-studies/2020-10-26-harvest-finance-curve-pool-manipulation.md)

**Core**

- [ ] **[SC-FLASH-1](checklist-reference.md#sc-flash-1)** Can any invariant be broken *within a single transaction* using borrowed capital?
- [ ] **[SC-FLASH-2](checklist-reference.md#sc-flash-2)** Are governance votes / share prices / collateral ratios read at a point an attacker can inflate atomically?
- [ ] **[SC-FLASH-3](checklist-reference.md#sc-flash-3)** Does the protocol assume "an attacker can't have $100M"? (they can, for one block)

**Extended (Cyfrin / Solodit)**

*Defi › FlashLoan*

- [ ] **[SOL-Defi-FlashLoan-1](checklist-reference.md#sol-defi-flashloan-1)** Is withdraw disabled in the same block to prevent flashloan attacks?
- [ ] **[SOL-Defi-FlashLoan-2](checklist-reference.md#sol-defi-flashloan-2)** Can ERC4626 be manipulated through flashloans?

*Defi › General*

- [ ] **[SOL-Defi-General-8](checklist-reference.md#sol-defi-general-8)** Is it possible to withdraw in the same transaction of deposit?

*Integrations › AAVE / Compound*

- [ ] **[SOL-Integrations-AC-6](checklist-reference.md#sol-integrations-ac-6)** Do flash loans on Aave inflate the pool index?

*Integrations › Balancer*

- [ ] **[SOL-Integrations-Balancer-1](checklist-reference.md#sol-integrations-balancer-1)** Does the protocol use the Balancer's flashloan?

*Token › Fungible : ERC20*

- [ ] **[SOL-Token-FE-9](checklist-reference.md#sol-token-fe-9)** Is there a flash-mint functionality?

## 6. DeFi Business Logic

Notes: [`knowledge-base/vulnerabilities/defi-logic.md`](../knowledge-base/vulnerabilities/defi-logic.md) · Case studies: [2023-04-15 Hundred Finance (~$7M)](../knowledge-base/case-studies/2023-04-15-hundred-finance-empty-market-exchange-rate.md), [2023-03-13 Euler Finance (~$197M)](../knowledge-base/case-studies/2023-03-13-euler-finance-donate-to-reserves.md), [2023-02-17 Platypus Finance (~$8.5M)](../knowledge-base/case-studies/2023-02-17-platypus-emergency-withdraw-solvency.md), [2021-04-28 Uranium Finance (~$50M)](../knowledge-base/case-studies/2021-04-28-uranium-finance-k-constant-typo.md)

**Core**

- [ ] **[SC-DEFI-1](checklist-reference.md#sc-defi-1)** Lending: are collateral factor, health factor, and liquidation math correct at the boundaries? Can a position be made unliquidatable, or self-liquidated for profit?
- [ ] **[SC-DEFI-2](checklist-reference.md#sc-defi-2)** AMM: are the swap invariant (`x*y=k`), fees, and reserves updated atomically and in the right order?
- [ ] **[SC-DEFI-3](checklist-reference.md#sc-defi-3)** Staking/rewards: can rewards be double-claimed, claimed after unstake, or diluted/inflated via deposit timing?
- [ ] **[SC-DEFI-4](checklist-reference.md#sc-defi-4)** Vaults (ERC-4626): does `deposit`/`mint`/`withdraw`/`redeem` round in the protocol's favor? Is the first-deposit inflation attack mitigated?
- [ ] **[SC-DEFI-5](checklist-reference.md#sc-defi-5)** Fee logic: can fees be bypassed, set to values that break accounting, or round to zero?
- [ ] **[SC-DEFI-6](checklist-reference.md#sc-defi-6)** Slippage / deadline: are user-supplied `minOut` and `deadline` enforced?
- [ ] **[SC-DEFI-7](checklist-reference.md#sc-defi-7)** Do "emergency", "donate", "migrate" or "rescue" style functions re-run the same solvency / health / accounting checks as the normal path? (Euler `donateToReserves`, Platypus `emergencyWithdraw`)

**Extended (Cyfrin / Solodit)**

*Attacker's Mindset › Donation Attack*

- [ ] **[SOL-AM-DA-1](checklist-reference.md#sol-am-da-1)** Does the protocol rely on `balance` or `balanceOf` instead of internal accounting?

*Basics › Payment*

- [ ] **[SOL-Basics-Payment-3](checklist-reference.md#sol-basics-payment-3)** Are there vulnerabilities related to force-feeding?
- [ ] **[SOL-Basics-Payment-4](checklist-reference.md#sol-basics-payment-4)** What is the minimum deposit/withdrawal amount?

*Defi › AMM/Swap*

- [ ] **[SOL-Defi-AS-3](checklist-reference.md#sol-defi-as-3)** Is there a validation check for protocol reserves?
- [ ] **[SOL-Defi-AS-4](checklist-reference.md#sol-defi-as-4)** Does the AMM utilize forked code?
- [ ] **[SOL-Defi-AS-5](checklist-reference.md#sol-defi-as-5)** Are there rounding issues in product constant formulas?

*Defi › General*

- [ ] **[SOL-Defi-General-2](checklist-reference.md#sol-defi-general-2)** Are there unexpected rewards accruing for user deposited assets?
- [ ] **[SOL-Defi-General-3](checklist-reference.md#sol-defi-general-3)** Could direct transfers of funds introduce vulnerabilities?
- [ ] **[SOL-Defi-General-4](checklist-reference.md#sol-defi-general-4)** Could the initial deposit introduce any issues?
- [ ] **[SOL-Defi-General-7](checklist-reference.md#sol-defi-general-7)** What would happen if only 1 wei remains in the pool?

*Defi › Lending*

- [ ] **[SOL-Defi-Lending-1](checklist-reference.md#sol-defi-lending-1)** Will the liquidation process function effectively during rapid market downturns?
- [ ] **[SOL-Defi-Lending-2](checklist-reference.md#sol-defi-lending-2)** Can a position be liquidated if the loan remains unpaid or if the collateral falls below the required threshold?
- [ ] **[SOL-Defi-Lending-3](checklist-reference.md#sol-defi-lending-3)** Is it possible for a user to gain undue profit from self-liquidation?
- [ ] **[SOL-Defi-Lending-4](checklist-reference.md#sol-defi-lending-4)** If token transfers or collateral additions are temporarily paused, can a user still be liquidated, even if they intend to deposit more funds?
- [ ] **[SOL-Defi-Lending-5](checklist-reference.md#sol-defi-lending-5)** If liquidations are temporarily suspended, what are the implications when they are resumed?
- [ ] **[SOL-Defi-Lending-6](checklist-reference.md#sol-defi-lending-6)** Is it possible for users to manipulate the system by front-running and slightly increasing their collateral to prevent liquidations?
- [ ] **[SOL-Defi-Lending-7](checklist-reference.md#sol-defi-lending-7)** Are all positions, regardless of size, incentivized adequately for liquidation?
- [ ] **[SOL-Defi-Lending-8](checklist-reference.md#sol-defi-lending-8)** Is interest considered during Loan-to-Value (LTV) calculation?
- [ ] **[SOL-Defi-Lending-9](checklist-reference.md#sol-defi-lending-9)** Can liquidation and repaying be enabled or disabled simultaneously?
- [ ] **[SOL-Defi-Lending-10](checklist-reference.md#sol-defi-lending-10)** Is it possible to lend and borrow the same token within a single transaction?
- [ ] **[SOL-Defi-Lending-11](checklist-reference.md#sol-defi-lending-11)** Is there a scenario where a liquidator might receive a lesser amount than anticipated?
- [ ] **[SOL-Defi-Lending-12](checklist-reference.md#sol-defi-lending-12)** Is it possible for a user to be in a condition where they cannot repay their loan?

*Defi › Liquid Staking Derivatives*

- [ ] **[SOL-Defi-LSD-1](checklist-reference.md#sol-defi-lsd-1)** Can a malicious validator front-run setting withdrawal credentials?
- [ ] **[SOL-Defi-LSD-4](checklist-reference.md#sol-defi-lsd-4)** Can an arbitrary exchange rate be set when processing queued withdrawals?
- [ ] **[SOL-Defi-LSD-6](checklist-reference.md#sol-defi-lsd-6)** Can inter-related storage be corrupted, especially storage related to operators and validators?

*Defi › Staking*

- [ ] **[SOL-Defi-Staking-1](checklist-reference.md#sol-defi-staking-1)** Can a user amplify another user's time lock duration by stacking tokens on their behalf?
- [ ] **[SOL-Defi-Staking-2](checklist-reference.md#sol-defi-staking-2)** Can the distribution of rewards be unduly delayed or prematurely claimed?
- [ ] **[SOL-Defi-Staking-3](checklist-reference.md#sol-defi-staking-3)** Are rewards up-to-date in all use-cases?

*Heuristics*

- [ ] **[SOL-Heuristics-12](checklist-reference.md#sol-heuristics-12)** Can functions be invoked multiple times with identical parameters?
- [ ] **[SOL-Heuristics-16](checklist-reference.md#sol-heuristics-16)** Are there any code asymmetries?

*Integrations › AAVE / Compound*

- [ ] **[SOL-Integrations-AC-2](checklist-reference.md#sol-integrations-ac-2)** What happens if the utilization rate is too high, and collateral cannot be retrieved?
- [ ] **[SOL-Integrations-AC-3](checklist-reference.md#sol-integrations-ac-3)** What happens if the protocol is paused?
- [ ] **[SOL-Integrations-AC-4](checklist-reference.md#sol-integrations-ac-4)** What happens if the pool becomes deprecated?
- [ ] **[SOL-Integrations-AC-5](checklist-reference.md#sol-integrations-ac-5)** What happens if assets you lend/borrow are within the same eMode category?
- [ ] **[SOL-Integrations-AC-7](checklist-reference.md#sol-integrations-ac-7)** Does the protocol properly implement AAVE/COMP reward claims?
- [ ] **[SOL-Integrations-AC-8](checklist-reference.md#sol-integrations-ac-8)** On AAVE, what happens if a user reaches the maximum debt on an isolated asset?
- [ ] **[SOL-Integrations-AC-9](checklist-reference.md#sol-integrations-ac-9)** Does borrowing an AAVE siloed asset restrict borrowing other assets?

*Integrations › Balancer*

- [ ] **[SOL-Integrations-Balancer-3](checklist-reference.md#sol-integrations-balancer-3)** Does the protocol use Balancer's Boosted Pool?

*Integrations › Uniswap*

- [ ] **[SOL-Integrations-Uniswap-2](checklist-reference.md#sol-integrations-uniswap-2)** Are there refunds after swaps?
- [ ] **[SOL-Integrations-Uniswap-10](checklist-reference.md#sol-integrations-uniswap-10)** Is a hard-coded fee tier parameter being used?

## 7. Upgradeability & Proxies

Notes: [`knowledge-base/vulnerabilities/upgradeability.md`](../knowledge-base/vulnerabilities/upgradeability.md) · Case studies: [2022-07-23 Audius (704 ETH)](../knowledge-base/case-studies/2022-07-23-audius-storage-collision-governance.md)

**Core**

- [ ] **[SC-PROXY-1](checklist-reference.md#sc-proxy-1)** Storage layout: does an upgrade risk a **storage collision** with the old layout?
- [ ] **[SC-PROXY-2](checklist-reference.md#sc-proxy-2)** Is the implementation contract left **uninitialized** (attacker can init & self-destruct/`delegatecall`)?
- [ ] **[SC-PROXY-3](checklist-reference.md#sc-proxy-3)** `delegatecall` to untrusted targets? Function-selector clashes between proxy and impl?
- [ ] **[SC-PROXY-4](checklist-reference.md#sc-proxy-4)** Are `__gap` slots reserved in upgradeable base contracts?
- [ ] **[SC-PROXY-5](checklist-reference.md#sc-proxy-5)** Who can upgrade, and is that authority appropriately decentralized/timelocked?
- [ ] **[SC-PROXY-6](checklist-reference.md#sc-proxy-6)** Does the proxy's own storage (admin, implementation, init flags) overlap the implementation's variables, so that `initialize` reads as never run and can be re-executed?

**Extended (Cyfrin / Solodit)**

*Basics › Initialization*

- [ ] **[SOL-Basics-Initialization-2](checklist-reference.md#sol-basics-initialization-2)** Has the contract inherited OpenZeppelin's Initializable?
- [ ] **[SOL-Basics-Initialization-3](checklist-reference.md#sol-basics-initialization-3)** Does the contract have a separate initializer function other than a constructor?

*Basics › Proxy/Upgradable*

- [ ] **[SOL-Basics-PU-1](checklist-reference.md#sol-basics-pu-1)** Is there a constructor in the proxied contract?
- [ ] **[SOL-Basics-PU-2](checklist-reference.md#sol-basics-pu-2)** Is the `initializer` modifier applied to the `initialization()` function?
- [ ] **[SOL-Basics-PU-3](checklist-reference.md#sol-basics-pu-3)** Is the upgradable version used for initialization?
- [ ] **[SOL-Basics-PU-4](checklist-reference.md#sol-basics-pu-4)** Is the `authorizeUpgrade()` function properly secured in a UUPS setup?
- [ ] **[SOL-Basics-PU-5](checklist-reference.md#sol-basics-pu-5)** Is the contract initialized?
- [ ] **[SOL-Basics-PU-6](checklist-reference.md#sol-basics-pu-6)** Are `selfdestruct` and `delegatecall` used within the implementation contracts?
- [ ] **[SOL-Basics-PU-7](checklist-reference.md#sol-basics-pu-7)** Are values in immutable variables preserved between upgrades?
- [ ] **[SOL-Basics-PU-8](checklist-reference.md#sol-basics-pu-8)** Has the contract inherited the correct branch of OpenZeppelin library?
- [ ] **[SOL-Basics-PU-9](checklist-reference.md#sol-basics-pu-9)** Could an upgrade of the contract result in storage collision?
- [ ] **[SOL-Basics-PU-10](checklist-reference.md#sol-basics-pu-10)** Are the order and types of storage variables consistent between upgrades?

## 8. Signatures, Proofs & Replay

Notes: [`knowledge-base/vulnerabilities/signatures.md`](../knowledge-base/vulnerabilities/signatures.md) · Case studies: [2022-01-18 Multichain / Anyswap `AnyswapV4Router.a… (~$1.4M)](../knowledge-base/case-studies/2022-01-18-multichain-anyswap-phantom-permit.md)

**Core**

- [ ] **[SC-SIG-1](checklist-reference.md#sc-sig-1)** Is every signed message bound to a **nonce**, and is the nonce consumed?
- [ ] **[SC-SIG-2](checklist-reference.md#sc-sig-2)** Is the signature bound to `chainId` and the contract address (EIP-712 domain)?
- [ ] **[SC-SIG-3](checklist-reference.md#sc-sig-3)** Is `ecrecover` checked against `address(0)` (malleability / invalid sig)?
- [ ] **[SC-SIG-4](checklist-reference.md#sc-sig-4)** Can a signature be replayed across chains, forks, or contract instances?
- [ ] **[SC-SIG-5](checklist-reference.md#sc-sig-5)** Are `v/r/s` malleability and signature-uniqueness assumptions safe?

**Extended (Cyfrin / Solodit)**

*Attacker's Mindset › Replay Attack*

- [ ] **[SOL-AM-ReplayAttack-1](checklist-reference.md#sol-am-replayattack-1)** Are there protections against replay attacks for failed transactions?
- [ ] **[SOL-AM-ReplayAttack-2](checklist-reference.md#sol-am-replayattack-2)** Is there protection against replaying signatures on different chains?

*Hash / Merkle Tree*

- [ ] **[SOL-HMT-1](checklist-reference.md#sol-hmt-1)** Is the Merkle tree vulnerable to front-running attacks?
- [ ] **[SOL-HMT-2](checklist-reference.md#sol-hmt-2)** Does the claim method validate `msg.sender`?
- [ ] **[SOL-HMT-3](checklist-reference.md#sol-hmt-3)** What is the result when passing a zero hash to the Merkle tree functions?
- [ ] **[SOL-HMT-4](checklist-reference.md#sol-hmt-4)** What occurs if the same proof is duplicated within the Merkle tree?
- [ ] **[SOL-HMT-5](checklist-reference.md#sol-hmt-5)** Are the leaves of the Merkle tree hashed with the claimable address included?

*Integrations › Gnosis Safe*

- [ ] **[SOL-Integrations-GS-2](checklist-reference.md#sol-integrations-gs-2)** Does the `execTransactionFromModule()` function increment the nonce?

*Signature*

- [ ] **[SOL-Signature-1](checklist-reference.md#sol-signature-1)** Are signatures guarded against replay attacks?
- [ ] **[SOL-Signature-2](checklist-reference.md#sol-signature-2)** Are signatures protected against malleability issues?
- [ ] **[SOL-Signature-3](checklist-reference.md#sol-signature-3)** Does the returned public key from the signature verification match the expected public key?
- [ ] **[SOL-Signature-4](checklist-reference.md#sol-signature-4)** Is the signature originating from the appropriate entity?
- [ ] **[SOL-Signature-5](checklist-reference.md#sol-signature-5)** If the signature has a deadline, is it still valid?

## 9. Denial of Service

Notes: [`knowledge-base/vulnerabilities/denial-of-service.md`](../knowledge-base/vulnerabilities/denial-of-service.md) · Case studies: [2022-04-23 Akutars / Aku Dreams NFT Dutch auction (11,539.5 ETH)](../knowledge-base/case-studies/2022-04-23-akutar-nft-refund-dos-and-locked-funds.md)

**Core**

- [ ] **[SC-DOS-1](checklist-reference.md#sc-dos-1)** Unbounded loops over user-growable arrays (can exceed block gas limit)?
- [ ] **[SC-DOS-2](checklist-reference.md#sc-dos-2)** Does a single failing external call (e.g. one recipient's transfer reverting) block a whole batch / the whole protocol? (push vs. pull payments)
- [ ] **[SC-DOS-3](checklist-reference.md#sc-dos-3)** Can an attacker grief by forcing gas costs, filling a queue, or locking funds?
- [ ] **[SC-DOS-4](checklist-reference.md#sc-dos-4)** Does the protocol handle a token that reverts on zero-value transfer?
- [ ] **[SC-DOS-5](checklist-reference.md#sc-dos-5)** Can a `require` in a refund / claim / settlement path be made permanently false (counter mismatch, one reverting recipient), locking every user's funds?

**Extended (Cyfrin / Solodit)**

*Attacker's Mindset › Denial-Of-Service(DOS) Attack*

- [ ] **[SOL-AM-DOSA-1](checklist-reference.md#sol-am-dosa-1)** Is the withdrawal pattern followed to prevent denial of service?
- [ ] **[SOL-AM-DOSA-2](checklist-reference.md#sol-am-dosa-2)** Is there a minimum transaction amount enforced?
- [ ] **[SOL-AM-DOSA-3](checklist-reference.md#sol-am-dosa-3)** How does the protocol handle tokens with blacklisting functionality?
- [ ] **[SOL-AM-DOSA-4](checklist-reference.md#sol-am-dosa-4)** Can forcing the protocol to process a queue lead to DOS?
- [ ] **[SOL-AM-DOSA-5](checklist-reference.md#sol-am-dosa-5)** What happens with low decimal tokens that might cause DOS?
- [ ] **[SOL-AM-DOSA-6](checklist-reference.md#sol-am-dosa-6)** Does the protocol handle external contract interactions safely?

*Attacker's Mindset › Griefing Attack*

- [ ] **[SOL-AM-GA-1](checklist-reference.md#sol-am-ga-1)** Is there an external function that relies on states that can be changed by others?
- [ ] **[SOL-AM-GA-2](checklist-reference.md#sol-am-ga-2)** Can the contract operations be manipulated with precise gas limit specifications?

*Basics › Array / Loop*

- [ ] **[SOL-Basics-AL-9](checklist-reference.md#sol-basics-al-9)** Is there possibility of iteration of a huge array?
- [ ] **[SOL-Basics-AL-10](checklist-reference.md#sol-basics-al-10)** Is there a potential for a Denial-of-Service (DoS) attack in the loop?
- [ ] **[SOL-Basics-AL-12](checklist-reference.md#sol-basics-al-12)** Is there a loop to handle batch fund transfer?

*Basics › Payment*

- [ ] **[SOL-Basics-Payment-1](checklist-reference.md#sol-basics-payment-1)** Is it possible for the receiver to revert?
- [ ] **[SOL-Basics-Payment-5](checklist-reference.md#sol-basics-payment-5)** How is the withdrawal handled?
- [ ] **[SOL-Basics-Payment-7](checklist-reference.md#sol-basics-payment-7)** Is it possible for native ETH to be locked in the contract?

*Defi › Liquid Staking Derivatives*

- [ ] **[SOL-Defi-LSD-7](checklist-reference.md#sol-defi-lsd-7)** Does the protocol iterate over the entire set of operators or validators?

## 10. Token Integration Quirks

Notes: [`knowledge-base/vulnerabilities/token-integration.md`](../knowledge-base/vulnerabilities/token-integration.md) · Case studies: [2022-03-15 Hundred Finance (~$6.2M)](../knowledge-base/case-studies/2022-03-15-hundred-finance-erc677-hook-reentrancy.md), [2022-01-18 Multichain / Anyswap `AnyswapV4Router.a… (~$1.4M)](../knowledge-base/case-studies/2022-01-18-multichain-anyswap-phantom-permit.md)

**Core**

- [ ] **[SC-TOKEN-1](checklist-reference.md#sc-token-1)** **Fee-on-transfer**: does the code assume received == sent amount?
- [ ] **[SC-TOKEN-2](checklist-reference.md#sc-token-2)** **Rebasing tokens**: does cached balance drift from actual balance?
- [ ] **[SC-TOKEN-3](checklist-reference.md#sc-token-3)** **Missing return value** ERC-20s (USDT): is `SafeERC20`/`safeTransfer` used?
- [ ] **[SC-TOKEN-4](checklist-reference.md#sc-token-4)** **ERC-777 / hook tokens** (ERC-677 `transferAndCall`, ERC-1363) enabling reentrancy on transfer?
- [ ] **[SC-TOKEN-5](checklist-reference.md#sc-token-5)** **Non-standard decimals** (e.g. USDC=6, WBTC=8) handled?
- [ ] **[SC-TOKEN-6](checklist-reference.md#sc-token-6)** **Approval race** / double-spend on non-zero→non-zero approve?
- [ ] **[SC-TOKEN-7](checklist-reference.md#sc-token-7)** **Phantom functions**: does the code call `permit` or other optional functions on tokens that may not implement them, where a `fallback` (WETH) or a codeless address makes the call "succeed"?

**Extended (Cyfrin / Solodit)**

*Defi › AMM/Swap*

- [ ] **[SOL-Defi-AS-8](checklist-reference.md#sol-defi-as-8)** Does the AMM properly handle tokens of varying decimal configurations and token types?
- [ ] **[SOL-Defi-AS-9](checklist-reference.md#sol-defi-as-9)** Does the AMM support the fee-on-transfer tokens?
- [ ] **[SOL-Defi-AS-10](checklist-reference.md#sol-defi-as-10)** Does the AMM support the rebasing tokens?

*Defi › General*

- [ ] **[SOL-Defi-General-1](checklist-reference.md#sol-defi-general-1)** Can the protocol handle ERC20 tokens with decimals other than 18?
- [ ] **[SOL-Defi-General-6](checklist-reference.md#sol-defi-general-6)** Does the protocol revert on maximum approval to prevent over-allowance?
- [ ] **[SOL-Defi-General-9](checklist-reference.md#sol-defi-general-9)** Does the protocol aim to support ALL kinds of ERC20 tokens?

*Heuristics*

- [ ] **[SOL-Heuristics-14](checklist-reference.md#sol-heuristics-14)** Is ETH/WETH handling implemented correctly?

*Integrations › AAVE / Compound*

- [ ] **[SOL-Integrations-AC-1](checklist-reference.md#sol-integrations-ac-1)** Does the protocol use cETH token?

*Integrations › LSD › cbETH*

- [ ] **[SOL-Integrations-LSD-cbETH-1](checklist-reference.md#sol-integrations-lsd-cbeth-1)** How is the control over the `cbETH`/`ETH` rate determined? Are there specific addresses with this capability due to the `onlyOracle` modifier?
- [ ] **[SOL-Integrations-LSD-cbETH-2](checklist-reference.md#sol-integrations-lsd-cbeth-2)** How does the system handle potential decreases in the `cbETH`/`ETH` rate?

*Integrations › LSD › rETH*

- [ ] **[SOL-Integrations-LSD-rETH-1](checklist-reference.md#sol-integrations-lsd-reth-1)** Does the application account for potential penalties or slashes?
- [ ] **[SOL-Integrations-LSD-rETH-2](checklist-reference.md#sol-integrations-lsd-reth-2)** How does the system manage rewards accrued from staking?
- [ ] **[SOL-Integrations-LSD-rETH-3](checklist-reference.md#sol-integrations-lsd-reth-3)** Does the application handle potential reverts in the `burn()` function when there's insufficient ether in the `RocketDepositPool`?
- [ ] **[SOL-Integrations-LSD-rETH-4](checklist-reference.md#sol-integrations-lsd-reth-4)** What measures are in place to counteract potential consensus attacks on RPL nodes?
- [ ] **[SOL-Integrations-LSD-rETH-5](checklist-reference.md#sol-integrations-lsd-reth-5)** How does the system handle the conversion between `ETH` and `rETH`?

*Integrations › LSD › sfrxETH*

- [ ] **[SOL-Integrations-LSD-sfrxETH-1](checklist-reference.md#sol-integrations-lsd-sfrxeth-1)** How does the system handle potential detachment of `sfrxETH` from `frxETH` during reward transfers?
- [ ] **[SOL-Integrations-LSD-sfrxETH-2](checklist-reference.md#sol-integrations-lsd-sfrxeth-2)** Is the stability of the `sfrxETH`/`ETH` rate guaranteed or can it decrease in the future?

*Integrations › LSD › stETH*

- [ ] **[SOL-Integrations-LSD-stETH-1](checklist-reference.md#sol-integrations-lsd-steth-1)** Is the application aware that `stETH` is a rebasing token?
- [ ] **[SOL-Integrations-LSD-stETH-2](checklist-reference.md#sol-integrations-lsd-steth-2)** Are you aware of the overhead when withdrawing `stETH`/`wstETH`?
- [ ] **[SOL-Integrations-LSD-stETH-3](checklist-reference.md#sol-integrations-lsd-steth-3)** Does the application handle conversions between `stETH` and `wstETH` correctly?

*Token › Fungible : ERC20*

- [ ] **[SOL-Token-FE-1](checklist-reference.md#sol-token-fe-1)** Are safe transfer functions used throughout the contract?
- [ ] **[SOL-Token-FE-2](checklist-reference.md#sol-token-fe-2)** Is there potential for a race condition for approvals?
- [ ] **[SOL-Token-FE-3](checklist-reference.md#sol-token-fe-3)** Could a difference in decimals between ERC20 tokens cause issues?
- [ ] **[SOL-Token-FE-4](checklist-reference.md#sol-token-fe-4)** Does the token implement any form of address whitelisting, blacklisting, or checks?
- [ ] **[SOL-Token-FE-5](checklist-reference.md#sol-token-fe-5)** Could the use of multiple addresses for a single token lead to complications?
- [ ] **[SOL-Token-FE-6](checklist-reference.md#sol-token-fe-6)** Does the token charge fee on transfer?
- [ ] **[SOL-Token-FE-7](checklist-reference.md#sol-token-fe-7)** Can the token be ERC777?
- [ ] **[SOL-Token-FE-8](checklist-reference.md#sol-token-fe-8)** Does the protocol use Solmate's `ERC20.safeTransferLib`?
- [ ] **[SOL-Token-FE-10](checklist-reference.md#sol-token-fe-10)** What happens on zero amount transfer?
- [ ] **[SOL-Token-FE-11](checklist-reference.md#sol-token-fe-11)** Is the token an ERC2612 implementation?
- [ ] **[SOL-Token-FE-12](checklist-reference.md#sol-token-fe-12)** Can the token be sent to any address?
- [ ] **[SOL-Token-FE-13](checklist-reference.md#sol-token-fe-13)** Is there a direct approval to a non-zero value?
- [ ] **[SOL-Token-FE-14](checklist-reference.md#sol-token-fe-14)** Is there a max approval used?
- [ ] **[SOL-Token-FE-15](checklist-reference.md#sol-token-fe-15)** Can the token be paused?
- [ ] **[SOL-Token-FE-16](checklist-reference.md#sol-token-fe-16)** Is the decrease allowance feature of transferFrom() handled correctly when the sender is the caller?

*Token › Non-fungible : ERC721/1155*

- [ ] **[SOL-Token-NfE1-1](checklist-reference.md#sol-token-nfe1-1)** How are the minting and transfer implemented?
- [ ] **[SOL-Token-NfE1-4](checklist-reference.md#sol-token-nfe1-4)** Is it possible to steal NFT abusing his approval?
- [ ] **[SOL-Token-NfE1-5](checklist-reference.md#sol-token-nfe1-5)** Does the ERC721/1155 contract correctly implement supportsInterface?
- [ ] **[SOL-Token-NfE1-6](checklist-reference.md#sol-token-nfe1-6)** Can the contract support both ERC721 and ERC1155 standards?
- [ ] **[SOL-Token-NfE1-7](checklist-reference.md#sol-token-nfe1-7)** What happens to the airdrops that are engaged to specific NFT?
- [ ] **[SOL-Token-NfE1-8](checklist-reference.md#sol-token-nfe1-8)** How is the approval/transfer handled for CryptoPunks collection?

## 11. Front-running / MEV

Notes: [`knowledge-base/vulnerabilities/front-running-mev.md`](../knowledge-base/vulnerabilities/front-running-mev.md) · Case studies: [2023-05-29 Jimbo's Protocol (~4,090 ETH)](../knowledge-base/case-studies/2023-05-29-jimbos-protocol-unprotected-rebalance.md)

**Core**

- [ ] **[SC-MEV-1](checklist-reference.md#sc-mev-1)** Can a pending tx be sandwiched for profit at the user's expense?
- [ ] **[SC-MEV-2](checklist-reference.md#sc-mev-2)** Is there a commit-reveal or slippage guard where ordering matters?
- [ ] **[SC-MEV-3](checklist-reference.md#sc-mev-3)** Can an attacker front-run initialization, a first deposit, or a claim?
- [ ] **[SC-MEV-4](checklist-reference.md#sc-mev-4)** Are `minAmountOut` and `deadline` enforced on every swap path?
- [ ] **[SC-MEV-5](checklist-reference.md#sc-mev-5)** Do protocol-owned or automated operations (rebalances, fee conversions, liquidity shifts, harvests) execute swaps without slippage or price-band bounds?

**Extended (Cyfrin / Solodit)**

*Attacker's Mindset › Front-running Attack*

- [ ] **[SOL-AM-FrA-1](checklist-reference.md#sol-am-fra-1)** Are "get-or-create" patterns protected against front-running attacks?
- [ ] **[SOL-AM-FrA-2](checklist-reference.md#sol-am-fra-2)** Are two-transaction actions designed to be safe from frontrunning?
- [ ] **[SOL-AM-FrA-3](checklist-reference.md#sol-am-fra-3)** Can users maliciously cause others' transactions to revert by preempting with dust?
- [ ] **[SOL-AM-FrA-4](checklist-reference.md#sol-am-fra-4)** Is the protocol using a properly user-bound commit-reveal scheme?

*Attacker's Mindset › Miner Attack*

- [ ] **[SOL-AM-MA-1](checklist-reference.md#sol-am-ma-1)** Is block.timestamp used for time-sensitive operations?
- [ ] **[SOL-AM-MA-3](checklist-reference.md#sol-am-ma-3)** Is contract logic sensitive to transaction ordering?

*Attacker's Mindset › Sandwich Attack*

- [ ] **[SOL-AM-SandwichAttack-1](checklist-reference.md#sol-am-sandwichattack-1)** Does the protocol have an explicit slippage protection on user interactions?

*Basics › Block Reorganization*

- [ ] **[SOL-Basics-BR-1](checklist-reference.md#sol-basics-br-1)** Does the protocol implement a factory pattern using the CREATE opcode?

*Basics › Function*

- [ ] **[SOL-Basics-Function-3](checklist-reference.md#sol-basics-function-3)** Can the function be front-run?

*Defi › AMM/Swap*

- [ ] **[SOL-Defi-AS-1](checklist-reference.md#sol-defi-as-1)** Is hardcoded slippage used?
- [ ] **[SOL-Defi-AS-2](checklist-reference.md#sol-defi-as-2)** Is there a deadline protection?
- [ ] **[SOL-Defi-AS-7](checklist-reference.md#sol-defi-as-7)** Is there a mechanism in place to protect against excessive slippage?
- [ ] **[SOL-Defi-AS-11](checklist-reference.md#sol-defi-as-11)** Does the protocol calculate `minAmountOut` before a token swap?
- [ ] **[SOL-Defi-AS-13](checklist-reference.md#sol-defi-as-13)** Is the slippage calculated on-chain?
- [ ] **[SOL-Defi-AS-14](checklist-reference.md#sol-defi-as-14)** Is the slippage parameter enforced at the last step before transferring funds to users?

*Defi › Liquid Staking Derivatives*

- [ ] **[SOL-Defi-LSD-2](checklist-reference.md#sol-defi-lsd-2)** Can the exchange rate repricing update be sandwich attacked to drain ETH from the protocol?

*Integrations › Uniswap*

- [ ] **[SOL-Integrations-Uniswap-1](checklist-reference.md#sol-integrations-uniswap-1)** Is the slippage calculated on-chain?
- [ ] **[SOL-Integrations-Uniswap-8](checklist-reference.md#sol-integrations-uniswap-8)** Is the slippage parameter enforced at the last step before transferring funds to users?

## 12. General Solidity Hygiene

Case studies: [2021-04-28 Uranium Finance (~$50M)](../knowledge-base/case-studies/2021-04-28-uranium-finance-k-constant-typo.md)

**Core**

- [ ] **[SC-HYG-1](checklist-reference.md#sc-hyg-1)** Uninitialized storage pointers; `delete` on structs with mappings.
- [ ] **[SC-HYG-2](checklist-reference.md#sc-hyg-2)** Correct handling of `address(this).balance` vs. accounting variables.
- [ ] **[SC-HYG-3](checklist-reference.md#sc-hyg-3)** Events emitted for every state change (for off-chain integrity)?
- [ ] **[SC-HYG-4](checklist-reference.md#sc-hyg-4)** Deprecated constructs (`selfdestruct`, `tx.origin`, `block.difficulty`) reviewed?
- [ ] **[SC-HYG-5](checklist-reference.md#sc-hyg-5)** Have the compiler version and library versions (OpenZeppelin, Solmate) been checked against Appendix A (known compiler and library bugs)?
- [ ] **[SC-HYG-6](checklist-reference.md#sc-hyg-6)** Forked or copied code: were constants, fee denominators and formulas diffed line by line against the upstream (Uniswap, Compound, OpenZeppelin) they came from?

**Extended (Cyfrin / Solodit)**

*Basics › Array / Loop*

- [ ] **[SOL-Basics-AL-1](checklist-reference.md#sol-basics-al-1)** What happens on the first and the last cycle of the iteration?
- [ ] **[SOL-Basics-AL-4](checklist-reference.md#sol-basics-al-4)** How does the protocol remove an item from an array?
- [ ] **[SOL-Basics-AL-6](checklist-reference.md#sol-basics-al-6)** Is the summing of variables done accurately compared to separate calculations?
- [ ] **[SOL-Basics-AL-8](checklist-reference.md#sol-basics-al-8)** Is there any issue with the first and the last iteration?
- [ ] **[SOL-Basics-AL-13](checklist-reference.md#sol-basics-al-13)** Is there a break or continue inside a loop?

*Basics › Event*

- [ ] **[SOL-Basics-Event-1](checklist-reference.md#sol-basics-event-1)** Does the protocol emit events on important state changes?

*Basics › Function*

- [ ] **[SOL-Basics-Function-4](checklist-reference.md#sol-basics-function-4)** Are the code comments coherent with the implementation?

*Basics › Inheritance*

- [ ] **[SOL-Basics-Inheritance-2](checklist-reference.md#sol-basics-inheritance-2)** Were all necessary functions implemented to fulfill inheritance purpose?
- [ ] **[SOL-Basics-Inheritance-3](checklist-reference.md#sol-basics-inheritance-3)** Has the contract implemented an interface?
- [ ] **[SOL-Basics-Inheritance-4](checklist-reference.md#sol-basics-inheritance-4)** Does the inheritance order matter?

*Basics › Map*

- [ ] **[SOL-Basics-Map-1](checklist-reference.md#sol-basics-map-1)** Is there need to delete the existing item from a map?

*Heuristics*

- [ ] **[SOL-Heuristics-1](checklist-reference.md#sol-heuristics-1)** Is there any logic implemented multiple times?
- [ ] **[SOL-Heuristics-2](checklist-reference.md#sol-heuristics-2)** Does the contract use any nested structures?
- [ ] **[SOL-Heuristics-6](checklist-reference.md#sol-heuristics-6)** Did you check the relevant EIP recommendations and security concerns?
- [ ] **[SOL-Heuristics-8](checklist-reference.md#sol-heuristics-8)** Are logical operators used correctly?
- [ ] **[SOL-Heuristics-13](checklist-reference.md#sol-heuristics-13)** Is the global state updated correctly?
- [ ] **[SOL-Heuristics-15](checklist-reference.md#sol-heuristics-15)** Does the protocol put any sensitive data on the blockchain?

## 13. Weak Randomness

Notes: [`knowledge-base/vulnerabilities/randomness.md`](../knowledge-base/vulnerabilities/randomness.md)

**Core**

- [ ] **[SC-RAND-1](checklist-reference.md#sc-rand-1)** Is `block.timestamp` / `blockhash` / `prevrandao` used as randomness for a value-bearing outcome? (predictable + validator-influenced)
- [ ] **[SC-RAND-2](checklist-reference.md#sc-rand-2)** Can the caller precompute the result in the same tx and revert on a loss?
- [ ] **[SC-RAND-3](checklist-reference.md#sc-rand-3)** Is a verifiable source (Chainlink VRF) or a sound commit-reveal used instead?

**Extended (Cyfrin / Solodit)**

*Attacker's Mindset › Miner Attack*

- [ ] **[SOL-AM-MA-2](checklist-reference.md#sol-am-ma-2)** Is the contract using block properties like timestamp or difficulty for randomness generation?

*Integrations › Chainlink › VRF*

- [ ] **[SOL-Integrations-Chainlink-VRF-1](checklist-reference.md#sol-integrations-chainlink-vrf-1)** Are all parameters properly verified when Chainlink VRF is called?
- [ ] **[SOL-Integrations-Chainlink-VRF-2](checklist-reference.md#sol-integrations-chainlink-vrf-2)** Is it guaranteed that the operator holds sufficient LINK in the subscription?
- [ ] **[SOL-Integrations-Chainlink-VRF-3](checklist-reference.md#sol-integrations-chainlink-vrf-3)** Is a sufficiently high request confirmation number chosen considering chain re-orgs?
- [ ] **[SOL-Integrations-Chainlink-VRF-4](checklist-reference.md#sol-integrations-chainlink-vrf-4)** Are measures in place to prevent VRF calls from being frontrun?

## 14. Governance

Notes: [`knowledge-base/vulnerabilities/governance.md`](../knowledge-base/vulnerabilities/governance.md) · Case studies: [2022-07-23 Audius (704 ETH)](../knowledge-base/case-studies/2022-07-23-audius-storage-collision-governance.md), [2022-04-16 Beanstalk Farms (~$182M)](../knowledge-base/case-studies/2022-04-16-beanstalk-flash-loan-governance.md)

**Core**

- [ ] **[SC-GOV-1](checklist-reference.md#sc-gov-1)** Is voting power snapshotted at a **past block**, not read from current balance?
- [ ] **[SC-GOV-2](checklist-reference.md#sc-gov-2)** Is there a **timelock** between a proposal passing and executing?
- [ ] **[SC-GOV-3](checklist-reference.md#sc-gov-3)** Can a flash loan / large holder reach quorum atomically?
- [ ] **[SC-GOV-4](checklist-reference.md#sc-gov-4)** What is `execute` allowed to call: treasury, upgrades, arbitrary targets?
- [ ] **[SC-GOV-5](checklist-reference.md#sc-gov-5)** Can the code a proposal executes change between vote and execution (metamorphic contract via `CREATE2` + `selfdestruct`, upgradeable target, unpinned bytecode)?

**Extended (Cyfrin / Solodit)**

*Attacker's Mindset › Sybil Attack*

- [ ] **[SOL-AM-SybilAttack-1](checklist-reference.md#sol-am-sybilattack-1)** Is there a mechanism depending on the number of users?

*Timelock*

- [ ] **[SOL-Timelock-1](checklist-reference.md#sol-timelock-1)** Are timelocks implemented for important changes?

## 15. Bridges & Cross-Chain

Notes: [`knowledge-base/vulnerabilities/bridges-cross-chain.md`](../knowledge-base/vulnerabilities/bridges-cross-chain.md)

**Core**

- [ ] **[SC-BRIDGE-1](checklist-reference.md#sc-bridge-1)** Is the cross-chain message verified against the correct validator set/threshold?
- [ ] **[SC-BRIDGE-2](checklist-reference.md#sc-bridge-2)** Is a unique nonce / message id consumed to prevent replay?
- [ ] **[SC-BRIDGE-3](checklist-reference.md#sc-bridge-3)** Is the message bound to source chain, destination, and exact payload?
- [ ] **[SC-BRIDGE-4](checklist-reference.md#sc-bridge-4)** Are bridge init/upgrade paths tightly guarded? (Nomad/Wormhole/Ronin class)
- [ ] **[SC-BRIDGE-5](checklist-reference.md#sc-bridge-5)** Can a cross-chain message target a privileged contract of the bridge itself (config, keeper or validator-set contract) and pass its `onlyOwner` check because the executor is the owner?
- [ ] **[SC-BRIDGE-6](checklist-reference.md#sc-bridge-6)** Is the zero/default value of a trusted-root, confirmation or nonce mapping treated as valid or "confirmed"?

**Extended (Cyfrin / Solodit)**

*Integrations › Chainlink › CCIP*

- [ ] **[SOL-Integrations-Chainlink-CCIP-1](checklist-reference.md#sol-integrations-chainlink-ccip-1)** Does the receiver contract's `_ccipReceive` function properly validate the `sourceChainSelector` and `sender` address against an allowlist?
- [ ] **[SOL-Integrations-Chainlink-CCIP-2](checklist-reference.md#sol-integrations-chainlink-ccip-2)** Does the sender contract validate the `destinationChainSelector` against an allowlist before calling `ccipSend`?
- [ ] **[SOL-Integrations-Chainlink-CCIP-3](checklist-reference.md#sol-integrations-chainlink-ccip-3)** Does the receiver contract properly decode data (`any2EvmMessage.data`) ?
- [ ] **[SOL-Integrations-Chainlink-CCIP-4](checklist-reference.md#sol-integrations-chainlink-ccip-4)** Does the application logic account for the potential latency introduced by waiting for source chain finality as defined by CCIP?
- [ ] **[SOL-Integrations-Chainlink-CCIP-5](checklist-reference.md#sol-integrations-chainlink-ccip-5)** Are the correct types of token pools (e.g., `BurnMintTokenPool`, `LockReleaseTokenPool`) deployed on the source and destination chains consistent with the desired token handling mechanism?
- [ ] **[SOL-Integrations-Chainlink-CCIP-6](checklist-reference.md#sol-integrations-chainlink-ccip-6)** Is proper router address verification implemented in the ccipReceive method?
- [ ] **[SOL-Integrations-Chainlink-CCIP-7](checklist-reference.md#sol-integrations-chainlink-ccip-7)** Are extraArgs parameters hardcoded instead of mutable in cross-chain message configurations?
- [ ] **[SOL-Integrations-Chainlink-CCIP-8](checklist-reference.md#sol-integrations-chainlink-ccip-8)** Is there a proper failure handling mechanism for CCIP messages to prevent blocking after Smart Execution window expiration?

*Integrations › LayerZero*

- [ ] **[SOL-Integrations-LayerZero-1](checklist-reference.md#sol-integrations-layerzero-1)** Does the `_debitFrom` function in ONFT properly validate token ownership and transfer permissions?
- [ ] **[SOL-Integrations-LayerZero-2](checklist-reference.md#sol-integrations-layerzero-2)** Which type of mechanism are utilized? Blocking or non-blocking?
- [ ] **[SOL-Integrations-LayerZero-3](checklist-reference.md#sol-integrations-layerzero-3)** Is gas estimated accurately for cross-chain messages?
- [ ] **[SOL-Integrations-LayerZero-4](checklist-reference.md#sol-integrations-layerzero-4)** Is the `_lzSend` function correctly utilized when inheriting LzApp?
- [ ] **[SOL-Integrations-LayerZero-5](checklist-reference.md#sol-integrations-layerzero-5)** Is the `ILayerZeroUserApplicationConfig` interface correctly implemented?
- [ ] **[SOL-Integrations-LayerZero-6](checklist-reference.md#sol-integrations-layerzero-6)** Are default contracts used?
- [ ] **[SOL-Integrations-LayerZero-7](checklist-reference.md#sol-integrations-layerzero-7)** Is the correct number of confirmations chosen for the chain?

*Integrations › Uniswap*

- [ ] **[SOL-Integrations-Uniswap-3](checklist-reference.md#sol-integrations-uniswap-3)** Is the order of `token0` and `token1` consistent across chains?

*Multi-chain/Cross-chain*

- [ ] **[SOL-McCc-1](checklist-reference.md#sol-mccc-1)** Are there assumption of consistency in the `block.number` or `block.timestamp` across chains?
- [ ] **[SOL-McCc-2](checklist-reference.md#sol-mccc-2)** Has the protocol been checked for the target chain differences?
- [ ] **[SOL-McCc-3](checklist-reference.md#sol-mccc-3)** Are the EVM opcodes and operations used by the protocol compatible across all targeted chains?
- [ ] **[SOL-McCc-4](checklist-reference.md#sol-mccc-4)** Does the expected behavior of `tx.origin` and `msg.sender` remain consistent across all deployment chains?
- [ ] **[SOL-McCc-5](checklist-reference.md#sol-mccc-5)** Is there any possibility of exploiting low gas fees to execute many transactions?
- [ ] **[SOL-McCc-6](checklist-reference.md#sol-mccc-6)** Is there consistency in ERC20 decimals across chains?
- [ ] **[SOL-McCc-7](checklist-reference.md#sol-mccc-7)** Have contract upgradability implications been evaluated on different chains?
- [ ] **[SOL-McCc-8](checklist-reference.md#sol-mccc-8)** Have cross-chain messaging implementations been thoroughly reviewed for permissions and functionality?
- [ ] **[SOL-McCc-9](checklist-reference.md#sol-mccc-9)** Is there a whitelist of compatible chains?
- [ ] **[SOL-McCc-10](checklist-reference.md#sol-mccc-10)** Have contracts been checked for compatibility when deployed to the zkSync Era?
- [ ] **[SOL-McCc-11](checklist-reference.md#sol-mccc-11)** Is block production consistency ensured?
- [ ] **[SOL-McCc-12](checklist-reference.md#sol-mccc-12)** Is `PUSH0` opcode supported for Solidity version `>=0.8.20`?
- [ ] **[SOL-McCc-13](checklist-reference.md#sol-mccc-13)** Are there any attributes attached to the bridged assets?

## 16. Low-Level Calls & Return Data

Notes: [`knowledge-base/vulnerabilities/low-level-calls.md`](../knowledge-base/vulnerabilities/low-level-calls.md) · Case studies: [2022-01-18 Multichain / Anyswap `AnyswapV4Router.a… (~$1.4M)](../knowledge-base/case-studies/2022-01-18-multichain-anyswap-phantom-permit.md)

**Core**

- [ ] **[SC-LL-1](checklist-reference.md#sc-ll-1)** Is the `bool` from every `call`/`send`/`delegatecall` checked?
- [ ] **[SC-LL-2](checklist-reference.md#sc-ll-2)** Any `delegatecall` to an untrusted/user-controlled target?
- [ ] **[SC-LL-3](checklist-reference.md#sc-ll-3)** Can a callee return-bomb the caller (unbounded returndata)?
- [ ] **[SC-LL-4](checklist-reference.md#sc-ll-4)** Is a `call` to a possibly-codeless address treated as success? (phantom function)

**Extended (Cyfrin / Solodit)**

*Basics › Payment*

- [ ] **[SOL-Basics-Payment-6](checklist-reference.md#sol-basics-payment-6)** Is `transfer()` or `send()` used for sending ETH?

*External Call*

- [ ] **[SOL-EC-3](checklist-reference.md#sol-ec-3)** What are the risks associated with using delegatecall in smart contracts?
- [ ] **[SOL-EC-4](checklist-reference.md#sol-ec-4)** Is the external contract call necessary?
- [ ] **[SOL-EC-6](checklist-reference.md#sol-ec-6)** Is there suspicion when a fixed gas amount is specified?
- [ ] **[SOL-EC-7](checklist-reference.md#sol-ec-7)** What happens if the call consumes all provided gas?
- [ ] **[SOL-EC-8](checklist-reference.md#sol-ec-8)** Is the contract passing large data to an unknown address?
- [ ] **[SOL-EC-9](checklist-reference.md#sol-ec-9)** What happens if the call returns vast data?
- [ ] **[SOL-EC-10](checklist-reference.md#sol-ec-10)** Are there any delegate calls to non-library contracts?
- [ ] **[SOL-EC-11](checklist-reference.md#sol-ec-11)** Is there a strict policy against delegate calls to untrusted contracts?
- [ ] **[SOL-EC-12](checklist-reference.md#sol-ec-12)** Is the address's existence verified?

*Heuristics*

- [ ] **[SOL-Heuristics-5](checklist-reference.md#sol-heuristics-5)** Does the `try/catch` block account for potential gas shortages?

*Low Level*

- [ ] **[SOL-LL-1](checklist-reference.md#sol-ll-1)** Is there validation on the size of the input data?
- [ ] **[SOL-LL-2](checklist-reference.md#sol-ll-2)** What happens if there is no matching function signature?
- [ ] **[SOL-LL-3](checklist-reference.md#sol-ll-3)** Is it checked if the target address of a call has the code?
- [ ] **[SOL-LL-4](checklist-reference.md#sol-ll-4)** Is there a check on the return data size when calling precompiled code?

## 17. Input Validation & Uninitialized State

Notes: [`knowledge-base/vulnerabilities/input-validation.md`](../knowledge-base/vulnerabilities/input-validation.md)

**Core**

- [ ] **[SC-INPUT-1](checklist-reference.md#sc-input-1)** Zero-address checks on setters and transfers?
- [ ] **[SC-INPUT-2](checklist-reference.md#sc-input-2)** Zero-amount / dust edge cases handled without corrupting accounting?
- [ ] **[SC-INPUT-3](checklist-reference.md#sc-input-3)** Array-length equality checked in batch functions?
- [ ] **[SC-INPUT-4](checklist-reference.md#sc-input-4)** Every critical variable initialized before use; parameters range-checked?
- [ ] **[SC-INPUT-5](checklist-reference.md#sc-input-5)** Do callbacks (flash-loan, Uniswap `swap`/`mint`, ERC-721 receiver) verify `msg.sender` is the expected pool/lender and that the initiator is this contract?
- [ ] **[SC-INPUT-6](checklist-reference.md#sc-input-6)** Can user-supplied addresses or calldata make the contract perform an arbitrary external call (router, target, token), including `transferFrom` against other users' approvals?
- [ ] **[SC-INPUT-7](checklist-reference.md#sc-input-7)** Does any mapping lookup treat the zero/default value (`bytes32(0)`, `address(0)`, `0`) as valid or "confirmed"?

**Extended (Cyfrin / Solodit)**

*Basics › Array / Loop*

- [ ] **[SOL-Basics-AL-5](checklist-reference.md#sol-basics-al-5)** Does any function get an index of an array as an argument?
- [ ] **[SOL-Basics-AL-7](checklist-reference.md#sol-basics-al-7)** Is it fine to have duplicate items in the array?
- [ ] **[SOL-Basics-AL-11](checklist-reference.md#sol-basics-al-11)** Is `msg.value` used within a loop?

*Basics › Function*

- [ ] **[SOL-Basics-Function-1](checklist-reference.md#sol-basics-function-1)** Are the inputs validated?
- [ ] **[SOL-Basics-Function-2](checklist-reference.md#sol-basics-function-2)** Are the outputs validated?
- [ ] **[SOL-Basics-Function-5](checklist-reference.md#sol-basics-function-5)** Can edge case inputs (0, max) result in unexpected behavior?
- [ ] **[SOL-Basics-Function-6](checklist-reference.md#sol-basics-function-6)** Does the function allow arbitrary user input?

*Basics › Initialization*

- [ ] **[SOL-Basics-Initialization-1](checklist-reference.md#sol-basics-initialization-1)** Are important state variables initialized properly?

*Basics › Payment*

- [ ] **[SOL-Basics-Payment-2](checklist-reference.md#sol-basics-payment-2)** Does the function gets the payment amount as a parameter?

*Defi › AMM/Swap*

- [ ] **[SOL-Defi-AS-6](checklist-reference.md#sol-defi-as-6)** Can arbitrary calls be made from user input?
- [ ] **[SOL-Defi-AS-12](checklist-reference.md#sol-defi-as-12)** Does the integrating contract verify the caller address in its callback functions?

*External Call*

- [ ] **[SOL-EC-2](checklist-reference.md#sol-ec-2)** Is there a multi-call?
- [ ] **[SOL-EC-5](checklist-reference.md#sol-ec-5)** Has the called address been whitelisted?

*Heuristics*

- [ ] **[SOL-Heuristics-3](checklist-reference.md#sol-heuristics-3)** Is there any unexpected behavior when `src==dst` (or `caller==receiver`)?
- [ ] **[SOL-Heuristics-9](checklist-reference.md#sol-heuristics-9)** What happens if the protocol's contracts are inputted as if they are normal actors?
- [ ] **[SOL-Heuristics-11](checklist-reference.md#sol-heuristics-11)** Is there any uninitialized state?

*Integrations › Uniswap*

- [ ] **[SOL-Integrations-Uniswap-4](checklist-reference.md#sol-integrations-uniswap-4)** Are the pools that are being interacted with whitelisted?
- [ ] **[SOL-Integrations-Uniswap-6](checklist-reference.md#sol-integrations-uniswap-6)** Is `pool.swap()` directly used?

## Appendix A. Version-specific issues (compiler and library bugs)

Checks that only apply to a specific Solidity compiler range or OpenZeppelin release. Read the target's `pragma` and lock-file first, then walk only the rows whose version range matches. Referenced from SC-HYG-5.

### EIP Adoption Issues

- [ ] **[SOL-Basics-VI-EAI-1](checklist-reference.md#sol-basics-vi-eai-1)** EIP-4758: Does the contract use `selfdestruct()`?

### OpenZeppelin Version Issues

- [ ] **[SOL-Basics-VI-OVI-1](checklist-reference.md#sol-basics-vi-ovi-1)** Does the contract use `ERC2771Context`? (version >=4.0.0 <4.9.3)
- [ ] **[SOL-Basics-VI-OVI-2](checklist-reference.md#sol-basics-vi-ovi-2)** Does the contract use OpenZeppelin's GovernorCompatibilityBravo? (version >=4.3.0 <4.8.3)
- [ ] **[SOL-Basics-VI-OVI-3](checklist-reference.md#sol-basics-vi-ovi-3)** Does the contract use OpenZeppelin's ECDSA.recover or ECDSA.tryRecover? (version <4.7.3)
- [ ] **[SOL-Basics-VI-OVI-4](checklist-reference.md#sol-basics-vi-ovi-4)** Does the contract use OpenZeppelin's ERC777? (version <3.4.0-rc.0)
- [ ] **[SOL-Basics-VI-OVI-5](checklist-reference.md#sol-basics-vi-ovi-5)** Does the contract use OpenZeppelin's `MerkleProof`? (version >=4.7.0 <4.9.2)
- [ ] **[SOL-Basics-VI-OVI-6](checklist-reference.md#sol-basics-vi-ovi-6)** Does the contract use OpenZeppelin's Governor or GovernorCompatibilityBravo? (version >=4.3.0 <4.9.1)
- [ ] **[SOL-Basics-VI-OVI-7](checklist-reference.md#sol-basics-vi-ovi-7)** Does the contract use OpenZeppelin's TransparentUpgradeableProxy? (version >=3.2.0 <4.8.3)
- [ ] **[SOL-Basics-VI-OVI-8](checklist-reference.md#sol-basics-vi-ovi-8)** Does the contract use OpenZeppelin's ERC721Consecutive?(version >=4.8.0 <4.8.2)
- [ ] **[SOL-Basics-VI-OVI-9](checklist-reference.md#sol-basics-vi-ovi-9)** Does the contract use OpenZeppelin's ERC165Checker or ERC165CheckerUpgradeable? (version >=2.3.0 <4.7.2)
- [ ] **[SOL-Basics-VI-OVI-10](checklist-reference.md#sol-basics-vi-ovi-10)** Does the contract use OpenZeppelin's LibArbitrumL2 or CrossChainEnabledArbitrumL2? (version >=4.6.0 <4.7.2)
- [ ] **[SOL-Basics-VI-OVI-11](checklist-reference.md#sol-basics-vi-ovi-11)** Does the contract use OpenZeppelin's GovernorVotesQuorumFraction? (version >=4.3.0 <4.7.2)
- [ ] **[SOL-Basics-VI-OVI-12](checklist-reference.md#sol-basics-vi-ovi-12)** Does the contract use OpenZeppelin's SignatureChecker? (version >=4.1.0 <4.7.1)
- [ ] **[SOL-Basics-VI-OVI-13](checklist-reference.md#sol-basics-vi-ovi-13)** Does the contract use OpenZeppelin's ERC165Checker? (version >=4.0.0 <4.7.1)
- [ ] **[SOL-Basics-VI-OVI-14](checklist-reference.md#sol-basics-vi-ovi-14)** Does the contract use OpenZeppelin's GovernorCompatibilityBravo? (version >=4.3.0 <4.4.2)
- [ ] **[SOL-Basics-VI-OVI-15](checklist-reference.md#sol-basics-vi-ovi-15)** Does the contract use OpenZeppelin's Initializable? (version >=3.2.0 <4.4.1)
- [ ] **[SOL-Basics-VI-OVI-16](checklist-reference.md#sol-basics-vi-ovi-16)** Does the contract use OpenZeppelin's ERC1155? (version >=4.2.0 <4.3.3)
- [ ] **[SOL-Basics-VI-OVI-17](checklist-reference.md#sol-basics-vi-ovi-17)** Does the contract use OpenZeppelin's UUPSUpgradeable? (version >=4.1.0 <4.3.2)
- [ ] **[SOL-Basics-VI-OVI-18](checklist-reference.md#sol-basics-vi-ovi-18)** Does the contract use OpenZeppelin's TimelockController? (version >=4.0.0-beta.0 <4.3.1\\n<3.4.2)

### Solidity Version Issues

- [ ] **[SOL-Basics-VI-SVI-1](checklist-reference.md#sol-basics-vi-svi-1)** Does the contract encode storage structs or arrays with types under 32 bytes directly using experimental ABIEncoderV2? (version 0.5.0~0.5.6)
- [ ] **[SOL-Basics-VI-SVI-2](checklist-reference.md#sol-basics-vi-svi-2)** Are there any instances where empty strings are directly passed to function calls? (version ~0.4.11)
- [ ] **[SOL-Basics-VI-SVI-3](checklist-reference.md#sol-basics-vi-svi-3)** Does the optimizer replace specific constants with alternative computations? (version ~0.4.10)
- [ ] **[SOL-Basics-VI-SVI-4](checklist-reference.md#sol-basics-vi-svi-4)** Does the contract use `abi.encodePacked`, especially in hash generation? (version >= 0.8.17)
- [ ] **[SOL-Basics-VI-SVI-5](checklist-reference.md#sol-basics-vi-svi-5)** BUILD: Is the contract optimized using sequences containing FullInliner with non-expression-split code? (version 0.6.7~0.8.20)
- [ ] **[SOL-Basics-VI-SVI-6](checklist-reference.md#sol-basics-vi-svi-6)** Are there any functions that conditionally terminate inside an inline assembly? (version 0.8.13~0.8.16)
- [ ] **[SOL-Basics-VI-SVI-7](checklist-reference.md#sol-basics-vi-svi-7)** Are tuples containing a statically-sized calldata array at the end being ABI-encoded? (version 0.5.8~0.8.15)
- [ ] **[SOL-Basics-VI-SVI-8](checklist-reference.md#sol-basics-vi-svi-8)** Does the contract have functions that copy `bytes` arrays from memory or calldata directly to storage? (version 0.0.1~0.8.14)
- [ ] **[SOL-Basics-VI-SVI-9](checklist-reference.md#sol-basics-vi-svi-9)** Is there a function with multiple inline assembly blocks? (version 0.8.13~0.8.14)
- [ ] **[SOL-Basics-VI-SVI-10](checklist-reference.md#sol-basics-vi-svi-10)** Is a nested array being ABI-encoded or passed directly to an external function? (version 0.5.8~0.8.13)
- [ ] **[SOL-Basics-VI-SVI-11](checklist-reference.md#sol-basics-vi-svi-11)** Is `abi.encodeCall` used together with fixed-length bytes literals? (version 0.8.11~0.8.12)
- [ ] **[SOL-Basics-VI-SVI-12](checklist-reference.md#sol-basics-vi-svi-12)** Is there any user defined types based on types shorter than 32 bytes? (version =0.8.8)
- [ ] **[SOL-Basics-VI-SVI-13](checklist-reference.md#sol-basics-vi-svi-13)** Is there an immutable variable of signed integer type shorter than 256 bits? (version 0.6.5~0.8.8)
- [ ] **[SOL-Basics-VI-SVI-14](checklist-reference.md#sol-basics-vi-svi-14)** Is there any use of `abi.encode` on memory with multi-dimensional array or structs? (version 0.4.16~0.8.3)
- [ ] **[SOL-Basics-VI-SVI-15](checklist-reference.md#sol-basics-vi-svi-15)** Is there an inline assembly block with `keccak256` inside? (version ~0.8.2)
- [ ] **[SOL-Basics-VI-SVI-16](checklist-reference.md#sol-basics-vi-svi-16)** Is there a copy of an empty `bytes` or `string` from `memory` or `calldata` to `storage`? (version ~0.7.3)
- [ ] **[SOL-Basics-VI-SVI-17](checklist-reference.md#sol-basics-vi-svi-17)** Is there a dynamically-sized storage-array with types of size at most 16 bytes? (version ~0.7.2)
- [ ] **[SOL-Basics-VI-SVI-18](checklist-reference.md#sol-basics-vi-svi-18)** Does the library use contract types in events? (version 0.5.0~0.5.7)
- [ ] **[SOL-Basics-VI-SVI-19](checklist-reference.md#sol-basics-vi-svi-19)** Does the contract use internal library functions with calldata parameters via `using for`? (version =0.6.9)
- [ ] **[SOL-Basics-VI-SVI-20](checklist-reference.md#sol-basics-vi-svi-20)** Are string literals with double backslashes passed directly to external or encoding functions with ABIEncoderV2 enabled? (version 0.5.14~0.6.7)
- [ ] **[SOL-Basics-VI-SVI-21](checklist-reference.md#sol-basics-vi-svi-21)** Does the contract access slices of dynamic arrays, especially multi-dimensional ones? (version 0.6.0~0.6.7)
- [ ] **[SOL-Basics-VI-SVI-22](checklist-reference.md#sol-basics-vi-svi-22)** Is there a contract with creation code, no constructor, but a base with a constructor that accepts non-zero values? (version 0.4.5~0.6.7)
- [ ] **[SOL-Basics-VI-SVI-23](checklist-reference.md#sol-basics-vi-svi-23)** Does the contract create extremely large memory arrays? (version 0.2.0~0.6.4)
- [ ] **[SOL-Basics-VI-SVI-24](checklist-reference.md#sol-basics-vi-svi-24)** Does the contract's inline assembly with Yul optimizer use assignments inside for loops combined with continue or break? (version =0.6.0)
- [ ] **[SOL-Basics-VI-SVI-25](checklist-reference.md#sol-basics-vi-svi-25)** Does the contract allow private methods to be overridden by inheriting contracts? (version 0.3.0~0.5.16)
- [ ] **[SOL-Basics-VI-SVI-26](checklist-reference.md#sol-basics-vi-svi-26)** Is there any Yul's continue or break statement inside the loop?? (version 0.5.8~0.5.15)
- [ ] **[SOL-Basics-VI-SVI-27](checklist-reference.md#sol-basics-vi-svi-27)** Are both experimental ABIEncoderV2 and Yul optimizer activated? (version =0.5.14)
- [ ] **[SOL-Basics-VI-SVI-28](checklist-reference.md#sol-basics-vi-svi-28)** Does the contract read from calldata structs with dynamic yet statically-sized members? (version 0.5.6~0.5.10)
- [ ] **[SOL-Basics-VI-SVI-29](checklist-reference.md#sol-basics-vi-svi-29)** Does the contract assign arrays of signed integers to differently typed storage arrays? (version 0.4.7~0.5.9)
- [ ] **[SOL-Basics-VI-SVI-30](checklist-reference.md#sol-basics-vi-svi-30)** Does the contract directly encode storage arrays with structs or static arrays in external calls or abi.encode*? (version 0.4.16~0.5.9)
- [ ] **[SOL-Basics-VI-SVI-31](checklist-reference.md#sol-basics-vi-svi-31)** Does the contract's constructor accept structs or arrays with dynamic arrays? (version 0.4.16~0.5.8)
- [ ] **[SOL-Basics-VI-SVI-32](checklist-reference.md#sol-basics-vi-svi-32)** Are uninitialized internal function pointers created in the constructor being called? (version 0.5.0~0.5.7)
- [ ] **[SOL-Basics-VI-SVI-33](checklist-reference.md#sol-basics-vi-svi-33)** Are uninitialized internal function pointers created in the constructor being called? (version 0.4.5~0.4.25)
- [ ] **[SOL-Basics-VI-SVI-34](checklist-reference.md#sol-basics-vi-svi-34)** Does the library use contract types in events? (version 0.3.0~0.4.25)
- [ ] **[SOL-Basics-VI-SVI-35](checklist-reference.md#sol-basics-vi-svi-35)** Does the contract encode storage structs or arrays with types under 32 bytes directly using experimental ABIEncoderV2? (version 0.4.19~0.4.25)
- [ ] **[SOL-Basics-VI-SVI-36](checklist-reference.md#sol-basics-vi-svi-36)** Does the contract's optimizer handle byte opcodes with a second argument of 31 or an equivalent constant expression? (version 0.5.5~0.5.6)
- [ ] **[SOL-Basics-VI-SVI-37](checklist-reference.md#sol-basics-vi-svi-37)** Are there double bitwise shifts with large constants that might sum up to overflow 256 bits? (version =0.5.5)
- [ ] **[SOL-Basics-VI-SVI-38](checklist-reference.md#sol-basics-vi-svi-38)** Is the ** operator used with an exponent type shorter than 256 bits? (version ~0.4.24)
- [ ] **[SOL-Basics-VI-SVI-39](checklist-reference.md#sol-basics-vi-svi-39)** Are structs used in the logged events? (version 0.4.17~0.4.24)
- [ ] **[SOL-Basics-VI-SVI-40](checklist-reference.md#sol-basics-vi-svi-40)** Are functions returning multi-dimensional fixed-size arrays called? (version 0.1.4~0.4.21)
- [ ] **[SOL-Basics-VI-SVI-41](checklist-reference.md#sol-basics-vi-svi-41)** Does the contract use both new-style and old-style constructors simultaneously? (version =0.4.22)
- [ ] **[SOL-Basics-VI-SVI-42](checklist-reference.md#sol-basics-vi-svi-42)** Is there a function name crafted to potentially override the fallback function execution? (version ~0.4.17)
- [ ] **[SOL-Basics-VI-SVI-43](checklist-reference.md#sol-basics-vi-svi-43)** Is the low-level .delegatecall() used without checking the actual execution outcome? (version 0.3.0~0.4.14)
- [ ] **[SOL-Basics-VI-SVI-44](checklist-reference.md#sol-basics-vi-svi-44)** Is the ecrecover() function used without validating its input? (version ~0.4.13)
- [ ] **[SOL-Basics-VI-SVI-45](checklist-reference.md#sol-basics-vi-svi-45)** Is the `.selector` member accessed on complex expressions? (version 0.6.2~0.8.20)
- [ ] **[SOL-Basics-VI-SVI-46](checklist-reference.md#sol-basics-vi-svi-46)** Is there any inconsistency (`memory` vs `calldata`) in the param type during inheritance? (version 0.6.9~0.8.13)
- [ ] **[SOL-Basics-VI-SVI-47](checklist-reference.md#sol-basics-vi-svi-47)** Are there any functions with the same name and parameter type inside the same contract? (version =0.7.1)
- [ ] **[SOL-Basics-VI-SVI-48](checklist-reference.md#sol-basics-vi-svi-48)** Does the contract use tuple assignments with multi-stack-slot components, like nested tuples or dynamic calldata references? (version 0.1.6~0.6.5)

---

## Coverage tracking

Copy [`templates/coverage-matrix.md`](../templates/coverage-matrix.md) into
`engagements/<target>/` and record, per contract, the answer to every item. The goal is
not to "pass": it is to have consciously *looked* at every category on every entry point
and recorded what you found. Cite item IDs in hypotheses, PoCs and reports so a reader
can trace a finding back to the question that produced it.
