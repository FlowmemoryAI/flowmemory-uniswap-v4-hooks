# Base Sepolia Plan

The first live FlowMemory hook surface should be Base Sepolia before any Base mainnet claim.

## Target

- Chain: Base Sepolia
- Chain id: `84532`
- Uniswap v4 PoolManager: `0x9a13F98Cb987694C9F086b1F5eB990EeA8264Ec3`
- CREATE2 deployer: `0x4e59b44847b379578588920cA78FbF26c0B4956C`
- Hook permission bits: `0x40` (`afterSwap` only)

The planner constants are in `contracts/FlowMemoryHookPlanner.sol`.

## Local Verification

Run:

```bash
forge test --match-test testPlannerMinesBaseSepoliaCreate2AddressWithTargetFlags -vvv
forge test --match-test testAfterSwapHookEmitsFlowPulseAndReturnsZeroHookDelta -vvv
```

The first test confirms the CREATE2 planner can find an address with only the `afterSwap` hook flag. The second confirms the callback emits the FlowPulse memory signal and returns zero hook delta.

## Required Live Release Record

Before announcing any live hook, publish a release record with:

- chain id;
- PoolManager address;
- deployer address;
- constructor args;
- init code hash;
- mined salt;
- computed hook address;
- deployment transaction hash;
- source verification URL;
- reader block range;
- observed `AfterSwapObserved` logs;
- observed `FlowPulse` logs;
- explicit statement that receipt metadata is reader-derived.

## Non-Goals

This repo does not implement:

- token custody;
- fee overrides;
- dynamic fees;
- custom accounting;
- production governance;
- production multisig policy;
- a production Base mainnet deployment claim.
