# FlowLitmus Launch Demo

FlowLitmus is the launch-grade demonstration that FlowMemory is more than a hook
demo and more than a memory metaphor.

It shows a runtime model.

It shows forbidden outcomes.

It runs them.

## One-Line Demo

```bash
python tools/flow_litmus.py run --suite examples/flow-litmus/litmus.manifest.json
```

Expected output:

```text
FlowLitmus Runtime Consistency Suite

FM-LB-001   pre-receipt txHash read                PASS  forbidden_pre_receipt_read
FM-SER-001  retrocausal receipt claim              PASS  retrocausal_receipt_claim
FM-QS-001   unquiesced post-boundary output        PASS  QuiescenceViolation
FM-RT-001   speculative output escaped             PASS  RetirementViolation
FM-FIS-001  stale output survived boundary         PASS  BoundaryFissionViolation
FM-SER-002  rootfield rollback                     PASS  rootfield_rollback
FM-SER-003  split-brain canonical write            PASS  split_brain_write
FM-OK-001   valid boundary history                 PASS  Serializable

8/8 passed
```

## Casebook

Explain each forbidden outcome:

```bash
python tools/render_flowlitmus_casebook.py --check
```

The casebook is [FLOWLITMUS_FORBIDDEN_OUTCOMES.md](FLOWLITMUS_FORBIDDEN_OUTCOMES.md).

## Why This Lands

FlowLitmus speaks a systems language:

- memory-model litmus tests;
- distributed consistency;
- happens-before boundaries;
- forbidden outcomes;
- serializable histories;
- rollback and split-brain faults.

For launch, that matters more than adding another primitive. It tells a
skeptical reviewer that FlowMemory is defining a runtime model with executable
rules, not only publishing ambitious words.

## Founder Script

FlowMemory started with a Uniswap v4 `afterSwap` hook that emits a FlowPulse.
The swap is not memory. The transaction is the proof envelope. The FlowPulse is
the memory artifact.

But the deeper point is not just memory. It is runtime consistency. Agents are
distributed systems now: model calls, tools, caches, state writes, and GPU jobs
all running across external events.

FlowLitmus makes that concrete. It is an executable suite of forbidden outcomes
for agent reality. It feeds the runtime adversarial histories: a model claiming
`txHash` before the receipt exists, a stale output crossing a boundary, a
rootfield rollback, a split-brain canonical write.

If the history respects FlowPulse receipt boundaries, it passes. If the history
is impossible, FlowLitmus catches it.

FlowMemory gives agents memory signals. FlowLitmus proves the runtime knows what
histories are impossible.

## Non-Claims

FlowLitmus does not prove semantic truth, model correctness, GPU execution,
custody, fund safety, live deployment, audited production readiness, or
production safety.
