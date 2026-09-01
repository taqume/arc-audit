// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ZeroBeneficiaryShutdown {
    receive() external payable {}

    function shutdown() external {
        selfdestruct(payable(address(0)));
    }

    function shutdownToSelf() external {
        selfdestruct(payable(address(this)));
    }

    function shutdownToBlocklistedTestAddress() external {
        selfdestruct(payable(0x70997970C51812dc3A010C7d01b50e0d17dc79C8));
    }

    function shutdownToArcPrecompile() external {
        selfdestruct(payable(0x1800000000000000000000000000000000000002));
    }
}
