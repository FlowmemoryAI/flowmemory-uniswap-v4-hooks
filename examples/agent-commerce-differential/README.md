# Agent Commerce Differential Example

Run:

```bash
python tools/agent_commerce_differential.py demo --pretty
python tools/agent_commerce_differential.py run --cases examples/agent-commerce-differential/differential-cases.json --pretty
```

The example shows one valid case accepted by both ordinary rails and
FlowMemory, plus nine differential cases where ordinary rails accept the action
surface and FlowMemory rejects the machine history.

It is local deterministic conformance only. It is not custody, escrow, wallet
authorization, fund protection, semantic truth, model correctness, GPU
acceleration, live mainnet deployment, or production verifier infrastructure.

