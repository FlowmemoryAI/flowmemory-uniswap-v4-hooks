# FMM-0 Witness Pack

The Witness Pack is the evidence-quality layer.

It does not add another primitive. It bundles the local conformance artifacts
into one reproducible packet a reviewer can run.

Run:

```bash
python tools/fmm0_witness_pack.py demo --pretty
```

Expected result:

```text
local conformance layers passed: 8/8
public Base Sepolia evidence: PENDING
escaped faults: 0
```

## What It Includes

- FMM-0 Phase Space;
- FMM-0 Counterexample Forge;
- FMM-0 Closure Lab;
- FMM-0 Boundary Bisimulation;
- FMM-0 Forbidden Core Extractor;
- FlowPulse Boundary ABI;
- FlowLitmus;
- Memory Consistency Card;
- pending-safe public Base Sepolia evidence status.

Each check includes a digest of the underlying local report. The result is a
single launch-facing witness packet: local conformance passes, public release
evidence stays pending until real receipt evidence exists.

## Non-Claims

The Witness Pack is not production verifier infrastructure. It is not semantic
truth, model correctness, custody, fund protection, Base mainnet deployment, or
GPU acceleration.

It is a reproducible local evidence packet for FMM-0.
