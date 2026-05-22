# Proof-Carried Agent Memory

Proof-Carried Agent Memory is the R&D direction that makes FlowMemory useful for AI.

The idea is simple:

```text
agent memory should carry proof, not just text
```

Most AI memory systems save summaries, embeddings, vector matches, or chat history.

That is useful, but it is weak memory. It can tell an agent what something sounded like. It cannot prove where the memory came from.

FlowMemory can give agents a stronger primitive.

## The Primitive

A proof-carried memory object includes:

- the execution boundary;
- the proof envelope;
- the memory artifact;
- a deterministic fingerprint;
- relationship edges;
- uncertainty labels;
- routing hints.

For DeFi:

```text
swap boundary -> FlowPulse -> receipt metadata -> AgentMemoryPack
```

For compute:

```text
GPU job -> ComputePulse -> output commitment -> AgentMemoryPack
```

For agents:

```text
tool/action/decision -> AgentPulse -> memory trace -> AgentMemoryPack
```

## Why It Matters

AI agents will increasingly act across systems:

- they will read market state;
- they will trigger transactions;
- they will run inference;
- they will reuse context;
- they will generate outputs;
- they will make decisions across many sessions.

If the agent's memory is only a vector match, the agent is remembering without evidence.

FlowMemory lets an agent remember with provenance.

The sharper R&D direction is that proof-backed memory can also remove context.

An agent should not keep every stale summary, model guess, speculative plan, or
cache hint after a verified boundary proves the world changed. BoundaryFission
turns a receipt-bound FlowPulse into a memory release event:

```text
FlowPulse proof envelope
  -> BoundaryFission
  -> conserved facts
  -> ResidueAtoms
  -> quarantined claims
  -> BranchAsh
  -> delegated recompute
```

That makes FlowMemory useful for the part of agent memory most systems ignore:
proof-triggered forgetting.

## What The Current Tool Builds

`tools/memory_trace.py` reads a MachineMemoryTrace and emits an Agent Memory Pack.

The pack contains:

- trace fingerprint;
- artifact fingerprints;
- validation issues;
- recall cards;
- compute reuse candidates;
- next-best-action routing.

This turns the example trace into an agent-readable memory surface.

## Why This Is More Than An Indexer

An indexer reconstructs activity.

FlowMemory emits committed memory at the boundary.

The Agent Memory Pack then turns those memory artifacts into something an agent can use:

- cite this memory;
- verify this memory;
- reuse this compute result;
- ask for missing proof;
- avoid treating R&D examples as deployed infrastructure;
- route future work through the memory graph.

## The Big Direction

The future system is a proof-backed memory router:

```text
new agent task
  -> derive commitments
  -> query Rootflow
  -> retrieve AgentMemoryPacks
  -> verify pulse fingerprints
  -> reuse prior compute/context when policy allows
  -> emit new AgentPulse
```

That is where FlowMemory becomes more than documentation.

It becomes an operating layer for machine memory.

The deeper version is a proof-backed memory runtime:

```text
new proof boundary
  -> compile AgentMemoryPacks
  -> apply AxiomPatch permissions
  -> run BoundaryFission release
  -> retire eligible speculative artifacts through PulseRetire
  -> map receipt facts through FlowMMU
  -> require active pre-boundary frames to quiesce through FlowQuiesce
  -> emit AgentPulse for what survived, changed, or died
```

That runtime does not just recall memory. It changes the agent's working state
when receipt-bound evidence arrives.

PulseRetire handles the other side of agent memory: not what must be released
after a boundary, but what must stay speculative before a boundary. It gives
agents a reorder buffer for reality.

FlowMMU handles dereference: expected boundary facts and receipt-settled facts
are not the same memory state. If an agent tries to read receipt-only fields too
early, it gets a deterministic `ReceiptPageFault`.

FlowQuiesce handles active work already in progress. If a frame read the old
rootfield epoch, its outputs cannot join the post-boundary world until it
revalidates, forks, abandons, or otherwise reaches a safe point.

## Line To Use

Agents should not remember with unsupported claims.

Agents should remember with proofs.
