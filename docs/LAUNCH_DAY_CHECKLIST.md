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
- [ ] `python tools/fmm0_phase_table.py demo --pretty` passes and catches illegal phase transitions.
- [ ] `python tools/fmm0_counterexample_forge.py demo --pretty` passes and catches 12/12 generated counterexamples.
- [ ] `python tools/fmm0_closure_lab.py demo --pretty` passes and preserves/rejects 8/8 closure laws.
- [ ] `python tools/fmm0_boundary_bisim.py demo --pretty` passes and preserves/rejects 8/8 boundary projection checks.
- [ ] `python tools/fmm0_forbidden_core.py demo --pretty` passes and extracts 10/10 one-minimal forbidden cores.
- [ ] `python tools/fmm0_witness_pack.py demo --pretty` passes and reports 8/8 local conformance layers.
- [ ] `python tools/flowpulse_boundary_abi.py check --pretty` passes and exposes 0 receipt-only fields.
- [ ] `python tools/cache_lineage_gate.py demo --pretty` passes and rejects 4/4 unsafe cache reuse attempts.
- [ ] `python tools/compute_reuse_router.py demo --pretty` passes and rejects 4/4 unsafe reuse attempts.
- [ ] `python tools/compute_reuse_consistency.py demo --pretty` passes and blocks 4/4 unsafe reuse cases.
- [ ] `python tools/flowmemory_release_transcript.py --pretty` passes and reports local PASS with public receipt evidence PENDING unless release evidence exists.
- [ ] `python tools/memory_consistency_card.py --pretty` passes and marks public Base Sepolia evidence pending unless release evidence exists.
- [ ] `python tools/reviewer_walkthrough.py --pretty` passes and shows each launch claim with evidence/status/non-claims.
- [ ] `python tools/verify_release_evidence.py --pretty` passes and reports `PENDING` unless real public receipt evidence exists.
- [ ] `python tools/render_flowlitmus_casebook.py --check` passes and explains every forbidden outcome.
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
- FMM-0 Phase Space;
- FMM-0 Counterexample Forge;
- FMM-0 Skeptic Walkthrough;
- Cache Lineage Gate;
- Compute Reuse Router;
- Compute Reuse Consistency;
- FlowMemory Release Transcript;
- FlowLitmus forbidden-outcomes casebook;
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
- Retrieval treats memory as text. FMM-0 treats machine history as phase space.
- FMM-0 is not just a claim; it has adversarial counterexamples.
- Public receipt evidence stays PENDING until `RELEASE_EVIDENCE.json` validates.
- Each impossible machine history has a FlowLitmus case and a named fault.
- KV reuse should be proof-carried, not vibe-carried.
- Compute reuse without memory consistency is just cache optimism.
- GPUs compute. FlowMemory remembers.
- The fastest GPU job is the one a system can prove it does not need to run again.
