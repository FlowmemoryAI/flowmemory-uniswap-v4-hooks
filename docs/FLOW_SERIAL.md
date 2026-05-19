# FlowSerial

FlowSerial is receipt-linearizability for machine cognition.

FlowMemory gives agents linearizability against reality.

An AI agent can generate a story. FlowSerial checks whether that story could
have happened.

## Why It Exists

AI agents increasingly behave like distributed systems. They run model calls,
tool calls, background workers, GPU jobs, cache reuse, planner loops, and state
writes across time.

The failure mode is not only hallucination.

It is impossible history.

Examples:

- a model output cites `txHash` before receipt metadata existed;
- a later state write rolls a rootfield head back behind a FlowPulse it already
  observed;
- two workers both claim canonical post-boundary state under incompatible
  FlowPulse heads;
- a cache reuse artifact says it used the latest market boundary, but its
  machine clock does not include that boundary.

Normal AI memory systems store those contradictions as text.

FlowSerial treats them as consistency errors.

## The Category

FlowSerial compiles an agent's outputs, tool calls, and state writes into a
single serial history around FlowPulse receipt boundaries. If the history can be
serialized, FlowSerial emits a certificate. If it cannot, FlowSerial emits a
typed fault.

```text
machine history
  -> FlowSerial
  -> serial schedule
     or
  -> typed impossibility fault
```

This is not memory storage.
This is not retrieval.
This is not a proof explorer.
This is not a workflow engine.
This is not semantic truth.

It is a systems property for autonomous agents: receipt-linearizability against
public execution boundaries.

## Why FlowPulse Matters

If the ordering source is local, the agent can rewrite it.

If it is a SaaS API log, the service can backfill it.

If it is a model transcript, the model can hallucinate it.

FlowSerial needs a boundary the agent cannot self-author:

- a FlowPulse emitted at the Uniswap v4 `afterSwap` boundary;
- reader-attached `txHash`;
- reader-attached `logIndex`;
- receipt status;
- block, transaction, and log ordering;
- hook address;
- rootfield;
- commitment;
- pool context.

The hook still does not know `txHash` or `logIndex` during execution. That is
the point. Receipt-only facts appear later and become ordering anchors for
machine cognition.

Without FlowPulse, this is timeline linting.

With FlowPulse, it is receipt-linearizability against a DeFi execution boundary.

## Faults

FlowSerial currently detects:

- `retrocausal_receipt_claim`: a machine event claims receipt facts before the
  FlowPulse receipt boundary exists in the history;
- `rootfield_rollback`: a later event moves a rootfield head backward after it
  observed a newer FlowPulse boundary;
- `split_brain_write`: two exclusive writers use incompatible FlowPulse heads;
- `missing_receipt_metadata`: the boundary is not receipt-bound enough to order
  cognition;
- `failed_receipt_boundary`: the boundary is not a successful FlowPulse
  afterSwap receipt boundary;
- `impossible_schedule`: local ordering constraints contradict each other.

## Demo

```bash
python tools/flow_serial.py demo --pretty
python -m unittest tools.test_flow_serial
```

Expected story:

```text
Valid history:
  serializable

Retrocausal history:
  impossible: model output claimed txHash before receipt boundary

Rollback history:
  impossible: rootfield head moved backward

Split-brain history:
  impossible: incompatible canonical writers
```

## Founder Script

AI agents are becoming distributed systems. They run model calls, tools, compute
jobs, state writes, and cache reuse across time. The failure mode is not just
hallucination. It is impossible history.

FlowMemory starts with a Uniswap v4 `afterSwap` hook that emits a FlowPulse.
The swap is not memory. The transaction is the proof envelope. The FlowPulse is
the memory artifact. The reader attaches receipt facts like `txHash` and
`logIndex` later.

FlowSerial is the next primitive. It compiles an agent's outputs, tool calls,
and state writes into a serial history around FlowPulse receipt boundaries. If
the history can be serialized, it emits a certificate. If not, it emits a fault:
retrocausal claim, rootfield rollback, split-brain write, impossible schedule.

This gives agents linearizability against reality.

## Non-Claims

FlowSerial does not prove AI outputs are true.
It does not prove model correctness.
It does not prove semantic truth.
It does not prove GPU execution or hardware attestation.
It does not accelerate GPUs.
It does not control swaps.
It does not protect funds.
It does not have custody.
It is not audited production infrastructure.
It is not live mainnet infrastructure.
It does not mean the hook knows `txHash` or `logIndex`.
It does not replace consensus.
It does not replace workflow engines.

FlowSerial is a local R&D primitive for receipt-linearizable machine histories.
