# Case Study: Hundred Finance — ERC-677 Transfer Hook Reentrancy

## Summary
- **Protocol:** Hundred Finance (Compound v2 fork) on Gnosis Chain (xDAI)
- **Date:** 2022-03-15
- **Chain:** Gnosis Chain (xDAI)
- **Loss:** ~$6.2M attributed to Hundred Finance (rekt.news); the DeFiHackLabs PoC reproduces ~$1.7M of it. Same-day sibling incident: Agave Finance ~$1.5M.
- **Vulnerability class:** [Token Integration Quirks](../vulnerabilities/token-integration.md)
- **Checklist categories:** token-integration, reentrancy
- **Checklist items:** SC-TOKEN-4, SC-REEN-4, SC-REEN-1, SOL-Token-FE-7, SOL-EC-13
- **Root cause in one sentence:** Gnosis bridge tokens are ERC-677 (`transferAndCall`) and fire an `onTokenTransfer` hook on the recipient, so the Compound-fork `borrow`, which transfers the asset out before writing the debt, handed the attacker a reentrancy window on a code path that is safe with plain ERC-20s.
- **Attack tx:** https://gnosisscan.io/tx/0x534b84f657883ddc1b66a314e8b392feb35024afdec61dfe8e7c510cfac1a098
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-03/HundredFinance_exp.sol

## Background
Hundred Finance is a Compound v2 fork. On Gnosis Chain, "native" assets arrive
through the official Omnibridge, which issues **ERC-677** tokens: a superset of
ERC-20 whose `transfer`/`transferAndCall` invoke `onTokenTransfer(from, value, data)`
on the recipient if it is a contract. The protocol invariant is the standard
Compound one, total borrow value must stay within the collateral factor, enforced
by the comptroller on each `borrow`. Compound's own reasoning that `borrowFresh` is
safe rests on the assumption that `doTransferOut` is an *inert* ERC-20 transfer that
yields no control. On Gnosis that assumption does not hold.

## The vulnerability
`borrowFresh` in the fork transfers the borrowed asset out before the account's debt
is committed to storage (the same interactions-before-effects ordering as the
pre-patch Compound source):

```solidity
// CToken.borrowFresh (deployed ordering, simplified)
doTransferOut(borrower, borrowAmount);   // ERC-677 transfer -> onTokenTransfer() callback
accountBorrows[borrower].principal = accountBorrowsNew;   // debt written only AFTER
totalBorrows = totalBorrowsNew;
```

When the borrowed token is a bridged ERC-677, `doTransferOut` calls
`onTokenTransfer` on the borrower mid-`borrowFresh`. At that instant the first
borrow's debt is not yet recorded, so a *second* borrow (of a different market) sees
inflated free liquidity and is approved. The attacker's contract exposes the hook:

```solidity
function onTokenTransfer(address _from, uint256 _value, bytes memory _data) external {
    if (_from != pair && xdaiBorrowed == false) {
        borrowXdai();   // re-enter a second market before the first debt is written
    }
}
```

## The exploit, step by step
1. Flash-loan USDC from the SushiSwap WXDAI/USDC pair (`uniswapV2Call`), amounting to
   nearly the pair's entire USDC balance.
2. `hUSDC.mint(balance)` and enter the market, establishing USDC collateral in
   Hundred Finance.
3. `hUSDC.borrow(90% of principal)`. Because USDC here is a plain-behaving token in
   this step, this simply draws down borrow capacity.
4. Borrow the ERC-677 asset so that `doTransferOut` triggers `onTokenTransfer`. Inside
   the hook, `hxDAI.borrow(...)` runs while the first borrow's debt is still unwritten,
   so the comptroller approves a second borrow the collateral could not actually
   support.
5. Convert the borrowed xDAI to WXDAI, swap through Curve, and repay the SushiSwap
   flash loan; the drained liquidity across markets is the profit.

## Why it worked
The Compound-fork code was "correct" for the tokens Compound integrates on Ethereum,
but wrong for the token *this deployment* used. The bug was not written by Hundred
Finance; it was inherited by porting Compound to a chain whose canonical tokens carry
a transfer hook. Compound itself had been warned: issue #141 (opened 2021-07-27 by
`coburncoburn` / DeFiPie) describes reentrancy via `borrowFresh`/`redeemFresh`
transferring before accounting when a cooperating malicious token is involved. The
same class also hit Agave Finance the same day. A scanner sees a canonical Compound
pattern and stays quiet; only asking "what token actually flows here, and does it
call back?" exposes it.

## The fix
Two independent mitigations, either of which closes the hole: (1) write state before
transferring (strict CEI), which Compound's later `borrowFresh` does; (2) add a
`nonReentrant` mutex spanning `borrow`/`redeem` so a hook cannot re-enter another
market.

```solidity
// (1) EFFECTS before INTERACTION
accountBorrows[borrower].principal = accountBorrowsNew;
totalBorrows = totalBorrowsNew;
doTransferOut(borrower, borrowAmount);   // callback now sees the committed debt

// (2) or gate the entry points with a shared guard
function borrow(uint256 amount) external nonReentrant returns (uint256) { ... }
```

The durable lesson is at integration time: a Compound/Aave fork must not list a token
whose transfer yields control unless every value-moving function follows CEI or is
guarded.

## Lessons for the checklist
- **SC-TOKEN-4** (ERC-777 / hook tokens enabling reentrancy on transfer): asking "can
  any listed token call back on transfer?" catches the bridged ERC-677 asset directly.
- **SC-REEN-4** (token hooks / callback window): the `onTokenTransfer` hook is the
  callback window; asking about it flags the borrow path.
- **SC-REEN-1 / SOL-EC-13** (external call before state update): the debt is written
  after `doTransferOut`, so the CEI question surfaces the ordering bug independently.
- **SOL-Token-FE-7** (token can be ERC777): the general "is this token hook-bearing?"
  question generalises to any transfer-hook token, ERC-777 or ERC-677.
- Proposed new checklist question: *"For each token this deployment actually lists,
  does `transfer`/`transferFrom` invoke a recipient hook (ERC-777 `tokensReceived`,
  ERC-677 `onTokenTransfer`), and if so is every value-moving function CEI-ordered or
  `nonReentrant`?"*

## References
- Post-mortem: Immunefi, "Hack Analysis: the Hundred Finance Heist, March 2022"
  (medium.com/immunefi/a-poc-of-the-hundred-finance-heist-4121f23a098).
- Transaction: https://gnosisscan.io/tx/0x534b84f657883ddc1b66a314e8b392feb35024afdec61dfe8e7c510cfac1a098
- Related: Agave Finance (2022-03-15, same class); Compound issue
  compound-finance/compound-protocol#141; Rari/Fei Fuse (2022-04-30); dForce imBTC
  ERC-777 reentrancy (2020).
