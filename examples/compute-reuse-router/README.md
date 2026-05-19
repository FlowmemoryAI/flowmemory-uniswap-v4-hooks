# Compute Reuse Router Example

This example shows the GPU workflow claim in executable form:

```text
GPUs compute. FlowMemory remembers.
```

The router does not make hardware faster. It checks whether a prior
ComputePulse has enough commitment, lineage, receipt, and policy evidence to
reuse the output instead of scheduling a new GPU job.

Run the screenshot demo:

```bash
python tools/compute_reuse_router.py demo --pretty
```

Run one request:

```bash
python tools/compute_reuse_router.py route \
  --request examples/compute-reuse-router/request.reuse.json \
  --ledger examples/compute-reuse-router/ledger.example.json \
  --policy examples/compute-reuse-router/policy.example.json \
  --pretty
```

The exact-hit request reuses prior compute. The other demo requests reject
unsafe reuse for runtime drift, unverified evidence, missing attestation, or
expiration.
