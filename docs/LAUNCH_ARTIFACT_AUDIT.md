# Launch Artifact Audit

This audit maps the launch objective to concrete repository artifacts.

Launch focus: FlowMemory's memory-native Uniswap v4 hook primitive.

Core claim:

> FlowMemory introduces the first memory-native Uniswap v4 hook primitive: a verified on-chain emission boundary for FlowPulse memory signals.

Boundary:

The swap transaction is not the memory. The transaction is the proof envelope. The FlowPulse is the memory artifact.

## Success Criteria

| Requirement | Artifact | Evidence |
| --- | --- | --- |
| Public repo explains the category | `README.md` | Opens with the memory-native primitive claim and explains the memory hook category. |
| Hook code preserves the narrow primitive | `contracts/FlowMemoryAfterSwapHook.sol` | PoolManager-gated, `afterSwap` path, required `hookData`, required rootfield, required commitment, zero hook delta. |
| Event schema keeps receipt facts out of the hook | `contracts/FlowPulse.sol`, `docs/EVENT_MODEL.md` | `FlowPulse` has no `txHash`, `transactionIndex`, or `logIndex`; reader attaches those later. |
| Interface surface is clean | `contracts/interfaces/IFlowMemoryHookData.sol` | Hook data struct only; no unused adapter callback surface. |
| Base Sepolia planning facts are public | `docs/BASE_SEPOLIA_PLAN.md` | Chain id, PoolManager, CREATE2 deployer, target hook bits, and release-record requirements. |
| Operator path exists | `docs/BASE_SEPOLIA_OPERATOR_RUNBOOK.md` | Preflight, deployment record, reader evidence, and public canary steps. |
| Reader/verifier model is documented | `docs/READER_VERIFIER_ARCHITECTURE.md` | Reader inputs, output shape, finality states, rejection reasons, and proof-envelope split. |
| Reader proof tooling exists | `tools/read_flowpulse_logs.py` | Reads hook logs, decodes events, fetches receipts, attaches receipt-derived facts, writes JSON. |
| Reader decoder is tested | `tools/test_read_flowpulse_logs.py` | Unit tests cover `FlowPulse`, `AfterSwapObserved`, and invalid zero rootfield/commitment cases. |
| Release artifact staging exists | `releases/base-sepolia/README.md` | Defines where public release record and evidence JSON should live. |
| Public canary language exists | `docs/PUBLIC_CANARY_TEMPLATE.md` | Gives evidence-first post copy without Base mainnet or custody overclaims. |
| Launch checklist exists | `docs/LAUNCH_DAY_CHECKLIST.md` | Separates launch with Base Sepolia evidence from launch as repo/live-prep artifact. |
| Marketing language is controlled | `docs/MARKETING_POSITIONING.md` | Strong category language plus explicit forbidden claims. |
| Frontier R&D artifact shows broader AI-agent value | `docs/FLOW_SERIAL.md`, `tools/flow_serial.py`, `examples/flow-serial/` | Demonstrates receipt-linearizable machine histories without claiming semantic truth, custody, swap control, or live production deployment. |
| Launch demo makes the runtime model executable | `docs/FLOWLITMUS_LAUNCH_DEMO.md`, `tools/flow_litmus.py`, `examples/flow-litmus/` | Runs forbidden-outcome cases that show pre-receipt, stale-state, retirement, quiescence, rollback, and split-brain failures. |
| Forbidden outcomes are explained | `docs/FLOWLITMUS_FORBIDDEN_OUTCOMES.md`, `examples/flow-litmus/flowlitmus-casebook.json`, `tools/render_flowlitmus_casebook.py` | Names each impossible machine history, why FlowPulse matters, and the fault that catches it. |
| FMM-0 memory model is named and mapped | `specs/FMM-0.v0.md`, `docs/FLOWMEMORY_MEMORY_MODEL.md`, `docs/FMM_0_CONFORMANCE_MATRIX.md`, `examples/memory-model/fmm0.manifest.json` | Defines the draft FlowMemory Agent Memory Model and maps each rule to evidence. |
| One-command launch screenshot exists | `docs/LAUNCH_REALITY_CHECK.md`, `tools/launch_reality_check.py`, `examples/launch-reality-check/` | Prints the boundary model, hook invariants, FlowLitmus table, and exact safe public claim. |
| Claim-to-evidence scorecard exists | `docs/MEMORY_CONSISTENCY_CARD.md`, `tools/memory_consistency_card.py`, `examples/memory-consistency-card/` | Frames FlowMemory as a receipt-bound memory consistency model and marks public Base Sepolia evidence pending. |
| FMM-0 Phase Space exists | `docs/FMM_0_PHASE_TABLE.md`, `specs/FMM-0-PhaseTable.v0.md`, `tools/fmm0_phase_table.py`, `examples/fmm0-phase-table/` | Makes machine-state phases executable and catches illegal pre-receipt receipt-field claims. |
| Skeptic claim ledger exists | `docs/SKEPTIC_REVIEW_WALKTHROUGH.md`, `docs/LAUNCH_CLAIM_LEDGER.md`, `tools/reviewer_walkthrough.py`, `examples/reviewer-walkthrough/` | Maps each launch claim to evidence, commands, expected results, status, and explicit non-claims. |
| Public release evidence gate exists | `tools/verify_release_evidence.py`, `releases/base-sepolia/RELEASE_EVIDENCE.template.json`, `releases/base-sepolia/expected-pending-output.txt` | Keeps public Base Sepolia receipt evidence pending until a real packet validates. |
| CI enforces required launch artifacts | `.github/workflows/ci.yml` | Required-file check includes reader, launch docs, and release staging folder. |

