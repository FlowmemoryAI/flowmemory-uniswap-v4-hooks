# PulseWatch Example

This example documents the deterministic local PulseWatch demo.

Run:

```bash
python tools/pulse_watch.py demo
```

Expected:

```text
FlowMemory PulseWatch

Watch report:
  status: PASS
  records seen: 2
  records accepted: 2
  memory records written: 2
  cursor: 119 -> 121
```

PulseWatch is the always-on reader/verifier loop. It does not make the hook run
without transactions; it keeps watching for transactions that emit FlowPulse
events and turns them into append-only memory records.
