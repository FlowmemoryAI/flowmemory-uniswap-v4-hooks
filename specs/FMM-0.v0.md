# FMM-0: FlowMemory Agent Memory Model

Status: draft launch model.

FMM-0 is the first FlowMemory memory model for agent histories anchored in
receipt-bound FlowPulse boundaries.

The core claim:

```text
Everyone treated agent memory like retrieval. FlowMemory treats it like a memory model.
```

FMM-0 is not a production standard, not a verifier network, and not semantic
truth. It is the local R&D model used by this repository to describe what an
agent may claim, cite, serialize, or reject around a FlowPulse boundary.

## Anchor

FMM-0 starts with the Uniswap v4 `afterSwap` hook.

The swap is not the memory.

The transaction is the proof envelope.

The FlowPulse is the memory artifact.

The hook emits the boundary signal. The reader attaches receipt metadata later.
The runtime model consumes that receipt-bound signal.

## Rules

### FMM-0.R0: Boundary Separation

A swap transaction, a FlowPulse, and reader-derived receipt metadata are
separate objects.

- The swap transaction is not memory.
- The transaction is the proof envelope.
- The FlowPulse is the memory artifact.
- `txHash`, `transactionIndex`, `logIndex`, `blockHash`, and receipt status are
  not hook-time facts.

### FMM-0.R1: Intentional Emission

Memory emission is explicit.

An opted-in swap path must provide FlowMemory `hookData` with a nonzero
`rootfieldId` and nonzero `commitment`. Ordinary transaction scraping is not
FMM-0 memory.

### FMM-0.R2: Receipt Mapping

Receipt facts become readable only after a reader maps them from actual chain
evidence.

Before mapping, a runtime can hold an expected FlowPulse pointer, but it cannot
dereference receipt-only fields.

### FMM-0.R3: Retirement

Speculative model outputs, cache candidates, and action drafts are not live
memory until a matching receipt-bound FlowPulse retires them.

If the boundary mismatches, the artifact is squashed, withheld, or recomputed.

### FMM-0.R4: Quiescence

When a receipt-bound FlowPulse advances a rootfield epoch, active pre-boundary
frames that read the old epoch must quiesce, revalidate, fork, or abandon before
joining post-boundary state.

### FMM-0.R5: Serialization

Agent histories must serialize around the FlowPulse receipt boundaries they
claim to observe.

Retrocausal receipt claims, rootfield rollbacks, and split-brain canonical
writes are impossible histories under FMM-0.

### FMM-0.R6: Forbidden Outcomes

FMM-0 is testable through litmus cases.

A runtime that accepts pre-receipt `txHash` reads, stale post-boundary outputs,
unretired speculative outputs, rootfield rollback, or split-brain writes is not
conforming to this draft model.

## Non-Claims

FMM-0 does not prove semantic truth.

FMM-0 does not prove model correctness.

FMM-0 is not audited production infrastructure.

FMM-0 is not a mainnet deployment claim.

FMM-0 does not make GPUs faster.

FMM-0 does not make the hook enforce agent runtime behavior. The hook emits the
boundary signal; runtime tools demonstrate the memory model around that signal.
