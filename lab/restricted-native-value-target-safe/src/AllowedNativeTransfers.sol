// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract AllowedNativeTransfers {
    function zeroValueProbe() external {
        (bool success,) = address(0).call{value: 0}("");
        require(success);
    }

    function sendToRuntimeTarget(address payable target) external payable {
        (bool success,) = target.call{value: msg.value}("");
        require(success);
    }

    function sendToOrdinaryAddress() external payable {
        payable(address(0xBEEF)).transfer(1);
    }
}
