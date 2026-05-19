# DischargeLine v0

Status: R&D draft.

DischargeLine is a local deterministic consistency model for receipt-bound
obligation discharge. It does not custody funds, escrow payments, authorize
wallets, enforce payment, prove work quality, verify semantic truth, guarantee
model correctness, accelerate GPUs, or claim live mainnet deployment.

It checks whether a receipt closes the right obligation under FlowMemory's
agent-commerce memory stack.

## Schema

```json
{
  "schema": "flowmemory.dischargeline_discharge.v0",
  "dischargeId": "discharge-001",
  "kind": "work_payment",
  "obligationId": "obl-agent-work-001",
  "expectedObligationId": "obl-agent-work-001",
  "spendIntentCommitment": "sha256:spend-intent-001",
  "expectedSpendIntentCommitment": "sha256:spend-intent-001",
  "expectedRecipient": "seller-agent-001",
  "expectedPaymentRequirementHash": "sha256:x402-payment-001",
  "receiptEnvelope": {
    "txHash": "0x...",
    "logIndex": 7,
    "receiptStatus": "success",
    "obligationId": "obl-agent-work-001",
    "spendIntentCommitment": "sha256:spend-intent-001",
    "recipient": "seller-agent-001",
    "paymentRequirementHash": "sha256:x402-payment-001"
  },
  "postSpendFlowPulseId": "flowpulse-post-spend-001",
  "fmm0State": "FMM0_LIVE",
  "conservationVerdict": "CONSERVED",
  "membraneVerdict": "MEMBRANE_ACCEPTED",
  "computeChargeLineVerdict": "NOT_APPLICABLE",
  "alreadyDischarged": false,
  "childRefusalOpen": false
}
```

## Decisions

`DISCHARGE_ACCEPTED`: the receipt can discharge the declared obligation.

`REJECTED`: at least one discharge invariant fails.

## Invariants

- `DCL-I1`: Receipt Required.
- `DCL-I2`: Receipt-Obligation Binding.
- `DCL-I3`: Post-Spend Memory Boundary.
- `DCL-I4`: FMM-0 Discharge State.
- `DCL-I5`: Conservation Compatibility.
- `DCL-I6`: Membrane Compatibility.
- `DCL-I7`: Compute Route Compatibility.
- `DCL-I8`: Single Discharge.
- `DCL-I9`: No Semantic Completion Upgrade.
- `DCL-I10`: Receipt-Time Discipline.

## Forbidden Cases

- wrong obligation receipt;
- wrong recipient discharge;
- stale quote discharge;
- duplicate discharge;
- discharge without receipt;
- discharge after child refusal;
- compute route mismatch discharge;
- missing post-spend FlowPulse;
- semantic completion overclaim;
- receipt fields in pre-discharge obligation fields.

## Non-Claims

DischargeLine does not claim custody, escrow, wallet authorization, fund
protection, work-quality proof, semantic truth, model correctness, GPU
acceleration, production verifier readiness, or live mainnet deployment.
