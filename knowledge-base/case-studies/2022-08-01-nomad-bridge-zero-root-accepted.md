# Case Study: Nomad Bridge — A Zero Root Made Every Message "Proven"

## Summary
- **Protocol:** Nomad token bridge (`Replica` optimistic-verification contract)
- **Date:** 2022-08-01
- **Chain:** Ethereum
- **Loss:** ~$190M (DeFiHackLabs records ~$152M)
- **Vulnerability class:** [Bridges & Cross-Chain Messaging](../vulnerabilities/bridges-cross-chain.md)
- **Checklist categories:** bridges-cross-chain, input-validation
- **Checklist items:** SC-BRIDGE-6, SC-INPUT-7, SC-BRIDGE-4, SOL-HMT-3, SOL-Heuristics-11
- **Root cause in one sentence:** An upgrade initialized `confirmAt[0x00] = 1`, and since an unproven message's stored root defaults to `bytes32(0)`, `process()` treated the zero root as confirmed and executed any message, so anyone could copy the first attacker's calldata and swap in their own recipient.
- **Attack tx:** https://etherscan.io/tx/0xa5fe9d044e4f3e5aa5bc4c0709333cd2190cba0f4e7f16bcf73f49f83e4a5460
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-08/NomadBridge_exp.sol

## Background
Nomad bridges tokens by locking on one chain and minting IOUs on the other, with an
optimistic verification scheme. On each chain a `Replica` contract validates inbound
messages against confirmed Merkle roots: a message must be `prove`d into an accepted root
before `process()` will dispatch it to its recipient. The intended invariant: `process()`
runs a message only if its root has genuinely been confirmed, and the zero value means
"unknown / not proven", never "accepted". A routine upgrade broke exactly that
distinction.

## The vulnerability
Verified against the pre-fix `Replica` (npm `@nomad-xyz/contracts-core@1.1.0`). `initialize`
pre-approves the committed root unconditionally, and `process` checks the *stored* root for
a message hash:

```solidity
// initialize (pre-fix): no guard against a zero committed root
confirmAt[_committedRoot] = 1;          // if _committedRoot == 0x00, then confirmAt[0x00] = 1
```

```solidity
// process (pre-fix)
bytes32 _messageHash = _m.keccak();
require(acceptableRoot(messages[_messageHash]), "!proven"); // messages[unknown] == 0x00
```

```solidity
// acceptableRoot (pre-fix): 0x00 falls through to the confirmAt lookup
uint256 _time = confirmAt[_root];       // confirmAt[0x00] == 1
if (_time == 0) return false;
return block.timestamp >= _time;        // 1 <= now  ->  TRUE
```

The chain of defaults is the whole bug. An upgrade set the committed root to `0x00`, so
`confirmAt[0x00] = 1`. For any message never proven, `messages[hash]` is the default
`bytes32(0)`. `process` passes that zero into `acceptableRoot`, which looks up
`confirmAt[0x00] == 1` and returns true. Every message is "proven" without a proof
(SC-BRIDGE-6, SC-INPUT-7). Solidity's zero-default for untouched mapping slots is treated as
a valid, confirmed root (SOL-HMT-3, SOL-Heuristics-11).

## The exploit, step by step
1. Construct a Nomad message whose action transfers a token (e.g. WBTC) from the bridge to
   an address you choose, with no valid proof.
2. Call `Replica.process(_message)`. `messages[hash]` is `0x00`; `acceptableRoot(0x00)` is
   true; the require passes and the bridge router hands the tokens to the recipient. The
   PoC's `_message` is the original attacker calldata with the recipient bytes replaced by
   `address(this)`.
3. Because the exploit needs no flash loan, no signature, and no proof, it was trivially
   copyable: hundreds of addresses replayed the same calldata with their own recipient,
   turning it into a "crowdsourced" drain (example process tx
   `0xa5fe9d04...`, the reproduced 100-WBTC withdrawal).
4. Loop over every token with balance in the bridge to drain the lot in one transaction.

## Why it worked
The upgrade's initializer accepted a zero root as a confirmed root (SC-BRIDGE-4:
init/upgrade path not guarded). Combined with the EVM's zero-default for untouched storage,
this made "not proven" and "proven under root 0x00" indistinguishable inside
`acceptableRoot`. The Quantstamp audit had raised precisely this class as **QSP-19,
"Proving With An Empty Leaf"**, i.e. the danger of a zero value being treated as a valid
proof input; it was not treated as blocking, and the later upgrade reintroduced the exact
condition. No scanner catches this because it depends on an operational value passed at
initialization, not on a static code pattern; the review question is "what does this
function do when a trusted-root or confirmation mapping returns its zero default?".

## The fix
Reject the zero root everywhere it could be mistaken for confirmation (verified against the
fixed `Replica` on `main`):

```solidity
// initialize: do not pre-approve a zero committed root
if (_committedRoot != bytes32(0)) confirmAt[_committedRoot] = 1;

// acceptableRoot: explicitly reject the "none"/zero status
if (_root == LEGACY_STATUS_PROCESSED || _root == LEGACY_STATUS_NONE) return false;

// setConfirmation: cannot set a nonzero confirmation for the zero root
require(_root != bytes32(0) || _confirmAt == 0, "can't set zero root");
```

## Lessons for the checklist
- **SC-BRIDGE-6** (is the zero/default value of a trusted-root or confirmation mapping
  treated as valid): this is the bug stated as a question.
- **SC-INPUT-7** (does any mapping lookup treat the zero/default value as valid or
  confirmed): `messages[unknown] -> 0x00 -> acceptableRoot` is exactly this.
- **SC-BRIDGE-4** (bridge init/upgrade paths guarded): the initializer set the dangerous
  value; the question forces scrutiny of upgrade-time state.
- **SOL-HMT-3** (zero hash passed to Merkle functions): names the empty-leaf/empty-root
  hazard QSP-19 warned about.
- **SOL-Heuristics-11** (uninitialized state): the default-zero mapping slot behaving as
  "confirmed" is the uninitialized-state trap.
- Proposed new question: *"For every mapping that gates authorization (roots, confirmations,
  nonces), does the code explicitly reject the zero/default key and value, and does no
  initializer or upgrade ever set the zero key to a truthy value?"*

## References
- Post-mortem: samczsun thread (twitter.com/samczsun/status/1554252024723546112) and CertiK incident analysis — not reachable from this environment. DeFiHackLabs "Hack Analysis: Nomad Bridge" lesson (by gmhacker.eth / Immunefi) was read here and corroborates the `process`/`initialize`/`acceptableRoot` chain and the April-21 upgrade that set root `0x00`.
- Transaction(s): example process `0xa5fe9d044e4f3e5aa5bc4c0709333cd2190cba0f4e7f16bcf73f49f83e4a5460`; init tx that set the trusted root `0x53fd92771d2084a9bf39a6477015ef53b7f116c79d98a21be723d06d79024cad`; Replica proxy `0x5d94309e5a0090b165fa4181519701637b6daeba`, vulnerable logic `0xb92336759618f55bd0f8313bd843604592e27bd8`. Audit: Quantstamp QSP-19 "Proving With An Empty Leaf".
- Related audits / similar incidents: BNB Bridge (2022) forged Merkle proof; both are proof/root verification failures.
