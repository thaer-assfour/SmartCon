# Case Study: Rari Capital / Fei Protocol Fuse — Cross-Function Reentrancy in `borrow`

## Summary
- **Protocol:** Rari Capital Fuse pools (Fei Protocol), a Compound v2 fork
- **Date:** 2022-04-30
- **Chain:** Ethereum
- **Loss:** ~$80M across seven Fuse pools (8, 18, 27, 127, 144, 146, 156)
- **Vulnerability class:** [Reentrancy](../vulnerabilities/reentrancy.md)
- **Checklist categories:** reentrancy, flash-loans
- **Checklist items:** SC-REEN-1, SC-REEN-2, SC-REEN-4, SC-FLASH-1, SOL-EC-13, SOL-AM-ReentrancyAttack-2
- **Root cause in one sentence:** `CToken.borrowFresh` sent the borrowed asset out via `doTransferOut` (an unbounded-gas ETH `call` in `CEther`) *before* writing the borrower's debt to storage, so the borrower re-entered the pool through `exitMarket`/`redeemUnderlying` and pulled its collateral back out while the comptroller still saw zero debt.
- **Attack tx:** https://etherscan.io/tx/0xab486012f21be741c9e674ffda227e30518e8a1e37a5f1d58d0b0d41f6e76530
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-04/Rari_exp.sol

## Background
Fuse let anyone spin up isolated Compound-style money markets. Each market is a
`CToken` (`CErc20` for ERC-20 underlyings, `CEther` for ETH). The safety invariant
of a Compound fork is simple: **an account may never hold more borrow value than its
collateral factor allows**, and the `Comptroller` enforces this on every
`borrow`, `redeem`, and `exitMarket`. The exploit broke that invariant inside a
single transaction because the borrow was moved to the account *before* its debt was
recorded, so a mid-borrow liquidity check saw a solvent account that in fact owed
nearly 2000 ETH.

## The vulnerability
Compound's `borrowFresh` performed the external transfer between its checks and its
effects. The following is the deployed Fuse/Compound logic (from `CToken.sol`,
verbatim ordering):

```solidity
// borrowFresh, deployed ordering: INTERACTION happens before EFFECTS
doTransferOut(borrower, borrowAmount);                 // (1) sends the asset out

accountBorrows[borrower].principal = vars.accountBorrowsNew;  // (2) debt written AFTER
accountBorrows[borrower].interestIndex = borrowIndex;
totalBorrows = vars.totalBorrowsNew;
```

For `CEther`, `doTransferOut` forwards ETH with a raw, gas-unbounded low-level call
(`recipient.call{value: amount}("")`-style), so control passes to the borrower's
`receive()` at step (1), while `accountBorrows` still reads the *pre-borrow* value.
Any comptroller check performed during that window (`exitMarketAllowed`,
`redeemAllowed`, which both call `getHypotheticalAccountLiquidity`) reads
`borrowBalanceStored == 0` for the fresh borrow and therefore treats the account as
fully collateralised.

## The exploit, step by step
1. Flash-loan 150,000,000 USDC from the Balancer Vault (`receiveFlashLoan`).
2. `fUSDC.mint(15,000,000 USDC)` in pool 127 and `enterMarkets([fUSDC])`, establishing
   USDC collateral.
3. Call `fETH.borrow(1977 ether)`. Inside `borrowFresh`, `doTransferOut` sends the
   1977 ETH to the attacker before the debt is written.
4. The attacker's `receive()` fires mid-borrow and calls
   `comptroller.exitMarket(fUSDC)`. Because the new ETH debt is not yet in storage,
   the hypothetical-liquidity check passes and the fUSDC collateral is removed from
   the account's assets list.
5. `borrowFresh` resumes and finally writes the 1977 ETH debt to storage, but fUSDC
   is no longer an entered market, so it no longer backs anything.
6. `fUSDC.redeemUnderlying(15,000,000)` returns the collateral: redeem is allowed
   because the account has no entered market requiring it.
7. Repay the Balancer flash loan; keep the borrowed ETH plus the redeemed USDC.
   Repeat across the other vulnerable pools.

## Why it worked
The check-effects-interactions order was inverted in the single most sensitive
function of a lending market. Individual `CToken`s carried a `nonReentrant` mutex,
but it did not span the cross-function path `borrow` -> (callback) ->
`exitMarket`/`redeemUnderlying`: those live on the `Comptroller` and on a *different*
`CToken`, so a per-function guard never fired. Slither's `reentrancy-eth` detector
flags "external call before state write," but on a Compound fork this pattern was
considered canonical and long-lived, so the signal was dismissed as a known-safe
convention rather than triaged against the cross-contract exit path.

## The fix
Reorder to strict CEI (write debt first) and cap the ETH transfer gas. Compound's
later `borrowFresh` does exactly this:

```solidity
// EFFECTS first: the deployed patch
accountBorrows[borrower].principal = accountBorrowsNew;   // write debt BEFORE sending
accountBorrows[borrower].interestIndex = borrowIndex;
totalBorrows = totalBorrowsNew;
// Note: Avoid token reentrancy attacks by writing increased borrow before external transfer.
doTransferOut(borrower, borrowAmount);
```

Rari's incident response additionally replaced the gas-unbounded `.call.value()` in
`CEther` with `.transfer()` (2300-gas stipend, too little to re-enter) and paused
borrowing globally, which stopped the attacker from reaching the remaining pools.

## Lessons for the checklist
- **SC-REEN-1 / SOL-EC-13** (external call before state update): asking "does
  `borrowFresh` write `accountBorrows` before or after `doTransferOut`?" points
  straight at the inverted order.
- **SC-REEN-2** (cross-function reentrancy): asking "what *other* function reads the
  debt that `borrow` has not yet written?" surfaces the `exitMarket`/`redeem` path
  that the per-`CToken` guard never covered.
- **SC-REEN-4** (`receive()`/callback window): asking "does `CEther`'s ETH transfer
  hand control to the borrower?" shows the raw `call` opens a reentrancy window.
- **SC-FLASH-1** (invariant breakable in one tx): the collateral-vs-debt invariant is
  restored and broken atomically once capital is free; a flash loan removes the
  capital barrier.
- **SOL-AM-ReentrancyAttack-2** (state change after external interaction): the debt
  write is precisely a state change positioned after the interaction.
- Proposed new checklist question: *"For every function that moves value out (ETH or
  tokens), is the caller's accounting written before the transfer, and is that guard
  effective across the comptroller / sibling-market functions the callback can reach?"*

## References
- Post-mortem: CertiK, "Fei Protocol Incident Analysis" (certik.medium.com/fei-protocol-incident-analysis-8527440696cc)
- Transaction: https://etherscan.io/tx/0xab486012f21be741c9e674ffda227e30518e8a1e37a5f1d58d0b0d41f6e76530
- PeckShield alert: https://twitter.com/peckshield/status/1520369315698016256
- Related: Compound-fork reentrancy issue (compound-finance/compound-protocol#141); C.R.E.A.M. (2021-08) cross-contract reentrancy; the DAO (2016).
