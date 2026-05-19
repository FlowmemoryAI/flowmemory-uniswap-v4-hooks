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
| `FM-C09` FMM-0 Phase Space catches illegal machine-state phase jumps. | PASS | `specs/FMM-0-PhaseTable.v0.md`<br>`docs/FMM_0_PHASE_TABLE.md`<br>`tools/fmm0_phase_table.py`<br>`examples/fmm0-phase-table/phase-table.json` | `python tools/fmm0_phase_table.py demo --pretty`<br>`python -m unittest tools.test_fmm0_phase_table` | The phase table catches pre-receipt txHash/logIndex smuggling, local-only to FMM-0 live jumps, and reader-derived to FMM-0 live jumps without consistency checks. | `not_semantic_truth`, `not_model_correctness`, `not_production_verifier_infrastructure` |
| `FM-C12` FMM-0 Counterexample Forge catches generated impossible histories. | PASS | `specs/FMM-0-CounterexampleForge.v0.md`<br>`docs/FMM_0_COUNTEREXAMPLE_FORGE.md`<br>`tools/fmm0_counterexample_forge.py`<br>`examples/fmm0-counterexample-forge/expected-output.txt` | `python tools/fmm0_counterexample_forge.py demo --pretty`<br>`python -m unittest tools.test_fmm0_counterexample_forge` | The counterexample forge generates 12 impossible histories and FMM-0 catches 12/12. | `not_semantic_truth`, `not_model_correctness`, `not_production_verifier_infrastructure` |
| `FM-C13` FMM-0 Closure Lab preserves valid memory algebra and rejects invalid composition. | PASS | `specs/FMM-0-ClosureLab.v0.md`<br>`docs/FMM_0_CLOSURE_LAB.md`<br>`tools/fmm0_closure_lab.py`<br>`examples/fmm0-closure-lab/expected-output.txt` | `python tools/fmm0_closure_lab.py demo --pretty`<br>`python -m unittest tools.test_fmm0_closure_lab` | The closure lab checks 8 closure laws, preserves 4/4 valid closures, rejects 4/4 invalid closures, and reports 0 escaped. | `not_semantic_truth`, `not_model_correctness`, `not_production_verifier_infrastructure` |
| `FM-C14` FMM-0 Boundary Bisimulation catches cross-layer FlowPulse projection drift. | PASS | `specs/FMM-0-BoundaryBisimulation.v0.md`<br>`docs/FMM_0_BOUNDARY_BISIMULATION.md`<br>`tools/fmm0_boundary_bisim.py`<br>`examples/fmm0-boundary-bisimulation/expected-output.txt` | `python tools/fmm0_boundary_bisim.py demo --pretty`<br>`python -m unittest tools.test_fmm0_boundary_bisim` | Boundary Bisimulation checks 8 projections, preserves 4/4 valid bisimulations, rejects 4/4 drift cases, and reports 0 escaped. | `not_semantic_truth`, `not_model_correctness`, `not_production_verifier_infrastructure` |
| `FM-C15` FMM-0 Forbidden Core Extractor shrinks impossible histories to one-minimal cores. | PASS | `specs/FMM-0-ForbiddenCore.v0.md`<br>`docs/FMM_0_FORBIDDEN_CORE_EXTRACTOR.md`<br>`tools/fmm0_forbidden_core.py`<br>`examples/fmm0-forbidden-core/expected-output.txt` | `python tools/fmm0_forbidden_core.py demo --pretty`<br>`python -m unittest tools.test_fmm0_forbidden_core` | Forbidden Core extracts 10/10 one-minimal cores and reports 0 escaped faults. | `not_formal_verification`, `not_semantic_truth`, `not_model_correctness`, `not_production_verifier_infrastructure` |
| `FM-C16` FMM-0 Witness Pack bundles local conformance evidence into a reproducible packet. | PASS | `specs/FMM-0-WitnessPack.v0.md`<br>`docs/FMM_0_WITNESS_PACK.md`<br>`tools/fmm0_witness_pack.py`<br>`examples/fmm0-witness-pack/expected-output.txt` | `python tools/fmm0_witness_pack.py demo --pretty`<br>`python -m unittest tools.test_fmm0_witness_pack` | Witness Pack reports 8/8 local conformance layers, PENDING public Base Sepolia evidence, and 0 escaped faults. | `not_production_verifier_infrastructure`, `not_semantic_truth`, `not_model_correctness`, `not_live_base_mainnet` |
| `FM-C17` FlowPulse Boundary ABI matches FMM-0 hook-time and receipt-time assumptions. | PASS | `specs/FlowPulse-BoundaryABI.v0.md`<br>`docs/FLOWPULSE_BOUNDARY_ABI.md`<br>`tools/flowpulse_boundary_abi.py`<br>`examples/flowpulse-boundary-abi/expected-output.txt` | `python tools/flowpulse_boundary_abi.py check --pretty`<br>`python -m unittest tools.test_flowpulse_boundary_abi` | Boundary ABI reports 9/9 checks passed and 0 receipt-only fields exposed. | `not_production_verifier_infrastructure`, `not_hook_time_receipt_metadata`, `not_semantic_truth`, `not_model_correctness` |
| `FM-C18` Compute Reuse Router turns proof-backed compute memory into a scheduler decision. | PASS | `specs/ComputeReuseRouter.v0.md`<br>`docs/COMPUTE_REUSE_ROUTER.md`<br>`tools/compute_reuse_router.py`<br>`examples/compute-reuse-router/expected-output.txt` | `python tools/compute_reuse_router.py demo --pretty`<br>`python -m unittest tools.test_compute_reuse_router` | Compute Reuse Router reuses 1 safe prior compute artifact and rejects 4/4 unsafe reuse attempts. | `not_gpu_acceleration`, `not_cuda_optimizer`, `not_kv_cache_storage`, `not_model_correctness` |
| `FM-C19` FlowMemory Release Transcript gives one offline object for passed, pending, and non-claimed launch state. | PASS | `specs/FlowMemoryReleaseTranscript.v0.md`<br>`docs/FLOWMEMORY_RELEASE_TRANSCRIPT.md`<br>`tools/flowmemory_release_transcript.py`<br>`examples/release-transcript/expected-output.txt` | `python tools/flowmemory_release_transcript.py --pretty`<br>`python -m unittest tools.test_flowmemory_release_transcript` | Release Transcript reports local PASS, public receipt evidence PENDING, and explicit non-claims. | `not_live_base_mainnet`, `not_audited_custody`, `not_fund_protection`, `not_production_verifier_infrastructure` |
| `FM-C10` Public Base Sepolia receipt evidence is pending. | PENDING | `releases/base-sepolia/RELEASE_EVIDENCE.json` | `python tools/verify_release_evidence.py --pretty` | A future RELEASE_EVIDENCE.json packet contains observed FlowPulse logs and reader-derived txHash/logIndex. | `not_live_base_mainnet`, `not_verified_deployment_yet` |
| `FM-C11` Production verifier infrastructure is not claimed. | NOT_CLAIMED | `docs/LAUNCH_REALITY_CHECK.md`<br>`docs/PUBLIC_LAUNCH_COPY.md`<br>`docs/MEMORY_CONSISTENCY_CARD.md` | - | Launch copy keeps production verifier infrastructure out of the claim surface. | `not_production_verifier_infrastructure`, `not_audited_runtime`, `not_mainnet_proven` |

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

Walkthrough ID: `sha256:17d64890adfbb3b2f92ddace7c94cd4c1f6c65b75fec7cee7dc11ecb20cab768`
