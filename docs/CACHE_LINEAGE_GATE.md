# Cache Lineage Gate

Cache Lineage Gate is the FlowMemory answer to unsafe KV/context reuse.

Modern inference systems increasingly depend on cache reuse. That is useful,
but it creates a new class of failure: a scheduler can reuse a cache artifact
because two requests look compatible while hidden context changed.

FlowMemory's position:

```text
KV reuse should be proof-carried, not vibe-carried.
```

## What It Checks

The gate checks a `CacheReuseRequest` against a ledger of prior `CachePulse`
artifacts.

Reuse is allowed only when these commitments match:

- rootfield;
- model;
- tokenizer;
- runtime;
- prompt prefix;
- side input;
- adapter;
- cache policy.

It also requires verified status, explicit reuse permission, a non-zero KV block
commitment, freshness, allowed executor, and attestation when policy requires
it.

## Why This Is Useful

The Compute Reuse Router asks whether prior compute can be reused.

Cache Lineage Gate asks whether the context memory underneath that compute is
safe to reuse.

That is the missing layer between GPU memory systems and proof-aware AI
workflows.

FlowMemory does not store KV tensors. It stores and checks the identity,
lineage, and reuse authority of cache artifacts.

## Run It

```bash
python tools/cache_lineage_gate.py demo --pretty
```

Expected summary:

```text
cache reuse accepted: 1
prefill required: 4
unsafe cache reuse rejected: 4/4
```

## Research Context

- NVIDIA TensorRT-LLM KV cache reuse: <https://nvidia.github.io/TensorRT-LLM/advanced/kv-cache-reuse.html>
- NVIDIA TensorRT-LLM KV cache system: <https://nvidia.github.io/TensorRT-LLM/features/kvcache.html>
- vLLM PagedAttention paper: <https://arxiv.org/abs/2309.06180>
- NVIDIA CMX context memory platform: <https://www.nvidia.com/en-gb/data-center/ai-storage/cmx/>

## Non-Claims

- Not KV tensor storage.
- Not GPU hardware speedup.
- Not model correctness.
- Not semantic truth.
- Not an attestation verifier.
- Not payload disclosure.
