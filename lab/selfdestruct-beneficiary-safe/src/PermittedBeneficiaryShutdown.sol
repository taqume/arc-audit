// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract PermittedBeneficiaryShutdown {
    function shutdownToOrdinaryAddress() external {
        selfdestruct(payable(address(0xBEEF)));
    }
}
