# FlowMemoryReleaseTranscript v0 Draft Spec

The Release Transcript is an offline evidence summary for public launch review.

It does not replace tests, audits, release records, or deployment evidence. It
binds the current local evidence surface into one deterministic object.

## Required Sections

| Section | Meaning |
| --- | --- |
| `localEvidence` | Local deterministic gates that should pass without RPC. |
| `publicEvidence` | Public release evidence status, usually `PENDING` before release. |
| `result` | Human-readable launch state. |
| `notClaims` | Explicit red lines the transcript does not assert. |
| `transcriptId` | Digest of the transcript body. |

## Required Local Evidence

- FMM-0 Witness Pack.
- Launch Reality Check.
- Compute Reuse Router.

## Required Public Evidence

- Base Sepolia receipt evidence gate.

Before the public release packet is filled, this may be `PENDING`. Pending is
not failure and not evidence.

## Design Line

The strongest launch artifact is not more vocabulary. It is one transcript that
says what passed, what is pending, and what is not claimed.
