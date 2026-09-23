# Upgradeability & Proxies

## What it is
Upgradeable contracts split logic (implementation) from storage (proxy) via
`delegatecall`. This introduces a class of bugs that don't exist in immutable
contracts: storage collisions, uninitialized implementations, selector clashes, and
over-powerful upgrade authority.

## Why it happens
- `delegatecall` runs the implementation's code against the **proxy's storage**, so
  the two must agree on storage layout exactly.
- Implementations are separate deployed contracts that can be initialized/abused
  directly if not disabled.
- Upgrade authority is a single point of total control.

## Vulnerable patterns
```solidity
// 1. Storage collision — reordering/inserting a variable in V2 corrupts state
// V1: address owner; uint256 total;
// V2: uint256 total; address owner;   <-- layouts no longer match -> corruption

// 2. Uninitialized implementation — attacker initializes the impl directly,
//    becomes owner, and can selfdestruct/delegatecall it (UUPS). (Parity-class bug)
contract Impl is UUPSUpgradeable {
    function initialize() external initializer { __Ownable_init(msg.sender); }
    // constructor missing _disableInitializers()  <-- BUG
}

// 3. Unprotected _authorizeUpgrade — anyone can upgrade to malicious logic
function _authorizeUpgrade(address) internal override {}   // no onlyOwner
```

## Secure pattern
```solidity
// Disable initializers on the implementation
constructor() { _disableInitializers(); }

// Guard the upgrade path
function _authorizeUpgrade(address) internal override onlyOwner {}

// Reserve storage gaps in upgradeable base contracts
uint256[50] private __gap;

// Preserve storage layout across versions (append-only; never reorder/remove).
// Use OZ's storage-layout checks / `@openzeppelin/upgrades` plugin in CI.
```
- Never reorder or remove state variables between versions; only append.
- Reserve `__gap` in base contracts.
- `_disableInitializers()` in the implementation constructor.
- Gate `_authorizeUpgrade` / upgrade functions; ideally timelock + multisig.
- Watch for function-selector clashes between proxy admin functions and implementation.

## How to detect
- `slither-check-upgradeability`, OZ upgrades plugin storage-layout diff.
- Grep for `initializer`, `UUPSUpgradeable`, `_authorizeUpgrade`, `delegatecall`.
- Confirm the deployed implementation is initialized (or initializers disabled).
- Diff V(n) vs V(n+1) storage layouts on every upgrade.

## Real-world
- **Parity Wallet (2017)** — uninitialized library + selfdestruct froze ~$150M.
- **Audius (2022)** — proxy initialization / storage issue enabling malicious proposal.
- Multiple UUPS "uninitialized implementation" disclosures across DeFi.

## Checklist mapping
[Checklist §7 — Upgradeability & Proxies](../../methodology/checklist.md#7-upgradeability--proxies)
