# Base Sepolia Operator Runbook

This runbook is for the first public FlowMemory Uniswap v4 memory-signal hook release.

The goal is not just deployment. The goal is public proof:

1. the hook address has the correct `afterSwap` permission bits;
2. the source is verified;
3. a real hook path emits `AfterSwapObserved`;
4. a real hook path emits `FlowPulse`;
5. the reader attaches receipt-derived `txHash` and `logIndex`;
6. the release record states the boundary clearly.

The transaction is the proof envelope. The FlowPulse is the memory artifact.

## Hard Rules

- Do not commit private keys, RPC URLs, signed transactions, API keys, seed phrases, or deployer secrets.
- Do not claim Base mainnet.
- Do not claim audited custody.
- Do not claim the hook controls swaps or protects funds.
- Do not claim the hook knows `txHash` or `logIndex` during execution.
- Do not claim the swap transaction itself is memory.

## Inputs To Confirm

| Input | Current planning value |
| --- | --- |
| Network | Base Sepolia |
| Chain id | `84532` |
| PoolManager | `0x05E73354cFDd6745C338b50BcFDfA3Aa6fA03408` |
| CREATE2 deployer | `0x4e59b44847b379578588920cA78FbF26c0B4956C` |
| Target hook bits | `0x40` |
| Enabled callback | `afterSwap` only |

Before broadcast, re-check the official Uniswap deployments page and record the timestamp in the release record.

## Preflight

```bash
forge fmt --check
forge build
forge test -vvv
forge test --match-test testPlannerMinesBaseSepoliaCreate2AddressWithTargetFlags -vvv
forge test --match-test testAfterSwapHookEmitsFlowPulseAndReturnsZeroHookDelta -vvv
python tools/read_flowpulse_logs.py --help
```

Expected test result:

```text
12 passed; 0 failed; 0 skipped
```

## Deployment Plan Record

Before sending any transaction, fill the planning section in a copy of [BASE_SEPOLIA_RELEASE_RECORD_TEMPLATE.md](BASE_SEPOLIA_RELEASE_RECORD_TEMPLATE.md).

Required fields before broadcast:

- repository commit;
- Solidity version;
- optimizer settings;
- PoolManager;
- constructor args;
- init code hash;
- target hook bits;
- mined salt;
- computed hook address;
- computed hook low bits.

## Deployment

This repository intentionally does not store a private-key deployment script. Deployment should happen from an operator environment that records exact inputs and does not leak secrets.

After deployment, record:

- deployer address;
- deployment transaction hash;
- deployment block;
- deployed bytecode hash;
- source verification URL;
- constructor args verification URL.

Do not call the deployment public-ready until source verification is visible.

## Reader Evidence

After the hook emits logs, run:

```bash
python tools/read_flowpulse_logs.py \
  --rpc-url "$BASE_SEPOLIA_RPC_URL" \
  --hook-address "$FLOWMEMORY_HOOK_ADDRESS" \
  --from-block "$DEPLOYMENT_BLOCK" \
  --to-block latest \
  --finality-confirmations 20 \
  --pretty \
  --output releases/base-sepolia/flowpulse-evidence.json
```

The evidence file should show:

- at least one `AfterSwapObserved`;
- at least one `FlowPulse`;
- `receiptStatus: success`;
- receipt-derived `txHash`;
- receipt-derived `logIndex`;
- a finality status;
- zero rejected records.

## Public Canary

Publish a canary only after deployment and reader evidence exist.

Minimum canary artifacts:

- release record;
- source verification URL;
- hook address;
- sample transaction;
- decoded `AfterSwapObserved`;
- decoded `FlowPulse`;
- reader evidence JSON;
- clear boundary statement.

Acceptable canary line:

> FlowMemory has a verified Base Sepolia hook deployment with observed FlowPulse logs and reader-derived receipt evidence.

Not acceptable:

> FlowMemory has a production Base mainnet Uniswap v4 hook.
