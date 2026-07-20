# Front-running & MEV

## What it is
The mempool is public and transaction ordering is for sale. An attacker (or the
block builder) observes a pending transaction and inserts their own before/after it
to extract value: front-running, back-running, and sandwiching. This is
**Maximal Extractable Value (MEV)**.

## Why it happens
Pending transactions are visible before inclusion, and ordering within a block is
controlled by builders/validators who maximize profit. Any operation whose
profitability depends on *being first* or on *the state the victim expected* is exposed.

## Common forms
- **Sandwiching:** attacker buys before a victim's large swap (pushing the price up),
  lets the victim buy at the worse price, then sells — pocketing the spread. Enabled
  by missing/loose slippage protection.
- **Front-running a claim/liquidation:** attacker copies a profitable tx (a claim, an
  arbitrage, a liquidation) and submits it first with higher priority fee.
- **Front-running initialization / first deposit / approve:** seize an unprotected
  `initialize`, or exploit the ERC-20 approve race.
- **Back-running:** insert a tx immediately after a state change (e.g. an oracle update).

## Vulnerable patterns
```solidity
// 1. Swap with no real slippage bound -> sandwichable
router.swapExactTokensForTokens(amountIn, 0, path, to, block.timestamp); // minOut = 0

// 2. Reward/state that anyone can claim, profitable to front-run
function harvest() external { /* pays msg.sender the arbitrage profit */ }
```

## Secure pattern
- Enforce **user-supplied `minAmountOut`** and a real **`deadline`** on every swap.
- Use **commit-reveal** where ordering leaks intent (auctions, some games).
- Consider **private mempools / order flow** (e.g. Flashbots Protect) for sensitive txs.
- Design so being front-run is not catastrophic: pull-based rewards, per-user
  accounting, and avoiding "first-caller-wins" value.
- For initialization, deploy+initialize atomically or restrict the initializer.

## How to detect
- Find swaps with `minOut = 0` or a `deadline` of `block.timestamp` (no protection).
- Ask, per state-changing function: "if I see this in the mempool, can I profit by
  ordering my tx around it?"
- Look for value that accrues to whoever calls first (claims, harvests, liquidations).

## Real-world
- Sandwich bots extract continuous value from DEX users lacking slippage protection.
- Generalized front-runners copy any profitable pending transaction on public mempools.

## Checklist mapping
[Checklist §11 — Front-running / MEV](../../methodology/checklist.md#11-front-running--mev)
