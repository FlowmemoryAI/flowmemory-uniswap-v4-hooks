# Agent Commerce Invariants

Autonomous commerce is not complete when a payment settles.

It is complete when the right obligation closes under a legal machine history.

FlowMemory's agent-commerce harnesses are not random demos. They are a layered
invariant surface for agents that transact, delegate, compute, pay, receive,
and remember on top of receipt-bound FlowPulse evidence.

| Harness | Invariant | Ordinary rails do not catch |
| --- | --- | --- |
| Compute Reuse Consistency | Compute/cache reuse must match live lineage, runtime, receipt, and memory-head constraints. | A cached result reused from stale or incompatible memory. |
| Compute Reuse Router | A cheaper or faster route must still be admissible under proof-backed compute history. | A route that saves compute by violating lineage. |
| Compute ChargeLine | A compute payment must match the memory-consistent compute route. | Paying fresh-compute pricing for reused work, or charging reuse as if it were fresh. |
| SpendLine | Autonomous spend must be memory-linearizable. | A valid signature from a stale or impossible memory head. |
| DischargeLine | A receipt must close the correct obligation exactly once. | A payment settled while the obligation remains open or closes the wrong work. |
| DuplexLine | Buyer spend and seller work must be co-serializable. | Payment history and work history that each look valid alone but cannot be true together. |
| Agent Commerce Conservation | Spend, work, compute, refusal, discharge, and memory state must balance across the episode. | Orphan payments, duplicate discharge, missing work, or unclosed obligations. |
| Obligation Membrane | Delegation must preserve the original obligation constraints. | Laundering obligation risk through subagents, compute providers, or aggregate work. |

## The Category

Payments move value.

FlowMemory checks whether the obligation history is legal.

That is the category: memory-native agent commerce.

The purpose is not to prove semantic truth or work quality. The purpose is to
make impossible commerce histories fail deterministically before they become
trusted downstream memory.

## Public Line

```text
Autonomous commerce does not only need payments that settle. It needs
obligations that conserve.
```

