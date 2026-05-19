# FlowMemory Tools

This folder contains dependency-light launch and evidence utilities.

## `read_flowpulse_logs.py`

Reads logs from a deployed `FlowMemoryAfterSwapHook`, decodes `AfterSwapObserved` and `FlowPulse`, fetches transaction receipts, and writes a proof-envelope JSON record.

The script does not need a private key. It only reads JSON-RPC data.

```bash
python tools/read_flowpulse_logs.py \
  --rpc-url "$BASE_SEPOLIA_RPC_URL" \
  --hook-address "$FLOWMEMORY_HOOK_ADDRESS" \
  --from-block 0 \
  --to-block latest \
  --pretty \
  --output releases/base-sepolia/flowpulse-evidence.json
```

Environment variable form:

```bash
export FLOWMEMORY_RPC_URL="$BASE_SEPOLIA_RPC_URL"
export FLOWMEMORY_HOOK_ADDRESS="0x..."
export FLOWMEMORY_FROM_BLOCK="0"
export FLOWMEMORY_TO_BLOCK="latest"
export FLOWMEMORY_FINALITY_CONFIRMATIONS="20"

python tools/read_flowpulse_logs.py --pretty
```

The output preserves the split that matters:

- `FlowPulse` payload comes from the hook log;
- `txHash`, `transactionIndex`, `logIndex`, receipt status, and block facts come from receipts;
- finality status comes from the configured confirmation policy.

Decoder tests:

```bash
python -m unittest tools.test_read_flowpulse_logs
```

## `memory_trace.py`

Builds a proof-carried Agent Memory Pack from a MachineMemoryTrace.

This is the R&D bridge from FlowPulse to useful AI-agent memory:

- validates pulse graph structure;
- computes deterministic trace and artifact fingerprints;
- emits recall cards an agent can cite;
- surfaces reusable ComputePulse candidates;
- labels R&D/mock artifacts as notes instead of deployed verifier claims.

```bash
python tools/memory_trace.py verify-trace \
  examples/pulse-trace/trace.example.json \
  --pretty \
  --output examples/pulse-trace/agent-memory-pack.example.json
```

Fingerprint only:

```bash
python tools/memory_trace.py fingerprint examples/pulse-trace/trace.example.json
```

Tests:

```bash
python -m unittest tools.test_memory_trace
```

## `axiom_writ.py`

Mints, verifies, and applies AxiomWrit objects.

AxiomWrit is the proof-conditioned cognition R&D primitive:

- a FlowPulse is remembered;
- an AxiomWrit is believed;
- a plan can cite a boundary claim if the writ allows it;
- a plan is denied if it overclaims semantic truth or on-chain action authority.

Run the demo:

```bash
python tools/axiom_writ.py demo --pretty
```

Regenerate example artifacts:

```bash
python tools/axiom_writ.py mint \
  --flowpulse-evidence examples/axiom-writ/flowpulse-evidence.fixture.json \
  --claim examples/axiom-writ/claim.swap-boundary.json \
  --policy examples/axiom-writ/policy.agent.json \
  --agent-id demo-agent \
  --out examples/axiom-writ/axiomwrit.example.json \
  --pretty
```

Tests:

```bash
python -m unittest tools.test_axiom_writ
```

## `axiom_patch.py`

Mints and applies AxiomPatch cognitive state transitions.

AxiomPatch is the operational mutation of AxiomWrit:

- citation-like actions can be allowed;
- unsafe action requests can be downgraded;
- overclaims or custody-like actions can be denied;
- proof-masked context is returned for the agent runtime.

Run the demo:

```bash
python tools/axiom_patch.py demo --pretty
```

Regenerate example artifacts:

```bash
python tools/axiom_patch.py mint \
  --flowpulse-evidence examples/axiom-patch/flowpulse-evidence.fixture.json \
  --claim examples/axiom-patch/claim.swap-boundary.json \
  --policy examples/axiom-patch/policy.patch.json \
  --agent-id demo-agent \
  --out examples/axiom-patch/axiompatch.example.json \
  --pretty

python tools/axiom_patch.py apply \
  --patch examples/axiom-patch/axiompatch.example.json \
  --plan examples/axiom-patch/plan.mixed-actions.json \
  --out examples/axiom-patch/verdict.allowed-downgraded-denied.json \
  --pretty
```

Tests:

```bash
python -m unittest tools.test_axiom_patch
```

## `boundary_fission.py`

Applies BoundaryFission memory release to an agent working set.

BoundaryFission is proof-triggered forgetting:

- a receipt-bound `FlowPulse` is the trigger;
- receipt-bound facts are conserved;
- stale model/cache outputs become `ResidueAtom` commitments;
- unsupported claims are quarantined;
- pre-boundary executable branches become `BranchAsh`;
- fresh recompute tasks can be delegated from the current boundary.

Run the demo:

```bash
python tools/boundary_fission.py demo
```

Regenerate example artifacts:

```bash
python tools/boundary_fission.py apply \
  --flowpulse examples/boundary-fission/flowpulse-evidence.fixture.json \
  --memory examples/boundary-fission/agent-working-memory.before.json \
  --policy examples/boundary-fission/fission-policy.fixture.json \
  --report examples/boundary-fission/fission-report.example.json \
  --after examples/boundary-fission/agent-working-memory.after.json \
  --pretty

python tools/boundary_fission.py verify \
  --report examples/boundary-fission/fission-report.example.json \
  --pretty
```

Tests:

```bash
python -m unittest tools.test_boundary_fission
```

## `pulse_retire.py`

Manages PulseRetire Queues.

PulseRetire is receipt-driven retirement for speculative machine cognition:

- agents and GPU workflows can compute ahead;
- speculative artifacts remain non-live until a matching FlowPulse receipt arrives;
- matching evidence retires artifacts and mints a causal nonce;
- mismatched evidence squashes artifacts;
- missing receipt metadata leaves artifacts speculative.

Run the demo:

```bash
python tools/pulse_retire.py demo --pretty
```

Regenerate example artifacts:

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

python tools/pulse_retire.py retire \
  --queue examples/pulse-retire/queue.after-enqueue.json \
  --flowpulse examples/pulse-retire/flowpulse.matching.json \
  --out examples/pulse-retire/retirement.retired.example.json \
  --queue-out examples/pulse-retire/queue.after-retire.json \
  --pretty
```

Tests:

```bash
python -m unittest tools.test_pulse_retire
```
