# Case Study: Platypus Finance — emergencyWithdraw Checked the Wrong Solvency Condition

## Summary
- **Protocol:** Platypus Finance (single-sided stableswap AMM + USP stablecoin)
- **Date:** 2023-02-17
- **Chain:** Avalanche
- **Loss:** ~$8.5M (about $2.5M reverse-hacked back by BlockSec within 24 hours)
- **Vulnerability class:** [DeFi Business Logic](../vulnerabilities/defi-logic.md)
- **Checklist categories:** defi-logic
- **Checklist items:** SC-DEFI-7, SC-DEFI-1, SOL-Defi-Lending-2, SOL-Heuristics-16
- **Root cause in one sentence:** `MasterPlatypusV4.emergencyWithdraw` gated the release of collateral on `isSolvent(..., open=true)`, which only asks "could this account still open/hold its debt," not "has the debt been repaid," so a borrower could withdraw all collateral while leaving USP debt outstanding.
- **Attack tx:** https://snowtrace.io/tx/0x1266a937c2ccd970e5d7929021eed3ec593a95c68a99b4920c2efa226679b430
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/Platypus_exp.sol

## Background
Platypus was a stableswap on Avalanche. Depositing a stablecoin mints an LP asset; staking that LP
in `MasterPlatypusV4` earns PTP emissions and, crucially, registers it as collateral in
`PlatypusTreasure`, against which users mint the USP stablecoin. The intended invariant is standard
for any collateralized debt system: collateral cannot leave while it still backs an outstanding debt.
`MasterPlatypusV4.deposit`/`withdraw` and the treasury enforce this. `emergencyWithdraw` is the
"get my tokens out, forget the rewards" escape hatch, and it is where the invariant was dropped.

## The vulnerability
`emergencyWithdraw` releases staked LP after a single check, `platypusTreasure.isSolvent(user, lp, true)`.
The deployed function (via the Immunefi analysis of the deployed contract):

```solidity
function emergencyWithdraw(uint256 _pid) public nonReentrant {
    PoolInfo storage pool = poolInfo[_pid];
    UserInfo storage user = userInfo[_pid][msg.sender];
    if (address(platypusTreasure) != address(0x00)) {
        (bool isSolvent, ) = platypusTreasure.isSolvent(msg.sender, address(pool.lpToken), true);
        require(isSolvent, 'remaining amount exceeds collateral factor');
    }
    // ... rewarder reset ...
    pool.lpToken.transfer(address(msg.sender), user.amount);  // ALL collateral leaves
    pool.sumOfFactors -= user.factor;
    user.amount = 0; user.factor = 0; user.rewardDebt = 0;
}
```

The `true` argument is `_open`, which selects the borrow limit rather than the liquidation limit in
`_isSolvent` (simplified):

```solidity
function _isSolvent(address _user, ERC20 _token, bool _open)
    internal view returns (bool solvent, uint256 debtAmount)
{
    uint256 debtShare = userPositions[_token][_user].debtShare;
    if (debtShare == 0) return (true, 0);
    debtAmount = debtShare * (totalDebtAmount + _interestSinceLastAccrue()) / totalDebtShare;
    solvent = debtAmount <= (_open ? _borrowLimitUSP(_user, _token)     // "can still borrow"
                                   : _liquidateLimitUSP(_user, _token));
}
```

`isSolvent` returns true whenever the debt is within the borrow limit. That says the position is
healthy; it says nothing about whether the debt was paid off before the collateral is handed back.
`emergencyWithdraw` then transfers 100% of the LP out anyway, so a healthy-but-indebted account exits
with both its collateral and its USP.

## The exploit, step by step
1. Flash loan 44M USDC from Aave v3.
2. Deposit USDC into the Platypus main pool to receive LP-USDC.
3. Stake LP-USDC into `MasterPlatypusV4` (pid 4); it is now registered collateral.
4. Read `positionView(...).borrowLimitUSP` and `borrow` exactly that much USP from `PlatypusTreasure`.
   The position is now at the borrow limit, so `isSolvent(..., open=true)` is true by a hair.
5. Call `MasterPlatypusV4.emergencyWithdraw(4)`. The solvency check passes, and all LP-USDC is
   returned while the USP debt stays on the books, now completely unbacked.
6. Redeem the LP-USDC back to USDC and repay the flash loan.
7. Swap the free USP for the pools' real stablecoin liquidity (USDC, USDC.e, USDT, USDT.e, BUSD,
   DAI.e), converting minted-from-nothing USP into ~$8.5M of assets.

## Why it worked
The check answered the wrong question. "Is the account solvent?" (its collateral could support this
debt) is not "may this collateral be removed?" (the debt is settled or will remain fully backed after
removal). The normal `withdraw`/repay path preserves the backing relationship; the emergency path was
written as if solvency alone were sufficient, and it selected the more permissive `_open` limit on top
of that. A scanner sees a `require(isSolvent, ...)` and marks the function as guarded. Only reading
what `isSolvent(..., true)` actually computes, and comparing it against what "safe to withdraw
collateral" requires, exposes the mismatch. This is a business-logic invariant no generic tool encodes.

## The fix
An emergency exit that can be called by an account with debt must either repay/deduct that debt first
or forbid withdrawal while debt is nonzero. Post-incident guidance for the pattern (simplified):

```solidity
function emergencyWithdraw(uint256 _pid) public nonReentrant {
    UserInfo storage user = userInfo[_pid][msg.sender];
    // require the position carries no debt against this collateral before releasing it
    (, uint256 debt) = platypusTreasure.isSolvent(msg.sender, address(poolInfo[_pid].lpToken), false);
    require(debt == 0, "repay debt before emergency withdraw");
    poolInfo[_pid].lpToken.transfer(msg.sender, user.amount);
    user.amount = 0; user.factor = 0; user.rewardDebt = 0;
}
```

Within 24 hours, Platypus and BlockSec executed a counter-transaction recovering ~$2.5M; the attacker
was later arrested by French authorities. Follow-on incidents in 2023 showed the codebase had further
issues.

## Lessons for the checklist
- **SC-DEFI-7** (do emergency/migrate functions re-run the same solvency and health checks as the
  normal path?): the normal path keeps debt backed; `emergencyWithdraw` did not. Asking this of the
  escape hatch is the finding.
- **SC-DEFI-1** (liquidation/health math at the boundaries, can a position leave unbacked debt?):
  forces the question "what happens to the debt when the collateral leaves," which has no safe answer
  here.
- **SOL-Defi-Lending-2** (can a position be liquidated when it should?): the collateral vanished, so
  the debt could never be liquidated at all, the mirror image of this control.
- **SOL-Heuristics-16** (code asymmetries): `withdraw` respects the collateral/debt relationship while
  `emergencyWithdraw` checks only a permissive solvency flag; the asymmetry is the bug.
- **Proposed new question:** "For any function that returns a user's collateral, does it require that
  associated debt is zero (or is repaid in the same call), rather than merely that the position looks
  solvent?"

## References
- Post-mortem: Immunefi "Hack Analysis: Platypus Finance, February 2023" (deployed-source walkthrough
  and PoC); PeckShield and spreek threads linked in the PoC header.
- Transaction(s): 0x1266a937c2ccd970e5d7929021eed3ec593a95c68a99b4920c2efa226679b430 (Snowtrace).
- Related audits / similar incidents: Platypus had prior audits; the emergency path escaped scrutiny.
  Same lesson as Euler donateToReserves the same year: emergency/donate helpers bypassing core checks.
