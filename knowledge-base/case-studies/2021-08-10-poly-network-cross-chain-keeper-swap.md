# Case Study: Poly Network — Cross-Chain Message Rewrites the Bridge's Own Keepers

## Summary
- **Protocol:** Poly Network (cross-chain interoperability bridge)
- **Date:** 2021-08-10
- **Chain:** Ethereum, BSC, Polygon
- **Loss:** ~$611M (almost entirely returned within ~2 weeks)
- **Vulnerability class:** [Bridges & Cross-Chain Messaging](../vulnerabilities/bridges-cross-chain.md)
- **Checklist categories:** bridges-cross-chain, access-control
- **Checklist items:** SC-BRIDGE-5, SC-BRIDGE-1, SC-BRIDGE-3, SC-AC-1, SOL-McCc-8
- **Root cause in one sentence:** `EthCrossChainManager.verifyHeaderAndExecuteTx` dispatches any cross-chain message to any contract, and because it (the manager) is the `onlyOwner` of the keeper-storage contract `EthCrossChainData`, the attacker aimed a message at that contract with a method string whose derived 4-byte selector collided with `putCurEpochConPubKeyBytes(bytes)`, replacing the bridge's consensus public keys with their own.
- **Attack tx:** https://etherscan.io/tx/0xb1f70464bd95b774c6ce60fc706eb5f9e35cb5f06e6cfe7c17dcda46ffd59581
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-08/PolyNetwork_exp.sol

## Background
Poly Network relays messages between chains. On Ethereum, `EthCrossChainManager` (ECCM)
verifies a Poly-chain block header and a Merkle proof that a cross-chain transaction was
included, then executes it by calling the target contract named in the message. The keeper
public keys that authorize headers are stored in a separate `EthCrossChainData` (ECCD)
contract, whose privileged setters are `onlyOwner`. Critically, the owner of ECCD is the
ECCM contract itself, so that legitimate cross-chain governance can rotate keepers. The
intended invariant: only a validly signed Poly-chain message can move funds, and only Poly
governance can change the keeper set. Both fall to one design flaw: the manager will target
*any* contract, including its own privileged data contract.

## The vulnerability
Verified against the Poly source at commit `d16252b2b8...`. After proof verification,
`verifyHeaderAndExecuteTx` resolves the target and calls `_executeCrossChainTx`, which
dynamically builds a selector from the message's `method` string:

```solidity
// EthCrossChainManager._executeCrossChainTx (verbatim)
require(Utils.isContract(_toContract), "The passed in address is not a contract!"); // only "is it a contract?"
(success, returnData) = _toContract.call(
    abi.encodePacked(
        bytes4(keccak256(abi.encodePacked(_method, "(bytes,bytes,uint64)"))), // selector from a STRING
        abi.encode(_args, _fromContractAddr, _fromChainId)));
```

```solidity
// EthCrossChainData setters are onlyOwner, and the owner is the ECCM contract
function putCurEpochConPubKeyBytes(bytes memory curEpochPkBytes)
    public whenNotPaused onlyOwner returns (bool) { ConKeepersPkBytes = curEpochPkBytes; return true; }
```

Two facts combine. (1) The only constraint on `_toContract` is that it is a contract
(SC-BRIDGE-5): the manager never forbids targeting ECCD or restricts to a whitelist of
business contracts. (2) The called selector is `keccak256(method + "(bytes,bytes,uint64)")`.
The attacker searched for a `method` string whose hash's first four bytes equal the selector
of `putCurEpochConPubKeyBytes(bytes)` (`0x41973cd9`); the PoC uses the method bytes
`f1121318093`. When the manager calls ECCD, ECCD sees `msg.sender == ECCM == owner`, so the
`onlyOwner` check passes (SC-AC-1), and the keeper keys are overwritten.

