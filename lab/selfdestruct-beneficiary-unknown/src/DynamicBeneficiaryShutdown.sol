// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract DynamicBeneficiaryShutdown {
    function shutdown(address payable beneficiary) external {
        selfdestruct(beneficiary);
    }
}
