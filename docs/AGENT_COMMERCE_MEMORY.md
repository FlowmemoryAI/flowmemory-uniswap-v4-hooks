# Agent Commerce Memory

AI agents on Base will not only chat, retrieve, and summarize.

They will pay APIs, hire other agents, buy compute, route work, retry failed
tasks, delegate to subagents, and move value through smart-account and payment
rails.

The missing layer is not another wallet.

The missing layer is memory consistency for autonomous commerce.

```text
Wallets answer: can this key spend?
x402 answers: can this payment requirement be satisfied?
Agent identity answers: who is this agent?
FlowMemory asks: could this economic action have legally emerged from the
agent's receipt-bound memory state?
```

That is the category:

```text
memory-native agent commerce
```

## What Base Gives Agents

Base agent infrastructure points toward agents with:

- wallets;
- USDC payments;
- x402-style pay-per-request flows;
- registration and identity surfaces;
- smart-account execution;
- service discovery.

Those rails matter.

They make autonomous commerce possible.

They do not, by themselves, make agent commerce memory-consistent.

## The FlowMemory Layer

FlowMemory adds the layer that checks whether an agent's economic action is
compatible with the machine history that produced it.

The thesis is simple:

```text
Signed payment is not enough.
Indexed logs are not enough.
Output hashes are not enough.

Agent commerce needs serializable economic memory.
```

## First Public Surfaces

### SpendLine

SpendLine is memory-linearizability for autonomous agent spending.

It checks whether a declared spend can be admitted into a receipt-bound memory
history before downstream systems treat that spend as memory-consistent.

It rejects:

- stale memory heads;
- duplicate spend intents;
- missing post-spend FlowPulse signals;
- receipt facts claimed before receipt boundaries;
- ignored AxiomPatch downgrades;
- x402-style payment requirement drift;
- compute reuse/payment drift.

Core line:

```text
Agents do not only need wallets. They need spend histories that cannot lie
about what they remembered.
```

### DuplexLine

DuplexLine is co-serializability for autonomous buyer/seller exchange.

It composes buyer-side SpendLine, seller work memory, payment requirement
binding, compute/cache reuse status, and FlowSerial ordering.

It rejects:

- wrong-task seller output;
- stale buyer or seller memory;
- payment requirement drift;
- missing seller WorkLine serialization;
- duplicate buyer intent replay;
- counterparty-payee rebinding;
- work replay across buyers;
- double-consumed payment requirements;
- seller reuse that violates buyer fresh-compute policy;
- impossible exchange schedules;
- payment receipt facts smuggled before settlement;
- task endpoint drift;
- reader-derived seller state presented as FMM-0 live.

Core line:

```text
Wallets move funds. x402 moves payments. DuplexLine checks whether buyer spend
and seller work can exist in the same legal machine history.
```

## What Comes Next

These are follow-on primitives that fit the same memory-native agent-commerce
model.

### QuoteLock

Locks a quote, payment requirement, service endpoint, and memory head together.

```text
An agent should not pay a quote from a world it no longer inhabits.
```

### IdentityHeadlock

Binds an agent identity assertion to the rootfield head used for the economic
action.

```text
Identity tells you who signed. Headlock tells you what world they signed from.
```

### DelegationSpine

Requires subagent actions to remain attached to the parent memory head,
delegation commitment, and allowed action surface.

```text
Subagents should inherit memory constraints, not just permissions.
```

### PurseEpoch

Advances agent budget state by receipt-bound memory epochs instead of vague
wall-clock resets.

```text
Agent budgets should not reset by vibes; they should advance by legal memory
epochs.
```

### IntentTombstone

Extinguishes sibling branches after one spend/work intent settles.

```text
Agents need a way to kill old intent branches after money moves.
```

### Receipt-Tethered Refusal

Turns unsafe spend/work attempts into reusable refusal artifacts tied to FMM-0
faults and repair conditions.

```text
A refusal should become part of machine state, not a forgotten chat message.
```

### ToolCall Spend Membrane

Requires value-moving tool calls to pass through spend-memory checks before
wallet submission.

```text
Agents do not only sign transactions; they call tools that move money.
Those calls need a memory membrane.
```

### Agent Solvency Memory

Checks declared obligation consistency across open SpendLines, WorkLines,
PurseEpochs, and IntentTombstones.

```text
Agents need memory-consistent obligations before they need reputation scores.
```

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

FlowMemory is defining local, deterministic memory-consistency surfaces for
autonomous economic agents.

## Sources

- Base AI agents overview: <https://docs.base.org/ai-agents/index>
- Base AI-agent payments quickstart: <https://docs.base.org/ai-agents/quickstart/payments>
- Base agent registration and identity: <https://docs.base.org/ai-agents/setup/agent-registration>
- x402 payment concepts: <https://docs.base.org/ai-agents/core-concepts/payments-and-transactions>
