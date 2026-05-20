# Base Sepolia Deployments

This folder is for sanitized deployment manifests only.

Do not commit private keys, RPC URLs, API keys, `.env` files, broadcast traces,
or wallet secrets.

Generate a dry-run manifest:

```bash
python tools/base_sepolia_deploy.py dry-run-manifest \
  --output deployments/base-sepolia/deployment-manifest.dry-run.json
```

Validate a manifest:

```bash
python tools/base_sepolia_deploy.py validate \
  --input deployments/base-sepolia/deployment-manifest.dry-run.json
```

Status values:

- `local_only`
- `dry_run`
- `deployed_testnet_unverified`
- `deployed_testnet_verified`
- `blocked_missing_environment`

No file in this directory is a Base mainnet claim.
