// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ForbiddenNativeTransfers {
    function sendToZero() external payable {
        (bool success,) = address(0).call{value: 1}("");
        require(success);
    }

    function fundArcPrecompile() external payable {
        payable(0x1800000000000000000000000000000000000003).transfer(1);
    }
}
