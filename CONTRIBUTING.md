# Contributing

FlowMemory is building a memory-native Uniswap v4 hook primitive and local R&D
tools for receipt-bound machine memory.

Contributions should preserve the core split:

```text
swap != memory
transaction = proof envelope
FlowPulse = memory artifact
```

## Local Checks

Run:

```bash
forge fmt --check
forge build
forge test -vvv
python -m unittest tools.test_read_flowpulse_logs tools.test_memory_trace tools.test_axiom_writ tools.test_axiom_patch tools.test_boundary_fission tools.test_pulse_retire tools.test_flow_mmu tools.test_flow_quiesce tools.test_flow_serial tools.test_flow_litmus tools.test_launch_reality_check
python tools/launch_reality_check.py --pretty
git diff --check
```

## Technical Boundaries

Do not add claims or code paths that imply:

- custody;
- fund protection;
- swap control;
- dynamic fee control;
- custom accounting;
- semantic truth validation;
- model correctness;
- GPU acceleration;
- production verifier infrastructure;
- `txHash` or `logIndex` known inside the hook.

Reader/verifier tooling may attach receipt facts after the transaction lands.
The hook itself must not pretend to know them during execution.

## Documentation Tone

The language should be bold but technically bounded.

Good:

- first memory-native Uniswap v4 hook primitive;
- verified on-chain emission boundary;
- FlowPulse memory signal;
- transaction as proof envelope;
- receipt-linearizable machine histories;
- executable forbidden outcomes.

Avoid:

- live mainnet claims without a release record;
- audited production claims;
- custody or fund-safety claims;
- broad AI truth claims;
- vague "AI memory" language without the FlowPulse boundary model.

## Pull Requests

Keep changes scoped. A good PR should explain:

- what boundary, signal, tool, or document changed;
- how it preserves the hook invariants;
- which tests or checks were run;
- what claims it deliberately avoids.
