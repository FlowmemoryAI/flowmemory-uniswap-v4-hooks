# ComputePulse v0 Draft Spec

ComputePulse is the FlowMemory pattern applied to AI and GPU execution.

The GPU job is not the memory.

The scheduler receipt is not the memory.

The ComputePulse is the memory artifact.

## Category

ComputePulse is proof-backed memory for machine compute.

It does not make GPU hardware faster.

It makes GPU work rememberable, reusable, and provable.

## Boundary

A ComputePulse is born after a compute boundary:

```text
request -> scheduler -> worker -> GPU/model execution -> output artifact -> ComputePulse
```

The emitter can be:

- a local job wrapper;
- an inference sidecar;
- a DePIN worker;
- a model gateway;
- a confidential compute enclave;
- a scheduler-integrated memory service.

## Required Commitments

| Field | Meaning |
| --- | --- |
| `rootfieldId` | Memory namespace receiving the compute artifact. |
| `jobId` | Scheduler or worker job identifier. |
| `modelCommitment` | Commitment to model, weights, adapter, or endpoint. |
| `inputCommitment` | Commitment to prompt, batch, dataset shard, or request. |
| `outputCommitment` | Commitment to generated output or artifact. |
| `runtimeCommitment` | Commitment to runtime config, container, sampler, or dependencies. |
| `executor` | Worker, provider, node, or enclave identity. |
| `hardwareClass` | Declared execution tier or GPU class. |
| `attestationRef` | Optional pointer to hardware/runtime attestation. |
| `sourceCachePulse` | Optional context/KV reuse artifact. |
| `parentPulseId` | Prior memory artifact this job extends. |
| `uri` | Advisory pointer to private or public artifact metadata. |

## Reader-Attached Evidence

The reader/verifier attaches evidence after the compute job completes:

- scheduler receipt;
- worker completion record;
- output artifact hash;
- runtime metadata;
- executor identity;
- attestation pointer if available;
- storage pointer;
- timestamp;
- policy result;
- optional on-chain anchoring transaction.

## Canonical ID

```text
computePulseId = keccak256(
  "ComputePulse/v0",
  rootfieldId,
  jobId,
  modelCommitment,
  inputCommitment,
  outputCommitment,
  runtimeCommitment,
  executor,
  parentPulseId
)
```

## Reuse Path

ComputePulse becomes powerful when schedulers query memory before running work:

1. Receive request.
2. Compute model, input, and runtime commitments.
3. Query Rootflow for compatible prior ComputePulses.
4. Verify output, policy, and reuse rights.
5. Reuse, fork, or run new work.
6. Emit a new child ComputePulse for the decision.

This is where workflow speed can improve.

Not by changing CUDA.

By making the system less forgetful.

## Adjacent Pulses

ComputePulse is part of the machine-memory family:

- `CachePulse`: KV cache, prompt prefix, context bundle, or reuse event.
- `ModelPulse`: model output or generated artifact provenance.
- `AgentPulse`: autonomous workflow action or decision trail.

Example chain:

```text
AgentPulse
  -> reads FlowPulse
  -> reuses CachePulse
  -> runs ComputePulse
  -> creates ModelPulse
  -> writes memory back to Rootflow
```

## Minimal Proof Object

```json
{
  "schema": "flowmemory.computepulse.v0",
  "status": "verified",
  "computePulseId": "0x...",
  "rootfieldId": "0x...",
  "jobId": "gpu-job-001",
  "modelCommitment": "0x...",
  "inputCommitment": "0x...",
  "outputCommitment": "0x...",
  "runtimeCommitment": "0x...",
  "hardwareClass": "H100-class",
  "executor": "0x...",
  "parentPulseId": "0x...",
  "checks": {
    "jobReceiptFound": true,
    "outputCommitmentMatches": true,
    "runtimeCommitmentMatches": true,
    "executorMatches": true,
    "payloadPrivacyPreserved": true,
    "artifactUriIsAdvisory": true
  }
}
```

## Design Line

Logs are for humans. Pulses are for machines.
