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
- [ ] README names FMM-0 as the FlowMemory Agent Memory Model.
- [ ] No private keys, RPC URLs, signed transactions, API keys, or secrets are committed.
- [ ] Base Sepolia PoolManager is re-checked against official Uniswap deployments.
- [ ] Release language does not claim Base mainnet.
- [ ] Release language does not claim audited custody.
- [ ] Release language does not claim the hook controls swaps or protects funds.
- [ ] Release language does not claim txHash/logIndex are known during hook execution.
- [ ] `python tools/launch_reality_check.py --pretty` passes and produces the screenshot text.
- [ ] `python tools/memory_consistency_card.py --pretty` passes and marks public Base Sepolia evidence pending unless release evidence exists.
- [ ] `python tools/reviewer_walkthrough.py --pretty` passes and shows each launch claim with evidence/status/non-claims.
- [ ] `python tools/verify_release_evidence.py --pretty` passes and reports `PENDING` unless real public receipt evidence exists.
- [ ] Public launch copy uses [PUBLIC_LAUNCH_COPY.md](PUBLIC_LAUNCH_COPY.md).

## If Base Sepolia Evidence Is Ready

- [ ] Release record is filled.
- [ ] Hook source is verified.
- [ ] Hook address has exactly `0x40` low hook bits.
- [ ] At least one `AfterSwapObserved` log is decoded.
- [ ] At least one `FlowPulse` log is decoded.
- [ ] Reader evidence JSON is published.
- [ ] `python tools/verify_release_evidence.py --require-pass` succeeds.
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
- FlowMemory Reality Check;
- FlowMemory Memory Consistency Card;
- FMM-0 draft memory model;
- FMM-0 Skeptic Walkthrough;
- executable forbidden outcomes for machine histories.
- receipt-bound memory consistency model.
- public receipt evidence pending until `RELEASE_EVIDENCE.json` validates.

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
- FlowMemory can tell impossible histories from live ones using receipt-bound FlowPulse boundaries.
- Everyone treated agent memory like retrieval. FlowMemory treats it like a memory model.
- Agent memory should be checked like a consistency model, not retrieved like text.
- Most AI memory retrieves context. FlowMemory checks whether the memory could have happened.
- Every launch claim has a command, and every overclaim has a red line.
- Public receipt evidence stays PENDING until `RELEASE_EVIDENCE.json` validates.
