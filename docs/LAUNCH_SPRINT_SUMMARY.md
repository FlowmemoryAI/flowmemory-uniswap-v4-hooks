# Launch Sprint Summary

This summary captures the public launch package for the FlowMemory Uniswap v4
hook repository.

## Core Position

FlowMemory introduces the first memory-native Uniswap v4 hook primitive: a
verified on-chain emission boundary where DeFi execution can produce FlowPulse
memory signals.

The swap is not the memory.

The transaction is the proof envelope.

The FlowPulse is the memory artifact.

## What Changed

The repo now presents a stack rather than a loose set of ideas:

- `FlowMemoryAfterSwapHook`: the memory-native Uniswap v4 `afterSwap` emission
  boundary.
- `FlowPulse`: the memory signal emitted from the boundary.
- `FlowMMU`: receipt-backed virtual memory for machine reality.
- `FlowQuiesce`: receipt-triggered safe points for active agent frames.
- `FlowSerial`: receipt-linearizability for machine cognition.
- `FlowLitmus`: executable forbidden outcomes for the runtime model.
- `FlowMemory Reality Check`: one launch command that shows the boundary model,
  hook invariant surface, FlowLitmus suite, and safe public claim.
- `FMM-0`: FlowMemory Agent Memory Model, the draft receipt-bound consistency
  model for machine histories.
- `FMM-0 Phase Space`: a machine-state phase diagram that catches
  illegal local-only to FMM-0 live jumps and pre-receipt receipt-field claims.
- `FMM-0 Counterexample Forge`: an adversarial harness that mutates valid
  artifacts into impossible histories and checks that FMM-0 catches them.
- `FMM-0 Closure Lab`: an executable memory-algebra harness that preserves
  valid receipt-bound composition and rejects invalid composition.
- `FMM-0 Boundary Bisimulation`: a cross-layer conformance harness that checks
  hook-to-receipt-to-runtime FlowPulse boundary projection.
- `FMM-0 Forbidden Core Extractor`: a diagnostic minimizer that shrinks
  impossible histories into one-minimal forbidden cores.
- `FMM-0 Witness Pack`: a reproducible local evidence packet for the launch
  conformance surface.
- `FlowPulse Boundary ABI`: a Solidity event/model drift gate for the
  FlowPulse boundary.
- `Cache Lineage Gate`: a proof-carried KV/context reuse gate that catches
  tokenizer, side-input, adapter, runtime, and cache-policy drift.
- `Compute Reuse Router`: a proof-backed AI/GPU workflow gate that routes safe
  prior compute reuse and rejects unsafe reuse.
- `Compute Reuse Consistency`: a bridge harness that requires cache lineage,
  compute fingerprint compatibility, and receipt-bound history before accepting
  reuse.
- `FlowMemory Release Transcript`: one offline launch transcript that shows
  passed local evidence, pending public evidence, and explicit non-claims.
- `FlowMemory Memory Consistency Card`: a claim-to-evidence scorecard that shows
  FlowMemory is treating agent memory as a consistency model, not retrieval.
- `FMM-0 Skeptic Walkthrough`: a claim ledger that maps every launch claim to
  evidence, commands, expected results, status, and explicit non-claims.
- `Base Sepolia Evidence Gate`: a pending-safe verifier for the public release
  evidence packet.
- `FlowLitmus Forbidden Outcomes`: a casebook explaining each impossible
  machine history and the FlowMemory fault that catches it.

## Launch Command

Use this as the screenshot-ready proof point:

```bash
python tools/launch_reality_check.py --pretty
```

Use this as the shortest reviewer path:

```text
docs/REVIEWER_QUICKSTART.md
```

Expected result:

```text
Result: FlowMemory can tell impossible histories from live ones using receipt-bound FlowPulse boundaries.
```

Use this as the launch positioning scorecard:

```bash
python tools/memory_consistency_card.py --pretty
```

Use this as the phase-space proof point:

