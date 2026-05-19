# FlowLitmus Forbidden Outcomes

FlowLitmus is the memory-model litmus suite for agent reality: each case names one impossible machine history and the FlowMemory fault that catches it.

FlowLitmus is not a dashboard, not retrieval, and not semantic truth. It is a casebook for FMM-0: each case names a machine history that should be impossible around receipt-bound FlowPulse boundaries.

Run the suite:

```bash
python tools/flow_litmus.py run --suite examples/flow-litmus/litmus.manifest.json
```

Expected:

```text
8/8 passed
```

## Casebook

### FM-LB-001: pre-receipt txHash read

Category: `receipt_mapping`

Impossible history: An agent reads txHash before reader-attached receipt metadata exists.

Why FlowPulse matters: The hook can emit a FlowPulse boundary signal, but txHash is a receipt fact. It cannot be read as hook-time memory.

Detected by: `FlowMMU`

Expected result: `forbidden_pre_receipt_read`

Case file: `examples/flow-litmus/cases/FM-LB-001-pre-receipt-deref.json`

### FM-SER-001: retrocausal receipt claim

Category: `serialization`

Impossible history: An agent event claims receipt facts before the FlowPulse boundary exists in the serial history.

Why FlowPulse matters: FMM-0 makes receipt-bound FlowPulses ordering anchors. The history cannot cite a receipt before that anchor exists.

Detected by: `FlowSerial`

Expected result: `retrocausal_receipt_claim`

Case file: `examples/flow-litmus/cases/FM-SER-001-retrocausal-claim.json`

### FM-QS-001: unquiesced post-boundary output

Category: `quiescence`

Impossible history: A pre-boundary frame publishes into post-boundary state without quiescing or revalidating.

Why FlowPulse matters: The receipt-bound FlowPulse advances the rootfield epoch. Old readers must reach a safe point before joining the new world.

Detected by: `FlowQuiesce`

Expected result: `QuiescenceViolation`

Case file: `examples/flow-litmus/cases/FM-QS-001-unquiesced-output.json`

### FM-RT-001: speculative output escaped

Category: `retirement`

Impossible history: A speculative model output becomes live before a matching FlowPulse receipt retires it.

Why FlowPulse matters: The FlowPulse receipt decides what can retire into live state. Speculation is allowed; unretired publication is not.

Detected by: `PulseRetire`

Expected result: `RetirementViolation`

Case file: `examples/flow-litmus/cases/FM-RT-001-unretired-output.json`

### FM-FIS-001: stale output survived boundary

Category: `fission`

Impossible history: Raw stale model output survives a receipt boundary as if the world had not changed.

Why FlowPulse matters: The receipt-bound boundary triggers memory release: conserve facts, compress stale context, quarantine unsupported claims, and recompute from the new boundary.

Detected by: `BoundaryFission`

Expected result: `BoundaryFissionViolation`

Case file: `examples/flow-litmus/cases/FM-FIS-001-stale-output-survives.json`

### FM-SER-002: rootfield rollback

Category: `serialization`

Impossible history: A canonical rootfield head moves backward after a receipt-bound FlowPulse advanced it.

Why FlowPulse matters: FlowPulse receipts are public ordering anchors. FMM-0 does not allow canonical memory to roll back beneath the proven boundary.

Detected by: `FlowSerial`

Expected result: `rootfield_rollback`

Case file: `examples/flow-litmus/cases/FM-SER-002-rootfield-rollback.json`

### FM-SER-003: split-brain canonical write

Category: `serialization`

Impossible history: Two incompatible writers both claim canonical state under incompatible FlowPulse heads.

Why FlowPulse matters: The receipt-bound FlowPulse gives machine state a public ordering surface. Competing canonical writes must serialize or fault.

Detected by: `FlowSerial`

Expected result: `split_brain_write`

Case file: `examples/flow-litmus/cases/FM-SER-003-split-brain-write.json`

### FM-OK-001: valid boundary history

Category: `valid_history`

Impossible history: None. This is the control case: a receipt-ordered history should serialize.

Why FlowPulse matters: The same boundary model that rejects impossible histories must accept a valid FlowPulse-ordered history.

Detected by: `FlowSerial`

Expected result: `Serializable`

Case file: `examples/flow-litmus/cases/FM-OK-001-valid-boundary-history.json`

## Non-Claims

- `not_semantic_truth`
- `not_model_correctness`
- `not_production_verifier_infrastructure`
- `not_custody`
- `not_swap_control`
- `not_gpu_acceleration`

Casebook ID: `sha256:47ecdce1819133b26d7ac270f726c08c99eefb2d94cc325b66a42ff472ffb814`
