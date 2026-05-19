# Obligation Membrane

Obligation Membrane checks whether multi-agent commerce preserves obligation
constraints across subagents, compute providers, aggregate work, refusal, and
payment closure.

SpendLine checks a spend.

DuplexLine checks a buyer/seller exchange.

Agent Commerce Conservation checks whether one episode balances.

Obligation Membrane asks the next launch-scale question:

```text
Can an obligation survive being passed through other agents without laundering
away its memory constraints?
```

## Core Sentence

```text
Autonomous commerce does not only need payments that settle. It needs
obligations that cannot be laundered.
```

## What It Checks

Obligation Membrane checks:

- FMM-0 requirements cannot be downgraded through a child obligation;
- fresh-compute requirements cannot become reuse underneath a parent;
- every delegated child obligation has lineage to the parent obligation;
- payee identity follows the work author unless an explicit payee delegation exists;
- a parent obligation cannot close while required child obligations remain open;
- child refusal or failure must propagate to the parent;
- aggregate work cannot silently omit failed or delegated child work;
- child rootfields either match or pass through an explicit bridge;
- child work cannot upgrade itself into semantic truth or model correctness;
- payment cannot close before the delegated work/compute chain closes.

## Demo

Run:

```bash
python tools/obligation_membrane.py demo --pretty
```

Expected result:

```text
Obligation Membrane

Valid chain:
  OM-OK-001  valid three agent compute chain                  MEMBRANE_ACCEPTED

Unsafe chains:
  OM-BAD-001 downgraded fmm0 requirement                      REJECTED
  OM-BAD-002 fresh compute requirement laundered               REJECTED
  OM-BAD-003 missing child obligation                         REJECTED
  OM-BAD-004 payee spine broken                               REJECTED
  OM-BAD-005 unresolved child obligation closed parent         REJECTED
  OM-BAD-006 child refusal swallowed                          REJECTED
  OM-BAD-007 rootfield drift across delegation                 REJECTED
  OM-BAD-008 aggregate work omits failed child                 REJECTED
  OM-BAD-009 unsupported truth upgrade                         REJECTED

Summary:
  obligation chains checked: 10
  valid chains accepted: 1/1
  unsafe chains rejected: 9/9
  escaped unsafe chains: 0
```

## Why It Matters

Agents will not only pay APIs.

They will hire brokers, delegate work, call compute providers, aggregate
outputs, retry failed branches, and settle later.

The failure mode is not only a bad wallet signature.

The deeper failure is this:

```text
An unsafe obligation gets passed through another agent until it looks clean.
```

Obligation Membrane names and tests that failure.

## Non-Claims

This is not custody.

This is not escrow.

This is not wallet authorization.

This is not fund protection.

This is not work-quality proof.

This is not semantic truth.

This is not model correctness.

This is not GPU acceleration.

This is not a live Base mainnet deployment claim.

This is not production verifier infrastructure.
