// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ConstantBeneficiaryShutdown {
    address payable private constant ZERO = payable(address(0));
    address payable private constant BLOCKLISTED = payable(0x70997970C51812dc3A010C7d01b50e0d17dc79C8);

    function shutdownToZeroConstant() external {
        selfdestruct(ZERO);
    }

    function shutdownToBlocklistedConstant() external {
        selfdestruct(BLOCKLISTED);
    }
}
