# Launch Day Checklist

Target date: May 19, 2026.

Launch focus: FlowMemory's memory-native Uniswap v4 hook primitive.

## Launch Thesis

FlowMemory introduces the first memory-native Uniswap v4 hook primitive: a verified on-chain emission boundary where DeFi execution can produce FlowPulse memory signals.

Execution already exists. Memory is the missing layer.

## Must Be True Before Public Launch

- [ ] `main` is green in GitHub Actions.
- [ ] `forge test -vvv` passes locally.
- [ ] README opens with the memory-native primitive category claim.
- [ ] No private keys, RPC URLs, signed transactions, API keys, or secrets are committed.
- [ ] Base Sepolia PoolManager is re-checked against official Uniswap deployments.
- [ ] Release language does not claim Base mainnet.
- [ ] Release language does not claim audited custody.
- [ ] Release language does not claim the hook controls swaps or protects funds.
- [ ] Release language does not claim txHash/logIndex are known during hook execution.

## If Base Sepolia Evidence Is Ready

- [ ] Release record is filled.
- [ ] Hook source is verified.
- [ ] Hook address has exactly `0x40` low hook bits.
- [ ] At least one `AfterSwapObserved` log is decoded.
- [ ] At least one `FlowPulse` log is decoded.
- [ ] Reader evidence JSON is published.
- [ ] Public canary uses [PUBLIC_CANARY_TEMPLATE.md](PUBLIC_CANARY_TEMPLATE.md).

## If Base Sepolia Evidence Is Not Ready

Use the repo as the launch artifact.

Allowed:

- first public FlowMemory hook surface;
- memory-native Uniswap v4 hook primitive;
- live-prep package;
- Base Sepolia release path;
- CI-tested public implementation;
- protocol-level memory signal primitive.

Not allowed:

- verified deployment;
- observed live logs;
- Base mainnet;
- production custody;
- audited custody;
- production verifier network.

## Founder Lines

- DeFi has execution. FlowMemory adds memory.
- Most hooks modify execution. FlowMemory emits memory.
- The transaction is the proof envelope. The FlowPulse is the memory artifact.
- This is not a trading hook. This is a memory hook.
- FlowMemory gives DeFi a way to remember.
