# Arithmetic & Precision

## What it is
Bugs from how numbers are computed: overflow/underflow, truncating division,
rounding in the wrong direction, and decimal mismatches. Post-Solidity-0.8
overflow reverts by default — so the modern money is in **precision and rounding**,
not raw overflow.

## Why it happens
- `unchecked { }` blocks (or `<0.8` code, or inline assembly) re-open overflow.
- Integer division truncates; **division before multiplication** destroys precision.
- Rounding always goes *some* direction — if it favors the user, it can be farmed.
- Tokens have different decimals (USDC=6, WBTC=8, most=18) and code assumes 18.
- Downcasts (`uint256`→`uint128`) silently truncate.

## Vulnerable patterns
```solidity
// 1. Division before multiplication loses precision
uint256 reward = (amount / totalStaked) * rewardPool;   // amount/total often == 0

// 2. Rounding favors the user, repeatedly
shares = assets / pricePerShare;   // rounds down deposits, but redeem rounds up? farmable

// 3. First-depositor / share inflation (ERC-4626)
// attacker deposits 1 wei -> mints 1 share -> donates large amount directly to vault
// -> later depositors' shares round down to 0, attacker owns the vault
```

## Secure pattern
```solidity
// Multiply before divide; use a mulDiv helper for full precision
uint256 reward = FixedPointMathLib.mulDiv(amount, rewardPool, totalStaked);

// Round in the PROTOCOL's favor, consistently:
// - mint/deposit: round shares DOWN (user gets no free value)
// - withdraw/redeem: round assets DOWN (protocol keeps the dust)

// First-deposit mitigation: virtual shares/assets offset (OZ ERC4626 `_decimalsOffset`),
// or seed the vault with a dead-shares initial deposit, or require a minimum first deposit.

// Normalize decimals explicitly
uint256 normalized = amount * (10 ** (18 - token.decimals()));
```

## How to detect
- Trace every `/` and `*`: is division first? Which way does it round? Who gains?
- Look for `unchecked` blocks and assembly; check the values are truly bounded.
- Look for `.decimals()` assumptions and hard-coded `1e18`.
- Fuzz invariants with Foundry: "shares never mint free value", "redeem ≤ deposit".

## Real-world
- **ERC-4626 first-depositor / donation inflation** — a whole class of vault bugs.
- Countless reward-distribution rounding leaks farmed over many small transactions.

## Checklist mapping
[Checklist §3 — Arithmetic & Precision](../../methodology/checklist.md#3-arithmetic--precision--notes)
