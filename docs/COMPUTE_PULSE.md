# ComputePulse: Memory For AI And GPU Workloads

ComputePulse is the FlowMemory pattern applied to AI and GPU execution.

The GPU job is not the memory.

The compute receipt is the proof envelope.

The ComputePulse is the memory artifact.

## Why ComputePulse Exists

AI infrastructure is moving from raw compute to remembered compute.

Large systems do not only need more GPUs. They need better memory of what those GPUs already did.

A GPU can execute an inference run, embedding batch, evaluation, training step, or checkpoint job. But the meaning of that work is usually scattered across:

- job logs;
- cloud metrics;
- private databases;
- model-serving traces;
- output files;
- dashboards;
- queue metadata;
- human screenshots.

ComputePulse turns GPU work into a structured memory signal.

## The Core Parallel

| DeFi FlowPulse | AI/GPU ComputePulse |
| --- | --- |
| Swap completes | GPU job completes |
| `afterSwap` boundary | post-compute boundary |
| FlowPulse emitted | ComputePulse emitted |
| Transaction receipt is the proof envelope | Compute receipt is the proof envelope |
| FlowPulse is the memory artifact | ComputePulse is the memory artifact |
| Reader attaches `txHash` and `logIndex` | Reader attaches runtime, executor, and attestation facts |
| Rootflow indexes protocol memory | Rootflow indexes compute memory |

## What A ComputePulse Commits To

A ComputePulse can commit to:

- `jobId`: job identifier from the scheduler or compute network;
- `modelCommitment`: hash or commitment for model name, version, weights, adapter, or endpoint;
- `inputCommitment`: hash or commitment for the prompt, batch, dataset shard, or request;
- `outputCommitment`: hash or commitment for the output artifact;
- `runtimeCommitment`: hash of runtime config, sampler settings, dependencies, or container image;
- `hardwareClass`: declared GPU class or execution tier;
- `executor`: worker, node, provider, or enclave identity;
- `attestationRef`: optional pointer to hardware/runtime attestation evidence;
- `parentPulseId`: prior memory artifact that the job depends on;
- `sequence`: sequence within a rootfield;
- `occurredAt`: reader-attached completion time or block/time source;
- `uri`: advisory artifact pointer;
- `rootfieldId`: namespace receiving the memory.

The payload can stay private.

The public artifact can still prove that a committed output belongs to a committed input, model, runtime, and executor path.

## Minimal Architecture

```text
AI request
  -> scheduler
  -> GPU worker
  -> model/inference/training/eval execution
  -> output artifact
  -> ComputePulse emitter
  -> compute receipt
  -> verifier
  -> Rootflow memory graph
```

The emitter can be:

- a local job wrapper;
- a DePIN worker;
- a model-serving sidecar;
- an inference gateway;
- a trusted execution environment;
- a sequencer-like memory service;
- a contract bridge for public commitments.

ComputePulse does not require putting prompts, outputs, or KV cache on-chain.

It requires commitments, lineage, and verification paths.

## KV Cache And Context Memory

ComputePulse should not claim to store GPU memory.

Instead, it can remember the identity and lineage of memory artifacts:

- KV cache bundle commitments;
- prompt prefix commitments;
- retrieved context commitments;
- embedding batch commitments;
- checkpoint commitments;
- tool-result commitments;
- session-state commitments.

The powerful claim:

```text
FlowMemory can help AI systems know what context already exists, where it came from, and whether it can be reused.
```

That is where workflow speed can improve.

Not because FlowMemory changes CUDA.

Because the system stops wasting work when memory is verifiable.

## Compute Reuse

The fastest GPU job is the one a system can prove it does not need to run again.

A ComputePulse-aware scheduler can:

1. receive a request;
2. compute input/model/runtime commitments;
3. query Rootflow for matching or compatible prior ComputePulses;
4. verify the prior output commitment and policy;
5. reuse, fork, or skip work;
6. emit a new child pulse for the reuse decision.

This turns memory from a passive log into an active compute primitive.

## Compute Reuse Router

The Compute Reuse Router is the first executable scheduler artifact for this
idea.

It takes:

- a request commitment set;
- a prior ComputePulse ledger;
- a reuse policy.

It returns:

- `REUSE_PRIOR_COMPUTE`; or
- `RUN_GPU_JOB`.

The router only reuses prior work when rootfield, model, input, runtime,
lineage, freshness, executor, hardware, and attestation policy checks pass.
Runtime drift, unverified evidence, missing attestation, and stale artifacts
force a new run.

```bash
python tools/compute_reuse_router.py demo --pretty
```

This is the practical GPU angle: not faster silicon, but less repeated work
because compute memory is proof-backed.

Cache Lineage Gate is the companion artifact for KV/context reuse:

```bash
python tools/cache_lineage_gate.py demo --pretty
```

It proves that reusable context must carry model, tokenizer, runtime, prefix,
side-input, adapter, and cache-policy commitments. Token equality alone is not
enough.

## Related Future Pulses

ComputePulse is the base AI/GPU workload artifact. It naturally leads to three adjacent memory signals:

- **CachePulse**: records commitments and lineage for KV cache, prompt prefixes, context bundles, and reuse events.
- **ModelPulse**: records output provenance for model responses, generated artifacts, evaluations, and summaries.
- **AgentPulse**: records autonomous workflow steps, including tool calls, trades, inference jobs, reused context, and produced outputs.

The point is not to create more names.

The point is to make machine memory composable:

```text
AgentPulse
  -> uses FlowPulse
  -> uses CachePulse
  -> runs ComputePulse
  -> creates ModelPulse
  -> writes back to Rootflow
```

An agent that can cite this chain is not just "remembering."

It is remembering with provenance.

## ComputePulse Proof Object

Example reader-derived proof:

```json
{
  "pulseType": "COMPUTE_PULSE_V1",
  "status": "verified",
  "computePulseId": "0x...",
  "rootfieldId": "0x...",
  "jobId": "gpu-job-2026-05-19-001",
  "modelCommitment": "0x...",
  "inputCommitment": "0x...",
  "outputCommitment": "0x...",
  "runtimeCommitment": "0x...",
  "hardwareClass": "H100-class",
  "executor": "0x...",
  "attestationRef": "ipfs://...",
  "parentPulseId": "0x...",
  "checks": {
    "jobReceiptFound": true,
    "outputCommitmentMatches": true,
    "runtimeCommitmentMatches": true,
    "executorMatches": true,
    "artifactUriIsAdvisory": true,
    "payloadPrivacyPreserved": true
  }
}
```

## What ComputePulse Is Not

- Not a CUDA optimizer.
- Not HBM, VRAM, or KV cache storage.
- Not a claim that GPU hardware becomes physically faster.
- Not a claim that private prompts or outputs must be public.
- Not a replacement for model-serving infrastructure.
- Not an attestation system by itself.

## What ComputePulse Is

- A memory signal for GPU work.
- A provenance artifact for AI outputs.
- A reusable compute memory primitive.
- A bridge between runtime logs and structured memory.
- A way for agents to cite proof-backed memory instead of vague context.
- A path from raw compute to remembered compute.

## Founder Line

GPUs compute. FlowMemory remembers.

The next AI bottleneck is not only compute. It is knowing what was computed, what can be reused, and what proof says the work happened.
