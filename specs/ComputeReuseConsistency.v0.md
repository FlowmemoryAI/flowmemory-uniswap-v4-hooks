# ComputeReuseConsistency v0 Draft Spec

ComputeReuseConsistency is a local harness for proof-backed compute reuse.

It requires three gates:

1. FlowSerial receipt-bound history is serializable.
2. Cache Lineage Gate allows context reuse.
3. Compute Reuse Router allows compute reuse.

If any gate fails, the system must not accept the reuse as live machine memory.

## Decisions

| Decision | Meaning |
| --- | --- |
| `ACCEPT_REUSE` | History, cache lineage, and compute fingerprint all pass. |
| `BLOCK_CACHE_REUSE` | Cache lineage is unsafe; prefill or recompute context. |
| `RUN_GPU_JOB` | Compute artifact is incompatible; schedule a new compute job. |
| `BLOCK_IMPOSSIBLE_HISTORY` | The agent history is not receipt-serializable. |

## Design Line

Compute reuse without memory consistency is just cache optimism.
