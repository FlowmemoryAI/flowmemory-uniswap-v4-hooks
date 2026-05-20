# Receipt Runtime Architecture

The missing product primitive is not another hook.

It is the loop around the hook:

```text
PolicyCard -> PulsePermit -> ActionPulse -> FlowPulseLink -> OutcomePulse -> PulsePass
```

FlowMemory becomes useful when memory does two things:

1. gates an action before execution;
2. settles the outcome after receipt evidence exists.

## Why This Matters

Generic agents can act.

Wallets can sign.

x402-style rails can pay.

FlowMemory asks a different question:

```text
Did this action happen from the right memory head, under the right policy, and did it produce the required receipt-bound outcome?
```

That is the product wedge. FlowMemory is not a generic agent marketplace or a
generic reputation system. It is a receipt-runtime layer for autonomous action.

## Object Model

| Object | Job |
| --- | --- |
| `PolicyCard` | Defines what the user or protocol allows. |
| `PulsePermit` | Binds a proposed action to the current memory head and policy hash. |
| `ActionPulse` | Records the selected route and permitted action intent. |
| `FlowPulseLink` | Links the action to receipt-bound FlowPulse evidence. |
| `OutcomePulse` | Settles the action outcome after receipt evidence exists. |
| `PulsePass` | Lets a user privately carry a scoped claim derived from the outcome. |

## Incentive Loop

```text
safe memory history -> lower required bond -> better route access -> successful outcome -> portable PulsePass claim -> higher future limits
```

Users get:

- portable proof of policy-safe outcomes;
- scoped disclosure instead of full wallet-history exposure;
- higher limits or better access when their receipt-bound memory supports it.

Developers get:

- a way to compete on task-specific successful outcomes instead of generic
  reputation;
- deterministic reason codes for denied actions;
- a clean integration loop that is smaller than building a whole agent economy.

Providers get:

- route priority when they produce bonded, policy-safe outcomes;
- a cost-per-success score instead of a raw price race.

## Demo

Run:

```bash
python tools/receipt_runtime_demo.py --pretty
```

Expected result:

```text
Selected route: provider.private-bonded
PulsePermit:    ALLOW
OutcomePulse:   OUTCOME_SETTLED
```

The cheapest provider loses because it does not carry the required bond or
expected FlowPulse link. The selected provider is not the cheapest raw route; it
is the cheapest route that can produce a policy-safe receipt-bound outcome.

## Security Boundary

ReceiptRuntime does not authorize wallets, custody funds, escrow payments, or
prove work quality.

It checks whether the action chain is memory-consistent:

- current memory head;
- policy hash;
- action intent hash;
- selected provider route;
- receipt-bound FlowPulse link;
- outcome settlement;
- scoped user claim.

## Public Line

Use:

```text
FlowMemory turns autonomous actions into receipt-bound outcomes users can privately carry.
```

Use:

```text
Cheap agents are not enough. FlowMemory routes by cost per successful receipt-bound outcome.
```

Avoid:

```text
FlowMemory protects funds.
FlowMemory authorizes wallet transactions.
FlowMemory proves every action was good.
FlowMemory provides live escrow.
```

