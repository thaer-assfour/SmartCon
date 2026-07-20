# Reentrancy

## What it is
A contract makes an external call that hands control to an attacker *before* it has
finished updating its own state. The attacker re-enters the same (or a related)
function and acts on the stale, not-yet-updated state — most classically to
withdraw funds multiple times.

## Why it happens
Violation of **Checks-Effects-Interactions (CEI)**: the interaction (external call)
happens before the effects (state updates). Any external call is a potential
yield-point: `.call{value}`, ERC-20 transfers into hook-bearing tokens (ERC-777),
ERC-721/1155 `onReceived` callbacks, and `receive()`/`fallback()`.

## Variants
- **Single-function:** re-enter the same `withdraw`.
- **Cross-function:** re-enter a *different* function that shares state (e.g. call
  `transfer()` during a `withdraw()` callback while balance is still high).
- **Cross-contract:** two contracts share state via a third; a guard on one is not
  a guard on the other.
- **Read-only reentrancy:** a `view` function returns inconsistent state mid-callback,
  and *another protocol* trusts it. No state is written by the victim, yet an
  integrator is exploited (e.g. Curve-style `get_virtual_price` during a remove-liquidity callback).

## Vulnerable pattern
```solidity
function withdraw() external {
    uint256 amount = balances[msg.sender];
    (bool ok, ) = msg.sender.call{value: amount}("");   // interaction FIRST
    require(ok);
    balances[msg.sender] = 0;                            // effect too late
}
```
The attacker's `receive()` calls `withdraw()` again before `balances` is zeroed.

## Secure pattern
```solidity
function withdraw() external nonReentrant {
    uint256 amount = balances[msg.sender];
    balances[msg.sender] = 0;                            // effects BEFORE interaction
    (bool ok, ) = msg.sender.call{value: amount}("");
    require(ok);
}
```
- Follow **CEI**: update state, then call out.
- Add a `nonReentrant` mutex (OpenZeppelin `ReentrancyGuard`) on *every* function
  touching shared state, including cross-contract entries.
- For read-only reentrancy, guard the view path too, or have integrators check the
  reentrancy lock before trusting a price.

## How to detect
- `slither` reentrancy detectors (`reentrancy-eth`, `reentrancy-no-eth`, `reentrancy-benign`).
- Manually: for each external call, ask "what state is not yet updated here, and
  what other function reads it?"
- Look for `.call{value:}` / token transfers positioned before state writes.

## Real-world
- **The DAO (2016)** — the original; ~3.6M ETH, led to the ETH/ETC fork.
- **Cream Finance, Fei/Rari, Siren, dForce (ERC-777)** — reentrancy via token hooks.
- **Read-only reentrancy** — multiple lending markets mispriced Curve LP collateral.

## Checklist mapping
[Checklist §1 — Reentrancy](../../methodology/checklist.md#1-reentrancy--notes)
