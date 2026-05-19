# FMM-0 Conformance Matrix

Model: `FMM-0`

Everyone treated agent memory like retrieval. FlowMemory treats it like a memory model.

Safe launch claim:

> FlowMemory defines FMM-0, a receipt-bound memory consistency model for machine histories.

## Anchor

- Boundary: `Uniswap v4 afterSwap`
- Signal: `FlowPulse`
- Proof envelope: `transaction receipt`
- Memory artifact: `FlowPulse`

## Matrix

| Rule | Status | Invariant | Evidence | Litmus |
| --- | --- | --- | --- | --- |
| `FMM-0.R0` Boundary Separation | PASS | Swap execution, FlowPulse emission, and reader-derived receipt metadata are separate objects. | `README.md`<br>`contracts/FlowMemoryAfterSwapHook.sol`<br>`contracts/FlowPulse.sol`<br>`docs/EVENT_MODEL.md` | - |
| `FMM-0.R1` Intentional Emission | PASS | Memory emission requires explicit FlowMemory hookData with rootfieldId and commitment. | `contracts/interfaces/IFlowMemoryHookData.sol`<br>`test/FlowMemoryAfterSwapHook.t.sol` | - |
| `FMM-0.R2` Receipt Mapping | PASS | Receipt-only fields cannot be dereferenced before reader mapping. | `tools/flow_mmu.py`<br>`tools/test_flow_mmu.py`<br>`examples/flow-litmus/cases/FM-LB-001-pre-receipt-deref.json` | `FM-LB-001` |
| `FMM-0.R3` Retirement | PASS | Speculative artifacts cannot become live until a matching FlowPulse receipt retires them. | `tools/pulse_retire.py`<br>`tools/test_pulse_retire.py`<br>`examples/flow-litmus/cases/FM-RT-001-unretired-output.json` | `FM-RT-001` |
| `FMM-0.R4` Quiescence | PASS | Active pre-boundary frames must quiesce, revalidate, fork, or abandon before joining post-boundary state. | `tools/flow_quiesce.py`<br>`tools/test_flow_quiesce.py`<br>`examples/flow-litmus/cases/FM-QS-001-unquiesced-output.json` | `FM-QS-001` |
| `FMM-0.R5` Serialization | PASS | Agent histories must serialize around the FlowPulse receipt boundaries they claim to observe. | `tools/flow_serial.py`<br>`tools/test_flow_serial.py`<br>`examples/flow-litmus/cases/FM-SER-001-retrocausal-claim.json`<br>`examples/flow-litmus/cases/FM-SER-002-rootfield-rollback.json`<br>`examples/flow-litmus/cases/FM-SER-003-split-brain-write.json` | `FM-SER-001`, `FM-SER-002`, `FM-SER-003` |
| `FMM-0.R6` Forbidden Outcomes | PASS | A conforming runtime rejects impossible histories and accepts valid receipt-ordered histories. | `tools/flow_litmus.py`<br>`tools/test_flow_litmus.py`<br>`examples/flow-litmus/litmus.manifest.json`<br>`examples/flow-litmus/cases/FM-OK-001-valid-boundary-history.json` | `FM-LB-001`, `FM-SER-001`, `FM-QS-001`, `FM-RT-001`, `FM-FIS-001`, `FM-SER-002`, `FM-SER-003`, `FM-OK-001` |
| `FMM-0.R7` Public Release Evidence | PENDING | A public Base Sepolia release record attaches receipt-derived txHash/logIndex evidence from a real deployed hook. | `releases/base-sepolia/RELEASE_EVIDENCE.json` | - |

## Result

Local model status: **PASS**.

Pending release evidence: `FMM-0.R7`.

## Non-Claims

- `not_semantic_truth`
- `not_model_correctness`
- `not_production_standard`
- `not_audited_runtime`
- `not_mainnet_proven`
- `not_gpu_acceleration`
- `not_hook_enforced_agent_runtime`

Matrix ID: `sha256:2f4145275b7a88a2d23b08b6d1ac53c5cd2f7c03a1d07d5e720071a0428a4db1`
