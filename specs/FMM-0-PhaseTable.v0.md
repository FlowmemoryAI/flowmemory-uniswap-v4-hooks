# FMM-0 Phase Table v0

FMM-0 Phase Table is a local R&D artifact for classifying machine artifacts
around FlowPulse receipt boundaries.

It does not claim semantic truth, model correctness, GPU acceleration, custody,
fund protection, Base mainnet deployment, audited infrastructure, or production
verifier infrastructure.

It defines a phase coordinate:

```text
(receiptStage, realityPhase, operationSurface, authorityLevel)
```

and a transition rule:

```text
No artifact may move from local-only speculative state into
FMM-0-conforming live state without reader-derived receipt metadata and
consistency checks.
```

## Axes

`receiptStage` separates hook-time artifacts from receipt-attached artifacts:

- `before_receipt`: txHash and logIndex are not available to the hook or local
  artifact.
- `after_receipt`: reader/verifier infrastructure has attached receipt-derived
  facts.

`realityPhase` names the artifact's current machine-state phase:

- `speculative`
- `live`
- `quarantined`
- `extinct`

`operationSurface` names the operations the artifact may ask a machine to take:

- `cite`
- `act`
- `forget`
- `recompute`
- `refuse`
- `split`
- `merge`
- `publish`

`authorityLevel` names where the artifact's authority comes from:

- `local_only`
- `public_boundary`
- `reader_derived`
- `fmm0_conforming`

## Receipt Separation

The hook emits the FlowPulse memory artifact. The transaction is the proof
envelope. The reader attaches `txHash`, `transactionIndex`, `logIndex`, block
metadata, and receipt status after execution.

A before-receipt artifact that claims `txHash` or `logIndex` is invalid under
this table.

## Non-Claims

The phase table is not a production verifier. It is not a semantic truth engine.
It is not model correctness infrastructure. It is not GPU acceleration. It is a
launch-facing state grammar for machine artifacts around FlowPulse boundaries.
