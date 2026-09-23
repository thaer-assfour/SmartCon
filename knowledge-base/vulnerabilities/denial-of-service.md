# Denial of Service

## What it is
An attacker (or a bad input) makes a contract function — or the whole protocol —
permanently or temporarily unusable, or locks funds, without necessarily stealing
anything. Impact ranges from griefing (Medium) to permanently frozen funds (High/Critical).

## Why it happens
- **Unbounded loops** over arrays a user can grow, eventually exceeding the block
  gas limit so the function can never complete.
- **Push payments in a batch**: one recipient that reverts (or is a contract with a
  reverting `receive`) blocks the entire distribution.
- **External call in a critical path** that an attacker can force to revert.
- **Strict accounting** that a griefer can knock out of a valid range (e.g. forcing
  a zero-value transfer on a token that reverts on zero).

## Vulnerable patterns
```solidity
// 1. Unbounded loop — grows until it can't be executed
for (uint256 i = 0; i < investors.length; i++) {
    payable(investors[i]).transfer(share);   // one revert bricks everyone
}

// 2. Single external call gating everything
require(externalContract.check(), "blocked");  // attacker controls externalContract

// 3. Funds locked because withdrawal depends on an all-or-nothing loop
```

## Secure pattern
```solidity
// Pull over push: let each user withdraw their own funds
mapping(address => uint256) public credit;
function withdraw() external {
    uint256 amt = credit[msg.sender];
    credit[msg.sender] = 0;
    (bool ok,) = msg.sender.call{value: amt}("");
    require(ok);
}
```
- **Pull payments**, not push loops, for distributions.
- Bound loops, or paginate/batch with caller-supplied ranges.
- Isolate failures: one recipient's revert must not block others (try/catch or credit accounting).
- Avoid making core flows depend on an attacker-controllable external call succeeding.
- Handle tokens that revert on zero-value transfer.

## How to detect
- `slither` (`calls-loop`, `costly-loop`).
- Find every loop and ask "who controls the length, and can it grow unbounded?"
- Find every external call in a critical path and ask "what if this always reverts?"
- Look for `transfer`/`send` inside loops (also 2300-gas stipend issues).

## Real-world
- **GovernMental / King of the Ether** — unbounded array / push-payment DoS.
- **Akutars (2022)** — a refund flaw permanently locked ~11,500 ETH.
- Numerous batch-airdrop and distribution contracts bricked by one malicious recipient.

## Checklist mapping
[Checklist §9 — Denial of Service](../../methodology/checklist.md#9-denial-of-service)
