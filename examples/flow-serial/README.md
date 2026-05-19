# FlowSerial Examples

FlowSerial checks whether a machine history can be serialized around
receipt-bound FlowPulse boundaries.

Run the full demo:

```bash
python tools/flow_serial.py demo --pretty
```

Regenerate example artifacts:

```bash
python tools/flow_serial.py certify \
  --history examples/flow-serial/history.valid.json \
  --out examples/flow-serial/certificate.valid.json \
  --pretty

python tools/flow_serial.py certify \
  --history examples/flow-serial/history.retrocausal.json \
  --out examples/flow-serial/fault.retrocausal.json \
  --pretty

python tools/flow_serial.py certify \
  --history examples/flow-serial/history.rollback.json \
  --out examples/flow-serial/fault.rollback.json \
  --pretty

python tools/flow_serial.py certify \
  --history examples/flow-serial/history.split-brain.json \
  --out examples/flow-serial/fault.split-brain.json \
  --pretty
```

Expected story:

- `history.valid.json` serializes a draft, a FlowPulse receipt boundary, and a post-boundary model output.
- `history.retrocausal.json` faults because a model output claims `txHash` before the receipt boundary exists in the history.
- `history.rollback.json` faults because the rootfield head moves backward after a FlowPulse boundary advanced it.
- `history.split-brain.json` faults because two canonical writers use incompatible FlowPulse heads for the same exclusive state key.

The hook still does not know `txHash` or `logIndex` during execution. FlowSerial
only uses receipt facts after a reader/verifier attaches them to the FlowPulse
proof envelope.
