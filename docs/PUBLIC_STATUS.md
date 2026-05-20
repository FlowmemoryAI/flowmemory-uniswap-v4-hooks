# Public Status

The public status page is a generated, claim-safe status artifact.

Generate:

```bash
python tools/public_status.py \
  --packet release-evidence/base-sepolia/RELEASE_PACKET.json \
  --output public/status/base-sepolia.md
```

If no release packet exists, the page remains blocked and testnet-only.

The page shows:

- testnet-only status;
- hook address;
- chain id;
- release packet hash;
- observed FlowPulse count;
- latest observed block;
- finality distribution;
- one proof-envelope example when available;
- non-claims.

The page must not claim Base mainnet, custody, wallet authorization, fund
protection, semantic truth, model correctness, GPU acceleration, or a
production verifier network.