```bash
python tools/fmm0_phase_table.py demo --pretty
```

Use this as the adversarial proof point:

```bash
python tools/fmm0_counterexample_forge.py demo --pretty
```

Use this as the memory-algebra proof point:

```bash
python tools/fmm0_closure_lab.py demo --pretty
```

Use this as the cross-layer projection proof point:

```bash
python tools/fmm0_boundary_bisim.py demo --pretty
```

Use this as the minimal-core diagnostic proof point:

```bash
python tools/fmm0_forbidden_core.py demo --pretty
```

Use this as the local evidence packet:

```bash
python tools/fmm0_witness_pack.py demo --pretty
```

Use this as the Solidity ABI/model drift gate:

```bash
python tools/flowpulse_boundary_abi.py check --pretty
```

Use this as the AI/GPU workflow reuse proof point:

```bash
python tools/cache_lineage_gate.py demo --pretty
python tools/compute_reuse_router.py demo --pretty
python tools/compute_reuse_consistency.py demo --pretty
```

Use this as the canonical offline launch transcript:

```bash
python tools/flowmemory_release_transcript.py --pretty
```

Use this as the reviewer credibility packet:

```bash
python tools/reviewer_walkthrough.py --pretty
```

Use this to check whether public Base Sepolia receipt evidence is ready:

```bash
python tools/verify_release_evidence.py --pretty
```

Current expected result before real receipt evidence exists:

```text
Public Base Sepolia receipt evidence: PENDING
Production verifier infrastructure: NOT_CLAIMED
```

Use this to explain each FlowLitmus case:

```bash
python tools/render_flowlitmus_casebook.py --check
```

Expected core thesis:

```text
Everyone treated agent memory like retrieval. FlowMemory treats it like a memory model.
```

## Verification

Local verification should include:

```bash
forge fmt --check
forge build
forge test -vvv
python -m unittest tools.test_read_flowpulse_logs tools.test_memory_trace tools.test_axiom_writ tools.test_axiom_patch tools.test_boundary_fission tools.test_pulse_retire tools.test_flow_mmu tools.test_flow_quiesce tools.test_flow_serial tools.test_flow_litmus tools.test_launch_reality_check tools.test_memory_consistency_card
python tools/launch_reality_check.py --pretty
python tools/memory_consistency_card.py --pretty
python -m unittest tools.test_fmm0_phase_table
python tools/fmm0_phase_table.py demo --pretty
python -m unittest tools.test_fmm0_counterexample_forge
python tools/fmm0_counterexample_forge.py demo --pretty
python -m unittest tools.test_fmm0_closure_lab
python tools/fmm0_closure_lab.py demo --pretty
python -m unittest tools.test_fmm0_boundary_bisim
python tools/fmm0_boundary_bisim.py demo --pretty
python -m unittest tools.test_fmm0_forbidden_core
python tools/fmm0_forbidden_core.py demo --pretty
python -m unittest tools.test_fmm0_witness_pack
python tools/fmm0_witness_pack.py demo --pretty
python -m unittest tools.test_flowpulse_boundary_abi
python tools/flowpulse_boundary_abi.py check --pretty
python -m unittest tools.test_cache_lineage_gate
python tools/cache_lineage_gate.py demo --pretty
python -m unittest tools.test_compute_reuse_router
python tools/compute_reuse_router.py demo --pretty
python -m unittest tools.test_compute_reuse_consistency
python tools/compute_reuse_consistency.py demo --pretty
python -m unittest tools.test_flowmemory_release_transcript
python tools/flowmemory_release_transcript.py --pretty
python -m unittest tools.test_reviewer_walkthrough
python tools/reviewer_walkthrough.py --pretty
python -m unittest tools.test_verify_release_evidence
python tools/verify_release_evidence.py --pretty
python -m unittest tools.test_flowlitmus_casebook
python tools/render_flowlitmus_casebook.py --check
git diff --check
```

