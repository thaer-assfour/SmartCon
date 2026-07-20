# PoC Scaffold (Foundry)

A ready-to-run Foundry proof-of-concept template for Phase 5. Copy this folder into
your engagement directory and edit `test/PoC.t.sol`.

## Setup

```bash
# From inside your copy of this folder:
forge install foundry-rs/forge-std

# Fork mode (exploit real deployed state) — set an RPC:
export ETH_RPC_URL=https://your-rpc-endpoint
forge test -vvvv

# Or run against local mocks (no RPC needed) — see the mock section in PoC.t.sol
forge test -vvvv --match-test testExploit
```

## Two modes

1. **Fork mode** (preferred when program rules allow): `vm.createSelectFork` pins a
   real network at a block, so you exploit the actual deployed contracts. Use
   `deal()` and `vm.prank()` to set up the attacker.
2. **Mock mode**: rebuild a minimal version of the vulnerable contract locally when
   forking isn't permitted or the target isn't deployed (e.g. a contest repo). Import
   the in-scope source directly instead.

## What a good PoC asserts

- Attacker balance **increased** by a quantified amount, or
- A protocol **invariant is broken** (e.g. `totalAssets < totalSupply`), or
- Victim funds are **frozen/lost**.

Keep it minimal — the smallest test that proves the bug. Do not weaponize.
