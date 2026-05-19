## Summary

Describe the boundary, signal, tool, doc, or release artifact changed.

## Checks Run

- [ ] `forge fmt --check`
- [ ] `forge build`
- [ ] `forge test -vvv`
- [ ] `python -m unittest tools.test_read_flowpulse_logs tools.test_memory_trace tools.test_axiom_writ tools.test_axiom_patch tools.test_boundary_fission tools.test_pulse_retire tools.test_flow_mmu tools.test_flow_quiesce tools.test_flow_serial tools.test_flow_litmus tools.test_launch_reality_check`
- [ ] `python tools/launch_reality_check.py --pretty`
- [ ] `git diff --check`

## Claim Boundaries

- [ ] Does not claim live mainnet deployment without release evidence.
- [ ] Does not claim audited production infrastructure.
- [ ] Does not claim custody or fund protection.
- [ ] Does not claim swap control, routing control, dynamic fees, or custom accounting.
- [ ] Does not claim semantic truth, model correctness, GPU acceleration, or production verifier infrastructure.
- [ ] Does not claim the hook knows `txHash` or `logIndex` during execution.

## FlowMemory Boundary

- [ ] Preserves: swap != memory.
- [ ] Preserves: transaction = proof envelope.
- [ ] Preserves: FlowPulse = memory artifact.
