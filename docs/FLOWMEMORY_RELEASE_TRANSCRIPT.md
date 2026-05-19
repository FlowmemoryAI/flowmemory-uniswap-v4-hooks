# FlowMemory Release Transcript

The FlowMemory Release Transcript is the canonical offline launch object.

It exists because the repository now has a deep local evidence stack. A public
reviewer should not have to reconstruct the launch state from ten separate
tools.

The transcript answers:

```text
What passed?
What is pending?
What is explicitly not claimed?
```

## What It Includes

- FMM-0 Witness Pack.
- Launch Reality Check.
- Compute Reuse Router.
- Cache Lineage Gate.
- Compute Reuse Consistency Harness.
- SpendLine Harness.
- DuplexLine Harness.
- Agent Commerce Conservation.
- Obligation Membrane.
- Public Base Sepolia receipt evidence gate.

The transcript is deterministic and does not depend on live RPC.

## Run It

```bash
python tools/flowmemory_release_transcript.py --pretty
```

Expected launch line:

```text
FlowMemory's local FMM-0 consistency surface is launch-ready; public receipt evidence remains pending and is not claimed.
```

## Why It Matters

The repo is not only a hook demo. It now has:

- a memory-native Uniswap v4 hook primitive;
- a FlowPulse event boundary;
- a local FMM-0 memory model;
- adversarial conformance harnesses;
- a Solidity ABI drift gate;
- an executable GPU workflow reuse gate;
- an executable cache-lineage reuse gate;
- an executable compute-reuse consistency harness;
- an executable autonomous spend consistency harness;
- an executable buyer/seller agent exchange consistency harness;
- an executable agent-commerce obligation conservation harness;
- an executable multi-agent obligation membrane harness;
- a pending-safe public evidence path.

The transcript makes that consumable in one artifact.

## Non-Claims

The transcript does not claim:

- live Base mainnet deployment;
- custody audit or fund-safety guarantees;
- swap control;
- semantic truth;
- model correctness;
- hardware speedup;
- production verifier readiness.
