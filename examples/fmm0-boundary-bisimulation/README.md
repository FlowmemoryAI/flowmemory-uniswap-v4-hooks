# FMM-0 Boundary Bisimulation Example

Run the screenshot-ready boundary projection demo:

```bash
python tools/fmm0_boundary_bisim.py demo --pretty
```

Expected output is in [expected-output.txt](expected-output.txt).

The demo checks that the same FlowPulse boundary survives projection from hook
signal, to receipt envelope, to FMM-0 runtime state.
