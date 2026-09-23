# Access Control

## What it is
A function that changes privileged state or moves value is callable by someone who
should not be allowed to call it — because a modifier is missing, wrong, or bypassable.

## Why it happens
- Forgot the modifier on a sensitive function.
- Used `tx.origin` (phishable) instead of `msg.sender`.
- Initializer left unprotected (anyone can become owner).
- Role admin misconfigured so a role can grant itself more power.
- Over-powerful admin/backdoor that concentrates risk.

## Vulnerable patterns
```solidity
// 1. Missing modifier — anyone can drain
function setImplementation(address impl) external { implementation = impl; }

// 2. tx.origin auth — phishable via a malicious intermediary contract
function withdraw() external { require(tx.origin == owner); ... }

// 3. Unprotected initializer — first caller becomes owner
function initialize(address _owner) external { owner = _owner; } // no init guard
```

## Secure pattern
```solidity
function setImplementation(address impl) external onlyOwner { implementation = impl; }

function withdraw() external {
    require(msg.sender == owner, "not owner");  // msg.sender, never tx.origin
    ...
}

// OpenZeppelin: initializer guard + disabled implementation initializer
function initialize(address _owner) external initializer { __Ownable_init(_owner); }
constructor() { _disableInitializers(); }
```
- Gate every state-changing/privileged function with the correct modifier.
- Use `msg.sender` for authorization; never `tx.origin`.
- Protect initializers (`initializer` modifier) and disable them on implementations.
- Prefer battle-tested `Ownable` / `AccessControl`; audit role-admin relationships.
- Apply least privilege; timelock and/or multisig the most powerful roles.

## How to detect
- `slither` (`suicidal`, `arbitrary-send`, `unprotected-upgrade`).
- Enumerate every `external`/`public` function (Phase 2) and confirm each has an
  authorization answer. The gap is usually a function nobody thought was reachable.
- Grep for `tx.origin`, `initialize(`, `selfdestruct`, `delegatecall`.

## Real-world
- **Parity multisig (2017)** — unprotected `initWallet`; ~$150M frozen when the
  library was self-destructed.
- **Numerous rug-adjacent bugs** — missing `onlyOwner` on mint / withdraw / upgrade.

## Checklist mapping
[Checklist §2 — Access Control](../../methodology/checklist.md#2-access-control)
