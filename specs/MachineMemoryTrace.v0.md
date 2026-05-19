# Machine Memory Trace v0 Draft Spec

MachineMemoryTrace is a portable trace format for connected FlowMemory artifacts.

It exists so the public can see the bigger category:

```text
FlowPulse -> ComputePulse -> ModelPulse -> AgentPulse -> Rootflow
```

## Purpose

A trace connects separate execution boundaries into one memory graph.

Each node is a memory artifact.

Each edge explains how one artifact depended on, extended, verified, reused, or summarized another artifact.

## Required Sections

| Section | Meaning |
| --- | --- |
| `schema` | Trace schema id. |
| `traceId` | Canonical trace id. |
| `rootfieldId` | Memory namespace. |
| `summary` | Human-readable summary. |
| `artifacts` | Pulse artifacts. |
| `edges` | Relationships between artifacts. |
| `verifierNotes` | What is real, mocked, pending, or advisory. |

## Artifact Types

- `FlowPulse`: DeFi execution boundary memory.
- `ComputePulse`: AI/GPU job memory.
- `CachePulse`: context or KV reuse memory.
- `ModelPulse`: output provenance memory.
- `AgentPulse`: autonomous workflow memory.

## Edge Types

- `observed_by`: a later artifact observed an earlier artifact.
- `uses`: an artifact used another artifact as input.
- `reuses`: an artifact reused a cache/context artifact.
- `produces`: an artifact produced another artifact.
- `summarizes`: an artifact summarized a prior memory set.
- `verifies`: an artifact or proof verified another artifact.

## Launch Demo Trace

The near-term demo can be explicit about what is real and what is mocked:

```text
real FlowPulse from Base Sepolia
  -> mocked ComputePulse from local inference wrapper
  -> mocked ModelPulse output commitment
  -> Rootflow trace JSON
```

This is still useful because it shows the architecture without pretending the AI/GPU side is already deployed.

## Design Line

FlowMemory starts with a hook.

The real product is proof-backed memory infrastructure for machines.
