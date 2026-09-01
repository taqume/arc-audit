// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

import {DynamicDependency} from "../lib/vendor/DynamicDependency.sol";

contract FirstPartyCaller is DynamicDependency {
    function invokeDependency(address target) external payable returns (bool) {
        return _invokeDependency(target);
    }
}
