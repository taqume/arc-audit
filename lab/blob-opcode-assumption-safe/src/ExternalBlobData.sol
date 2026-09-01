// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract ExternalBlobData {
    function combine(bytes32 commitment, uint256 quotedFee) external pure returns (bytes32) {
        return keccak256(abi.encode(commitment, quotedFee));
    }
}
