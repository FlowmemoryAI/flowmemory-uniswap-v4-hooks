# Agent Commerce Differential Harness

The Agent Commerce Differential Harness shows the category delta in one table:

```text
Ordinary rails can accept an action surface while FlowMemory rejects the machine history.
```

This is the shortest way to explain why memory-native agent commerce is not
just another wallet, payment rail, indexer, or agent log.

Normal rails answer whether an action can execute.

FlowMemory asks whether the machine history that produced it is legal.

## What It Compares

The ordinary baseline is intentionally simple:

- wallet signature valid;
- spend permission in scope;
- session key in scope;
- x402-style payment requirement satisfied;
- identity present;
- receipt observed by an indexer;
- cache fingerprint matches.

The FlowMemory side checks whether the same action surface survives local
memory-consistency rules:

- SpendLine;
- DuplexLine;
- Agent Commerce Conservation;
- Obligation Membrane;
- DischargeLine;
- Compute ChargeLine;
- FMM-0 fault state.

## Why It Matters

A valid signature, satisfied payment requirement, observed receipt, present
identity, and matching cache fingerprint can still belong to an impossible
agent-commerce history.

The differential cases make that visible:

| Ordinary rail accepts | FlowMemory rejects because |
| --- | --- |
| Valid signature | Memory head is stale. |
| x402-style payment satisfied | Receipt closes the wrong obligation. |
| Identity present | Payee spine is broken. |
| Permission in scope | Declared intent is replayed. |
| Cache fingerprint matches | Source artifact is not FMM-0 conforming. |
| Indexer sees receipt | Post-spend FlowPulse is missing. |
| Session key in scope | AxiomPatch downgrade was ignored. |
| Compute payment receipt exists | Receipt does not match the declared compute route. |
| Child permission valid | Child refusal was swallowed by the parent obligation. |

## Run It

```bash
python tools/agent_commerce_differential.py demo --pretty
python tools/agent_commerce_differential.py demo --json --pretty
python -m unittest tools.test_agent_commerce_differential
```

Expected summary:

```text
valid cases accepted by both: 1/1
differential failures caught by FlowMemory: 9/9
unsafe histories accepted by ordinary baseline only: 9
escaped unsafe histories: 0
```

## What This Is Not

Do not claim from this harness:

- custody;
- escrow;
- wallet authorization;
- fund protection;
- semantic truth;
- model correctness;
- GPU acceleration;
- live Base mainnet deployment;
- production verifier infrastructure.

This is a local baseline simulator plus FlowMemory conformance harness.

That is the point.

