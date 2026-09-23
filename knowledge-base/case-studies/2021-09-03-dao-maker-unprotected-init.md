# Case Study: DAO Maker — Unprotected init() Lets Anyone Become Owner and emergencyExit

## Summary
- **Protocol:** DAO Maker (token vesting / distribution contracts)
- **Date:** 2021-09-03
- **Chain:** Ethereum
- **Loss:** ~$4M across several vesting contracts
- **Vulnerability class:** [Access Control](../vulnerabilities/access-control.md)
- **Checklist categories:** access-control
- **Checklist items:** SC-AC-4, SC-AC-2, SOL-Basics-AC-2, SOL-Basics-Initialization-3
- **Root cause in one sentence:** the vesting contract's `init(...)` had neither an initializer guard nor access control, so anyone could re-initialize it with attacker-controlled parameters, take ownership, and call the owner-only `emergencyExit` to drain the held tokens.
- **Attack tx:** https://etherscan.io/tx/0x96bf6bd14a81cf19939c0b966389daed778c3a9528a6c5dd7a4d980dec966388
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-09/DaoMaker_exp.sol

## Background
DAO Maker ran token distribution/vesting contracts that hold a project's tokens and release them on a
schedule. Each contract is configured once through an `init(uint256, uint256[], uint256[], address)`
call that sets the start time, the release periods, the release percentages, and the token. The
intended flow is that the deployer initializes the contract exactly once, at deployment, and only a
privileged owner can invoke recovery paths such as `emergencyExit`. The invariant that failed is the
most basic one: initialization must happen once, and only by an authorized party.

## The vulnerability
`init` was a plain external function with no `initializer` modifier and no owner/deployer check, and
it (re)assigned the privileged role. Reconstructed from the exploit interface and the public analysis
(simplified; the deployed source is a vesting contract, not shown verbatim):

```solidity
// simplified reconstruction of the flawed pattern
function init(uint256 startTime, uint256[] calldata periods, uint256[] calldata percents, address token)
    external            // no `initializer` guard, no onlyOwner / deployer check
{
    _owner        = msg.sender;   // caller becomes the privileged account
    vestingToken  = token;
    releasePeriods = periods;
    releasePercents = percents;
    startAt       = startTime;
}

function emergencyExit(address to) external onlyOwner {
    vestingToken.transfer(to, vestingToken.balanceOf(address(this)));   // owner drains everything
}
```

Because `init` can be called again by anyone, an attacker calls it a second time, becomes `_owner`,
and then `emergencyExit` (correctly gated to the owner) hands them the entire balance. The access
control on `emergencyExit` is real but worthless once ownership itself is up for grabs.

## The exploit, step by step
1. Pick a funded DAO Maker vesting contract (the PoC uses `0x2FD602Ed...` holding DERC).
2. Call `init(1640984401, [5702400], [10000], DERC)`: a single release period at 100% (10000 basis
   points), token set to DERC, and the caller installed as owner.
3. Call `emergencyExit(attacker)`; the owner-only recovery path transfers the full DERC balance out.
4. Repeat against the other vesting contracts: ~13.5M CAPS (`0x6e70c88b...`), 2.5M CPD twice
   (`0xd6c8dd83...`), 1.44M DERC (`0xdd571023...`), and ~20.6M SHO (`0xa43b89d5...`), for ~$4M total.

## Why it worked
This is the Parity-class initializer bug in a non-proxy dress: a state-changing setup function that
assigns ownership but is left callable by anyone, any number of times. The contract behaved perfectly
for its owner and passed functional tests because legitimate use only ever calls `init` once at
deployment. The gap is a function nobody thought was reachable a second time. No economic modeling or
flash loan is needed; the attack is a direct call. Automated tools can catch some of this
(`slither` flags unprotected initializers and functions that write owner-like state), but the
definitive check is enumerating every external function and asking who may call it and how often.

## The fix
Guard the initializer so it runs once, and never let it (re)assign ownership after deployment:

```solidity
// OpenZeppelin Initializable
function initialize(uint256 startTime, uint256[] calldata periods, uint256[] calldata percents, address token)
    external initializer                    // reverts if already initialized
{
    __Ownable_init(msg.sender);             // owner set once, at genuine initialization
    // ... set schedule ...
}
constructor() { _disableInitializers(); }   // if used behind a proxy
```

## Lessons for the checklist
- **SC-AC-4** (are initializers protected against being called twice / by anyone?): asking this of
  `init` gives an immediate no; the whole exploit follows from that single answer.
- **SC-AC-2** (any function that should be gated but is public?): `init` assigns ownership yet is
  ungated, exactly the function this item hunts for.
- **SOL-Basics-AC-2** (functions lacking access control): the same defect from Cyfrin's basics; an
  ownership-setting function with no caller restriction.
- **SOL-Basics-Initialization-3** (separate initializer function): a standalone `init`/`initialize`
  is a red flag to check for a once-guard, precisely because it is not the constructor.
- **Proposed new question:** "Does any non-constructor setup function assign owner/admin or configure
  token custody, and if so, is it protected by an `initializer`-style once-guard AND restricted to an
  authorized caller?"

## References
- Post-mortem: Mudit Gupta thread (twitter.com/Mudit__Gupta/status/1434059922774237185).
- Transaction(s): 0x96bf6bd14a81cf19939c0b966389daed778c3a9528a6c5dd7a4d980dec966388 (DAOMaker README
  also cites 0xd5e2edd6089dcf5dca78c0ccbdf659acedab173a8ab3cb65720e35b640c0af7c). Attacker
  0x2708cace7b42302af26f1ab896111d87faeff92f. Affected contracts: 0x6e70c88b... (CAPS),
  0xd6c8dd83... (CPD), 0xdd571023... (DERC), 0xa43b89d5... (SHO).
- Related audits / similar incidents: Parity multisig (2017) unprotected `initWallet`; a large family
  of unprotected-initializer disclosures across proxy and clone-factory deployments.
