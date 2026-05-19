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

For the phase-space demo:

```bash
python tools/fmm0_phase_table.py demo --pretty
```

This shows the key transition: local-only speculative artifacts cannot jump
directly into FMM-0-conforming live state, and pre-receipt artifacts cannot
claim `txHash` or `logIndex`.

For the adversarial counterexample demo:

```bash
python tools/fmm0_counterexample_forge.py demo --pretty
```

This generates impossible histories and checks that FMM-0 catches them.

For the memory-algebra closure demo:

```bash
python tools/fmm0_closure_lab.py demo --pretty
```

This checks that valid receipt-bound memory composition stays valid, while
rollback, split-brain heads, pre-receipt receipt facts, and semantic overclaims
are rejected.

For the cross-layer boundary projection demo:

```bash
python tools/fmm0_boundary_bisim.py demo --pretty
```

This checks that the same FlowPulse boundary survives hook signal, receipt
envelope, and FMM-0 runtime projection without rootfield, commitment, or receipt
drift.

For the minimal forbidden-core demo:

```bash
python tools/fmm0_forbidden_core.py demo --pretty
```

This shrinks impossible histories into one-minimal diagnostic cores so an
integrator can see the smallest reason a machine history failed.

For the witness pack:

```bash
python tools/fmm0_witness_pack.py demo --pretty
```

This bundles the local conformance surface into one reproducible evidence
packet while keeping public Base Sepolia evidence pending.

For the Solidity ABI/model drift gate:

```bash
python tools/flowpulse_boundary_abi.py check --pretty
```

This verifies that the `FlowPulse` hook-time event surface still excludes
receipt-only fields like `txHash` and `logIndex`.

For that, run the Memory Consistency Card:

```bash
python tools/memory_consistency_card.py --pretty
```

It maps the claim to evidence: hook boundary, FlowPulse emission, receipt
metadata separation, reader-derived proof envelope, FlowSerial, FlowLitmus, and
pending public Base Sepolia receipt evidence.

For skeptical reviewers:

```bash
python tools/reviewer_walkthrough.py --pretty
```

This maps every launch claim to files, commands, expected results, status, and
explicit non-claims.

For the public release evidence gate:

```bash
python tools/verify_release_evidence.py --pretty
```

This stays `PENDING` until a real `RELEASE_EVIDENCE.json` packet validates.

For the FlowLitmus casebook:

```bash
python tools/render_flowlitmus_casebook.py --check
```

This names each impossible machine history and the FlowMemory fault that catches it.

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

8. FMM-0 Phase Space shows machine-state phases: local-only,
   public-boundary, reader-derived, FMM-0-conforming, quarantined, and extinct.

9. Counterexample Forge mutates valid artifacts into impossible histories and
   checks that FMM-0 catches them.

10. The launch claim is not "we emitted an event." The launch claim is:
   FlowMemory gives machines a way to tell live histories from impossible ones.

11. The Memory Consistency Card makes the evidence surface explicit. Local
   consistency evidence passes. Public Base Sepolia receipt evidence remains
   pending until the release record is filled.

12. The model name is FMM-0: FlowMemory Agent Memory Model.

13. The skeptic walkthrough makes the claim surface reviewable: every launch
    claim has a command, and every overclaim has a red line.

14. Public Base Sepolia receipt evidence stays `PENDING` until the release
    evidence gate validates the actual packet.

15. The forbidden-outcomes casebook translates FlowLitmus from a test suite into
    a reviewer-readable memory-model casebook.

16. Cache Lineage Gate shows the context-memory angle: KV/context reuse should
    be proof-carried, not vibe-carried.

17. Compute Reuse Router shows the AI/GPU angle without overclaiming hardware:
    proof-backed compute memory can become a scheduler reuse decision.

18. Compute Reuse Consistency ties the AI/GPU angle back to the memory model:
    cache lineage, compute fingerprint, and receipt-bound history all have to
    pass before reuse becomes live.

19. FlowMemory Release Transcript gives one offline object for what passed,
    what is pending, and what is explicitly not claimed.

## Demo Caption

```text
FlowMemory Reality Check: live histories pass, impossible histories fault.
```

```text
Memory Consistency Card: most AI memory retrieves context. FlowMemory checks whether the memory could have happened.
```

```text
FMM-0 Skeptic Walkthrough: every launch claim has a command, and every overclaim has a red line.
```

```text
FMM-0 Phase Space: retrieval treats memory as text; FMM-0 treats machine history as phase space.
```

```text
Counterexample Forge: FMM-0 is not just a claim; it has adversarial counterexamples.
```

```text
Release Evidence Gate: public receipt evidence stays pending until the Base Sepolia packet validates.
```

```text
FlowLitmus casebook: each impossible history has a name, a boundary reason, and a fault.
```

```text
Cache Lineage Gate: KV reuse should be proof-carried, not vibe-carried.
```

```text
Compute Reuse Router: the fastest GPU job is the one the system can prove it does not need to run again.
```

```text
Compute reuse without memory consistency is just cache optimism.
```

```text
Release Transcript: local evidence is green, public receipt evidence is pending, and overclaims are fenced out.
```

## Founder Script

FlowMemory starts with a Uniswap v4 `afterSwap` hook that emits a FlowPulse.
The swap is not the memory. The transaction is the proof envelope. The
FlowPulse is the memory artifact.

But the deeper launch claim is runtime consistency. Agents are becoming
distributed systems: model calls, tool calls, state writes, caches, and compute
jobs all crossing external events. FMM-0 Phase Space shows that
machine artifacts have phases: local-only, reader-derived, FMM-0-conforming,
quarantined, or extinct. Counterexample Forge mutates valid artifacts into
impossible histories and checks that FMM-0 catches them. FlowLitmus is our
executable forbidden-outcome suite. It tests whether an agent history respects
FlowPulse receipt boundaries or becomes impossible.

So the launch is not "we emitted an event." The launch is: FlowMemory gives
machines a way to tell live histories from impossible ones.

The Memory Consistency Card turns that into a scorecard. It shows which claims
are supported by repo evidence and which release evidence is still pending.

The Skeptic Walkthrough is the credibility layer: it maps each public claim to
evidence, commands, expected results, status, and explicit non-claims.

The Release Transcript is the launch packaging layer: one offline object says
what passed, what is still pending, and what the repo does not claim.

The Cache Lineage Gate is the context-memory bridge: it checks whether reusable
KV/context memory carries the right tokenizer, side-input, adapter, runtime, and
policy commitments before the scheduler trusts it.

The Compute Reuse Router is the GPU workflow bridge: it does not make a chip
faster, but it shows how proof-backed memory can stop safe prior compute from
being run twice.

The Compute Reuse Consistency Harness is the systems bridge: cache lineage,
compute fingerprint compatibility, and receipt-bound history must all pass
before autonomous compute reuse becomes live.

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
- machine-state phase space;
- adversarial counterexamples for impossible machine histories;
- forbidden phase transitions around FlowPulse receipt boundaries.
- claim-to-evidence launch scorecard;
- public Base Sepolia evidence pending until the release record is filled.
- every launch claim has a command, and every overclaim has a red line.
- public receipt evidence pending until `RELEASE_EVIDENCE.json` validates.
