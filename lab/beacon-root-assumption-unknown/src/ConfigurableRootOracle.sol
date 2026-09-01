// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ConfigurableRootOracle {
    address public immutable oracle;

    constructor(address oracle_) {
        oracle = oracle_;
    }

    function read(bytes calldata input) external view returns (bytes memory) {
        (bool success, bytes memory data) = oracle.staticcall(input);
        require(success);
        return data;
    }
}
