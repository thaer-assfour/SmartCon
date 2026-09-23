# Case Study: Audius — Proxy/Implementation Storage Collision Re-Opens initialize()

## Summary
- **Protocol:** Audius (on-chain governance, staking, delegation)
- **Date:** 2022-07-23
- **Chain:** Ethereum
- **Loss:** 704 ETH (~$1.08M realized) from ~18.5M AUDIO drained from the community treasury
- **Vulnerability class:** [Upgradeability & Proxies](../vulnerabilities/upgradeability.md)
- **Checklist categories:** upgradeability, governance, access-control
- **Checklist items:** SC-PROXY-1, SC-PROXY-6, SC-AC-4, SC-GOV-4, SOL-Basics-PU-9, SOL-Basics-PU-2
- **Root cause in one sentence:** the custom `AudiusAdminUpgradeabilityProxy` stored `proxyAdmin` in storage slot 0, colliding with the OpenZeppelin `Initializable` `initialized`/`initializing` booleans that the implementation keeps in the same slot, which defeated the once-guard so anyone could re-run `initialize` and reset the governance parameters.
- **Attack tx:** https://etherscan.io/tx/0xfefd829e246002a8fd061eede7501bccb6e244a9aacea0ebceaecef5d877a984 (initialize + submitProposal + stake); https://etherscan.io/tx/0x4227bca8ed4b8915c7eec0e14ad3748a88c4371d4176e716e8007249b9980dc9 (evaluate/execute)
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-07/Audius_exp.sol

## Background
Audius ran upgradeable contracts (Governance, Staking, DelegateManagerV2) behind a custom proxy,
`AudiusAdminUpgradeabilityProxy`. Under `delegatecall`, an implementation executes against the proxy's
storage, so proxy and implementation must not both claim the same slots. The implementations used
OpenZeppelin's `Initializable`, whose `initializer` modifier is supposed to guarantee `initialize`
runs exactly once. Governance is the crown jewel: it holds the community treasury and executes
proposals, so its parameters (voting period, execution delay, quorum, guardian) must be immutable after
setup. The invariant that broke: initialization happens once, and governance params cannot be reset.

## The vulnerability
OZ `Initializable` packs two booleans, `initialized` and `initializing`, into storage slot 0. Audius's
proxy also stored its `proxyAdmin` address in slot 0. Because the implementation runs on the proxy's
storage, the `proxyAdmin` address and the initializer flags occupy the same slot (verified layout):

```
 slot        implementation view      proxy view
 0           (init flags: bool,bool)   proxyAdmin address    <-- COLLISION
 [0x360..bc] implementation           (EIP-1967 impl slot)
```

The `proxyAdmin` address in slot 0 does not decode to the boolean state the `initializer` modifier
expects. The net effect was that the once-guard no longer held: the modifier's checks (built from the
`initialized`/`initializing` bits) no longer prevented re-entry into `initialize`, so `initialize`
could be called again by anyone. The implementations also carried a separate V2 flag in slot 1, but the
base OZ flags in slot 0 were the ones the guard depended on, and those were the ones the admin address
clobbered. This is the pure storage-collision failure mode: two contracts disagree on what lives at a
slot, and privileged control leaks through the disagreement.

## The exploit, step by step
1. Call `Governance.initialize(attacker, votingPeriod=3, executionDelay=0, votingQuorumPercent=1,
   maxInProgressProposals=4, guardian=attacker)`. The collision lets this succeed on the already-live
   contract, resetting governance to attacker-chosen values: 3-block voting, no execution delay, 1%
   quorum, and the attacker as guardian and registry.
2. Call `evaluateProposalOutcome(84)` to clear an in-progress proposal slot so a new proposal can be
   submitted.
3. `submitProposal(...)` a proposal (id 85) to `transfer(attacker, 99% of governance's AUDIO)`.
4. Re-initialize `Staking` and `DelegateManagerV2` the same way, set the service-provider factory to
   the attacker, and `delegateStake(self, 1e31)` to fabricate the staked voting weight that the
   1%-quorum vote now requires.
5. `submitVote(85, Yes)` with the fabricated weight, then `evaluateProposalOutcome(85)`; with 1% quorum
   and zero delay, the proposal executes and transfers ~18.5M AUDIO to the attacker.
6. Swap AUDIO for ETH on Uniswap v2, netting ~704 ETH (~$1.08M) as the dump crashed the AUDIO price.

## Why it worked
Storage collisions are invisible in the source of either contract read alone. The Governance
implementation looks correctly initializer-guarded; the proxy looks like a reasonable admin proxy. The
defect exists only in their interaction: the admin address and the init flags share slot 0. The
contracts had been audited (OpenZeppelin in 2020, Kudelski in 2021), yet a layout collision between a
custom proxy and the OZ base slots slipped through, because auditing each contract in isolation does
not surface it. On top of the upgradeability bug, governance was configured with a 1% quorum and zero
execution delay, so once `initialize` was re-callable there was nothing to slow the treasury transfer.

## The fix
Never store proxy bookkeeping (admin, implementation, init flags) in low, collidable slots. EIP-1967
puts them at hashed, effectively un-collidable slots, which is exactly the mitigation:

```solidity
// EIP-1967 reserved slots (keccak-based, cannot collide with sequential implementation storage)
bytes32 internal constant _IMPLEMENTATION_SLOT =
    0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc;
bytes32 internal constant _ADMIN_SLOT =
    0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103;
// plus: keep the `initializer` modifier and `_disableInitializers()` on the implementation,
// and never let the proxy write to slot 0.
```

Audius (with help from samczsun) used the same re-initialization to regain control and patch, then
temporarily suspended the affected contracts.

## Lessons for the checklist
- **SC-PROXY-1** (storage collision on upgrade): asking whether the proxy and implementation agree on
  slot 0 exposes the `proxyAdmin` vs init-flags overlap directly.
- **SC-PROXY-6** (proxy's own storage overlapping implementation init flags so `initialize` re-runs):
  this item describes the exact failure; answering it is the finding.
- **SC-AC-4** (initializers protected against being called twice / by anyone): the guard existed but
  was defeated by the collision; verifying it actually holds on the deployed layout is the check.
- **SC-GOV-4** (what may `execute` call?): governance could transfer 99% of the treasury with 1% quorum
  and no delay, so a single re-init led straight to a treasury drain.
- **SOL-Basics-PU-9** (storage collision) and **SOL-Basics-PU-2** (initializer modifier): the Cyfrin
  pair covering, respectively, the layout overlap and whether the once-guard is present and effective.
- **Proposed new question:** "Does the proxy write any variable to a sequential slot (slot 0, 1, ...)
  that the implementation also uses, and specifically do the proxy admin/implementation/init-flag slots
  use EIP-1967 hashed slots rather than low slots the logic can reach?"

## References
- Post-mortem: Audius Governance Takeover Post-Mortem 7/23/22 (blog.audius.co); technical layout
  breakdown by jordaniza; SunSec thread linked in the PoC header.
- Transaction(s): initialize+propose+stake 0xfefd829e...877a984; submitVote 0x3c09c630...900dd5d5;
  evaluate/execute 0x4227bca8...b9980dc9. Governance proxy 0x4deca517d6817b6510798b7328f2314d3003abac,
  logic 0x1c91af03a390b4c619b444425b3119e553b5b44b.
- Related audits / similar incidents: audited by OpenZeppelin (2020) and Kudelski (2021); a general
  proxy storage-collision class (see also EFVault 2023-02-24, storage collision).
