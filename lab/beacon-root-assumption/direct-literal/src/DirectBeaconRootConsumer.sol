// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract DirectBeaconRootConsumer {
    function readBeaconRoot(uint256 timestamp) external view returns (bytes memory) {
        (, bytes memory data) = address(0x000F3df6D732807Ef1319fB7B8bB8522d0Beac02).staticcall(abi.encode(timestamp));
        return data;
    }
}
