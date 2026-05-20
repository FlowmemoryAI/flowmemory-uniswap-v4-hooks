# Operations

This folder contains production-like Base Sepolia operation templates.

Templates use environment variables and do not contain secrets.

Run PulseWatch directly:

```bash
python tools/pulse_watch.py run \
  --rpc-url "$FLOWMEMORY_RPC_URL" \
  --hook-address "$FLOWMEMORY_HOOK_ADDRESS" \
  --from-block "$FLOWMEMORY_FROM_BLOCK" \
  --state .flowmemory/pulsewatch-state.json \
  --memory-store .flowmemory/pulsewatch-memory.jsonl
```

Systemd template:

```text
ops/systemd/pulsewatch.service
```

Docker Compose template:

```text
ops/docker-compose.yml
```
