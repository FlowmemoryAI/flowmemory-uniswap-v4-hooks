# FlowPulse Boundary ABI v0

FlowPulse Boundary ABI is the conformance surface between the Solidity hook
event and the FMM-0 runtime model.

It checks that:

- `FlowPulse` exposes the hook-time memory artifact fields;
- `pulseId`, `rootfieldId`, and `actor` remain indexed boundary fields;
- `rootfieldId`, `commitment`, `sequence`, and `occurredAt` remain present;
- `txHash`, `transactionIndex`, `logIndex`, block facts, receipt status, and
  finality are not hook-time event fields;
- `AfterSwapObserved` also excludes receipt-only metadata.

The ABI gate does not claim production verification. It does not claim semantic
truth, model correctness, custody, fund protection, Base mainnet deployment, or
GPU acceleration.

It checks ABI/model drift for the FlowPulse boundary.
