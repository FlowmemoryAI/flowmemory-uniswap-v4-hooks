# Local Conformance, Not Enforcement

This repository is a launch-prep artifact for memory-native execution
boundaries and autonomous-commerce memory consistency.

It is not production enforcement infrastructure.

That distinction is not a weakness. It is the boundary that keeps the public
claim precise.

## The Claim

FlowMemory defines deterministic local conformance rules for memory-native
DeFi and autonomous agent commerce.

The repo shows whether a declared machine history is admissible under the
FlowMemory model:

- did the hook emit the FlowPulse boundary without pretending to know receipt
  facts;
- did the reader attach proof-envelope metadata later;
- did the agent spend follow a live memory head;
- did the compute route match the compute charge;
- did the receipt discharge the right obligation;
- did delegated work preserve the obligation constraints;
- did the commerce episode conserve obligation state.

That is local deterministic conformance.

## The Non-Claim

Do not claim from this repo:

- wallet enforcement;
- custody;
- escrow;
- fund protection;
- work-quality proof;
- semantic truth;
- model correctness;
- GPU hardware acceleration;
- live Base mainnet deployment;
- production verifier infrastructure.

## Why This Matters

Autonomous agents will not only need signatures and payments.

They will need a way to prove that a spend, receipt, compute route, memory head,
delegation path, and discharge all belong to one legal machine history.

Local conformance is the first hard surface for that category.

The hook emits the memory signal.

The reader proves where it landed.

The conformance harnesses ask whether the machine history built on top of that
signal could legally exist.

## Pressure-Test Answer

If someone says this is "just local validation," the answer is direct:

```text
Correct. These are local deterministic conformance harnesses. FlowMemory is
defining the memory-consistency surface before claiming production enforcement.
```

That is the honest launch boundary.
