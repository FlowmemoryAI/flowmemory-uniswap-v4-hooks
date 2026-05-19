# FMM-0 Boundary Bisimulation v0

FMM-0 Boundary Bisimulation is the cross-layer conformance artifact for the
FlowMemory Agent Memory Model.

It checks one question:

```text
Can the same FlowPulse boundary survive translation from hook signal, to receipt envelope, to runtime memory state?
```

The harness projects a FlowPulse through three layers:

- hook projection: the on-chain boundary signal without receipt-only metadata;
- receipt projection: reader-attached proof-envelope facts such as `txHash` and
  `logIndex`;
- runtime projection: FMM-0 live state that cites the same rootfield,
  commitment, and receipt facts.

It also mutates the projections to make sure cross-layer drift is caught:

- rootfield drift;
- commitment drift;
- runtime receipt drift;
- hook-time receipt metadata smuggling.

## Non-Claims

Boundary Bisimulation is not formal verification. It is not semantic truth,
model correctness, custody, fund protection, Base mainnet deployment,
production verifier infrastructure, or GPU acceleration.

It is a local cross-layer conformance harness for FlowPulse boundary semantics.