GitHub Actions should show:

- `Foundry`: passing;
- `Repository hygiene`: passing.

## Strongest Public Claim

FlowMemory defines a runtime consistency model for agents using receipt-bound
FlowPulse boundaries.

Short version:

```text
FMM-0 is the FlowMemory Agent Memory Model.
FMM-0 Phase Space gives machine histories a phase diagram.
FMM-0 Counterexample Forge gives the model adversarial negative tests.
FMM-0 Closure Lab gives the model executable memory algebra.
FMM-0 Boundary Bisimulation gives the model cross-layer projection checks.
FMM-0 Forbidden Core Extractor gives the model minimal failure diagnostics.
FMM-0 Witness Pack gives the model a reproducible local evidence packet.
FlowPulse Boundary ABI keeps the Solidity event surface aligned with the memory model.
Cache Lineage Gate makes KV/context reuse proof-carried.
Compute Reuse Router turns proof-backed compute memory into a scheduler decision.
Compute Reuse Consistency requires cache lineage, compute fingerprint, and receipt-bound history to agree.
FlowMemory Release Transcript gives reviewers one offline object for passed, pending, and not-claimed launch state.
FlowSerial gives receipt-linearizability.
FlowLitmus makes forbidden outcomes executable.
FlowMemory Reality Check shows live histories pass and impossible histories fault.
Memory Consistency Card maps the launch claim to evidence and marks public-chain evidence pending.
Skeptic Walkthrough maps every public claim to evidence, commands, expected result, and non-claims.
Release Evidence Gate keeps public receipt evidence pending until a real Base Sepolia packet validates.
FlowLitmus Forbidden Outcomes names each impossible history and the fault that catches it.
```

## What To Share First

1. Repository root.
2. README `Launch Reality Check` section.
3. Terminal screenshot from `python tools/launch_reality_check.py --pretty`.
4. Terminal screenshot from `python tools/fmm0_phase_table.py demo --pretty`.
5. Terminal screenshot from `python tools/fmm0_counterexample_forge.py demo --pretty`.
6. Terminal screenshot from `python tools/fmm0_closure_lab.py demo --pretty`.
7. Terminal screenshot from `python tools/flowmemory_release_transcript.py --pretty`.
8. Optional cache/GPU-angle screenshot from `python tools/cache_lineage_gate.py demo --pretty`.
9. Optional GPU-angle screenshot from `python tools/compute_reuse_router.py demo --pretty`.
10. Optional systems-angle screenshot from `python tools/compute_reuse_consistency.py demo --pretty`.
7. Terminal screenshot from `python tools/fmm0_boundary_bisim.py demo --pretty`.
8. Terminal screenshot from `python tools/fmm0_forbidden_core.py demo --pretty`.
9. Terminal screenshot from `python tools/fmm0_witness_pack.py demo --pretty`.
10. Terminal screenshot from `python tools/flowpulse_boundary_abi.py check --pretty`.
11. Terminal screenshot from `python tools/memory_consistency_card.py --pretty`.
12. Terminal screenshot from `python tools/reviewer_walkthrough.py --pretty`.
13. `docs/PUBLIC_LAUNCH_COPY.md` for the exact public post and founder script.

## Remaining Launch Gaps

These are not repo-writing tasks. They require public chain evidence:

- Base Sepolia deployment transaction;
- source verification URL;
- at least one `AfterSwapObserved` log;
- at least one `FlowPulse` log;
- `RELEASE_EVIDENCE.json` with reader-generated receipt-derived `txHash` and `logIndex`;
- filled Base Sepolia release record.

Until those exist, use the repo as the launch artifact and avoid live deployment
claims.

## Claims To Avoid

- live mainnet deployment;
- audited production infrastructure;
- custody;
- fund protection;
- swap control;
- custom accounting;
- semantic truth;
- model correctness;
- GPU acceleration;
- production compute verifier;
- `txHash` or `logIndex` known inside the hook.
