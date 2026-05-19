# FlowMemory Runtime Model

FlowMemory is not only a memory story.

It is a runtime model for machine histories that cross public execution
boundaries.

The launch name for the draft model is **FMM-0: FlowMemory Agent Memory Model**.

## Core Split

FlowMemory separates four layers:

- execution: the Uniswap v4 swap lifecycle;
- emission: the `afterSwap` hook emits a FlowPulse;
- evidence: receipt readers attach `txHash`, `logIndex`, receipt status, block
  facts, and finality;
- memory: downstream FlowMemory / Rootflow systems use the FlowPulse as the
  memory artifact.

The swap is not the memory.

The transaction is the proof envelope.

The FlowPulse is the memory artifact.

## Runtime Rule

Receipt facts are not hook-time facts.

The hook does not know `txHash`, `transactionIndex`, `logIndex`, `blockHash`, or
receipt status during execution. Any machine history that claims those facts
before reader-attached receipt evidence exists is impossible under the
FlowMemory runtime model.

## Forbidden Outcomes

FlowMemory runtime semantics reject:

- pre-receipt dereference of receipt-only fields;
- retrocausal receipt claims;
- post-boundary publication from unquiesced pre-boundary frames;
- speculative artifacts escaping before retirement;
- stale raw memory surviving boundary fission;
- rootfield rollback;
- split-brain canonical writes under incompatible FlowPulse heads.

## Why This Matters

AI agents are becoming distributed systems. They have caches, concurrent
workers, model calls, tools, background tasks, GPU jobs, and state writers.

The failure mode is not only hallucination.

The failure mode is impossible history.

FlowMemory gives those systems public memory signals. FlowLitmus turns the
signals into executable forbidden outcomes.

## Memory Consistency Card

The launch scorecard is:

```bash
python tools/memory_consistency_card.py --pretty
```

It packages the runtime model as a claim-to-evidence ladder:

- `FM-C0`: execution boundary;
- `FM-C1`: intentional memory emission;
- `FM-C2`: receipt metadata separation;
- `FM-C3`: reader-derived proof envelope;
- `FM-C4`: receipt-linearizable histories;
- `FM-C5`: executable forbidden outcomes;
- `FM-C6`: public Base Sepolia receipt evidence.

`FM-C0` through `FM-C5` are local repo evidence. `FM-C6` remains pending until a
release record includes public receipt evidence.

The line to remember:

```text
Most AI memory retrieves context. FlowMemory checks whether the memory could have happened.
```
