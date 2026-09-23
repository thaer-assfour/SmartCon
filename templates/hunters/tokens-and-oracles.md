# Hunter brief — Tokens & price sources

<!-- GENERATED FILE. Do not edit by hand.
     Sources: methodology/checklist-map.json (SmartCon core questions and placement rules)
              methodology/upstream/cyfrin-audit-checklist.json (Cyfrin / Solodit items)
              knowledge-base/case-studies/*.md (post-mortems citing checklist items)
     Regenerate: python3 tools/build-checklist.py -->

## Role

You are one of 6 parallel reviewers in SmartCon **Phase 4 (manual deep review)**. You own 2 checklist categories: **10. Token Integration Quirks**, **4. Oracle & Price Manipulation**. The other hunters own the rest (Callbacks, reentrancy & liveness: 1, 9, 16; Accounting & math: 3, 6; Privilege, upgrades, governance & signatures: 2, 7, 14, 8; Atomic capital, ordering & randomness: 5, 11, 13; Inputs, cross-chain boundaries & hygiene: 17, 15, 12); do not spend time on their categories except to hand them a lead. You read and reason; you do not modify the target, you do not fix anything, and you never run an exploit against a live deployment.

**Focus.** Which tokens can enter the system and what non-standard behaviour they bring (fee-on-transfer, rebasing, hooks, missing return values, blacklists, phantom functions, odd decimals), and every place a price or exchange rate is read: where it comes from, whether it can be moved in the same transaction, and what happens when it is stale, zero or reverts.

**Start with.**

1. List the tokens in scope (or the rule for listing new ones) and check each core token-integration item against the transfer/approve/permit call sites.
2. List every price read (oracle call, reserve ratio, balanceOf-based ratio, get_virtual_price, pricePerShare, exchangeRate) and classify it as spot / TWAP / external feed / internal accounting.
3. For each spot or balance-derived read, write the one-transaction manipulation that moves it and estimate the capital needed.

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

### 10. Token Integration Quirks

Notes: [`knowledge-base/vulnerabilities/token-integration.md`](../../knowledge-base/vulnerabilities/token-integration.md) · Case studies: [2022-03-15 Hundred Finance (~$6.2M)](../../knowledge-base/case-studies/2022-03-15-hundred-finance-erc677-hook-reentrancy.md), [2022-01-18 Multichain / Anyswap `AnyswapV4Router.a… (~$1.4M)](../../knowledge-base/case-studies/2022-01-18-multichain-anyswap-phantom-permit.md)

**Core**

- **[SC-TOKEN-1](../../methodology/checklist-reference.md#sc-token-1)** **Fee-on-transfer**: does the code assume received == sent amount?
- **[SC-TOKEN-2](../../methodology/checklist-reference.md#sc-token-2)** **Rebasing tokens**: does cached balance drift from actual balance?
- **[SC-TOKEN-3](../../methodology/checklist-reference.md#sc-token-3)** **Missing return value** ERC-20s (USDT): is `SafeERC20`/`safeTransfer` used?
- **[SC-TOKEN-4](../../methodology/checklist-reference.md#sc-token-4)** **ERC-777 / hook tokens** (ERC-677 `transferAndCall`, ERC-1363) enabling reentrancy on transfer?
- **[SC-TOKEN-5](../../methodology/checklist-reference.md#sc-token-5)** **Non-standard decimals** (e.g. USDC=6, WBTC=8) handled?
- **[SC-TOKEN-6](../../methodology/checklist-reference.md#sc-token-6)** **Approval race** / double-spend on non-zero→non-zero approve?
- **[SC-TOKEN-7](../../methodology/checklist-reference.md#sc-token-7)** **Phantom functions**: does the code call `permit` or other optional functions on tokens that may not implement them, where a `fallback` (WETH) or a codeless address makes the call "succeed"?

**Extended (Cyfrin / Solodit)**

- **[SOL-Defi-AS-8](../../methodology/checklist-reference.md#sol-defi-as-8)** Does the AMM properly handle tokens of varying decimal configurations and token types?
- **[SOL-Defi-AS-9](../../methodology/checklist-reference.md#sol-defi-as-9)** Does the AMM support the fee-on-transfer tokens?
- **[SOL-Defi-AS-10](../../methodology/checklist-reference.md#sol-defi-as-10)** Does the AMM support the rebasing tokens?
- **[SOL-Defi-General-1](../../methodology/checklist-reference.md#sol-defi-general-1)** Can the protocol handle ERC20 tokens with decimals other than 18?
- **[SOL-Defi-General-6](../../methodology/checklist-reference.md#sol-defi-general-6)** Does the protocol revert on maximum approval to prevent over-allowance?
- **[SOL-Defi-General-9](../../methodology/checklist-reference.md#sol-defi-general-9)** Does the protocol aim to support ALL kinds of ERC20 tokens?
- **[SOL-Heuristics-14](../../methodology/checklist-reference.md#sol-heuristics-14)** Is ETH/WETH handling implemented correctly?
- **[SOL-Integrations-AC-1](../../methodology/checklist-reference.md#sol-integrations-ac-1)** Does the protocol use cETH token?
- **[SOL-Integrations-LSD-cbETH-1](../../methodology/checklist-reference.md#sol-integrations-lsd-cbeth-1)** How is the control over the `cbETH`/`ETH` rate determined? Are there specific addresses with this capability due to the `onlyOracle` modifier?
- **[SOL-Integrations-LSD-cbETH-2](../../methodology/checklist-reference.md#sol-integrations-lsd-cbeth-2)** How does the system handle potential decreases in the `cbETH`/`ETH` rate?
- **[SOL-Integrations-LSD-rETH-1](../../methodology/checklist-reference.md#sol-integrations-lsd-reth-1)** Does the application account for potential penalties or slashes?
- **[SOL-Integrations-LSD-rETH-2](../../methodology/checklist-reference.md#sol-integrations-lsd-reth-2)** How does the system manage rewards accrued from staking?
- **[SOL-Integrations-LSD-rETH-3](../../methodology/checklist-reference.md#sol-integrations-lsd-reth-3)** Does the application handle potential reverts in the `burn()` function when there's insufficient ether in the `RocketDepositPool`?
- **[SOL-Integrations-LSD-rETH-4](../../methodology/checklist-reference.md#sol-integrations-lsd-reth-4)** What measures are in place to counteract potential consensus attacks on RPL nodes?
- **[SOL-Integrations-LSD-rETH-5](../../methodology/checklist-reference.md#sol-integrations-lsd-reth-5)** How does the system handle the conversion between `ETH` and `rETH`?
- **[SOL-Integrations-LSD-sfrxETH-1](../../methodology/checklist-reference.md#sol-integrations-lsd-sfrxeth-1)** How does the system handle potential detachment of `sfrxETH` from `frxETH` during reward transfers?
- **[SOL-Integrations-LSD-sfrxETH-2](../../methodology/checklist-reference.md#sol-integrations-lsd-sfrxeth-2)** Is the stability of the `sfrxETH`/`ETH` rate guaranteed or can it decrease in the future?
- **[SOL-Integrations-LSD-stETH-1](../../methodology/checklist-reference.md#sol-integrations-lsd-steth-1)** Is the application aware that `stETH` is a rebasing token?
- **[SOL-Integrations-LSD-stETH-2](../../methodology/checklist-reference.md#sol-integrations-lsd-steth-2)** Are you aware of the overhead when withdrawing `stETH`/`wstETH`?
- **[SOL-Integrations-LSD-stETH-3](../../methodology/checklist-reference.md#sol-integrations-lsd-steth-3)** Does the application handle conversions between `stETH` and `wstETH` correctly?
- **[SOL-Token-FE-1](../../methodology/checklist-reference.md#sol-token-fe-1)** Are safe transfer functions used throughout the contract?
- **[SOL-Token-FE-2](../../methodology/checklist-reference.md#sol-token-fe-2)** Is there potential for a race condition for approvals?
- **[SOL-Token-FE-3](../../methodology/checklist-reference.md#sol-token-fe-3)** Could a difference in decimals between ERC20 tokens cause issues?
- **[SOL-Token-FE-4](../../methodology/checklist-reference.md#sol-token-fe-4)** Does the token implement any form of address whitelisting, blacklisting, or checks?
- **[SOL-Token-FE-5](../../methodology/checklist-reference.md#sol-token-fe-5)** Could the use of multiple addresses for a single token lead to complications?
- **[SOL-Token-FE-6](../../methodology/checklist-reference.md#sol-token-fe-6)** Does the token charge fee on transfer?
- **[SOL-Token-FE-7](../../methodology/checklist-reference.md#sol-token-fe-7)** Can the token be ERC777?
- **[SOL-Token-FE-8](../../methodology/checklist-reference.md#sol-token-fe-8)** Does the protocol use Solmate's `ERC20.safeTransferLib`?
- **[SOL-Token-FE-10](../../methodology/checklist-reference.md#sol-token-fe-10)** What happens on zero amount transfer?
- **[SOL-Token-FE-11](../../methodology/checklist-reference.md#sol-token-fe-11)** Is the token an ERC2612 implementation?
- **[SOL-Token-FE-12](../../methodology/checklist-reference.md#sol-token-fe-12)** Can the token be sent to any address?
- **[SOL-Token-FE-13](../../methodology/checklist-reference.md#sol-token-fe-13)** Is there a direct approval to a non-zero value?
- **[SOL-Token-FE-14](../../methodology/checklist-reference.md#sol-token-fe-14)** Is there a max approval used?
- **[SOL-Token-FE-15](../../methodology/checklist-reference.md#sol-token-fe-15)** Can the token be paused?
- **[SOL-Token-FE-16](../../methodology/checklist-reference.md#sol-token-fe-16)** Is the decrease allowance feature of transferFrom() handled correctly when the sender is the caller?
- **[SOL-Token-NfE1-1](../../methodology/checklist-reference.md#sol-token-nfe1-1)** How are the minting and transfer implemented?
- **[SOL-Token-NfE1-4](../../methodology/checklist-reference.md#sol-token-nfe1-4)** Is it possible to steal NFT abusing his approval?
- **[SOL-Token-NfE1-5](../../methodology/checklist-reference.md#sol-token-nfe1-5)** Does the ERC721/1155 contract correctly implement supportsInterface?
- **[SOL-Token-NfE1-6](../../methodology/checklist-reference.md#sol-token-nfe1-6)** Can the contract support both ERC721 and ERC1155 standards?
- **[SOL-Token-NfE1-7](../../methodology/checklist-reference.md#sol-token-nfe1-7)** What happens to the airdrops that are engaged to specific NFT?
- **[SOL-Token-NfE1-8](../../methodology/checklist-reference.md#sol-token-nfe1-8)** How is the approval/transfer handled for CryptoPunks collection?

### 4. Oracle & Price Manipulation

Notes: [`knowledge-base/vulnerabilities/oracle-and-price-manipulation.md`](../../knowledge-base/vulnerabilities/oracle-and-price-manipulation.md) · Case studies: [2023-05-29 Jimbo's Protocol (~4,090 ETH)](../../knowledge-base/case-studies/2023-05-29-jimbos-protocol-unprotected-rebalance.md), [2023-02-10 dForce (~$3.65M)](../../knowledge-base/case-studies/2023-02-10-dforce-read-only-reentrancy.md), [2021-10-27 C.R.E.A.M. Finance (~$130M)](../../knowledge-base/case-studies/2021-10-27-cream-finance-yusd-price-manipulation.md), [2021-05-19 PancakeBunny (~$45M)](../../knowledge-base/case-studies/2021-05-19-pancakebunny-flash-loan-lp-pricing.md), [2020-10-26 Harvest Finance fUSDC / fUSDT vaults (~$33.8M)](../../knowledge-base/case-studies/2020-10-26-harvest-finance-curve-pool-manipulation.md)

**Core**

- **[SC-ORACLE-1](../../methodology/checklist-reference.md#sc-oracle-1)** Does pricing use a **spot price** from an AMM reserve/`getReserves`/`balanceOf`? (manipulable in one tx via flash loan)
- **[SC-ORACLE-2](../../methodology/checklist-reference.md#sc-oracle-2)** For Chainlink: are `updatedAt` staleness and `answeredInRound` checked? Is a zero/negative price handled? Are min/max bounds considered?
- **[SC-ORACLE-3](../../methodology/checklist-reference.md#sc-oracle-3)** Is a TWAP used, and is its window long enough to resist manipulation?
- **[SC-ORACLE-4](../../methodology/checklist-reference.md#sc-oracle-4)** Does the protocol trust `token.balanceOf(pair)` for accounting? (donation-manipulable)
- **[SC-ORACLE-5](../../methodology/checklist-reference.md#sc-oracle-5)** What happens if the oracle reverts or returns stale data: fail open or closed?
- **[SC-ORACLE-6](../../methodology/checklist-reference.md#sc-oracle-6)** Is a price or exchange rate derived from a pool or vault that a flash loan can inflate in the same transaction (LP-token pricing, `get_virtual_price`, `pricePerShare`, a cToken `exchangeRate` on a near-empty market)?

**Extended (Cyfrin / Solodit)**

- **[SOL-AM-PMA-1](../../methodology/checklist-reference.md#sol-am-pma-1)** Is the price calculated by the ratio of token balances?
- **[SOL-AM-PMA-2](../../methodology/checklist-reference.md#sol-am-pma-2)** Is the price calculated from DEX liquidity pool spot prices?
- **[SOL-Defi-General-5](../../methodology/checklist-reference.md#sol-defi-general-5)** Are the protocol token pegged to any other asset?
- **[SOL-Defi-LSD-8](../../methodology/checklist-reference.md#sol-defi-lsd-8)** If using a Proof Of Reserves Oracle, does the protocol check for stale data?
- **[SOL-Defi-Oracle-1](../../methodology/checklist-reference.md#sol-defi-oracle-1)** Is the Oracle using deprecated Chainlink functions?
- **[SOL-Defi-Oracle-2](../../methodology/checklist-reference.md#sol-defi-oracle-2)** Is the returned price validated to be non-zero?
- **[SOL-Defi-Oracle-3](../../methodology/checklist-reference.md#sol-defi-oracle-3)** Is the price update time validated?
- **[SOL-Defi-Oracle-4](../../methodology/checklist-reference.md#sol-defi-oracle-4)** Is there a validation to check if the rollup sequencer is running?
- **[SOL-Defi-Oracle-5](../../methodology/checklist-reference.md#sol-defi-oracle-5)** Is the Oracle's TWAP period appropriately set?
- **[SOL-Defi-Oracle-6](../../methodology/checklist-reference.md#sol-defi-oracle-6)** Is the desired price feed pair supported across all deployed chains?
- **[SOL-Defi-Oracle-7](../../methodology/checklist-reference.md#sol-defi-oracle-7)** Is the heartbeat of the price feed suitable for the use case?
- **[SOL-Defi-Oracle-8](../../methodology/checklist-reference.md#sol-defi-oracle-8)** Are there any inconsistencies with decimal precision when using different price feeds?
- **[SOL-Defi-Oracle-9](../../methodology/checklist-reference.md#sol-defi-oracle-9)** Is the price feed address hard-coded?
- **[SOL-Defi-Oracle-10](../../methodology/checklist-reference.md#sol-defi-oracle-10)** What happens if oracle price updates are front-run?
- **[SOL-Defi-Oracle-11](../../methodology/checklist-reference.md#sol-defi-oracle-11)** How does the system handle potential oracle reverts?
- **[SOL-Defi-Oracle-12](../../methodology/checklist-reference.md#sol-defi-oracle-12)** Are the price feeds appropriate for the underlying assets?
- **[SOL-Defi-Oracle-13](../../methodology/checklist-reference.md#sol-defi-oracle-13)** Is the contract vulnerable to oracle manipulation, especially using spot prices from AMMs?
- **[SOL-Defi-Oracle-14](../../methodology/checklist-reference.md#sol-defi-oracle-14)** How does the system address potential inaccuracies during flash crashes?
- **[SOL-Integrations-Balancer-2](../../methodology/checklist-reference.md#sol-integrations-balancer-2)** Does the protocol use Balancer's Oracle? (getTimeWeightedAverage)
- **[SOL-Integrations-Balancer-4](../../methodology/checklist-reference.md#sol-integrations-balancer-4)** Does the protocol use Balancer vault pool liquidity status for any pricing?
- **[SOL-Integrations-Uniswap-5](../../methodology/checklist-reference.md#sol-integrations-uniswap-5)** Is there a reliance on pool reserves?
- **[SOL-Integrations-Uniswap-9](../../methodology/checklist-reference.md#sol-integrations-uniswap-9)** Is `pool.slot0` being used to calculate sensitive information like current price and exchange rates?

## Output contract

Return exactly these four sections, in this order, as Markdown, with nothing before the first heading. The orchestrator merges them mechanically.

### Hypotheses

| # | Hypothesis (attacker story, one or two sentences) | Checklist item(s) | Entry point (`Contract.function`, `file:line`) | Invariant broken | Preconditions | Rough impact | Confidence | How to prove (PoC sketch) |
|---|---|---|---|---|---|---|---|---|

Rank by impact × confidence (`high` / `medium` / `low`). No hypothesis without a `file:line`. A finding you could not fully confirm still goes here at `low` confidence; the orchestrator decides what reaches Phase 5.

### Coverage

| ID | Contract(s) | Answer (`Y` present → hypothesis above / `N` checked, absent / `?` open lead / `N.A.` not applicable) | Evidence (`file:line` or a one-line reason) |
|---|---|---|---|

One row per **core** item of your categories per in-scope contract (group contracts when the answer and evidence are identical), plus every extended item you examined.

### Not covered

What you did not get to and why (time, missing source, out of scope). An empty list means you claim full coverage of your categories.

### Leads for other hunters

Anything you noticed that belongs to another cluster: `<cluster slug>`: `<item ID>`: one line. Leave empty if none.