## Verification Commands

Run before public sharing:

```bash
forge fmt --check
forge build
forge test -vvv
python tools/read_flowpulse_logs.py --help
python -m unittest tools.test_read_flowpulse_logs
python -m unittest tools.test_flow_serial
python tools/flow_serial.py demo --pretty
python -m unittest tools.test_flow_litmus
python tools/flow_litmus.py run --suite examples/flow-litmus/litmus.manifest.json
python -m unittest tools.test_fmm0_manifest
python tools/render_fmm0_matrix.py --check
python -m unittest tools.test_launch_reality_check
python tools/launch_reality_check.py --pretty
python -m unittest tools.test_memory_consistency_card
python tools/memory_consistency_card.py --pretty
python -m unittest tools.test_reviewer_walkthrough
python tools/reviewer_walkthrough.py --pretty
python -m unittest tools.test_verify_release_evidence
python tools/verify_release_evidence.py --pretty
python -m unittest tools.test_flowlitmus_casebook
python tools/render_flowlitmus_casebook.py --check
git diff --check
```

GitHub Actions should show both jobs green:

- `Foundry`;
- `Repository hygiene`.

## What Is Ready Now

- Public category positioning.
- Public hook code and tests.
- Base Sepolia planning docs.
- Release record template.
- Operator runbook.
- Reader/verifier architecture.
- Dependency-light reader utility.
- Reader decoder tests.
- Public canary template.
- Launch-day checklist.
- FlowSerial R&D artifact for receipt-linearizable machine cognition.
- FlowLitmus launch demo for executable forbidden outcomes.
- FlowLitmus forbidden-outcomes casebook.
- FMM-0 draft memory model and conformance matrix.
- FlowMemory Reality Check for a screenshot-ready launch command.
- Memory Consistency Card for claim-to-evidence launch positioning.
- FMM-0 Skeptic Walkthrough for claim-to-command reviewability.
- Pending-safe Base Sepolia release evidence verifier.

## What Still Requires Live Evidence

These are not repository-writing tasks. They require deployment and public chain data:

- mined final hook salt for the exact deployable init code;
- deployed Base Sepolia hook address;
- source verification URL;
- deployment transaction hash;
- at least one hook-triggered `AfterSwapObserved`;
- at least one hook-triggered `FlowPulse`;
- reader-generated evidence JSON with receipt-derived `txHash` and `logIndex`;
- filled Base Sepolia release record.

## Claims Allowed Before Live Evidence

- First public FlowMemory hook surface.
- Memory-native Uniswap v4 hook primitive.
- Verified on-chain emission boundary design.
- CI-tested public implementation.
- Base Sepolia release path.
- Live-prep package for memory-native DeFi infrastructure.

## Claims Reserved For After Live Evidence

- Verified Base Sepolia hook deployment.
- Observed FlowPulse logs.
- Reader-derived receipt evidence.
- Public Base Sepolia canary.

## Claims Not Allowed From This Repo Alone

- Production Base mainnet hook is live.
- Audited custody infrastructure.
- The hook protects funds.
- The hook controls swaps.
- The hook knows `txHash` or `logIndex` during execution.
- Every ordinary Uniswap transaction automatically becomes FlowMemory.
- The swap transaction itself is memory.
