# BoundaryFission

BoundaryFission is the newest FlowMemory R&D primitive: proof-triggered
forgetting for autonomous systems.

Most AI-memory systems try to keep more context, retrieve more aggressively, or
summarize more smoothly. BoundaryFission goes the other way.

When a receipt-bound `FlowPulse` lands, stale working memory is forced through a
release boundary:

- receipt-bound facts are conserved;
- stale model and cache outputs are compressed into `ResidueAtom` commitments;
- unsupported claims are quarantined;
- speculative on-chain action branches become `BranchAsh`;
- fresh compute can be delegated from the current boundary.

The category claim:

> FlowMemory does not just help agents remember. It gives agents
> proof-triggered forgetting.

## Why This Is Different

This is not storage.
This is not indexing.
This is not RAG.
This is not a proof explorer.
This is not a dashboard.

BoundaryFission treats a `FlowPulse` as a boundary event that changes memory
state. The transaction is still the proof envelope. The `FlowPulse` is still the
memory artifact. BoundaryFission is what happens when that artifact collides
with an agent's existing working memory.

## Why The Chain Boundary Matters

Forgetting should not be fully self-authored by the agent.

Without the chain boundary, memory release is local housekeeping. With
FlowMemory, release can be triggered by a public execution boundary the agent did
not privately invent.

The Uniswap v4 `afterSwap` hook supplies the first public boundary:

```text
swap completes -> afterSwap boundary -> FlowPulse -> receipt metadata -> BoundaryFission
```

The hook still does not know `txHash` or `logIndex` during execution. A
reader/verifier attaches those facts from the transaction receipt later. That is
why the fission trigger requires reader-attached receipt metadata.

## Products Of Fission

`BoundaryFission` splits working memory into five products:

| Product | Meaning |
| --- | --- |
| conserved facts | Receipt-bound facts that survive the boundary. |
| `ResidueAtom` | A commitment proving a memory was compressed or erased without retaining raw payloads. |
| quarantine | Claims that cannot be supported by the FlowPulse boundary, such as inferred user intent. |
| `BranchAsh` | A killed speculative branch, usually an executable action plan that must be downgraded. |
| delegated recompute | A draft task asking fresh compute to rerun from the current FlowPulse boundary. |

The important rule is conservation under release:

```text
unsafe memory cannot simply vanish.
it must become conserved fact, residue, quarantine, branch ash, or delegated recompute.
```

## Demo

```bash
python tools/boundary_fission.py demo

python tools/boundary_fission.py apply \
  --flowpulse examples/boundary-fission/flowpulse-evidence.fixture.json \
  --memory examples/boundary-fission/agent-working-memory.before.json \
  --policy examples/boundary-fission/fission-policy.fixture.json \
  --report examples/boundary-fission/fission-report.example.json \
  --after examples/boundary-fission/agent-working-memory.after.json \
  --pretty

python tools/boundary_fission.py verify \
  --report examples/boundary-fission/fission-report.example.json \
  --pretty
```

Expected shape:

```text
Conserved: 2
ResidueAtoms: 2
Quarantined: 1
BranchAsh: 1
Delegated recompute: 2
```

## What It Does Not Prove

BoundaryFission does not prove semantic truth.
It does not prove trader intent.
It does not prove model correctness.
It does not prove GPU execution.
It does not authorize transactions.

It proves a deterministic memory release occurred under a stated policy after a
receipt-bound `FlowPulse` boundary.
