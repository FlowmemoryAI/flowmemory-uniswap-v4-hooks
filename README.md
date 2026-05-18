# FlowMemory Uniswap V4 Hooks

Public, dependency-light reference implementation for the FlowMemory Uniswap v4 `afterSwap` hook path.

This repo is intentionally small. It contains the hook candidate, hook permission planner, event schema, and tests needed to understand and verify the first FlowMemory hook surface without cloning the full FlowMemory monorepo.

## What It Does

`FlowMemoryAfterSwapHook` turns a Uniswap v4 `afterSwap` callback into a `FlowPulse` memory signal:

1. Uniswap v4 `PoolManager` calls `afterSwap`.
2. The hook verifies the caller is the configured `PoolManager`.
3. The hook decodes FlowMemory hook data: `rootfieldId`, `commitment`, `parentPulseId`, and `uri`.
4. The hook emits `AfterSwapObserved` and `FlowPulse` with pulse type `SWAP_MEMORY_SIGNAL`.
5. Off-chain readers derive receipt-only metadata such as `txHash`, `transactionIndex`, and `logIndex` after the transaction lands.

The hook returns zero hook delta. It does not take custody, override fees, perform custom accounting, or claim receipt metadata during execution.

## Run It

Install Foundry, then:

```bash
forge test -vvv
```

Useful targeted checks:

```bash
forge test --match-test testAfterSwapHookEmitsFlowPulseAndReturnsZeroHookDelta -vvv
forge test --match-test testPlannerMinesBaseSepoliaCreate2AddressWithTargetFlags -vvv
```

## Repository Layout

```text
contracts/
  FlowMemoryAfterSwapHook.sol      # PoolManager-gated afterSwap hook candidate
  FlowMemoryHookPlanner.sol        # Hook flag helpers and Base Sepolia CREATE2 planner
  FlowPulse.sol                    # FlowPulse event schema and pulse type ids
  interfaces/
    IFlowMemoryHookAdapter.sol     # Encoded hook-data shape
    IUniswapV4SwapHookLike.sol     # Minimal ABI-compatible v4 afterSwap surface
test/
  FlowMemoryAfterSwapHook.t.sol    # Dependency-free Foundry tests
docs/
  HOW_IT_WORKS.md
  BASE_SEPOLIA_PLAN.md
```

## Live Boundary

This repository is public and runnable, but it is not a production deployment claim. Before a live Base Sepolia or Base mainnet hook is announced, the release record must include the mined hook salt/address, PoolManager address, constructor args, init code hash, deployer, source verification, and reader evidence.

See [docs/BASE_SEPOLIA_PLAN.md](docs/BASE_SEPOLIA_PLAN.md).
