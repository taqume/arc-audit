// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ConfigurableRootOracle {
    address internal immutable rootOracle;

    constructor(address configuredRootOracle) {
        rootOracle = configuredRootOracle;
    }

    function readRoot(uint256 timestamp) external view returns (bytes memory) {
        (, bytes memory data) = rootOracle.staticcall(abi.encode(timestamp));
        return data;
    }
}
