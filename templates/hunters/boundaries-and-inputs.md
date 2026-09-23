# Hunter brief — Inputs, cross-chain boundaries & hygiene

<!-- GENERATED FILE. Do not edit by hand.
     Sources: methodology/checklist-map.json (SmartCon core questions and placement rules)
              methodology/upstream/cyfrin-audit-checklist.json (Cyfrin / Solodit items)
              knowledge-base/case-studies/*.md (post-mortems citing checklist items)
     Regenerate: python3 tools/build-checklist.py -->

## Role

You are one of 6 parallel reviewers in SmartCon **Phase 4 (manual deep review)**. You own 3 checklist categories: **17. Input Validation & Uninitialized State**, **15. Bridges & Cross-Chain**, **12. General Solidity Hygiene**. The other hunters own the rest (Callbacks, reentrancy & liveness: 1, 9, 16; Accounting & math: 3, 6; Tokens & price sources: 10, 4; Privilege, upgrades, governance & signatures: 2, 7, 14, 8; Atomic capital, ordering & randomness: 5, 11, 13); do not spend time on their categories except to hand them a lead. You read and reason; you do not modify the target, you do not fix anything, and you never run an exploit against a live deployment.

**Focus.** Every parameter, callback caller and decoded payload the contract trusts; arbitrary external calls built from user input; zero and default values treated as valid; cross-chain messages and their binding to source, destination, payload and validator set; and the compiler / library versions in use (Appendix A).

**Start with.**

1. For every external/public function, list each parameter and how it is validated (zero, range, length equality, whitelist, caller identity).
2. Find every place a user-supplied address is called or a user-supplied calldata is forwarded, and every callback whose msg.sender is not checked against the contract just called.
3. Record pragma and library versions and walk only the Appendix A rows whose range matches.

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

### 17. Input Validation & Uninitialized State

Notes: [`knowledge-base/vulnerabilities/input-validation.md`](../../knowledge-base/vulnerabilities/input-validation.md) · Case studies: [2023-04-09 SushiSwap `RouteProcessor2` router (>$3.3M)](../../knowledge-base/case-studies/2023-04-09-sushiswap-routeprocessor2-unverified-callback.md), [2022-08-01 Nomad token bridge (~$190M)](../../knowledge-base/case-studies/2022-08-01-nomad-bridge-zero-root-accepted.md), [2022-01-27 Qubit Finance QBridge (~$80M)](../../knowledge-base/case-studies/2022-01-27-qubit-finance-codeless-address-call.md)

**Core**

- **[SC-INPUT-1](../../methodology/checklist-reference.md#sc-input-1)** Zero-address checks on setters and transfers?
- **[SC-INPUT-2](../../methodology/checklist-reference.md#sc-input-2)** Zero-amount / dust edge cases handled without corrupting accounting?
- **[SC-INPUT-3](../../methodology/checklist-reference.md#sc-input-3)** Array-length equality checked in batch functions?
- **[SC-INPUT-4](../../methodology/checklist-reference.md#sc-input-4)** Every critical variable initialized before use; parameters range-checked?
- **[SC-INPUT-5](../../methodology/checklist-reference.md#sc-input-5)** Do callbacks (flash-loan, Uniswap `swap`/`mint`, ERC-721 receiver) verify `msg.sender` is the expected pool/lender and that the initiator is this contract?
- **[SC-INPUT-6](../../methodology/checklist-reference.md#sc-input-6)** Can user-supplied addresses or calldata make the contract perform an arbitrary external call (router, target, token), including `transferFrom` against other users' approvals?
- **[SC-INPUT-7](../../methodology/checklist-reference.md#sc-input-7)** Does any mapping lookup treat the zero/default value (`bytes32(0)`, `address(0)`, `0`) as valid or "confirmed"?

**Extended (Cyfrin / Solodit)**

- **[SOL-Basics-AL-5](../../methodology/checklist-reference.md#sol-basics-al-5)** Does any function get an index of an array as an argument?
- **[SOL-Basics-AL-7](../../methodology/checklist-reference.md#sol-basics-al-7)** Is it fine to have duplicate items in the array?
- **[SOL-Basics-AL-11](../../methodology/checklist-reference.md#sol-basics-al-11)** Is `msg.value` used within a loop?
- **[SOL-Basics-Function-1](../../methodology/checklist-reference.md#sol-basics-function-1)** Are the inputs validated?
- **[SOL-Basics-Function-2](../../methodology/checklist-reference.md#sol-basics-function-2)** Are the outputs validated?
- **[SOL-Basics-Function-5](../../methodology/checklist-reference.md#sol-basics-function-5)** Can edge case inputs (0, max) result in unexpected behavior?
- **[SOL-Basics-Function-6](../../methodology/checklist-reference.md#sol-basics-function-6)** Does the function allow arbitrary user input?
- **[SOL-Basics-Initialization-1](../../methodology/checklist-reference.md#sol-basics-initialization-1)** Are important state variables initialized properly?
- **[SOL-Basics-Payment-2](../../methodology/checklist-reference.md#sol-basics-payment-2)** Does the function gets the payment amount as a parameter?
- **[SOL-Defi-AS-6](../../methodology/checklist-reference.md#sol-defi-as-6)** Can arbitrary calls be made from user input?
- **[SOL-Defi-AS-12](../../methodology/checklist-reference.md#sol-defi-as-12)** Does the integrating contract verify the caller address in its callback functions?
- **[SOL-EC-2](../../methodology/checklist-reference.md#sol-ec-2)** Is there a multi-call?
- **[SOL-EC-5](../../methodology/checklist-reference.md#sol-ec-5)** Has the called address been whitelisted?
- **[SOL-Heuristics-3](../../methodology/checklist-reference.md#sol-heuristics-3)** Is there any unexpected behavior when `src==dst` (or `caller==receiver`)?
- **[SOL-Heuristics-9](../../methodology/checklist-reference.md#sol-heuristics-9)** What happens if the protocol's contracts are inputted as if they are normal actors?
- **[SOL-Heuristics-11](../../methodology/checklist-reference.md#sol-heuristics-11)** Is there any uninitialized state?
- **[SOL-Integrations-Uniswap-4](../../methodology/checklist-reference.md#sol-integrations-uniswap-4)** Are the pools that are being interacted with whitelisted?
- **[SOL-Integrations-Uniswap-6](../../methodology/checklist-reference.md#sol-integrations-uniswap-6)** Is `pool.swap()` directly used?

### 15. Bridges & Cross-Chain

Notes: [`knowledge-base/vulnerabilities/bridges-cross-chain.md`](../../knowledge-base/vulnerabilities/bridges-cross-chain.md) · Case studies: [2022-08-01 Nomad token bridge (~$190M)](../../knowledge-base/case-studies/2022-08-01-nomad-bridge-zero-root-accepted.md), [2022-01-27 Qubit Finance QBridge (~$80M)](../../knowledge-base/case-studies/2022-01-27-qubit-finance-codeless-address-call.md), [2021-08-10 Poly Network (~$611M)](../../knowledge-base/case-studies/2021-08-10-poly-network-cross-chain-keeper-swap.md)

**Core**

- **[SC-BRIDGE-1](../../methodology/checklist-reference.md#sc-bridge-1)** Is the cross-chain message verified against the correct validator set/threshold?
- **[SC-BRIDGE-2](../../methodology/checklist-reference.md#sc-bridge-2)** Is a unique nonce / message id consumed to prevent replay?
- **[SC-BRIDGE-3](../../methodology/checklist-reference.md#sc-bridge-3)** Is the message bound to source chain, destination, and exact payload?
- **[SC-BRIDGE-4](../../methodology/checklist-reference.md#sc-bridge-4)** Are bridge init/upgrade paths tightly guarded? (Nomad/Wormhole/Ronin class)
- **[SC-BRIDGE-5](../../methodology/checklist-reference.md#sc-bridge-5)** Can a cross-chain message target a privileged contract of the bridge itself (config, keeper or validator-set contract) and pass its `onlyOwner` check because the executor is the owner?
- **[SC-BRIDGE-6](../../methodology/checklist-reference.md#sc-bridge-6)** Is the zero/default value of a trusted-root, confirmation or nonce mapping treated as valid or "confirmed"?

**Extended (Cyfrin / Solodit)**

- **[SOL-Integrations-Chainlink-CCIP-1](../../methodology/checklist-reference.md#sol-integrations-chainlink-ccip-1)** Does the receiver contract's `_ccipReceive` function properly validate the `sourceChainSelector` and `sender` address against an allowlist?
- **[SOL-Integrations-Chainlink-CCIP-2](../../methodology/checklist-reference.md#sol-integrations-chainlink-ccip-2)** Does the sender contract validate the `destinationChainSelector` against an allowlist before calling `ccipSend`?
- **[SOL-Integrations-Chainlink-CCIP-3](../../methodology/checklist-reference.md#sol-integrations-chainlink-ccip-3)** Does the receiver contract properly decode data (`any2EvmMessage.data`) ?
- **[SOL-Integrations-Chainlink-CCIP-4](../../methodology/checklist-reference.md#sol-integrations-chainlink-ccip-4)** Does the application logic account for the potential latency introduced by waiting for source chain finality as defined by CCIP?
- **[SOL-Integrations-Chainlink-CCIP-5](../../methodology/checklist-reference.md#sol-integrations-chainlink-ccip-5)** Are the correct types of token pools (e.g., `BurnMintTokenPool`, `LockReleaseTokenPool`) deployed on the source and destination chains consistent with the desired token handling mechanism?
- **[SOL-Integrations-Chainlink-CCIP-6](../../methodology/checklist-reference.md#sol-integrations-chainlink-ccip-6)** Is proper router address verification implemented in the ccipReceive method?
- **[SOL-Integrations-Chainlink-CCIP-7](../../methodology/checklist-reference.md#sol-integrations-chainlink-ccip-7)** Are extraArgs parameters hardcoded instead of mutable in cross-chain message configurations?
- **[SOL-Integrations-Chainlink-CCIP-8](../../methodology/checklist-reference.md#sol-integrations-chainlink-ccip-8)** Is there a proper failure handling mechanism for CCIP messages to prevent blocking after Smart Execution window expiration?
- **[SOL-Integrations-LayerZero-1](../../methodology/checklist-reference.md#sol-integrations-layerzero-1)** Does the `_debitFrom` function in ONFT properly validate token ownership and transfer permissions?
- **[SOL-Integrations-LayerZero-2](../../methodology/checklist-reference.md#sol-integrations-layerzero-2)** Which type of mechanism are utilized? Blocking or non-blocking?
- **[SOL-Integrations-LayerZero-3](../../methodology/checklist-reference.md#sol-integrations-layerzero-3)** Is gas estimated accurately for cross-chain messages?
- **[SOL-Integrations-LayerZero-4](../../methodology/checklist-reference.md#sol-integrations-layerzero-4)** Is the `_lzSend` function correctly utilized when inheriting LzApp?
- **[SOL-Integrations-LayerZero-5](../../methodology/checklist-reference.md#sol-integrations-layerzero-5)** Is the `ILayerZeroUserApplicationConfig` interface correctly implemented?
- **[SOL-Integrations-LayerZero-6](../../methodology/checklist-reference.md#sol-integrations-layerzero-6)** Are default contracts used?
- **[SOL-Integrations-LayerZero-7](../../methodology/checklist-reference.md#sol-integrations-layerzero-7)** Is the correct number of confirmations chosen for the chain?
- **[SOL-Integrations-Uniswap-3](../../methodology/checklist-reference.md#sol-integrations-uniswap-3)** Is the order of `token0` and `token1` consistent across chains?
- **[SOL-McCc-1](../../methodology/checklist-reference.md#sol-mccc-1)** Are there assumption of consistency in the `block.number` or `block.timestamp` across chains?
- **[SOL-McCc-2](../../methodology/checklist-reference.md#sol-mccc-2)** Has the protocol been checked for the target chain differences?
- **[SOL-McCc-3](../../methodology/checklist-reference.md#sol-mccc-3)** Are the EVM opcodes and operations used by the protocol compatible across all targeted chains?
- **[SOL-McCc-4](../../methodology/checklist-reference.md#sol-mccc-4)** Does the expected behavior of `tx.origin` and `msg.sender` remain consistent across all deployment chains?
- **[SOL-McCc-5](../../methodology/checklist-reference.md#sol-mccc-5)** Is there any possibility of exploiting low gas fees to execute many transactions?
- **[SOL-McCc-6](../../methodology/checklist-reference.md#sol-mccc-6)** Is there consistency in ERC20 decimals across chains?
- **[SOL-McCc-7](../../methodology/checklist-reference.md#sol-mccc-7)** Have contract upgradability implications been evaluated on different chains?
- **[SOL-McCc-8](../../methodology/checklist-reference.md#sol-mccc-8)** Have cross-chain messaging implementations been thoroughly reviewed for permissions and functionality?
- **[SOL-McCc-9](../../methodology/checklist-reference.md#sol-mccc-9)** Is there a whitelist of compatible chains?
- **[SOL-McCc-10](../../methodology/checklist-reference.md#sol-mccc-10)** Have contracts been checked for compatibility when deployed to the zkSync Era?
- **[SOL-McCc-11](../../methodology/checklist-reference.md#sol-mccc-11)** Is block production consistency ensured?
- **[SOL-McCc-12](../../methodology/checklist-reference.md#sol-mccc-12)** Is `PUSH0` opcode supported for Solidity version `>=0.8.20`?
- **[SOL-McCc-13](../../methodology/checklist-reference.md#sol-mccc-13)** Are there any attributes attached to the bridged assets?

### 12. General Solidity Hygiene

Case studies: [2021-04-28 Uranium Finance (~$50M)](../../knowledge-base/case-studies/2021-04-28-uranium-finance-k-constant-typo.md)

**Core**

- **[SC-HYG-1](../../methodology/checklist-reference.md#sc-hyg-1)** Uninitialized storage pointers; `delete` on structs with mappings.
- **[SC-HYG-2](../../methodology/checklist-reference.md#sc-hyg-2)** Correct handling of `address(this).balance` vs. accounting variables.
- **[SC-HYG-3](../../methodology/checklist-reference.md#sc-hyg-3)** Events emitted for every state change (for off-chain integrity)?
- **[SC-HYG-4](../../methodology/checklist-reference.md#sc-hyg-4)** Deprecated constructs (`selfdestruct`, `tx.origin`, `block.difficulty`) reviewed?
- **[SC-HYG-5](../../methodology/checklist-reference.md#sc-hyg-5)** Have the compiler version and library versions (OpenZeppelin, Solmate) been checked against Appendix A (known compiler and library bugs)?
- **[SC-HYG-6](../../methodology/checklist-reference.md#sc-hyg-6)** Forked or copied code: were constants, fee denominators and formulas diffed line by line against the upstream (Uniswap, Compound, OpenZeppelin) they came from?

**Extended (Cyfrin / Solodit)**

- **[SOL-Basics-AL-1](../../methodology/checklist-reference.md#sol-basics-al-1)** What happens on the first and the last cycle of the iteration?
- **[SOL-Basics-AL-4](../../methodology/checklist-reference.md#sol-basics-al-4)** How does the protocol remove an item from an array?
- **[SOL-Basics-AL-6](../../methodology/checklist-reference.md#sol-basics-al-6)** Is the summing of variables done accurately compared to separate calculations?
- **[SOL-Basics-AL-8](../../methodology/checklist-reference.md#sol-basics-al-8)** Is there any issue with the first and the last iteration?
- **[SOL-Basics-AL-13](../../methodology/checklist-reference.md#sol-basics-al-13)** Is there a break or continue inside a loop?
- **[SOL-Basics-Event-1](../../methodology/checklist-reference.md#sol-basics-event-1)** Does the protocol emit events on important state changes?
- **[SOL-Basics-Function-4](../../methodology/checklist-reference.md#sol-basics-function-4)** Are the code comments coherent with the implementation?
- **[SOL-Basics-Inheritance-2](../../methodology/checklist-reference.md#sol-basics-inheritance-2)** Were all necessary functions implemented to fulfill inheritance purpose?
- **[SOL-Basics-Inheritance-3](../../methodology/checklist-reference.md#sol-basics-inheritance-3)** Has the contract implemented an interface?
- **[SOL-Basics-Inheritance-4](../../methodology/checklist-reference.md#sol-basics-inheritance-4)** Does the inheritance order matter?
- **[SOL-Basics-Map-1](../../methodology/checklist-reference.md#sol-basics-map-1)** Is there need to delete the existing item from a map?
- **[SOL-Heuristics-1](../../methodology/checklist-reference.md#sol-heuristics-1)** Is there any logic implemented multiple times?
- **[SOL-Heuristics-2](../../methodology/checklist-reference.md#sol-heuristics-2)** Does the contract use any nested structures?
- **[SOL-Heuristics-6](../../methodology/checklist-reference.md#sol-heuristics-6)** Did you check the relevant EIP recommendations and security concerns?
- **[SOL-Heuristics-8](../../methodology/checklist-reference.md#sol-heuristics-8)** Are logical operators used correctly?
- **[SOL-Heuristics-13](../../methodology/checklist-reference.md#sol-heuristics-13)** Is the global state updated correctly?
- **[SOL-Heuristics-15](../../methodology/checklist-reference.md#sol-heuristics-15)** Does the protocol put any sensitive data on the blockchain?

### Appendix A. Version-specific issues (compiler and library bugs)

Checks that only apply to a specific Solidity compiler range or OpenZeppelin release. Read the target's `pragma` and lock-file first, then walk only the rows whose version range matches. Referenced from SC-HYG-5.

- **[SOL-Basics-VI-EAI-1](../../methodology/checklist-reference.md#sol-basics-vi-eai-1)** EIP-4758: Does the contract use `selfdestruct()`?
- **[SOL-Basics-VI-OVI-1](../../methodology/checklist-reference.md#sol-basics-vi-ovi-1)** Does the contract use `ERC2771Context`? (version >=4.0.0 <4.9.3)
- **[SOL-Basics-VI-OVI-2](../../methodology/checklist-reference.md#sol-basics-vi-ovi-2)** Does the contract use OpenZeppelin's GovernorCompatibilityBravo? (version >=4.3.0 <4.8.3)
- **[SOL-Basics-VI-OVI-3](../../methodology/checklist-reference.md#sol-basics-vi-ovi-3)** Does the contract use OpenZeppelin's ECDSA.recover or ECDSA.tryRecover? (version <4.7.3)
- **[SOL-Basics-VI-OVI-4](../../methodology/checklist-reference.md#sol-basics-vi-ovi-4)** Does the contract use OpenZeppelin's ERC777? (version <3.4.0-rc.0)
- **[SOL-Basics-VI-OVI-5](../../methodology/checklist-reference.md#sol-basics-vi-ovi-5)** Does the contract use OpenZeppelin's `MerkleProof`? (version >=4.7.0 <4.9.2)
- **[SOL-Basics-VI-OVI-6](../../methodology/checklist-reference.md#sol-basics-vi-ovi-6)** Does the contract use OpenZeppelin's Governor or GovernorCompatibilityBravo? (version >=4.3.0 <4.9.1)
- **[SOL-Basics-VI-OVI-7](../../methodology/checklist-reference.md#sol-basics-vi-ovi-7)** Does the contract use OpenZeppelin's TransparentUpgradeableProxy? (version >=3.2.0 <4.8.3)
- **[SOL-Basics-VI-OVI-8](../../methodology/checklist-reference.md#sol-basics-vi-ovi-8)** Does the contract use OpenZeppelin's ERC721Consecutive?(version >=4.8.0 <4.8.2)
- **[SOL-Basics-VI-OVI-9](../../methodology/checklist-reference.md#sol-basics-vi-ovi-9)** Does the contract use OpenZeppelin's ERC165Checker or ERC165CheckerUpgradeable? (version >=2.3.0 <4.7.2)
- **[SOL-Basics-VI-OVI-10](../../methodology/checklist-reference.md#sol-basics-vi-ovi-10)** Does the contract use OpenZeppelin's LibArbitrumL2 or CrossChainEnabledArbitrumL2? (version >=4.6.0 <4.7.2)
- **[SOL-Basics-VI-OVI-11](../../methodology/checklist-reference.md#sol-basics-vi-ovi-11)** Does the contract use OpenZeppelin's GovernorVotesQuorumFraction? (version >=4.3.0 <4.7.2)
- **[SOL-Basics-VI-OVI-12](../../methodology/checklist-reference.md#sol-basics-vi-ovi-12)** Does the contract use OpenZeppelin's SignatureChecker? (version >=4.1.0 <4.7.1)
- **[SOL-Basics-VI-OVI-13](../../methodology/checklist-reference.md#sol-basics-vi-ovi-13)** Does the contract use OpenZeppelin's ERC165Checker? (version >=4.0.0 <4.7.1)
- **[SOL-Basics-VI-OVI-14](../../methodology/checklist-reference.md#sol-basics-vi-ovi-14)** Does the contract use OpenZeppelin's GovernorCompatibilityBravo? (version >=4.3.0 <4.4.2)
- **[SOL-Basics-VI-OVI-15](../../methodology/checklist-reference.md#sol-basics-vi-ovi-15)** Does the contract use OpenZeppelin's Initializable? (version >=3.2.0 <4.4.1)
- **[SOL-Basics-VI-OVI-16](../../methodology/checklist-reference.md#sol-basics-vi-ovi-16)** Does the contract use OpenZeppelin's ERC1155? (version >=4.2.0 <4.3.3)
- **[SOL-Basics-VI-OVI-17](../../methodology/checklist-reference.md#sol-basics-vi-ovi-17)** Does the contract use OpenZeppelin's UUPSUpgradeable? (version >=4.1.0 <4.3.2)
- **[SOL-Basics-VI-OVI-18](../../methodology/checklist-reference.md#sol-basics-vi-ovi-18)** Does the contract use OpenZeppelin's TimelockController? (version >=4.0.0-beta.0 <4.3.1\\n<3.4.2)
- **[SOL-Basics-VI-SVI-1](../../methodology/checklist-reference.md#sol-basics-vi-svi-1)** Does the contract encode storage structs or arrays with types under 32 bytes directly using experimental ABIEncoderV2? (version 0.5.0~0.5.6)
- **[SOL-Basics-VI-SVI-2](../../methodology/checklist-reference.md#sol-basics-vi-svi-2)** Are there any instances where empty strings are directly passed to function calls? (version ~0.4.11)
- **[SOL-Basics-VI-SVI-3](../../methodology/checklist-reference.md#sol-basics-vi-svi-3)** Does the optimizer replace specific constants with alternative computations? (version ~0.4.10)
- **[SOL-Basics-VI-SVI-4](../../methodology/checklist-reference.md#sol-basics-vi-svi-4)** Does the contract use `abi.encodePacked`, especially in hash generation? (version >= 0.8.17)
- **[SOL-Basics-VI-SVI-5](../../methodology/checklist-reference.md#sol-basics-vi-svi-5)** BUILD: Is the contract optimized using sequences containing FullInliner with non-expression-split code? (version 0.6.7~0.8.20)
- **[SOL-Basics-VI-SVI-6](../../methodology/checklist-reference.md#sol-basics-vi-svi-6)** Are there any functions that conditionally terminate inside an inline assembly? (version 0.8.13~0.8.16)
- **[SOL-Basics-VI-SVI-7](../../methodology/checklist-reference.md#sol-basics-vi-svi-7)** Are tuples containing a statically-sized calldata array at the end being ABI-encoded? (version 0.5.8~0.8.15)
- **[SOL-Basics-VI-SVI-8](../../methodology/checklist-reference.md#sol-basics-vi-svi-8)** Does the contract have functions that copy `bytes` arrays from memory or calldata directly to storage? (version 0.0.1~0.8.14)
- **[SOL-Basics-VI-SVI-9](../../methodology/checklist-reference.md#sol-basics-vi-svi-9)** Is there a function with multiple inline assembly blocks? (version 0.8.13~0.8.14)
- **[SOL-Basics-VI-SVI-10](../../methodology/checklist-reference.md#sol-basics-vi-svi-10)** Is a nested array being ABI-encoded or passed directly to an external function? (version 0.5.8~0.8.13)
- **[SOL-Basics-VI-SVI-11](../../methodology/checklist-reference.md#sol-basics-vi-svi-11)** Is `abi.encodeCall` used together with fixed-length bytes literals? (version 0.8.11~0.8.12)
- **[SOL-Basics-VI-SVI-12](../../methodology/checklist-reference.md#sol-basics-vi-svi-12)** Is there any user defined types based on types shorter than 32 bytes? (version =0.8.8)
- **[SOL-Basics-VI-SVI-13](../../methodology/checklist-reference.md#sol-basics-vi-svi-13)** Is there an immutable variable of signed integer type shorter than 256 bits? (version 0.6.5~0.8.8)
- **[SOL-Basics-VI-SVI-14](../../methodology/checklist-reference.md#sol-basics-vi-svi-14)** Is there any use of `abi.encode` on memory with multi-dimensional array or structs? (version 0.4.16~0.8.3)
- **[SOL-Basics-VI-SVI-15](../../methodology/checklist-reference.md#sol-basics-vi-svi-15)** Is there an inline assembly block with `keccak256` inside? (version ~0.8.2)
- **[SOL-Basics-VI-SVI-16](../../methodology/checklist-reference.md#sol-basics-vi-svi-16)** Is there a copy of an empty `bytes` or `string` from `memory` or `calldata` to `storage`? (version ~0.7.3)
- **[SOL-Basics-VI-SVI-17](../../methodology/checklist-reference.md#sol-basics-vi-svi-17)** Is there a dynamically-sized storage-array with types of size at most 16 bytes? (version ~0.7.2)
- **[SOL-Basics-VI-SVI-18](../../methodology/checklist-reference.md#sol-basics-vi-svi-18)** Does the library use contract types in events? (version 0.5.0~0.5.7)
- **[SOL-Basics-VI-SVI-19](../../methodology/checklist-reference.md#sol-basics-vi-svi-19)** Does the contract use internal library functions with calldata parameters via `using for`? (version =0.6.9)
- **[SOL-Basics-VI-SVI-20](../../methodology/checklist-reference.md#sol-basics-vi-svi-20)** Are string literals with double backslashes passed directly to external or encoding functions with ABIEncoderV2 enabled? (version 0.5.14~0.6.7)
- **[SOL-Basics-VI-SVI-21](../../methodology/checklist-reference.md#sol-basics-vi-svi-21)** Does the contract access slices of dynamic arrays, especially multi-dimensional ones? (version 0.6.0~0.6.7)
- **[SOL-Basics-VI-SVI-22](../../methodology/checklist-reference.md#sol-basics-vi-svi-22)** Is there a contract with creation code, no constructor, but a base with a constructor that accepts non-zero values? (version 0.4.5~0.6.7)
- **[SOL-Basics-VI-SVI-23](../../methodology/checklist-reference.md#sol-basics-vi-svi-23)** Does the contract create extremely large memory arrays? (version 0.2.0~0.6.4)
- **[SOL-Basics-VI-SVI-24](../../methodology/checklist-reference.md#sol-basics-vi-svi-24)** Does the contract's inline assembly with Yul optimizer use assignments inside for loops combined with continue or break? (version =0.6.0)
- **[SOL-Basics-VI-SVI-25](../../methodology/checklist-reference.md#sol-basics-vi-svi-25)** Does the contract allow private methods to be overridden by inheriting contracts? (version 0.3.0~0.5.16)
- **[SOL-Basics-VI-SVI-26](../../methodology/checklist-reference.md#sol-basics-vi-svi-26)** Is there any Yul's continue or break statement inside the loop?? (version 0.5.8~0.5.15)
- **[SOL-Basics-VI-SVI-27](../../methodology/checklist-reference.md#sol-basics-vi-svi-27)** Are both experimental ABIEncoderV2 and Yul optimizer activated? (version =0.5.14)
- **[SOL-Basics-VI-SVI-28](../../methodology/checklist-reference.md#sol-basics-vi-svi-28)** Does the contract read from calldata structs with dynamic yet statically-sized members? (version 0.5.6~0.5.10)
- **[SOL-Basics-VI-SVI-29](../../methodology/checklist-reference.md#sol-basics-vi-svi-29)** Does the contract assign arrays of signed integers to differently typed storage arrays? (version 0.4.7~0.5.9)
- **[SOL-Basics-VI-SVI-30](../../methodology/checklist-reference.md#sol-basics-vi-svi-30)** Does the contract directly encode storage arrays with structs or static arrays in external calls or abi.encode*? (version 0.4.16~0.5.9)
- **[SOL-Basics-VI-SVI-31](../../methodology/checklist-reference.md#sol-basics-vi-svi-31)** Does the contract's constructor accept structs or arrays with dynamic arrays? (version 0.4.16~0.5.8)
- **[SOL-Basics-VI-SVI-32](../../methodology/checklist-reference.md#sol-basics-vi-svi-32)** Are uninitialized internal function pointers created in the constructor being called? (version 0.5.0~0.5.7)
- **[SOL-Basics-VI-SVI-33](../../methodology/checklist-reference.md#sol-basics-vi-svi-33)** Are uninitialized internal function pointers created in the constructor being called? (version 0.4.5~0.4.25)
- **[SOL-Basics-VI-SVI-34](../../methodology/checklist-reference.md#sol-basics-vi-svi-34)** Does the library use contract types in events? (version 0.3.0~0.4.25)
- **[SOL-Basics-VI-SVI-35](../../methodology/checklist-reference.md#sol-basics-vi-svi-35)** Does the contract encode storage structs or arrays with types under 32 bytes directly using experimental ABIEncoderV2? (version 0.4.19~0.4.25)
- **[SOL-Basics-VI-SVI-36](../../methodology/checklist-reference.md#sol-basics-vi-svi-36)** Does the contract's optimizer handle byte opcodes with a second argument of 31 or an equivalent constant expression? (version 0.5.5~0.5.6)
- **[SOL-Basics-VI-SVI-37](../../methodology/checklist-reference.md#sol-basics-vi-svi-37)** Are there double bitwise shifts with large constants that might sum up to overflow 256 bits? (version =0.5.5)
- **[SOL-Basics-VI-SVI-38](../../methodology/checklist-reference.md#sol-basics-vi-svi-38)** Is the ** operator used with an exponent type shorter than 256 bits? (version ~0.4.24)
- **[SOL-Basics-VI-SVI-39](../../methodology/checklist-reference.md#sol-basics-vi-svi-39)** Are structs used in the logged events? (version 0.4.17~0.4.24)
- **[SOL-Basics-VI-SVI-40](../../methodology/checklist-reference.md#sol-basics-vi-svi-40)** Are functions returning multi-dimensional fixed-size arrays called? (version 0.1.4~0.4.21)
- **[SOL-Basics-VI-SVI-41](../../methodology/checklist-reference.md#sol-basics-vi-svi-41)** Does the contract use both new-style and old-style constructors simultaneously? (version =0.4.22)
- **[SOL-Basics-VI-SVI-42](../../methodology/checklist-reference.md#sol-basics-vi-svi-42)** Is there a function name crafted to potentially override the fallback function execution? (version ~0.4.17)
- **[SOL-Basics-VI-SVI-43](../../methodology/checklist-reference.md#sol-basics-vi-svi-43)** Is the low-level .delegatecall() used without checking the actual execution outcome? (version 0.3.0~0.4.14)
- **[SOL-Basics-VI-SVI-44](../../methodology/checklist-reference.md#sol-basics-vi-svi-44)** Is the ecrecover() function used without validating its input? (version ~0.4.13)
- **[SOL-Basics-VI-SVI-45](../../methodology/checklist-reference.md#sol-basics-vi-svi-45)** Is the `.selector` member accessed on complex expressions? (version 0.6.2~0.8.20)
- **[SOL-Basics-VI-SVI-46](../../methodology/checklist-reference.md#sol-basics-vi-svi-46)** Is there any inconsistency (`memory` vs `calldata`) in the param type during inheritance? (version 0.6.9~0.8.13)
- **[SOL-Basics-VI-SVI-47](../../methodology/checklist-reference.md#sol-basics-vi-svi-47)** Are there any functions with the same name and parameter type inside the same contract? (version =0.7.1)
- **[SOL-Basics-VI-SVI-48](../../methodology/checklist-reference.md#sol-basics-vi-svi-48)** Does the contract use tuple assignments with multi-stack-slot components, like nested tuples or dynamic calldata references? (version 0.1.6~0.6.5)

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
