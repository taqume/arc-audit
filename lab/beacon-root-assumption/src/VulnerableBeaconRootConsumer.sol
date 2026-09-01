// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnerableBeaconRootConsumer {
    address internal constant ETHEREUM_BEACON_ROOTS = 0x000F3df6D732807Ef1319fB7B8bB8522d0Beac02;

    function readBeaconRoot(uint256 timestamp) external view returns (bytes32) {
        (bool success, bytes memory data) = ETHEREUM_BEACON_ROOTS.staticcall(abi.encode(timestamp));
        require(success && data.length == 32, "beacon root unavailable");
        return abi.decode(data, (bytes32));
    }
}
