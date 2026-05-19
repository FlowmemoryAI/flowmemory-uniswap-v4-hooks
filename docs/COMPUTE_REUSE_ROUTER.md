# Compute Reuse Router

The Compute Reuse Router is the first executable FlowMemory artifact aimed at
AI/GPU workflow usefulness.

It turns the slogan into a testable decision:

```text
GPUs compute. FlowMemory remembers.
```

The router does not make GPU hardware faster. It checks whether a prior
ComputePulse is safe to reuse before a scheduler spends GPU time again.

## Why This Matters

Modern AI serving is becoming a memory and reuse problem, not only a raw compute
problem. NVIDIA TensorRT-LLM documents KV-cache reuse across requests with
matching prefixes, and vLLM's PagedAttention work frames KV-cache memory waste
and sharing as central throughput constraints. NVIDIA's CMX context memory
platform pushes the same direction at infrastructure scale: context and KV-cache
placement, reuse, and prestaging are now first-class AI-system concerns.

FlowMemory does not compete with those systems.

FlowMemory adds the proof layer around them:

```text
What was computed?
Which input, model, runtime, executor, and context produced it?
Can this request reuse that artifact without inventing trust?
```

## The Router Decision

The router receives:

- a `ComputeReuseRequest`;
- a ledger of prior `ComputePulse` artifacts;
- a reuse policy.

It emits:

- `REUSE_PRIOR_COMPUTE`; or
- `RUN_GPU_JOB`.

That decision is deterministic and digestable. Unsafe reuse produces explicit
reasons.

## Reuse Is Strict

A prior ComputePulse can be reused only when:

- the status is verified;
- reuse is explicitly allowed;
- rootfield, model, input, and runtime commitments match;
- output commitment is present and non-zero;
- the artifact is fresh under policy;
- executor and hardware class are allowed;
- attestation exists when required;
- requested cache lineage matches;
- URI content is treated as advisory, not authoritative.

This keeps the claim strong without pretending FlowMemory verifies model
correctness or accelerates CUDA.

## Run It

```bash
python tools/compute_reuse_router.py demo --pretty
```

Expected summary:

```text
prior compute reused: 1
GPU jobs avoided: 1
unsafe reuse rejected: 4/4
```

Run one request:

```bash
python tools/compute_reuse_router.py route \
  --request examples/compute-reuse-router/request.reuse.json \
  --ledger examples/compute-reuse-router/ledger.example.json \
  --policy examples/compute-reuse-router/policy.example.json \
  --pretty
```

## The Novel Angle

Most AI memory products retrieve context.

Compute Reuse Router uses memory as a scheduling primitive.

It does not ask:

```text
What text looks relevant?
```

It asks:

```text
Which prior compute artifact can this system prove is reusable?
```

That is the bridge from vague agent memory to proof-backed compute memory.

## Research Context

- NVIDIA TensorRT-LLM KV cache reuse: <https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html>
- NVIDIA TensorRT-LLM KV cache system: <https://nvidia.github.io/TensorRT-LLM/features/kvcache.html>
- vLLM PagedAttention paper: <https://arxiv.org/abs/2309.06180>
- NVIDIA CMX context memory platform: <https://developer.nvidia.com/blog/introducing-nvidia-bluefield-4-powered-cmx-context-memory-storage-platform-for-the-next-frontier-of-ai/>
- NVIDIA GPU attestation SDK: <https://docs.nvidia.com/attestation/attestation-client-tools-sdk/latest/gpu_and_switch_attestation.html>
