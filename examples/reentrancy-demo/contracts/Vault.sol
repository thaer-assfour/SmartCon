// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title VulnerableVault
/// @notice A deliberately vulnerable ETH vault used to demonstrate the SmartCon
///         methodology. DO NOT DEPLOY. The bug is a classic reentrancy: the
///         external call happens BEFORE the balance is updated (Checks-Effects-
///         Interactions is violated).
///
/// Maps to knowledge-base/vulnerabilities/reentrancy.md and checklist §1.
contract VulnerableVault {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    /// @dev VULNERABLE: interaction (the ETH send) runs before the effect
    ///      (zeroing the balance), so a malicious `receive()` can re-enter
    ///      `withdraw` while `balances[msg.sender]` is still non-zero.
    function withdraw() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "nothing to withdraw");

        (bool ok, ) = msg.sender.call{value: amount}(""); // <-- interaction FIRST
        require(ok, "transfer failed");

        balances[msg.sender] = 0;                          // <-- effect TOO LATE
    }

    function totalETH() external view returns (uint256) {
        return address(this).balance;
    }
}
