# PulseWatch Operations

PulseWatch is the always-on reader. The hook is transaction-triggered;
PulseWatch is continuous.

## Run Once

```bash
python tools/pulse_watch.py run \
  --rpc-url "$FLOWMEMORY_RPC_URL" \
  --hook-address "$FLOWMEMORY_HOOK_ADDRESS" \
  --from-block "$FLOWMEMORY_FROM_BLOCK" \
  --state .flowmemory/pulsewatch-state.json \
  --memory-store .flowmemory/pulsewatch-memory.jsonl \
  --once \
  --json --pretty
```

## Continuous Run

```bash
python tools/pulse_watch.py run \
  --rpc-url "$FLOWMEMORY_RPC_URL" \
  --hook-address "$FLOWMEMORY_HOOK_ADDRESS" \
  --from-block "$FLOWMEMORY_FROM_BLOCK" \
  --state .flowmemory/pulsewatch-state.json \
  --memory-store .flowmemory/pulsewatch-memory.jsonl \
  --poll-seconds 30 \
  --max-retries 3 \
  --retry-seconds 5
```

## Health

```bash
python tools/pulse_watch.py health \
  --state .flowmemory/pulsewatch-state.json \
  --expected-chain-id 84532 \
  --expected-hook-address "$FLOWMEMORY_HOOK_ADDRESS" \
  --latest-block "$FLOWMEMORY_LATEST_BLOCK"
```

Health output includes reader lag, latest scanned block, configured chain,
hook address, cursor status, and last error.

## Replay

```bash
python tools/pulse_watch.py replay \
  --reader-output releases/base-sepolia/flowpulse-evidence.json \
  --from-cursor "$FLOWMEMORY_FROM_BLOCK"
```

Replay must reproduce the same canonical memory record ids from the same reader
output.

## Service Templates

See:

- `ops/systemd/pulsewatch.service`
- `ops/docker-compose.yml`

These templates use environment variables and do not contain secrets.

## Degraded Status

Use degraded status when:

- RPC fails repeatedly;
- reader lag exceeds SLO;
- cursor state is missing or corrupt;
- finality downgrades after a reorg warning;
- hook address or chain id does not match configuration.

Do not silently promote observed evidence to verified evidence.
