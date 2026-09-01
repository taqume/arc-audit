// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract DynamicNativeTransfer {
    function sendToRuntimeTarget(address payable target) external payable {
        (bool success,) = target.call{value: msg.value}("");
        require(success);
    }
}
