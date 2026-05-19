# FMM-0 Counterexample Forge

FMM-0 should not only pass examples.

It should catch counterexamples.

The Counterexample Forge is the adversarial launch harness for FMM-0 Phase
Space. It mutates valid machine artifacts into impossible histories and checks
whether the local model rejects them.

Run:

```bash
python tools/fmm0_counterexample_forge.py demo --pretty
```

Expected result:

```text
Generated counterexamples: 12
Caught by FMM-0: 12/12
Escaped: 0
Result: FMM-0 is not just a claim; it has adversarial counterexamples.
```

## Why This Is Not A Normal Memory Benchmark

Most AI-memory systems benchmark recall, personalization, latency, token cost,
retrieval depth, and graph quality.

Those are useful, but they do not test the FlowMemory question:

```text
Could this memory history have happened?
```

Counterexample Forge tests the negative space. It creates states that should be
impossible around FlowPulse receipt boundaries:

- a local artifact claims `txHash` before the receipt exists;
- a local artifact claims `logIndex` before the receipt exists;
- a speculative local output tries to publish as live;
- a reader-derived FlowPulse tries to become FMM-0 live without consistency
  checks;
- a receipt with the wrong rootfield/commitment tries to anneal a local output;
- receipt evidence is used to overclaim semantic truth or model correctness.

## Why The Chain Boundary Matters

The Uniswap v4 `afterSwap` hook emits the FlowPulse memory artifact. The
transaction is the proof envelope. The reader attaches receipt facts later.

Counterexample Forge tests that the model does not collapse those stages.

Receipt facts cannot appear before receipt attachment. Reader-derived evidence
does not automatically become FMM-0 live history. FMM-0 live state requires
consistency checks.

## What This Proves

It proves that the local repo can generate and catch adversarial violations of
the FMM-0 phase model.

It does not prove semantic truth, model correctness, production verifier
infrastructure, custody, fund protection, GPU acceleration, or Base mainnet
deployment.
