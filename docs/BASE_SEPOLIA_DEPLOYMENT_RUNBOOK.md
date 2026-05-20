# Base Sepolia Deployment Runbook

This runbook is Base Sepolia only.

It does not claim Base mainnet deployment, custody, wallet authorization, fund
protection, escrow, semantic truth, model correctness, GPU acceleration, or a
production verifier network.

## Prerequisites

- Foundry installed.
- A Base Sepolia RPC endpoint.
- A funded Base Sepolia deployer wallet controlled outside this repository.
- No private keys or RPC URLs committed to git.

## Environment

Use local shell environment variables or an untracked `.env` file:

```bash
BASE_SEPOLIA_RPC_URL=
BASE_SEPOLIA_DEPLOYER_ADDRESS=
BASE_SEPOLIA_POOL_MANAGER=0x05E73354cFDd6745C338b50BcFDfA3Aa6fA03408
FLOWMEMORY_HOOK_ADDRESS=
FLOWMEMORY_FROM_BLOCK=
FLOWMEMORY_FINALITY_CONFIRMATIONS=20
```

Private keys stay outside committed files. If an operator uses a private key,
it must be injected only at command runtime.

## Preflight

```bash
forge build
forge test -vvv
python tools/base_sepolia_deploy.py check-chain --rpc-url "$BASE_SEPOLIA_RPC_URL"
python tools/mainnet_candidate_gate.py --pretty
```

The mainnet candidate gate is expected to remain blocked until independent
mainnet evidence exists.

## Dry-Run Manifest

```bash
python tools/base_sepolia_deploy.py dry-run-manifest \
  --output deployments/base-sepolia/deployment-manifest.dry-run.json

python tools/base_sepolia_deploy.py validate \
  --input deployments/base-sepolia/deployment-manifest.dry-run.json
```

The manifest is sanitized. It must not contain private keys, RPC URLs, API
tokens, or `.env` contents.

## Deployment

The hook address must satisfy Uniswap v4 hook permission bits. A normal CREATE
deployment may fail that requirement. Use the planner and CREATE2 path before
publishing any deployment manifest.

Read-only script dry run:

```bash
forge script script/DeployBaseSepolia.s.sol:DeployBaseSepolia \
  --sig "run(address)" "$BASE_SEPOLIA_POOL_MANAGER" \
  --rpc-url "$BASE_SEPOLIA_RPC_URL"
```

Broadcast only after the operator has confirmed the planned address, funding,
and CREATE2 path:

```bash
forge script script/DeployBaseSepolia.s.sol:DeployBaseSepolia \
  --sig "run(address)" "$BASE_SEPOLIA_POOL_MANAGER" \
  --rpc-url "$BASE_SEPOLIA_RPC_URL" \
  --broadcast
```

If the script refuses the address because the afterSwap-only flag is missing,
the correct status is `BLOCKED`, not deployed.

## Source Verification

After deployment, record the explorer verification status in the sanitized
deployment manifest:

- `deployed_testnet_unverified`
- `deployed_testnet_verified`

Do not upgrade status without an explorer/source verification record.

## After Deployment

1. Start PulseWatch.
2. Generate observed release evidence.
3. Generate the public status page.
4. Run production readiness.
5. Publish only testnet-safe claims.
