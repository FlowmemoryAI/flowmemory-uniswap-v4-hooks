# FlowMemorySystemArchitecture v0 Draft Spec

This spec defines the minimum architecture packet for the FlowMemory system
surface. It is intentionally broader than the hook contract and narrower than a
full production network.

## Purpose

The architecture packet must let a reviewer answer:

```text
What emits memory?
What proves where it landed?
What checks whether the history could have happened?
What product surfaces act from that checked memory?
What is explicitly not claimed?
```

## Required Layers

| Layer | Required responsibility |
| --- | --- |
| `execution_boundary` | Defines where external execution produces a pulse opportunity. |
| `pulse_emission` | Defines the memory signal schema and required payload fields. |
| `reader_24_7` | Defines continuous observation, receipt attachment, cursoring, and dedupe. |
| `evidence` | Defines append-only raw/canonical proof-envelope records. |
| `memory_model` | Defines admissible and forbidden machine histories. |
| `policy_action` | Defines how agents, compute, and commerce are allowed, denied, downgraded, or repaired. |
| `product_api` | Defines the developer-facing surface for proof-backed memory. |
| `operations` | Defines monitoring, replay, release evidence, claim gates, and incident response. |

## Required Invariants

- Hooks and adapters do not invent receipt metadata.
- Receipt metadata is reader-derived.
- The hook is transaction-triggered, not a 24/7 process.
- The reader is the 24/7 process.
- Memory records are append-only.
- URI content is advisory unless separately verified.
- Wallet/payment rails are external to FlowMemory conformance.
- Compute reuse stores commitments and lineage, not GPU memory contents.
- Public release claims are gated by evidence.

## Required Non-Claims

- no custody;
- no escrow;
- no fund protection;
- no wallet authorization;
- no hook-time `txHash`, `transactionIndex`, or `logIndex`;
- no semantic truth;
- no model correctness;
- no GPU hardware acceleration;
- no live Base mainnet deployment without release evidence;
- no production verifier network without operator evidence.

## Readiness Levels

| Level | Meaning |
| --- | --- |
| `local_conformance` | Deterministic local fixtures and tests pass. |
| `public_testnet_evidence` | Public testnet logs, receipts, and reader evidence validate. |
| `public_canary` | A public status surface exposes current evidence and degraded states. |
| `production_candidate` | Operator, replay, monitoring, source verification, incident response, and external review exist. |

## Review Artifact

The canonical machine-readable architecture packet is:

```text
examples/system-architecture/architecture-manifest.json
```

It is checked by:

```text
python tools/system_architecture_review.py --pretty
```

