# FlowMemory Memory Consistency Card

FlowMemory Memory Consistency Card is the launch-facing scorecard for the repo.

It makes the claim precise:

```text
Everyone treated agent memory like retrieval. FlowMemory treats it like a memory model.
```

This is the category shift.

Most AI memory products ask what an agent can retrieve.

FlowMemory asks whether the agent history could have happened.

The card is the launch scorecard for **FMM-0: FlowMemory Agent Memory Model**.

## Command

```bash
python tools/memory_consistency_card.py --pretty
```

Optional screenshot artifact:

```bash
python tools/memory_consistency_card.py --pretty \
  --write examples/memory-consistency-card/latest-output.txt
```

## Why This Exists

The hook is the launch anchor, but the hook alone is not the whole story.

The hook emits a FlowPulse at a verified Uniswap v4 `afterSwap` boundary. The
reader attaches receipt metadata later. FMM-0 Phase Space classifies
machine artifacts before and after that receipt boundary. FlowSerial checks
whether machine history can be serialized around those receipt-bound boundaries.
FlowLitmus turns forbidden outcomes into executable tests.

The card turns that stack into one reviewer-facing artifact.

It answers:

- what claim is being made;
- which repo files support each layer;
- which checks pass locally;
- which public-chain evidence is still pending;
- which claims must not be made.

## Consistency Ladder

The card separates local repo evidence from public release evidence:

| Level | Meaning | Launch Status |
| --- | --- | --- |
| `FM-C0` | Uniswap v4 reaches an `afterSwap` execution boundary. | Local repo evidence |
| `FM-C1` | Explicit `hookData` intentionally emits a FlowPulse. | Local repo evidence |
| `FM-C2` | Receipt metadata is not known inside the hook. | Local repo evidence |
| `FM-C3` | Reader infrastructure attaches receipt facts later. | Local repo evidence |
| `FM-C4` | Machine histories can be serialized around FlowPulse receipts. | Local repo evidence |
| `FM-C5` | Impossible histories fault under FlowLitmus. | Local executable evidence |
| `FM-C6` | FMM-0 Phase Space catches illegal machine-state phase jumps. | Local executable evidence |
| `FM-C7` | A real Base Sepolia release can attach public `txHash`/`logIndex` evidence. | Pending release evidence |

This matters because it prevents the launch from collapsing into either hype or
timidity.

FlowMemory can be bold about the new category:

```text
FlowMemory defines FMM-0, a receipt-bound memory consistency model for machine histories.
```

And precise about the current boundary:

```text
Public Base Sepolia receipt evidence is pending until the release record is filled.
```

The release evidence gate is:

```bash
python tools/verify_release_evidence.py --pretty
```

That command keeps `FM-C7` pending until `releases/base-sepolia/RELEASE_EVIDENCE.json`
and its referenced receipt artifacts validate.

The phase table demo is:

```bash
python tools/fmm0_phase_table.py demo --pretty
```

## What To Screenshot

Screenshot the output from:

```bash
python tools/memory_consistency_card.py --pretty
```

The strongest section is:

```text
Consistency ladder
  PASS    FM-C0  Execution boundary
  PASS    FM-C1  Intentional memory emission
  PASS    FM-C2  Receipt metadata separation
  PASS    FM-C3  Reader-derived proof envelope
  PASS    FM-C4  Receipt-linearizable histories
  PASS    FM-C5  Executable forbidden outcomes
  PASS    FM-C6  FMM-0 phase space
  PENDING FM-C7  Public Base Sepolia evidence
```

That is the honest launch shape: local consistency model proven, public release
evidence pending.

## Public Wording

Use this:

```text
FlowMemory is not treating agent memory like retrieval. It is treating memory like a consistency model.
```

Then:

```text
The Uniswap v4 afterSwap hook emits the FlowPulse boundary signal. FMM-0 Phase Space classifies machine-state phases. FlowSerial gives receipt-linearizability. FlowLitmus makes forbidden histories executable. The Memory Consistency Card maps the claim to evidence and shows what is still pending for public-chain release.
```

Short version:

```text
Most AI memory retrieves context. FlowMemory checks whether the memory could have happened.
```

## Non-Claims

The card is not a live mainnet deployment claim.

It is not an audited production verifier claim.

It is not semantic truth.

It is not model correctness.

It is not GPU acceleration.

It is the launch scorecard for a new memory-native runtime model anchored in a
Uniswap v4 `afterSwap` FlowPulse boundary.
