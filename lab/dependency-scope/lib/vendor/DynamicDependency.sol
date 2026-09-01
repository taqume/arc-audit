// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

abstract contract DynamicDependency {
    function _invokeDependency(address target) internal returns (bool) {
        (bool success,) = target.call{value: msg.value}("");
        return success;
    }
}
