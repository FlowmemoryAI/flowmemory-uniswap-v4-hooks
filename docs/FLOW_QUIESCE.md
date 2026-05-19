# FlowQuiesce

FlowQuiesce is receipt-triggered quiescence for autonomous agents and GPU
workflows.

FlowMemory gives agents a grace period for reality.

When a receipt-bound `FlowPulse` arrives, the rootfield has crossed a public
boundary. Any active agent or compute frame that read the old rootfield epoch
must reach a safe point before its output can join the post-boundary state.

## Why It Exists

AI agents do not just need memory. They need safe points.

A model can be halfway through a plan when the external world changes. A GPU
workflow can be processing context from a prior boundary. A tool-using agent can
have pending outputs based on a rootfield state that is now stale.

FlowQuiesce makes those active frames visible.

```text
FlowPulse receipt
  -> ReceiptEpoch advances
  -> active pre-boundary readers are identified
  -> grace period opens
  -> required frames quiesce / revalidate / fork / abandon
  -> grace period closes
```

## What It Is Not

This is not a workflow engine.
This is not action permission.
This is not cache invalidation.
This is not semantic truth.
This is not GPU acceleration.
This is not custody or swap control.

It is a public safe-point protocol for machine cognition.

## Demo

```bash
python tools/flow_quiesce.py demo --pretty
python -m unittest tools.test_flow_quiesce
```

Expected story:

```text
FlowPulse receipt advanced reality epoch.
frame-001 was an active pre-boundary reader.
frame-001 must quiesce.
frame-002 is unaffected.

Before ack:
  grace period open
  output-001 unsafe

After ack:
  grace period closed
  output-001 safe to join epoch 1
```

## Non-Claims

FlowQuiesce does not prove model output is true.
It does not prove semantic truth.
It does not prove GPU execution or hardware attestation.
It does not accelerate GPUs.
It does not control swaps.
It does not protect funds.
It does not have custody.
It is not audited production infrastructure.
It is not live mainnet infrastructure.
It does not mean the hook knows `txHash` or `logIndex`.

It identifies active frames that read pre-boundary context and requires a
quiescent acknowledgment before their outputs join post-boundary state.
