# PulseRetire Queue

PulseRetire Queue is a receipt-driven retirement queue for speculative machine
cognition.

FlowMemory gives agents a reorder buffer for reality: they can compute
speculatively, but only receipt-bound FlowPulses can retire those thoughts into
live action.

The short line:

```text
The agent can speculate. The receipt decides what becomes real.
```

## Why It Exists

AI agents and GPU workflows increasingly compute ahead of the world. They draft
outputs, warm context, prepare actions, and stage cache reuse before external
events have actually settled.

Current memory systems usually let that speculative output leak into live state.
PulseRetire gives those artifacts a retirement discipline.

Before a matching FlowPulse receipt:

- model outputs are speculative;
- cache reuse is speculative;
- next actions are speculative;
- no causal nonce exists;
- nothing becomes live agent state.

After a matching receipt-bound FlowPulse:

- artifacts retire;
- a causal nonce is minted;
- outputs can become live;
- cache reuse can be bound to the receipt;
- agent actions can cite the boundary.

If the FlowPulse mismatches, the artifacts are squashed.

## Why The Hook Boundary Matters

This is not a timestamp gate.
This is not ordinary workflow orchestration.
This is not cache invalidation.

PulseRetire depends on an external boundary the agent cannot self-author.

The Uniswap v4 `afterSwap` hook emits the FlowPulse memory artifact after the
swap boundary. The transaction receipt is the proof envelope. The reader attaches
`txHash`, `logIndex`, receipt status, and block facts after execution.

The queued artifact may expect:

- `rootfieldId`;
- `commitment`;
- `hookAddress`;
- `subjectPoolId`;
- optional `parentPulseId`.

It may not include:

- `txHash`;
- `logIndex`;
- `transactionIndex`;
- `blockHash`.

Those facts are receipt-only. They do not exist inside the hook during execution.

## Demo Shape

```text
speculative model output
speculative cache reuse
speculative next action
        ↓
PulseRetire Queue
        ↓
matching FlowPulse receipt?
        ├── yes -> retire into live agent state
        └── no  -> squash / withhold / recompute
```

Run it:

```bash
python tools/pulse_retire.py demo --pretty
python -m unittest tools.test_pulse_retire
```

## Non-Claims

PulseRetire does not prove semantic truth.
It does not prove model correctness.
It does not prove GPU execution.
It does not accelerate hardware.
It does not custody funds.
It does not control swaps.
It is not audited production infrastructure.
It is not deployed mainnet infrastructure.
It does not mean the hook knows `txHash` or `logIndex`.

It proves whether a speculative artifact became causally live under a
deterministic policy after a receipt-bound FlowPulse arrived.
