# FlowMemory Technical Walkthrough

This walkthrough gives reviewers the medium-depth path after the root README. It keeps the first page clean while preserving the claim surface, evidence path, and review order.

## Core Model

```text
execution boundary -> FlowPulse -> transaction receipt -> reader/verifier -> memory record -> consistency checks
```

For the Uniswap v4 hook:

- the execution boundary is `afterSwap`;
- the memory signal is `FlowPulse`;
- the transaction receipt is the proof envelope;
- PulseWatch/readers attach receipt metadata after execution;
- FMM-0 checks whether later machine histories are consistent with receipt-bound pulses.

## Hook Boundary

The hook is intentionally narrow:

- PoolManager-gated;
- `afterSwap` only;
- zero hook delta;
- no custody;
- no routing;
- no fee control;
- no custom accounting path;
- no hook-time `txHash` or `logIndex`.

The hook emits `FlowPulse` with a compact commitment. The larger artifact can live off-chain in a database, object store, IPFS, Arweave, or a future Rootflow graph.

## Evidence Path

Run:

```bash
python tools/flowmemory_release_transcript.py --pretty
python tools/public_claim_gate.py --pretty
python tools/launch_reality_check.py --pretty
python tools/compute_reuse_consistency.py demo --pretty
forge test -vvv
```

Expected current public status:

```text
Local FMM-0 consistency surface: PASS
FlowLitmus forbidden outcomes: PASS
Public Base Sepolia receipt evidence: PENDING
Production verifier infrastructure: NOT_CLAIMED
```

## Reader Path

The hook does not run continuously. It only runs when a valid Uniswap v4 transaction reaches the configured lifecycle boundary.

PulseWatch is the continuous layer:

```text
hook transaction -> FlowPulse log -> transaction receipt -> PulseWatch -> append-only memory record
```

Run:

```bash
python tools/pulse_watch.py demo
```

## Why This Is Not Just Logs

A normal event log records that something happened.

FlowMemory tries to make important events usable as verified memory checkpoints:

- where the boundary occurred;
- what artifact was committed;
- which namespace and sequence it belongs to;
- which prior pulse it extends;
- whether the receipt and finality policy support it;
- whether later cache, compute, or workflow reuse is consistent with it.

The practical value is not transaction volume. The practical value is proving that high-value actions, datasets, outputs, releases, configs, or compute artifacts can be relied on later.

## Review Path

Start here:

1. [Reviewer Quickstart](docs/REVIEWER_QUICKSTART.md)
2. [How It Works](docs/HOW_IT_WORKS.md)
3. [Event Model](docs/EVENT_MODEL.md)
4. [Reader And Verifier Architecture](docs/READER_VERIFIER_ARCHITECTURE.md)
5. [Skeptic Review Walkthrough](docs/SKEPTIC_REVIEW_WALKTHROUGH.md)
6. [Documentation Index](docs/INDEX.md)

## Claim Boundary

Use:

```text
FlowMemory introduces a memory-native Uniswap v4 afterSwap hook primitive and local receipt-bound consistency tooling.
```

Avoid:

```text
live Base mainnet deployment
production verifier readiness
custody or fund protection
semantic truth
GPU acceleration
hook-time txHash/logIndex
```
