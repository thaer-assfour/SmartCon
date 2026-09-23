# Worked Example — Reentrancy Drain

A complete, runnable demonstration of the SmartCon methodology against a
deliberately vulnerable contract. It exercises three phases end to end:

- **Phase 3 — Automated analysis:** Slither flags the reentrancy.
- **Phase 4 — Manual deep review:** a recorded run of the six parallel
  [hunter briefs](../../templates/hunters/README.md), merged by root cause, in
  [`phase4-hunters-run.md`](phase4-hunters-run.md).
- **Phase 5 — Proof of Concept:** a real EVM (`@ethereumjs/vm`) executes the exploit
  and proves funds are drained.

> The contracts here are intentionally insecure. **Do not deploy them.**

## The target

[`contracts/Vault.sol`](contracts/Vault.sol) — a `VulnerableVault` that sends ETH
*before* zeroing the caller's balance (Checks-Effects-Interactions violated).
[`contracts/Attacker.sol`](contracts/Attacker.sol) re-enters `withdraw()` from its
`receive()` hook until the vault is empty.

Maps to [knowledge-base/vulnerabilities/reentrancy.md](../../knowledge-base/vulnerabilities/reentrancy.md)
and [checklist §1](../../methodology/checklist.md#1-reentrancy).

## Run it

```bash
./run.sh
```

That installs deps, runs Slither, then executes the PoC. To run the pieces manually:

```bash
npm install
node exploit.mjs                                   # Phase 5 — executed exploit
PATH="$PWD/offline-solc:$PATH" slither contracts/ --solc-standard-json   # Phase 3
```

## Expected results

**Phase 3 (Slither)** flags the bug precisely — external call before the state write:

```
Detector: reentrancy-eth
Reentrancy in VulnerableVault.withdraw() (contracts/Vault.sol#21-29):
        External calls:
        - (ok,None) = msg.sender.call{value: amount}() (contracts/Vault.sol#25)
        State variables written after the call(s):
        - balances[msg.sender] = 0 (contracts/Vault.sol#28)
```

**Phase 5 (executed PoC)** drains the vault — attacker stakes 1 ETH, walks away with 16:

```
Vault balance   : 15 ETH  ->  0 ETH
Attacker balance: 1 ETH  ->  16 ETH
Attacker net gain: 15 ETH (staked 1 ETH, walked away with the vault)
EXPLOIT CONFIRMED: reentrancy drained the vault. Severity: Critical.
```

The written-up finding is in [`finding-01-reentrancy.md`](finding-01-reentrancy.md)
(Phase 6, produced from [`templates/report.md`](../../templates/report.md)).

## Note on the `offline-solc/` shim

Slither needs a `solc` binary. In restricted networks where the native solc cannot be
downloaded, [`offline-solc/`](offline-solc/) provides a drop-in `solc` shim backed by
the `solc-js` npm package (pure JavaScript compiler). Put it first on `PATH` and run
Slither with `--solc-standard-json`. In a normal environment with `solc`/`solc-select`
installed (via [`tools/setup.sh`](../../tools/setup.sh)), you don't need the shim.
