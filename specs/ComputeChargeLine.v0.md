# Compute ChargeLine v0

Status: R&D draft.

Compute ChargeLine is a local consistency model for AI/GPU compute payments.
It does not custody funds, escrow payments, authorize wallets, prove work
quality, verify semantic truth, guarantee model correctness, accelerate GPUs,
prove hardware execution, or claim production attestation infrastructure.

It checks whether the payment mode for compute matches the memory-consistent
compute route.

## Schema

```json
{
  "schema": "flowmemory.compute_charge.v0",
  "chargeId": "compute-charge-001",
  "rootfieldId": "bytes32",
  "buyerMemoryHead": "flowpulse-buyer-compute-001",
  "expectedBuyerMemoryHead": "flowpulse-buyer-compute-001",
  "buyerComputePolicy": "ALLOWS_REUSE",
  "paymentRequirementHash": "sha256:compute-payment-001",
  "observedPaymentRequirementHash": "sha256:compute-payment-001",
  "paymentMode": "FRESH_COMPUTE",
  "chargeAlreadyConsumed": false,
  "attestationRequired": true,
  "attestationRef": "attestation:local-demo-ref",
  "expectedRuntimeCommitment": "sha256:runtime-cuda-vllm-001",
  "runtimeCommitment": "sha256:runtime-cuda-vllm-001",
  "computeRoute": {
    "routeDecision": "RUN_GPU_JOB",
    "computeReuseVerdict": "NOT_APPLICABLE",
    "cacheLineageVerdict": "NOT_APPLICABLE",
    "computePulseId": "computepulse-fresh-001"
  }
}
```

## Decisions

`CHARGE_ACCEPTED`: the charge matches the memory-consistent compute route.

`REJECT_CHARGE`: at least one charge invariant fails.

## Invariants

- `CCL-I1`: Payment mode matches compute route.
- `CCL-I2`: Unsafe reuse cannot close compute payment.
- `CCL-I3`: Fresh-compute policy cannot be laundered.
- `CCL-I4`: Payment requirement hash is stable.
- `CCL-I5`: Compute charge is single-use.
- `CCL-I6`: Required attestation reference is present.
- `CCL-I7`: Runtime commitment is stable.
- `CCL-I8`: Buyer memory head is current.

## Forbidden Cases

- reuse route charged as fresh;
- unsafe reuse charged;
- buyer requires fresh compute and seller reuses;
- duplicate compute charge;
- missing required attestation reference;
- runtime drift under same payment;
- payment requirement drift;
- stale buyer memory head.

## Non-Claims

Compute ChargeLine does not claim custody, escrow, wallet authorization, fund
protection, work-quality proof, semantic truth, model correctness, GPU
acceleration, hardware execution proof, production attestation infrastructure,
or live mainnet deployment.
