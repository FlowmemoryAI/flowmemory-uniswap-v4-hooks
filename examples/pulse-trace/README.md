# Pulse Trace Example

This example shows the machine-memory path FlowMemory is building toward:

```text
FlowPulse -> ComputePulse -> ModelPulse -> Rootflow
```

The current repository proves the first artifact: a FlowPulse emitted from a Uniswap v4 `afterSwap` boundary.

The ComputePulse and ModelPulse entries in this example are draft R&D artifacts. They show the intended shape of AI/GPU memory without claiming a deployed compute verifier.

## Why This Exists

The public launch should make the category visible:

- DeFi execution can emit FlowPulse.
- GPU work can emit ComputePulse.
- Model output can emit ModelPulse.
- Rootflow can connect them into memory a machine can verify and reuse.

## Files

- `trace.example.json`: sample machine-memory trace.

## Core Message

The swap is not the memory.

The GPU job is not the memory.

The model output is not the memory.

The pulse is the memory artifact.
