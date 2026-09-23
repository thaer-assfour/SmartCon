# Hunter brief — Privilege, upgrades, governance & signatures

<!-- GENERATED FILE. Do not edit by hand.
     Sources: methodology/checklist-map.json (SmartCon core questions and placement rules)
              methodology/upstream/cyfrin-audit-checklist.json (Cyfrin / Solodit items)
              knowledge-base/case-studies/*.md (post-mortems citing checklist items)
     Regenerate: python3 tools/build-checklist.py -->

## Role

You are one of 6 parallel reviewers in SmartCon **Phase 4 (manual deep review)**. You own 4 checklist categories: **2. Access Control**, **7. Upgradeability & Proxies**, **14. Governance**, **8. Signatures, Proofs & Replay**. The other hunters own the rest (Callbacks, reentrancy & liveness: 1, 9, 16; Accounting & math: 3, 6; Tokens & price sources: 10, 4; Atomic capital, ordering & randomness: 5, 11, 13; Inputs, cross-chain boundaries & hygiene: 17, 15, 12); do not spend time on their categories except to hand them a lead. You read and reason; you do not modify the target, you do not fix anything, and you never run an exploit against a live deployment.

**Focus.** Who may call what, and whether that answer changes under initializers, proxies, storage layout, role administration, votes and signed messages or proofs. Assume every privileged path will be probed by an unprivileged caller and every signed payload will be replayed.

**Start with.**

1. Build the actor/permission matrix from the attack-surface table and mark every state-changing function that is not gated or is gated by the wrong role.
2. For proxies: map the storage layout of proxy and implementation side by side, find every initializer and check it cannot be run again or by anyone.
3. For governance and signatures: where is voting power or the signer read, at which block, bound to which domain, nonce and deadline.

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

### 2. Access Control

Notes: [`knowledge-base/vulnerabilities/access-control.md`](../../knowledge-base/vulnerabilities/access-control.md) · Case studies: [2023-04-09 SushiSwap `RouteProcessor2` router (>$3.3M)](../../knowledge-base/case-studies/2023-04-09-sushiswap-routeprocessor2-unverified-callback.md), [2022-07-23 Audius (704 ETH)](../../knowledge-base/case-studies/2022-07-23-audius-storage-collision-governance.md), [2021-09-03 DAO Maker (~$4M)](../../knowledge-base/case-studies/2021-09-03-dao-maker-unprotected-init.md), [2021-08-10 Poly Network (~$611M)](../../knowledge-base/case-studies/2021-08-10-poly-network-cross-chain-keeper-swap.md)

**Core**

- **[SC-AC-1](../../methodology/checklist-reference.md#sc-ac-1)** Is every state-changing/privileged function gated by the correct modifier?
- **[SC-AC-2](../../methodology/checklist-reference.md#sc-ac-2)** Any function that *should* be `onlyOwner`/role-gated but is public?
- **[SC-AC-3](../../methodology/checklist-reference.md#sc-ac-3)** Is `tx.origin` used for authorization? (phishable; should be `msg.sender`)
- **[SC-AC-4](../../methodology/checklist-reference.md#sc-ac-4)** Are initializers protected against being called twice / by anyone?
- **[SC-AC-5](../../methodology/checklist-reference.md#sc-ac-5)** Are role admins set correctly? Can a role escalate itself?
- **[SC-AC-6](../../methodology/checklist-reference.md#sc-ac-6)** Is there a default-admin or emergency backdoor that concentrates too much power?

**Extended (Cyfrin / Solodit)**

- **[SOL-AM-RP-1](../../methodology/checklist-reference.md#sol-am-rp-1)** Can the admin of the protocol pull assets from the protocol?
- **[SOL-Basics-AC-1](../../methodology/checklist-reference.md#sol-basics-ac-1)** Did you clarify all the actors and their allowed interactions in the protocol?
- **[SOL-Basics-AC-2](../../methodology/checklist-reference.md#sol-basics-ac-2)** Are there functions lacking proper access controls?
- **[SOL-Basics-AC-3](../../methodology/checklist-reference.md#sol-basics-ac-3)** Do certain addresses require whitelisting?
- **[SOL-Basics-AC-4](../../methodology/checklist-reference.md#sol-basics-ac-4)** Does the protocol allow transfer of privileges?
- **[SOL-Basics-AC-5](../../methodology/checklist-reference.md#sol-basics-ac-5)** What happens during the transfer of privileges?
- **[SOL-Basics-AC-6](../../methodology/checklist-reference.md#sol-basics-ac-6)** Does the contract inherit others?
- **[SOL-Basics-AC-7](../../methodology/checklist-reference.md#sol-basics-ac-7)** Does the contract use `tx.origin` in validation?
- **[SOL-Basics-Function-7](../../methodology/checklist-reference.md#sol-basics-function-7)** Should it be `external`/`public`?
- **[SOL-Basics-Function-8](../../methodology/checklist-reference.md#sol-basics-function-8)** Does this function need to be called by only EOA or only contracts?
- **[SOL-Basics-Function-9](../../methodology/checklist-reference.md#sol-basics-function-9)** Does this function need to be restricted for specific callers?
- **[SOL-Basics-Inheritance-1](../../methodology/checklist-reference.md#sol-basics-inheritance-1)** Is it necessary to limit visibility of parent contract's public functions?
- **[SOL-CR-1](../../methodology/checklist-reference.md#sol-cr-1)** What happens to the user accounting in special conditions?
- **[SOL-CR-2](../../methodology/checklist-reference.md#sol-cr-2)** Is there a pause mechanism?
- **[SOL-CR-3](../../methodology/checklist-reference.md#sol-cr-3)** Is there a functionality for the admin to withdraw from the protocol?
- **[SOL-CR-4](../../methodology/checklist-reference.md#sol-cr-4)** Can the admin change critical protocol property immediately?
- **[SOL-CR-5](../../methodology/checklist-reference.md#sol-cr-5)** Is there any admin setter function missing events?
- **[SOL-CR-6](../../methodology/checklist-reference.md#sol-cr-6)** How is the ownership/privilege transferred??
- **[SOL-CR-7](../../methodology/checklist-reference.md#sol-cr-7)** Is there a proper validation in privileged setter functions?
- **[SOL-Defi-LSD-5](../../methodology/checklist-reference.md#sol-defi-lsd-5)** Can paused states be bypassed to perform restricted actions even when they should be paused?
- **[SOL-EC-14](../../methodology/checklist-reference.md#sol-ec-14)** How is the msg.sender handled?
- **[SOL-Integrations-GS-1](../../methodology/checklist-reference.md#sol-integrations-gs-1)** Do your modules execute the Guard's hooks?

### 7. Upgradeability & Proxies

Notes: [`knowledge-base/vulnerabilities/upgradeability.md`](../../knowledge-base/vulnerabilities/upgradeability.md) · Case studies: [2022-07-23 Audius (704 ETH)](../../knowledge-base/case-studies/2022-07-23-audius-storage-collision-governance.md)

**Core**

- **[SC-PROXY-1](../../methodology/checklist-reference.md#sc-proxy-1)** Storage layout: does an upgrade risk a **storage collision** with the old layout?
- **[SC-PROXY-2](../../methodology/checklist-reference.md#sc-proxy-2)** Is the implementation contract left **uninitialized** (attacker can init & self-destruct/`delegatecall`)?
- **[SC-PROXY-3](../../methodology/checklist-reference.md#sc-proxy-3)** `delegatecall` to untrusted targets? Function-selector clashes between proxy and impl?
- **[SC-PROXY-4](../../methodology/checklist-reference.md#sc-proxy-4)** Are `__gap` slots reserved in upgradeable base contracts?
- **[SC-PROXY-5](../../methodology/checklist-reference.md#sc-proxy-5)** Who can upgrade, and is that authority appropriately decentralized/timelocked?
- **[SC-PROXY-6](../../methodology/checklist-reference.md#sc-proxy-6)** Does the proxy's own storage (admin, implementation, init flags) overlap the implementation's variables, so that `initialize` reads as never run and can be re-executed?

**Extended (Cyfrin / Solodit)**

- **[SOL-Basics-Initialization-2](../../methodology/checklist-reference.md#sol-basics-initialization-2)** Has the contract inherited OpenZeppelin's Initializable?
- **[SOL-Basics-Initialization-3](../../methodology/checklist-reference.md#sol-basics-initialization-3)** Does the contract have a separate initializer function other than a constructor?
- **[SOL-Basics-PU-1](../../methodology/checklist-reference.md#sol-basics-pu-1)** Is there a constructor in the proxied contract?
- **[SOL-Basics-PU-2](../../methodology/checklist-reference.md#sol-basics-pu-2)** Is the `initializer` modifier applied to the `initialization()` function?
- **[SOL-Basics-PU-3](../../methodology/checklist-reference.md#sol-basics-pu-3)** Is the upgradable version used for initialization?
- **[SOL-Basics-PU-4](../../methodology/checklist-reference.md#sol-basics-pu-4)** Is the `authorizeUpgrade()` function properly secured in a UUPS setup?
- **[SOL-Basics-PU-5](../../methodology/checklist-reference.md#sol-basics-pu-5)** Is the contract initialized?
- **[SOL-Basics-PU-6](../../methodology/checklist-reference.md#sol-basics-pu-6)** Are `selfdestruct` and `delegatecall` used within the implementation contracts?
- **[SOL-Basics-PU-7](../../methodology/checklist-reference.md#sol-basics-pu-7)** Are values in immutable variables preserved between upgrades?
- **[SOL-Basics-PU-8](../../methodology/checklist-reference.md#sol-basics-pu-8)** Has the contract inherited the correct branch of OpenZeppelin library?
- **[SOL-Basics-PU-9](../../methodology/checklist-reference.md#sol-basics-pu-9)** Could an upgrade of the contract result in storage collision?
- **[SOL-Basics-PU-10](../../methodology/checklist-reference.md#sol-basics-pu-10)** Are the order and types of storage variables consistent between upgrades?

### 14. Governance

Notes: [`knowledge-base/vulnerabilities/governance.md`](../../knowledge-base/vulnerabilities/governance.md) · Case studies: [2022-07-23 Audius (704 ETH)](../../knowledge-base/case-studies/2022-07-23-audius-storage-collision-governance.md), [2022-04-16 Beanstalk Farms (~$182M)](../../knowledge-base/case-studies/2022-04-16-beanstalk-flash-loan-governance.md)

**Core**

- **[SC-GOV-1](../../methodology/checklist-reference.md#sc-gov-1)** Is voting power snapshotted at a **past block**, not read from current balance?
- **[SC-GOV-2](../../methodology/checklist-reference.md#sc-gov-2)** Is there a **timelock** between a proposal passing and executing?
- **[SC-GOV-3](../../methodology/checklist-reference.md#sc-gov-3)** Can a flash loan / large holder reach quorum atomically?
- **[SC-GOV-4](../../methodology/checklist-reference.md#sc-gov-4)** What is `execute` allowed to call: treasury, upgrades, arbitrary targets?
- **[SC-GOV-5](../../methodology/checklist-reference.md#sc-gov-5)** Can the code a proposal executes change between vote and execution (metamorphic contract via `CREATE2` + `selfdestruct`, upgradeable target, unpinned bytecode)?

**Extended (Cyfrin / Solodit)**

- **[SOL-AM-SybilAttack-1](../../methodology/checklist-reference.md#sol-am-sybilattack-1)** Is there a mechanism depending on the number of users?
- **[SOL-Timelock-1](../../methodology/checklist-reference.md#sol-timelock-1)** Are timelocks implemented for important changes?

### 8. Signatures, Proofs & Replay

Notes: [`knowledge-base/vulnerabilities/signatures.md`](../../knowledge-base/vulnerabilities/signatures.md) · Case studies: [2022-01-18 Multichain / Anyswap `AnyswapV4Router.a… (~$1.4M)](../../knowledge-base/case-studies/2022-01-18-multichain-anyswap-phantom-permit.md)

**Core**

- **[SC-SIG-1](../../methodology/checklist-reference.md#sc-sig-1)** Is every signed message bound to a **nonce**, and is the nonce consumed?
- **[SC-SIG-2](../../methodology/checklist-reference.md#sc-sig-2)** Is the signature bound to `chainId` and the contract address (EIP-712 domain)?
- **[SC-SIG-3](../../methodology/checklist-reference.md#sc-sig-3)** Is `ecrecover` checked against `address(0)` (malleability / invalid sig)?
- **[SC-SIG-4](../../methodology/checklist-reference.md#sc-sig-4)** Can a signature be replayed across chains, forks, or contract instances?
- **[SC-SIG-5](../../methodology/checklist-reference.md#sc-sig-5)** Are `v/r/s` malleability and signature-uniqueness assumptions safe?

**Extended (Cyfrin / Solodit)**

- **[SOL-AM-ReplayAttack-1](../../methodology/checklist-reference.md#sol-am-replayattack-1)** Are there protections against replay attacks for failed transactions?
- **[SOL-AM-ReplayAttack-2](../../methodology/checklist-reference.md#sol-am-replayattack-2)** Is there protection against replaying signatures on different chains?
- **[SOL-HMT-1](../../methodology/checklist-reference.md#sol-hmt-1)** Is the Merkle tree vulnerable to front-running attacks?
- **[SOL-HMT-2](../../methodology/checklist-reference.md#sol-hmt-2)** Does the claim method validate `msg.sender`?
- **[SOL-HMT-3](../../methodology/checklist-reference.md#sol-hmt-3)** What is the result when passing a zero hash to the Merkle tree functions?
- **[SOL-HMT-4](../../methodology/checklist-reference.md#sol-hmt-4)** What occurs if the same proof is duplicated within the Merkle tree?
- **[SOL-HMT-5](../../methodology/checklist-reference.md#sol-hmt-5)** Are the leaves of the Merkle tree hashed with the claimable address included?
- **[SOL-Integrations-GS-2](../../methodology/checklist-reference.md#sol-integrations-gs-2)** Does the `execTransactionFromModule()` function increment the nonce?
- **[SOL-Signature-1](../../methodology/checklist-reference.md#sol-signature-1)** Are signatures guarded against replay attacks?
- **[SOL-Signature-2](../../methodology/checklist-reference.md#sol-signature-2)** Are signatures protected against malleability issues?
- **[SOL-Signature-3](../../methodology/checklist-reference.md#sol-signature-3)** Does the returned public key from the signature verification match the expected public key?
- **[SOL-Signature-4](../../methodology/checklist-reference.md#sol-signature-4)** Is the signature originating from the appropriate entity?
- **[SOL-Signature-5](../../methodology/checklist-reference.md#sol-signature-5)** If the signature has a deadline, is it still valid?

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

Anything you noticed that belongs to another cluster, one line each in the form `<cluster slug>`: `<item ID>`: what and where (`file:line`). Use these slugs exactly: `callbacks-and-liveness` (Callbacks, reentrancy & liveness), `accounting-and-math` (Accounting & math), `tokens-and-oracles` (Tokens & price sources), `economics-and-ordering` (Atomic capital, ordering & randomness), `boundaries-and-inputs` (Inputs, cross-chain boundaries & hygiene). Write `None.` if there are none.
