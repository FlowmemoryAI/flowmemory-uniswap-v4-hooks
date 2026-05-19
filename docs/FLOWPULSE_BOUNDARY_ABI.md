# FlowPulse Boundary ABI Conformance

The FlowPulse boundary must not drift.

FMM-0 depends on a strict split:

- hook-time fields are emitted by the Solidity event;
- receipt-time fields such as `txHash` and `logIndex` are attached later by the
  reader/verifier layer.

The Boundary ABI Conformance Gate checks that the Solidity event surface still
matches that model.

Run:

```bash
python tools/flowpulse_boundary_abi.py check --pretty
```

Expected result:

```text
ABI checks passed: 9/9
receipt-only fields exposed: 0
status: PASS
```

## What It Checks

- `FlowPulse` event exists;
- `FlowPulse` fields match the hook-time memory artifact schema;
- indexed boundary fields are `pulseId`, `rootfieldId`, and `actor`;
- receipt-only fields are absent from `FlowPulse`;
- receipt-only fields are absent from `AfterSwapObserved`;
- `sequence` and `occurredAt` stay `uint64`;
- `rootfieldId` and `commitment` stay present.

## Non-Claims

This is not formal verification. It is not production verifier
infrastructure. It is not semantic truth, model correctness, custody, fund
protection, Base mainnet deployment, or GPU acceleration.

It is a local ABI/model drift gate for the FlowPulse boundary.
