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

## `flow_mmu.py`

Maps virtual FlowPulse pointers into read-only receipt pages.

FlowMMU is receipt-backed virtual memory for agents:

- an agent can allocate a `PulsePointer` before receipt metadata exists;
- virtual fields like `rootfieldId` and `commitment` can be read before mapping;
- receipt-only fields like `txHash` and `logIndex` throw `ReceiptPageFault` before mapping;
- matching FlowPulse evidence maps a read-only `ReceiptPage`;
- mismatched evidence produces an address-mismatch fault.

Run the demo:

```bash
python tools/flow_mmu.py demo --pretty
```

Regenerate example artifacts:

```bash
python tools/flow_mmu.py init \
  --agent-id demo-agent \
  --rootfield-id 0x1111111111111111111111111111111111111111111111111111111111111111 \
  --out examples/flow-mmu/page-table.initial.json \
  --pretty

python tools/flow_mmu.py alloc \
  --table examples/flow-mmu/page-table.initial.json \
  --pointer examples/flow-mmu/pulse-pointer.request.json \
  --out examples/flow-mmu/page-table.with-pointer.json \
  --pretty
```

Tests:

```bash
python -m unittest tools.test_flow_mmu
```

## `flow_quiesce.py`

Builds receipt-triggered quiescence epochs for agent runtimes.

FlowQuiesce gives agents a grace period for reality:

- a FlowPulse receipt advances a rootfield epoch;
- active frames that read that rootfield are required to quiesce;
- unrelated frames are unaffected;
- pending outputs stay unsafe until required frames acknowledge a safe point;
- a quiescence certificate closes the grace period.

Run the demo:

```bash
python tools/flow_quiesce.py demo --pretty
```

Tests:

```bash
python -m unittest tools.test_flow_quiesce
```

## `flow_serial.py`

Compiles machine histories into serial schedules or typed impossibility faults.

FlowSerial gives agents linearizability against reality:

- a successful FlowPulse receipt boundary becomes a public ordering anchor;
- post-boundary events can cite reader-attached receipt facts;
- pre-boundary events cannot claim `txHash`, `logIndex`, or other receipt-only facts;
- rootfield heads cannot roll backward after receipt-bound advancement;
- exclusive machine-state writers cannot claim incompatible FlowPulse heads.

Run the demo:

```bash
python tools/flow_serial.py demo --pretty
```

Regenerate example artifacts:

```bash
python tools/flow_serial.py certify \
  --history examples/flow-serial/history.valid.json \
  --out examples/flow-serial/certificate.valid.json \
  --pretty

python tools/flow_serial.py certify \
  --history examples/flow-serial/history.retrocausal.json \
  --out examples/flow-serial/fault.retrocausal.json \
  --pretty
```

Tests:

```bash
python -m unittest tools.test_flow_serial
```

## `flow_litmus.py`

Runs the FlowLitmus runtime consistency suite.

FlowLitmus is a conformance suite for reality:

- pre-receipt `txHash` reads must fault;
- retrocausal receipt claims must fault;
- unquiesced post-boundary outputs must stay unsafe;
- unretired speculative outputs must not become live;
- stale memory must not survive boundary fission as raw post-boundary context;
- rootfield rollback and split-brain canonical writes must fault;
- valid receipt-ordered histories must serialize.

Run the suite:

```bash
python tools/flow_litmus.py run \
  --suite examples/flow-litmus/litmus.manifest.json
```

Machine-readable output:

```bash
python tools/flow_litmus.py run \
  --suite examples/flow-litmus/litmus.manifest.json \
  --json \
  --pretty \
  --out examples/flow-litmus/results.latest.json
```

Tests:

```bash
python -m unittest tools.test_flow_litmus
```

## `launch_reality_check.py`

Runs the screenshot-ready launch harness.

The Reality Check prints:

- the boundary model;
- the hook invariant surface;
- required launch artifacts;
- the FlowLitmus forbidden-outcome table;
- the safe public launch claim and non-claims.

Run:

```bash
python tools/launch_reality_check.py --pretty
```

Write the screenshot text:

```bash
python tools/launch_reality_check.py --pretty \
  --write examples/launch-reality-check/latest-output.txt
```

Tests:

```bash
python -m unittest tools.test_launch_reality_check
```

## `memory_consistency_card.py`

Runs the launch-facing claim-to-evidence scorecard.

The card frames FlowMemory as FMM-0, the FlowMemory Agent Memory Model:

- the Uniswap v4 `afterSwap` boundary anchors the signal;
- the FlowPulse is the memory artifact;
- receipt metadata is reader-derived;
- FlowSerial gives receipt-linearizability;
- FlowLitmus makes impossible histories executable;
- public Base Sepolia receipt evidence remains pending until the release record is filled.

Run:

```bash
python tools/memory_consistency_card.py --pretty
```

Write the screenshot text:

```bash
python tools/memory_consistency_card.py --pretty \
  --write examples/memory-consistency-card/latest-output.txt
```

Tests:

```bash
python -m unittest tools.test_memory_consistency_card
```

## `render_fmm0_matrix.py`

Renders the FMM-0 conformance matrix from `examples/memory-model/fmm0.manifest.json`.

FMM-0 is the draft launch model:

```text
Everyone treated agent memory like retrieval. FlowMemory treats it like a memory model.
```

Generate the matrix:

```bash
python tools/render_fmm0_matrix.py \
  --manifest examples/memory-model/fmm0.manifest.json \
  --out docs/FMM_0_CONFORMANCE_MATRIX.md
```

Check local evidence paths while allowing public Base Sepolia release evidence to remain pending:

```bash
python tools/render_fmm0_matrix.py --check
```

Tests:

```bash
python -m unittest tools.test_fmm0_manifest
```

## `reviewer_walkthrough.py`

Renders the FMM-0 Skeptic Walkthrough from `examples/reviewer-walkthrough/fmm0-claim-ledger.json`.

This is the launch credibility layer:

```text
Every launch claim has a command, and every overclaim has a red line.
```

Run:

```bash
python tools/reviewer_walkthrough.py --pretty
```

Write the screenshot text:

```bash
python tools/reviewer_walkthrough.py --pretty \
  --write examples/reviewer-walkthrough/expected-output.txt
```

Regenerate the markdown walkthrough:

```bash
python tools/reviewer_walkthrough.py \
  --markdown docs/SKEPTIC_REVIEW_WALKTHROUGH.md
```

Tests:

```bash
python -m unittest tools.test_reviewer_walkthrough
```

## `verify_release_evidence.py`

Verifies the Base Sepolia release evidence packet.

This gate is pending-safe: if `releases/base-sepolia/RELEASE_EVIDENCE.json` is
missing, it prints `PENDING` instead of fabricating a public receipt claim.

Run:

```bash
python tools/verify_release_evidence.py --pretty
```

Require a real public receipt packet:

```bash
python tools/verify_release_evidence.py --require-pass
```

Tests:

```bash
python -m unittest tools.test_verify_release_evidence
```
