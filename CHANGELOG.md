# Changelog

## 0.1.3 Base Sepolia Production Path - 2026-05-20

Added the production-like Base Sepolia deployment and evidence path.

What changed:

- Added guarded Foundry scripts for Base Sepolia deployment/read-only
  verification checks.
- Added sanitized deployment manifest tooling that refuses non-Base-Sepolia
  chain ids and redacts secret-like fields.
- Added deterministic release evidence packet generation from observed
  FlowPulse/AfterSwap reader output.
- Added PulseWatch health and replay commands, plus retry/backoff for live
  reader mode.
- Added public Base Sepolia status generation.
- Added production readiness gate and Base Sepolia operator runbooks.
- Added systemd and Docker Compose PulseWatch operation templates.

Boundary:

- This is a Base Sepolia production-like path, not a Base mainnet claim.
- Missing RPC, wallet funding, source verification, or observed FlowPulse logs
  remain blocked instead of being faked.

## 0.1.2 System Architecture and Receipt Runtime - 2026-05-20

Added the full-system architecture package and the first deterministic receipt
runtime MVP.

What changed:

- Added `docs/SYSTEM_ARCHITECTURE.md` as the end-to-end architecture for
  boundary emission, PulseWatch, evidence stores, FMM-0, agent commerce,
  compute reuse, product APIs, and production operations.
- Added `specs/FlowMemorySystemArchitecture.v0.md` and
  `examples/system-architecture/architecture-manifest.json`.
- Added `tools/system_architecture_review.py` and tests to make the
  architecture packet executable.
- Added `docs/RECEIPT_RUNTIME_ARCHITECTURE.md` and `specs/ReceiptRuntime.v0.md`.
- Added `tools/receipt_runtime_demo.py` and tests for the loop:
  `PolicyCard -> PulsePermit -> ActionPulse -> FlowPulseLink -> OutcomePulse -> PulsePass`.
- Wired system architecture and receipt runtime into README, CI, public claim
  gate, tools docs, and release transcript.

Core architecture line:

```text
Memory should gate the action before execution and settle the outcome after receipt evidence.
```

Boundary:

- Receipt Runtime does not authorize wallets, custody funds, or escrow payments.
- Receipt Runtime does not settle live payments.
- Receipt Runtime does not prove semantic truth or model correctness.
- Receipt Runtime does not claim live Base mainnet deployment.

## 0.1.1 PulseWatch 24/7 Reader - 2026-05-20

Added PulseWatch as the always-on reader/verifier layer for FlowPulse memory.

Key clarification:

```text
The hook is transaction-triggered.
PulseWatch is continuous.
```

What changed:

- Added `tools/pulse_watch.py` with deterministic demo, live polling mode,
  cursor state, duplicate skipping, append-only memory records, and validation.
- Added `tools/test_pulse_watch.py` with coverage for demo output, duplicate
  protection, proof-envelope memory records, CLI verification, and hook-time
  receipt metadata smuggling.
- Added `docs/PULSEWATCH_24_7_READER.md` and `specs/PulseWatch.v0.md`.
- Added `examples/pulse-watch/` with expected output.
- Wired PulseWatch into `docs/READER_VERIFIER_ARCHITECTURE.md`,
  `docs/INTEGRATION_BLUEPRINT.md`, README, CI, and release transcript.

Verified locally before this entry:

- `python -m unittest discover -s tools -p "test_*.py"`: 407 tests passed.
- `python tools/pulse_watch.py demo`: passed.
- `python tools/flowmemory_release_transcript.py --pretty`: passed and includes
  `PulseWatch 24/7 Reader`.
- `python tools/public_claim_gate.py --pretty`: 0 unguarded overclaims.
- `forge fmt --check`: passed.
- `forge build`: passed.
- `forge test -vvv`: 12 tests passed.

Boundary:

- PulseWatch does not make hooks run without transactions.
- PulseWatch does not claim production verifier readiness.
- PulseWatch does not claim live deployment, custody, fund protection, or
  production operations.

## 0.1.0 Launch Prep - 2026-05-19

FlowMemory Uniswap v4 Hooks is public launch prep for the first memory-native
FlowMemory hook primitive.

Core public claim:

```text
The swap is not the memory.
The transaction is the proof envelope.
The FlowPulse is the memory artifact.
```

What this release-prep surface includes:

- `FlowMemoryAfterSwapHook`: a narrow Uniswap v4 `afterSwap` memory-emission boundary.
- `FlowPulse`: the memory signal emitted from the hook boundary.
- FMM-0: a receipt-bound memory consistency model for machine histories.
- FlowLitmus: executable forbidden outcomes for impossible machine histories.
- FMM-0 witness, counterexample, closure, boundary, and forbidden-core harnesses.
- Memory-Native Agent Commerce Stack doc for the agent-commerce architecture in one public artifact.
- Agent Commerce Skeptic Responses doc for direct reviewer objections and launch-safe answers.
- Launch hardening docs for local conformance boundaries, agent-commerce invariants, and reviewer FAQ.
- Agent Commerce Differential Harness for showing ordinary rails accept while FlowMemory rejects impossible histories.
- FlowPulse Boundary ABI gate for hook-time and receipt-time schema separation.
- Cache Lineage Gate, Compute Reuse Router, and Compute Reuse Consistency for proof-backed AI/GPU workflow reuse discipline.
- Compute ChargeLine for matching AI/GPU compute payment to the memory-consistent compute route.
- DischargeLine Harness for receipt-bound obligation completion.
- SpendLine Harness for memory-linearizable autonomous agent spend histories.
- DuplexLine Harness for co-serializable buyer/seller agent exchange histories.
- Agent Commerce Conservation Lab for obligation conservation across spend, work, compute, refusal, and memory state.
- Obligation Membrane for no-laundering checks across subagents, compute providers, aggregate work, refusal, and payment closure.
- Public Claim Gate, Release Transcript, Reviewer Quickstart, Skeptic Walkthrough, and Launch Reality Check.
- Public Technical Report: a publication-style Markdown source and PDF for reviewers, journals, and public launch readers.
- External Review Packet: a simple plus technical review handoff, with PDF, for outside security and architecture review.
- Repo Boundary and Future Runtime Architecture doc for keeping this launch repo
  centered on the Uniswap v4 `afterSwap` FlowPulse primitive while deferring
  FlowCompiler, FlowKernel, MCP adapters, and coding-agent conformance to
  future packages.

Verified locally before this entry:

- `python -m unittest discover -s tools -p 'test_*.py'`: 399 tests passed.
- `forge fmt --check`: passed.
- `forge build`: passed.
- `forge test -vvv`: 12 tests passed.
- `python tools/public_claim_gate.py --pretty`: 24 files checked, 0 unguarded overclaims.
- GitHub Actions `CI`: passing on `main`.

Public evidence status:

- Local FMM-0 consistency surface: `PASS`.
- Public Base Sepolia receipt evidence: `PENDING`.
- Production verifier infrastructure: `NOT_CLAIMED`.

Do not claim from this repo alone:

- live Base mainnet deployment;
- audited custody or fund-safety guarantees;
- swap-economic control, routing, fee control, or custom accounting;
- hook-time `txHash`, `transactionIndex`, or `logIndex`;
- semantic truth or model correctness;
- GPU hardware speedup;
- production verifier readiness.
