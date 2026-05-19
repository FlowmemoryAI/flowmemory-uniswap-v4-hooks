# Cache Lineage Gate Example

Cache Lineage Gate makes KV/context reuse proof-carried.

It does not store KV tensors. It checks commitments around the cache artifact:
model, tokenizer, runtime, prompt prefix, side inputs, adapter, and cache
policy.

Run the demo:

```bash
python tools/cache_lineage_gate.py demo --pretty
```

Run one request:

```bash
python tools/cache_lineage_gate.py gate \
  --request examples/cache-lineage-gate/request.reuse.json \
  --ledger examples/cache-lineage-gate/ledger.example.json \
  --policy examples/cache-lineage-gate/policy.example.json \
  --pretty
```

The exact request reuses cache. The other demo requests reject unsafe reuse for
tokenizer drift, side-input drift, cache-policy drift, and unverified evidence.
