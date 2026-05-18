// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {FlowMemoryAfterSwapHook} from "../contracts/FlowMemoryAfterSwapHook.sol";
import {FlowMemoryHookPlanner} from "../contracts/FlowMemoryHookPlanner.sol";
import {IUniswapV4SwapHookLike} from "../contracts/interfaces/IUniswapV4SwapHookLike.sol";

interface FlowMemoryAfterSwapVm {
    struct Log {
        bytes32[] topics;
        bytes data;
        address emitter;
    }

    function expectRevert(bytes4 revertData) external;
    function expectRevert(bytes calldata revertData) external;
    function expectRevert() external;
    function recordLogs() external;
    function getRecordedLogs() external returns (Log[] memory);
}

contract FlowMemoryAfterSwapUnauthorizedCaller {
    function callAfterSwap(
        FlowMemoryAfterSwapHook hook,
        address sender,
        IUniswapV4SwapHookLike.PoolKey calldata key,
        IUniswapV4SwapHookLike.SwapParams calldata params,
        int256 swapDelta,
        bytes calldata hookData
    ) external returns (bytes4 selector, int128 hookDelta) {
        return hook.afterSwap(sender, key, params, swapDelta, hookData);
    }
}

contract FlowMemoryAfterSwapHookTest {
    FlowMemoryAfterSwapVm private constant vm =
        FlowMemoryAfterSwapVm(address(uint160(uint256(keccak256("hevm cheat code")))));
    bytes32 private constant FLOWPULSE_SIGNATURE =
        keccak256("FlowPulse(bytes32,bytes32,address,uint8,bytes32,bytes32,bytes32,uint64,uint64,string)");
    bytes32 private constant AFTER_SWAP_OBSERVED_SIGNATURE =
        keccak256("AfterSwapObserved(address,address,bytes32,bytes32,bytes32,bytes32)");

    struct HookTestCase {
        bytes32 rootfieldId;
        bytes32 commitment;
        bytes32 parentPulseId;
        IUniswapV4SwapHookLike.PoolKey key;
        IUniswapV4SwapHookLike.SwapParams params;
        bytes hookData;
        int256 swapDelta;
    }

    error AssertionFailed();

    function testPlannerDefinesAfterSwapOnlyPermissionTarget() public {
        FlowMemoryHookPlanner planner = new FlowMemoryHookPlanner();
        FlowMemoryHookPlanner.HookPermissions memory permissions = planner.targetPermissions();

        _assertTrue(planner.FLOWMEMORY_AFTER_SWAP_FLAGS() == planner.AFTER_SWAP_FLAG());
        _assertTrue(planner.FLOWMEMORY_AFTER_SWAP_FLAGS() == uint160(1 << 6));
        _assertTrue(permissions.afterSwap);
        _assertTrue(!permissions.beforeSwap);
        _assertTrue(!permissions.afterSwapReturnDelta);
        _assertTrue(!permissions.beforeSwapReturnDelta);
        _assertTrue(!permissions.afterAddLiquidity);
        _assertTrue(!permissions.afterRemoveLiquidity);
        _assertTrue(!permissions.beforeDonate);
        _assertTrue(!permissions.afterDonate);
    }

    function testPlannerRejectsCustomAccountingAndExtraHookFlags() public {
        FlowMemoryHookPlanner planner = new FlowMemoryHookPlanner();
        address afterSwapOnly = address(uint160(planner.AFTER_SWAP_FLAG()));
        address afterSwapWithReturnDelta =
            address(uint160(planner.AFTER_SWAP_FLAG() | planner.AFTER_SWAP_RETURNS_DELTA_FLAG()));
        address beforeAndAfterSwap = address(uint160(planner.BEFORE_SWAP_FLAG() | planner.AFTER_SWAP_FLAG()));

        _assertTrue(planner.hasOnlyAfterSwapFlag(afterSwapOnly));
        _assertTrue(!planner.hasOnlyAfterSwapFlag(afterSwapWithReturnDelta));
        _assertTrue(!planner.hasOnlyAfterSwapFlag(beforeAndAfterSwap));
    }

    function testPlannerRejectsInvalidCreate2InputsAndMissingSalt() public {
        FlowMemoryHookPlanner planner = new FlowMemoryHookPlanner();
        bytes32 initCodeHash = _afterSwapHookInitCodeHash(planner.BASE_SEPOLIA_POOL_MANAGER());
        address create2Deployer = planner.CREATE2_DEPLOYER();

        vm.expectRevert(FlowMemoryHookPlanner.ZeroCreate2Deployer.selector);
        planner.computeCreate2Address(address(0), bytes32(0), initCodeHash);

        vm.expectRevert(FlowMemoryHookPlanner.ZeroInitCodeHash.selector);
        planner.computeCreate2Address(create2Deployer, bytes32(0), bytes32(0));

        vm.expectRevert(abi.encodeWithSelector(FlowMemoryHookPlanner.SaltNotFound.selector, uint256(0), uint256(0)));
        planner.findSalt(create2Deployer, initCodeHash, 0, 0);
    }

    function testPlannerMinesBaseSepoliaCreate2AddressWithTargetFlags() public {
        FlowMemoryHookPlanner planner = new FlowMemoryHookPlanner();
        bytes32 initCodeHash = _afterSwapHookInitCodeHash(planner.BASE_SEPOLIA_POOL_MANAGER());

        FlowMemoryHookPlanner.HookPlan memory plan = planner.planBaseSepolia(initCodeHash, 0, 100_000);

        _assertTrue(plan.chainId == planner.BASE_SEPOLIA_CHAIN_ID());
        _assertTrue(planner.BASE_SEPOLIA_POOL_MANAGER() == 0x05E73354cFDd6745C338b50BcFDfA3Aa6fA03408);
        _assertTrue(plan.poolManager == planner.BASE_SEPOLIA_POOL_MANAGER());
        _assertTrue(plan.create2Deployer == planner.CREATE2_DEPLOYER());
        _assertTrue(plan.targetFlags == planner.FLOWMEMORY_AFTER_SWAP_FLAGS());
        _assertTrue(plan.initCodeHash == initCodeHash);
        _assertTrue(planner.hasOnlyAfterSwapFlag(plan.hookAddress));
        _assertTrue(plan.hookAddress == planner.computeCreate2Address(plan.create2Deployer, plan.salt, initCodeHash));
    }

    function testConstructorRejectsZeroPoolManager() public {
        vm.expectRevert(FlowMemoryAfterSwapHook.ZeroPoolManager.selector);
        new FlowMemoryAfterSwapHook(address(0));
    }

    function testAfterSwapHookEmitsFlowPulseAndReturnsZeroHookDelta() public {
        FlowMemoryAfterSwapHook hook = new FlowMemoryAfterSwapHook(address(this));
        HookTestCase memory testCase = _sampleHookTestCase(hook, "flowmemory://base-sepolia/after-swap");

        vm.recordLogs();
        (bytes4 selector, int128 hookDelta) =
            hook.afterSwap(address(this), testCase.key, testCase.params, testCase.swapDelta, testCase.hookData);
        FlowMemoryAfterSwapVm.Log[] memory logs = vm.getRecordedLogs();

        _assertTrue(selector == hook.UNISWAP_V4_AFTER_SWAP_SELECTOR());
        _assertTrue(hookDelta == 0);
        _assertTrue(logs.length == 2);
        _assertTrue(logs[0].topics[0] == AFTER_SWAP_OBSERVED_SIGNATURE);
        _assertTrue(logs[1].topics[0] == FLOWPULSE_SIGNATURE);
        _assertTrue(logs[1].topics[2] == testCase.rootfieldId);
        _assertTrue(logs[1].topics[3] == bytes32(uint256(uint160(address(this)))));
        _assertSwapPulseData(
            logs[1].data,
            _poolIdForMemory(testCase.key),
            testCase.commitment,
            testCase.parentPulseId,
            "flowmemory://base-sepolia/after-swap"
        );
    }

    function testAfterSwapHookDerivesExpectedPulseIdAndContextHash() public {
        FlowMemoryAfterSwapHook hook = new FlowMemoryAfterSwapHook(address(this));
        HookTestCase memory testCase = _sampleHookTestCase(hook, "flowmemory://base-sepolia/after-swap");

        vm.recordLogs();
        hook.afterSwap(address(this), testCase.key, testCase.params, testCase.swapDelta, testCase.hookData);
        FlowMemoryAfterSwapVm.Log[] memory logs = vm.getRecordedLogs();

        bytes32 poolId = _poolIdForMemory(testCase.key);
        bytes32 contextHash = _contextHash(testCase.params, testCase.swapDelta, testCase.hookData);

        _assertAfterSwapObserved(logs[0], poolId, testCase.rootfieldId, testCase.commitment, contextHash);
        _assertTrue(
            logs[1].topics[1]
                == _expectedPulseId(
                    address(hook),
                    address(this),
                    address(this),
                    poolId,
                    testCase.rootfieldId,
                    testCase.commitment,
                    testCase.parentPulseId,
                    contextHash,
                    1
                )
        );
    }

    function testAfterSwapHookIsPoolManagerGated() public {
        FlowMemoryAfterSwapHook hook = new FlowMemoryAfterSwapHook(address(this));
        FlowMemoryAfterSwapUnauthorizedCaller caller = new FlowMemoryAfterSwapUnauthorizedCaller();
        IUniswapV4SwapHookLike.PoolKey memory key = _samplePoolKey(address(hook));
        IUniswapV4SwapHookLike.SwapParams memory params = _sampleSwapParams();
        bytes memory hookData =
            hook.encodeSwapHookData(keccak256("rootfield.gated"), keccak256("commitment.gated"), bytes32(0), "");

        vm.expectRevert(
            abi.encodeWithSelector(FlowMemoryAfterSwapHook.UnauthorizedPoolManager.selector, address(caller))
        );
        caller.callAfterSwap(hook, address(this), key, params, int256(0), hookData);
    }

    function testAfterSwapHookRejectsInvalidHookDataWithoutCustodyOrFeeState() public {
        FlowMemoryAfterSwapHook hook = new FlowMemoryAfterSwapHook(address(this));
        IUniswapV4SwapHookLike.PoolKey memory key = _samplePoolKey(address(hook));
        IUniswapV4SwapHookLike.SwapParams memory params = _sampleSwapParams();
        bytes memory validHookData =
            hook.encodeSwapHookData(keccak256("rootfield.valid"), keccak256("commitment.valid"), bytes32(0), "");
        bytes memory malformedHookData = hex"1234";

        vm.expectRevert(FlowMemoryAfterSwapHook.ZeroSender.selector);
        hook.afterSwap(address(0), key, params, int256(0), validHookData);

        vm.expectRevert(FlowMemoryAfterSwapHook.EmptyHookData.selector);
        hook.afterSwap(address(this), key, params, int256(0), "");

        vm.expectRevert();
        hook.afterSwap(address(this), key, params, int256(0), malformedHookData);

        bytes memory zeroRootfieldData =
            hook.encodeSwapHookData(bytes32(0), keccak256("commitment.zero-rootfield"), bytes32(0), "");
        vm.expectRevert(FlowMemoryAfterSwapHook.ZeroRootfieldId.selector);
        hook.afterSwap(address(this), key, params, int256(0), zeroRootfieldData);

        bytes memory zeroCommitmentData =
            hook.encodeSwapHookData(keccak256("rootfield.zero-commitment"), bytes32(0), bytes32(0), "");
        vm.expectRevert(FlowMemoryAfterSwapHook.ZeroCommitment.selector);
        hook.afterSwap(address(this), key, params, int256(0), zeroCommitmentData);

        (bool success,) = address(hook).call("");
        _assertTrue(!success);
        _assertTrue(address(hook).balance == 0);
    }

    function testAfterSwapHookUsesDefaultUriForBlankUri() public {
        FlowMemoryAfterSwapHook hook = new FlowMemoryAfterSwapHook(address(this));
        bytes32 rootfieldId = keccak256("rootfield.default-uri");
        bytes32 commitment = keccak256("hook.commitment.default-uri");
        bytes32 parentPulseId = bytes32(0);
        IUniswapV4SwapHookLike.PoolKey memory key = _samplePoolKey(address(hook));
        IUniswapV4SwapHookLike.SwapParams memory params = _sampleSwapParams();
        bytes memory hookData = hook.encodeSwapHookData(rootfieldId, commitment, parentPulseId, "");

        vm.recordLogs();
        hook.afterSwap(address(this), key, params, int256(0), hookData);
        FlowMemoryAfterSwapVm.Log[] memory logs = vm.getRecordedLogs();

        _assertSwapPulseData(
            logs[1].data, _poolIdForMemory(key), commitment, parentPulseId, hook.DEFAULT_AFTER_SWAP_URI()
        );
    }

    function testAfterSwapHookSequencesIncrementPerRootfield() public {
        FlowMemoryAfterSwapHook hook = new FlowMemoryAfterSwapHook(address(this));
        IUniswapV4SwapHookLike.PoolKey memory key = _samplePoolKey(address(hook));
        IUniswapV4SwapHookLike.SwapParams memory params = _sampleSwapParams();
        bytes32 firstRootfieldId = keccak256("rootfield.sequence.alpha");
        bytes32 secondRootfieldId = keccak256("rootfield.sequence.beta");

        bytes memory firstData =
            hook.encodeSwapHookData(firstRootfieldId, keccak256("commitment.alpha.1"), bytes32(0), "");
        bytes memory secondData =
            hook.encodeSwapHookData(firstRootfieldId, keccak256("commitment.alpha.2"), bytes32(0), "");
        bytes memory thirdData =
            hook.encodeSwapHookData(secondRootfieldId, keccak256("commitment.beta.1"), bytes32(0), "");

        vm.recordLogs();
        hook.afterSwap(address(this), key, params, int256(0), firstData);
        hook.afterSwap(address(this), key, params, int256(0), secondData);
        hook.afterSwap(address(this), key, params, int256(0), thirdData);
        FlowMemoryAfterSwapVm.Log[] memory logs = vm.getRecordedLogs();

        _assertTrue(_decodeSequence(logs[1].data) == 1);
        _assertTrue(_decodeSequence(logs[3].data) == 2);
        _assertTrue(_decodeSequence(logs[5].data) == 1);
        _assertTrue(logs[1].topics[2] == firstRootfieldId);
        _assertTrue(logs[3].topics[2] == firstRootfieldId);
        _assertTrue(logs[5].topics[2] == secondRootfieldId);
    }

    function testHookEventSchemasExcludeTxHashAndLogIndexAssumptions() public pure {
        bytes32 flowPulseWithReceiptMetadata = keccak256(
            "FlowPulse(bytes32,bytes32,address,uint8,bytes32,bytes32,bytes32,uint64,uint64,string,bytes32,uint256)"
        );
        bytes32 afterSwapObservedWithReceiptMetadata =
            keccak256("AfterSwapObserved(address,address,bytes32,bytes32,bytes32,bytes32,bytes32,uint256)");

        _assertTrue(FLOWPULSE_SIGNATURE != flowPulseWithReceiptMetadata);
        _assertTrue(AFTER_SWAP_OBSERVED_SIGNATURE != afterSwapObservedWithReceiptMetadata);
    }

    function _afterSwapHookInitCodeHash(address poolManager) private pure returns (bytes32) {
        return keccak256(abi.encodePacked(type(FlowMemoryAfterSwapHook).creationCode, abi.encode(poolManager)));
    }

    function _samplePoolKey(address hooks) private pure returns (IUniswapV4SwapHookLike.PoolKey memory) {
        return IUniswapV4SwapHookLike.PoolKey({
            currency0: address(0x1000), currency1: address(0x2000), fee: 3000, tickSpacing: 60, hooks: hooks
        });
    }

    function _sampleSwapParams() private pure returns (IUniswapV4SwapHookLike.SwapParams memory) {
        return IUniswapV4SwapHookLike.SwapParams({zeroForOne: true, amountSpecified: -1 ether, sqrtPriceLimitX96: 42});
    }

    function _sampleHookTestCase(FlowMemoryAfterSwapHook hook, string memory uri)
        private
        pure
        returns (HookTestCase memory testCase)
    {
        testCase.rootfieldId = keccak256("rootfield.true-hook");
        testCase.commitment = keccak256("hook.commitment.true");
        testCase.parentPulseId = keccak256("parent.pulse.true");
        testCase.key = _samplePoolKey(address(hook));
        testCase.params = _sampleSwapParams();
        testCase.hookData =
            hook.encodeSwapHookData(testCase.rootfieldId, testCase.commitment, testCase.parentPulseId, uri);
        testCase.swapDelta = 123;
    }

    function _assertAfterSwapObserved(
        FlowMemoryAfterSwapVm.Log memory log,
        bytes32 poolId,
        bytes32 rootfieldId,
        bytes32 commitment,
        bytes32 contextHash
    ) private view {
        (bytes32 observedRootfieldId, bytes32 observedCommitment, bytes32 observedContextHash) =
            abi.decode(log.data, (bytes32, bytes32, bytes32));

        _assertTrue(log.topics[0] == AFTER_SWAP_OBSERVED_SIGNATURE);
        _assertTrue(log.topics[1] == bytes32(uint256(uint160(address(this)))));
        _assertTrue(log.topics[2] == bytes32(uint256(uint160(address(this)))));
        _assertTrue(log.topics[3] == poolId);
        _assertTrue(observedRootfieldId == rootfieldId);
        _assertTrue(observedCommitment == commitment);
        _assertTrue(observedContextHash == contextHash);
    }

    function _poolIdForMemory(IUniswapV4SwapHookLike.PoolKey memory key) private pure returns (bytes32) {
        return keccak256(abi.encode(key.currency0, key.currency1, key.fee, key.tickSpacing, key.hooks));
    }

    function _contextHash(IUniswapV4SwapHookLike.SwapParams memory params, int256 swapDelta, bytes memory hookData)
        private
        pure
        returns (bytes32)
    {
        return
            keccak256(
                abi.encode(params.zeroForOne, params.amountSpecified, params.sqrtPriceLimitX96, swapDelta, hookData)
            );
    }

    function _expectedPulseId(
        address hook,
        address poolManager,
        address sender,
        bytes32 poolId,
        bytes32 rootfieldId,
        bytes32 commitment,
        bytes32 parentPulseId,
        bytes32 contextHash,
        uint64 sequence
    ) private view returns (bytes32) {
        return keccak256(
            abi.encode(
                keccak256("flowmemory.flowpulse.v0"),
                block.chainid,
                hook,
                poolManager,
                sender,
                poolId,
                rootfieldId,
                commitment,
                parentPulseId,
                contextHash,
                sequence
            )
        );
    }

    function _decodeSequence(bytes memory data) private pure returns (uint64 sequence) {
        (,,,, sequence,,) = abi.decode(data, (uint8, bytes32, bytes32, bytes32, uint64, uint64, string));
    }

    function _assertSwapPulseData(
        bytes memory data,
        bytes32 expectedSubject,
        bytes32 expectedCommitment,
        bytes32 expectedParentPulseId,
        string memory expectedUri
    ) private pure {
        (
            uint8 pulseType,
            bytes32 subject,
            bytes32 flowPulseCommitment,
            bytes32 decodedParentPulseId,
            uint64 sequence,
            uint64 occurredAt,
            string memory uri
        ) = abi.decode(data, (uint8, bytes32, bytes32, bytes32, uint64, uint64, string));

        _assertTrue(pulseType == 4);
        _assertTrue(subject == expectedSubject);
        _assertTrue(flowPulseCommitment == expectedCommitment);
        _assertTrue(decodedParentPulseId == expectedParentPulseId);
        _assertTrue(sequence == 1);
        _assertTrue(occurredAt > 0);
        _assertTrue(keccak256(bytes(uri)) == keccak256(bytes(expectedUri)));
    }

    function _assertTrue(bool condition) private pure {
        if (!condition) revert AssertionFailed();
    }
}
