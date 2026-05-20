// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {FlowMemoryAfterSwapHook} from "../contracts/FlowMemoryAfterSwapHook.sol";

/// @notice Base Sepolia deployment guard for FlowMemoryAfterSwapHook.
/// @dev This script intentionally has no secret handling and no forge-std
/// dependency. Operators should use the runbook and deployment manifest tooling
/// around this script. A normal CREATE deployment may not satisfy Uniswap v4
/// hook address permission bits; this script refuses to bless such an address.
contract DeployBaseSepolia {
    uint256 internal constant BASE_SEPOLIA_CHAIN_ID = 84532;
    address internal constant BASE_SEPOLIA_POOL_MANAGER = 0x05E73354cFDd6745C338b50BcFDfA3Aa6fA03408;

    error WrongChain(uint256 actualChainId);
    error WrongPoolManager(address actualPoolManager);
    error HookAddressMissingAfterSwapFlag(address hook);

    event FlowMemoryAfterSwapHookDeploymentChecked(
        uint256 indexed chainId, address indexed poolManager, address indexed hook, bool hasAfterSwapOnlyFlag
    );

    function run(address poolManager) external returns (FlowMemoryAfterSwapHook hook) {
        if (block.chainid != BASE_SEPOLIA_CHAIN_ID) {
            revert WrongChain(block.chainid);
        }
        if (poolManager != BASE_SEPOLIA_POOL_MANAGER) {
            revert WrongPoolManager(poolManager);
        }

        hook = new FlowMemoryAfterSwapHook(poolManager);
        bool hasAfterSwapOnlyFlag = hook.hasPermissionedHookAddress();
        emit FlowMemoryAfterSwapHookDeploymentChecked(block.chainid, poolManager, address(hook), hasAfterSwapOnlyFlag);

        if (!hasAfterSwapOnlyFlag) {
            revert HookAddressMissingAfterSwapFlag(address(hook));
        }
    }
}
