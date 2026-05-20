# Release Evidence

Release evidence turns observed Base Sepolia hook logs into a deterministic
packet.

This is testnet evidence only. It is not a Base mainnet claim and not a
production verifier network claim.

## Generate From Reader Output

```bash
python tools/release_evidence.py generate \
  --reader-output releases/base-sepolia/flowpulse-evidence.json \
  --output release-evidence/base-sepolia/RELEASE_PACKET.json
```

Observed release packets require at least one observed `FlowPulse`.

## Scan Directly

```bash
python tools/release_evidence.py scan \
  --rpc-url "$FLOWMEMORY_RPC_URL" \
  --hook-address "$FLOWMEMORY_HOOK_ADDRESS" \
  --from-block "$FLOWMEMORY_FROM_BLOCK" \
  --to-block latest \
  --output release-evidence/base-sepolia/RELEASE_PACKET.json
```

## Verify

```bash
python tools/release_evidence.py verify \
  --input release-evidence/base-sepolia/RELEASE_PACKET.json

python tools/release_evidence.py replay \
  --input release-evidence/base-sepolia/RELEASE_PACKET.json
```

## Packet Rules

- Proof envelope identity is `chainId + txHash + logIndex`.
- Duplicate proof envelopes are removed.
- Fixture evidence requires explicit `--fixture-mode`.
- Observed packets fail closed when no FlowPulse exists.
- Packet hash is deterministic.
- Finality states must not silently upgrade.
