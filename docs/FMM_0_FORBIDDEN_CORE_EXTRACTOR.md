# FMM-0 Forbidden Core Extractor

FMM-0 does not only catch impossible histories.

It can shrink them.

The Forbidden Core Extractor takes an invalid machine artifact or transition
and reduces it to the smallest mutation core that still violates the model.

Run:

```bash
python tools/fmm0_forbidden_core.py demo --pretty
```

Expected result:

```text
minimal cores found: 10/10
one-minimal cores: 10/10
escaped faults: 0
```

## Why This Matters

Without Forbidden Core, a reviewer sees:

```text
This machine history is invalid.
```

With Forbidden Core, a reviewer sees:

```text
This machine history is invalid because this minimal boundary-state core still faults.
```

That is useful for debugging agent runtimes, reader pipelines, receipt
projection, and future compute traces.

## What It Shrinks

The extractor covers ten deterministic failure families:

- pre-receipt `txHash` smuggling;
- pre-receipt `logIndex` smuggling;
- local-only to FMM-0 live without reader evidence;
- reader-derived to FMM-0 live without consistency evidence;
- reader-derived FlowPulse missing `txHash`;
- reader-derived FlowPulse missing `logIndex`;
- rootfield drift;
- commitment drift;
- semantic-truth overclaim;
- model-correctness overclaim.

## Non-Claims

Forbidden Core is not formal verification. It is not proof of complete safety.
It is not semantic truth, model correctness, custody, fund protection, Base
mainnet deployment, production verifier infrastructure, or GPU acceleration.

It is deterministic minimal-witness extraction for impossible machine histories.
