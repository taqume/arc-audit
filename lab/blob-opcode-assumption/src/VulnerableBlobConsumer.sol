// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract VulnerableBlobConsumer {
    function blobCommitment(uint256 index) external view returns (bytes32) {
        return blobhash(index);
    }

    function currentBlobFee() external view returns (uint256) {
        return block.blobbasefee;
    }
}
