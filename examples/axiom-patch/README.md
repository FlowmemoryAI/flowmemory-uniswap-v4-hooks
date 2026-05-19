# AxiomPatch: Proof-Conditioned Cognitive State Transition

AxiomPatch is the operational mutation of AxiomWrit.

Run the demo:

```bash
python tools/axiom_patch.py demo --pretty
python -m unittest tools.test_axiom_patch
```

Regenerate the example patch and verdict:

```bash
python tools/axiom_patch.py mint \
  --flowpulse-evidence examples/axiom-patch/flowpulse-evidence.fixture.json \
  --claim examples/axiom-patch/claim.swap-boundary.json \
  --policy examples/axiom-patch/policy.patch.json \
  --agent-id demo-agent \
  --out examples/axiom-patch/axiompatch.example.json \
  --pretty

python tools/axiom_patch.py apply \
  --patch examples/axiom-patch/axiompatch.example.json \
  --plan examples/axiom-patch/plan.mixed-actions.json \
  --out examples/axiom-patch/verdict.allowed-downgraded-denied.json \
  --pretty
```

The core transition:

```text
submit_onchain_transaction -> propose_unsigned_action
```

The patch does not say the agent may act on-chain. It gives the agent a safer downgraded action that preserves usefulness without overclaiming proof.
