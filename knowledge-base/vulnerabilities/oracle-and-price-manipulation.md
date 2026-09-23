# Oracle & Price Manipulation

## What it is
The protocol reads a price that an attacker can move within a single transaction
(or over a short window) and then acts on that manipulated price — to borrow more
than they should, liquidate unfairly, or mint mispriced shares.

## Why it happens
- **Spot price** from an AMM (`getReserves`, `balanceOf` of a pair) is manipulable
  atomically with a flash loan.
- Chainlink feeds used without checking **staleness** (`updatedAt`), round
  completeness (`answeredInRound`), or a zero/negative answer.
- TWAP window too short to resist manipulation, or the wrong pool chosen.
- Accounting trusts `token.balanceOf(address)` which anyone can inflate by donating.

## Vulnerable patterns
```solidity
// 1. Spot price from reserves — one flash loan moves it
(uint112 r0, uint112 r1,) = pair.getReserves();
uint256 price = r1 * 1e18 / r0;                 // manipulable atomically

// 2. Chainlink without validation
(, int256 answer,,,) = feed.latestRoundData();  // ignores staleness & sign
uint256 price = uint256(answer);

// 3. Balance-based accounting — donation-manipulable
uint256 price = underlying.balanceOf(address(vault)) * 1e18 / totalShares;
```

## Secure pattern
```solidity
// Chainlink: validate fully
(uint80 roundId, int256 answer, , uint256 updatedAt, uint80 answeredInRound) = feed.latestRoundData();
require(answer > 0, "bad price");
require(updatedAt != 0 && block.timestamp - updatedAt <= MAX_STALENESS, "stale");
require(answeredInRound >= roundId, "incomplete round");

// Prefer manipulation-resistant sources:
// - Chainlink / redundant oracles for the main price
// - Uniswap v3 TWAP with a sufficiently long window as a sanity bound
// - Never price collateral off a single-block spot reserve
// - Track internal accounting variables instead of raw balanceOf where possible
```

## How to detect
- Search for `getReserves`, `balanceOf(` used in pricing, `latestRoundData` /
  `latestAnswer` (the latter has no staleness data — a red flag).
- Ask: "can I move this price in the same tx I exploit it, with borrowed capital?"
- Model a flash-loan sandwich around every price read used for value decisions.

## Real-world
- **Mango Markets (2022, ~$115M)** — oracle/price manipulation of the collateral token.
- **Cheese Bank, Harvest, Warp, Inverse Finance** — spot-price / TWAP manipulation.
- **Numerous** — unchecked stale Chainlink data during depeg/outage events.

## Checklist mapping
[Checklist §4 — Oracle & Price Manipulation](../../methodology/checklist.md#4-oracle--price-manipulation)
