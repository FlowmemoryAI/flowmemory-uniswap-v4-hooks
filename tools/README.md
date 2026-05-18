# FlowMemory Tools

This folder contains dependency-light launch and evidence utilities.

## `read_flowpulse_logs.py`

Reads logs from a deployed `FlowMemoryAfterSwapHook`, decodes `AfterSwapObserved` and `FlowPulse`, fetches transaction receipts, and writes a proof-envelope JSON record.

The script does not need a private key. It only reads JSON-RPC data.

```bash
python tools/read_flowpulse_logs.py \
  --rpc-url "$BASE_SEPOLIA_RPC_URL" \
  --hook-address "$FLOWMEMORY_HOOK_ADDRESS" \
  --from-block 0 \
  --to-block latest \
  --pretty \
  --output releases/base-sepolia/flowpulse-evidence.json
```

Environment variable form:

```bash
export FLOWMEMORY_RPC_URL="$BASE_SEPOLIA_RPC_URL"
export FLOWMEMORY_HOOK_ADDRESS="0x..."
export FLOWMEMORY_FROM_BLOCK="0"
export FLOWMEMORY_TO_BLOCK="latest"
export FLOWMEMORY_FINALITY_CONFIRMATIONS="20"

python tools/read_flowpulse_logs.py --pretty
```

The output preserves the split that matters:

- `FlowPulse` payload comes from the hook log;
- `txHash`, `transactionIndex`, `logIndex`, receipt status, and block facts come from receipts;
- finality status comes from the configured confirmation policy.

Decoder tests:

```bash
python -m unittest tools.test_read_flowpulse_logs
```
