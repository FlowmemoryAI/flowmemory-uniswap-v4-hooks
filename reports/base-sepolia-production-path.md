# Base Sepolia Production Path Report

Date: 2026-05-20
Branch: `production/base-sepolia-release-evidence`
Starting commit: `2d1aaa7 Add system architecture receipt runtime`

## Executive Summary

This pass moves the FlowMemory Uniswap v4 hook repo from a strong local artifact toward an operator-grade Base Sepolia production path.

It does not claim a live Base mainnet deployment.
It does not claim custody, wallet authorization, fund protection, escrow, semantic truth, model correctness, GPU acceleration, or a production verifier network.

The boundary remains intact:

```text
FlowMemoryAfterSwapHook emits FlowPulse.
PulseWatch attaches txHash, logIndex, receipt, and finality later.
The transaction is the proof envelope.
The FlowPulse is the memory artifact.
```

## What Is Actually Deployed

Nothing was deployed during this pass.

Reason: no live deployer key, funded deployer, RPC confirmation, source-verification credentials, deployed hook address, or observed Base Sepolia logs were provided for this run.

Status: `BLOCKED`, not faked.

## Testnet-Only Production Path Added

The repo now has a Base Sepolia-only deployment and evidence path:

- Foundry deployment script for Base Sepolia.
- Foundry read-only verification script.
- sanitized deployment manifest generator and validator.
- Base Sepolia chain ID enforcement.
- explicit deployment status enum.
- release evidence packet generator and verifier.
- deterministic release packet hash.
- PulseWatch service operations path.
- public status artifact generator.
- production readiness gate.
- claim-safe docs and non-claims.

## Simulated Or Local-Only

The following remain local or simulated until real Base Sepolia evidence exists:

- dry-run deployment manifest.
- PulseWatch demo input/output.
- Python unit-test fixtures.
- release packet fixture mode.
- readiness checks that intentionally report missing observed evidence as blocked.

Fixture evidence cannot silently become verified evidence.

## Fixture-Only

Fixture mode exists only for deterministic testing and reviewer reproducibility.

Fixture release packets:

- must be explicitly marked as fixture mode;
- cannot be marked `testnet_verified`;
- are rejected if they pretend to be observed public evidence.

## Blocked Until Live Evidence Exists

The following are blocked until an operator performs the live testnet sequence:

- Base Sepolia deployment broadcast.
- deployed hook address.
- source verification URL.
- observed `AfterSwapObserved` logs.
- observed `FlowPulse` logs.
- finalized receipt metadata.
- release evidence packet from observed logs.
- public status page promotion from blocked to packet-ready.

## Non-Claims

The following are explicit non-claims. Do not claim:

- Base mainnet deployment.
- production custody.
- wallet authorization.
- fund protection.
- escrow.
- semantic truth.
- model correctness.
- GPU acceleration.
- production verifier network.
- hook-time `txHash`.
- hook-time `logIndex`.

## Files Added

- `script/DeployBaseSepolia.s.sol`
- `script/VerifyBaseSepolia.s.sol`
- `tools/base_sepolia_deploy.py`
- `tools/release_evidence.py`
- `tools/public_status.py`
- `tools/production_readiness.py`
- `tools/test_base_sepolia_deploy.py`
- `tools/test_release_evidence.py`
- `tools/test_public_status.py`
- `tools/test_production_readiness.py`
- `docs/BASE_SEPOLIA_DEPLOYMENT_RUNBOOK.md`
- `docs/PULSEWATCH_OPERATIONS.md`
- `docs/RELEASE_EVIDENCE.md`
- `docs/PUBLIC_STATUS.md`
- `docs/PRODUCTION_READINESS.md`
- `docs/NON_CLAIMS.md`
- `docs/SLOS.md`
- `docs/INDEX.md`
- `FLOWMEMORY_TECHNICAL_WALKTHROUGH.md`
- `deployments/base-sepolia/README.md`
- `deployments/base-sepolia/.gitignore`
- `release-evidence/base-sepolia/README.md`
- `release-evidence/base-sepolia/.gitignore`
- `public/status/README.md`
- `public/status/base-sepolia.md`
- `ops/README.md`
- `ops/systemd/pulsewatch.service`
- `ops/docker-compose.yml`
- `reports/base-sepolia-production-path.md`

## Files Updated

- `.env.example`
- `.github/workflows/ci.yml`
- `CHANGELOG.md`
- `README.md`
- `tools/README.md`
- `tools/public_claim_gate.py`
- `tools/pulse_watch.py`
- `tools/test_pulse_watch.py`

## Verification Run

Commands run:

```bash
python -m unittest discover -s tools -p "test_*.py"
forge fmt --check
git diff --check
forge build
forge test -vvv
python tools/public_claim_gate.py --pretty
python tools/production_readiness.py --pretty
python tools/mainnet_candidate_gate.py --pretty
python tools/public_status.py --output public/status/base-sepolia.md
python tools/base_sepolia_deploy.py dry-run-manifest --output deployments/base-sepolia/deployment-manifest.dry-run.local.json
python tools/base_sepolia_deploy.py validate --input deployments/base-sepolia/deployment-manifest.dry-run.local.json
python tools/pulse_watch.py demo
```

Results:

- Python tools: `445 tests`, `OK`.
- Foundry build: `Compiler run successful`.
- Foundry tests: `12 passed`, `0 failed`, `0 skipped`.
- Public claim gate: `41 files checked`, `0 unguarded overclaims`.
- Production readiness: `testnet_path_ready_evidence_blocked`.
- Mainnet candidate gate: `mainnetCandidateReady: False`.
- Public status: `blocked_no_release_packet`.
- Base Sepolia dry-run manifest: `PASS`.
- PulseWatch demo: `PASS`.

## Production Readiness State

Current readiness is:

```text
testnet_path_ready_evidence_blocked
```

That is the expected safe state before a live Base Sepolia deployment and observed logs exist.

Passing:

- docs exist;
- public status is testnet-only;
- claim gate passes;
- deployment manifest tooling validates sanitized dry-run output;
- PulseWatch has health, replay, retry, cursor, and idempotency coverage.

Blocked:

- no observed deployment manifest;
- no observed release evidence packet.

## Operator Next Steps

1. Provide a Base Sepolia RPC URL through the environment.
2. Fund a deployment signer on Base Sepolia.
3. Run the deployment dry-run.
4. Broadcast the Base Sepolia deployment.
5. Verify source on the target explorer.
6. Record a sanitized deployment manifest.
7. Run a swap flow that intentionally supplies FlowMemory `hookData`.
8. Run PulseWatch from the chosen block range.
9. Generate an observed release evidence packet.
10. Regenerate public status from the observed packet.
11. Re-run claim, readiness, and CI gates.

## Public Status

Current public status path:

```text
public/status/base-sepolia.md
```

Current status:

```text
blocked_no_release_packet
```

This is intentionally public-safe. It gives reviewers a status page without implying deployment evidence exists.

## Final Launch Boundary

The repo is stronger after this pass because it now distinguishes local readiness from public testnet evidence.

The correct public statement is:

```text
FlowMemory has a Base Sepolia production-like deployment and evidence path ready for operator execution. Live Base Sepolia deployment evidence remains blocked until a real deployment, source verification, observed FlowPulse logs, and release packet exist.
```

Do not say:

```text
FlowMemory is live on Base mainnet or has a production verifier network.
```

That statement is not supported and is blocked by the claim gates.
