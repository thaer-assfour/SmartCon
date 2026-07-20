// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Test, console2} from "forge-std/Test.sol";

/// @title SmartCon PoC template
/// @notice Replace the placeholders and prove the exploit. Two modes are shown:
///         (A) fork mode against real deployed state, and (B) local mock mode.
///
/// Delete the mode you don't use. Keep the PoC minimal and assert quantified impact.
contract PoC is Test {
    // ------------------------------------------------------------------
    // Configure your target here
    // ------------------------------------------------------------------
    // address constant TARGET = 0x0000000000000000000000000000000000000000;
    // uint256 constant FORK_BLOCK = 0; // pin a block for reproducibility

    address attacker = makeAddr("attacker");
    address victim   = makeAddr("victim");

    function setUp() public {
        // ---- MODE A: FORK ----
        // vm.createSelectFork(vm.rpcUrl("mainnet"), FORK_BLOCK);
        // Fund the attacker with capital / flash-loan source as needed:
        // deal(address(WETH), attacker, 100 ether);

        // ---- MODE B: MOCK ----
        // Deploy a minimal reproduction of the vulnerable contract, or import the
        // in-scope source directly and deploy it here.
    }

    /// @notice The exploit. Structure: (1) snapshot before, (2) execute the attack,
    ///         (3) assert the damage.
    function testExploit() public {
        // 1) Snapshot pre-state
        uint256 attackerBefore = attacker.balance;

        // 2) Execute the attack as the attacker
        vm.startPrank(attacker);
        // ... call the vulnerable path, e.g. reentrancy / price manipulation / etc.
        vm.stopPrank();

        // 3) Assert quantified impact
        uint256 attackerAfter = attacker.balance;
        console2.log("attacker profit (wei):", attackerAfter - attackerBefore);

        // Example assertions — replace with the invariant you broke:
        // assertGt(attackerAfter, attackerBefore, "attacker did not profit");
        // assertEq(address(target).balance, 0, "protocol was not drained");

        // Until filled in, fail loudly so an empty PoC never looks like a pass:
        fail(); // TODO: remove once the exploit + assertions are implemented
    }
}
