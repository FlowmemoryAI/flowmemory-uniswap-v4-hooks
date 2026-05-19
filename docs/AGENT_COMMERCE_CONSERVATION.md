# Agent Commerce Conservation Lab

Agent Commerce Conservation Lab checks whether an autonomous commerce episode
conserves declared obligations across spend, work, compute, refusal, and
receipt-bound memory state.

DuplexLine checks whether one buyer/seller exchange is co-serializable.

Conservation Lab asks the next systems question:

```text
Did the whole commerce episode balance?
```

## Core Sentence

```text
Autonomous commerce does not only need payments that settle. It needs
obligations that conserve.
```

## What It Checks

Conservation Lab checks:

- every obligation closes exactly once;
- no obligation closes twice;
- every closure targets a declared obligation;
- payment closures discharge payment obligations;
- work closures discharge work obligations;
- participant memory heads match the episode expectations;
- unsafe compute reuse cannot close a compute payment;
- a rejected exchange produces a refusal or repair state.

## Demo

Run:

```bash
python tools/agent_commerce_conservation.py demo --pretty
```

Expected result:

```text
Agent Commerce Conservation Lab

Valid episode:
  ACC-OK-001  PASS  CONSERVED            all_conservation_gates_passed

Invalid episodes:
  ACC-BAD-001 PASS  REJECT_CONSERVATION  allClosuresTargetObligations
  ACC-BAD-002 PASS  REJECT_CONSERVATION  allClosuresTargetObligations
  ACC-BAD-003 PASS  REJECT_CONSERVATION  everyObligationClosesExactlyOnce
  ACC-BAD-004 PASS  REJECT_CONSERVATION  everyObligationClosesExactlyOnce
  ACC-BAD-005 PASS  REJECT_CONSERVATION  memoryHeadsCompatible
  ACC-BAD-006 PASS  REJECT_CONSERVATION  unsafeComputeReuseCannotClosePayment
  ACC-BAD-007 PASS  REJECT_CONSERVATION  rejectedExchangeHasRefusal

Invariant coverage:
  ACC-I1  PASS  Every obligation closes at most once
  ACC-I2  PASS  Every payment discharges one payment obligation
  ACC-I3  PASS  Every work delivery matches one work obligation
  ACC-I4  PASS  No closure crosses incompatible memory heads
  ACC-I5  PASS  Unsafe compute reuse cannot close payment
  ACC-I6  PASS  Rejected exchange requires refusal or repair

Summary:
  episodes checked: 8
  valid episodes conserved: 1/1
  invalid episodes rejected: 7/7
  escaped invalid episodes: 0

Result:
  Agent commerce must conserve declared obligations across spend, work, compute, and memory state.
```

## Why It Matters

Wallets can authorize a payment.

x402-style flows can move payment over an API flow.

Indexers can show that payment and work events happened.

Conservation Lab checks whether the episode balanced under the memory model.

It catches:

- payment with no matching work/payment obligation;
- work delivery with no matching work obligation;
- double-paid obligations;
- double-delivered work;
- work paid under a stale buyer memory head;
- compute payment closed against unsafe reuse;
- rejected exchange without a refusal or repair state.

## Non-Claims

This is not custody.

This is not escrow.

This is not wallet authorization.

This is not fund protection.

This is not work-quality proof.

This is not semantic truth.

This is not model correctness.

This is not a live Base mainnet deployment claim.

This is not production verifier infrastructure.
