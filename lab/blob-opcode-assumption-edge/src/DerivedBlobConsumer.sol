// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract DerivedBlobConsumer {
    function commitmentDigest(uint256 index, bytes32 salt) external view returns (bytes32) {
        return keccak256(abi.encode(blobhash(index), salt));
    }

    function scaledBlobFee(uint256 multiplier) external view returns (uint256) {
        return block.blobbasefee * multiplier;
    }
}
