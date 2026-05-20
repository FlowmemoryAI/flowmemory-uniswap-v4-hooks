# Production Readiness

This repository now has a production-like Base Sepolia path.

It is not a production verifier network and it is not a Base mainnet deployment
claim.

Run:

```bash
python tools/production_readiness.py --pretty
```

The readiness gate checks:

- deployment runbook exists;
- PulseWatch operations docs exist;
- release evidence docs exist;
- public status docs exist;
- SLO docs exist;
- non-claims docs exist;
- deployment manifest is sanitized when present;
- release packet verifies when present;
- public status is testnet-only;
- public claim gate passes.

`testnet_path_ready_evidence_blocked` is acceptable before live environment
variables, deployment funding, or observed Base Sepolia FlowPulse logs exist.

`fail` means the repo has an unsafe or inconsistent production-readiness claim.
