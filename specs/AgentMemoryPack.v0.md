# AgentMemoryPack v0 Draft Spec

AgentMemoryPack is FlowMemory's first AI-agent memory object.

It converts a MachineMemoryTrace into a compact recall surface that an agent can verify, cite, and route through.

## Category

AgentMemoryPack is proof-carried memory for agents.

Normal agent memory stores text.

Vector memory stores similarity.

Indexer memory stores reconstructed activity.

AgentMemoryPack stores memory artifacts with proof envelopes, deterministic fingerprints, routing hints, and explicit uncertainty.

## Why This Is Different

An agent should not remember important execution with vague notes.

It should remember:

- what boundary produced the memory;
- what proof envelope anchors it;
- what commitment identifies the artifact;
- what can be reused;
- what is mocked, pending, or verified;
- what the next action should be.

The result is not just recall.

It is memory with provenance.

## Input

An AgentMemoryPack is built from:

```text
MachineMemoryTrace
  -> FlowPulse
  -> ComputePulse
  -> CachePulse
  -> ModelPulse
  -> AgentPulse
```

Not every trace needs every artifact type.

The minimum useful trace is one verified FlowPulse.

The more powerful trace links FlowPulse to ComputePulse and ModelPulse.

## Output Fields

| Field | Meaning |
| --- | --- |
| `schema` | `flowmemory.agent_memory_pack.v0`. |
| `status` | `verified`, `verified_with_notes`, `verified_with_warnings`, or `rejected`. |
| `traceFingerprint` | Deterministic trace hash over canonical JSON. |
| `rootfieldId` | Memory namespace. |
| `summary` | Human-readable trace summary. |
| `counts` | Artifact, edge, error, warning, and info counts. |
| `artifactTypes` | Artifact type set. |
| `recallCards` | Agent-readable memory cards. |
| `routing` | Reuse candidates and next action. |
| `issues` | Validation findings. |

## Recall Card

Each recall card contains:

- artifact id;
- artifact type;
- boundary;
- status;
- deterministic fingerprint;
- recall score;
- recommended agent use.

This gives an agent a stable citation target.

## Routing

Routing is where the primitive becomes useful.

An AgentMemoryPack can expose:

- reusable ComputePulse candidates;
- CachePulse context reuse candidates;
- ModelPulse output provenance;
- FlowPulse transaction proof anchors;
- next best action.

The initial tool only implements ComputePulse reuse candidates. That is enough to show the pattern.

## Design Line

Agents should not remember with unsupported claims.

Agents should remember with proofs.
