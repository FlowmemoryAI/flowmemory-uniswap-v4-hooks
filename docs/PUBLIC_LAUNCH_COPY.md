# Public Launch Copy

Use this when sharing the repository publicly.

## Anchor Lines

```text
The swap is not the memory.
The transaction is the proof envelope.
The FlowPulse is the memory artifact.
```

## Short Launch Post

FlowMemory introduces the first memory-native Uniswap v4 hook primitive: a
verified on-chain emission boundary where DeFi execution can produce FlowPulse
memory signals.

Most hooks modify execution.

FlowMemory emits memory.

The swap is not the memory. The transaction is the proof envelope. The
FlowPulse is the memory artifact.

We also added FlowMemory Reality Check: one command that runs the FlowLitmus
forbidden-outcome suite and shows whether machine histories respect
receipt-bound FlowPulse boundaries.

```bash
python tools/launch_reality_check.py --pretty
```

Result:

```text
FlowMemory can tell impossible histories from live ones using receipt-bound FlowPulse boundaries.
```

The sharper AI-infrastructure thesis:

```text
Everyone treated agent memory like retrieval. FlowMemory treats it like a memory model.
```

The model name is FMM-0: FlowMemory Agent Memory Model.

For that, run the Memory Consistency Card:

```bash
python tools/memory_consistency_card.py --pretty
```

It maps the claim to evidence: hook boundary, FlowPulse emission, receipt
metadata separation, reader-derived proof envelope, FlowSerial, FlowLitmus, and
pending public Base Sepolia receipt evidence.

## Technical Thread

1. FlowMemory is not another swap hook. It is a memory hook.

2. The Uniswap v4 `afterSwap` lifecycle point is the first public boundary:
   execution has happened, the hook emits a FlowPulse, and the receipt becomes
   the proof envelope.

3. The hook does not custody funds, route swaps, change fees, or change custom
   accounting. The narrow surface is the point.

4. The hook also does not know `txHash` or `logIndex` during execution. A
   reader/verifier attaches receipt metadata later.

5. That separation creates the primitive: the transaction is the proof envelope;
   the FlowPulse is the memory artifact.

6. FlowSerial adds receipt-linearizability for machine cognition: agent events
   can either serialize around FlowPulse receipt boundaries or fault as
   impossible histories.

7. FlowLitmus makes the runtime model executable. It tests forbidden outcomes:
   pre-receipt reads, retrocausal receipt claims, unquiesced output, speculative
   output escaping, stale memory survival, rollback, and split-brain writes.

8. The launch claim is not "we emitted an event." The launch claim is:
   FlowMemory gives machines a way to tell live histories from impossible ones.

9. The Memory Consistency Card makes the evidence surface explicit. Local
   consistency evidence passes. Public Base Sepolia receipt evidence remains
   pending until the release record is filled.

10. The model name is FMM-0: FlowMemory Agent Memory Model.

## Demo Caption

```text
FlowMemory Reality Check: live histories pass, impossible histories fault.
```

```text
Memory Consistency Card: most AI memory retrieves context. FlowMemory checks whether the memory could have happened.
```

## Founder Script

FlowMemory starts with a Uniswap v4 `afterSwap` hook that emits a FlowPulse.
The swap is not the memory. The transaction is the proof envelope. The
FlowPulse is the memory artifact.

But the deeper launch claim is runtime consistency. Agents are becoming
distributed systems: model calls, tool calls, state writes, caches, and compute
jobs all crossing external events. FlowLitmus is our executable
forbidden-outcome suite. It tests whether an agent history respects FlowPulse
receipt boundaries or becomes impossible.

So the launch is not "we emitted an event." The launch is: FlowMemory gives
machines a way to tell live histories from impossible ones.

The Memory Consistency Card turns that into a scorecard. It shows which claims
are supported by repo evidence and which release evidence is still pending.

## Skeptic Replies

**Is this just an event?**

No. The on-chain hook emits a FlowPulse memory signal at a verified Uniswap v4
`afterSwap` boundary. The reader attaches receipt metadata later. FlowSerial and
FlowLitmus show how machine histories can use that boundary to reject impossible
runtime states.

**Does the hook verify AI memory?**

No. The hook emits the boundary signal. It does not validate semantic truth,
model correctness, or downstream AI claims.

**Does this control swaps or protect funds?**

No. The hook is deliberately narrow: `afterSwap`, PoolManager-gated, required
memory payload, zero hook delta, no custody, no routing, no dynamic fee path, no
custom accounting path.

**Why does this need a chain boundary?**

Because receipt facts are not self-authored by the agent. `txHash`, `logIndex`,
receipt status, and transaction ordering exist after the transaction lands and
are attached by reader/verifier infrastructure.

## Do Not Say

- live mainnet deployment;
- audited production infrastructure;
- custody;
- fund protection;
- swap control;
- custom accounting;
- semantic truth;
- model correctness;
- GPU acceleration;
- production compute verifier;
- `txHash` or `logIndex` known inside the hook.

## Say Instead

- first public FlowMemory hook surface;
- memory-native Uniswap v4 hook primitive;
- verified on-chain emission boundary design;
- FlowPulse memory signal;
- transaction as proof envelope;
- reader-attached receipt metadata;
- receipt-linearizable machine histories;
- executable forbidden outcomes for agent runtimes;
- local R&D runtime conformance suite.
- receipt-bound memory consistency model;
- claim-to-evidence launch scorecard;
- public Base Sepolia evidence pending until the release record is filled.
