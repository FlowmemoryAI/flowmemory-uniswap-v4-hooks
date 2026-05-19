# FMM-0 Phase Space Examples

This directory contains the executable fixtures for the FMM-0 Reality Phase
Table.

Run:

```bash
python tools/fmm0_phase_table.py demo --pretty
```

The demo classifies four machine artifacts:

- a pre-receipt local model output;
- a reader-derived FlowPulse;
- an FMM-0-conforming machine history;
- an invalid artifact that smuggles `txHash` and `logIndex` before receipt
  attachment.

The point is not to prove semantic truth. The point is to make receipt-stage
separation visible and executable.
