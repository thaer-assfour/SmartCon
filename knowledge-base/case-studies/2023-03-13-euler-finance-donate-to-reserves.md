# Case Study: Euler Finance — donateToReserves Skipped the Health Check

## Summary
- **Protocol:** Euler Finance (v1 lending)
- **Date:** 2023-03-13
- **Chain:** Ethereum
- **Loss:** ~$197M (about $200M by some counts) across DAI, WBTC, stETH, USDC markets
- **Vulnerability class:** [DeFi Business Logic](../vulnerabilities/defi-logic.md)
- **Checklist categories:** defi-logic
- **Checklist items:** SC-DEFI-7, SC-DEFI-1, SC-FLASH-1, SOL-Defi-Lending-3, SOL-Heuristics-16
- **Root cause in one sentence:** `donateToReserves` burned a caller's eTokens (collateral) without the liquidity/health check that every other balance-reducing path enforces, letting an account push itself deep underwater and be self-liquidated at the maximum discount.
- **Attack tx:** https://etherscan.io/tx/0xc310a0affe2169d1f6feec1c63dbc7f7c62a887fa48795d327d4d2da2d6b111d
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-03/Euler_exp.sol

## Background
Euler was a permissionless money market. Depositing underlying mints eTokens (interest-bearing
collateral); borrowing mints dTokens (debt). A special `mint(subAccountId, amount)` mints matched
eTokens and dTokens in one call, a "self-borrow" used to loop leverage. Solvency is enforced by a
liquidity check (`checkLiquidity`) that must pass after any operation that reduces collateral or
increases debt: `withdraw`, `borrow`, and transfers all run it. The intended invariant is that no
account can end an interaction with debt value exceeding risk-adjusted collateral value.

`donateToReserves(subAccountId, amount)` was introduced in eIP-14 to let an account gift its own
eTokens to the protocol reserves. Reserves are meant to be a surplus buffer, so donating "can only
help" the system, and the function was written without a post-operation liquidity check. That single
omission is the entire bug.

## The vulnerability
`donateToReserves` reduces the caller's eToken balance and credits `reserveBalance`, but never calls
`checkLiquidity`. Compare it to `withdraw`, which performs the same kind of balance reduction and
does re-check liquidity. The deployed source (euler-contracts `modules/EToken.sol`):

```solidity
function donateToReserves(uint subAccountId, uint amount) external nonReentrant {
    // ... loadAssetCache, resolve account ...
    uint origBalance = assetStorage.users[account].balance;
    require(origBalance >= amount, "e/insufficient-balance");
    unchecked { newBalance = origBalance - amount; }

    assetStorage.users[account].balance = encodeAmount(newBalance);      // collateral burned
    assetStorage.reserveBalance = ... + amount;                          // moved to reserves
    emit Withdraw(...); emitViaProxy_Transfer(proxyAddr, account, address(0), amount);
    logAssetStatus(assetCache);
    // <-- NO checkLiquidity(account): the account may now be insolvent
}
```

Liquidation then rewards the liquidator with a discount that grows as the violator's health falls,
capped at 20% (`modules/Liquidation.sol`, simplified):

```solidity
// baseDiscount rises to the cap as healthScore -> 0
uint baseDiscount = UNDERLYING_RESERVES_FEE + (1e18 - liqOpp.healthScore); // 0.02e18 + (1 - hs)
uint discount     = baseDiscount * discountBooster / 1e18;
if (discount > MAXIMUM_DISCOUNT) discount = MAXIMUM_DISCOUNT;              // 0.20e18 == 20%
liqOpp.conversionRate = underlyingPrice * 1e18 / collateralPrice * 1e18 / (1e18 - discount);
```

## The exploit, step by step
The attacker split the roles across two contracts, a `violator` and a `liquidator`, funded by a
30M DAI Aave v2 flash loan. The PoC's own annotated amounts:

