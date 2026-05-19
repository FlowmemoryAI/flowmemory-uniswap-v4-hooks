# FlowQuiesce Example

FlowQuiesce is receipt-triggered quiescence for agent runtimes.

```text
FlowPulse receipt arrives
  -> ReceiptEpoch advances
  -> active pre-boundary readers must quiesce
  -> outputs stay unsafe until ack
  -> grace period closes
```

Run the demo:

```bash
python tools/flow_quiesce.py demo --pretty
```

Regenerate artifacts:

```bash
python tools/flow_quiesce.py advance \
  --flowpulse examples/flow-quiesce/flowpulse.matching.json \
  --previous-epoch examples/flow-quiesce/epoch.0.json \
  --out examples/flow-quiesce/epoch.1.json \
  --pretty

python tools/flow_quiesce.py scan \
  --epoch examples/flow-quiesce/epoch.1.json \
  --frames examples/flow-quiesce/agent-frames.active.json \
  --out examples/flow-quiesce/quiescence-request.example.json \
  --pretty

python tools/flow_quiesce.py certify \
  --request examples/flow-quiesce/quiescence-request.example.json \
  --out examples/flow-quiesce/quiescence-certificate.open.json \
  --pretty

python tools/flow_quiesce.py ack \
  --request examples/flow-quiesce/quiescence-request.example.json \
  --frame-id frame-001 \
  --mode revalidated \
  --out examples/flow-quiesce/ack.frame-001.json \
  --pretty

python tools/flow_quiesce.py certify \
  --request examples/flow-quiesce/quiescence-request.example.json \
  --acks examples/flow-quiesce/ack.frame-001.json \
  --out examples/flow-quiesce/quiescence-certificate.closed.json \
  --pretty
```

Launch sentence:

```text
FlowMemory gives agents a grace period for reality.
```
