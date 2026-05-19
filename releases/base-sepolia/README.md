# Base Sepolia Release Artifacts

Use this folder for public Base Sepolia release evidence.

Do not commit private keys, RPC URLs, signed transactions, seed phrases, API keys, or deployer secrets.

Expected public artifacts:

- completed release record;
- `RELEASE_EVIDENCE.json` copied from `RELEASE_EVIDENCE.template.json` and filled with public facts;
- source verification URL;
- reader evidence JSON from `tools/read_flowpulse_logs.py`;
- sample decoded `AfterSwapObserved`;
- sample decoded `FlowPulse`;
- public canary text.

Until those artifacts exist, this folder is a staging area, not a live deployment claim.

Check the release evidence gate:

```bash
python tools/verify_release_evidence.py --pretty
```

Current expected state before public receipt evidence exists:

```text
Public Base Sepolia receipt evidence: PENDING
Production verifier infrastructure: NOT_CLAIMED
```

Use `--require-pass` only when a real public Base Sepolia evidence packet is present.
