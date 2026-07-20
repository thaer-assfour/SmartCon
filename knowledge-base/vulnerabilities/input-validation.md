# Input Validation & Uninitialized State

## What it is
A grab-bag of high-frequency bugs from trusting inputs and state that were never
validated: zero addresses, zero amounts, out-of-range parameters, uninitialized
storage pointers, and unset critical variables. Individually mundane, collectively
responsible for a large share of real findings.

## Why it happens
Developers assume "no one would pass that", and Solidity provides no automatic
validation. Defaults are zero, and zero is often a valid-looking but dangerous value.

## Common issues and patterns
```solidity
// 1. Zero-address burns funds / bricks config
function setTreasury(address t) external onlyOwner { treasury = t; } // t == address(0)?
function transfer(address to, uint256 v) { ... }                     // to == 0 -> tokens gone

// 2. Zero-amount / dust that breaks accounting or wastes gas / DoS a token
function deposit(uint256 amt) external { shares[msg.sender] += amt; } // amt == 0 no-op edge

// 3. Unchecked array-length mismatch in "batch" calls
function airdrop(address[] calldata to, uint256[] calldata amt) external {
    for (uint i; i < to.length; ++i) _send(to[i], amt[i]);           // amt shorter -> revert/misindex
}

// 4. Uninitialized storage pointer (older Solidity) writes to slot 0
// 5. Critical variable never set (oracle, admin) left at default -> undefined behavior
```

## Secure pattern
```solidity
require(t != address(0), "zero address");
require(amt > 0, "zero amount");
require(to.length == amt.length, "length mismatch");
require(param <= MAX && param >= MIN, "out of range");
// Initialize all critical variables in the constructor/initializer and assert them set.
```
- Validate addresses (`!= address(0)`), amounts (`> 0` where zero is invalid), and
  ranges on every external input.
- Check array-length equality in batch functions.
- Ensure every critical variable is initialized before use; assert invariants at deploy.
- Prefer explicit reverts with reasons over silent no-ops that corrupt accounting.

## How to detect
- For each external function, list its parameters and ask "what breaks at 0 / max /
  mismatched length / unset?"
- Grep for setters without zero-address checks, batch functions without length checks,
  and constructors/initializers that skip a critical variable.
- Slither: `uninitialized-state`, `uninitialized-storage`, `missing-zero-check`.

## Real-world
- Countless contest/audit Lows and Mediums: zero-address config bricking, batch
  length-mismatch reverts, unset oracle causing zero prices.
- Uninitialized storage pointer bugs corrupting slot 0 in pre-0.5 code.

## Checklist mapping
[Checklist §17 — Input Validation & Uninitialized State](../../methodology/checklist.md#17-input-validation--uninitialized-state--notes)
