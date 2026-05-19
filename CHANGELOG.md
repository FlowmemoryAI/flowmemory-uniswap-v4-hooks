# Changelog

## 0.1.0 Launch Prep - 2026-05-19

FlowMemory Uniswap v4 Hooks is public launch prep for the first memory-native
FlowMemory hook primitive.

Core public claim:

```text
The swap is not the memory.
The transaction is the proof envelope.
The FlowPulse is the memory artifact.
```

What this release-prep surface includes:

- `FlowMemoryAfterSwapHook`: a narrow Uniswap v4 `afterSwap` memory-emission boundary.
- `FlowPulse`: the memory signal emitted from the hook boundary.
- FMM-0: a receipt-bound memory consistency model for machine histories.
- FlowLitmus: executable forbidden outcomes for impossible machine histories.
- FMM-0 witness, counterexample, closure, boundary, and forbidden-core harnesses.
- FlowPulse Boundary ABI gate for hook-time and receipt-time schema separation.
- Cache Lineage Gate, Compute Reuse Router, and Compute Reuse Consistency for proof-backed AI/GPU workflow reuse discipline.
- Public Claim Gate, Release Transcript, Reviewer Quickstart, Skeptic Walkthrough, and Launch Reality Check.
- Public Technical Report: a publication-style Markdown source and PDF for reviewers, journals, and public launch readers.
- External Developer Review Packet: a simple plus technical review handoff for senior security and architecture reviewers.

Verified locally before this entry:

- `python -m unittest discover -s tools -p 'test_*.py'`: 276 tests passed.
- `forge fmt --check`: passed.
- `forge build`: passed.
- `forge test -vvv`: 12 tests passed.
- GitHub Actions `CI`: passing on `main`.

Public evidence status:

- Local FMM-0 consistency surface: `PASS`.
- Public Base Sepolia receipt evidence: `PENDING`.
- Production verifier infrastructure: `NOT_CLAIMED`.

Do not claim from this repo alone:

- live Base mainnet deployment;
- audited custody or fund-safety guarantees;
- swap control, routing, fee control, or custom accounting;
- hook-time `txHash`, `transactionIndex`, or `logIndex`;
- semantic truth or model correctness;
- GPU hardware speedup;
- production verifier readiness.
