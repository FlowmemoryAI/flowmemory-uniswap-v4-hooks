# PulseRetire Queue Example

PulseRetire Queue is receipt-driven retirement for speculative machine
cognition.

An agent or GPU workflow can compute ahead, but the output stays speculative
until a matching receipt-bound `FlowPulse` retires it into live state.

```text
speculative model output
  -> PulseRetire Queue
  -> matching FlowPulse receipt?
      -> yes: retire into live agent state
      -> no: squash / withhold / recompute
```

Run the demo:

```bash
python tools/pulse_retire.py demo --pretty
```

Regenerate the example artifacts:

```bash
python tools/pulse_retire.py init \
  --agent-id demo-agent \
  --rootfield-id 0x1111111111111111111111111111111111111111111111111111111111111111 \
  --out examples/pulse-retire/queue.initial.json \
  --pretty

python tools/pulse_retire.py enqueue \
  --queue examples/pulse-retire/queue.initial.json \
  --artifact examples/pulse-retire/speculative-model-output.json \
  --out examples/pulse-retire/queue.after-one.json \
  --pretty

python tools/pulse_retire.py enqueue \
  --queue examples/pulse-retire/queue.after-one.json \
  --artifact examples/pulse-retire/speculative-cache-reuse.json \
  --out examples/pulse-retire/queue.after-two.json \
  --pretty

python tools/pulse_retire.py enqueue \
  --queue examples/pulse-retire/queue.after-two.json \
  --artifact examples/pulse-retire/speculative-agent-action.json \
  --out examples/pulse-retire/queue.after-enqueue.json \
  --pretty

python tools/pulse_retire.py retire \
  --queue examples/pulse-retire/queue.after-enqueue.json \
  --flowpulse examples/pulse-retire/flowpulse.matching.json \
  --out examples/pulse-retire/retirement.retired.example.json \
  --queue-out examples/pulse-retire/queue.after-retire.json \
  --pretty

python tools/pulse_retire.py retire \
  --queue examples/pulse-retire/queue.after-enqueue.json \
  --flowpulse examples/pulse-retire/flowpulse.mismatched.json \
  --out examples/pulse-retire/retirement.squashed.example.json \
  --pretty
```

Expected story:

```text
Before FlowPulse:
  model-output-001: speculative
  cache-reuse-001: speculative
  next-action-001: speculative

Matching FlowPulse:
  all artifacts retire
  causal nonce minted

Mismatched FlowPulse:
  artifacts are squashed
  fresh compute required
```

The agent can speculate. The receipt decides what becomes real.
