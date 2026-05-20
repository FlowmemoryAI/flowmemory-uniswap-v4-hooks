# FlowMemory Uniswap v4 Hooks

[![CI](https://github.com/FlowmemoryAI/flowmemory-uniswap-v4-hooks/actions/workflows/ci.yml/badge.svg)](https://github.com/FlowmemoryAI/flowmemory-uniswap-v4-hooks/actions/workflows/ci.yml)

FlowMemory turns important execution boundaries into verifiable memory checkpoints.

This repository contains the first public FlowMemory primitive: a narrow Uniswap v4 `afterSwap` hook that emits a `FlowPulse` memory signal after a completed swap boundary.

The hook does not custody funds, route trades, set fees, or change swap accounting. It emits a compact commitment at a verified boundary so downstream systems can attach receipt evidence and check whether later memory, cache, compute, or workflow state is consistent with that boundary.

```text
execution boundary -> FlowPulse -> transaction receipt -> verified memory record
```

## Current Status

```text
Local hook and FMM-0 consistency surface: PASS
Public Base Sepolia receipt evidence: PENDING
Production verifier infrastructure: NOT_CLAIMED
Base mainnet deployment: NOT_CLAIMED
```

Run the local status transcript:

```bash
python tools/flowmemory_release_transcript.py --pretty
```

Run the production-candidate gate:

```bash
python tools/mainnet_candidate_gate.py --pretty
```

Expected current result:

```text
localLaunchReady:      True
mainnetCandidateReady: False
releaseMode:           LOCAL_LAUNCH_READY_ONLY
```

## Plain-English Model

A normal event log records that something happened.

FlowMemory adds a memory discipline around that event:

- the hook emits a small on-chain memory signal;
- the transaction receipt proves where the signal landed;
- a reader attaches receipt fields like `txHash`, `logIndex`, block facts, and finality;
- an append-only memory record preserves the signal and proof envelope;
- downstream checks can accept, reject, quarantine, or recompute later machine state.

The full memory artifact does not need to live on-chain. The on-chain signal carries a commitment to off-chain or downstream data.

## Core Terms

| Term | Meaning |
| --- | --- |
| `FlowPulse` | A compact memory signal emitted at a boundary. |
| `rootfieldId` | The memory namespace for a pulse sequence. |
| `commitment` | A hash or opaque pointer to the related off-chain artifact. |
| `parentPulseId` | Optional link to a prior memory signal. |
| `sequence` | Monotonic sequence within a `rootfieldId`. |
| Transaction receipt | The proof envelope that shows where the signal landed. |
| PulseWatch | The reader/verifier loop that turns logs and receipts into append-only memory records. |
| FMM-0 | The local receipt-bound consistency model for machine histories. |

## What This Is

- A public Uniswap v4 `afterSwap` memory-signal hook.
- A proof-envelope reader path for `FlowPulse` logs.
- Local consistency tooling for receipt-bound machine histories.
- A launch-prep evidence surface with explicit claim boundaries.

## What This Is Not

- Not a fee hook.
- Not a custody hook.
- Not a routing hook.
- Not a trading engine.
- Not a fund-protection system.
- Not a live Base mainnet deployment claim.
- Not production verifier infrastructure.
- Not semantic truth or model correctness.
- Not GPU hardware acceleration.

## Start Here

For a first technical pass, read:

1. [Reviewer Quickstart](docs/REVIEWER_QUICKSTART.md)
2. [How It Works](docs/HOW_IT_WORKS.md)
3. [Event Model](docs/EVENT_MODEL.md)
4. [Reader And Verifier Architecture](docs/READER_VERIFIER_ARCHITECTURE.md)
5. [Docs Index](docs/INDEX.md)

For a medium-depth reviewer bridge, see [FLOWMEMORY_TECHNICAL_WALKTHROUGH.md](FLOWMEMORY_TECHNICAL_WALKTHROUGH.md).

For the public technical report, see [FLOWMEMORY_PUBLIC_TECHNICAL_REPORT.md](FLOWMEMORY_PUBLIC_TECHNICAL_REPORT.md) or [FLOWMEMORY_PUBLIC_TECHNICAL_REPORT.pdf](FLOWMEMORY_PUBLIC_TECHNICAL_REPORT.pdf).

## Run The Main Checks

```bash
python tools/flowmemory_release_transcript.py --pretty
python tools/public_claim_gate.py --pretty
python tools/launch_reality_check.py --pretty
python tools/compute_reuse_consistency.py demo --pretty
forge test -vvv
```

The most important local demo:

```bash
python tools/launch_reality_check.py --pretty
```

Expected result:

```text
Result: FlowMemory can tell impossible histories from live ones using receipt-bound FlowPulse boundaries.
```

Run the always-on reader demo:

```bash
python tools/pulse_watch.py demo
```

## Repository Map

| Path | Purpose |
| --- | --- |
| `contracts/` | Solidity hook, FlowPulse event schema, and minimal interfaces. |
| `test/` | Foundry tests for hook behavior and invariants. |
| `tools/` | Local readers, claim gates, consistency harnesses, and demos. |
| `docs/` | Architecture, security, reader, launch, and reviewer docs. |
| `script/` | Base Sepolia Foundry deployment and verification helpers. |
| `deployments/base-sepolia/` | Sanitized deployment-manifest staging area. |
| `release-evidence/base-sepolia/` | Observed Base Sepolia release-packet staging area. |
| `public/status/` | Tiny claim-safe public proof/status artifact. |
| `ops/` | PulseWatch service supervision examples. |
| `specs/` | Draft specs for FlowPulse, FMM-0, cache/compute reuse, and related primitives. |
| `examples/` | Reproducible example inputs and expected outputs. |
| `releases/` | Release evidence templates and future public evidence packets. |

## Practical Angle

The useful claim is not that every swap needs memory. The useful claim is that high-value execution moments should leave verifiable memory checkpoints.

That pattern can apply to:

- protocol operations;
- release and deployment evidence;
- config changes;
- data pipeline checkpoints;
- compute jobs;
- cache and compute reuse;
- model output provenance;
- agent or workflow actions.

The Uniswap v4 hook is the first public boundary because it provides a clean on-chain proof surface. The broader pattern is proof-backed memory for machine workflows.

## Public Claim Boundary

Use:

```text
FlowMemory introduces a memory-native Uniswap v4 afterSwap hook primitive and local receipt-bound consistency tooling.
```

Do not claim:

```text
live Base mainnet deployment
production verifier readiness
custody or fund protection
semantic truth
GPU acceleration
hook-time txHash/logIndex
```