1. Flash loan 30M DAI from Aave v2.
2. `violator` deposits 20M DAI, receiving ~19.5M eDAI.
3. `mint(0, 200M)` self-borrows: +195.6M eDAI collateral and +200M dDAI debt.
4. `repay(0, 10M)` burns 10M dDAI using the remaining flash-loan DAI.
5. `mint(0, 200M)` again: +195.6M eDAI and +200M dDAI.
6. `donateToReserves(0, 100M)` burns 100M eDAI collateral with no health check, so the violator's
   eDAI (collateral) now sits far below its dDAI (debt): it is deeply insolvent by construction.
7. `liquidator` calls `checkLiquidation` then `liquidate`. Because healthScore is far below 1, the
   discount pins at the 20% maximum, and the liquidator seizes ~310M eDAI while assuming only
   ~259M dDAI of debt.
8. `withdraw` converts the net seized collateral to underlying: ~38.9M DAI leaves the DAI market.
9. Repay the flash loan; keep the difference. Repeating across markets totalled ~$197M.

## Why it worked
The protocol's solvency invariant is enforced by `checkLiquidity`, but enforcement was attached
per-function rather than to the concept of "collateral just decreased." `donateToReserves` was new
(eIP-14) and reasoned about as strictly benevolent, so nobody asked whether it could make the caller
itself insolvent. It could: an account can donate away collateral it needs to back its own debt. The
liquidation engine then behaved exactly as designed, but against a position that should never have
been reachable. Automated tools see a state write guarded by `nonReentrant` and a balance check; they
do not know the protocol invariant that this path must also re-check liquidity, so the gap is invisible
to a pattern scanner and only visible to someone enumerating every balance-reducing entry point.

## The fix
Euler patched `donateToReserves` to run the liquidity check after reducing the balance, so a donation
can never leave the caller unhealthy (simplified):

```solidity
function donateToReserves(uint subAccountId, uint amount) external nonReentrant {
    // ... reduce balance, credit reserves ...
    checkLiquidity(account);   // added: revert if the donor is now insolvent
    logAssetStatus(assetCache);
}
```

The attacker, self-identifying as "Jacob," returned effectively all recoverable funds by early April
2023, and Euler opened a claims contract for depositors.

## Lessons for the checklist
- **SC-DEFI-7** (do emergency/donate/migrate functions re-run the same solvency and health checks as
  the normal path?): asking this of `donateToReserves` immediately exposes the missing
  `checkLiquidity` that `withdraw` has. This one question is the whole finding.
- **SC-DEFI-1** (can a position be made unliquidatable or self-liquidated for profit?): forces you to
  try to manufacture an underwater position and liquidate it yourself, which is exactly the attack.
- **SC-FLASH-1** (can an invariant break within one tx with borrowed capital?): the entire sequence is
  atomic on a 30M DAI flash loan, so "nobody has enough capital to become a large violator" is false.
- **SOL-Defi-Lending-3** (undue profit from self-liquidation): names the precise economic outcome, an
  attacker liquidating its own violator and walking away with more collateral than debt.
- **SOL-Heuristics-16** (code asymmetries): `withdraw` checks liquidity and `donateToReserves` does
  not; spotting that asymmetry between two balance-reducing functions is the tell.
- **Proposed new question:** "For every function that reduces a user's collateral or increases their
  debt (including gift/donate/burn/sweep helpers), is the same post-state solvency check applied that
  the primary withdraw/borrow path uses?"

## References
- Post-mortem: eIP-14 introduced `donateToReserves`; analyses by BlockSec, PeckShield, and
  Omniscia (audit of the module) — see the tweet thread links in the PoC header.
- Transaction(s): 0xc310a0affe2169d1f6feec1c63dbc7f7c62a887fa48795d327d4d2da2d6b111d (and sibling
  txs draining WBTC, stETH, USDC markets).
- Related audits / similar incidents: Euler had multiple audits; the vulnerable line shipped in a
  later governance-approved module (eIP-14), underscoring that new "helper" functions need the same
  scrutiny as core paths. Recovery: hacker returned funds; Euler EulerClaims contract.
