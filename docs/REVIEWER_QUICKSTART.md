# Reviewer Quickstart

This repo has one launch theorem:

```text
Execution is not memory. A verified boundary can emit a memory signal, and
machine systems can test whether later memory, cache, and compute reuse are
consistent with that boundary.
```

## Run These First

```bash
python tools/flowmemory_release_transcript.py --pretty
python tools/public_claim_gate.py --pretty
python tools/launch_reality_check.py --pretty
python tools/compute_reuse_consistency.py demo --pretty
forge test -vvv
```

## What The Commands Show

| Command | Why it matters |
| --- | --- |
| `flowmemory_release_transcript.py` | One offline object for passed local evidence, pending public evidence, and explicit non-claims. |
| `public_claim_gate.py` | Public launch copy can mention risky claims only as explicit non-claims. |
| `launch_reality_check.py` | Hook boundary model, launch artifact inventory, and forbidden-outcome runtime checks. |
| `compute_reuse_consistency.py` | Cache lineage, compute fingerprint, and receipt-bound history must all pass before reuse becomes live. |
| `forge test -vvv` | The hook remains narrow: `afterSwap`, PoolManager-gated, zero hook delta, no custody, no fee/routing/accounting path. |

## What This Proves Locally

- The swap is not the memory.
- The transaction is the proof envelope.
- The FlowPulse is the memory artifact.
- The hook does not know `txHash` or `logIndex` during execution.
- Reader/verifier infrastructure attaches receipt metadata later.
- FMM-0 catches impossible machine histories around receipt-bound FlowPulse boundaries.
- KV/context reuse can be rejected when lineage drifts.
- Compute reuse can be rejected when fingerprints or memory history drift.

## What Is Pending

Public Base Sepolia receipt evidence remains `PENDING` until a real release
packet validates.

## Do Not Claim

- Live Base mainnet deployment.
- Custody, fund protection, swap control, or production verifier readiness.
- Semantic truth or model correctness.
- GPU hardware speedup.
- Hook-time `txHash` or `logIndex`.

## Launch Sentence

FlowMemory introduces a memory-native Uniswap v4 hook primitive and a local
memory-consistency stack for proof-backed AI/compute reuse.

Short version:

```text
Most hooks modify execution. FlowMemory emits memory.
Compute reuse without memory consistency is just cache optimism.
```
