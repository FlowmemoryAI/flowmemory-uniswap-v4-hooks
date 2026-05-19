# FMM-0 Skeptic Walkthrough

This document is a 10-minute review path for FlowMemory's public launch repo.

The goal is not to ask reviewers to believe the category language. The goal is to show exactly which claims are supported by local code, tests, specs, and examples, and exactly which claims are not being made.

## Core Boundary Model

- the swap is not the memory;
- the transaction is the proof envelope;
- the FlowPulse is the memory artifact;
- the hook does not know txHash/logIndex during execution;
- reader/verifier attaches receipt metadata later;

## Verdict

- Local FMM-0 consistency surface: **PASS**
- FlowLitmus forbidden outcomes: **PASS**
- Public Base Sepolia receipt evidence: **PENDING**
- Production verifier infrastructure: **NOT_CLAIMED**

## Claim Ledger

| Claim | Status | Evidence | Commands | Expected | Non-claims |
| --- | --- | --- | --- | --- | --- |
| `FM-C01` Hook emits FlowPulse at the Uniswap v4 afterSwap boundary. | PASS | `contracts/FlowMemoryAfterSwapHook.sol`<br>`contracts/FlowPulse.sol`<br>`test/FlowMemoryAfterSwapHook.t.sol` | `forge test --match-test testAfterSwapHookEmitsFlowPulseAndReturnsZeroHookDelta -vvv` | FlowPulse is emitted and the hook returns the afterSwap selector with zero hook delta. | `not_swap_memory`, `not_custody`, `not_swap_control` |
| `FM-C02` Hook returns zero hook delta. | PASS | `contracts/FlowMemoryAfterSwapHook.sol`<br>`test/FlowMemoryAfterSwapHook.t.sol` | `forge test --match-test testAfterSwapHookEmitsFlowPulseAndReturnsZeroHookDelta -vvv` | No custom accounting delta is returned. | `not_custom_accounting`, `not_balance_change_engine` |
| `FM-C03` Hook has no custody, fee, routing, or custom-accounting path. | PASS | `contracts/FlowMemoryAfterSwapHook.sol`<br>`contracts/FlowMemoryHookPlanner.sol`<br>`docs/SECURITY_MODEL.md` | `forge test --match-test testPlannerRejectsCustomAccountingAndExtraHookFlags -vvv` | Planner rejects custom-accounting and extra hook flags. | `not_custody`, `not_fee_engine`, `not_routing_engine`, `not_fund_protection` |
| `FM-C04` Hook does not know txHash/logIndex during execution. | PASS | `contracts/FlowPulse.sol`<br>`docs/EVENT_MODEL.md`<br>`docs/FLOWMEMORY_RUNTIME_MODEL.md`<br>`test/FlowMemoryAfterSwapHook.t.sol` | `forge test --match-test testHookEventSchemasExcludeTxHashAndLogIndexAssumptions -vvv` | FlowPulse schema excludes txHash, transactionIndex, and logIndex. | `not_txhash_at_hook_time`, `not_logindex_at_hook_time` |
| `FM-C05` Reader/verifier attaches receipt metadata later. | PASS | `tools/read_flowpulse_logs.py`<br>`tools/test_read_flowpulse_logs.py`<br>`docs/READER_VERIFIER_ARCHITECTURE.md` | `python -m unittest tools.test_read_flowpulse_logs` | Reader output separates hook log payload from txHash/logIndex receipt facts. | `not_hook_time_receipt_metadata`, `not_semantic_truth` |
| `FM-C06` FMM-0 defines legal and impossible machine histories around FlowPulse receipt boundaries. | PASS | `specs/FMM-0.v0.md`<br>`docs/FLOWMEMORY_MEMORY_MODEL.md`<br>`examples/memory-model/fmm0.manifest.json`<br>`docs/FMM_0_CONFORMANCE_MATRIX.md` | `python tools/render_fmm0_matrix.py --check` | FMM-0 matrix reports local model status PASS and public release evidence PENDING. | `not_production_standard`, `not_production_verifier_infrastructure` |
| `FM-C07` FlowSerial catches impossible schedules. | PASS | `tools/flow_serial.py`<br>`tools/test_flow_serial.py`<br>`examples/flow-serial/` | `python -m unittest tools.test_flow_serial` | Retrocausal receipt claims, rollback, and split-brain writes fault. | `not_semantic_truth`, `not_model_correctness` |
| `FM-C08` FlowLitmus makes forbidden outcomes executable. | PASS | `tools/flow_litmus.py`<br>`tools/test_flow_litmus.py`<br>`examples/flow-litmus/litmus.manifest.json` | `python tools/flow_litmus.py run --suite examples/flow-litmus/litmus.manifest.json` | FlowLitmus reports 8/8 passed. | `not_ai_memory_verifier_network`, `not_model_correctness` |
| `FM-C09` Public Base Sepolia receipt evidence is pending. | PENDING | `releases/base-sepolia/RELEASE_EVIDENCE.json` | `python tools/verify_release_evidence.py --pretty` | A future RELEASE_EVIDENCE.json packet contains observed FlowPulse logs and reader-derived txHash/logIndex. | `not_live_base_mainnet`, `not_verified_deployment_yet` |
| `FM-C10` Production verifier infrastructure is not claimed. | NOT_CLAIMED | `docs/LAUNCH_REALITY_CHECK.md`<br>`docs/PUBLIC_LAUNCH_COPY.md`<br>`docs/MEMORY_CONSISTENCY_CARD.md` | - | Launch copy keeps production verifier infrastructure out of the claim surface. | `not_production_verifier_infrastructure`, `not_audited_runtime`, `not_mainnet_proven` |

## Launch-Safe Wording

> FlowMemory defines FMM-0, a receipt-bound memory consistency model for machine histories.

## Do Not Claim

- semantic truth;
- model correctness;
- fund protection;
- custody;
- GPU acceleration;
- production verifier infrastructure;
- live Base mainnet deployment.

Walkthrough ID: `sha256:caac38b83557d251de80f74151fd87f124baae5978c8a40e76e2fff7c749198b`
