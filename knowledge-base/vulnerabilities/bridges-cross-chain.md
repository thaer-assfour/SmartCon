# Bridges & Cross-Chain Messaging

## What it is
Bridges lock/burn assets on one chain and mint/release on another based on a
message. They are the largest single source of value lost in DeFi, because a flaw in
message verification lets an attacker mint unbacked assets or withdraw without a
matching deposit.

## Why it happens
- Weak or missing verification of the cross-chain **proof/signature** (the whole
  security model is "only a valid message releases funds").
- Trusting a **replayable** message (no nonce / no per-message uniqueness).
- Verifier set / guardian threshold misconfigured or bypassable.
- Merkle/receipt proof verification with a logic bug (wrong root, unchecked leaf,
  malleable encoding).
- Initialization / upgrade flaws on the bridge contract (see
  [upgradeability](upgradeability.md)).

## Vulnerable patterns
```solidity
// 1. Message accepted without validating the guardian signatures properly
function receiveMessage(bytes calldata msg_, bytes calldata sigs) external {
    // BUG: does not verify `sigs` meet threshold over the guardian set
    _mint(decode(msg_));
}

// 2. Replayable message — no nonce consumed
function claim(bytes32 msgHash, Proof calldata p) external {
    require(verify(msgHash, p));
    _release(msgHash);          // msgHash never marked used -> replay
}

// 3. Verified against attacker-supplied root / spoofable proof
```

## Secure pattern
- Verify the message against the **canonical validator set** with the correct
  threshold, using a well-reviewed signature/proof scheme.
- Consume a **unique nonce / message id**; reject already-processed messages.
- Bind messages to **source chain id, destination, and the exact payload**.
- Guard initialization and upgrades of bridge contracts tightly (timelock/multisig).
- Fail closed on any verification ambiguity.

## How to detect
- Trace the full path from "message arrives" to "funds released/minted": every check
  that must hold, and whether any can be skipped or spoofed.
- Look for missing nonce/replay protection, threshold checks that compare the wrong
  quantity, and proof verification against caller-influenced data.
- Check init/upgrade authority on the bridge.

## Real-world
- **Ronin (2022, ~$625M)** — attacker controlled enough validator keys to forge withdrawals.
- **Wormhole (2022, ~$326M)** — signature verification flaw allowed minting unbacked wETH.
- **Nomad (2022, ~$190M)** — a bad initialization made any message "proven", enabling
  a free-for-all drain.
- **BNB Bridge (2022, ~$586M)** — forged Merkle proof accepted by the verifier.

## Checklist mapping
[Checklist §15 — Bridges & Cross-Chain](../../methodology/checklist.md#15-bridges--cross-chain--notes)
