# Low-Level Calls & Return Data

## What it is
Bugs from misusing `call`/`delegatecall`/`staticcall` and mishandling their return
data or gas: unchecked call success, dangerous `delegatecall` targets, return-data
bombs, gas griefing, and calling code at addresses with no contract.

## Why it happens
- Low-level `call`/`send` return a `bool` that is easy to ignore — a failed transfer
  looks like success.
- `delegatecall` executes foreign code in *your* storage/context; an untrusted or
  user-controlled target is total compromise.
- Copying unbounded return data (`returndatacopy`) lets a callee return a huge blob to
  exhaust the caller's gas (**return bomb**).
- A `call` to an address with no code returns `success = true`, so "it worked" is a lie.
- Forwarding all gas to an untrusted callee enables griefing/reentrancy windows.

## Vulnerable patterns
```solidity
// 1. Unchecked low-level call — failure silently ignored
msg.sender.call{value: amount}("");                 // return value discarded

// 2. delegatecall to a user-influenced target — full takeover
(bool ok,) = target.delegatecall(data);             // if `target` is attacker-set: game over

// 3. call to a non-contract returns true
(bool ok,) = maybeContract.call(data);
require(ok);                                         // ok even if no code ran

// 4. Return bomb — callee returns massive data to burn caller gas
(bool ok, bytes memory ret) = callee.call(data);    // `ret` copied unbounded
```

## Secure pattern
```solidity
// Check success explicitly
(bool ok, ) = msg.sender.call{value: amount}("");
require(ok, "transfer failed");

// For token transfers use SafeERC20 (handles missing return + success)
IERC20(token).safeTransfer(to, amount);

// Never delegatecall an untrusted/user-supplied address; whitelist targets.

// Verify code exists when semantics require a real contract
require(target.code.length > 0, "no contract");

// Limit forwarded gas or use assembly to bound returndata to avoid return bombs
```

## How to detect
- Grep for `.call(`, `.call{`, `.delegatecall(`, `.send(`, `.staticcall(`.
- For each: is the `bool` checked? is the target trusted/whitelisted? is returndata
  bounded? is a code-existence check needed?
- Look for `delegatecall` with any caller/config-controlled destination.

## Real-world
- **Parity (2017)** — `delegatecall` into a library that was then self-destructed.
- Multiple protocols bricked or griefed by return bombs and unchecked transfer failures.
- Phantom-function bugs: `call` to an EOA/non-contract treated as a successful integration.

## Checklist mapping
[Checklist §16 — Low-Level Calls & Return Data](../../methodology/checklist.md#16-low-level-calls--return-data--notes)
