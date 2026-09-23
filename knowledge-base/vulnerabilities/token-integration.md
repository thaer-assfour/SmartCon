# Token Integration Quirks

## What it is
The ERC-20 "standard" is loosely followed in practice. Protocols that assume every
token behaves like a textbook ERC-20 break when integrated with real-world tokens:
fee-on-transfer, rebasing, missing return values, transfer hooks, odd decimals, and
approval quirks. Many exploits are "the code is correct for a normal token, wrong
for *this* token."

## The quirks

### Fee-on-transfer (e.g. some tokens, PAXG-style)
Amount received < amount sent. Code that does `token.transferFrom(user, this, amt)`
then credits `amt` over-credits the user.
```solidity
uint256 before = token.balanceOf(address(this));
token.transferFrom(msg.sender, address(this), amt);
uint256 received = token.balanceOf(address(this)) - before;  // credit `received`, not `amt`
```

### Rebasing (stETH, AMPL)
`balanceOf` changes without a transfer. Cached balances drift from reality; internal
share accounting or snapshots must be used instead of assuming a static balance.

### Missing return value (USDT, BNB, others)
`transfer`/`approve` don't return a bool; `require(token.transfer(...))` reverts or
mis-parses. **Use `SafeERC20`** (`safeTransfer`, `safeTransferFrom`, `forceApprove`).

### ERC-777 / transfer hooks
`tokensReceived` / `tokensToSend` hooks hand control to the counterparty on transfer,
enabling **reentrancy** even on "plain token transfers." (See [reentrancy](reentrancy.md).)

### Non-standard decimals (USDC=6, WBTC=8)
Hard-coded `1e18` breaks value math. Normalize using `token.decimals()`.

### Approval race / non-zero→non-zero approve
Some tokens (USDT) revert if you `approve` a new non-zero allowance without first
setting it to zero. Use `forceApprove` / approve-zero-then-set.

### Others
- Tokens that **revert on zero-value transfer** (can be used to DoS batch flows).
- **Blocklist** tokens (USDC/USDT) — a blocked address can brick a shared flow.
- **Double-entry / proxy tokens** (e.g. old TUSD) — two addresses, one balance.

## Secure pattern
- Always `SafeERC20`.
- Measure **actual received** via balance-before/after when fee-on-transfer is possible.
- Use internal share accounting for rebasing tokens.
- Normalize decimals explicitly; never assume 18.
- Decide a token allowlist policy if the protocol can't safely support arbitrary tokens.

## How to detect
- Ask, per integrated token: is it fee-on-transfer? rebasing? does it return a bool?
  hooks? decimals? Then check the code against that specific behavior.
- Grep for raw `.transfer(`/`.transferFrom(`/`.approve(` (not `safe*`), and `1e18`
  assumptions, and `balanceOf` used as accounting.

## Real-world
- **Balancer (2020)** — fee-on-transfer (STA deflationary token) drained a pool.
- **Multiple** — USDT integrations reverting due to missing-return / approval-race handling.
- **ERC-777 reentrancy** — imBTC on Uniswap/Lendf.me (dForce, ~$25M).

## Checklist mapping
[Checklist §10 — Token Integration Quirks](../../methodology/checklist.md#10-token-integration-quirks)
