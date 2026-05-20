// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {FlowMemoryAfterSwapHook} from "../contracts/FlowMemoryAfterSwapHook.sol";

/// @notice Read-only Base Sepolia hook verification helper.
contract VerifyBaseSepolia {
    uint256 internal constant BASE_SEPOLIA_CHAIN_ID = 84532;
    address internal constant BASE_SEPOLIA_POOL_MANAGER = 0x05E73354cFDd6745C338b50BcFDfA3Aa6fA03408;

    struct VerificationResult {
        uint256 chainId;
        address hook;
        address poolManager;
        bool chainIsBaseSepolia;
        bool poolManagerMatchesBaseSepolia;
        bool afterSwapOnlyFlag;
    }

    function verify(address hook) external view returns (VerificationResult memory result) {
        FlowMemoryAfterSwapHook deployed = FlowMemoryAfterSwapHook(hook);
        address poolManager = deployed.poolManager();
        result = VerificationResult({
            chainId: block.chainid,
            hook: hook,
            poolManager: poolManager,
            chainIsBaseSepolia: block.chainid == BASE_SEPOLIA_CHAIN_ID,
            poolManagerMatchesBaseSepolia: poolManager == BASE_SEPOLIA_POOL_MANAGER,
            afterSwapOnlyFlag: deployed.hasPermissionedHookAddress()
        });
    }
}
