# ReceiptRuntime v0 Draft Spec

ReceiptRuntime is the minimal product loop that turns FlowMemory from an
observer into an action-memory architecture.

It adds one missing control-plane idea:

```text
Memory should gate the action before execution and settle the outcome after receipt evidence.
```

## Required Objects

| Object | Meaning |
| --- | --- |
| `PolicyCard` | A user or protocol policy describing which action may happen from which memory head. |
| `PulsePermit` | A pre-action authorization envelope bound to policy hash, actor, action intent, and memory head. |
| `ActionPulse` | A record that a permitted action was proposed through a selected route. |
| `FlowPulseLink` | A link between the action and the receipt-bound FlowPulse evidence. |
| `OutcomePulse` | A settlement record showing the permitted action produced the required receipt-bound outcome. |
| `PulsePass` | A portable, scoped claim derived from one or more outcome pulses. |

## Core Invariant

A valid receipt-runtime action must preserve this chain:

```text
PolicyCard
  -> PulsePermit
  -> ActionPulse
  -> FlowPulseLink
  -> OutcomePulse
  -> PulsePass claim
```

If the current memory head does not match the permit, the action is denied.

If the selected route cannot produce the required FlowPulse link, the route is
rejected.

If the user wants privacy, the PulsePass can reveal a predicate while hiding the
provider id, transaction hash, and amount.

## What This Proves

ReceiptRuntime proves that FlowMemory can be useful before and after execution:

- before execution, it gates actions by memory head and policy;
- after execution, it settles the outcome using receipt-bound evidence;
- after settlement, it gives the user a portable claim.

## What This Does Not Prove

ReceiptRuntime does not claim wallet authorization, custody, escrow, fund
protection, work-quality proof, semantic truth, production payment settlement,
TEE privacy, ZK privacy, or live Base mainnet deployment.

