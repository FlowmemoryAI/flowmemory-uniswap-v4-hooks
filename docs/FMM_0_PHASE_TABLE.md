# FMM-0 Phase Space

Memory is the wrong first word.

Before retrieval, before context, before storage, a machine artifact has a
phase.

The Reality Phase Table is the rendered view of FMM-0 Phase Space.

FMM-0 Phase Space defines four axes:

1. receipt stage;
2. reality phase;
3. operation surface;
4. authority level.

A FlowPulse boundary changes the phase space because receipt metadata does not
exist inside the hook. The hook emits the FlowPulse memory artifact. The
transaction is the proof envelope. The reader attaches `txHash` and `logIndex`
later.

The Phase Table makes that visible.

It shows why a pre-receipt local output is not the same kind of thing as a
reader-derived FlowPulse or an FMM-0-conforming machine history.

## Launch Sentence

```text
FlowMemory gives machine state a phase diagram.
```

The sharper technical line:

```text
Retrieval treats memory as text; FMM-0 treats machine history as a phase space with forbidden transitions.
```

## What It Catches

The table makes three launch-critical boundaries executable:

- a local model output cannot jump directly into FMM-0-conforming live state;
- a pre-receipt artifact cannot claim `txHash` or `logIndex`;
- a reader-derived FlowPulse can become eligible for FlowSerial and FlowLitmus
  checks.
- receipt evidence alone is not FMM-0 live history; the history still has to
  pass consistency checks.

Run:

```bash
python tools/fmm0_phase_table.py demo --pretty
```

Expected result:

```text
Result: FMM-0 treats machine memory as phase space, not retrieval text.
```

## The Core Rule

```text
No artifact may jump from local-only/speculative to
FMM-0-conforming/live without reader-derived receipt metadata and consistency
checks.
```

This is the difference between a memory story and a memory model.

## Why afterSwap Matters

The Uniswap v4 `afterSwap` hook gives FlowMemory a verified on-chain emission
boundary. The FlowPulse is emitted at the boundary, but receipt-only facts still
do not exist inside the hook.

That split is the point.

The Phase Table turns the split into machine-state law:

- hook-time artifact: no `txHash` or `logIndex`;
- reader-derived artifact: receipt metadata attached after the transaction
  lands;
- FMM-0 artifact: consistency-checked machine history around the boundary.

## What This Is Not

FMM-0 Phase Space is not:

- semantic truth;
- model correctness;
- GPU acceleration;
- custody;
- fund protection;
- live Base mainnet evidence;
- audited infrastructure;
- production verifier infrastructure.

It is a local R&D artifact that classifies machine artifacts around FlowPulse
receipt boundaries and catches illegal phase transitions.
