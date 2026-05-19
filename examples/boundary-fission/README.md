# BoundaryFission Example

BoundaryFission is proof-triggered forgetting.

The input is not a vector store and not a dashboard. It is an agent working set
hit by a receipt-bound `FlowPulse` boundary. The output is a deterministic
memory release report:

- receipt-bound facts are conserved;
- stale model outputs become `ResidueAtom` commitments;
- unsupported intent claims are quarantined;
- executable on-chain branches become `BranchAsh`;
- stale compute/cache reuse becomes delegated recompute.

Run the demo:

```bash
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

python tools/boundary_fission.py explain \
  --report examples/boundary-fission/fission-report.example.json
```

Expected result:

```text
1 FlowPulse boundary fact conserved
2 stale memories compressed to ResidueAtoms
1 unsupported claim quarantined
1 speculative transaction branch killed
2 recompute tasks delegated
0 raw private payloads retained in the after-state
```

The transaction is the proof envelope. The FlowPulse is the memory artifact.
BoundaryFission is the memory-state transition that follows from that boundary.