## The exploit, step by step
1. Craft a cross-chain message whose `toContract` is ECCD (`0xcF2afe10...`) and whose
   `method` is `f1121318093`, with `args` encoding the attacker's own keeper key set.
2. Submit it through `verifyHeaderAndExecuteTx`. Proof verification passes against the
   then-current keepers; the manager calls ECCD with selector `0x41973cd9`.
3. ECCD's `onlyOwner` gate is satisfied because the caller is the manager, its owner. The
   consensus public keys are replaced with the attacker's (the PoC logs the before/after
   `getCurEpochConPubKeyBytes`).
4. Now controlling the keeper set, the attacker signs ordinary `unlock` withdrawal messages
   (second `verifyHeaderAndExecuteTx` in the PoC targets the LockProxy/AssetProxy) and
   drains locked assets on Ethereum, and repeats the pattern on BSC and Polygon.

## Why it worked
The bridge treated its own configuration contract as just another call target
(SC-BRIDGE-5): message authorization proved "this message was included on Poly chain" but
never constrained *what* an included message may do on the destination. Because the manager
was the privileged owner of the keeper store, a message that reached ECCD inherited that
privilege, collapsing the trust boundary (SOL-McCc-8, SC-AC-1). The string-to-selector
construction turned "call an arbitrary method by name" into "call any 4-byte selector,
including privileged ones", so even a modest denylist on method *names* would have been
bypassable by hash collision. The header/proof verification (SC-BRIDGE-1) was sound in
isolation; the failure was that a valid message was allowed to target a self-privileged
contract (SC-BRIDGE-3, binding to allowed payloads/targets).

## The fix
Constrain what cross-chain messages may invoke.

```solidity
// (simplified) whitelist allowed (target, method) pairs; never allow the bridge's own config contracts
require(whiteListContractMethodMap[_toContract][_method], "target/method not allowed");
require(_toContract != EthCrossChainDataAddress, "cannot target keeper store");
```

Poly added allow-lists for permitted target contracts and methods so a cross-chain message
can only reach designated business contracts, never the manager's own data/keeper store.

## Lessons for the checklist
- **SC-BRIDGE-5** (can a cross-chain message target a privileged contract of the bridge
  itself): this is the exact question, and it names ECCD as the forbidden target.
- **SC-BRIDGE-1** (message verified against validator set/threshold): confirms the header
  check was the intended gate, and shows why a downstream target flaw defeats it.
- **SC-BRIDGE-3** (message bound to src/dst/payload): asks whether the payload/target is
  constrained; here it was not.
- **SC-AC-1** (privileged function gated by the correct modifier): forces the reviewer to
  ask *who* the `onlyOwner` of ECCD actually is, revealing it is the reachable manager.
- **SOL-McCc-8** (cross-chain messaging permissions): flags that message execution crosses a
  privilege boundary.
- Proposed new question: *"Can a cross-chain or relayed message name, as its execution
  target, any contract that the relayer/executor is itself the privileged owner or admin of?"*

## References
- Post-mortem: SlowMist root-cause analysis and rekt.news/polynetwork-rekt — not reachable from this environment; the analysis is quoted in the PoC comments. Source at github.com/polynetwork/eth-contracts commit `d16252b2b857eecf8e558bd3e1f3bb14cff30e9b` (read here).
- Transaction(s): Ethereum `0xb1f70464bd95b774c6ce60fc706eb5f9e35cb5f06e6cfe7c17dcda46ffd59581`; ECCM `0x838bf9E95CB12Dd76a54C9f9D2E3082EAF928270`; ECCD `0xcF2afe102057bA5c16f899271045a0A37fCb10f2`; exploiter `0xC8a65Fadf0e0dDAf421F28FEAb69Bf6E2E589963`. Per-chain splits were not verified from a reachable primary source.
- Related audits / similar incidents: Wormhole (2022) signature-verification flaw and Ronin (2022) validator-key compromise are the other end of the bridge-authorization spectrum.
