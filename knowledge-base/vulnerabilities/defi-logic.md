# DeFi Business Logic

## What it is
Bugs in the *intended economics* of a protocol — lending, AMMs, staking, vaults —
where the code faithfully does the wrong thing. These are the highest-value and
hardest-to-find bugs, because no generic detector knows the protocol's rules. This
is where Phase 1's written invariants pay off.

## Sub-areas and what to hunt

### Lending / borrowing
- Collateral factor & health-factor math at the boundaries: can a position be made
  **unliquidatable**, or become insolvent without triggering liquidation?
- Liquidation incentive: can a borrower **self-liquidate at a profit**, or can a
  liquidator seize more than the debt covers?
- Interest accrual: is it applied consistently on borrow, repay, and liquidation?
- Bad-debt handling: what happens when collateral value < debt?

### AMM / DEX
- Is the swap invariant (`x*y=k` or the curve's equivalent) preserved *after fees*?
- Are reserves and fees updated atomically and in the right order (no read of stale
  reserves mid-swap)?
- First-liquidity / `MINIMUM_LIQUIDITY` handling; can the first LP steal from later LPs?

### Staking / rewards
- Double-claim: can rewards be claimed twice, or after unstaking?
- Deposit-timing: can someone deposit right before a reward accrual and withdraw
  right after, capturing rewards they didn't earn?
- Reward rate / duration math: rounding to zero, or overflow of accumulated per-share.

### Vaults (ERC-4626)
- Rounding direction on `deposit`/`mint`/`withdraw`/`redeem` — always in the
  protocol's favor (see [arithmetic notes](arithmetic-and-precision.md)).
- First-deposit inflation / donation attack mitigated (virtual shares)?
- Does `totalAssets()` include or exclude pending yield / fees correctly?

### Fees & slippage
- Can fees be bypassed, or set to values that break accounting / round to zero?
- Are user-supplied `minAmountOut` and `deadline` actually enforced on every path?

## Vulnerable pattern (example: reward timing)
```solidity
function claim() external {
    uint256 owed = rewardPerToken * balances[msg.sender] - paid[msg.sender];
    // if rewardPerToken updates on deposit, a just-in-time deposit before a big
    // accrual + withdraw right after can capture rewards without real exposure
    ...
}
```

## How to detect
- Re-read the Phase 1 invariants and, for each, write a Foundry test that *tries to
  break it* (invariant/fuzz testing shines here).
- Walk each economic path end to end with adversarial inputs and ordering.
- Compare against reference implementations (OZ, Solmate, Uniswap) — deviations are
  where custom bugs hide.

## Real-world
- **Euler (2023, ~$197M)** — flawed liquidation / `donateToReserves` accounting.
- **Fei/Rari, Compound (proposal 62/64)** — reward and accounting logic errors.
- **Countless contest findings** — vault rounding, reward timing, liquidation edges.

## Checklist mapping
[Checklist §6 — DeFi Business Logic](../../methodology/checklist.md#6-defi-business-logic--notes)
