# FlowMemoryReleaseTranscript v0 Draft Spec

The Release Transcript is an offline evidence summary for public launch review.

It does not replace tests, audits, release records, or deployment evidence. It
binds the current local evidence surface into one deterministic object.

## Required Sections

| Section | Meaning |
| --- | --- |
| `repoBoundary` | Current package boundary plus future packages explicitly deferred from this launch repo. |
| `localEvidence` | Local deterministic gates that should pass without RPC. |
| `publicEvidence` | Public release evidence status, usually `PENDING` before release. |
| `result` | Human-readable launch state. |
| `notClaims` | Explicit red lines the transcript does not assert. |
| `transcriptId` | Digest of the transcript body. |

## Required Local Evidence

- FMM-0 Witness Pack.
- Launch Reality Check.
- Compute Reuse Router.
- Cache Lineage Gate.
- Compute Reuse Consistency Harness.

## Required Public Evidence

- Base Sepolia receipt evidence gate.

Before the public release packet is filled, this may be `PENDING`. Pending is
not failure and not evidence.

## Design Line

The strongest launch artifact is not more vocabulary. It is one transcript that
says what passed, what is pending, and what is not claimed.

The hook repo boundary is part of that discipline: this launch package centers
the Uniswap v4 `afterSwap` FlowPulse primitive, while future runtime surfaces
such as FlowCompiler, FlowKernel, MCP adapters, and coding-agent conformance are
deferred to separate packages.
