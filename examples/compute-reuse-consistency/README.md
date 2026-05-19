# Compute Reuse Consistency Example

Run the harness:

```bash
python tools/compute_reuse_consistency.py demo --pretty
```

The harness combines FlowSerial, Cache Lineage Gate, and Compute Reuse Router.
It proves that safe reuse needs receipt-bound history, cache lineage, and
compute fingerprint compatibility.
