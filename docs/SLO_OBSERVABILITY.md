# SLO And Observability Plan

This repo does not claim a live production verifier network. This document
defines the observability surface a future deployment candidate should have
before production language is used.

## Critical Signals

| Signal | Why it matters |
| --- | --- |
| Hook address and permission bits | Confirms the deployed hook is the intended `afterSwap` memory hook. |
| Source verification status | Confirms reviewers can inspect the deployed bytecode/source match. |
| `AfterSwapObserved` log count | Shows the hook boundary is being reached. |
| `FlowPulse` log count | Shows memory signals are being emitted. |
| Reader lag | Measures time from finalized receipt to reader-derived evidence packet. |
| Finality depth | Prevents premature evidence from being treated as final. |
| Evidence packet validation failures | Catches malformed receipts, wrong chain ids, missing logs, or schema drift. |
| Claim-gate result | Catches overclaim drift in public docs and release copy. |

## Initial SLO Targets

These are candidate targets for a future monitored deployment:

| SLO | Target |
| --- | --- |
| Source verification | 100% for promoted hook deployments. |
| Reader evidence reproducibility | 99.9% of finalized sampled receipts reproduce within 10 minutes. |
| Claim-gate health | 0 unguarded overclaims on every public release commit. |
| Evidence packet validity | 100% for published release packets. |
| Incident acknowledgement | Operator acknowledges public evidence incidents within 24 hours. |

## Alerts

Alert when:

- hook permission bits differ from the expected `afterSwap`-only surface;
- source verification disappears or mismatches;
- reader lag exceeds the target;
- evidence packet validation fails;
- public claim gate fails;
- mainnet candidate gate changes release mode unexpectedly.

## Telemetry Contract

Reader/verifier telemetry should be structured, replayable, and receipt-derived.
The hook must not emit receipt-only metadata at execution time.

See [specs/ReaderVerifierTelemetry.v0.md](../specs/ReaderVerifierTelemetry.v0.md).
