// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ConstantNativeTransfers {
    address payable private constant ZERO = payable(address(0));
    address payable private constant ARC_PRECOMPILE = payable(0x1800000000000000000000000000000000000001);
    uint256 private constant AMOUNT = 1;

    function sendWithConstants() external payable {
        bool success = ZERO.send(AMOUNT);
        require(success);
    }

    function callWithConstants() external payable {
        (bool success,) = ARC_PRECOMPILE.call{value: AMOUNT}("");
        require(success);
    }
}
