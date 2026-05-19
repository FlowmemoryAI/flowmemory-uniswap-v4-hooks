# FlowMemory Memory Model

FlowMemory is not only proposing a hook.

It is proposing a memory model for machines that cross public execution
boundaries.

The launch model is **FMM-0: FlowMemory Agent Memory Model**.

```text
Everyone treated agent memory like retrieval. FlowMemory treats it like a memory model.
```

## Why This Is Different

Most AI memory systems optimize retrieval:

- which text is relevant;
- which vector is close;
- which summary should be remembered;
- which context window should receive the memory.

FlowMemory starts from a harder systems question:

```text
Could this memory history have happened?
```

That is why the Uniswap v4 hook matters. It gives the repo a public execution
boundary that can emit a FlowPulse. The FlowPulse becomes the memory artifact.
The receipt becomes the proof envelope. Reader-derived metadata gives machines a
shared ordering surface.

## FMM-0 In One Sentence

FMM-0 is a receipt-bound consistency model for agent memory.

It says an agent history must respect the FlowPulse boundaries it claims to
observe.

## Model Stack

```text
Uniswap v4 afterSwap boundary
  -> FlowPulse memory artifact
  -> transaction proof envelope
  -> reader-attached receipt facts
  -> FlowSerial serial history
  -> FlowLitmus forbidden outcomes
  -> Memory Consistency Card
```

The hook is deliberately narrow because FMM-0 is not execution control.

The hook emits the boundary signal. The runtime model decides what machine
histories can safely claim after that signal exists.

## Conformance

Generate the conformance matrix:

```bash
python tools/render_fmm0_matrix.py \
  --manifest examples/memory-model/fmm0.manifest.json \
  --out docs/FMM_0_CONFORMANCE_MATRIX.md
```

Run the public launch card:

```bash
python tools/memory_consistency_card.py --pretty
```

Run the executable forbidden outcomes:

```bash
python tools/flow_litmus.py run --suite examples/flow-litmus/litmus.manifest.json
```

## Safe Public Claim

Use:

```text
FlowMemory defines FMM-0, a receipt-bound memory consistency model for machine histories.
```

Then:

```text
The Uniswap v4 hook emits the FlowPulse boundary signal. The reader attaches receipt metadata. FlowSerial gives receipt-linearizability. FlowLitmus makes forbidden outcomes executable.
```

## What FMM-0 Is Not

FMM-0 is not a production standard.

FMM-0 is not audited production infrastructure.

FMM-0 is not semantic truth.

FMM-0 is not model correctness.

FMM-0 is not GPU acceleration.

FMM-0 does not mean the hook controls swaps. The hook emits memory. The runtime
model consumes receipt-bound memory artifacts.
