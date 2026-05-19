# DischargeLine

DischargeLine checks whether a receipt closes the right obligation.

The core distinction:

```text
Settlement is not discharge.
```

A transaction can settle while the obligation remains open.

Wallets show that money moved.

DischargeLine asks whether the right obligation actually closed under FMM-0,
post-spend FlowPulse memory, conservation, membrane, and compute-route checks.

## What It Checks

DischargeLine checks:

- a receipt envelope exists;
- the receipt binds to the declared obligation and spend intent;
- the recipient matches the expected payee;
- the payment requirement hash did not drift;
- a post-spend FlowPulse memory artifact exists;
- discharge state is FMM-0 live;
- Agent Commerce Conservation accepted the episode;
- Obligation Membrane accepted the delegated chain;
- compute discharge agrees with Compute ChargeLine;
- the obligation has not already been discharged;
- child refusals are not still open;
- discharge does not upgrade into work quality, semantic truth, or model correctness;
- receipt-time fields do not appear in pre-discharge obligation fields.

## Demo

Run:

```bash
python tools/dischargeline_harness.py demo --pretty
```

Expected result:

```text
DischargeLine Harness

Valid discharges:
  DCL-OK-001  valid x402 work discharge              DISCHARGE_ACCEPTED
  DCL-OK-002  valid compute discharge                DISCHARGE_ACCEPTED

Invalid discharges:
  DCL-BAD-001 wrong obligation receipt               REJECTED
  DCL-BAD-002 wrong recipient discharge              REJECTED
  DCL-BAD-003 stale quote discharge                  REJECTED
  DCL-BAD-004 duplicate discharge                    REJECTED
  DCL-BAD-005 discharge without receipt              REJECTED
  DCL-BAD-006 discharge after child refusal          REJECTED
  DCL-BAD-007 compute route mismatch discharge       REJECTED
  DCL-BAD-008 missing post spend flowpulse           REJECTED
  DCL-BAD-009 semantic completion overclaim          REJECTED
  DCL-BAD-010 receipt fields in obligation           REJECTED

Summary:
  discharge cases checked: 12
  valid discharges accepted: 2/2
  invalid discharges rejected: 10/10
  escaped invalid discharges: 0
```

## Why It Matters

Autonomous commerce needs more than payment success.

An agent can pay the wrong obligation, pay the wrong recipient, reuse a stale
quote, discharge twice, ignore child refusal, or claim completion without a
post-spend memory boundary.

DischargeLine makes obligation completion receipt-bound and memory-consistent.

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
