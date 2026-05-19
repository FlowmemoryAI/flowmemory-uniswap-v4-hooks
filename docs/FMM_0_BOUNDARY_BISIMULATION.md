# FMM-0 Boundary Bisimulation

FlowMemory's core claim depends on a boundary surviving translation.

The hook emits a FlowPulse.

The reader attaches receipt metadata.

FMM-0 runtime state cites that proof envelope.

Boundary Bisimulation checks that those are the same boundary, not three
similar-looking stories.

Run:

```bash
python tools/fmm0_boundary_bisim.py demo --pretty
```

Expected result:

```text
Projection checks: 8
Bisimulations preserved: 4/4
Drift cases rejected: 4/4
Escaped: 0
```

## Why This Matters

Most demos break at layer boundaries.

The event looks clean. The receipt reader adds metadata. The runtime consumes a
derived object. Somewhere in that translation, meaning can drift.

Boundary Bisimulation makes the drift executable:

- hook projection cannot contain `txHash` or `logIndex`;
- receipt projection must preserve hook boundary identity;
- runtime projection must preserve receipt identity;
- rootfield drift, commitment drift, receipt drift, and hook-time metadata
  smuggling are rejected.

This is the cross-layer credibility layer. It shows that FlowMemory is not only
emitting an event. It is preserving boundary semantics across the hook, proof
envelope, and runtime memory model.

## Non-Claims

Boundary Bisimulation is not semantic truth verification. It is not model
correctness. It is not a production verifier, audited custody system, mainnet
deployment claim, fund-protection claim, or GPU acceleration claim.

It is a local conformance harness for boundary semantics.
