# CacheLineageGate v0 Draft Spec

Cache Lineage Gate is proof-backed reuse for KV cache, prompt-prefix cache, and
context memory artifacts.

It does not store cache tensors.

It checks whether a request may reuse a committed cache artifact without
inventing trust.

## Required Match

A `CachePulse` is reusable only if:

- schema is `flowmemory.cachepulse.v0`;
- status is `verified`;
- reuse is explicitly allowed;
- KV block commitment exists;
- rootfield commitment matches;
- model commitment matches;
- tokenizer commitment matches;
- runtime commitment matches;
- prompt-prefix commitment matches;
- side-input commitment matches;
- adapter commitment matches;
- cache-policy commitment matches;
- executor is allowed;
- attestation exists when required;
- artifact age is inside policy;
- URI content is advisory only.

## Why Side Inputs Matter

Two requests can look identical at the token level while differing in adapter,
multimodal side input, tool context, runtime flags, or cache policy. A scheduler
that reuses cache from token identity alone can silently attach the wrong memory.

Cache Lineage Gate forces those hidden dimensions into commitments.

## Output

The gate emits:

- `REUSE_CACHE`; or
- `RUN_PREFILL`.

Unsafe reuse produces explicit reasons such as tokenizer drift, side-input
drift, cache-policy drift, or unverified evidence.

## Design Line

KV reuse should be proof-carried, not vibe-carried.
