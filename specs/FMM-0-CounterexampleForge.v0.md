# FMM-0 Counterexample Forge v0

FMM-0 Counterexample Forge is a local adversarial test artifact for FlowMemory's
receipt-bound memory model.

It does not store memories. It does not retrieve context. It does not rank
semantic relevance.

It forges impossible machine histories and checks whether FMM-0 catches them.

## Purpose

Most agent-memory benchmarks ask:

```text
Can the agent remember the right thing?
```

Counterexample Forge asks:

```text
Can this machine history be rejected when it could not have happened?
```

That is the useful difference.

## Counterexample Shape

A counterexample has:

- an `id`;
- a `mutation`;
- a `target`;
- an expected fault;
- an observed fault;
- a caught/not-caught result;
- explicit non-claims.

## Required Mutants

The launch suite must include mutants for:

- pre-receipt `txHash` smuggling;
- pre-receipt `logIndex` smuggling;
- local-only speculative state jumping directly to FMM-0 live state;
- reader-derived live state jumping to FMM-0 live state without consistency
  checks;
- rootfield/commitment mismatch during annealing;
- local-only `publish_as_live`;
- reader-derived semantic-truth overclaim;
- reader-derived model-correctness overclaim.

## Non-Claims

Counterexample Forge is not a proof of semantic truth.

It is not a proof of model correctness.

It is not a production verifier.

It is not GPU acceleration.

It is not public Base mainnet evidence.

It is a local adversarial harness for FMM-0's forbidden state transitions.
