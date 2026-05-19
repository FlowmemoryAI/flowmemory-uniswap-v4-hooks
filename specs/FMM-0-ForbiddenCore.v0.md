# FMM-0 Forbidden Core v0

FMM-0 Forbidden Core Extractor is the deterministic diagnostic layer for the
FlowMemory Agent Memory Model.

Counterexample Forge catches impossible histories.

Forbidden Core shrinks them.

It takes an invalid machine artifact, transition, or boundary drift case and
extracts a minimal mutation core: the smallest set of boundary-state atoms that
still produces the same FMM-0 fault relative to a valid baseline.

## Core Properties

- The full invalid case produces the expected fault.
- The extracted core still produces the expected fault.
- Removing any one atom from the extracted core changes or removes that fault.
- The core is diagnostic, deterministic, and launch-reviewable.

## Non-Claims

Forbidden Core is not formal verification. It is not semantic truth, model
correctness, custody, fund protection, Base mainnet deployment, production
verifier infrastructure, or GPU acceleration.

It is minimal-witness extraction for impossible machine histories.
