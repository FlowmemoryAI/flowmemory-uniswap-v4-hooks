# Launch Review FAQ

This FAQ is for launch-day review, not marketing softness. It answers the
questions that serious reviewers will ask first.

## Is this just an event?

No.

The Uniswap v4 hook is intentionally a narrow FlowPulse emission boundary. The
larger release surface defines the downstream memory-consistency model around
that receipt-bound FlowPulse.

## Does this enforce wallet safety?

No.

This repo is local conformance, not wallet enforcement. It does not custody
funds, protect funds, authorize wallets, or act as escrow.

## Does this prove the model output is true?

No.

FlowMemory does not claim semantic truth, work quality, or model correctness.
It checks whether declared payment, work, compute route, memory head, receipt,
delegation, and discharge facts are internally consistent.

## Is this live on Base mainnet?

No.

Base mainnet deployment is not claimed. Public Base Sepolia receipt evidence is
pending until a real release record exists.

## Does this make GPUs faster?

No.

FlowMemory does not claim GPU hardware acceleration or hardware speedup. The
compute-memory claim is workflow consistency: avoid unsafe reuse, permit
admissible reuse, and keep compute payment tied to the route that actually
satisfies memory state.

## Why use a chain boundary?

Because receipt facts cannot exist inside the hook.

The hook emits a FlowPulse at the afterSwap boundary. A reader later attaches
txHash, transactionIndex, logIndex, block, and finality facts from the proof
envelope.

That separation is the architecture.

## Why not just use an indexer?

An indexer tells you what happened.

FlowMemory asks whether the machine history that used that event could legally
exist.

## Why not put more logic inside the hook?

Because the primitive is memory emission, not swap control.

The first hook is narrow on purpose: no custody, no dynamic fee path, no routing
engine, no custom accounting, and zero hook delta.

## Why does agent commerce need this?

Agents will transact, delegate, buy compute, reuse memory, sell work, receive
payments, and close obligations.

A payment alone does not prove that the right obligation closed.

Settlement is not discharge.

## What is the shortest honest launch line?

```text
FlowMemory defines local deterministic memory-consistency rules for
receipt-bound DeFi and autonomous agent commerce.
```

