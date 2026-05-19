# ComputeReuseRouter v0 Draft Spec

The Compute Reuse Router is the scheduler-facing side of ComputePulse.

It answers one narrow question:

```text
Can this AI/GPU request safely reuse a prior committed compute artifact?
```

The router does not make a GPU physically faster. It makes the workflow less
forgetful by proving when prior work can be reused instead of rerun.

## Category

ComputeReuseRouter is proof-backed compute reuse.

It is not a CUDA optimizer. It is not KV-cache storage. It is not model
correctness. It is the policy gate between a requested compute job and a prior
ComputePulse memory artifact.

## Inputs

| Input | Meaning |
| --- | --- |
| `ComputeReuseRequest` | The requested model, input, runtime, rootfield, and optional cache lineage. |
| `ComputePulseLedger` | Prior ComputePulse artifacts available to the scheduler. |
| `ComputeReusePolicy` | Reuse rules for freshness, executor, hardware class, attestation, and cross-rootfield behavior. |

## Required Match

A prior ComputePulse is reusable only if all required checks pass:

- schema is `flowmemory.computepulse.v0`;
- status is `verified`;
- reuse is explicitly allowed;
- rootfield matches unless policy allows cross-rootfield reuse;
- model commitment matches;
- input commitment matches;
- runtime commitment matches;
- output commitment is present and non-zero;
- completed time is not in the future;
- age is within policy;
- hardware class is allowed;
- executor is allowed;
- attestation reference exists when required;
- optional cache lineage matches when the request names it;
- URI content is advisory and never the authority for reuse.

## Output

The router emits a `ComputeReuseDecision`:

- `REUSE_PRIOR_COMPUTE` if a prior ComputePulse satisfies the policy;
- `RUN_GPU_JOB` if no safe prior artifact exists.

The output includes rejected candidates and reasons so a reviewer can see why
unsafe reuse failed.

## Design Line

The fastest GPU job is the one a system can prove it does not need to run again.

## Non-Claims

- Not GPU acceleration.
- Not a CUDA optimizer.
- Not KV-cache storage.
- Not semantic truth.
- Not model correctness.
- Not an attestation verifier.
- Not public deployment evidence.
