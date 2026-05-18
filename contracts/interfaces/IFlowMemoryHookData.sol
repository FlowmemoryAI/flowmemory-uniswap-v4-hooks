// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice FlowMemory hook-data type used to intentionally emit a FlowPulse
/// memory signal from a Uniswap v4 swap boundary.
/// @dev This interface contains only data shape. It is not an adapter callback
/// surface, so reviewers can see that hook execution enters through
/// FlowMemoryAfterSwapHook.afterSwap.
interface IFlowMemoryHookData {
    struct FlowMemorySwapHookData {
        bytes32 rootfieldId;
        bytes32 commitment;
        bytes32 parentPulseId;
        string uri;
    }
}
