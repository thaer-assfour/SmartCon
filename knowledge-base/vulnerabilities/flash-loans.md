# Flash Loans & Atomic Composition

## What it is
Flash loans let anyone borrow an enormous amount of capital with no collateral, as
long as it is repaid in the same transaction. They are not a vulnerability
themselves — they are an **amplifier** that turns "an attacker would need $100M"
into "an attacker needs one transaction." Any invariant that can be broken *within
a single atomic transaction* is in danger.

## Why it happens
Protocols assume economic barriers ("nobody has enough capital to move this
market", "governance requires holding tokens for a while"). Flash loans erase the
capital barrier for the length of one transaction.

## Common flash-loan-enabled attacks
- **Price/oracle manipulation:** borrow → swap to skew an AMM spot price → exploit a
  protocol that reads that price → swap back → repay. (See
  [oracle notes](oracle-and-price-manipulation.md).)
- **Governance takeover:** borrow governance tokens → pass a malicious proposal /
  reach quorum in one block → drain. (Mitigation: snapshot voting weight in the past.)
- **Collateral/share inflation:** atomically inflate a share price or collateral
  value, borrow against it, walk away.
- **Reward/accounting abuse:** deposit huge → trigger a per-share reward
  calculation → withdraw, capturing a disproportionate share.

## Vulnerable pattern (conceptual)
```
1. flashLoan(100_000_000 USDC)
2. manipulate a spot price / vote weight / share price that the victim trusts NOW
3. call victim.borrow() / victim.vote() / victim.redeem() using the skewed value
4. unwind the manipulation
5. repay the flash loan, keep the profit
```

## Secure pattern
- Never make value decisions on a metric that can be moved atomically. Use
  manipulation-resistant oracles (Chainlink, long TWAP).
- Snapshot governance voting power at a past block (`ERC20Votes` checkpoints);
  require proposal delays/timelocks.
- Use internal accounting rather than instantaneous `balanceOf`.
- Consider per-block guards on sensitive multi-step interactions where appropriate.

## How to detect
- For each invariant from Phase 1, ask: "can this be violated and restored inside
  one transaction?" If yes, capital is not a barrier.
- Look for governance that reads *current* balance, pricing that reads *current*
  reserves, and rewards computed from *instantaneous* deposits.

## Real-world
- **bZx (2020)** — early flash-loan price manipulation, two incidents.
- **Beanstalk (2022, ~$182M)** — flash-loaned governance tokens passed a malicious
  proposal in a single transaction.
- **PancakeBunny, Cream, Harvest** — flash-loan-amplified price/accounting attacks.

## Checklist mapping
[Checklist §5 — Flash Loans & Atomic Composition](../../methodology/checklist.md#5-flash-loans--atomic-composition--notes)
