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
- `FlowMemory Memory Consistency Card`: a claim-to-evidence scorecard that shows
  FlowMemory is treating agent memory as a consistency model, not retrieval.
- `FMM-0 Skeptic Walkthrough`: a claim ledger that maps every launch claim to
  evidence, commands, expected results, status, and explicit non-claims.
- `Base Sepolia Evidence Gate`: a pending-safe verifier for the public release
  evidence packet.

## Launch Command

Use this as the screenshot-ready proof point:

```bash
python tools/launch_reality_check.py --pretty
```

Expected result:

```text
Result: FlowMemory can tell impossible histories from live ones using receipt-bound FlowPulse boundaries.
```

Use this as the launch positioning scorecard:

```bash
python tools/memory_consistency_card.py --pretty
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
python -m unittest tools.test_reviewer_walkthrough
python tools/reviewer_walkthrough.py --pretty
python -m unittest tools.test_verify_release_evidence
python tools/verify_release_evidence.py --pretty
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
FlowSerial gives receipt-linearizability.
FlowLitmus makes forbidden outcomes executable.
FlowMemory Reality Check shows live histories pass and impossible histories fault.
Memory Consistency Card maps the launch claim to evidence and marks public-chain evidence pending.
Skeptic Walkthrough maps every public claim to evidence, commands, expected result, and non-claims.
Release Evidence Gate keeps public receipt evidence pending until a real Base Sepolia packet validates.
```

## What To Share First

1. Repository root.
2. README `Launch Reality Check` section.
3. Terminal screenshot from `python tools/launch_reality_check.py --pretty`.
4. Terminal screenshot from `python tools/memory_consistency_card.py --pretty`.
5. Terminal screenshot from `python tools/reviewer_walkthrough.py --pretty`.
6. `docs/PUBLIC_LAUNCH_COPY.md` for the exact public post and founder script.

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
