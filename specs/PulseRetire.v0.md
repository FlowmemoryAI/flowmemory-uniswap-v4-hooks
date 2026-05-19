# PulseRetire v0 Draft Spec

PulseRetire is receipt-driven retirement for speculative machine cognition.

Agents and GPU workflows can compute ahead, but speculative artifacts cannot
become live until a matching FlowPulse proof envelope retires them.

Category sentence:

> FlowMemory gives AI agents a reorder buffer for reality: they can compute
> speculatively, but only receipt-bound FlowPulses can retire those thoughts into
> live action.

## Queue Schema

```json
{
  "schema": "flowmemory.pulse_retire_queue.v0",
  "queueId": "sha256:...",
  "queueType": "receipt_driven_retirement_queue",
  "agentId": "demo-agent",
  "rootfieldId": "0x...",
  "retirementMode": "in_order",
  "entries": [
    {
      "entryId": "sha256:...",
      "queuePosition": 0,
      "artifactId": "model-output-001",
      "artifactType": "ModelPulseDraft",
      "artifactState": "speculative",
      "createdBeforeReceipt": true,
      "artifactCommitment": "sha256:...",
      "expectedPulse": {
        "boundary": "uniswap_v4_afterSwap",
        "rootfieldId": "0x...",
        "commitment": "0x...",
        "hookAddress": "0x...",
        "subjectPoolId": "0x...",
        "parentPulseId": "0x..."
      },
      "forbiddenAtEnqueue": [
        "txHash",
        "logIndex",
        "transactionIndex",
        "blockHash"
      ],
      "onRetire": [
        "release_model_output",
        "allow_as_live_context"
      ],
      "onSquash": [
        "withhold_model_output",
        "require_fresh_compute"
      ]
    }
  ],
  "notClaims": [
    "not_financial_debt",
    "not_token",
    "not_custody",
    "not_swap_control",
    "not_semantic_truth",
    "not_gpu_attestation",
    "not_hardware_acceleration"
  ]
}
```

## Retirement Schema

```json
{
  "schema": "flowmemory.pulse_retirement.v0",
  "retirementId": "sha256:...",
  "queueId": "sha256:...",
  "entryId": "sha256:...",
  "artifactId": "model-output-001",
  "status": "retired",
  "retiredBy": {
    "artifactType": "FlowPulse",
    "boundary": "uniswap_v4_afterSwap",
    "chainId": "84532",
    "hookAddress": "0x...",
    "txHash": "0x...",
    "logIndex": "7",
    "blockNumber": "123456",
    "receiptStatus": "success",
    "pulseId": "0x...",
    "rootfieldId": "0x...",
    "commitment": "0x...",
    "subjectPoolId": "0x...",
    "parentPulseId": "0x..."
  },
  "causalNonce": "sha256:...",
  "effects": [
    "release_model_output",
    "allow_as_live_context"
  ],
  "squashReasons": [],
  "checks": {
    "flowPulseRecordFound": true,
    "readerAttachedTxHash": true,
    "readerAttachedLogIndex": true,
    "receiptStatusSuccess": true,
    "rootfieldMatches": true,
    "commitmentMatches": true,
    "hookAddressMatches": true,
    "subjectPoolMatches": true,
    "noReceiptFieldsAtEnqueue": true
  }
}
```

## Required Discipline

At enqueue time, an artifact must not contain receipt-only fields:

- `txHash`;
- `logIndex`;
- `transactionIndex`;
- `blockHash`.

At retirement time, a matching FlowPulse must have:

- reader-attached `txHash`;
- reader-attached `logIndex`;
- successful receipt status;
- matching `rootfieldId`;
- matching `commitment`;
- matching `hookAddress`;
- matching `subjectPoolId`.

If those checks pass, the artifact retires into live state.
If receipt metadata is missing, the artifact stays speculative.
If a checked field mismatches, the artifact is squashed.

## Causal Nonce

`causalNonce` is minted only after retirement:

```text
H(chainId, hookAddress, txHash, logIndex, rootfieldId, commitment, subjectPoolId)
```

The nonce cannot exist before reader-attached receipt metadata exists.

## Systems Analogy

CPUs can execute speculatively, but results become architecturally visible only
when they retire.

PulseRetire applies that discipline to AI agents and GPU workflows:

```text
compute ahead, but retire only against a public execution boundary.
```
