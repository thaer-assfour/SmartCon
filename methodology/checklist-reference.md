# Checklist Reference

<!-- GENERATED FILE. Do not edit by hand.
     Sources: methodology/checklist-map.json (SmartCon core questions and placement rules)
              methodology/upstream/cyfrin-audit-checklist.json (Cyfrin / Solodit items)
              knowledge-base/case-studies/*.md (post-mortems citing checklist items)
     Regenerate: python3 tools/build-checklist.py -->

One entry per checklist item, in the same order as [`checklist.md`](checklist.md). `SC-*` entries are SmartCon's own; `SOL-*` entries carry the
description, remediation and Solodit references from the [Cyfrin / Solodit checklist](https://github.com/Cyfrin/audit-checklist)
(retrieved 2026-09-23). "Cited by" lists the case studies whose Summary names the item.

## 1. Reentrancy

### SC-REEN-1

**Question.** Does any function make an external call (token transfer, `call`, callback) *before* updating state? (Checks-Effects-Interactions violation)

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/reentrancy.md`](../knowledge-base/vulnerabilities/reentrancy.md)

**Cited by.** [2022-04-30 Rari Capital Fuse pools (~$80M)](../knowledge-base/case-studies/2022-04-30-rari-fei-fuse-reentrancy.md); [2022-03-15 Hundred Finance (~$6.2M)](../knowledge-base/case-studies/2022-03-15-hundred-finance-erc677-hook-reentrancy.md)

### SC-REEN-2

**Question.** Are there cross-function reentrancy paths that share state but not a guard?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/reentrancy.md`](../knowledge-base/vulnerabilities/reentrancy.md)

**Cited by.** [2022-04-30 Rari Capital Fuse pools (~$80M)](../knowledge-base/case-studies/2022-04-30-rari-fei-fuse-reentrancy.md)

### SC-REEN-3

**Question.** Is there **read-only reentrancy**: a view function returning stale state that other protocols trust mid-callback?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/reentrancy.md`](../knowledge-base/vulnerabilities/reentrancy.md)

**Cited by.** [2023-02-10 dForce (~$3.65M)](../knowledge-base/case-studies/2023-02-10-dforce-read-only-reentrancy.md)

### SC-REEN-4

**Question.** Do ERC-777 / ERC-721 / ERC-1155 hooks or `receive()`/`fallback()` give the attacker a callback window?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/reentrancy.md`](../knowledge-base/vulnerabilities/reentrancy.md)

**Cited by.** [2022-04-30 Rari Capital Fuse pools (~$80M)](../knowledge-base/case-studies/2022-04-30-rari-fei-fuse-reentrancy.md); [2022-03-15 Hundred Finance (~$6.2M)](../knowledge-base/case-studies/2022-03-15-hundred-finance-erc677-hook-reentrancy.md)

### SC-REEN-5

**Question.** Is `nonReentrant` applied consistently across *all* functions touching the same state, including cross-contract entry points?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/reentrancy.md`](../knowledge-base/vulnerabilities/reentrancy.md)

### SOL-AM-ReentrancyAttack-1

**Question.** Is there a view function that can return a stale value during interactions?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Reentrancy Attack*

**Description.** Read-only reentrancy. The read-only reentrancy is a reentrancy scenario where a view function is reentered, which in most cases is unguarded as it does not modify the contract's state. However, if the state is inconsistent, wrong values could be reported. Other protocols relying on a return value can be tricked into reading the wrong state to perform unwanted actions.

**Remediation.** Extend the reentrancy guard to the view functions as well.

**References.**
- <https://medium.com/@zokyo.io/read-only-reentrancy-attacks-understanding-the-threat-to-your-smart-contracts-99444c0a7334>
- <https://solodit.xyz/issues/m-03-read-only-reentrancy-is-possible-code4rena-angle-protocol-angle-protocol-invitational-git>
- <https://solodit.xyz/issues/h-13-balancerpairoracle-can-be-manipulated-using-read-only-reentrancy-sherlock-none-blueberry-update-git>

Tags: Reentrancy Attack

**Cited by.** [2023-02-10 dForce (~$3.65M)](../knowledge-base/case-studies/2023-02-10-dforce-read-only-reentrancy.md)

### SOL-AM-ReentrancyAttack-2

**Question.** Is there any state change after interaction to an external contract?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Reentrancy Attack*

**Description.** Untrusted external contract calls could callback leading to unexpected results such as multiple withdrawals or out-of-order events.

**Remediation.** Use check-effects-interactions pattern or reentrancy guards.

**References.**
- <https://www.geeksforgeeks.org/reentrancy-attack-in-smart-contracts/>
- <https://solodit.xyz/issues/m-09-malicious-royalty-recipient-can-steal-excess-eth-from-buy-orders-code4rena-caviar-caviar-private-pools-git>
- <https://solodit.xyz/issues/h-01-re-entrancy-in-settleauction-allow-stealing-all-funds-code4rena-kuiper-kuiper-contest-git>

Tags: Reentrancy Attack

**Cited by.** [2022-04-30 Rari Capital Fuse pools (~$80M)](../knowledge-base/case-studies/2022-04-30-rari-fei-fuse-reentrancy.md)

### SOL-Defi-LSD-3

**Question.** Can re-entrancy when ETH is sent during rewards/withdrawals or when NFTs are minted via `_safeMint` (to represent pending withdrawals) be used to drain the protocol's ETH?

Source: Cyfrin / Solodit · upstream path: *Defi › Liquid Staking Derivatives*

**Description.** Re-entrancy vulnerabilties can often exist in the reward or withdrawal code of LSD protocols.

**Remediation.** Always follow the Checks-Effects-Interactions pattern; sending ETH or minting NFTs via `_safeMint` should always happen after storage updates.

### SOL-EC-1

**Question.** What are the implications if the call reenters a different function?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** Reentrant calls to different functions can unpredictably alter contract states. Note that view functions should be checked as well to prevent the Readonly Reentrancy.

**Remediation.** Ensure the contract state is maintained reasonably during the external interactions.

**References.**
- <https://medium.com/@zokyo.io/read-only-reentrancy-attacks-understanding-the-threat-to-your-smart-contracts-99444c0a7334>
- <https://solodit.xyz/issues/m-03-read-only-reentrancy-is-possible-code4rena-angle-protocol-angle-protocol-invitational-git>

### SOL-EC-13

**Question.** Is the check-effect-interaction pattern being utilized?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** The check-effect-interaction pattern prevents reentrancy attacks.

**Remediation.** Adhere to the CEI pattern and use `reentrancyGuard` judiciously.

**References.**
- <https://www.geeksforgeeks.org/reentrancy-attack-in-smart-contracts/>
- <https://solodit.xyz/issues/m-09-malicious-royalty-recipient-can-steal-excess-eth-from-buy-orders-code4rena-caviar-caviar-private-pools-git>
- <https://solodit.xyz/issues/h-01-re-entrancy-in-settleauction-allow-stealing-all-funds-code4rena-kuiper-kuiper-contest-git>

**Cited by.** [2022-04-30 Rari Capital Fuse pools (~$80M)](../knowledge-base/case-studies/2022-04-30-rari-fei-fuse-reentrancy.md); [2022-03-15 Hundred Finance (~$6.2M)](../knowledge-base/case-studies/2022-03-15-hundred-finance-erc677-hook-reentrancy.md)

### SOL-Heuristics-4

**Question.** Is the NonReentrant modifier placed before every other modifier?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** The order of modifiers can influence the behavior of a function. Generally,  NonReentrant must come first than other modifiers.

**Remediation.** Reorder modifiers so that NonReentrant is placed before other modifiers.

### SOL-Token-NfE1-2

**Question.** Is the contract safe from reentrancy attack?

Source: Cyfrin / Solodit · upstream path: *Token › Non-fungible : ERC721/1155*

**Description.** By standard, the token receiver contracts implement onERC721Received and onERC1155Received and this can potentially be a source of reentrancy attacks if not correctly handled.

**Remediation.** Double check the potential reentrancy attack.

### SOL-Token-NfE1-3

**Question.** Is the OpenZeppelin implementation of ERC721 and ERC1155 safeguarded against reentrancy attacks, especially in the `safeTransferFrom` functions?

Source: Cyfrin / Solodit · upstream path: *Token › Non-fungible : ERC721/1155*

**Description.** The `safeTransferFrom` functions in OpenZeppelin's ERC721 and ERC1155 can expose the contract to reentrancy attacks due to external calls to user addresses.

**Remediation.** Use the checks-effects-interactions pattern and implement reentrancy guards to prevent potential reentrancy attacks when making external calls.

## 2. Access Control

### SC-AC-1

**Question.** Is every state-changing/privileged function gated by the correct modifier?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/access-control.md`](../knowledge-base/vulnerabilities/access-control.md)

**Cited by.** [2021-08-10 Poly Network (~$611M)](../knowledge-base/case-studies/2021-08-10-poly-network-cross-chain-keeper-swap.md)

### SC-AC-2

**Question.** Any function that *should* be `onlyOwner`/role-gated but is public?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/access-control.md`](../knowledge-base/vulnerabilities/access-control.md)

**Cited by.** [2021-09-03 DAO Maker (~$4M)](../knowledge-base/case-studies/2021-09-03-dao-maker-unprotected-init.md)

### SC-AC-3

**Question.** Is `tx.origin` used for authorization? (phishable; should be `msg.sender`)

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/access-control.md`](../knowledge-base/vulnerabilities/access-control.md)

### SC-AC-4

**Question.** Are initializers protected against being called twice / by anyone?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/access-control.md`](../knowledge-base/vulnerabilities/access-control.md)

**Cited by.** [2022-07-23 Audius (704 ETH)](../knowledge-base/case-studies/2022-07-23-audius-storage-collision-governance.md); [2021-09-03 DAO Maker (~$4M)](../knowledge-base/case-studies/2021-09-03-dao-maker-unprotected-init.md)

### SC-AC-5

**Question.** Are role admins set correctly? Can a role escalate itself?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/access-control.md`](../knowledge-base/vulnerabilities/access-control.md)

### SC-AC-6

**Question.** Is there a default-admin or emergency backdoor that concentrates too much power?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/access-control.md`](../knowledge-base/vulnerabilities/access-control.md)

### SOL-AM-RP-1

**Question.** Can the admin of the protocol pull assets from the protocol?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Rug Pull*

**Description.** Some protocols grant an admin with a privilege of pulling assets directly from the protocol. In general, if there is an actor that can affect the user funds directly it must be reported.

**Remediation.** Allow access to only the relevant parts of protocol funds, e.g. by tracking fees internally. Forcing a timelock on the admin actions can be another mitigation.

**References.**
- <https://solodit.xyz/issues/m-06-centralisation-risk-admin-role-of-tokenmanagereth-can-rug-pull-all-eth-from-the-bridge-code4rena-skale-skale-contest-git>

### SOL-Basics-AC-1

**Question.** Did you clarify all the actors and their allowed interactions in the protocol?

Source: Cyfrin / Solodit · upstream path: *Basics › Access Control*

**Description.** This is a general check item. Having a clear understanding of all relevant actors and interactions in the protocol is critical for security.

**Remediation.** List down all the actors and interactions and draw a diagram.

### SOL-Basics-AC-2

**Question.** Are there functions lacking proper access controls?

Source: Cyfrin / Solodit · upstream path: *Basics › Access Control*

**Description.** Access controls determine who can use certain functions of a contract. If these are missing or improperly implemented, it can expose the contract to unauthorized changes or withdrawals.

**Remediation.** Implement and rigorously test access controls like `onlyOwner` or role-based permissions to ensure only authorized users can access certain functions.

**Cited by.** [2021-09-03 DAO Maker (~$4M)](../knowledge-base/case-studies/2021-09-03-dao-maker-unprotected-init.md)

### SOL-Basics-AC-3

**Question.** Do certain addresses require whitelisting?

Source: Cyfrin / Solodit · upstream path: *Basics › Access Control*

**Description.** Whitelisting allows only a specific set of addresses to interact with the contract, offering an additional layer of security against malicious actors.

**Remediation.** Establish a whitelisting mechanism and ensure that only trusted addresses can execute sensitive or restricted operations.

### SOL-Basics-AC-4

**Question.** Does the protocol allow transfer of privileges?

Source: Cyfrin / Solodit · upstream path: *Basics › Access Control*

**Description.** Transfer of critical privileges must be done in two-step process. A two-step transfer process, usually involving a request followed by a confirmation, adds an extra layer of security against unintentional or malicious owner changes.

**Remediation.** Implement a two-step transfer mechanism that requires the new actor to accept the transfer, ensuring better security and intentional ownership changes.

### SOL-Basics-AC-5

**Question.** What happens during the transfer of privileges?

Source: Cyfrin / Solodit · upstream path: *Basics › Access Control*

**Description.** The protocol needs to work consistently and reasonably even during the transfer of privileges.

**Remediation.** Double check how the protocol works during the transfer of privileges.

### SOL-Basics-AC-6

**Question.** Does the contract inherit others?

Source: Cyfrin / Solodit · upstream path: *Basics › Access Control*

**Description.** If you do not override a parent contract's function explicitly, the parent's one will be exposed with its visibility and probably a wrong accessibiliy.

**Remediation.** Make sure you check the accessibility to the parent's external/public functions.

### SOL-Basics-AC-7

**Question.** Does the contract use `tx.origin` in validation?

Source: Cyfrin / Solodit · upstream path: *Basics › Access Control*

**Description.** Use of `tx.origin` for authorization may be abused by a malicious contract forwarding calls from the legitimate user. Use `msg.sender` instead. `require( tx.origin == msg.sender)` is a useful check to ensure that the `msg.sender` is an EOA(externally owned account).

**Remediation.** Make sure you know the difference of `tx.origin` and `msg.sender` and use properly.

**References.**
- <https://swcregistry.io/docs/SWC-115>

### SOL-Basics-Function-7

**Question.** Should it be `external`/`public`?

Source: Cyfrin / Solodit · upstream path: *Basics › Function*

**Description.** Ensure the visibility modifier is appropriate for the function's use, preventing unnecessary exposure.

**Remediation.** Limit function visibility to the strictest level possible (`private` or `internal`).

### SOL-Basics-Function-8

**Question.** Does this function need to be called by only EOA or only contracts?

Source: Cyfrin / Solodit · upstream path: *Basics › Function*

**Description.** There are several edge cases regarding the caller checking mechanism, both for EOA and contracts.

**Remediation.** Ensure the correct access control is implemented according to the protocol's context. (read all the references)

**References.**
- <https://solodit.xyz/issues/m-15-onlyeoaex-modifier-that-ensures-call-is-from-eoa-might-not-hold-true-in-the-future-sherlock-blueberry-blueberry-git>
- <https://solodit.xyz/issues/m-17-addressiscontract-is-not-a-reliable-way-of-checking-if-the-input-is-an-eoa-code4rena-stakehouse-protocol-lsd-network-stakehouse-contest-git>

### SOL-Basics-Function-9

**Question.** Does this function need to be restricted for specific callers?

Source: Cyfrin / Solodit · upstream path: *Basics › Function*

**Description.** Ensure that functions modifying contract state or accessing sensitive operations are access-controlled.

**Remediation.** Implement access control mechanisms like `onlyOwner` or custom modifiers.

**References.**
- <https://solodit.xyz/issues/h-8-lack-of-access-control-for-mintrebalancer-and-burnrebalancer-sherlock-none-ussd-autonomous-secure-dollar-git>
- <https://solodit.xyz/issues/h-02-anyone-can-change-approvaldisapproval-threshold-for-any-action-using-llamarelativequorum-strategy-code4rena-llama-llama-git>
- <https://solodit.xyz/issues/anyone-can-take-a-loan-out-on-behalf-of-any-collateral-holder-at-any-terms-spearbit-astaria-pdf>

### SOL-Basics-Inheritance-1

**Question.** Is it necessary to limit visibility of parent contract's public functions?

Source: Cyfrin / Solodit · upstream path: *Basics › Inheritance*

**Description.** External/Public functions of all parent contracts will be exposed with the same visibility as long as they are not overridden.

**Remediation.** Make sure to expose only relevant functions from parent contracts.

### SOL-CR-1

**Question.** What happens to the user accounting in special conditions?

Source: Cyfrin / Solodit · upstream path: *Centralization Risk*

**Description.** Users must be allowed to manage their existing positions in all protocol status. For example, users must be able to repay the debt even when the protocol is paused or the protocol should not accrue debts when it is paused.

**Remediation.** Ensure user positions are protected in special/emergent protocol situations.

### SOL-CR-2

**Question.** Is there a pause mechanism?

Source: Cyfrin / Solodit · upstream path: *Centralization Risk*

**Description.** Some functionalities must work even when the whole protocol is paused. For example, users must be able to withdraw (or repay) assets even while the protocol is paused.

**Remediation.** Review the pause mechanism thoroughly to ensure that it only affects intended functions and can't be abused by a malicious operator.

### SOL-CR-3

**Question.** Is there a functionality for the admin to withdraw from the protocol?

Source: Cyfrin / Solodit · upstream path: *Centralization Risk*

**Description.** Some protocols are written to allow admin pull any amount of assets from the pool. This is a red flag and MUST be disallowed. The best practice is to track the protocol fee and only allow access to that amount.

**Remediation.** Ensure the admin can not steal user funds. Track the protocol earning separately.

### SOL-CR-4

**Question.** Can the admin change critical protocol property immediately?

Source: Cyfrin / Solodit · upstream path: *Centralization Risk*

**Description.** Changes in the critical protocol properties MUST go through a cooling period to allow users react on the changes.

**Remediation.** Implement a timelock for the critical property changes and emit proper events.

### SOL-CR-5

**Question.** Is there any admin setter function missing events?

Source: Cyfrin / Solodit · upstream path: *Centralization Risk*

**Description.** Events are often used to monitor the protocol status. Without emission of events, users might be affected due to ignorance of the changes.

**Remediation.** Emit proper events on critical configuration changes.

### SOL-CR-6

**Question.** How is the ownership/privilege transferred??

Source: Cyfrin / Solodit · upstream path: *Centralization Risk*

**Description.** Critical privileges MUST be transferred via a two-step process and the protocol MUST behave as expected before/during/after transfer.

**Remediation.** Use two-step process for transferring critical privileges and ensure the protocol works properly before/during/after the transfer.

### SOL-CR-7

**Question.** Is there a proper validation in privileged setter functions?

Source: Cyfrin / Solodit · upstream path: *Centralization Risk*

**Description.** The validation on the protocol configuration values is often overlooked assuming the admin is trusted. But it is always recommended clarifying the range of each configuration value and validate in setter functions. (e.g. protocol fee should be limited)

**Remediation.** Ensure the protocol level properties are properly validated in the documented range.

### SOL-Defi-LSD-5

**Question.** Can paused states be bypassed to perform restricted actions even when they should be paused?

Source: Cyfrin / Solodit · upstream path: *Defi › Liquid Staking Derivatives*

**Description.** LSD protocols often implement pausing of different functionality. Auditors should check if there are any gaps where for example one function is missing a pause check that other related functions contain.

**Remediation.** All related functions should contain the same related pause checks.

### SOL-EC-14

**Question.** How is the msg.sender handled?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** On interacting with external contracts, the caller becomes a new `msg.sender` instead of the original caller.

**Remediation.** Ensure the validation is in place to check the actor is handled correctly.

**References.**
- <https://solodit.xyz/issues/swapinternal-shouldnt-use-msgsender-spearbit-connext-pdf>
- <https://solodit.xyz/issues/m-01-onlycentrifugechainorigin-cant-require-msgsender-equal-axelargateway-code4rena-centrifuge-centrifuge-git>

### SOL-Integrations-GS-1

**Question.** Do your modules execute the Guard's hooks?

Source: Cyfrin / Solodit · upstream path: *Integrations › Gnosis Safe*

**Description.** Failing to execute the Guard's hooks  (`checkTransaction()`, `checkAfterExecution()`) can bypass critical security checks implemented in those hooks.

**Remediation.** Ensure that all modules correctly execute the Guard's hooks as intended.

## 3. Arithmetic & Precision

### SC-MATH-1

**Question.** Any `unchecked` blocks where overflow/underflow is actually reachable?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/arithmetic-and-precision.md`](../knowledge-base/vulnerabilities/arithmetic-and-precision.md)

**Cited by.** [2022-03-20 Umbrella Network (~$700K)](../knowledge-base/case-studies/2022-03-20-umbrella-network-staking-underflow.md)

### SC-MATH-2

**Question.** Does division happen before multiplication, losing precision?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/arithmetic-and-precision.md`](../knowledge-base/vulnerabilities/arithmetic-and-precision.md)

### SC-MATH-3

**Question.** What direction does rounding go, and who profits? Can it be repeated to drain?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/arithmetic-and-precision.md`](../knowledge-base/vulnerabilities/arithmetic-and-precision.md)

**Cited by.** [2023-04-15 Hundred Finance (~$7M)](../knowledge-base/case-studies/2023-04-15-hundred-finance-empty-market-exchange-rate.md)

### SC-MATH-4

**Question.** First-depositor / share-inflation: can a tiny first deposit + donation make shares mis-price for later depositors? (ERC-4626 classic)

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/arithmetic-and-precision.md`](../knowledge-base/vulnerabilities/arithmetic-and-precision.md)

**Cited by.** [2023-04-15 Hundred Finance (~$7M)](../knowledge-base/case-studies/2023-04-15-hundred-finance-empty-market-exchange-rate.md)

### SC-MATH-5

**Question.** Are decimals normalized across tokens of different precision?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/arithmetic-and-precision.md`](../knowledge-base/vulnerabilities/arithmetic-and-precision.md)

### SC-MATH-6

**Question.** Any casts (`uint256`→`uint128`, signed↔unsigned) that silently truncate?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/arithmetic-and-precision.md`](../knowledge-base/vulnerabilities/arithmetic-and-precision.md)

### SC-MATH-7

**Question.** Empty-market / zero-supply edge: what do exchange rates and rounding do when `totalSupply` is 0 or a few wei (Compound v2 `redeemUnderlying` rounding, first `mint` after a full redeem)?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/arithmetic-and-precision.md`](../knowledge-base/vulnerabilities/arithmetic-and-precision.md) · added from: case study 2023-04-15 Hundred Finance

**Cited by.** [2023-04-15 Hundred Finance (~$7M)](../knowledge-base/case-studies/2023-04-15-hundred-finance-empty-market-exchange-rate.md)

### SOL-Basics-Math-1

**Question.** Is the mathematical calculation accurate?

Source: Cyfrin / Solodit · upstream path: *Basics › Math*

**Description.** Ensure that the logic behind any mathematical operation is correctly implemented.

**Remediation.** Verify calculations against established mathematical rules in the document or the comments.

### SOL-Basics-Math-2

**Question.** Is there any loss of precision in time calculations?

Source: Cyfrin / Solodit · upstream path: *Basics › Math*

**Description.** Loss of precision can lead to significant errors over time or frequent calculations.

**Remediation.** Use appropriate data types and ensure rounding methods are correctly applied.

### SOL-Basics-Math-3

**Question.** Are you aware that expressions like `1 day` are cast to `uint24`, potentially causing overflows?

Source: Cyfrin / Solodit · upstream path: *Basics › Math*

**Description.** Operations with certain expressions might lead to unintended data type conversions.

**Remediation.** Always be explicit with data types and avoid relying on implicit type conversions.

### SOL-Basics-Math-4

**Question.** Is there any case where dividing is done before multiplication?

Source: Cyfrin / Solodit · upstream path: *Basics › Math*

**Description.** Multiplying before division is generally better to keep the precision.

**Remediation.** To avoid loss of precision, always multiply first and then divide.

### SOL-Basics-Math-5

**Question.** Does the rounding direction matter?

Source: Cyfrin / Solodit · upstream path: *Basics › Math*

**Description.** Rounding direction often matters when the accounting relies on user's shares.

**Remediation.** Use the proper rounding direction in favor of the protocol

**Cited by.** [2023-04-15 Hundred Finance (~$7M)](../knowledge-base/case-studies/2023-04-15-hundred-finance-empty-market-exchange-rate.md)

### SOL-Basics-Math-6

**Question.** Is there a possibility of division by zero?

Source: Cyfrin / Solodit · upstream path: *Basics › Math*

**Description.** Division by zero will revert the transaction.

**Remediation.** Always check denominators before division.

### SOL-Basics-Math-7

**Question.** Even in versions like `>0.8.0`, have you ensured variables won't underflow or overflow leading to reverts?

Source: Cyfrin / Solodit · upstream path: *Basics › Math*

**Description.** Variables can sometimes exceed their bounds, causing reverts.

**Remediation.** Use checks to prevent variable underflows and overflows.

**Cited by.** [2022-03-20 Umbrella Network (~$700K)](../knowledge-base/case-studies/2022-03-20-umbrella-network-staking-underflow.md)

### SOL-Basics-Math-8

**Question.** Are you aware that assigning a negative value to an unsigned integer causes a revert?

Source: Cyfrin / Solodit · upstream path: *Basics › Math*

**Description.** Unsigned integers cannot hold negative values.

**Remediation.** Always ensure that only non-negative values are assigned to unsigned integers.

### SOL-Basics-Math-9

**Question.** Have you properly reviewed all usages of `unchecked{}`?

Source: Cyfrin / Solodit · upstream path: *Basics › Math*

**Description.** Arithmetics do not overflow inside the `unchecked{}` block.

**Remediation.** Use `unchecked{}` only when it is strictly guaranteed that no overflow/underflow happens.

### SOL-Basics-Math-10

**Question.** In comparisons using < or >, should you instead be using ≤ or ≥?

Source: Cyfrin / Solodit · upstream path: *Basics › Math*

**Description.** Usage of incorrect inequality can cause unexpected behavior for the edge values.

**Remediation.** Review the logic and ensure the appropriate comparison operators are used.

### SOL-Basics-Math-11

**Question.** Have you taken into consideration mathematical operations in inline assembly?

Source: Cyfrin / Solodit · upstream path: *Basics › Math*

**Description.** Inline assembly can behave differently than high-level language constructs. (division by zero, overflow/underflow do not revert!)

**Remediation.** Ensure mathematical operations in inline assembly are properly tested and verified.

### SOL-Basics-Math-12

**Question.** What happens for the minimum/maximum values included in the calculation?

Source: Cyfrin / Solodit · upstream path: *Basics › Math*

**Description.** If the calculation includes numerous terms, you need to confirm all edge cases where each term has the possible min/max values.

**Remediation.** Ensure the edge cases do not lead to unexpected outcome.

**Cited by.** [2022-03-20 Umbrella Network (~$700K)](../knowledge-base/case-studies/2022-03-20-umbrella-network-staking-underflow.md)

### SOL-Basics-Type-1

**Question.** Is there a forced type casting?

Source: Cyfrin / Solodit · upstream path: *Basics › Type*

**Description.** Explicit type casting does not revert on overflow/underflow.

**Remediation.** Avoid a forced type casting as much as possible and ensure values are in the range of type limit.

**References.**
- <https://solodit.xyz/issues/risk-of-token-theft-due-to-unchecked-type-conversion-trailofbits-none-primitive-hyper-pdf>

### SOL-Basics-Type-2

**Question.** Does the protocol use time units like `days`?

Source: Cyfrin / Solodit · upstream path: *Basics › Type*

**Description.** The time units are of `uint8` type and this can lead to unintended overflow.

**Remediation.** Double check the calculations including time units and ensure there is no overflow for reasonable values.

**References.**
- <https://solodit.xyz/issues/m-05-expiration-calculation-overflows-if-call-option-duration-195-days-code4rena-cally-cally-contest-git>

### SOL-Defi-LSD-9

**Question.** Does unnecessary precision loss occur in deposit, withdrawal or reward calculations?

Source: Cyfrin / Solodit · upstream path: *Defi › Liquid Staking Derivatives*

**Description.** Mathematical calculations have to be performed in LSD protocol deposit, withdrawal and reward functions. Auditors should check for precision loss issues such as division before multiplication, rounding down to zero etc.

**Remediation.** Don't perform division before multiplication, be aware of rounding down to zero, rounding direction, unsafe casting etc.

### SOL-Heuristics-7

**Question.** Are there any off-by-one errors?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** Off-by-one errors are not rare. Is `<=` correct in this context or should `<` be used? Should a variable be set to the length of a list or the length - 1? Should an iteration start at 1 or 0?

**Remediation.** Review all usages of comparison operators for correctness.

### SOL-Heuristics-10

**Question.** Are there rounding errors that can be amplified?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** While minor rounding errors can be inevitable in certain operations, they can pose significant issues if they can be magnified. Amplification can occur when a function is invoked multiple times strategically or under specific conditions.

**Remediation.** Conduct thorough tests to identify and understand potential rounding errors. Ensure that they cannot be amplified to a level that would be detrimental to the system or its users. In cases where significant rounding errors are detected, the implementation should be revised to minimize or eliminate them.

**References.**
- <https://github.com/OpenCoreCH/smart-contract-audits/blob/main/reports/c4/rigor.md#high-significant-rounding-errors-for-interest-calculation>

**Cited by.** [2023-04-15 Hundred Finance (~$7M)](../knowledge-base/case-studies/2023-04-15-hundred-finance-empty-market-exchange-rate.md)

### SOL-Heuristics-17

**Question.** Does calling a function multiple times with smaller amounts yield the same contract state as calling it once with the aggregate amount?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** Associative properties of certain financial operations suggest that performing the operation multiple times with smaller amounts should yield an equivalent outcome as performing it once with the aggregate amount. Variations might be indicative of potential issues such as rounding errors, unintended fee accumulations, or other inconsistencies.

**Remediation.** Implement tests to validate consistency. Where discrepancies exist, ensure they are intentional, minimal, and well-documented. If discrepancies are unintended, reevaluate the implementation to ensure precision and correctness.

### SOL-Integrations-Uniswap-7

**Question.** Is `unchecked` used properly with Uniswap's math libraries?

Source: Cyfrin / Solodit · upstream path: *Integrations › Uniswap*

**Description.** Uniswap's TickMath and FullMath libraries require careful usage of `unchecked` due to solidity version specifics.

**Remediation.** Review and test the use of `unchecked` in contracts utilizing Uniswap's math libraries to ensure safety and correctness.

**References.**
- <https://solodit.xyz/issues/use-unchecked-intickmathsol-andfullmathsol-spearbit-overlay-pdf>

### SOL-LL-5

**Question.** Is there a non-zero check for the denominator?

Source: Cyfrin / Solodit · upstream path: *Low Level*

**Description.** At the evm level and in yul/inline assembly, when dividing or modulo'ing by 0, It does not revert with Panic(18) as solidity would do, its result 0. If this behavior is not desired it should be checked. Basically, x / 0 = 0 and x % 0 = 0.

**Remediation.** Check if the denominator is zero before division.

**References.**
- <https://github.com/AmadiMichael/LowLevelVulnerabilities?tab=readme-ov-file#when-dividing-or-moduloin-check-that-the-denominator-is-not-0>

## 4. Oracle & Price Manipulation

### SC-ORACLE-1

**Question.** Does pricing use a **spot price** from an AMM reserve/`getReserves`/`balanceOf`? (manipulable in one tx via flash loan)

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/oracle-and-price-manipulation.md`](../knowledge-base/vulnerabilities/oracle-and-price-manipulation.md)

**Cited by.** [2021-10-27 C.R.E.A.M. Finance (~$130M)](../knowledge-base/case-studies/2021-10-27-cream-finance-yusd-price-manipulation.md); [2021-05-19 PancakeBunny (~$45M)](../knowledge-base/case-studies/2021-05-19-pancakebunny-flash-loan-lp-pricing.md); [2020-10-26 Harvest Finance fUSDC / fUSDT vaults (~$33.8M)](../knowledge-base/case-studies/2020-10-26-harvest-finance-curve-pool-manipulation.md)

### SC-ORACLE-2

**Question.** For Chainlink: are `updatedAt` staleness and `answeredInRound` checked? Is a zero/negative price handled? Are min/max bounds considered?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/oracle-and-price-manipulation.md`](../knowledge-base/vulnerabilities/oracle-and-price-manipulation.md)

### SC-ORACLE-3

**Question.** Is a TWAP used, and is its window long enough to resist manipulation?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/oracle-and-price-manipulation.md`](../knowledge-base/vulnerabilities/oracle-and-price-manipulation.md)

### SC-ORACLE-4

**Question.** Does the protocol trust `token.balanceOf(pair)` for accounting? (donation-manipulable)

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/oracle-and-price-manipulation.md`](../knowledge-base/vulnerabilities/oracle-and-price-manipulation.md)

**Cited by.** [2021-10-27 C.R.E.A.M. Finance (~$130M)](../knowledge-base/case-studies/2021-10-27-cream-finance-yusd-price-manipulation.md)

### SC-ORACLE-5

**Question.** What happens if the oracle reverts or returns stale data: fail open or closed?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/oracle-and-price-manipulation.md`](../knowledge-base/vulnerabilities/oracle-and-price-manipulation.md)

### SC-ORACLE-6

**Question.** Is a price or exchange rate derived from a pool or vault that a flash loan can inflate in the same transaction (LP-token pricing, `get_virtual_price`, `pricePerShare`, a cToken `exchangeRate` on a near-empty market)?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/oracle-and-price-manipulation.md`](../knowledge-base/vulnerabilities/oracle-and-price-manipulation.md) · added from: case studies PancakeBunny, Cream, Harvest, dForce

**Cited by.** [2023-02-10 dForce (~$3.65M)](../knowledge-base/case-studies/2023-02-10-dforce-read-only-reentrancy.md); [2021-10-27 C.R.E.A.M. Finance (~$130M)](../knowledge-base/case-studies/2021-10-27-cream-finance-yusd-price-manipulation.md); [2021-05-19 PancakeBunny (~$45M)](../knowledge-base/case-studies/2021-05-19-pancakebunny-flash-loan-lp-pricing.md); [2020-10-26 Harvest Finance fUSDC / fUSDT vaults (~$33.8M)](../knowledge-base/case-studies/2020-10-26-harvest-finance-curve-pool-manipulation.md)

### SOL-AM-PMA-1

**Question.** Is the price calculated by the ratio of token balances?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Price Manipulation Attack*

**Description.** Price can be manipulated via flash loans or donations if it is derived from the ratio of token balances.

**Remediation.** Use the Chainlink oracles for the asset prices.

**References.**
- <https://solodit.xyz/issues/h-05-flash-loan-price-manipulation-in-purchasepyroflan-code4rena-behodler-behodler-contest-git>
- <https://solodit.xyz/issues/h-05-underlying-assets-stealing-in-autopxgmx-and-autopxglp-via-share-price-manipulation-code4rena-redacted-cartel-redacted-cartel-contest-git>
- <https://solodit.xyz/issues/h-02-use-of-slot0-to-get-sqrtpricelimitx96-can-lead-to-price-manipulation-code4rena-maia-dao-ecosystem-maia-dao-ecosystem-git>

**Cited by.** [2021-10-27 C.R.E.A.M. Finance (~$130M)](../knowledge-base/case-studies/2021-10-27-cream-finance-yusd-price-manipulation.md); [2021-05-19 PancakeBunny (~$45M)](../knowledge-base/case-studies/2021-05-19-pancakebunny-flash-loan-lp-pricing.md)

### SOL-AM-PMA-2

**Question.** Is the price calculated from DEX liquidity pool spot prices?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Price Manipulation Attack*

**Description.** Spot price readings derived directly from DEX liquidity pools are vulnerable to manipulation through flash loans that can temporarily drain the pools.

**Remediation.** Use TWAP (time-weighted average price) with appropriate time windows based on asset volatility and liquidity, or use reliable oracle solutions.

**References.**
- <https://solodit.cyfrin.io/issues/h-08-omooracle-getliquidityamounts-uses-spot-price-making-it-manipulatable-pashov-audit-group-none-omo_2025-01-25-markdown>
- <https://solodit.cyfrin.io/issues/h-03-the-use-of-spot-price-by-coresaltyfeed-can-lead-to-price-manipulation-and-undesired-liquidations-code4rena-saltyio-saltyio-git>

**Cited by.** [2021-05-19 PancakeBunny (~$45M)](../knowledge-base/case-studies/2021-05-19-pancakebunny-flash-loan-lp-pricing.md); [2020-10-26 Harvest Finance fUSDC / fUSDT vaults (~$33.8M)](../knowledge-base/case-studies/2020-10-26-harvest-finance-curve-pool-manipulation.md)

### SOL-Defi-General-5

**Question.** Are the protocol token pegged to any other asset?

Source: Cyfrin / Solodit · upstream path: *Defi › General*

**Description.** The target tokens can be depegged.

**Remediation.** Ensure the protocol behave as expected during the depeg.

### SOL-Defi-LSD-8

**Question.** If using a Proof Of Reserves Oracle, does the protocol check for stale data?

Source: Cyfrin / Solodit · upstream path: *Defi › Liquid Staking Derivatives*

**Description.** LSD protocols may use an external Proof of Reserves Oracle to fetch off-chain data for their current ETH reserves. If the protocol doesn't check how long ago the data was last updated it can process stale data as if it were fresh.

**Remediation.** Check the time data was last updated against the Oracle's heartbeat and revert if the data is too old.

### SOL-Defi-Oracle-1

**Question.** Is the Oracle using deprecated Chainlink functions?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** Usage of deprecated Chainlink functions like latestRoundData() might return stale or incorrect data, affecting the integrity of smart contracts.

**Remediation.** Replace deprecated functions with the current recommended methods to ensure accurate data retrieval from oracles.

**References.**
- <https://github.com/code-423n4/2022-04-backd-findings/issues/17>

### SOL-Defi-Oracle-2

**Question.** Is the returned price validated to be non-zero?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** Price feed might return zero and this must be handled as invalid.

**Remediation.** Ensure the returned price is not zero.

### SOL-Defi-Oracle-3

**Question.** Is the price update time validated?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** Price feeds might not be supported in the future. To ensure accurate price usage, it's vital to regularly check the last update timestamp against a predefined delay.

**Remediation.** Implement a mechanism to check the heartbeat of the price feed and compare it against a predefined maximum delay (`MAX_DELAY`). Adjust the `MAX_DELAY` variable based on the observed heartbeat.

### SOL-Defi-Oracle-4

**Question.** Is there a validation to check if the rollup sequencer is running?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** The rollup sequencer can become offline, which can lead to potential vulnerabilities due to stale price.

**Remediation.** Utilize the sequencer uptime feed to confirm the sequencers are up.

**References.**
- <https://docs.chain.link/data-feeds/l2-sequencer-feeds>

### SOL-Defi-Oracle-5

**Question.** Is the Oracle's TWAP period appropriately set?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** An inadequately set TWAP (Time-Weighted Average Price) period could be exploited to manipulate prices.

**Remediation.** Adjust the TWAP period to a duration that mitigates the risk of manipulation while providing timely price updates.

**References.**
- <https://github.com/code-423n4/2022-06-canto-v2-findings/issues/124>

### SOL-Defi-Oracle-6

**Question.** Is the desired price feed pair supported across all deployed chains?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** In multi-chain deployments, it's crucial to ensure the desired price feed pair is available and consistent across all chains.

**Remediation.** Review the supported price feed pairs on all chains and ensure they are consistent.

### SOL-Defi-Oracle-7

**Question.** Is the heartbeat of the price feed suitable for the use case?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** A price feed heartbeat that's too slow might not be suitable for some use cases.

**Remediation.** Assess the requirements of the use case and ensure the price feed heartbeat aligns with them.

### SOL-Defi-Oracle-8

**Question.** Are there any inconsistencies with decimal precision when using different price feeds?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** Different price feeds might have varying decimal precisions, which can lead to inaccuracies.

**Remediation.** Ensure that the contract handles potential variations in decimal precision across different price feeds.

### SOL-Defi-Oracle-9

**Question.** Is the price feed address hard-coded?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** Hard-coded price feed addresses can be problematic, especially if they become deprecated or if they're not accurate in the first place.

**Remediation.** Review and verify the hardcoded price feed addresses. Consider mechanisms to update the address if required in the future.

### SOL-Defi-Oracle-10

**Question.** What happens if oracle price updates are front-run?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** Oracle price updates can be front-run and cause various problems.

**Remediation.** Ensure the protocol is not affected in the case where oracle price updates are front-run.

**References.**
- <https://blog.angle.money/angle-research-series-part-1-oracles-and-front-running-d75184abc67>

### SOL-Defi-Oracle-11

**Question.** How does the system handle potential oracle reverts?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** Unanticipated oracle reverts can lead to Denial-Of-Service.

**Remediation.** Implement try/catch blocks around oracle calls and have alternative strategies ready.

### SOL-Defi-Oracle-12

**Question.** Are the price feeds appropriate for the underlying assets?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** Using an ETH price feed for stETH or a BTC price feed for WBTC can introduce risks associated with the underlying assets deviating from their pegs.

**Remediation.** Ensure that the price feeds accurately represent the underlying assets to address potential depeg risks.

### SOL-Defi-Oracle-13

**Question.** Is the contract vulnerable to oracle manipulation, especially using spot prices from AMMs?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** Reliance on AMM spot prices as oracles can be manipulated via flashloan.

**Remediation.** Choose reliable and tamper-resistant oracle sources. Avoid using spot prices from AMMs directly without additional checks.

**Cited by.** [2023-02-10 dForce (~$3.65M)](../knowledge-base/case-studies/2023-02-10-dforce-read-only-reentrancy.md)

### SOL-Defi-Oracle-14

**Question.** How does the system address potential inaccuracies during flash crashes?

Source: Cyfrin / Solodit · upstream path: *Defi › Oracle*

**Description.** During flash crashes, oracles might return inaccurate prices.

**Remediation.** Implement checks to ensure that the price returned by the oracle lies within an expected range to guard against potential flash crash vulnerabilities.

### SOL-Integrations-Balancer-2

**Question.** Does the protocol use Balancer's Oracle? (getTimeWeightedAverage)

Source: Cyfrin / Solodit · upstream path: *Integrations › Balancer*

**Description.** The price will only be updated whenever a transaction (e.g. swap) within the Balancer pool is triggered. Due to the lack of updates, the price provided by Balancer Oracle will not reflect the true value of the assets.

**Remediation.** Do not use the Balancer's oracle for any pricing.

**References.**
- <https://solodit.xyz/issues/m-13-rely-on-balancer-oracle-which-is-not-updated-frequently-sherlock-notional-notional-git>

### SOL-Integrations-Balancer-4

**Question.** Does the protocol use Balancer vault pool liquidity status for any pricing?

Source: Cyfrin / Solodit · upstream path: *Integrations › Balancer*

**Description.** Balancer vault does not charge any fees for flash loans at the moment. However, it is possible Balancer implements fees for flash loans in the future.

**Remediation.** Balancer pools are susceptible to manipulation of their external queries, and all integrations must now take an extra step of precaution when consuming data. Via readonly reentrancy, an attacker can force token balances and BPT supply to be out of sync, creating very inaccurate BPT prices.

**References.**
- <https://solodit.xyz/issues/h-13-balancerpairoracle-can-be-manipulated-using-read-only-reentrancy-sherlock-none-blueberry-update-git>

### SOL-Integrations-Uniswap-5

**Question.** Is there a reliance on pool reserves?

Source: Cyfrin / Solodit · upstream path: *Integrations › Uniswap*

**Description.** Relying on pool reserves can be risky, as they can be manipulated, especially using a flashloan.

**Remediation.** Implement alternative methods or checks without relying solely on pool reserves.

### SOL-Integrations-Uniswap-9

**Question.** Is `pool.slot0` being used to calculate sensitive information like current price and exchange rates?

Source: Cyfrin / Solodit · upstream path: *Integrations › Uniswap*

**Description.** `pool.slot0` can be easily manipulated via flash loans to sandwich attack users.

**Remediation.** Use UniswapV3 TWAP or Chainlink Price Oracle.

**References.**
- <https://solodit.xyz/issues/h-4-no-slippage-protection-during-repayment-due-to-dynamic-slippage-params-and-easily-influenced-slot0-sherlock-real-wagmi-2-git>
- <https://solodit.xyz/issues/h-02-use-of-slot0-to-get-sqrtpricelimitx96-can-lead-to-price-manipulation-code4rena-maia-dao-ecosystem-maia-dao-ecosystem-git>
- <https://docs.uniswap.org/concepts/protocol/oracle>

## 5. Flash Loans & Atomic Composition

### SC-FLASH-1

**Question.** Can any invariant be broken *within a single transaction* using borrowed capital?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/flash-loans.md`](../knowledge-base/vulnerabilities/flash-loans.md)

**Cited by.** [2023-03-13 Euler Finance (~$197M)](../knowledge-base/case-studies/2023-03-13-euler-finance-donate-to-reserves.md); [2022-04-30 Rari Capital Fuse pools (~$80M)](../knowledge-base/case-studies/2022-04-30-rari-fei-fuse-reentrancy.md); [2021-05-19 PancakeBunny (~$45M)](../knowledge-base/case-studies/2021-05-19-pancakebunny-flash-loan-lp-pricing.md); [2020-10-26 Harvest Finance fUSDC / fUSDT vaults (~$33.8M)](../knowledge-base/case-studies/2020-10-26-harvest-finance-curve-pool-manipulation.md)

### SC-FLASH-2

**Question.** Are governance votes / share prices / collateral ratios read at a point an attacker can inflate atomically?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/flash-loans.md`](../knowledge-base/vulnerabilities/flash-loans.md)

**Cited by.** [2022-04-16 Beanstalk Farms (~$182M)](../knowledge-base/case-studies/2022-04-16-beanstalk-flash-loan-governance.md); [2021-05-19 PancakeBunny (~$45M)](../knowledge-base/case-studies/2021-05-19-pancakebunny-flash-loan-lp-pricing.md)

### SC-FLASH-3

**Question.** Does the protocol assume "an attacker can't have $100M"? (they can, for one block)

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/flash-loans.md`](../knowledge-base/vulnerabilities/flash-loans.md)

**Cited by.** [2021-10-27 C.R.E.A.M. Finance (~$130M)](../knowledge-base/case-studies/2021-10-27-cream-finance-yusd-price-manipulation.md)

### SOL-Defi-FlashLoan-1

**Question.** Is withdraw disabled in the same block to prevent flashloan attacks?

Source: Cyfrin / Solodit · upstream path: *Defi › FlashLoan*

**Description.** Allowing withdrawals within the same block as other interactions may enable attackers to exploit flashloan vulnerabilities.

**Remediation.** Implement a delay or disable withdrawals within the same block where a deposit or loan action took place to mitigate such risks.

**Cited by.** [2020-10-26 Harvest Finance fUSDC / fUSDT vaults (~$33.8M)](../knowledge-base/case-studies/2020-10-26-harvest-finance-curve-pool-manipulation.md)

### SOL-Defi-FlashLoan-2

**Question.** Can ERC4626 be manipulated through flashloans?

Source: Cyfrin / Solodit · upstream path: *Defi › FlashLoan*

**Description.** ERC4626, the tokenized vault standard, could be susceptible to flashloan attacks if the underlying mechanisms do not adequately account for such threats.

**Remediation.** Ensure that ERC4626-related operations have in-built protections against rapid, in-block actions that could be leveraged by flashloans.

**References.**
- <https://github.com/code-423n4/2022-01-behodler-findings/issues/304>

### SOL-Defi-General-8

**Question.** Is it possible to withdraw in the same transaction of deposit?

Source: Cyfrin / Solodit · upstream path: *Defi › General*

**Description.** Protocols often provide various benefits to the depositors based on the deposit amount. This can lead to flashloan-deposit-harvest-withdraw attack cycle.

**Remediation.** Ensure the withdrawal is protected for some blocks after deposit.

### SOL-Integrations-AC-6

**Question.** Do flash loans on Aave inflate the pool index?

Source: Cyfrin / Solodit · upstream path: *Integrations › AAVE / Compound*

**Description.** Flash loans can influence the pool index (a maximum of 180 flashloans can be performed within a block).

**Remediation.** Implement mechanisms to manage the effects of flash loans on the pool index.

### SOL-Integrations-Balancer-1

**Question.** Does the protocol use the Balancer's flashloan?

Source: Cyfrin / Solodit · upstream path: *Integrations › Balancer*

**Description.** Balancer vault does not charge any fees for flash loans at the moment. However, it is possible Balancer implements fees for flash loans in the future.

**Remediation.** Ensure the protocol repays the fee together with the original debt on repayment in the `receiveFlashLoan` function.

**References.**
- <https://solodit.xyz/issues/receiveflashloan-does-not-account-for-fees-trailofbits-none-lindy-labs-sandclock-pdf>

### SOL-Token-FE-9

**Question.** Is there a flash-mint functionality?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Flash mints can drastically increase token supply temporarily, leading to potential abuse.

**Remediation.** Implement strict controls and checks around any flash mint functionality.

## 6. DeFi Business Logic

### SC-DEFI-1

**Question.** Lending: are collateral factor, health factor, and liquidation math correct at the boundaries? Can a position be made unliquidatable, or self-liquidated for profit?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/defi-logic.md`](../knowledge-base/vulnerabilities/defi-logic.md)

**Cited by.** [2023-03-13 Euler Finance (~$197M)](../knowledge-base/case-studies/2023-03-13-euler-finance-donate-to-reserves.md); [2023-02-17 Platypus Finance (~$8.5M)](../knowledge-base/case-studies/2023-02-17-platypus-emergency-withdraw-solvency.md)

### SC-DEFI-2

**Question.** AMM: are the swap invariant (`x*y=k`), fees, and reserves updated atomically and in the right order?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/defi-logic.md`](../knowledge-base/vulnerabilities/defi-logic.md)

**Cited by.** [2021-04-28 Uranium Finance (~$50M)](../knowledge-base/case-studies/2021-04-28-uranium-finance-k-constant-typo.md)

### SC-DEFI-3

**Question.** Staking/rewards: can rewards be double-claimed, claimed after unstake, or diluted/inflated via deposit timing?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/defi-logic.md`](../knowledge-base/vulnerabilities/defi-logic.md)

### SC-DEFI-4

**Question.** Vaults (ERC-4626): does `deposit`/`mint`/`withdraw`/`redeem` round in the protocol's favor? Is the first-deposit inflation attack mitigated?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/defi-logic.md`](../knowledge-base/vulnerabilities/defi-logic.md)

### SC-DEFI-5

**Question.** Fee logic: can fees be bypassed, set to values that break accounting, or round to zero?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/defi-logic.md`](../knowledge-base/vulnerabilities/defi-logic.md)

### SC-DEFI-6

**Question.** Slippage / deadline: are user-supplied `minOut` and `deadline` enforced?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/defi-logic.md`](../knowledge-base/vulnerabilities/defi-logic.md)

### SC-DEFI-7

**Question.** Do "emergency", "donate", "migrate" or "rescue" style functions re-run the same solvency / health / accounting checks as the normal path? (Euler `donateToReserves`, Platypus `emergencyWithdraw`)

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/defi-logic.md`](../knowledge-base/vulnerabilities/defi-logic.md) · added from: case studies Euler, Platypus

**Cited by.** [2023-03-13 Euler Finance (~$197M)](../knowledge-base/case-studies/2023-03-13-euler-finance-donate-to-reserves.md); [2023-02-17 Platypus Finance (~$8.5M)](../knowledge-base/case-studies/2023-02-17-platypus-emergency-withdraw-solvency.md)

### SOL-AM-DA-1

**Question.** Does the protocol rely on `balance` or `balanceOf` instead of internal accounting?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Donation Attack*

**Description.** Attackers can manipulate the accounting by donating tokens.

**Remediation.** Implement internal accounting instead of relying on `balanceOf` natively.

**References.**
- <https://solodit.xyz/issues/h-02-first-depositor-can-break-minting-of-shares-code4rena-prepo-prepo-contest-git>

**Cited by.** [2021-10-27 C.R.E.A.M. Finance (~$130M)](../knowledge-base/case-studies/2021-10-27-cream-finance-yusd-price-manipulation.md)

### SOL-Basics-Payment-3

**Question.** Are there vulnerabilities related to force-feeding?

Source: Cyfrin / Solodit · upstream path: *Basics › Payment*

**Description.** Certain actions like self-destruct, deterministic address feeding, and coinbase transactions can be used to force-feed contracts.

**Remediation.** Ensure the contract behaves as expected when receiving unexpected funds.

**References.**
- <https://scsfg.io/hackers/unexpected-ether/>

### SOL-Basics-Payment-4

**Question.** What is the minimum deposit/withdrawal amount?

Source: Cyfrin / Solodit · upstream path: *Basics › Payment*

**Description.** Dust deposit/withdrawal often can lead to various vulnerabilities, e.g. rounding issue in accounting or Denial-Of-Service.

**Remediation.** Add a threshold for the deposit/withdrawal amount.

### SOL-Defi-AS-3

**Question.** Is there a validation check for protocol reserves?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** Protocols may face risks if reserves are not validated and can be lent out, affecting the system's solvency.

**Remediation.** Ensure reserve validation logic is in place to safeguard the protocol's liquidity and overall health.

**References.**
- <https://github.com/sherlock-audit/2022-08-sentiment-judging/blob/main/122-M/1-report.md>

### SOL-Defi-AS-4

**Question.** Does the AMM utilize forked code?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** Using forked code, especially from known projects like Uniswap, can introduce known vulnerabilities if not updated or audited properly.

**Remediation.** Review the differences. Utilize tools such as contract-diff.xyz to compare and identify the origin of code snippets.

**Cited by.** [2021-04-28 Uranium Finance (~$50M)](../knowledge-base/case-studies/2021-04-28-uranium-finance-k-constant-typo.md)

### SOL-Defi-AS-5

**Question.** Are there rounding issues in product constant formulas?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** Rounding issues in the formulas can lead to inaccuracies or imbalances in token swaps and liquidity provisions.

**Remediation.** Review the mathematical operations in the AMM's formulas, ensuring they handle rounding appropriately without introducing vulnerabilities.

**Cited by.** [2021-04-28 Uranium Finance (~$50M)](../knowledge-base/case-studies/2021-04-28-uranium-finance-k-constant-typo.md)

### SOL-Defi-General-2

**Question.** Are there unexpected rewards accruing for user deposited assets?

Source: Cyfrin / Solodit · upstream path: *Defi › General*

**Description.** Some protocols or platforms may provide additional rewards for staked or deposited assets. If these rewards are not properly accounted for or managed, it could lead to discrepancies in the user's expected vs actual returns.

**Remediation.** The protocol should have mechanisms in place to track all potential rewards for user deposited assets. Users should be provided with clear interfaces or methods to claim any unexpected rewards to ensure fairness and transparency.

### SOL-Defi-General-3

**Question.** Could direct transfers of funds introduce vulnerabilities?

Source: Cyfrin / Solodit · upstream path: *Defi › General*

**Description.** Direct transfers of assets without using the protocol's logic can lead to various problems in accounting especially if the accounting relies on `balanceOf` (or `address.balance`).

**Remediation.** Implement the internal accounting so that it is not be affected by direct transfers.

### SOL-Defi-General-4

**Question.** Could the initial deposit introduce any issues?

Source: Cyfrin / Solodit · upstream path: *Defi › General*

**Description.** The first deposit can set certain parameters or conditions that subsequent deposits rely on.

**Remediation.** Test and ensure that the first deposit initializes and sets all necessary parameters correctly.

**Cited by.** [2023-04-15 Hundred Finance (~$7M)](../knowledge-base/case-studies/2023-04-15-hundred-finance-empty-market-exchange-rate.md)

### SOL-Defi-General-7

**Question.** What would happen if only 1 wei remains in the pool?

Source: Cyfrin / Solodit · upstream path: *Defi › General*

**Description.** Leaving residual amounts can lead to discrepancies in accounting or locked funds.

**Remediation.** Implement logic to handle minimal residual amounts in the pool.

### SOL-Defi-Lending-1

**Question.** Will the liquidation process function effectively during rapid market downturns?

Source: Cyfrin / Solodit · upstream path: *Defi › Lending*

**Description.** Failure to liquidate positions during sharp price drops can result in substantial platform losses.

**Remediation.** Ensure robustness during extreme market conditions.

### SOL-Defi-Lending-2

**Question.** Can a position be liquidated if the loan remains unpaid or if the collateral falls below the required threshold?

Source: Cyfrin / Solodit · upstream path: *Defi › Lending*

**Description.** If positions cannot be liquidated under these circumstances, it poses a risk to lenders who might not recover their funds.

**Remediation.** Ensure a reliable mechanism for liquidating under-collateralized or defaulting loans to safeguard lenders.

**Cited by.** [2023-02-17 Platypus Finance (~$8.5M)](../knowledge-base/case-studies/2023-02-17-platypus-emergency-withdraw-solvency.md)

### SOL-Defi-Lending-3

**Question.** Is it possible for a user to gain undue profit from self-liquidation?

Source: Cyfrin / Solodit · upstream path: *Defi › Lending*

**Description.** Self-liquidation profit loopholes can lead to potential system abuse and unintended financial consequences.

**Remediation.** Audit and test self-liquidation mechanisms to prevent any exploitative behaviors.

**Cited by.** [2023-03-13 Euler Finance (~$197M)](../knowledge-base/case-studies/2023-03-13-euler-finance-donate-to-reserves.md)

### SOL-Defi-Lending-4

**Question.** If token transfers or collateral additions are temporarily paused, can a user still be liquidated, even if they intend to deposit more funds?

Source: Cyfrin / Solodit · upstream path: *Defi › Lending*

**Description.** Unexpected pauses can place users at risk of unwarranted liquidations, despite their willingness to increase collateral.

**Remediation.** Implement safeguards that protect users from liquidation during operational pauses or interruptions.

### SOL-Defi-Lending-5

**Question.** If liquidations are temporarily suspended, what are the implications when they are resumed?

Source: Cyfrin / Solodit · upstream path: *Defi › Lending*

**Description.** Pausing liquidations can increase the solvency risk and lead to unpredictable behaviors upon resumption.

**Remediation.** Outline clear protocols for pausing and resuming liquidations, ensuring solvency is maintained.

### SOL-Defi-Lending-6

**Question.** Is it possible for users to manipulate the system by front-running and slightly increasing their collateral to prevent liquidations?

Source: Cyfrin / Solodit · upstream path: *Defi › Lending*

**Description.** Lenders must be prevented from griefing via front-running the liquidation.

**Remediation.** Ensure it is not possible to prevent liquidators by any means.

### SOL-Defi-Lending-7

**Question.** Are all positions, regardless of size, incentivized adequately for liquidation?

Source: Cyfrin / Solodit · upstream path: *Defi › Lending*

**Description.** Without proper incentives, small positions might be overlooked, leading to inefficiencies.

**Remediation.** Ensure a balanced incentive structure that motivates liquidators to address positions of all sizes.

### SOL-Defi-Lending-8

**Question.** Is interest considered during Loan-to-Value (LTV) calculation?

Source: Cyfrin / Solodit · upstream path: *Defi › Lending*

**Description.** Omitting interest in LTV calculations can result in inaccurate credit assessments.

**Remediation.** Include accrued interest in LTV calculations to maintain accurate and fair credit evaluations.

**References.**
- <https://solodit.xyz/issues/h-7-users-can-be-liquidated-prematurely-because-calculation-understates-value-of-underlying-position-sherlock-blueberry-blueberry-git>

### SOL-Defi-Lending-9

**Question.** Can liquidation and repaying be enabled or disabled simultaneously?

Source: Cyfrin / Solodit · upstream path: *Defi › Lending*

**Description.** Protocols might need to ensure that liquidation and repaying mechanisms are either both active or inactive to maintain consistency.

**Remediation.** Review protocol logic to allow or disallow liquidation and repaying functions collectively to avoid operational discrepancies.

**References.**
- <https://solodit.xyz/issues/m-2-liquidations-are-enabled-when-repayments-are-disabled-causing-borrowers-to-lose-funds-without-a-chance-to-repay-sherlock-blueberry-blueberry-git>

### SOL-Defi-Lending-10

**Question.** Is it possible to lend and borrow the same token within a single transaction?

Source: Cyfrin / Solodit · upstream path: *Defi › Lending*

**Description.** Protocols that allow the same token to be lent and borrowed in a single transaction may be vulnerable to attacks that exploit rapid price inflation or flash loans to manipulate the system.

**Remediation.** Protocols should implement constraints to prohibit the same token from being used in a lend and borrow action within the same block or transaction, reducing the risk of flash-loan attacks and other manipulative practices.

### SOL-Defi-Lending-11

**Question.** Is there a scenario where a liquidator might receive a lesser amount than anticipated?

Source: Cyfrin / Solodit · upstream path: *Defi › Lending*

**Description.** Discrepancies in liquidation returns can discourage liquidators and impact system stability.

**Remediation.** Ensure a clear and consistent calculation mechanism for liquidation rewards.

### SOL-Defi-Lending-12

**Question.** Is it possible for a user to be in a condition where they cannot repay their loan?

Source: Cyfrin / Solodit · upstream path: *Defi › Lending*

**Description.** Certain scenarios or conditions might prevent a user from repaying their loan, causing them to be perpetually in debt. This can be due to factors such as excessive collateralization, high fees, fluctuating token values, or other unforeseen events.

**Remediation.** Review the lending protocol's logic to ensure there are no conditions that could trap a user in perpetual debt. Implement safeguards to notify or protect users from taking actions that may lead to irrecoverable financial situations.

### SOL-Defi-LSD-1

**Question.** Can a malicious validator front-run setting withdrawal credentials?

Source: Cyfrin / Solodit · upstream path: *Defi › Liquid Staking Derivatives*

**Description.** A malicious Ethereum validator can betray a liquid staking protocol by front-running to first call `DepositContract::deposit` sending 1 ETH and passing their own withdrawal credentials; after the protocol's subsequent call succeeds the withdrawal credentials are not overwritten since only the "initial deposit" sets the withdrawals credentials while the second deposit is treated as a "top-up deposit".  The malicious validator now controls 33 ether with 32 ether belonging to the protocol's users and has set their own withdrawal credentials instead of the protocol's withdrawal credentials.

**Remediation.** The function which calls `DepositContract::deposit` should take as input `DepositContract.get_deposit_root` then check that the input deposit root matches the current one. This works as the current deposit root changes with every deposit.

### SOL-Defi-LSD-4

**Question.** Can an arbitrary exchange rate be set when processing queued withdrawals?

Source: Cyfrin / Solodit · upstream path: *Defi › Liquid Staking Derivatives*

**Description.** If an arbitrary exchange rate can be set when processing queued withdrawals this creates a subtle rug-pull vector of user withdrawals.

**Remediation.** When withdrawals are processed the current exchange rate should be retrieved in the same way as when withdrawals are created.

### SOL-Defi-LSD-6

**Question.** Can inter-related storage be corrupted, especially storage related to operators and validators?

Source: Cyfrin / Solodit · upstream path: *Defi › Liquid Staking Derivatives*

**Description.** To reduce the gas cost of reading from storage, protocols may use multiple inter-related data structures to store complex information like operator and validator information. Auditors should examine whether functions which update these inter-related data structures can be used to corrupt them by over-writing records which contain indexes into to another storage location.

**Remediation.** Protocols can use invariant fuzz testing with invariants which validate that relationships between inter-related data structures can't be broken by functions which update them.

### SOL-Defi-Staking-1

**Question.** Can a user amplify another user's time lock duration by stacking tokens on their behalf?

Source: Cyfrin / Solodit · upstream path: *Defi › Staking*

**Description.** If users can amplify time locks for others by stacking tokens, it may lead to unintended lock durations and potentially be exploited.

**Remediation.** Implement strict checks and controls to prevent users from influencing the time locks of other users through token stacking.

### SOL-Defi-Staking-2

**Question.** Can the distribution of rewards be unduly delayed or prematurely claimed?

Source: Cyfrin / Solodit · upstream path: *Defi › Staking*

**Description.** Manipulation in the timing of reward distribution can adversely affect users and the protocol's intended incentives.

**Remediation.** Implement time controls and constraints on reward distributions to maintain the protocol's intended behavior.

### SOL-Defi-Staking-3

**Question.** Are rewards up-to-date in all use-cases?

Source: Cyfrin / Solodit · upstream path: *Defi › Staking*

**Description.** The staking protocol often has a function to update the rewards (e.g. `updateRewards`) and sometimes it is used as a modifier. This update function MUST be called before all relevant operations.

**Remediation.** Ensure the update reward function is called properly in all places where the reward is relevant.

### SOL-Heuristics-12

**Question.** Can functions be invoked multiple times with identical parameters?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** Functions that should be unique per parameters set might be callable multiple times, leading to potential issues.

**Remediation.** Ensure functions have measures to prevent repeated calls with identical or similar parameters, especially when these calls can produce adverse effects.

### SOL-Heuristics-16

**Question.** Are there any code asymmetries?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** In many projects, there should be some symmetries for different functions. For instance, a `withdraw` function should (usually) undo all the state changes of a `deposit` function and a `delete` function should undo all the state changes of the corresponding `add` function. Asymmetries in these function pairs (e.g., forgetting to unset a field or to subtract from a value) can often lead to undesired behavior. Sometimes one side of a 'pair' is missing, like missing removing from a whitelist while there is a function to add to a whitelist.

**Remediation.** Review paired functions for symmetry and ensure they counteract each other's state changes appropriately.

**References.**
- <https://github.com/OpenCoreCH/smart-contract-auditing-heuristics#code-asymmetries>

**Cited by.** [2023-03-13 Euler Finance (~$197M)](../knowledge-base/case-studies/2023-03-13-euler-finance-donate-to-reserves.md); [2023-02-17 Platypus Finance (~$8.5M)](../knowledge-base/case-studies/2023-02-17-platypus-emergency-withdraw-solvency.md); [2021-04-28 Uranium Finance (~$50M)](../knowledge-base/case-studies/2021-04-28-uranium-finance-k-constant-typo.md)

### SOL-Integrations-AC-2

**Question.** What happens if the utilization rate is too high, and collateral cannot be retrieved?

Source: Cyfrin / Solodit · upstream path: *Integrations › AAVE / Compound*

**Description.** A high utilization rate can potentially mean that there aren't enough assets in the pool to allow users to withdraw their collateral.

**Remediation.** Ensure that there are mechanisms to handle user withdrawal when the utilization rate is high.

### SOL-Integrations-AC-3

**Question.** What happens if the protocol is paused?

Source: Cyfrin / Solodit · upstream path: *Integrations › AAVE / Compound*

**Description.** If the AAVE protocol is paused, the protocol can not interact with it.

**Remediation.** Ensure the protocol behaves as expected when the AAVE protocol is paused.

### SOL-Integrations-AC-4

**Question.** What happens if the pool becomes deprecated?

Source: Cyfrin / Solodit · upstream path: *Integrations › AAVE / Compound*

**Description.** Pools can be deprecated.

**Remediation.** Ensure the protocol behaves as expected when the Pools are paused.

### SOL-Integrations-AC-5

**Question.** What happens if assets you lend/borrow are within the same eMode category?

Source: Cyfrin / Solodit · upstream path: *Integrations › AAVE / Compound*

**Description.** Lending and borrowing assets within the same eMode category might have rules or limitations.

**Remediation.** Ensure the protocol behaves as expected when interacting with assets in the same eMode category.

### SOL-Integrations-AC-7

**Question.** Does the protocol properly implement AAVE/COMP reward claims?

Source: Cyfrin / Solodit · upstream path: *Integrations › AAVE / Compound*

**Description.** Misimplementation of reward claims can lead to users not receiving their correct rewards.

**Remediation.** Ensure a proper and tested implementation of AAVE/COMP reward claims.

### SOL-Integrations-AC-8

**Question.** On AAVE, what happens if a user reaches the maximum debt on an isolated asset?

Source: Cyfrin / Solodit · upstream path: *Integrations › AAVE / Compound*

**Description.** Reaching the maximum debt on an isolated asset can result in denial-of-service or other limitations on user actions.

**Remediation.** Ensure that the protocol works as expected when a user reaches the maximum debt.

### SOL-Integrations-AC-9

**Question.** Does borrowing an AAVE siloed asset restrict borrowing other assets?

Source: Cyfrin / Solodit · upstream path: *Integrations › AAVE / Compound*

**Description.** Borrowing a siloed asset on Aave will prohibit users from borrowing other assets.

**Remediation.** Make use of `getSiloedBorrowing(address asset)` to prevent unexpected problems.

**References.**
- <https://docs.aave.com/developers/whats-new/siloed-borrowing>

### SOL-Integrations-Balancer-3

**Question.** Does the protocol use Balancer's Boosted Pool?

Source: Cyfrin / Solodit · upstream path: *Integrations › Balancer*

**Description.** Balancer's Boosted Pool uses Phantom BPT where all pool tokens are minted at the time of pool creation and are held by the pool itself. Therefore, virtualSupply should be used instead of totalSupply to determine the amount of BPT supply in circulation.

**Remediation.** Ensure the protocol uses the correct function to get the total BPT supply in circulation.

**References.**
- <https://solodit.xyz/issues/h-7-totalbptsupply-will-be-excessively-inflated-sherlock-notional-notional-update-git>

### SOL-Integrations-Uniswap-2

**Question.** Are there refunds after swaps?

Source: Cyfrin / Solodit · upstream path: *Integrations › Uniswap*

**Description.** In case of failed or partially filled orders, the protocol must issue refunds to the users.

**Remediation.** Implement a refund mechanism to handle failed or partially filled swaps.

### SOL-Integrations-Uniswap-10

**Question.** Is a hard-coded fee tier parameter being used?

Source: Cyfrin / Solodit · upstream path: *Integrations › Uniswap*

**Description.** In UniswapV3 liquidity can be spread across multiple fee tiers. If a function which initiates a uni v3 swap hard-codes the fee tier parameter, this can have several negative effects.

**Remediation.** Functions allowing users to perform uni v3 swaps should allow users to pass in the fee tier parameter.

**References.**
- <https://dacian.me/defi-slippage-attacks#heading-hard-coded-fee-tier-in-uniswapv3-swap>

## 7. Upgradeability & Proxies

### SC-PROXY-1

**Question.** Storage layout: does an upgrade risk a **storage collision** with the old layout?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/upgradeability.md`](../knowledge-base/vulnerabilities/upgradeability.md)

**Cited by.** [2022-07-23 Audius (704 ETH)](../knowledge-base/case-studies/2022-07-23-audius-storage-collision-governance.md)

### SC-PROXY-2

**Question.** Is the implementation contract left **uninitialized** (attacker can init & self-destruct/`delegatecall`)?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/upgradeability.md`](../knowledge-base/vulnerabilities/upgradeability.md)

### SC-PROXY-3

**Question.** `delegatecall` to untrusted targets? Function-selector clashes between proxy and impl?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/upgradeability.md`](../knowledge-base/vulnerabilities/upgradeability.md)

### SC-PROXY-4

**Question.** Are `__gap` slots reserved in upgradeable base contracts?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/upgradeability.md`](../knowledge-base/vulnerabilities/upgradeability.md)

### SC-PROXY-5

**Question.** Who can upgrade, and is that authority appropriately decentralized/timelocked?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/upgradeability.md`](../knowledge-base/vulnerabilities/upgradeability.md)

### SC-PROXY-6

**Question.** Does the proxy's own storage (admin, implementation, init flags) overlap the implementation's variables, so that `initialize` reads as never run and can be re-executed?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/upgradeability.md`](../knowledge-base/vulnerabilities/upgradeability.md) · added from: case study 2022-07-23 Audius

**Cited by.** [2022-07-23 Audius (704 ETH)](../knowledge-base/case-studies/2022-07-23-audius-storage-collision-governance.md)

### SOL-Basics-Initialization-2

**Question.** Has the contract inherited OpenZeppelin's Initializable?

Source: Cyfrin / Solodit · upstream path: *Basics › Initialization*

**Description.** If the contract is supposed to be inherited by other contracts, `onlyInitializing` modifier MUST be used instead of `initializer`.

**Remediation.** Make sure to use the correct modifier for the initializer function.

**References.**
- <https://solodit.xyz/issues/h-03-wrong-implementation-of-eip712metatransaction-code4rena-rolla-rolla-contest-git>

### SOL-Basics-Initialization-3

**Question.** Does the contract have a separate initializer function other than a constructor?

Source: Cyfrin / Solodit · upstream path: *Basics › Initialization*

**Description.** Initializer function can be front-run right after the deployment. The impact is critical if the initializer sets the access controls.

**Remediation.** Use the factory pattern to allow only the factory to call the initializer or ensure it is not front-runnable in the deploy script.

**References.**
- <https://solodit.xyz/issues/initialization-functions-can-be-front-run-trailofbits-advanced-blockchain-pdf>

**Cited by.** [2021-09-03 DAO Maker (~$4M)](../knowledge-base/case-studies/2021-09-03-dao-maker-unprotected-init.md)

### SOL-Basics-PU-1

**Question.** Is there a constructor in the proxied contract?

Source: Cyfrin / Solodit · upstream path: *Basics › Proxy/Upgradable*

**Description.** Proxied contract can't have a constructor and it's common to move constructor logic to an external initializer function, usually called initialize

**Remediation.** Use initializer functions for initialization of proxied contracts.

### SOL-Basics-PU-2

**Question.** Is the `initializer` modifier applied to the `initialization()` function?

Source: Cyfrin / Solodit · upstream path: *Basics › Proxy/Upgradable*

**Description.** Without the `initializer` modifier, there is a risk that the initialization function can be called multiple times.

**Remediation.** Always use the `initializer` modifier for initialization functions in proxied contracts and ensure they're called once during deployment.

**Cited by.** [2022-07-23 Audius (704 ETH)](../knowledge-base/case-studies/2022-07-23-audius-storage-collision-governance.md)

### SOL-Basics-PU-3

**Question.** Is the upgradable version used for initialization?

Source: Cyfrin / Solodit · upstream path: *Basics › Proxy/Upgradable*

**Description.** Upgradable contracts must use the upgradable versions of parent initializer functions. (e.g. Pausable vs PausableUpgradable)

**Remediation.** Use upgradable versions of parent initializer functions.

### SOL-Basics-PU-4

**Question.** Is the `authorizeUpgrade()` function properly secured in a UUPS setup?

Source: Cyfrin / Solodit · upstream path: *Basics › Proxy/Upgradable*

**Description.** Inadequate security on the `authorizeUpgrade()` function can allow unauthorized upgrades.

**Remediation.** Ensure proper access controls and checks are in place for the `authorizeUpgrade()` function.

### SOL-Basics-PU-5

**Question.** Is the contract initialized?

Source: Cyfrin / Solodit · upstream path: *Basics › Proxy/Upgradable*

**Description.** An uninitialized contract can be taken over by an attacker. This applies to both a proxy and its implementation contract, which may impact the proxy.

**Remediation.** To prevent the implementation contract from being used, invoke the `_disableInitializers` function in the constructor to automatically lock it when it is deployed.

**References.**
- <https://docs.openzeppelin.com/contracts/4.x/api/proxy#Initializable>

### SOL-Basics-PU-6

**Question.** Are `selfdestruct` and `delegatecall` used within the implementation contracts?

Source: Cyfrin / Solodit · upstream path: *Basics › Proxy/Upgradable*

**Description.** Using `selfdestruct` and `delegatecall` in implementation contracts can introduce vulnerabilities and unexpected behavior in a proxy setup.

**Remediation.** Avoid using `selfdestruct` and `delegatecall` in implementation contracts to ensure contract stability and security.

### SOL-Basics-PU-7

**Question.** Are values in immutable variables preserved between upgrades?

Source: Cyfrin / Solodit · upstream path: *Basics › Proxy/Upgradable*

**Description.** Immutable variables are stored in the bytecode, not in the proxy storage. So using immutable variable is not recommended in proxy setup. If used, make sure all immutables stay consistent across implementations during upgrades.

**Remediation.** Avoid using immutable variables in upgradable contracts.

### SOL-Basics-PU-8

**Question.** Has the contract inherited the correct branch of OpenZeppelin library?

Source: Cyfrin / Solodit · upstream path: *Basics › Proxy/Upgradable*

**Description.** Sometimes developers overlook and use an incorrect branch of OZ library, e.g. use Ownable instead of OwnableUpgradeable.

**Remediation.** Make sure inherit the correct branch of OZ library according to the contract's upgradeability design.

**References.**
- <https://solodit.xyz/issues/h-01-usage-of-an-incorrect-version-of-ownbale-library-can-potentially-malfunction-all-onlyowner-functions-code4rena-covalent-covalent-contest-git>

### SOL-Basics-PU-9

**Question.** Could an upgrade of the contract result in storage collision?

Source: Cyfrin / Solodit · upstream path: *Basics › Proxy/Upgradable*

**Description.** Storage collisions can occur when storage layouts between contract versions conflict, leading to data corruption and unpredictable behavior.

**Remediation.** Maintain a consistent storage layout between upgrades, and when using inheritance, set storage gaps to avoid potential collisions.

**Cited by.** [2022-07-23 Audius (704 ETH)](../knowledge-base/case-studies/2022-07-23-audius-storage-collision-governance.md)

### SOL-Basics-PU-10

**Question.** Are the order and types of storage variables consistent between upgrades?

Source: Cyfrin / Solodit · upstream path: *Basics › Proxy/Upgradable*

**Description.** Changing the order or type of storage variables between upgrades can lead to storage collisions.

**Remediation.** Maintain a consistent order and type for storage variables across contract versions to avoid storage collisions.

## 8. Signatures, Proofs & Replay

### SC-SIG-1

**Question.** Is every signed message bound to a **nonce**, and is the nonce consumed?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/signatures.md`](../knowledge-base/vulnerabilities/signatures.md)

### SC-SIG-2

**Question.** Is the signature bound to `chainId` and the contract address (EIP-712 domain)?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/signatures.md`](../knowledge-base/vulnerabilities/signatures.md)

### SC-SIG-3

**Question.** Is `ecrecover` checked against `address(0)` (malleability / invalid sig)?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/signatures.md`](../knowledge-base/vulnerabilities/signatures.md)

### SC-SIG-4

**Question.** Can a signature be replayed across chains, forks, or contract instances?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/signatures.md`](../knowledge-base/vulnerabilities/signatures.md)

**Cited by.** [2022-01-18 Multichain / Anyswap `AnyswapV4Router.a… (~$1.4M)](../knowledge-base/case-studies/2022-01-18-multichain-anyswap-phantom-permit.md)

### SC-SIG-5

**Question.** Are `v/r/s` malleability and signature-uniqueness assumptions safe?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/signatures.md`](../knowledge-base/vulnerabilities/signatures.md)

### SOL-AM-ReplayAttack-1

**Question.** Are there protections against replay attacks for failed transactions?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Replay Attack*

**Description.** Failed transactions can be susceptible to replay attacks if not properly protected.

**Remediation.** Implement nonce-based or other mechanisms to ensure that each transaction can only be executed once, preventing replay attacks.

**References.**
- <https://github.com/code-423n4/2022-03-rolla-findings/issues/45>

### SOL-AM-ReplayAttack-2

**Question.** Is there protection against replaying signatures on different chains?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Replay Attack*

**Description.** Signatures valid on one chain may be replayed on another, leading to potential security breaches.

**Remediation.** Use chain-specific parameters or domain separators to ensure signatures are only valid on the intended chain.

**References.**
- <https://github.com/sherlock-audit/2022-09-harpie-judging/blob/main/004-M/004-m.md>

### SOL-HMT-1

**Question.** Is the Merkle tree vulnerable to front-running attacks?

Source: Cyfrin / Solodit · upstream path: *Hash / Merkle Tree*

**Description.** When using a merkle tree, the new proof is calculated at a certain time and there exists a period of time between when the proof is generated and the proof is published.

**Remediation.** Ensure that front-running the merkle proof setting does not affect the protocol.

### SOL-HMT-2

**Question.** Does the claim method validate `msg.sender`?

Source: Cyfrin / Solodit · upstream path: *Hash / Merkle Tree*

**Description.** Validation of `msg.sender` is critical in the use of Merkle tree.

**Remediation.** Ensure that the `msg.sender` is actually the same address included in the leave.

### SOL-HMT-3

**Question.** What is the result when passing a zero hash to the Merkle tree functions?

Source: Cyfrin / Solodit · upstream path: *Hash / Merkle Tree*

**Description.** Passing the zero hash can lead to unintended behaviors or vulnerabilities if not properly handled.

**Remediation.** Implement checks to handle zero hash values appropriately and prevent potential misuse.

**Cited by.** [2022-08-01 Nomad token bridge (~$190M)](../knowledge-base/case-studies/2022-08-01-nomad-bridge-zero-root-accepted.md)

### SOL-HMT-4

**Question.** What occurs if the same proof is duplicated within the Merkle tree?

Source: Cyfrin / Solodit · upstream path: *Hash / Merkle Tree*

**Description.** Duplicate proofs within a Merkle tree can lead to double-spending or other vulnerabilities.

**Remediation.** Ensure the Merkle tree construction and verification process detects and prevents the use of duplicate proofs.

### SOL-HMT-5

**Question.** Are the leaves of the Merkle tree hashed with the claimable address included?

Source: Cyfrin / Solodit · upstream path: *Hash / Merkle Tree*

**Description.** Not including claimable addresses when hashing leaves can let an attacker to claim.

**Remediation.** Ensure that the Merkle tree construction includes the hashing of claimable addresses within the leaves.

### SOL-Integrations-GS-2

**Question.** Does the `execTransactionFromModule()` function increment the nonce?

Source: Cyfrin / Solodit · upstream path: *Integrations › Gnosis Safe*

**Description.** If the nonce is not incremented in `execTransactionFromModule()`, it can cause issues when relying on it for signatures.

**Remediation.** Ensure increase nonce inside the function `execTransactionFromModule()`.

### SOL-Signature-1

**Question.** Are signatures guarded against replay attacks?

Source: Cyfrin / Solodit · upstream path: *Signature*

**Description.** Lacking protection mechanisms like `nonce` and `block.chainid` can make signatures vulnerable to replay attacks. Also, EIP-712 provides a standard for creating typed and structured data to be signed, ensuring better security and user experience.

**Remediation.** Implement a `nonce` system and incorporate `block.chainid` in your signature scheme. Ensure adherence to EIP-712 for all signatures.

### SOL-Signature-2

**Question.** Are signatures protected against malleability issues?

Source: Cyfrin / Solodit · upstream path: *Signature*

**Description.** Signature malleability can be exploited by attackers to produce valid signatures without the private key. Using outdated versions of libraries can introduce known vulnerabilities.

**Remediation.** Avoid using `ecrecover()` for signature verification. Instead, utilize the OpenZeppelin's latest version of ECDSA to ensure signatures are safe from malleability issues.

### SOL-Signature-3

**Question.** Does the returned public key from the signature verification match the expected public key?

Source: Cyfrin / Solodit · upstream path: *Signature*

**Description.** Mismatched public keys can indicate an incorrect or malicious signer, potentially leading to unauthorized actions.

**Remediation.** Implement rigorous checks to ensure the public key derived from a signature matches the expected signer's public key.

### SOL-Signature-4

**Question.** Is the signature originating from the appropriate entity?

Source: Cyfrin / Solodit · upstream path: *Signature*

**Description.** If signatures aren't properly checked, malicious actors might exploit them, leading to unauthorized transactions or actions.

**Remediation.** Ensure strict verification mechanisms are in place to confirm that signatures originate from the expected entities.

### SOL-Signature-5

**Question.** If the signature has a deadline, is it still valid?

Source: Cyfrin / Solodit · upstream path: *Signature*

**Description.** Signatures with expiration dates that aren't checked can be reused maliciously after they should no longer be valid.

**Remediation.** Always check the expiration date of signatures and ensure they're not accepted past their valid period.

## 9. Denial of Service

### SC-DOS-1

**Question.** Unbounded loops over user-growable arrays (can exceed block gas limit)?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/denial-of-service.md`](../knowledge-base/vulnerabilities/denial-of-service.md)

### SC-DOS-2

**Question.** Does a single failing external call (e.g. one recipient's transfer reverting) block a whole batch / the whole protocol? (push vs. pull payments)

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/denial-of-service.md`](../knowledge-base/vulnerabilities/denial-of-service.md)

**Cited by.** [2022-04-23 Akutars / Aku Dreams NFT Dutch auction (11,539.5 ETH)](../knowledge-base/case-studies/2022-04-23-akutar-nft-refund-dos-and-locked-funds.md)

### SC-DOS-3

**Question.** Can an attacker grief by forcing gas costs, filling a queue, or locking funds?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/denial-of-service.md`](../knowledge-base/vulnerabilities/denial-of-service.md)

**Cited by.** [2022-04-23 Akutars / Aku Dreams NFT Dutch auction (11,539.5 ETH)](../knowledge-base/case-studies/2022-04-23-akutar-nft-refund-dos-and-locked-funds.md)

### SC-DOS-4

**Question.** Does the protocol handle a token that reverts on zero-value transfer?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/denial-of-service.md`](../knowledge-base/vulnerabilities/denial-of-service.md)

### SC-DOS-5

**Question.** Can a `require` in a refund / claim / settlement path be made permanently false (counter mismatch, one reverting recipient), locking every user's funds?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/denial-of-service.md`](../knowledge-base/vulnerabilities/denial-of-service.md) · added from: case study 2022-04-23 Akutar NFT

**Cited by.** [2022-04-23 Akutars / Aku Dreams NFT Dutch auction (11,539.5 ETH)](../knowledge-base/case-studies/2022-04-23-akutar-nft-refund-dos-and-locked-funds.md)

### SOL-AM-DOSA-1

**Question.** Is the withdrawal pattern followed to prevent denial of service?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Denial-Of-Service(DOS) Attack*

**Description.** To prevent denial of service attacks during withdrawals, it's critical to follow the withdrawal pattern best practices - pull based approach.

**Remediation.** Implement withdrawal pattern best practices to ensure that contract behavior remains predictable and robust against denial of service attacks.

**References.**
- <https://solodit.xyz/issues/m-06-denial-of-service-contract-owner-could-block-users-from-withdrawing-their-strike-code4rena-putty-putty-contest-git>

**Cited by.** [2022-04-23 Akutars / Aku Dreams NFT Dutch auction (11,539.5 ETH)](../knowledge-base/case-studies/2022-04-23-akutar-nft-refund-dos-and-locked-funds.md)

### SOL-AM-DOSA-2

**Question.** Is there a minimum transaction amount enforced?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Denial-Of-Service(DOS) Attack*

**Description.** Enforcing a minimum transaction amount can prevent attackers from clogging the network with zero amount or dust transactions.

**Remediation.** Disallow transactions below a certain threshold to maintain efficiency and prevent denial of service through dust spamming.

**References.**
- <https://solodit.xyz/issues/h-02-denial-of-service-code4rena-hubble-hubble-contest-git>
- <https://solodit.cyfrin.io/issues/m-16-users-can-be-griefed-due-to-lack-of-minimum-size-within-the-loan-and-offer-sherlock-debita-finance-v3-git>

### SOL-AM-DOSA-3

**Question.** How does the protocol handle tokens with blacklisting functionality?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Denial-Of-Service(DOS) Attack*

**Description.** Tokens with blacklisting capabilities, such as USDC, can pose unique risks and challenges to protocols.

**Remediation.** Account for the possibility of blacklisting within token protocols to ensure continued functionality even if certain addresses are blacklisted.

**References.**
- <https://solodit.cyfrin.io/issues/m-4-blacklisted-creditor-can-block-all-repayment-besides-emergency-closure-sherlock-real-wagmi-2-git>

### SOL-AM-DOSA-4

**Question.** Can forcing the protocol to process a queue lead to DOS?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Denial-Of-Service(DOS) Attack*

**Description.** Forcing protocols to process queues, like a queue of dust withdrawals, can be exploited to cause a denial of service.

**Remediation.** Design queue processing in a manner that is resilient to spam and cannot be exploited to cause denial of service.

**References.**
- <https://solodit.cyfrin.io/?b=false&f=&fc=gte&ff=&fn=1&i=HIGH%2CMEDIUM&p=1&pc=&r=all&s=gas+griefing&t=>
- <https://solodit.cyfrin.io/issues/denial-of-slashing-ottersec-none-ethos-evm-pdf>

### SOL-AM-DOSA-5

**Question.** What happens with low decimal tokens that might cause DOS?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Denial-Of-Service(DOS) Attack*

**Description.** Tokens with low decimals can present issues where the transaction process fails due to rounding to zero amounts.

**Remediation.** Implement logic to handle low decimal tokens in a way that prevents the transaction process from breaking due to insufficient token amounts.

**References.**
- <https://solodit.xyz/issues/potential-funds-locked-due-low-token-decimal-and-long-stream-duration-spearbit-locke-pdf>

### SOL-AM-DOSA-6

**Question.** Does the protocol handle external contract interactions safely?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Denial-Of-Service(DOS) Attack*

**Description.** Protocols must handle interactions with external contracts in a way that does not compromise their functionality if external dependencies fail.

**Remediation.** Ensure robust handling of external contract interactions to maintain protocol integrity regardless of external contract performance.

**References.**
- <https://solodit.xyz/issues/m-09-unhandled-chainlink-revert-would-lock-all-price-oracle-access-code4rena-juicebox-juicebox-v2-contest-git>

### SOL-AM-GA-1

**Question.** Is there an external function that relies on states that can be changed by others?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Griefing Attack*

**Description.** Malicious actors can prevent regular user transactions by making a slight change to the on-chain states.

**Remediation.** Ensure normal user actions especially important actions like withdrawal and repayment are not disturbed by other actors.

**References.**
- <https://solodit.xyz/issues/m-10-griefing-attack-to-block-withdraws-code4rena-mochi-mochi-contest-git>
- <https://solodit.cyfrin.io/issues/griefing-attack-in-group-ip-management-via-license-token-minting-halborn-story-proof-of-creativity-protocol-markdown>
- <https://solodit.cyfrin.io/issues/h-6-loss-of-rewards-due-to-continuous-griefing-attacks-on-l2-environment-sherlock-notional-leveraged-vaults-pendle-pt-and-vault-incentives-git>

### SOL-AM-GA-2

**Question.** Can the contract operations be manipulated with precise gas limit specifications?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Griefing Attack*

**Description.** Attackers can supply carefully calculated gas amounts to force specific execution paths in the contract, manipulating its behavior in unexpected ways.

**Remediation.** Implement explicit gas checks before critical operations.

**References.**
- <https://solodit.cyfrin.io/issues/19573>
- <https://solodit.cyfrin.io/issues/2786>
- <https://scsfg.io/hackers/griefing/>

### SOL-Basics-AL-9

**Question.** Is there possibility of iteration of a huge array?

Source: Cyfrin / Solodit · upstream path: *Basics › Array / Loop*

**Description.** Due to the block gas limit, there is a clear limitation in the amount of operation that can be handled in a transaction.

**Remediation.** Ensure the number of iterations is properly bounded.

**References.**
- <https://solodit.cyfrin.io/issues/m-5-users-buying-too-many-tickets-will-dos-them-and-the-protocol-if-they-are-the-winner-due-to-oog-sherlock-winnables-raffles-git>

### SOL-Basics-AL-10

**Question.** Is there a potential for a Denial-of-Service (DoS) attack in the loop?

Source: Cyfrin / Solodit · upstream path: *Basics › Array / Loop*

**Description.** Loops that contain external calls or are dependent on user-controlled input can be exploited to halt the contract's functions. (e.g. sending ETH to multiple users)

**Remediation.** Ensure a failure of a single iteration does not revert the whole operation.

### SOL-Basics-AL-12

**Question.** Is there a loop to handle batch fund transfer?

Source: Cyfrin / Solodit · upstream path: *Basics › Array / Loop*

**Description.** If there is a mechanism to transfer funds out based on some kind of shares, it is likely that there is a problem of 'dust' funds not handled correctly.

**Remediation.** Make sure the last transfer handles all residual.

**Cited by.** [2022-04-23 Akutars / Aku Dreams NFT Dutch auction (11,539.5 ETH)](../knowledge-base/case-studies/2022-04-23-akutar-nft-refund-dos-and-locked-funds.md)

### SOL-Basics-Payment-1

**Question.** Is it possible for the receiver to revert?

Source: Cyfrin / Solodit · upstream path: *Basics › Payment*

**Description.** There are cases where a receiver contract can deny the transaction. For example, a malicious receiver can have a fallback to revert. If a caller tried to send funds using `transfer` or `send`, the whole transaction will revert. (Meanwhile, `call()` does not revert but returns a boolean)

**Remediation.** Make sure that the receiver can not deny the payment or add a backup handler with a try-catch.

**Cited by.** [2022-04-23 Akutars / Aku Dreams NFT Dutch auction (11,539.5 ETH)](../knowledge-base/case-studies/2022-04-23-akutar-nft-refund-dos-and-locked-funds.md)

### SOL-Basics-Payment-5

**Question.** How is the withdrawal handled?

Source: Cyfrin / Solodit · upstream path: *Basics › Payment*

**Description.** The best practice in withdrawal process is to implement pull-based approach. Track the accounting and let users pull the payments instead of sending funds proactively.

**Remediation.** Implement pull-based approach in withdrawals.

### SOL-Basics-Payment-7

**Question.** Is it possible for native ETH to be locked in the contract?

Source: Cyfrin / Solodit · upstream path: *Basics › Payment*

**Description.** If a `payable` function does not transfer all ETH passed in `msg.value` and the contract does not have a withdraw method, ETH will be locked in the contract

**Remediation.** Make sure either no ETH remains in the contract at the end of `payable` functions or make sure there is a `withdraw` function.

**References.**
- <https://solodit.xyz/issues/m-09-bathbuddy-locks-up-ether-it-receives-code4rena-rubicon-rubicon-contest-git>
- <https://solodit.xyz/issues/m-22-eth-sent-when-calling-executeassmartwallet-function-can-be-lost-code4rena-stakehouse-protocol-lsd-network-stakehouse-contest-git>

### SOL-Defi-LSD-7

**Question.** Does the protocol iterate over the entire set of operators or validators?

Source: Cyfrin / Solodit · upstream path: *Defi › Liquid Staking Derivatives*

**Description.** LSD protocols may need to iterate over the entire set of operators or validators which can become exorbitantly expensive or lead to out of gas if the operator or validator set becomes large. In permissionless systems where anyone can create operators or validators this creates a denial of service attack vector.

**Remediation.** Refactor to avoid needing to iterate over the entire operator/validator set. Alternatively only use a small and trusted set of operators/validators.

## 10. Token Integration Quirks

### SC-TOKEN-1

**Question.** **Fee-on-transfer**: does the code assume received == sent amount?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/token-integration.md`](../knowledge-base/vulnerabilities/token-integration.md)

### SC-TOKEN-2

**Question.** **Rebasing tokens**: does cached balance drift from actual balance?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/token-integration.md`](../knowledge-base/vulnerabilities/token-integration.md)

### SC-TOKEN-3

**Question.** **Missing return value** ERC-20s (USDT): is `SafeERC20`/`safeTransfer` used?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/token-integration.md`](../knowledge-base/vulnerabilities/token-integration.md)

### SC-TOKEN-4

**Question.** **ERC-777 / hook tokens** (ERC-677 `transferAndCall`, ERC-1363) enabling reentrancy on transfer?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/token-integration.md`](../knowledge-base/vulnerabilities/token-integration.md)

**Cited by.** [2022-03-15 Hundred Finance (~$6.2M)](../knowledge-base/case-studies/2022-03-15-hundred-finance-erc677-hook-reentrancy.md)

### SC-TOKEN-5

**Question.** **Non-standard decimals** (e.g. USDC=6, WBTC=8) handled?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/token-integration.md`](../knowledge-base/vulnerabilities/token-integration.md)

### SC-TOKEN-6

**Question.** **Approval race** / double-spend on non-zero→non-zero approve?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/token-integration.md`](../knowledge-base/vulnerabilities/token-integration.md)

### SC-TOKEN-7

**Question.** **Phantom functions**: does the code call `permit` or other optional functions on tokens that may not implement them, where a `fallback` (WETH) or a codeless address makes the call "succeed"?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/token-integration.md`](../knowledge-base/vulnerabilities/token-integration.md) · added from: case study 2022-01-18 Multichain

**Cited by.** [2022-01-18 Multichain / Anyswap `AnyswapV4Router.a… (~$1.4M)](../knowledge-base/case-studies/2022-01-18-multichain-anyswap-phantom-permit.md)

### SOL-Defi-AS-8

**Question.** Does the AMM properly handle tokens of varying decimal configurations and token types?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** If the AMM doesn't support tokens with varying decimals or types, it might lead to incorrect calculations and potential losses.

**Remediation.** Ensure compatibility with tokens of varying decimal places and validate token types before processing them.

### SOL-Defi-AS-9

**Question.** Does the AMM support the fee-on-transfer tokens?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** Fee-on-transfer tokens can cause problems because the sending amount and the received amount do not match.

**Remediation.** Ensure the fee-on-transfer tokens are handled correctly if they are supposed to be supported.

### SOL-Defi-AS-10

**Question.** Does the AMM support the rebasing tokens?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** Rebasing tokens can change the actual balance.

**Remediation.** Ensure the rebasing tokens are handled correctly if they are supposed to be supported.

### SOL-Defi-General-1

**Question.** Can the protocol handle ERC20 tokens with decimals other than 18?

Source: Cyfrin / Solodit · upstream path: *Defi › General*

**Description.** Not all ERC20 tokens use 18 decimals. Overlooking this can lead to computation errors.

**Remediation.** Always check and adjust for the decimal count of the ERC20 tokens being handled.

### SOL-Defi-General-6

**Question.** Does the protocol revert on maximum approval to prevent over-allowance?

Source: Cyfrin / Solodit · upstream path: *Defi › General*

**Description.** Setting high allowances can make funds vulnerable to abuse; protocols sometimes set max to prevent this risk.

**Remediation.** Consider implementing a revert on approval functions when an unnecessarily high allowance is set.

**References.**
- <https://solodit.xyz/issues/m-3-universalapprovemax-will-not-work-for-some-tokens-that-dont-support-approve-typeuint256max-amount-sherlock-dodo-dodo-git>

### SOL-Defi-General-9

**Question.** Does the protocol aim to support ALL kinds of ERC20 tokens?

Source: Cyfrin / Solodit · upstream path: *Defi › General*

**Description.** Not all ERC20 tokens are compliant to the ERC20 standard and there are several weird ERC20 tokens (e.g. Fee-On-Transfer tokens, rebasing tokens, tokens with blacklisting).

**Remediation.** Clarify what kind of tokens are supported and whitelist the ERC20 tokens that the protocol would accept.

**References.**
- <https://github.com/d-xo/weird-erc20>

### SOL-Heuristics-14

**Question.** Is ETH/WETH handling implemented correctly?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** Contracts might have special logic for ETH, like wrapping to WETH. Assuming exclusivity between handling ETH and WETH without checks can introduce errors.

**Remediation.** Clearly differentiate the logic between ETH and WETH handling, ensuring no overlap or mutual exclusivity assumptions without validation.

### SOL-Integrations-AC-1

**Question.** Does the protocol use cETH token?

Source: Cyfrin / Solodit · upstream path: *Integrations › AAVE / Compound*

**Description.** The absence of the `underlying()` function in the cETH token contract can cause integration issues.

**Remediation.** Double check the protocol works as expected when integrating cETH token.

### SOL-Integrations-LSD-cbETH-1

**Question.** How is the control over the `cbETH`/`ETH` rate determined? Are there specific addresses with this capability due to the `onlyOracle` modifier?

Source: Cyfrin / Solodit · upstream path: *Integrations › LSD › cbETH*

**Description.** The rate between `cbETH` and `ETH` being controllable by a few addresses can introduce centralization risks and potential manipulations.

**Remediation.** Any address with `onlyOracle` permissions should be scrutinized and their actions should be transparent to the community.

### SOL-Integrations-LSD-cbETH-2

**Question.** How does the system handle potential decreases in the `cbETH`/`ETH` rate?

Source: Cyfrin / Solodit · upstream path: *Integrations › LSD › cbETH*

**Description.** The rate of `cbETH` to `ETH` can decrease, which can impact users who hold or interact with `cbETH`.

**Remediation.** Implement mechanisms to inform users about the current `cbETH`/`ETH` rate. Consider providing alerts or notifications for significant rate changes. Ensure there's a mechanism to handle or rectify situations where the rate decreases dramatically.

### SOL-Integrations-LSD-rETH-1

**Question.** Does the application account for potential penalties or slashes?

Source: Cyfrin / Solodit · upstream path: *Integrations › LSD › rETH*

**Description.** Validators on the Ethereum 2.0 Beacon Chain can be penalized or slashed for misbehavior. This can affect the value of `rETH`.

**Remediation.** Implement mechanisms to account for potential penalties or slashes that can impact the value of `rETH`.

### SOL-Integrations-LSD-rETH-2

**Question.** How does the system manage rewards accrued from staking?

Source: Cyfrin / Solodit · upstream path: *Integrations › LSD › rETH*

**Description.** Staking on the Ethereum 2.0 Beacon Chain accrues rewards. The system should account for these rewards when dealing with `rETH`.

**Remediation.** Ensure proper distribution or accumulation of rewards in the system's `rETH` management.

### SOL-Integrations-LSD-rETH-3

**Question.** Does the application handle potential reverts in the `burn()` function when there's insufficient ether in the `RocketDepositPool`?

Source: Cyfrin / Solodit · upstream path: *Integrations › LSD › rETH*

**Description.** If there's not enough ether in the `RocketDepositPool` contract, the `burn()` function can fail. It's important for the system to handle these failures gracefully.

**Remediation.** Ensure there's a mechanism to either prevent calls to `burn()` when there's insufficient ether or handle the revert gracefully, informing the user appropriately.

### SOL-Integrations-LSD-rETH-4

**Question.** What measures are in place to counteract potential consensus attacks on RPL nodes?

Source: Cyfrin / Solodit · upstream path: *Integrations › LSD › rETH*

**Description.** There's a risk of consensus attacks on RPL nodes where malicious nodes may submit incorrect exchange rate data, leading to discrepancies.

**Remediation.** Implement a system in place to quickly rectify incorrect data submissions by nodes.

### SOL-Integrations-LSD-rETH-5

**Question.** How does the system handle the conversion between `ETH` and `rETH`?

Source: Cyfrin / Solodit · upstream path: *Integrations › LSD › rETH*

**Description.** The conversion rate between `ETH` and `rETH` might change over time based on the rewards accrued from staking. Ensure this dynamic is properly captured.

**Remediation.** Integrate accurate conversion mechanisms that consider the ever-changing staking rewards when converting between `ETH` and `rETH`.

### SOL-Integrations-LSD-sfrxETH-1

**Question.** How does the system handle potential detachment of `sfrxETH` from `frxETH` during reward transfers?

Source: Cyfrin / Solodit · upstream path: *Integrations › LSD › sfrxETH*

**Description.** If `sfrxETH` detaches from `frxETH` during reward transfers, it could cause discrepancies in expected and actual values, especially if these transfers are controlled by a centralized entity like the Frax team's multi-sig contract.

**Remediation.** Ensure there's transparency around the actions of the Frax team's multi-sig contract. Consider mechanisms to alert users or stakeholders about discrepancies between `sfrxETH` and `frxETH`.

### SOL-Integrations-LSD-sfrxETH-2

**Question.** Is the stability of the `sfrxETH`/`ETH` rate guaranteed or can it decrease in the future?

Source: Cyfrin / Solodit · upstream path: *Integrations › LSD › sfrxETH*

**Description.** While the `sfrxETH`/`ETH` rate might be stable now, changes in the future could impact users and stakeholders, especially if they're not forewarned.

**Remediation.** Provide clear documentation and alerts about potential changes to the `sfrxETH`/`ETH` rate. Ensure users are informed well in advance about any planned changes that could affect the rate.

### SOL-Integrations-LSD-stETH-1

**Question.** Is the application aware that `stETH` is a rebasing token?

Source: Cyfrin / Solodit · upstream path: *Integrations › LSD › stETH*

**Description.** `stETH` rebases, which can introduce complexities when integrated with DeFi platforms. Using `wstETH` can simplify integrations as it is non-rebasing.

**Remediation.** Consider using `wstETH` for simpler DeFi integrations and to avoid complexities associated with rebasing tokens.

### SOL-Integrations-LSD-stETH-2

**Question.** Are you aware of the overhead when withdrawing `stETH`/`wstETH`?

Source: Cyfrin / Solodit · upstream path: *Integrations › LSD › stETH*

**Description.** Withdrawing `stETH` or `wstETH` can introduce overheads, due to various problems like queue time, receipt of an NFT, and withdrawal amount limits.

**Remediation.** Ensure account for these overheads and constraints in the protocol logic.

### SOL-Integrations-LSD-stETH-3

**Question.** Does the application handle conversions between `stETH` and `wstETH` correctly?

Source: Cyfrin / Solodit · upstream path: *Integrations › LSD › stETH*

**Description.** Converting between `stETH` and `wstETH` can be tricky due to the rebasing nature of `stETH`. It's crucial to handle these conversions correctly to avoid potential issues.

**Remediation.** Ensure that the rebasing characteristics of `stETH` are properly managed when converting between `stETH` and `wstETH`.

### SOL-Token-FE-1

**Question.** Are safe transfer functions used throughout the contract?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Not all ERC20 tokens are compliant to the EIP20 standard. Some do not return boolean flag, some do not revert on failure.

**Remediation.** Use OpenZeppelin's SafeERC20 where the safeTransfer and safeTransferFrom functions handle the return value check as well as non-standard-compliant tokens.

**Cited by.** [2022-01-27 Qubit Finance QBridge (~$80M)](../knowledge-base/case-studies/2022-01-27-qubit-finance-codeless-address-call.md)

### SOL-Token-FE-2

**Question.** Is there potential for a race condition for approvals?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Race condition for approvals can cause an unexpected loss of funds to the signer.

**Remediation.** Use OpenZeppelin's safeIncreaseAllowance and safeDecreaseAllowance functions.

**References.**
- <https://solodit.xyz/issues/m01-approval-process-can-be-front-run-openzeppelin-notional-governance-contracts-v2-audit-markdown>

### SOL-Token-FE-3

**Question.** Could a difference in decimals between ERC20 tokens cause issues?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Different decimals in ERC20 tokens can cause incorrect calculations or interpretations.

**Remediation.** Always check and handle the decimals of ERC20 tokens to prevent potential issues.

### SOL-Token-FE-4

**Question.** Does the token implement any form of address whitelisting, blacklisting, or checks?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Tokens that have address checks can lead to various problems.

**Remediation.** Ensure the token's own blacklisting mechanism does not affect the protocol's functionality.

### SOL-Token-FE-5

**Question.** Could the use of multiple addresses for a single token lead to complications?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Some tokens have multiple addresses and this can introduce vulnerabilities.

**Remediation.** Do not rely on the token address in the accounting.

### SOL-Token-FE-6

**Question.** Does the token charge fee on transfer?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Some tokens charge fee on transfer and the receiver gets less amount than specified.

**Remediation.** If the protocol intends to support this kind of token, ensure the accounting logic is correct.

### SOL-Token-FE-7

**Question.** Can the token be ERC777?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** ERC777 tokens have hooks that execute code before and after transfers, which might lead to reentrancy.

**Remediation.** Be cautious when integrating with ERC777 and be aware of the hook implications.

**Cited by.** [2022-03-15 Hundred Finance (~$6.2M)](../knowledge-base/case-studies/2022-03-15-hundred-finance-erc677-hook-reentrancy.md)

### SOL-Token-FE-8

**Question.** Does the protocol use Solmate's `ERC20.safeTransferLib`?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Solmate `ERC20.safeTransferLib` do not check the contract existence and this opens up a possibility for a honeypot attack.

**Remediation.** Use OpenZeppelin's SafeERC20.

**References.**
- <https://solodit.xyz/issues/m-02-solmates-erc20-does-not-check-for-token-contracts-existence-which-opens-up-possibility-for-a-honeypot-attack-code4rena-size-size-contest-git>

### SOL-Token-FE-10

**Question.** What happens on zero amount transfer?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Some tokens revert on transfer of zero amount and can cause issues in certain integrations and operations.

**Remediation.** Transfer only when the amount is positive.

### SOL-Token-FE-11

**Question.** Is the token an ERC2612 implementation?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Missing `DOMAIN_SEPARATOR()` can lead to vulnerabilities in the ERC2612 permit functionality.

**Remediation.** Ensure complete and correct implementation of ERC2612, including the `DOMAIN_SEPARATOR()` function.

**Cited by.** [2022-01-18 Multichain / Anyswap `AnyswapV4Router.a… (~$1.4M)](../knowledge-base/case-studies/2022-01-18-multichain-anyswap-phantom-permit.md)

### SOL-Token-FE-12

**Question.** Can the token be sent to any address?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Certain addresses might be blocked or restricted to receive tokens (e.g. LUSD).

**Remediation.** Ensure the receiver blacklisting does not affect the protocol's functionality.

### SOL-Token-FE-13

**Question.** Is there a direct approval to a non-zero value?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Some ERC20 tokens do not work when changing the allowance from an existing non-zero allowance value. For example Tether (USDT)'s approve() function will revert if the current approval is not zero, to protect against front-running changes of approvals.

**Remediation.** Set the allowance to zero before increasing the allowance and use safeApprove/safeIncreaseAllowance.

**References.**
- <https://solodit.xyz/issues/m-17-did-not-approve-to-zero-first-sherlock-notional-notional-git>

### SOL-Token-FE-14

**Question.** Is there a max approval used?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Some tokens don't support approve `type(uint256).max` amount and revert.

**Remediation.** Avoid approval of `type(uint256).max`.

**References.**
- <https://solodit.xyz/issues/m-3-universalapprovemax-will-not-work-for-some-tokens-that-dont-support-approve-typeuint256max-amount-sherlock-dodo-dodo-git>

### SOL-Token-FE-15

**Question.** Can the token be paused?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Some ERC20 tokens can be paused by the contract owner.

**Remediation.** Ensure the protocol is not affected when the token is paused.

### SOL-Token-FE-16

**Question.** Is the decrease allowance feature of transferFrom() handled correctly when the sender is the caller?

Source: Cyfrin / Solodit · upstream path: *Token › Fungible : ERC20*

**Description.** Allowance should not be decreased in a transferFrom() call if the sender is the same as the caller, to prevent incorrect balance and allowance tracking.

**Remediation.** Ensure that the smart contract logic maintains correct allowance levels when transferFrom() involves the token owner themselves.

**References.**
- <https://solodit.xyz/issues/m-2-transferfrom-uses-allowance-even-if-spender-from-sherlock-surge-surge-git>

### SOL-Token-NfE1-1

**Question.** How are the minting and transfer implemented?

Source: Cyfrin / Solodit · upstream path: *Token › Non-fungible : ERC721/1155*

**Description.** According to the ERC721 standard, a wallet/broker/auction application MUST implement the wallet interface if it will accept safe transfers. Use safe version of mint and transfer functions to prevent NFT being lost. (the similar applies to ERC1155)

**Remediation.** Use OpenZeppelin's safe mint/transfer functions for ERC721/1155.

### SOL-Token-NfE1-4

**Question.** Is it possible to steal NFT abusing his approval?

Source: Cyfrin / Solodit · upstream path: *Token › Non-fungible : ERC721/1155*

**Description.** Most of the time the `from` parameter of `transferFrom()` should be `msg.sender`. Otherwise an attacker can take advantage of other user's approvals and steal.

**Remediation.** Ensure that the contract verifies the `msg.sender` is actually the owner.

### SOL-Token-NfE1-5

**Question.** Does the ERC721/1155 contract correctly implement supportsInterface?

Source: Cyfrin / Solodit · upstream path: *Token › Non-fungible : ERC721/1155*

**Description.** Contracts must properly implement the supportsInterface function to ensure they comply with ERC721/1155 standards and interoperate with other contracts correctly.

**Remediation.** Implement the supportsInterface function to return true for ERC721 and ERC1155 token types, ensuring accurate reporting of supported features.

**References.**
- <https://solodit.xyz/issues/m-04-the-ferc1155sol-dont-respect-the-eip2981-code4rena-fractional-fractional-v2-contest-git>

### SOL-Token-NfE1-6

**Question.** Can the contract support both ERC721 and ERC1155 standards?

Source: Cyfrin / Solodit · upstream path: *Token › Non-fungible : ERC721/1155*

**Description.** To facilitate broader compatibility and usage in various applications, contracts may need to support both ERC721 and ERC1155 token standards.

**Remediation.** Use the supportsInterface method to check for and support interfaces of both ERC1155 and ERC721 within the same contract.

**References.**
- <https://solodit.xyz/issues/h-06-some-real-world-nft-tokens-may-support-both-erc721-and-erc1155-standards-which-may-break-infinityexchange_transfernfts-code4rena-infinity-nft-marketplace-infinity-nft-marketplace-contest-git>

### SOL-Token-NfE1-7

**Question.** What happens to the airdrops that are engaged to specific NFT?

Source: Cyfrin / Solodit · upstream path: *Token › Non-fungible : ERC721/1155*

**Description.** For many NFT collections, a kind of privilege is provided in various ways, e.g. airdrop. The NFT owner must be able to claim the benefits while they lock in protocols.

**Remediation.** Ensure the NFT holders can claim all benefits.

**References.**
- <https://solodit.xyz/issues/m-04-its-possible-to-swap-nft-token-ids-without-fee-and-also-attacker-can-wrap-unwrap-all-the-nft-token-balance-of-the-pair-contract-and-steal-their-air-drops-for-those-token-ids-code4rena-caviar-caviar-contest-git>

### SOL-Token-NfE1-8

**Question.** How is the approval/transfer handled for CryptoPunks collection?

Source: Cyfrin / Solodit · upstream path: *Token › Non-fungible : ERC721/1155*

**Description.** CryptoPunks collections that do not support the `transferFrom()` function can present risks. The `offerPunkForSaleToAddress()` function in particular can be susceptible to front-running attacks, which can compromise the ownership and security of the token.

**Remediation.** Ensure validation is done properly to prevent malicious actors claiming the ownership.

**References.**
- <https://solodit.xyz/issues/h-3-cryptopunks-nfts-may-be-stolen-via-deposit-frontrunning-sherlock-ajna-ajna-git>
- <https://solodit.xyz/issues/h-02-anyone-can-steal-cryptopunk-during-the-deposit-flow-to-wpunkgateway-code4rena-paraspace-paraspace-contest-git>

## 11. Front-running / MEV

### SC-MEV-1

**Question.** Can a pending tx be sandwiched for profit at the user's expense?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/front-running-mev.md`](../knowledge-base/vulnerabilities/front-running-mev.md)

**Cited by.** [2023-05-29 Jimbo's Protocol (~4,090 ETH)](../knowledge-base/case-studies/2023-05-29-jimbos-protocol-unprotected-rebalance.md)

### SC-MEV-2

**Question.** Is there a commit-reveal or slippage guard where ordering matters?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/front-running-mev.md`](../knowledge-base/vulnerabilities/front-running-mev.md)

### SC-MEV-3

**Question.** Can an attacker front-run initialization, a first deposit, or a claim?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/front-running-mev.md`](../knowledge-base/vulnerabilities/front-running-mev.md)

### SC-MEV-4

**Question.** Are `minAmountOut` and `deadline` enforced on every swap path?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/front-running-mev.md`](../knowledge-base/vulnerabilities/front-running-mev.md)

**Cited by.** [2023-05-29 Jimbo's Protocol (~4,090 ETH)](../knowledge-base/case-studies/2023-05-29-jimbos-protocol-unprotected-rebalance.md)

### SC-MEV-5

**Question.** Do protocol-owned or automated operations (rebalances, fee conversions, liquidity shifts, harvests) execute swaps without slippage or price-band bounds?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/front-running-mev.md`](../knowledge-base/vulnerabilities/front-running-mev.md) · added from: case study 2023-05-29 Jimbo's Protocol

**Cited by.** [2023-05-29 Jimbo's Protocol (~4,090 ETH)](../knowledge-base/case-studies/2023-05-29-jimbos-protocol-unprotected-rebalance.md)

### SOL-AM-FrA-1

**Question.** Are "get-or-create" patterns protected against front-running attacks?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Front-running Attack*

**Description.** Functions combining resource creation and interaction (like getOrCreateAndUse) are vulnerable to front-running attacks where attackers can create the resource with different parameters before the victim, potentially manipulating prices or conditions.

**Remediation.** Separate creation and interaction into distinct transactions or implement robust protections (parameter validation, relative references instead of absolute values) to ensure safe operation regardless of creation timing.

**References.**
- <https://solodit.cyfrin.io/issues/h-03-fillorder-executor-can-be-front-run-by-the-order-creator-by-changing-orders-limitprice_e36-the-executors-assets-can-be-stolen-code4rena-init-capital-init-capital-git>
- <https://solodit.cyfrin.io/issues/m-01-routergetorcreatepoolandaddliquidity-can-be-frontrunned-which-leads-to-price-manipulation-code4rena-maverick-maverick-git>

### SOL-AM-FrA-2

**Question.** Are two-transaction actions designed to be safe from frontrunning?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Front-running Attack*

**Description.** Actions that require two separate transactions may be at risk of frontrunning, where an attacker can intervene between the two calls.

**Remediation.** Ensure critical actions that are split across multiple transactions cannot be interfered with by attackers. This can involve checks or locks between the transactions.

**References.**
- <https://github.com/sherlock-audit/2022-11-isomorph-judging/issues/47>

### SOL-AM-FrA-3

**Question.** Can users maliciously cause others' transactions to revert by preempting with dust?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Front-running Attack*

**Description.** Attackers may cause legitimate transactions to fail by front-running with transactions of negligible amounts.

**Remediation.** Implement checks to prevent transactions with non-material amounts from affecting the contract's state or execution flow.

**References.**
- <https://solodit.xyz/issues/m-12-attacker-can-grift-syndicate-staking-by-staking-a-small-amount-code4rena-stakehouse-protocol-lsd-network-stakehouse-contest-git>

### SOL-AM-FrA-4

**Question.** Is the protocol using a properly user-bound commit-reveal scheme?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Front-running Attack*

**Description.** Sensitive on-chain actions can be exposed in the mempool, enabling frontrunning and information exploitation. Effective commit-reveal schemes must bind commitments to specific users and transactions.

**Remediation.** Implement a two-phase process where users first commit a hash containing their address and all transaction parameters, then reveal actual actions after the commitment phase ends, preventing frontrunning and information leakage.

**References.**
- <https://solodit.cyfrin.io/issues/h01-votes-can-be-duplicated-openzeppelin-uma-audit-phase-1-markdown>
- <https://solodit.cyfrin.io/issues/ethregistrarcontrollerregister-is-vulnerable-to-front-running-fixed-consensys-ens-permanent-registrar-markdown>

### SOL-AM-MA-1

**Question.** Is block.timestamp used for time-sensitive operations?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Miner Attack*

**Description.** Miners can manipulate block.timestamp by several seconds, potentially affecting time-dependent contract logic.

**Remediation.** Use block.number instead of timestamps for critical timing operations or ensure manipulation tolerance is acceptable.

Tags: Miner Attack

### SOL-AM-MA-3

**Question.** Is contract logic sensitive to transaction ordering?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Miner Attack*

**Description.** Miners control transaction ordering and can exploit this for front-running, back-running, or sandwich attacks.

**Remediation.** Implement protection by allowing users to specify acceptable results that revert transactions when breached.

**References.**
- <https://solodit.cyfrin.io/issues/20754>

### SOL-AM-SandwichAttack-1

**Question.** Does the protocol have an explicit slippage protection on user interactions?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Sandwich Attack*

**Description.** An attacker can monitor the mempool and puts two transactions before and after the user's transaction. For example, when an attacker spots a large trade, executes their own trade first to manipulate the price, and then profits by closing their position after the user's trade is executed.

**Remediation.** Allow users to specify the minimum output amount and revert the transaction if it is not satisfied.

**References.**
- <https://solodit.xyz/issues/h-12-sandwich-attack-to-accruepremiumandexpireprotections-sherlock-carapace-carapace-git>
- <https://solodit.xyz/issues/h-1-adversary-can-sandwich-oracle-updates-to-exploit-vault-sherlock-olympus-olympus-update-git>

**Cited by.** [2023-05-29 Jimbo's Protocol (~4,090 ETH)](../knowledge-base/case-studies/2023-05-29-jimbos-protocol-unprotected-rebalance.md)

### SOL-Basics-BR-1

**Question.** Does the protocol implement a factory pattern using the CREATE opcode?

Source: Cyfrin / Solodit · upstream path: *Basics › Block Reorganization*

**Description.** Contracts created with the CREATE opcode will be eliminated if a block reorg happens.

**Remediation.** Use CREATE2 instead of CREATE.

**References.**
- <https://solodit.xyz/issues/m-08-factorycreate-is-vulnerable-to-reorg-attacks-code4rena-abracadabra-money-abracadabra-money-git>
- <https://solodit.xyz/issues/m-02-reorg-attack-on-users-vault-deployment-and-deposit-may-lead-to-theft-of-funds-code4rena-amphora-protocol-amphora-protocol-git>
- <https://solodit.xyz/issues/m-4-loss-of-bond-amounts-on-re-org-attacks-sherlock-optimism-fault-proofs-git>
- <https://solodit.xyz/issues/m-01-questfactory-is-suspicious-of-the-reorg-attack-code4rena-rabbithole-rabbithole-quest-protocol-contest-git>
- <https://solodit.xyz/issues/m-14-re-org-attack-in-factory-code4rena-frankencoin-frankencoin-git>

### SOL-Basics-Function-3

**Question.** Can the function be front-run?

Source: Cyfrin / Solodit · upstream path: *Basics › Function*

**Description.** Front-running can allow attackers to prioritize their transactions over others.

**Remediation.** Make sure there is no unexpected risk even if attackers front-run.

**References.**
- <https://solodit.xyz/issues/m-08-borrower-can-cause-a-dos-by-frontrunning-a-liquidation-and-repaying-as-low-as-1-wei-of-the-current-debt-code4rena-venus-protocol-venus-protocol-isolated-pools-git>
- <https://solodit.xyz/issues/m-01-new-proposals-can-be-dosd-by-frontrunning-zachobront-none-optimismgovernormd-markdown_>
- <https://solodit.xyz/issues/h-01-challenges-can-be-frontrun-with-de-leveraging-to-cause-lossses-for-challengers-code4rena-frankencoin-frankencoin-git>

### SOL-Defi-AS-1

**Question.** Is hardcoded slippage used?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** Using hardcoded slippage can lead to poor trades and freezing user funds during times of high volatility.

**Remediation.** Allow users to specify the slippage parameter in the actual asset amount which was calculated off-chain.

**References.**
- <https://dacian.me/defi-slippage-attacks#heading-on-chain-slippage-calculation-can-be-manipulated>

### SOL-Defi-AS-2

**Question.** Is there a deadline protection?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** Without deadline protection, user transactions are vulnerable to sandwich attacks.

**Remediation.** Allow a user specify the deadline of the swap.

**References.**
- <https://defihacklabs.substack.com/p/solidity-security-lesson-6-defi-slippage?utm_source=profile&utm_medium=reader2>

### SOL-Defi-AS-7

**Question.** Is there a mechanism in place to protect against excessive slippage?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** Without slippage protection, traders might experience unexpected losses due to large price deviations during a trade.

**Remediation.** Incorporate a slippage parameter that users can set to limit their maximum acceptable slippage.

### SOL-Defi-AS-11

**Question.** Does the protocol calculate `minAmountOut` before a token swap?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** Protocols integrating AMMs should determine the `minAmountOut` prior to swaps to avoid unfavorable rates. The source of the rates and potential for manipulation should also be considered.

**Remediation.** Ensure that the protocol calculates `minAmountOut` before executing swaps. If external oracles are used, validate their trustworthiness and consider potential vulnerabilities like sandwich attacks.

**References.**
- <https://blog.chain.link/guide-to-sandwich-attacks/>

**Cited by.** [2023-05-29 Jimbo's Protocol (~4,090 ETH)](../knowledge-base/case-studies/2023-05-29-jimbos-protocol-unprotected-rebalance.md)

### SOL-Defi-AS-13

**Question.** Is the slippage calculated on-chain?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** ON-chain slippage calculation can be manipulated.

**Remediation.** Allow users to specify the slippage parameter in the actual asset amount which was calculated off-chain.

**References.**
- <https://dacian.me/defi-slippage-attacks#heading-on-chain-slippage-calculation-can-be-manipulated>

### SOL-Defi-AS-14

**Question.** Is the slippage parameter enforced at the last step before transferring funds to users?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** Enforcing slippage parameters for intermediate swaps but not the final step can result in users receiving less tokens than their specified minimum

**Remediation.** Enforce slippage parameter as the last step before transferring funds to users

**References.**
- <https://dacian.me/defi-slippage-attacks#heading-mintokensout-for-intermediate-not-final-amount>

### SOL-Defi-LSD-2

**Question.** Can the exchange rate repricing update be sandwich attacked to drain ETH from the protocol?

Source: Cyfrin / Solodit · upstream path: *Defi › Liquid Staking Derivatives*

**Description.** Liquid staking protocols typically have their own liquid ERC20 token that accrues value against ETH as the protocol receives staking rewards; in the normal course of operations the exchange rate should continually be increasing as the protocol accrues rewards such that the protocol's ERC20 token can be exchanged for increasing amounts of ETH. If the protocol allows instant withdrawals, an attacker can perform a risk-free sandwich attack to drain ETH from the protocol by 1) front-running the exchange rate txn to deposit a large amount of ETH, 2) back-running to withdraw at the increased rate.

**Remediation.** Don't allow instant withdrawals but use a withdrawal queue and run the repricing transaction through flashbots.

### SOL-Integrations-Uniswap-1

**Question.** Is the slippage calculated on-chain?

Source: Cyfrin / Solodit · upstream path: *Integrations › Uniswap*

**Description.** ON-chain slippage calculation can be manipulated.

**Remediation.** Allow users to specify the slippage parameter in the actual asset amount which was calculated off-chain.

**References.**
- <https://dacian.me/defi-slippage-attacks#heading-on-chain-slippage-calculation-can-be-manipulated>

### SOL-Integrations-Uniswap-8

**Question.** Is the slippage parameter enforced at the last step before transferring funds to users?

Source: Cyfrin / Solodit · upstream path: *Integrations › Uniswap*

**Description.** Enforcing slippage parameters for intermediate swaps but not the final step can result in users receiving less tokens than their specified minimum

**Remediation.** Enforce slippage parameter as the last step before transferring funds to users

**References.**
- <https://dacian.me/defi-slippage-attacks#heading-mintokensout-for-intermediate-not-final-amount>

## 12. General Solidity Hygiene

### SC-HYG-1

**Question.** Uninitialized storage pointers; `delete` on structs with mappings.

SmartCon core question

### SC-HYG-2

**Question.** Correct handling of `address(this).balance` vs. accounting variables.

SmartCon core question

### SC-HYG-3

**Question.** Events emitted for every state change (for off-chain integrity)?

SmartCon core question

### SC-HYG-4

**Question.** Deprecated constructs (`selfdestruct`, `tx.origin`, `block.difficulty`) reviewed?

SmartCon core question

### SC-HYG-5

**Question.** Have the compiler version and library versions (OpenZeppelin, Solmate) been checked against Appendix A (known compiler and library bugs)?

SmartCon core question · added from: Cyfrin version-issue items

### SC-HYG-6

**Question.** Forked or copied code: were constants, fee denominators and formulas diffed line by line against the upstream (Uniswap, Compound, OpenZeppelin) they came from?

SmartCon core question · added from: case study 2021-04-28 Uranium Finance

**Cited by.** [2021-04-28 Uranium Finance (~$50M)](../knowledge-base/case-studies/2021-04-28-uranium-finance-k-constant-typo.md)

### SOL-Basics-AL-1

**Question.** What happens on the first and the last cycle of the iteration?

Source: Cyfrin / Solodit · upstream path: *Basics › Array / Loop*

**Description.** Sometimes the first and last cycles have a different logic from others and there can be problems.

**Remediation.** Ensure the logic is correct for the first and the last cycles.

### SOL-Basics-AL-4

**Question.** How does the protocol remove an item from an array?

Source: Cyfrin / Solodit · upstream path: *Basics › Array / Loop*

**Description.** `delete` does not rearrange the array but just resets the element.

**Remediation.** Copy the last element to the index of the element to be removed and decrease the length of an array.

### SOL-Basics-AL-6

**Question.** Is the summing of variables done accurately compared to separate calculations?

Source: Cyfrin / Solodit · upstream path: *Basics › Array / Loop*

**Description.** Direct calculation against a sum may yield different results than the sum of individual calculations, leading to precision issues.

**Remediation.** Ensure that summation logic is thoroughly tested and verified, especially when dealing with financial calculations to maintain accuracy.

**References.**
- <https://github.com/sherlock-audit/2022-11-isomorph-judging/issues/174>

### SOL-Basics-AL-8

**Question.** Is there any issue with the first and the last iteration?

Source: Cyfrin / Solodit · upstream path: *Basics › Array / Loop*

**Description.** The first and the last iteration in loops can sometimes have edge cases that differ from other iterations, possibly leading to vulnerabilities.

**Remediation.** Always test the initial and the last iteration separately and ensure consistent behavior throughout all iterations.

### SOL-Basics-AL-13

**Question.** Is there a break or continue inside a loop?

Source: Cyfrin / Solodit · upstream path: *Basics › Array / Loop*

**Description.** Sometimes developers overlook the edge cases that can happened due to the break or continue in the middle of the loop.

**Remediation.** Make sure the break or continue inside a loop does not lead to unexpected behaviors.

### SOL-Basics-Event-1

**Question.** Does the protocol emit events on important state changes?

Source: Cyfrin / Solodit · upstream path: *Basics › Event*

**Description.** Emitting events properly is important especially if the change is critical.

**Remediation.** Ensure to emit events in all important functions.

### SOL-Basics-Function-4

**Question.** Are the code comments coherent with the implementation?

Source: Cyfrin / Solodit · upstream path: *Basics › Function*

**Description.** Misleading or outdated comments can result in misunderstood function behaviors.

**Remediation.** Keep comments updated and ensure they accurately describe the function logic.

**References.**
- <https://solodit.xyz/issues/m-08-wrong-comment-in-getfee-code4rena-yeti-finance-yeti-finance-contest-git>
- <https://solodit.xyz/issues/m-8-wrong-change_collateral_delay-in-collateralbook-sherlock-isomorph-isomorph-git>

### SOL-Basics-Inheritance-2

**Question.** Were all necessary functions implemented to fulfill inheritance purpose?

Source: Cyfrin / Solodit · upstream path: *Basics › Inheritance*

**Description.** Parent contracts often assume the inheriting contracts to implement public functions to utilize the parent's functionality. Sometimes developers miss implementing them and it makes the inheritance useless.

**Remediation.** Make sure to expose relevant functions from parent contracts.

**References.**
- <https://solodit.xyz/issues/m-02-pauseunpause-functionalities-not-implemented-in-many-pausable-contracts-code4rena-stader-labs-stader-labs-git>
- <https://twitter.com/bytes032/status/1736065591536935366>

### SOL-Basics-Inheritance-3

**Question.** Has the contract implemented an interface?

Source: Cyfrin / Solodit · upstream path: *Basics › Inheritance*

**Description.** Interfaces are used by other protocols to interact with the protocol. Missing implementation will lead to unexpected cases.

**Remediation.** Make sure to implement all functions specified in the interface.

### SOL-Basics-Inheritance-4

**Question.** Does the inheritance order matter?

Source: Cyfrin / Solodit · upstream path: *Basics › Inheritance*

**Description.** Inheriting contracts in the wrong order can lead to unexpected behavior, e.g. storage allocation.

**Remediation.** Verify the inheritance chain is ordered from 'most base-like' to 'most derived' to prevent issues like incorrect variable initialization.

### SOL-Basics-Map-1

**Question.** Is there need to delete the existing item from a map?

Source: Cyfrin / Solodit · upstream path: *Basics › Map*

**Description.** If a variable of nested structure is deleted, only the top-level fields are reset by default values (zero) and the nested level fields are not reset.

**Remediation.** Always ensure that inner fields are deleted before the outer fields of the structure.

### SOL-Heuristics-1

**Question.** Is there any logic implemented multiple times?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** Inconsistent implementations of the same logic can introduce errors or vulnerabilities.

**Remediation.** Standardize the logic and make it as a separate function.

### SOL-Heuristics-2

**Question.** Does the contract use any nested structures?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** If a variable of nested structure is deleted, only the top-level fields are reset by default values (zero) and the nested level fields are not reset.

**Remediation.** Always ensure that inner fields are deleted before the outer fields of the structure.

### SOL-Heuristics-6

**Question.** Did you check the relevant EIP recommendations and security concerns?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** Incomplete or incorrect implementation of EIP recommendations can lead to vulnerabilities.

**Remediation.** Read the recommendations and security concerns and ensure all are implemented as per the official recommendations.

### SOL-Heuristics-8

**Question.** Are logical operators used correctly?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** Logical operators like `==`, `!=`, `&&`, `||`, `!` can be overlooked especially when the test coverage is not good.

**Remediation.** Review all usages of logical operators for correctness.

### SOL-Heuristics-13

**Question.** Is the global state updated correctly?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** While working with a `memory` copy for optimization, developers might overlook updating the global state.

**Remediation.** Always ensure the global state mirrors changes made in `memory`. Consider tools or extensions that can highlight discrepancies.

### SOL-Heuristics-15

**Question.** Does the protocol put any sensitive data on the blockchain?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** Data on the blockchain, including that marked 'private' in smart contracts, is visible to anyone who knows how to query the blockchain's state or analyze its transaction history. Private variables are not exempt from public inspection.

**Remediation.** Sensitive data should either be kept off-chain or encrypted before being stored on-chain. It's important to manage encryption keys securely and ensure that on-chain data does not expose private information even when encrypted, if the encryption method is weak or the keys are mishandled.

## 13. Weak Randomness

### SC-RAND-1

**Question.** Is `block.timestamp` / `blockhash` / `prevrandao` used as randomness for a value-bearing outcome? (predictable + validator-influenced)

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/randomness.md`](../knowledge-base/vulnerabilities/randomness.md)

**Cited by.** [2022-08-24 LuckyTiger NFT mint (small and not precisely documen…)](../knowledge-base/case-studies/2022-08-24-luckytiger-nft-predictable-randomness.md)

### SC-RAND-2

**Question.** Can the caller precompute the result in the same tx and revert on a loss?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/randomness.md`](../knowledge-base/vulnerabilities/randomness.md)

**Cited by.** [2022-08-24 LuckyTiger NFT mint (small and not precisely documen…)](../knowledge-base/case-studies/2022-08-24-luckytiger-nft-predictable-randomness.md)

### SC-RAND-3

**Question.** Is a verifiable source (Chainlink VRF) or a sound commit-reveal used instead?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/randomness.md`](../knowledge-base/vulnerabilities/randomness.md)

**Cited by.** [2022-08-24 LuckyTiger NFT mint (small and not precisely documen…)](../knowledge-base/case-studies/2022-08-24-luckytiger-nft-predictable-randomness.md)

### SOL-AM-MA-2

**Question.** Is the contract using block properties like timestamp or difficulty for randomness generation?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Miner Attack*

**Description.** Block properties (timestamp, difficulty) and other predictable values should not be used for randomness as they can be influenced or predicted by miners.

**Remediation.** Use a secure randomness source like Chainlink VRF, commit-reveal schemes, or a provably fair randomization mechanism instead.

**References.**
- <https://solodit.cyfrin.io/issues/m-01-randomindex-is-not-truly-random-possibility-of-predictably-minting-a-specific-token-id-code4rena-larvalabs-meebits-larvalabs-meebits-contest-git>

**Cited by.** [2022-08-24 LuckyTiger NFT mint (small and not precisely documen…)](../knowledge-base/case-studies/2022-08-24-luckytiger-nft-predictable-randomness.md)

### SOL-Integrations-Chainlink-VRF-1

**Question.** Are all parameters properly verified when Chainlink VRF is called?

Source: Cyfrin / Solodit · upstream path: *Integrations › Chainlink › VRF*

**Description.** If the parameters are not thoroughly verified when Chainlink VRF is called, the `fullfillRandomWord` function will not revert but return an incorrect value.

**Remediation.** Ensure that all parameters passed to Chainlink VRF are verified to ensure the correct operation of `fullfillRandomWord`.

### SOL-Integrations-Chainlink-VRF-2

**Question.** Is it guaranteed that the operator holds sufficient LINK in the subscription?

Source: Cyfrin / Solodit · upstream path: *Integrations › Chainlink › VRF*

**Description.** Chainlink VRF can go into a pending state if there's insufficient LINK in the subscription. Once the subscription is refilled, the transaction can potentially be frontrun, introducing vulnerabilities.

**Remediation.** Ensure the pending subscription does not affect the protocol's functionality.

### SOL-Integrations-Chainlink-VRF-3

**Question.** Is a sufficiently high request confirmation number chosen considering chain re-orgs?

Source: Cyfrin / Solodit · upstream path: *Integrations › Chainlink › VRF*

**Description.** Not choosing a high enough request confirmation number can pose risks, especially in the context of chain re-orgs.

**Remediation.** Evaluate the chain's vulnerability to re-orgs and adjust the request confirmation number accordingly.

**References.**
- <https://github.com/pashov/audits/blob/master/solo/NFTLoots-security-review.md#c-01-polygon-chain-reorgs-will-often-change-game-results>

### SOL-Integrations-Chainlink-VRF-4

**Question.** Are measures in place to prevent VRF calls from being frontrun?

Source: Cyfrin / Solodit · upstream path: *Integrations › Chainlink › VRF*

**Description.** VRF calls can be frontrun and it's crucial to ensure that the user interactions are closed before the VRF call to prevent this.

**Remediation.** Ensure the implementation closes the user interaction phase before initiating the VRF call.

## 14. Governance

### SC-GOV-1

**Question.** Is voting power snapshotted at a **past block**, not read from current balance?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/governance.md`](../knowledge-base/vulnerabilities/governance.md)

**Cited by.** [2022-04-16 Beanstalk Farms (~$182M)](../knowledge-base/case-studies/2022-04-16-beanstalk-flash-loan-governance.md)

### SC-GOV-2

**Question.** Is there a **timelock** between a proposal passing and executing?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/governance.md`](../knowledge-base/vulnerabilities/governance.md)

**Cited by.** [2022-04-16 Beanstalk Farms (~$182M)](../knowledge-base/case-studies/2022-04-16-beanstalk-flash-loan-governance.md)

### SC-GOV-3

**Question.** Can a flash loan / large holder reach quorum atomically?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/governance.md`](../knowledge-base/vulnerabilities/governance.md)

**Cited by.** [2022-04-16 Beanstalk Farms (~$182M)](../knowledge-base/case-studies/2022-04-16-beanstalk-flash-loan-governance.md)

### SC-GOV-4

**Question.** What is `execute` allowed to call: treasury, upgrades, arbitrary targets?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/governance.md`](../knowledge-base/vulnerabilities/governance.md)

**Cited by.** [2022-07-23 Audius (704 ETH)](../knowledge-base/case-studies/2022-07-23-audius-storage-collision-governance.md)

### SC-GOV-5

**Question.** Can the code a proposal executes change between vote and execution (metamorphic contract via `CREATE2` + `selfdestruct`, upgradeable target, unpinned bytecode)?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/governance.md`](../knowledge-base/vulnerabilities/governance.md) · added from: Tornado Cash governance 2023-05-20

### SOL-AM-SybilAttack-1

**Question.** Is there a mechanism depending on the number of users?

Source: Cyfrin / Solodit · upstream path: *Attacker's Mindset › Sybil Attack*

**Description.** It is very easy to trigger actions using a lot of alternative addresses on blockchain. Any quorum mechanism or utilization based rewarding system can be vulnerable to sybil attacks.

**Remediation.** Do not rely on the number of users in quorum design.

**References.**
- <https://solodit.xyz/issues/h-7-sybil-on-withdrawal-requests-can-allow-leverage-factor-manipulation-with-flashloans-sherlock-carapace-carapace-git>
- <https://solodit.xyz/issues/routers-can-sybil-attack-the-sponsor-vault-to-drain-funds-spearbit-connext-pdf>
- <https://solodit.xyz/issues/h-5-staker-rewards-can-be-gathered-with-maximal-multiplier-no-matter-how-borrowers-are-overdue-sherlock-union-finance-union-finance-git>

### SOL-Timelock-1

**Question.** Are timelocks implemented for important changes?

Source: Cyfrin / Solodit · upstream path: *Timelock*

**Description.** Immediate changes in the protocol can affect the users.

**Remediation.** Implement timelocks for important changes, allowing users adequate time to respond to proposed alterations.

**Cited by.** [2022-04-16 Beanstalk Farms (~$182M)](../knowledge-base/case-studies/2022-04-16-beanstalk-flash-loan-governance.md)

## 15. Bridges & Cross-Chain

### SC-BRIDGE-1

**Question.** Is the cross-chain message verified against the correct validator set/threshold?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/bridges-cross-chain.md`](../knowledge-base/vulnerabilities/bridges-cross-chain.md)

**Cited by.** [2021-08-10 Poly Network (~$611M)](../knowledge-base/case-studies/2021-08-10-poly-network-cross-chain-keeper-swap.md)

### SC-BRIDGE-2

**Question.** Is a unique nonce / message id consumed to prevent replay?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/bridges-cross-chain.md`](../knowledge-base/vulnerabilities/bridges-cross-chain.md)

### SC-BRIDGE-3

**Question.** Is the message bound to source chain, destination, and exact payload?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/bridges-cross-chain.md`](../knowledge-base/vulnerabilities/bridges-cross-chain.md)

**Cited by.** [2022-01-27 Qubit Finance QBridge (~$80M)](../knowledge-base/case-studies/2022-01-27-qubit-finance-codeless-address-call.md); [2021-08-10 Poly Network (~$611M)](../knowledge-base/case-studies/2021-08-10-poly-network-cross-chain-keeper-swap.md)

### SC-BRIDGE-4

**Question.** Are bridge init/upgrade paths tightly guarded? (Nomad/Wormhole/Ronin class)

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/bridges-cross-chain.md`](../knowledge-base/vulnerabilities/bridges-cross-chain.md)

**Cited by.** [2022-08-01 Nomad token bridge (~$190M)](../knowledge-base/case-studies/2022-08-01-nomad-bridge-zero-root-accepted.md)

### SC-BRIDGE-5

**Question.** Can a cross-chain message target a privileged contract of the bridge itself (config, keeper or validator-set contract) and pass its `onlyOwner` check because the executor is the owner?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/bridges-cross-chain.md`](../knowledge-base/vulnerabilities/bridges-cross-chain.md) · added from: case study 2021-08-10 Poly Network

**Cited by.** [2021-08-10 Poly Network (~$611M)](../knowledge-base/case-studies/2021-08-10-poly-network-cross-chain-keeper-swap.md)

### SC-BRIDGE-6

**Question.** Is the zero/default value of a trusted-root, confirmation or nonce mapping treated as valid or "confirmed"?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/bridges-cross-chain.md`](../knowledge-base/vulnerabilities/bridges-cross-chain.md) · added from: case study 2022-08-01 Nomad

**Cited by.** [2022-08-01 Nomad token bridge (~$190M)](../knowledge-base/case-studies/2022-08-01-nomad-bridge-zero-root-accepted.md)

### SOL-Integrations-Chainlink-CCIP-1

**Question.** Does the receiver contract's `_ccipReceive` function properly validate the `sourceChainSelector` and `sender` address against an allowlist?

Source: Cyfrin / Solodit · upstream path: *Integrations › Chainlink › CCIP*

**Description.** Receiver contracts might process messages from unintended source chains or senders if they don't validate the origin.

**Remediation.** Implement checks within `_ccipReceive` to verify the `any2EvmMessage.sourceChainSelector` and decoded `any2EvmMessage.sender` against administratively controlled allowlists.

### SOL-Integrations-Chainlink-CCIP-2

**Question.** Does the sender contract validate the `destinationChainSelector` against an allowlist before calling `ccipSend`?

Source: Cyfrin / Solodit · upstream path: *Integrations › Chainlink › CCIP*

**Description.** Sender contracts might accidentally send messages and tokens to unintended or unsupported destination chains.

**Remediation.** Implement checks in the sending function to ensure the `destinationChainSelector` corresponds to an explicitly allowlisted chain.

### SOL-Integrations-Chainlink-CCIP-3

**Question.** Does the receiver contract properly decode data (`any2EvmMessage.data`) ?

Source: Cyfrin / Solodit · upstream path: *Integrations › Chainlink › CCIP*

**Description.** The encoding on the source chain and decoding on the destination chain must maintain precise structural consistency.

**Remediation.** Standardize both contracts to use identical ABI encoding/decoding patterns with explicit type declarations and thorough parameter validation to ensure cross-chain message integrity.

### SOL-Integrations-Chainlink-CCIP-4

**Question.** Does the application logic account for the potential latency introduced by waiting for source chain finality as defined by CCIP?

Source: Cyfrin / Solodit · upstream path: *Integrations › Chainlink › CCIP*

**Description.** Applications assuming immediate cross-chain execution might behave unexpectedly due to varying finality times across blockchains which CCIP respects.

**Remediation.** Design application logic to be aware of and tolerant to CCIP execution latencies, which depend on the source chain's finality mechanism (finality tag or block depth).

**References.**
- <https://docs.chain.link/ccip/concepts/ccip-execution-latency#finality-by-blockchain>

### SOL-Integrations-Chainlink-CCIP-5

**Question.** Are the correct types of token pools (e.g., `BurnMintTokenPool`, `LockReleaseTokenPool`) deployed on the source and destination chains consistent with the desired token handling mechanism?

Source: Cyfrin / Solodit · upstream path: *Integrations › Chainlink › CCIP*

**Description.** Deploying mismatched pool types (e.g., expecting Lock & Mint but deploying Burn & Mint on the destination) will lead to failed transfers or incorrect token handling.

**Remediation.** Verify that the deployed token pool contracts on each chain match the intended cross-chain mechanism (Burn & Mint requires BurnMint pools; Lock & Mint requires LockRelease on source, BurnMint on destination, etc.).

**References.**
- <https://docs.chain.link/ccip/concepts/cross-chain-tokens#token-handling-mechanisms-and-token-pool-deployment>

### SOL-Integrations-Chainlink-CCIP-6

**Question.** Is proper router address verification implemented in the ccipReceive method?

Source: Cyfrin / Solodit · upstream path: *Integrations › Chainlink › CCIP*

**Description.** Without proper router validation, any address can spoof messages, potentially compromising contract security and asset integrity.

**Remediation.** Implement a router address verification check that validates msg.sender against a trusted router address.

**References.**
- <https://docs.chain.link/ccip/best-practices#verify-router-addresses>

### SOL-Integrations-Chainlink-CCIP-7

**Question.** Are extraArgs parameters hardcoded instead of mutable in cross-chain message configurations?

Source: Cyfrin / Solodit · upstream path: *Integrations › Chainlink › CCIP*

**Description.** Hardcoded extraArgs parameters prevent adaptation to future CCIP protocol upgrades and gas requirement changes, potentially causing cross-chain transactions to fail or become incompatible with network upgrades.

**Remediation.** Implement extraArgs as mutable parameters that can be configured off-chain or via updateable contract variables rather than hardcoding them directly in the contract logic.

**References.**
- <https://docs.chain.link/ccip/best-practices#using-extraargs>

### SOL-Integrations-Chainlink-CCIP-8

**Question.** Is there a proper failure handling mechanism for CCIP messages to prevent blocking after Smart Execution window expiration?

Source: Cyfrin / Solodit · upstream path: *Integrations › Chainlink › CCIP*

**Description.** When a CCIP message fails and the Smart Execution time window (8 hours) expires, all subsequent messages from the same sender will be blocked until the failed message succeeds, potentially causing permanent denial of service if the message cannot be fixed.

**Remediation.** Implement robust error handling in CCIPReceiver implementation with try/catch blocks and recovery mechanisms to ensure messages can be successfully processed even under unexpected conditions.

**References.**
- <https://solodit.cyfrin.io/issues/m-04-price-updating-mechanism-can-break-code4rena-renzo-renzo-git>

### SOL-Integrations-LayerZero-1

**Question.** Does the `_debitFrom` function in ONFT properly validate token ownership and transfer permissions?

Source: Cyfrin / Solodit · upstream path: *Integrations › LayerZero*

**Description.** It's crucial that the `_debitFrom` function verifies whether the specified owner is the actual owner of the tokenId and if the sender has the correct permissions to transfer the token.

**Remediation.** Ensure thorough checks and validations are performed in the `_debitFrom` function to maintain token security.

**References.**
- <https://composable-security.com/blog/secure-integration-with-layer-zero/>

### SOL-Integrations-LayerZero-2

**Question.** Which type of mechanism are utilized? Blocking or non-blocking?

Source: Cyfrin / Solodit · upstream path: *Integrations › LayerZero*

**Description.** Using blocking mechanism can potentially lead to a Denial-of-Service (DoS) attack.

**Remediation.** Consider using non-blocking mechanism to prevent potential DoS attacks.

**References.**
- <https://solodit.xyz/issues/h-06-attacker-can-block-layerzero-channel-code4rena-velodrome-finance-velodrome-finance-contest-git>

### SOL-Integrations-LayerZero-3

**Question.** Is gas estimated accurately for cross-chain messages?

Source: Cyfrin / Solodit · upstream path: *Integrations › LayerZero*

**Description.** Inaccurate gas estimation can result in cross-chain message failures.

**Remediation.** Implement mechanisms to estimate gas accurately.

### SOL-Integrations-LayerZero-4

**Question.** Is the `_lzSend` function correctly utilized when inheriting LzApp?

Source: Cyfrin / Solodit · upstream path: *Integrations › LayerZero*

**Description.** When inheriting LzApp, direct calls to `lzEndpoint.send` can introduce vulnerabilities. Using `_lzSend` is the recommended approach.

**Remediation.** Ensure that the `_lzSend` function is used instead of making direct calls to `lzEndpoint.send`.

### SOL-Integrations-LayerZero-5

**Question.** Is the `ILayerZeroUserApplicationConfig` interface correctly implemented?

Source: Cyfrin / Solodit · upstream path: *Integrations › LayerZero*

**Description.** The User Application should include the `forceResumeReceive` function to handle unexpected scenarios and unblock the message queue when needed.

**Remediation.** Implement the `ILayerZeroUserApplicationConfig` interface and ensure that the `forceResumeReceive` function is present and functional.

### SOL-Integrations-LayerZero-6

**Question.** Are default contracts used?

Source: Cyfrin / Solodit · upstream path: *Integrations › LayerZero*

**Description.** Default configuration contracts are upgradeable by the LayerZero team.

**Remediation.** Configure the applications uniquely and avoid using default settings.

### SOL-Integrations-LayerZero-7

**Question.** Is the correct number of confirmations chosen for the chain?

Source: Cyfrin / Solodit · upstream path: *Integrations › LayerZero*

**Description.** Choosing an inappropriate number of confirmations can introduce risks, especially considering past reorg events on the chain.

**Remediation.** Evaluate the chain's history and potential vulnerabilities to determine the optimal number of confirmations.

### SOL-Integrations-Uniswap-3

**Question.** Is the order of `token0` and `token1` consistent across chains?

Source: Cyfrin / Solodit · upstream path: *Integrations › Uniswap*

**Description.** The order of `token0` and `token1` in AMM pools may vary depending on the chain, which can lead to inconsistencies.

**Remediation.** Always verify the order of tokens when interacting with different chains to avoid potential issues.

### SOL-McCc-1

**Question.** Are there assumption of consistency in the `block.number` or `block.timestamp` across chains?

Source: Cyfrin / Solodit · upstream path: *Multi-chain/Cross-chain*

**Description.** Block time can vary across different chains, leading to potential timing discrepancies.

**Remediation.** Avoid comparing timestamp or block numbers for different chains.

**References.**
- <https://solodit.cyfrin.io/issues/m-06-l1xrenzobridge-and-l2xrenzobridge-uses-the-blocktimestamp-as-dependency-which-can-cause-issues-code4rena-renzo-renzo-git>

### SOL-McCc-2

**Question.** Has the protocol been checked for the target chain differences?

Source: Cyfrin / Solodit · upstream path: *Multi-chain/Cross-chain*

**Description.** Understanding the differences between chains is vital for ensuring compatibility and preventing unexpected behaviors.

**Remediation.** Regularly check for chain differences and update the protocol accordingly.

**References.**
- <https://www.evmdiff.com/diff?base=1&target=10>
- <https://github.com/0xJuancito/multichain-auditor#differences-from-ethereum>

### SOL-McCc-3

**Question.** Are the EVM opcodes and operations used by the protocol compatible across all targeted chains?

Source: Cyfrin / Solodit · upstream path: *Multi-chain/Cross-chain*

**Description.** Incompatibility can arise when the protocol uses EVM operations not supported on certain chains.

**Remediation.** Review and ensure compatibility for chains like Arbitrum and Optimism.

**References.**
- <https://docs.arbitrum.io/solidity-support>
- <https://community.optimism.io/docs/developers/build/differences/#transaction-costs>

### SOL-McCc-4

**Question.** Does the expected behavior of `tx.origin` and `msg.sender` remain consistent across all deployment chains?

Source: Cyfrin / Solodit · upstream path: *Multi-chain/Cross-chain*

**Description.** Different chains might interpret these values differently, leading to unexpected behaviors.

**Remediation.** Test and verify the behavior on all targeted chains.

**References.**
- <https://community.optimism.io/docs/developers/build/differences/#opcode-differences>

### SOL-McCc-5

**Question.** Is there any possibility of exploiting low gas fees to execute many transactions?

Source: Cyfrin / Solodit · upstream path: *Multi-chain/Cross-chain*

**Description.** Some attacks become viable with low gas costs or when a large number of transactions can be processed.

**Remediation.** Evaluate and mitigate potential attack vectors associated with gas fees.

**References.**
- <https://github.com/0xJuancito/multichain-auditor#gas-fees>

### SOL-McCc-6

**Question.** Is there consistency in ERC20 decimals across chains?

Source: Cyfrin / Solodit · upstream path: *Multi-chain/Cross-chain*

**Description.** Decimals in ERC20 tokens can differ across chains.

**Remediation.** Ensure consistent ERC20 decimals or implement chain-specific adjustments.

**References.**
- <https://github.com/0xJuancito/multichain-auditor#erc20-decimals>

### SOL-McCc-7

**Question.** Have contract upgradability implications been evaluated on different chains?

Source: Cyfrin / Solodit · upstream path: *Multi-chain/Cross-chain*

**Description.** Contracts may have different upgradability properties depending on the chain, like USDT being upgradable on Polygon but not on Ethereum.

**Remediation.** Verify and document upgradability characteristics for each chain.

### SOL-McCc-8

**Question.** Have cross-chain messaging implementations been thoroughly reviewed for permissions and functionality?

Source: Cyfrin / Solodit · upstream path: *Multi-chain/Cross-chain*

**Description.** Cross-chain messaging requires robust security checks to ensure the correct permissions and intended functionality.

**Remediation.** Double check the access control over cross-chain messaging components.

**Cited by.** [2021-08-10 Poly Network (~$611M)](../knowledge-base/case-studies/2021-08-10-poly-network-cross-chain-keeper-swap.md)

### SOL-McCc-9

**Question.** Is there a whitelist of compatible chains?

Source: Cyfrin / Solodit · upstream path: *Multi-chain/Cross-chain*

**Description.** Allowing messages from an unsupported chain can lead to unpredictable results.

**Remediation.** Implement a whitelist to prevent messages from unsupported chains.

### SOL-McCc-10

**Question.** Have contracts been checked for compatibility when deployed to the zkSync Era?

Source: Cyfrin / Solodit · upstream path: *Multi-chain/Cross-chain*

**Description.** zkSync Era might have specific requirements or differences when compared to standard Ethereum deployments.

**Remediation.** Review and ensure compatibility before deploying contracts to zkSync Era.

**References.**
- <https://era.zksync.io/docs/reference/architecture/differences-with-ethereum.html>

### SOL-McCc-11

**Question.** Is block production consistency ensured?

Source: Cyfrin / Solodit · upstream path: *Multi-chain/Cross-chain*

**Description.** Inconsistent block production can lead to unexpected application behaviors.

**Remediation.** Develop with the assumption that block production may not always be consistent.

### SOL-McCc-12

**Question.** Is `PUSH0` opcode supported for Solidity version `>=0.8.20`?

Source: Cyfrin / Solodit · upstream path: *Multi-chain/Cross-chain*

**Description.** `PUSH0` might not be supported on all chains, leading to potential incompatibility issues.

**Remediation.** Ensure if `PUSH0` is supported in the target chain.

**References.**
- <https://github.com/0xJuancito/multichain-auditor#support-for-the-push0-opcode>

### SOL-McCc-13

**Question.** Are there any attributes attached to the bridged assets?

Source: Cyfrin / Solodit · upstream path: *Multi-chain/Cross-chain*

**Description.** When assets (e.g. tokens) are bridged across chains, the relevant attributes (e.g. approval) must be bridged or reset accordingly.

**Remediation.** Ensure accounting all the relevant attributes when assets are bridged.

**References.**
- <https://solodit.cyfrin.io/issues/not-update-rewards-in-handleincomingupdate-function-of-sdlpoolprimary-leads-to-incorrect-reward-calculations-codehawks-stakelink-git>

## 16. Low-Level Calls & Return Data

### SC-LL-1

**Question.** Is the `bool` from every `call`/`send`/`delegatecall` checked?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/low-level-calls.md`](../knowledge-base/vulnerabilities/low-level-calls.md)

### SC-LL-2

**Question.** Any `delegatecall` to an untrusted/user-controlled target?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/low-level-calls.md`](../knowledge-base/vulnerabilities/low-level-calls.md)

### SC-LL-3

**Question.** Can a callee return-bomb the caller (unbounded returndata)?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/low-level-calls.md`](../knowledge-base/vulnerabilities/low-level-calls.md)

### SC-LL-4

**Question.** Is a `call` to a possibly-codeless address treated as success? (phantom function)

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/low-level-calls.md`](../knowledge-base/vulnerabilities/low-level-calls.md)

**Cited by.** [2022-01-27 Qubit Finance QBridge (~$80M)](../knowledge-base/case-studies/2022-01-27-qubit-finance-codeless-address-call.md); [2022-01-18 Multichain / Anyswap `AnyswapV4Router.a… (~$1.4M)](../knowledge-base/case-studies/2022-01-18-multichain-anyswap-phantom-permit.md)

### SOL-Basics-Payment-6

**Question.** Is `transfer()` or `send()` used for sending ETH?

Source: Cyfrin / Solodit · upstream path: *Basics › Payment*

**Description.** The transfer() and send() functions forward a fixed amount of 2300 gas. Historically, it has often been recommended to use these functions for value transfers to guard against reentrancy attacks. However, the gas cost of EVM instructions may change significantly during hard forks which may break already deployed contract systems that make fixed assumptions about gas costs. For example. EIP 1884 broke several existing smart contracts due to a cost increase of the SLOAD instruction.

**Remediation.** Use `call()` to prevent potential gas issues.

**References.**
- <https://solodit.xyz/issues/use-call-instead-of-transfer-cyfrin-none-woosh-deposit-vault-markdown>
- <https://solodit.xyz/issues/m-5-call-should-be-used-instead-of-transfer-on-an-address-payable-sherlock-dodo-dodo-git>
- <https://solodit.xyz/issues/m-10-addresscallvaluex-should-be-used-instead-of-payabletransfer-code4rena-debt-dao-debt-dao-contest-git>

### SOL-EC-3

**Question.** What are the risks associated with using delegatecall in smart contracts?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** A delegatecall is a low-level function call that delegates the execution of a function in another contract while maintaining the original contract's context. It can lead to critical vulnerabilities if the destination address is not secure or can be altered by an unauthorized party.

**Remediation.** Use delegatecall only with trusted contracts, and ensure that the address to be delegated to is not changeable by unauthorized users. Implement strong access controls and audit the code for potential security issues before deployment.

Tags: SWC-112

### SOL-EC-4

**Question.** Is the external contract call necessary?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** Unnecessary external calls can introduce vulnerabilities.

**Remediation.** Evaluate and eliminate non-essential external contract calls.

### SOL-EC-6

**Question.** Is there suspicion when a fixed gas amount is specified?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** Specifying fixed gas amounts can lead to out-of-gas vulnerabilities.

**Remediation.** Use dynamic gas estimation or ensure sufficient gas is available before the call.

**References.**
- <https://solodit.xyz/issues/m-02-fixed-amount-of-gas-sent-in-call-may-be-insufficient-code4rena-joyn-joyn-contest-git>
- <https://solodit.xyz/issues/a-malicious-fee-receiver-can-cause-a-denial-of-service-trailofbits-nftx-protocol-v2-pdf>

### SOL-EC-7

**Question.** What happens if the call consumes all provided gas?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** Calls that consume all available gas can halt subsequent actions.

**Remediation.** Ensure enough gas is reserved for post-call tasks or use dynamic gas estimation.

**References.**
- <https://solodit.xyz/issues/a-malicious-fee-receiver-can-cause-a-denial-of-service-trailofbits-nftx-protocol-v2-pdf>
- <https://solodit.xyz/issues/poison-order-that-consumes-gas-can-block-market-trades-wont-fix-consensys-0x-v3-exchange-markdown>

### SOL-EC-8

**Question.** Is the contract passing large data to an unknown address?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** Large data passed to untrusted addresses may be exploited for griefing.

**Remediation.** Limit data passed or employ inline assembly to manage data transfer.

**References.**
- <https://solodit.xyz/issues/h-2-malicious-user-can-use-an-excessively-large-_toaddress-in-oftcoresendfrom-to-break-layerzero-communication-sherlock-uxd-uxd-protocol-git>

### SOL-EC-9

**Question.** What happens if the call returns vast data?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** External calls returning vast data can deplete available gas.

**Remediation.** Limit or verify data size returned from external sources.

**References.**
- <https://solodit.cyfrin.io/?b=false&f=&fc=gte&ff=&fn=1&i=HIGH%2CMEDIUM&p=1&pc=&r=all&s=gas+griefing&t=>

### SOL-EC-10

**Question.** Are there any delegate calls to non-library contracts?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** Non-library delegate calls can alter the state of the calling contract.

**Remediation.** Thoroughly review and verify such delegate calls so that the delegate calls do not change the caller's state unexpectedly.

### SOL-EC-11

**Question.** Is there a strict policy against delegate calls to untrusted contracts?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** Delegate calls grant the called contract the context of the caller, risking state alterations.

**Remediation.** Restrict delegate calls to only trusted, reviewed, and audited contracts.

**References.**
- <https://solodit.xyz/issues/m-01-delegate-call-in-vault_execute-can-alter-vaults-ownership-code4rena-fractional-fractional-v2-contest-git>

### SOL-EC-12

**Question.** Is the address's existence verified?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** Calling non-existent addresses can lead to unintended behaviors. Low level calls (call, delegate call and static call) return success if the called contract doesn't exist (not deployed or destructed)

**Remediation.** Verify the existence of an address before making a call.

**References.**
- <https://solodit.xyz/issues/h-02-non-existing-revenue-contract-can-be-passed-to-claimrevenue-to-send-all-tokens-to-treasury-code4rena-debt-dao-debt-dao-contest-git>
- <https://solodit.xyz/issues/m-10-call-to-non-existing-contracts-returns-success-code4rena-biconomy-biconomy-hyphen-20-contest-git>
- <https://solodit.xyz/issues/lack-of-contract-existence-check-on-delegatecall-will-result-in-unexpected-behavior-trailofbits-degate-pdf>
- <https://solodit.xyz/issues/m-02-solmates-erc20-does-not-check-for-token-contracts-existence-which-opens-up-possibility-for-a-honeypot-attack-code4rena-size-size-contest-git>
- <https://solodit.xyz/issues/m-25-vault-can-be-created-for-not-yet-existing-erc20-tokens-which-allows-attackers-to-set-traps-to-steal-nfts-from-borrowers-code4rena-astaria-astaria-git>
- <https://solodit.xyz/issues/calls-made-to-non-existentremoved-routes-or-controllers-will-not-result-in-failure-consensys-socket-markdown>

**Cited by.** [2022-01-27 Qubit Finance QBridge (~$80M)](../knowledge-base/case-studies/2022-01-27-qubit-finance-codeless-address-call.md)

### SOL-Heuristics-5

**Question.** Does the `try/catch` block account for potential gas shortages?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** A `try/catch` block without adequate gas can fail, leading to unexpected behaviors.

**Remediation.** Ensure sufficient gas is supplied when using the `try/catch` block.

**References.**
- <https://forum.openzeppelin.com/t/a-brief-analysis-of-the-new-try-catch-functionality-in-solidity-0-6/2564>

### SOL-LL-1

**Question.** Is there validation on the size of the input data?

Source: Cyfrin / Solodit · upstream path: *Low Level*

**Description.** In low-level, data size is not checked by default and it can affect the unintended memory locations.

**Remediation.** Validate that inputs do not exceed the size of it's expected type and either revert or clean the unused bits depending on your use case before using that value.

**References.**
- <https://github.com/AmadiMichael/LowLevelVulnerabilities?tab=readme-ov-file#validate-all-input-bit-size>

### SOL-LL-2

**Question.** What happens if there is no matching function signature?

Source: Cyfrin / Solodit · upstream path: *Low Level*

**Description.** It is expected to revert if there is no matching function signature in the contract. Overlooking this can let the execution continue into other parts of the unintended bytecode.

**Remediation.** Ensure that the code reverts after comparing all supported function signatures, fallback etc and not matching any.

**References.**
- <https://github.com/AmadiMichael/LowLevelVulnerabilities?tab=readme-ov-file#end-execution-after-function-dispatching>

**Cited by.** [2022-01-18 Multichain / Anyswap `AnyswapV4Router.a… (~$1.4M)](../knowledge-base/case-studies/2022-01-18-multichain-anyswap-phantom-permit.md)

### SOL-LL-3

**Question.** Is it checked if the target address of a call has the code?

Source: Cyfrin / Solodit · upstream path: *Low Level*

**Description.** Calling an address without code is always successful.

**Remediation.** Ensure that addresses being called, static-called or delegate-called have code deployed.

**References.**
- <https://github.com/AmadiMichael/LowLevelVulnerabilities?tab=readme-ov-file#ensure-that-addresses-being-called-static-called-or-delegate-called-have-code-deployed-to-them>

**Cited by.** [2022-01-27 Qubit Finance QBridge (~$80M)](../knowledge-base/case-studies/2022-01-27-qubit-finance-codeless-address-call.md)

### SOL-LL-4

**Question.** Is there a check on the return data size when calling precompiled code?

Source: Cyfrin / Solodit · upstream path: *Low Level*

**Description.** When calling precompiled code, the call is still successful on error or ”failure”. A failed precompile call simply has a return data size of 0.

**Remediation.** Check the return data size not the success of the call to determine if it failed.

**References.**
- <https://github.com/AmadiMichael/LowLevelVulnerabilities?tab=readme-ov-file#when-calling-precompiles-check-the-returndatasize-not-the-success-of-the-call-to-determine-if-it-failed>

## 17. Input Validation & Uninitialized State

### SC-INPUT-1

**Question.** Zero-address checks on setters and transfers?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/input-validation.md`](../knowledge-base/vulnerabilities/input-validation.md)

**Cited by.** [2022-01-27 Qubit Finance QBridge (~$80M)](../knowledge-base/case-studies/2022-01-27-qubit-finance-codeless-address-call.md)

### SC-INPUT-2

**Question.** Zero-amount / dust edge cases handled without corrupting accounting?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/input-validation.md`](../knowledge-base/vulnerabilities/input-validation.md)

### SC-INPUT-3

**Question.** Array-length equality checked in batch functions?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/input-validation.md`](../knowledge-base/vulnerabilities/input-validation.md)

### SC-INPUT-4

**Question.** Every critical variable initialized before use; parameters range-checked?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/input-validation.md`](../knowledge-base/vulnerabilities/input-validation.md)

### SC-INPUT-5

**Question.** Do callbacks (flash-loan, Uniswap `swap`/`mint`, ERC-721 receiver) verify `msg.sender` is the expected pool/lender and that the initiator is this contract?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/input-validation.md`](../knowledge-base/vulnerabilities/input-validation.md) · added from: case study 2023-04-09 SushiSwap RouteProcessor2

**Cited by.** [2023-04-09 SushiSwap `RouteProcessor2` router (>$3.3M)](../knowledge-base/case-studies/2023-04-09-sushiswap-routeprocessor2-unverified-callback.md)

### SC-INPUT-6

**Question.** Can user-supplied addresses or calldata make the contract perform an arbitrary external call (router, target, token), including `transferFrom` against other users' approvals?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/input-validation.md`](../knowledge-base/vulnerabilities/input-validation.md) · added from: Dexible, Transit Swap, Socket

**Cited by.** [2023-04-09 SushiSwap `RouteProcessor2` router (>$3.3M)](../knowledge-base/case-studies/2023-04-09-sushiswap-routeprocessor2-unverified-callback.md)

### SC-INPUT-7

**Question.** Does any mapping lookup treat the zero/default value (`bytes32(0)`, `address(0)`, `0`) as valid or "confirmed"?

SmartCon core question · knowledge base: [`knowledge-base/vulnerabilities/input-validation.md`](../knowledge-base/vulnerabilities/input-validation.md) · added from: case study 2022-08-01 Nomad

**Cited by.** [2022-08-01 Nomad token bridge (~$190M)](../knowledge-base/case-studies/2022-08-01-nomad-bridge-zero-root-accepted.md)

### SOL-Basics-AL-5

**Question.** Does any function get an index of an array as an argument?

Source: Cyfrin / Solodit · upstream path: *Basics › Array / Loop*

**Description.** If an array is supposed to be updated (removal in the middle), the indexes will change.

**Remediation.** Do not use an index of an array that is supposed to be updated as a parameter of a function.

### SOL-Basics-AL-7

**Question.** Is it fine to have duplicate items in the array?

Source: Cyfrin / Solodit · upstream path: *Basics › Array / Loop*

**Description.** In most cases, an array (especially an input array by users) is supposed to be unique.

**Remediation.** Add a validation to check the array is unique.

**References.**
- <https://solodit.cyfrin.io/issues/duplicate-interactions-mixbytes-none-liquorice-markdown>

### SOL-Basics-AL-11

**Question.** Is `msg.value` used within a loop?

Source: Cyfrin / Solodit · upstream path: *Basics › Array / Loop*

**Description.** `msg.value` is consistent for the whole transaction. If it is used in the for loop, it is likely there is a mistake in accounting.

**Remediation.** Avoid using `msg.value` inside loops. Refer to multi-call vulnerability.

### SOL-Basics-Function-1

**Question.** Are the inputs validated?

Source: Cyfrin / Solodit · upstream path: *Basics › Function*

**Description.** Inputs to functions should be validated to prevent unexpected behavior.

**Remediation.** Ensure thorough validation. E.g. min/max for numeric values, start/end for dates, ownership of positions.

**References.**
- <https://solodit.xyz/issues/missing-owner-check-on-from-when-transferring-tokens-spearbit-clober-pdf>
- <https://solodit.xyz/issues/m-13-bondbasesdasetdefaults-doesnt-validate-inputs-sherlock-bond-bond-protocol-git>
- <https://solodit.xyz/issues/h-16-user-supplied-amm-pools-and-no-input-validation-allows-stealing-of-steth-protocol-fees-sherlock-swivel-illuminate-git>

### SOL-Basics-Function-2

**Question.** Are the outputs validated?

Source: Cyfrin / Solodit · upstream path: *Basics › Function*

**Description.** Outputs of functions should be validated to prevent unexpected behavior.

**Remediation.** Ensure the outputs are valid.

### SOL-Basics-Function-5

**Question.** Can edge case inputs (0, max) result in unexpected behavior?

Source: Cyfrin / Solodit · upstream path: *Basics › Function*

**Description.** Edge input values can lead to unexpected behavior.

**Remediation.** Make sure the function works as expected for the edge values.

**References.**
- <https://solodit.xyz/issues/lack-of-validation-openzeppelin-bancor-compounding-rewards-audit-markdown>
- <https://solodit.xyz/issues/p1-m07-lack-of-input-validation-openzeppelin-eco-contracts-audit-markdown>

### SOL-Basics-Function-6

**Question.** Does the function allow arbitrary user input?

Source: Cyfrin / Solodit · upstream path: *Basics › Function*

**Description.** Implementing a function that accepts arbitrary user input and makes low-level calls based on this data introduces a significant security risk. Low-level calls in Solidity, such as call(), are powerful and can lead to unintended contract behavior if not used cautiously. With the ability for users to supply arbitrary data, they can potentially trigger unexpected paths in the contract logic, exploit reentrancy vulnerabilities, or even interact with other contracts in a malicious manner.

**Remediation.** Restrict the usage of low-level calls, especially when combined with arbitrary user input. Ensure that any data used in these calls is thoroughly validated and sanitized.

### SOL-Basics-Initialization-1

**Question.** Are important state variables initialized properly?

Source: Cyfrin / Solodit · upstream path: *Basics › Initialization*

**Description.** Overlooking explicit initialization of state variables can lead to critical issues.

**Remediation.** Make sure to initialize all state variables correctly.

**References.**
- <https://solodit.xyz/issues/h-01-mintersolstartinflation-can-be-bypassed-code4rena-backd-backd-tokenomics-contest-git>

### SOL-Basics-Payment-2

**Question.** Does the function gets the payment amount as a parameter?

Source: Cyfrin / Solodit · upstream path: *Basics › Payment*

**Description.** For ETH deposits, `msg.value` must be checked if it is not less than the amount specified.

**Remediation.** Require `msg.value==amount`.

### SOL-Defi-AS-6

**Question.** Can arbitrary calls be made from user input?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** Allowing arbitrary calls based on user input can expose the contract to various vulnerabilities.

**Remediation.** Validate and sanitize user inputs. Avoid executing arbitrary calls based solely on input data.

**Cited by.** [2023-04-09 SushiSwap `RouteProcessor2` router (>$3.3M)](../knowledge-base/case-studies/2023-04-09-sushiswap-routeprocessor2-unverified-callback.md)

### SOL-Defi-AS-12

**Question.** Does the integrating contract verify the caller address in its callback functions?

Source: Cyfrin / Solodit · upstream path: *Defi › AMM/Swap*

**Description.** Callback functions can be manipulated if they don't validate the calling contract's address. This is especially crucial for functions like `swap()` that involve tokens or assets.

**Remediation.** Implement checks in the callback functions to validate the address of the calling contract. Additionally, review the logic for any potential bypasses to this check.

**Cited by.** [2023-04-09 SushiSwap `RouteProcessor2` router (>$3.3M)](../knowledge-base/case-studies/2023-04-09-sushiswap-routeprocessor2-unverified-callback.md)

### SOL-EC-2

**Question.** Is there a multi-call?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** Mismanagement of `msg.value` across multiple calls can lead to vulnerabilities.

**Remediation.** Do not use ETH in multicall.

**References.**
- <https://solodit.xyz/issues/m-08-passing-multiple-eth-deposits-in-orders-array-will-use-the-same-msgvalue-many-times-code4rena-nested-finance-nested-finance-contest-git>

### SOL-EC-5

**Question.** Has the called address been whitelisted?

Source: Cyfrin / Solodit · upstream path: *External Call*

**Description.** Calling untrusted addresses can lead to malicious actions.

**Remediation.** Ensure that only whitelisted or trusted contract addresses are called.

**References.**
- <https://solodit.xyz/issues/too-generic-calls-in-genericbridgefacet-allow-stealing-of-tokens-spearbit-lifi-pdf>
- <https://solodit.xyz/issues/hardcode-or-whitelist-the-axelar-destinationaddress-spearbit-lifi-pdf>

**Cited by.** [2023-04-09 SushiSwap `RouteProcessor2` router (>$3.3M)](../knowledge-base/case-studies/2023-04-09-sushiswap-routeprocessor2-unverified-callback.md)

### SOL-Heuristics-3

**Question.** Is there any unexpected behavior when `src==dst` (or `caller==receiver`)?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** Overlooking the possibility of a sender and a recipient (source and destination) being the same in smart contracts can lead to unintended problems.

**Remediation.** Ensure the protocol behaves as expected when `src==dst`.

### SOL-Heuristics-9

**Question.** What happens if the protocol's contracts are inputted as if they are normal actors?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** Supplying unexpected addresses can lead to unintended behaviors, especially if the address points to another contract inside the same protocol.

**Remediation.** Implement checks to validate receiver addresses and ensure the protocol behaves as expected.

### SOL-Heuristics-11

**Question.** Is there any uninitialized state?

Source: Cyfrin / Solodit · upstream path: *Heuristics*

**Description.** Checking a variable against its default value might be used to detect initialization. If such defaults can also be valid state, it could lead to vulnerabilities.

**Remediation.** Avoid solely relying on default values to determine initialization status.

**Cited by.** [2022-08-01 Nomad token bridge (~$190M)](../knowledge-base/case-studies/2022-08-01-nomad-bridge-zero-root-accepted.md)

### SOL-Integrations-Uniswap-4

**Question.** Are the pools that are being interacted with whitelisted?

Source: Cyfrin / Solodit · upstream path: *Integrations › Uniswap*

**Description.** Missing verification on the interacting pools can introduce risks.

**Remediation.** Ensure pools are whitelisted or verify the pool's factory address before any interactions.

### SOL-Integrations-Uniswap-6

**Question.** Is `pool.swap()` directly used?

Source: Cyfrin / Solodit · upstream path: *Integrations › Uniswap*

**Description.** Directly using `pool.swap()` can bypass certain security mechanisms.

**Remediation.** Always use the Router contract to handle swaps, providing an added layer of security and standardization.

**Cited by.** [2023-04-09 SushiSwap `RouteProcessor2` router (>$3.3M)](../knowledge-base/case-studies/2023-04-09-sushiswap-routeprocessor2-unverified-callback.md)

## Appendix A. Version-specific issues (compiler and library bugs)

### SOL-Basics-VI-EAI-1

**Question.** EIP-4758: Does the contract use `selfdestruct()`?

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › EIP Adoption Issues*

**Description.** `selfdestruct` will not be available after EIP-4758. This EIP will rename the SELFDESTRUCT opcode and replace its functionality.

**Remediation.** Do not use `selfdestruct` to ensure the contract works in the future.

**References.**
- <https://eips.ethereum.org/EIPS/eip-4758>
- <https://solodit.xyz/issues/m-09-selfdestruct-will-not-be-available-after-eip-4758-code4rena-escher-escher-contest-git>
- <https://solodit.xyz/issues/m-03-system-will-not-work-anymore-after-eip-4758-code4rena-axelar-network-axelar-network-git>

### SOL-Basics-VI-OVI-1

**Question.** Does the contract use `ERC2771Context`? (version >=4.0.0 <4.9.3)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** `ERC2771Context._msgData()` reverts if `msg.data.length < 20`. The correct behavior is not specified in ERC-2771, but based on the specified behavior of `_msgSender` we assume the full `msg.data` should be returned in this case.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-2

**Question.** Does the contract use OpenZeppelin's GovernorCompatibilityBravo? (version >=4.3.0 <4.8.3)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** GovernorCompatibilityBravo may trim proposal calldata. The proposal creation entrypoint (propose) in GovernorCompatibilityBravo allows the creation of proposals with a signatures array shorter than the calldatas array. This causes the additional elements of the latter to be ignored, and if the proposal succeeds the corresponding actions would eventually execute without any calldata. The ProposalCreated event correctly represents what will eventually execute, but the proposal parameters as queried through getActions appear to respect the original intended calldata.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-3

**Question.** Does the contract use OpenZeppelin's ECDSA.recover or ECDSA.tryRecover? (version <4.7.3)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** ECDSA signature malleability. The functions ECDSA.recover and ECDSA.tryRecover are vulnerable to a kind of signature malleability due to accepting EIP-2098 compact signatures in addition to the traditional 65 byte signature format. This is only an issue for the functions that take a single bytes argument, and not the functions that take r, v, s or r, vs as separate arguments. The potentially affected contracts are those that implement signature reuse or replay protection by marking the signature itself as used rather than the signed message or a nonce included in it. A user may take a signature that has already been submitted, submit it again in a different form, and bypass this protection.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-4

**Question.** Does the contract use OpenZeppelin's ERC777? (version <3.4.0-rc.0)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** Extending this contract with a custom _beforeTokenTransfer function could allow a reentrancy attack to happen. More specifically, when burning tokens, _beforeTokenTransfer is invoked before the send hook is externally called on the sender while token balances are adjusted afterwards. At the moment of the call to the sender, which can result in reentrancy, state managed by _beforeTokenTransfer may not correspond to the actual token balances or total supply.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-5

**Question.** Does the contract use OpenZeppelin's `MerkleProof`? (version >=4.7.0 <4.9.2)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** When the `verifyMultiProof`, `verifyMultiProofCalldata`, `processMultiProof`, or `processMultiProofCalldata` functions are in use, it is possible to construct merkle trees that allow forging a valid multiproof for an arbitrary set of leaves.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-6

**Question.** Does the contract use OpenZeppelin's Governor or GovernorCompatibilityBravo? (version >=4.3.0 <4.9.1)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** Governor proposal creation may be blocked by frontrunning. By frontrunning the creation of a proposal, an attacker can become the proposer and gain the ability to cancel it. The attacker can do this repeatedly to try to prevent a proposal from being proposed at all. This impacts the Governor contract in v4.9.0 only, and the GovernorCompatibilityBravo contract since v4.3.0.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-7

**Question.** Does the contract use OpenZeppelin's TransparentUpgradeableProxy? (version >=3.2.0 <4.8.3)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** Transparency is broken in case of selector clash with non-decodable calldata. The TransparentUpgradeableProxy uses the ifAdmin modifier to achieve transparency. If a non-admin address calls the proxy the call should be frowarded transparently. This works well in most cases, but the forwarding of some functions can fail if there is a selector conflict and decoding issue.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-8

**Question.** Does the contract use OpenZeppelin's ERC721Consecutive?(version >=4.8.0 <4.8.2)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** The ERC721Consecutive contract designed for minting NFTs in batches does not update balances when a batch has size 1 and consists of a single token. Subsequent transfers from the receiver of that token may overflow the balance as reported by balanceOf. The issue exclusively presents with batches of size 1.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-9

**Question.** Does the contract use OpenZeppelin's ERC165Checker or ERC165CheckerUpgradeable? (version >=2.3.0 <4.7.2)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** Denial of Service (DoS) in the `supportsERC165InterfaceUnchecked()` function in `ERC165Checker.sol` and `ERC165CheckerUpgradeable.sol`, which can consume excessive resources when processing a large amount of data via an EIP-165 supportsInterface query.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-10

**Question.** Does the contract use OpenZeppelin's LibArbitrumL2 or CrossChainEnabledArbitrumL2? (version >=4.6.0 <4.7.2)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** Incorrect resource transfer between spheres via contracts using the cross-chain utilities for Arbitrum L2: `CrossChainEnabledArbitrumL2` or `LibArbitrumL2`. Calls from EOAs would be classified as cross-chain calls. The vulnerability will classify direct interactions of externally owned accounts (EOAs) as cross-chain calls, even though they are not started on L1.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-11

**Question.** Does the contract use OpenZeppelin's GovernorVotesQuorumFraction? (version >=4.3.0 <4.7.2)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** Checkpointing quorum was missing and past proposals that failed due to lack of quorum could pass later. It is necessary to avoid quorum changes making old, failed because of quorum, proposals suddenly successful.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-12

**Question.** Does the contract use OpenZeppelin's SignatureChecker? (version >=4.1.0 <4.7.1)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** Since 0.8.0, abi.decode reverts if the bytes raw data overflow the target type. SignatureChecker.isValidSignatureNow is not expected to revert. However, an incorrect assumption about Solidity 0.8's abi.decode allows some cases to revert, given a target contract that doesn't implement EIP-1271 as expected. The contracts that may be affected are those that use SignatureChecker to check the validity of a signature and handle invalid signatures in a way other than reverting.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-13

**Question.** Does the contract use OpenZeppelin's ERC165Checker? (version >=4.0.0 <4.7.1)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** Since 0.8.0, abi.decode reverts if the bytes raw data overflow the target type. ERC165Checker.supportsInterface is designed to always successfully return a boolean, and under no circumstance revert. However, an incorrect assumption about Solidity 0.8's abi.decode allows some cases to revert, given a target contract that doesn't implement EIP-165 as expected, specifically if it returns a value other than 0 or 1. The contracts that may be affected are those that use ERC165Checker to check for support for an interface and then handle the lack of support in a way other than reverting.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-14

**Question.** Does the contract use OpenZeppelin's GovernorCompatibilityBravo? (version >=4.3.0 <4.4.2)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** GovernorCompatibilityBravo incorrect ABI encoding may lead to unexpected behavior

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-15

**Question.** Does the contract use OpenZeppelin's Initializable? (version >=3.2.0 <4.4.1)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** It is possible for `initializer()`-protected functions to be executed twice, if this happens in the same transaction. For this to happen, either one call has to be a subcall the other, or both call have to be subcalls of a common initializer()-protected function. This can particularly be dangerous is the initialization is not part of the proxy construction, and reentrancy is possible by executing an external call to an untrusted address.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-16

**Question.** Does the contract use OpenZeppelin's ERC1155? (version >=4.2.0 <4.3.3)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** Possible inconsistency in the value returned by totalSupply DURING a mint. If you mint a token, the receiver is a smart contract, and the receiver implements onERC1155Receive, then this receiver is called with the balance already updated, but with the totalsupply not yet updated.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-17

**Question.** Does the contract use OpenZeppelin's UUPSUpgradeable? (version >=4.1.0 <4.3.2)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** Upgradeable contracts using UUPSUpgradeable may be vulnerable to an attack affecting uninitialized implementation contracts.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-OVI-18

**Question.** Does the contract use OpenZeppelin's TimelockController? (version >=4.0.0-beta.0 <4.3.1\\n<3.4.2)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › OpenZeppelin Version Issues*

**Description.** A vulnerability in TimelockController allowed an actor with the executor role to take immediate control of the timelock, by resetting the delay to 0 and escalating privileges, thus gaining unrestricted access to assets held in the contract. Instances with the executor role set to 'open' allow anyone to use the executor role, thus leaving the timelock at risk of being taken over by an attacker.

**Remediation.** Use the latest stable OpenZeppelin version

### SOL-Basics-VI-SVI-1

**Question.** Does the contract encode storage structs or arrays with types under 32 bytes directly using experimental ABIEncoderV2? (version 0.5.0~0.5.6)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Storage structs and arrays with types shorter than 32 bytes can cause data corruption if encoded directly from storage using the experimental ABIEncoderV2.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2019/03/26/solidity-optimizer-and-abiencoderv2-bug/>

### SOL-Basics-VI-SVI-2

**Question.** Are there any instances where empty strings are directly passed to function calls? (version ~0.4.11)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** If an empty string is used in a function call, the following function arguments will not be correctly passed to the function.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-3

**Question.** Does the optimizer replace specific constants with alternative computations? (version ~0.4.10)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** In some situations, the optimizer replaces certain numbers in the code with routines that compute different numbers.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2017/05/03/solidity-optimizer-bug/>

### SOL-Basics-VI-SVI-4

**Question.** Does the contract use `abi.encodePacked`, especially in hash generation? (version >= 0.8.17)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** If you use `keccak256(abi.encodePacked(a, b))` and both `a` and `b` are dynamic types, it is easy to craft collisions in the hash value by moving parts of `a` into `b` and vice-versa. More specifically, `abi.encodePacked(\'a\', \'bc\') == abi.encodePacked(\'ab\', \'c\').

**Remediation.** Use `abi.encode` instead of `abi.encodePacked`.

**References.**
- <https://solodit.xyz/issues/m-1-abiencodepacked-allows-hash-collision-sherlock-nftport-nftport-git>
- <https://docs.soliditylang.org/en/v0.8.17/abi-spec.html?highlight=collisions#non-standard-packed-mode>

### SOL-Basics-VI-SVI-5

**Question.** BUILD: Is the contract optimized using sequences containing FullInliner with non-expression-split code? (version 0.6.7~0.8.20)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Optimizer sequences containing FullInliner do not preserve the evaluation order of arguments of inlined function calls in code that is not in expression-split form.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2023/07/19/full-inliner-non-expression-split-argument-evaluation-order-bug/>

### SOL-Basics-VI-SVI-6

**Question.** Are there any functions that conditionally terminate inside an inline assembly? (version 0.8.13~0.8.16)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Calling functions that conditionally terminate the external EVM call using the assembly statements ``return(...)`` or ``stop()`` may result in incorrect removals of prior storage writes.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2022/09/08/storage-write-removal-before-conditional-termination/>

### SOL-Basics-VI-SVI-7

**Question.** Are tuples containing a statically-sized calldata array at the end being ABI-encoded? (version 0.5.8~0.8.15)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** ABI-encoding a tuple with a statically-sized calldata array in the last component would corrupt 32 leading bytes of its first dynamically encoded component.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2022/08/08/calldata-tuple-reencoding-head-overflow-bug/>

### SOL-Basics-VI-SVI-8

**Question.** Does the contract have functions that copy `bytes` arrays from memory or calldata directly to storage? (version 0.0.1~0.8.14)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Copying ``bytes`` arrays from memory or calldata to storage may result in dirty storage values.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2022/06/15/dirty-bytes-array-to-storage-bug/>

### SOL-Basics-VI-SVI-9

**Question.** Is there a function with multiple inline assembly blocks? (version 0.8.13~0.8.14)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** The Yul optimizer may incorrectly remove memory writes from inline assembly blocks, that do not access solidity variables.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2022/06/15/inline-assembly-memory-side-effects-bug/>

### SOL-Basics-VI-SVI-10

**Question.** Is a nested array being ABI-encoded or passed directly to an external function? (version 0.5.8~0.8.13)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** ABI-reencoding of nested dynamic calldata arrays did not always perform proper size checks against the size of calldata and could read beyond `calldatasize()`.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2022/05/17/calldata-reencode-size-check-bug/>

### SOL-Basics-VI-SVI-11

**Question.** Is `abi.encodeCall` used together with fixed-length bytes literals? (version 0.8.11~0.8.12)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Literals used for a fixed length bytes parameter in ``abi.encodeCall`` were encoded incorrectly.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2022/03/16/encodecall-bug/>

### SOL-Basics-VI-SVI-12

**Question.** Is there any user defined types based on types shorter than 32 bytes? (version =0.8.8)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** User defined value types with underlying type shorter than 32 bytes used incorrect storage layout and wasted storage

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2021/09/29/user-defined-value-types-bug/>

### SOL-Basics-VI-SVI-13

**Question.** Is there an immutable variable of signed integer type shorter than 256 bits? (version 0.6.5~0.8.8)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Immutable variables of signed integer type shorter than 256 bits can lead to values with invalid higher order bits if inline assembly is used.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2021/09/29/signed-immutables-bug/>

### SOL-Basics-VI-SVI-14

**Question.** Is there any use of `abi.encode` on memory with multi-dimensional array or structs? (version 0.4.16~0.8.3)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** If used on memory byte arrays, result of the function ``abi.decode`` can depend on the contents of memory outside of the actual byte array that is decoded.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2021/04/21/decoding-from-memory-bug/>

### SOL-Basics-VI-SVI-15

**Question.** Is there an inline assembly block with `keccak256` inside? (version ~0.8.2)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** The bytecode optimizer incorrectly re-used previously evaluated Keccak-256 hashes. You are unlikely to be affected if you do not compute Keccak-256 hashes in inline assembly.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2021/03/23/keccak-optimizer-bug/>

### SOL-Basics-VI-SVI-16

**Question.** Is there a copy of an empty `bytes` or `string` from `memory` or `calldata` to `storage`? (version ~0.7.3)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Copying an empty byte array (or string) from memory or calldata to storage can result in data corruption if the target array's length is increased subsequently without storing new data.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2020/10/19/empty-byte-array-copy-bug/>

### SOL-Basics-VI-SVI-17

**Question.** Is there a dynamically-sized storage-array with types of size at most 16 bytes? (version ~0.7.2)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** When assigning a dynamically-sized array with types of size at most 16 bytes in storage causing the assigned array to shrink, some parts of deleted slots were not zeroed out.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2020/10/07/solidity-dynamic-array-cleanup-bug/>

### SOL-Basics-VI-SVI-18

**Question.** Does the library use contract types in events? (version 0.5.0~0.5.7)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Contract types used in events in libraries cause an incorrect event signature hash

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-19

**Question.** Does the contract use internal library functions with calldata parameters via `using for`? (version =0.6.9)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Function calls to internal library functions with calldata parameters called via ``using for`` can result in invalid data being read.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-20

**Question.** Are string literals with double backslashes passed directly to external or encoding functions with ABIEncoderV2 enabled? (version 0.5.14~0.6.7)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** String literals containing double backslash characters passed directly to external or encoding function calls can lead to a different string being used when ABIEncoderV2 is enabled.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-21

**Question.** Does the contract access slices of dynamic arrays, especially multi-dimensional ones? (version 0.6.0~0.6.7)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Accessing array slices of arrays with dynamically encoded base types (e.g. multi-dimensional arrays) can result in invalid data being read.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-22

**Question.** Is there a contract with creation code, no constructor, but a base with a constructor that accepts non-zero values? (version 0.4.5~0.6.7)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** The creation code of a contract that does not define a constructor but has a base that does define a constructor did not revert for calls with non-zero value.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-23

**Question.** Does the contract create extremely large memory arrays? (version 0.2.0~0.6.4)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** The creation of very large memory arrays can result in overlapping memory regions and thus memory corruption.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2020/04/06/memory-creation-overflow-bug/>

### SOL-Basics-VI-SVI-24

**Question.** Does the contract's inline assembly with Yul optimizer use assignments inside for loops combined with continue or break? (version =0.6.0)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** The Yul optimizer can remove essential assignments to variables declared inside for loops when Yul's continue or break statement is used. You are unlikely to be affected if you do not use inline assembly with for loops and continue and break statements.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-25

**Question.** Does the contract allow private methods to be overridden by inheriting contracts? (version 0.3.0~0.5.16)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Private methods can be overridden by inheriting contracts.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-26

**Question.** Is there any Yul's continue or break statement inside the loop?? (version 0.5.8~0.5.15)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** The Yul optimizer can remove essential assignments to variables declared inside for loops when Yul's continue or break statement is used. You are unlikely to be affected if you do not use inline assembly with for loops and continue and break statements.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-27

**Question.** Are both experimental ABIEncoderV2 and Yul optimizer activated? (version =0.5.14)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** If both the experimental ABIEncoderV2 and the experimental Yul optimizer are activated, one component of the Yul optimizer may reuse data in memory that has been changed in the meantime.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-28

**Question.** Does the contract read from calldata structs with dynamic yet statically-sized members? (version 0.5.6~0.5.10)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Reading from calldata structs that contain dynamically encoded, but statically-sized members can result in incorrect values.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-29

**Question.** Does the contract assign arrays of signed integers to differently typed storage arrays? (version 0.4.7~0.5.9)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Assigning an array of signed integers to a storage array of different type can lead to data corruption in that array.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2019/06/25/solidity-storage-array-bugs/>

### SOL-Basics-VI-SVI-30

**Question.** Does the contract directly encode storage arrays with structs or static arrays in external calls or abi.encode*? (version 0.4.16~0.5.9)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Storage arrays containing structs or other statically-sized arrays are not read properly when directly encoded in external function calls or in abi.encode*.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2019/06/25/solidity-storage-array-bugs/>

### SOL-Basics-VI-SVI-31

**Question.** Does the contract's constructor accept structs or arrays with dynamic arrays? (version 0.4.16~0.5.8)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** A contract's constructor that takes structs or arrays that contain dynamically-sized arrays reverts or decodes to invalid data.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-32

**Question.** Are uninitialized internal function pointers created in the constructor being called? (version 0.5.0~0.5.7)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Calling uninitialized internal function pointers created in the constructor does not always revert and can cause unexpected behavior.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-33

**Question.** Are uninitialized internal function pointers created in the constructor being called? (version 0.4.5~0.4.25)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Calling uninitialized internal function pointers created in the constructor does not always revert and can cause unexpected behavior.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-34

**Question.** Does the library use contract types in events? (version 0.3.0~0.4.25)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Contract types used in events in libraries cause an incorrect event signature hash

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-35

**Question.** Does the contract encode storage structs or arrays with types under 32 bytes directly using experimental ABIEncoderV2? (version 0.4.19~0.4.25)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Storage structs and arrays with types shorter than 32 bytes can cause data corruption if encoded directly from storage using the experimental ABIEncoderV2.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2019/03/26/solidity-optimizer-and-abiencoderv2-bug/>

### SOL-Basics-VI-SVI-36

**Question.** Does the contract's optimizer handle byte opcodes with a second argument of 31 or an equivalent constant expression? (version 0.5.5~0.5.6)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** The optimizer incorrectly handles byte opcodes whose second argument is 31 or a constant expression that evaluates to 31. This can result in unexpected values.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2019/03/26/solidity-optimizer-and-abiencoderv2-bug/>

### SOL-Basics-VI-SVI-37

**Question.** Are there double bitwise shifts with large constants that might sum up to overflow 256 bits? (version =0.5.5)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Double bitwise shifts by large constants whose sum overflows 256 bits can result in unexpected values.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2019/03/26/solidity-optimizer-and-abiencoderv2-bug/>

### SOL-Basics-VI-SVI-38

**Question.** Is the ** operator used with an exponent type shorter than 256 bits? (version ~0.4.24)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Using the ** operator with an exponent of type shorter than 256 bits can result in unexpected values.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2018/09/13/solidity-bugfix-release/>

### SOL-Basics-VI-SVI-39

**Question.** Are structs used in the logged events? (version 0.4.17~0.4.24)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Using structs in events logged wrong data.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2018/09/13/solidity-bugfix-release/>

### SOL-Basics-VI-SVI-40

**Question.** Are functions returning multi-dimensional fixed-size arrays called? (version 0.1.4~0.4.21)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Calling functions that return multi-dimensional fixed-size arrays can result in memory corruption.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2018/09/13/solidity-bugfix-release/>

### SOL-Basics-VI-SVI-41

**Question.** Does the contract use both new-style and old-style constructors simultaneously? (version =0.4.22)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** If a contract has both a new-style constructor (using the constructor keyword) and an old-style constructor (a function with the same name as the contract) at the same time, one of them will be ignored.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-42

**Question.** Is there a function name crafted to potentially override the fallback function execution? (version ~0.4.17)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** It is possible to craft the name of a function such that it is executed instead of the fallback function in very specific circumstances.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-43

**Question.** Is the low-level .delegatecall() used without checking the actual execution outcome? (version 0.3.0~0.4.14)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** The low-level .delegatecall() does not return the execution outcome, but converts the value returned by the functioned called to a boolean instead.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-44

**Question.** Is the ecrecover() function used without validating its input? (version ~0.4.13)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** The ecrecover() builtin can return garbage for malformed input.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-45

**Question.** Is the `.selector` member accessed on complex expressions? (version 0.6.2~0.8.20)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Accessing the ``.selector`` member on complex expressions leaves the expression unevaluated in the legacy code generation.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2023/07/19/missing-side-effects-on-selector-access-bug/>

### SOL-Basics-VI-SVI-46

**Question.** Is there any inconsistency (`memory` vs `calldata`) in the param type during inheritance? (version 0.6.9~0.8.13)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** It was possible to change the data location of the parameters or return variables from ``calldata`` to ``memory`` and vice-versa while overriding internal and public functions. This caused invalid code to be generated when calling such a function internally through virtual function calls.

**Remediation.** Use the latest Solidity version.

**References.**
- <https://blog.soliditylang.org/2022/05/17/data-location-inheritance-bug/>

### SOL-Basics-VI-SVI-47

**Question.** Are there any functions with the same name and parameter type inside the same contract? (version =0.7.1)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** The compiler does not flag an error when two or more free functions with the same name and parameter types are defined in a source unit or when an imported free function alias shadows another free function with a different name but identical parameter types.

**Remediation.** Use the latest Solidity version.

### SOL-Basics-VI-SVI-48

**Question.** Does the contract use tuple assignments with multi-stack-slot components, like nested tuples or dynamic calldata references? (version 0.1.6~0.6.5)

Source: Cyfrin / Solodit · upstream path: *Basics › Version Issues › Solidity Version Issues*

**Description.** Tuple assignments with components that occupy several stack slots, i.e. nested tuples, pointers to external functions or references to dynamically sized calldata arrays, can result in invalid values.

**Remediation.** Use the latest Solidity version.
