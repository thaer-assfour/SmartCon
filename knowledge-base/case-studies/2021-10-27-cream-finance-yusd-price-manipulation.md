# Case Study: C.R.E.A.M. Finance — yUSD `pricePerShare` Donation Attack

## Summary
- **Protocol:** C.R.E.A.M. Finance (Compound v2 fork), crYUSD market
- **Date:** 2021-10-27
- **Chain:** Ethereum
- **Loss:** ~$130M (all available lending liquidity across C.R.E.A.M.'s markets)
- **Vulnerability class:** [Oracle & Price Manipulation](../vulnerabilities/oracle-and-price-manipulation.md)
- **Checklist categories:** oracle-and-price-manipulation, flash-loans
- **Checklist items:** SC-ORACLE-1, SC-ORACLE-4, SC-ORACLE-6, SC-FLASH-3, SOL-AM-DA-1, SOL-AM-PMA-1
- **Root cause in one sentence:** crYUSD collateral was priced by the yUSD (Yearn) vault's `pricePerShare`, which is `totalAssets / totalSupply`, so after shrinking the vault's supply the attacker doubled that ratio by *donating* the underlying Curve LP directly to the vault, doubling their collateral value with no matching debt.
- **Attack tx:** https://etherscan.io/tx/0x0fe2542079644e107cbf13690eb9c2c65963ccb79089ff96bfaf8dced2331c92
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-10/Cream_2_exp.sol

## Background
C.R.E.A.M. listed Yearn's yUSD vault token as collateral (market crYUSD). yUSD is a
Yearn v1-style vault over the Curve `yDAI+yUSDC+yUSDT+yTUSD` LP; its share price is
`getPricePerFullShare() = balance / totalSupply`. C.R.E.A.M.'s oracle multiplied that
share price by the underlying's price to value crYUSD collateral. The invariant that
mattered: collateral value must reflect real assets, so borrow capacity cannot exceed
what the collateral is truly worth. Because `pricePerShare` is a bare
balance-over-supply ratio, it is inflatable by any address that can (a) reduce
`totalSupply` and (b) increase `balance` by donation.

## The vulnerability
C.R.E.A.M.'s `PriceOracleProxy` valued a Yearn vault token from its live share price
(deployed source):

```solidity
// PriceOracleProxy.getYvTokenPrice (deployed, simplified)
uint256 pricePerShare = YVaultV1Interface(token).getPricePerFullShare(); // = balance / totalSupply
address underlying = YVaultV1Interface(token).token();
uint256 underlyingPrice = crvTokens[underlying].isCrvToken
    ? getCrvTokenPrice(underlying)     // Curve get_virtual_price for the yCRV LP
    : getTokenPrice(underlying);
return mul_(underlyingPrice, Exp({mantissa: pricePerShare}));   // collateral value scales with pricePerShare
```

`getPricePerFullShare` reads `token.balanceOf(vault) / totalSupply()`. Anyone can
raise the numerator by transferring the underlying straight to the vault (a
donation), and the attacker had first shrunk the denominator by redeeming most of the
supply. The oracle trusted this ratio as if only honest deposits could move it.

## The exploit, step by step
1. Flash-loan 500,000,000 DAI from MakerDAO; deposit into Curve's yPool and into yUSD
   to mint yUSD, then `crYUSD.mint(...)` so the first account holds a large crYUSD
   collateral position, and `enterMarkets([crYUSD])`.
2. In a second contract, flash-loan 524,102 WETH from Aave; use it as crETH collateral
   and repeatedly borrow yUSD from C.R.E.A.M. to mint more crYUSD into the first
   account, stacking collateral to roughly $1.5B nominal.
3. Withdraw the vault down: redeem almost the entire yUSD vault so its `totalSupply`
   drops to about $8M of underlying.
4. **Donate** the underlying Curve LP (`yDAI+yUSDC+yUSDT+yTUSD`, ~$8M worth) directly
   into the yUSD vault via `yUSD_vault.transfer(yUSD, totalAssets)`. With supply
   halved-equivalent and balance doubled, `pricePerShare` roughly doubles.
5. crYUSD collateral is now valued at ~2x, so C.R.E.A.M. reports the account massively
   over-collateralised. Borrow every available asset across markets, repay the Aave
   and Maker flash loans, and keep the rest.

## Why it worked
The oracle read a vault share price that is a raw `balanceOf`/`totalSupply` ratio,
which is a donation-manipulable accounting number rather than a market price. Flash
loans supplied the capital to both dominate the vault's supply and fund the donation,
so the `SC-FLASH-3` assumption ("nobody has enough capital to control this vault") was
false for one transaction. As one analyst put it, the attacker's $2B collateral was
made to back a $3B debt atomically; only C.R.E.A.M.'s $130M of available liquidity
capped the theft. `pricePerShare`-based pricing looked like a reasonable "value the
vault at its NAV," which is why it survived review.

## The fix
Do not price a vault share off `pricePerShare` unless donations cannot move it; use
independent pricing and internal accounting. Practical mitigations:

```solidity
// Prefer a supply-and-donation-resistant valuation:
// 1) price the vault from an oracle over its net assets, not balanceOf/totalSupply;
// 2) or use a virtual-shares / internal-accounting vault where a bare transfer
//    does NOT change price per share;
// 3) bound pricePerShare growth per block and reject sudden jumps.
require(pps <= lastPps + maxPpsDeltaPerBlock, "pps jump");
```

C.R.E.A.M. removed the manipulable collateral and moved off naive share-price
oracles. The general rule: treat any `balanceOf`-derived share price as attacker
input.

## Lessons for the checklist
- **SC-ORACLE-4 / SOL-AM-DA-1** (trusts `token.balanceOf` for accounting; relies on
  balanceOf instead of internal accounting): asking "can someone donate to move this
  price?" points straight at `getPricePerFullShare`.
- **SC-ORACLE-6** (price derived from a pool/vault a flash loan can inflate,
  `pricePerShare`): named exactly; asking it flags the crYUSD oracle.
- **SC-ORACLE-1 / SOL-AM-PMA-1** (price from a ratio of balances): `balance /
  totalSupply` is the ratio in question.
- **SC-FLASH-3** (assumes attacker cannot have huge capital): asking "what if the
  attacker briefly owns most of this vault?" breaks the supply-dominance assumption.
- Proposed new checklist question: *"For every vault/share token used as a price, can
  a direct token donation to the vault change its price per share, and is that price
  used for collateral or mint decisions?"*

## References
- Post-mortem: Immunefi, "Hack Analysis: Cream Finance Oct 2021"
  (medium.com/immunefi/hack-analysis-cream-finance-oct-2021-fc222d913fc5); Mudit
  Gupta, "Creamed Cream."
- Transaction: https://etherscan.io/tx/0x0fe2542079644e107cbf13690eb9c2c65963ccb79089ff96bfaf8dced2331c92
- Related: Harvest Finance (2020-10-26); Yearn/Alchemix share-price pricing warnings;
  ERC-4626 inflation/donation class (SC-DEFI-4).
