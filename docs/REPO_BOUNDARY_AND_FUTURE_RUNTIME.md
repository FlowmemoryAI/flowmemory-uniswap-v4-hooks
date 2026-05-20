# Repo Boundary and Future Runtime Architecture

This repository has one center of gravity:

```text
Uniswap v4 afterSwap -> FlowPulse -> transaction receipt -> reader metadata -> FMM-0
```

The hook repo exists to make the first public FlowMemory boundary primitive clear
and inspectable. It is not the place to ship every future agent-runtime package.

## What This Repo Is

This repository is the public launch surface for the memory-native Uniswap v4
`afterSwap` hook primitive.

It contains:

- the `afterSwap` hook that emits `FlowPulse`;
- the `FlowPulse` event schema and hook-data shape;
- receipt-time separation for `txHash`, `transactionIndex`, and `logIndex`;
- FMM-0 local memory consistency harnesses;
- FlowLitmus forbidden-history checks;
- compute and agent-commerce R&D harnesses that show downstream memory
  consistency examples;
- public claim gates, reviewer walkthroughs, and release-evidence scaffolding.

The launch claim is deliberately narrow:

```text
The swap is not the memory.
The transaction is the proof envelope.
The FlowPulse is the memory artifact.
FMM-0 asks whether downstream machine histories could have happened.
```

## Do Not Claim From This Repo

This repository does not claim:

- live Base mainnet deployment;
- custody, escrow, or fund protection;
- wallet enforcement or spend authorization;
- swap-economic control, routing, fees, or custom accounting;
- hook-time access to `txHash`, `transactionIndex`, or `logIndex`;
- semantic truth, model correctness, or work-quality proof;
- GPU hardware acceleration;
- production verifier infrastructure;
- a coding-agent framework;
- a plugin ecosystem.

The current R&D harnesses are local deterministic conformance checks. They are
evidence for the memory model, not production enforcement.

## Boundary Layers

FlowMemory separates the launch architecture into four layers:

| Layer | Launch role |
| --- | --- |
| Execution | Uniswap v4 executes the swap through PoolManager. |
| Emission | `FlowMemoryAfterSwapHook` emits the `FlowPulse` at `afterSwap`. |
| Evidence | Transaction receipts and logs later provide proof-envelope facts. |
| Memory | FMM-0 checks whether receipt-bound histories are admissible. |

That separation is the category point. FlowMemory does not turn the swap itself
into memory. It emits a memory artifact from a verifiable execution boundary and
keeps receipt facts outside the hook until a reader attaches them.

## Future Runtime Packages

Future FlowMemory runtime packages should build on this hook boundary without
being folded into this launch repo.

| Future package | Purpose |
| --- | --- |
| `flowmemory-core` | Shared pulse, envelope, rootfield, commitment, and FMM schemas. |
| `flowmemory-onchain-reader` | Receipt/log reader and public evidence verifier. |
| `flowmemory-agent-commerce` | Spend, discharge, duplex exchange, and obligation conformance packages. |
| [`flowmemory-warranted-agents`](https://github.com/FlowmemoryAI/flowmemory-warranted-agents) | Local warranted-agent framework for PolicyCards, FlowBond, PulsePass, adapter conformance, launch packets, and scoped proof demos. |
| `flowmemory-coding` | Coding-agent memory conformance and plan-to-envelope compilation. |
| `flowmemory-kernel` | Plugin host for runtime adapters and policy modules. |
| `flowmemory-mcp` | MCP-facing adapter for local conformance tools. |

Those packages can share the same primitives:

```text
Pulse + Envelope + Rootfield + Commitment + History + ForbiddenCore + Repair
```

But they should not make the Uniswap hook repo look like a general-purpose AI
agent framework.

## Why Coding-Agent Conformance Is Deferred

Coding-agent conformance is a strong future direction:

```text
agent plan -> required envelopes -> observed history -> forbidden core -> repair
```

It belongs in a dedicated package because its natural surface is local file
trees, diffs, commands, tests, commits, delegation, and final-answer claims.
Those are not Uniswap hook concerns.

The current launch repo can mention that future direction, but it should not
ship a full coding-agent compiler, MCP server, IDE integration, or plugin host
before the hook primitive has been reviewed on its own terms.

## Launch Spine

FlowMemory's launch repo is centered on one primitive: a Uniswap v4 `afterSwap`
hook that emits a `FlowPulse` memory artifact.

The swap is not the memory; the transaction is the proof envelope; the
`FlowPulse` is the memory artifact.

The hook is deliberately narrow: no custody, no routing, no fees, no custom
accounting, no swap-economic control, and no hook-time `txHash` or `logIndex`.

Reader infrastructure attaches receipt metadata later, preserving the boundary
between hook-time signals and receipt-time evidence.

FMM-0 is the local memory consistency model that asks whether downstream machine
histories could have happened around receipt-bound `FlowPulse` boundaries.

The current R&D harnesses show forbidden histories, unsafe reuse, and
agent-commerce consistency failures locally; they do not claim wallet
enforcement, production verification, semantic truth, GPU acceleration, or live
mainnet deployment.

Future packages such as FlowKernel, FlowCompiler, warranted-agent conformance,
and coding-agent conformance should build on this boundary, while this public
launch repo remains the `afterSwap` FlowPulse primitive plus its local
conformance evidence.
