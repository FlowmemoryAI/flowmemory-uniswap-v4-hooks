# Base Sepolia Release Evidence

This folder is for generated Base Sepolia release evidence packets.

Generated packets must come from observed reader output unless `--fixture-mode`
is explicit. Test fixture packets are not public deployment evidence.

Generate from reader output:

```bash
python tools/release_evidence.py generate \
  --reader-output releases/base-sepolia/flowpulse-evidence.json \
  --output release-evidence/base-sepolia/RELEASE_PACKET.json
```

Scan directly from RPC:

```bash
python tools/release_evidence.py scan \
  --rpc-url "$FLOWMEMORY_RPC_URL" \
  --hook-address "$FLOWMEMORY_HOOK_ADDRESS" \
  --from-block "$FLOWMEMORY_FROM_BLOCK" \
  --output release-evidence/base-sepolia/RELEASE_PACKET.json
```

Verify:

```bash
python tools/release_evidence.py verify \
  --input release-evidence/base-sepolia/RELEASE_PACKET.json
```

Do not commit secrets or private `.env` files here.
