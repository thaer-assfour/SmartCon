# Case Study: Qubit Finance QBridge — `safeTransferFrom` on `address(0)` Mints Free Collateral

## Summary
- **Protocol:** Qubit Finance QBridge (Ethereum -> BSC deposit bridge)
- **Date:** 2022-01-27
- **Chain:** Ethereum (deposit) / BSC (mint)
- **Loss:** ~$80M
- **Vulnerability class:** [Low-Level Calls & Return Data](../vulnerabilities/low-level-calls.md)
- **Checklist categories:** low-level-calls, bridges-cross-chain, input-validation
- **Checklist items:** SC-LL-4, SC-INPUT-1, SC-BRIDGE-3, SOL-LL-3, SOL-EC-12, SOL-Token-FE-1
- **Root cause in one sentence:** After ETH deposits were moved to a dedicated `depositETH`, the legacy `deposit()` path still accepted the ETH resourceID whose token address had been set to `address(0)`, so `QBridgeHandler.deposit` called `safeTransferFrom` on a codeless address, which returns success with empty returndata, firing a Deposit event for value that never moved and minting qXETH on BSC.
- **Attack tx:** https://etherscan.io/tx/0xac7292e7d0ec8ebe1c94203d190874b2aab30592327b6cc875d00f18de6f3133 (BSC mint https://bscscan.com/tx/0x50946e3e4ccb7d39f3512b7ecb75df66e6868b9af0eee8a7e4b61ef8a459518e)
- **Reproduction:** https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-01/Qubit_exp.sol

## Background
QBridge let users deposit an asset on Ethereum and receive a bridged representation
(e.g. qXETH) on BSC. A `resourceID` identifies which asset is being bridged, mapped to a
token contract address inside `QBridgeHandler`. For real ERC-20 deposits the handler pulls
tokens with `safeTransferFrom(depositor, this, amount)`; the emitted Deposit event is what
the BSC side trusts to mint. At some point ETH deposits were migrated to a dedicated
`depositETH` function, and the ETH `resourceID`'s token address in the handler was left as
`address(0)`. The intended invariant: a Deposit event is emitted only after the stated
amount of the stated asset has actually been transferred into the handler. That invariant
depends on `safeTransferFrom` actually moving value, which is false when the token address
has no code.

## The vulnerability
The legacy `deposit()` path resolved the ETH resourceID to `address(0)` and then called a
token transfer on it. The snippet is a simplified reconstruction (the deployed handler
source was not fetched here; the behaviour is confirmed by the PoC, which prints
`resourceIDToTokenContractAddress(resourceID) == address(0)`):

```solidity
// (simplified) QBridgeHandler.deposit for the legacy ERC-20 path
function deposit(bytes32 resourceID, address depositer, bytes calldata data) external onlyBridge {
    address tokenAddress = resourceIDToTokenContractAddress[resourceID]; // == address(0) for ETH resourceID
    require(contractWhitelist[tokenAddress], "not whitelisted");         // address(0) was effectively allowed
    (uint256 option, uint256 amount) = abi.decode(data, (uint256, uint256));
    IERC20(tokenAddress).safeTransferFrom(depositer, address(this), amount); // call to a CODELESS address
    emit Deposit(destinationDomainID, resourceID, depositer, amount);        // fires with amount, nothing moved
}
```

`safeTransferFrom` performs a low-level `call`. A `call` to an address with no code returns
`success = true` and empty returndata (SC-LL-4, SOL-LL-3, SOL-EC-12). OpenZeppelin's
`SafeERC20` tolerates empty returndata (it only reverts on an explicit `false` return), so
`safeTransferFrom(address(0), ...)` neither reverts nor moves anything (SOL-Token-FE-1). The
handler then emits a full-value `Deposit` for ETH that was never supplied.

## The exploit, step by step
From `testExploit()`:
1. Call `QBridge.deposit(1, resourceID, data)` with the ETH `resourceID`
   (`0x...02f422fe9ea622049d6f73f81a906b9b8cff03b7f01`) and a `data` blob encoding a large
   `amount` (the PoC decodes `option` and `amount` from it) and the attacker as recipient.
2. QBridge forwards to `QBridgeHandler.deposit(resourceID, attacker, data)`, which resolves
   the token to `address(0)` and calls `safeTransferFrom` on it: success, empty returndata,
   no value moved, no revert.
3. A `Deposit` event fires as though the full `amount` of xETH was bridged.
4. The off-chain relayer observes the event and the BSC side mints the bridged asset:
   77,162 qXETH to the attacker, which was then used as collateral to borrow and drain
   Qubit's pools (~$80M).

## Why it worked
The bridge trusted a Deposit event whose emission was gated by a token transfer that
silently no-ops when the token address is codeless (SC-LL-4). Two missing guards would each
have stopped it: a zero-address check on the resolved token (SC-INPUT-1), and a
code-existence check before treating the transfer as real (SOL-EC-12). The deeper issue is
the migration asymmetry: `depositETH` was added but the old `deposit()` path was left able
to select the ETH resourceID, so a decommissioned code path remained reachable with a
now-poisoned (`address(0)`) mapping entry. The BSC mint trusted a source-chain event that
was never actually bound to a real transfer of the claimed asset and amount (SC-BRIDGE-3).

## The fix
Reject codeless token targets and retire the legacy path for ETH.

```solidity
address tokenAddress = resourceIDToTokenContractAddress[resourceID];
require(tokenAddress != address(0), "unknown resource");     // zero-address guard
require(tokenAddress.code.length > 0, "token has no code");  // codeless-target guard
require(contractWhitelist[tokenAddress], "not whitelisted");
// and: the ETH resourceID must only be usable via depositETH, never the ERC-20 path
```

## Lessons for the checklist
- **SC-LL-4** (call to a possibly-codeless address treated as success / phantom function):
  the `safeTransferFrom` on `address(0)` succeeding is precisely this.
- **SC-INPUT-1** (zero-address checks): a check on the resolved token address stops the
  poisoned ETH resourceID.
- **SC-BRIDGE-3** (message bound to src/dst/payload): asks whether the mint is bound to a
  real transfer of the stated asset/amount; here it was bound only to an event.
- **SOL-LL-3** (target address has code) and **SOL-EC-12** (address existence verified):
  both mandate the code-existence check that was missing.
- **SOL-Token-FE-1** (safe transfer functions): highlights that `SafeERC20` still no-ops on
  a codeless target, so "we used SafeERC20" is not sufficient.
- Proposed new question: *"After any token-address migration, is every legacy path that can
  still resolve a now-`address(0)` mapping entry disabled, and does each transfer verify the
  token has code before trusting its success?"*

## References
- Post-mortem: rekt.news/qubit-rekt and Qubit's own report (medium.com/@QubitFin/protocol-exploit-report-305c34540fa3) — not reachable from this environment; behaviour confirmed against the PoC.
- Transaction(s): ETH deposit `0xac7292e7d0ec8ebe1c94203d190874b2aab30592327b6cc875d00f18de6f3133`; BSC mint `0x50946e3e4ccb7d39f3512b7ecb75df66e6868b9af0eee8a7e4b61ef8a459518e`. Per the PoC, QBridge is `0x20E5E35ba29dC3B540a1aee781D0814D5c77Bce6` and the handler `0x17B7163cf1Dbd286E262ddc68b553D899B93f526`; `0xd01ae1a708614948b2b5e0b7ab5be6afa01325c7` is the attacker EOA (the task brief labelled this as "QBridge", which the PoC contradicts).
- Related audits / similar incidents: general phantom-function class where a `call`/`safeTransfer` to a non-contract is read as a successful integration.
