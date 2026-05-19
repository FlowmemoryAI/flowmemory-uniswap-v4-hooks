# Compute Reuse Consistency Harness

The Compute Reuse Consistency Harness is the bridge between the Compute Reuse
Router, Cache Lineage Gate, and the FlowMemory memory model.

It ties AI/GPU reuse back into the FlowMemory memory model:

```text
safe reuse = cache lineage + compute fingerprint + receipt-bound history
```

The harness does not benchmark GPUs. It tests whether autonomous compute reuse
is legal under the memory model.

## Cases

- Safe cache and compute reuse after a FlowPulse boundary.
- Tokenizer drift blocks cache reuse.
- Runtime drift blocks compute reuse.
- Retrocausal receipt claims block reuse.
- Missing cache attestation blocks reuse when required.

## Run It

```bash
python tools/compute_reuse_consistency.py demo --pretty
```

Expected summary:

```text
cases passed: 5/5
unsafe reuse blocked: 4/4
```

## Launch Line

FlowMemory is not trying to make GPUs faster. It is making compute reuse harder
to get wrong.

## Non-Claims

- Not GPU acceleration.
- Not KV-cache storage.
- Not model correctness.
- Not semantic truth.
- Not production attestation.
