# Signatures & Replay

## What it is
Bugs in how a contract verifies off-chain signatures (permits, meta-transactions,
orders, claims). A signature that can be replayed, is not bound to the right domain,
or is accepted when malformed lets an attacker reuse authorization or forge intent.

## Why it happens
- No **nonce**, or the nonce isn't consumed, so the same signature works twice.
- Signed message not bound to `chainId` / contract address, so it replays across
  chains, forks, or sibling deployments.
- `ecrecover` returns `address(0)` for invalid signatures and the code doesn't check.
- Signature malleability (`s` in the upper range, or accepting both `v` values).

## Vulnerable patterns
```solidity
// 1. No nonce -> replayable forever
function claim(uint256 amount, bytes memory sig) external {
    bytes32 h = keccak256(abi.encodePacked(msg.sender, amount));
    require(recover(h, sig) == signer);
    _pay(msg.sender, amount);   // can be called again with the same sig
}

// 2. ecrecover result not validated
address a = ecrecover(hash, v, r, s);   // returns address(0) on bad input
require(a == signer);                    // ok only if signer != address(0)

// 3. No chainId/contract binding -> cross-chain / cross-instance replay
```

## Secure pattern
```solidity
// Use EIP-712 with a domain separator (binds name, version, chainId, contract)
bytes32 digest = _hashTypedDataV4(structHash);
address signer = ECDSA.recover(digest, sig);   // OZ ECDSA reverts on malleable/zero
require(signer == expected && signer != address(0), "bad sig");

// Consume a nonce
require(!usedNonce[signer][nonce], "replay");
usedNonce[signer][nonce] = true;

// For permits, prefer OZ ERC20Permit / EIP-2612 which handle deadline + nonce + domain.
```
- Bind every signed payload with **EIP-712 domain** (chainId + verifyingContract).
- Track and consume a **nonce** per signer.
- Use OpenZeppelin `ECDSA` (rejects malleable `s` and `address(0)`).
- Include a **deadline** and enforce it.

## How to detect
- Grep for `ecrecover`, `recover(`, `permit`, `EIP712`, `DOMAIN_SEPARATOR`.
- For each signature check: is there a nonce? is it consumed? is chainId bound? is
  `address(0)` rejected? can it replay on another chain/instance?
- Watch cached `DOMAIN_SEPARATOR` that doesn't re-derive on chainId change (post-fork replay).

## Real-world
- Multiple airdrop/claim contracts drained via missing-nonce signature replay.
- Cross-chain replay where the same signed permit worked on a forked chain.
- Malleability-based double-processing of orders in early DEX/relayer designs.

## Checklist mapping
[Checklist §8 — Signatures & Replay](../../methodology/checklist.md#8-signatures-proofs--replay)
