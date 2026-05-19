# FlowLitmus Examples

FlowLitmus is the executable runtime consistency suite for FlowMemory.

It runs named forbidden outcomes against the local R&D tools and checks whether
the runtime model can distinguish impossible FlowPulse histories from live
ones.

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

Explain one case:

```bash
python tools/flow_litmus.py explain \
  --case examples/flow-litmus/cases/FM-SER-001-retrocausal-claim.json
```

Expected terminal story:

```text
FlowLitmus Runtime Consistency Suite

FM-LB-001   pre-receipt txHash read              PASS  forbidden_pre_receipt_read
FM-SER-001  retrocausal receipt claim            PASS  retrocausal_receipt_claim
FM-QS-001   unquiesced post-boundary output      PASS  QuiescenceViolation
FM-RT-001   speculative output escaped           PASS  RetirementViolation
FM-FIS-001  stale output survived boundary       PASS  BoundaryFissionViolation
FM-SER-002  rootfield rollback                   PASS  rootfield_rollback
FM-SER-003  split-brain canonical write          PASS  split_brain_write
FM-OK-001   valid boundary history               PASS  Serializable

8/8 passed
```

FlowLitmus does not prove semantic truth, model correctness, GPU execution,
custody, fund safety, production readiness, or live mainnet deployment. It is a
local R&D conformance suite for FlowPulse receipt-boundary rules.
