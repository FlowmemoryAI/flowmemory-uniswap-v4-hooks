# FMM-0 Memory Model Example

This folder contains the FMM-0 manifest used to generate the public conformance
matrix.

```bash
python tools/render_fmm0_matrix.py \
  --manifest examples/memory-model/fmm0.manifest.json \
  --out docs/FMM_0_CONFORMANCE_MATRIX.md
```

FMM-0 is the FlowMemory Agent Memory Model:

```text
Everyone treated agent memory like retrieval. FlowMemory treats it like a memory model.
```

The final rule, `FMM-0.R7`, intentionally remains pending until a Base Sepolia
release record includes public receipt evidence from a deployed hook.
