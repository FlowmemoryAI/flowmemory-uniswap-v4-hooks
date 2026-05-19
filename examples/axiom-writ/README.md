# AxiomWrit: Proof-Conditioned Cognition From A FlowPulse

AxiomWrit is the R&D primitive that turns FlowPulse evidence into scoped machine belief.

Run the demo:

```bash
python tools/axiom_writ.py demo --pretty
python -m unittest tools.test_axiom_writ
```

Regenerate the examples:

```bash
python tools/axiom_writ.py mint \
  --flowpulse-evidence examples/axiom-writ/flowpulse-evidence.fixture.json \
  --claim examples/axiom-writ/claim.swap-boundary.json \
  --policy examples/axiom-writ/policy.agent.json \
  --agent-id demo-agent \
  --out examples/axiom-writ/axiomwrit.example.json \
  --pretty

python tools/axiom_writ.py apply \
  --writ examples/axiom-writ/axiomwrit.example.json \
  --plan examples/axiom-writ/plan.allowed-citation.json \
  --out examples/axiom-writ/cognition-verdict.allowed.json \
  --pretty

python tools/axiom_writ.py apply \
  --writ examples/axiom-writ/axiomwrit.example.json \
  --plan examples/axiom-writ/plan.denied-action.json \
  --out examples/axiom-writ/cognition-verdict.denied.json \
  --pretty
```

The expected story:

```text
FlowPulse evidence enters.
AxiomWrit is minted.
Citation plan is allowed.
Action plan is denied.
Agent now has proof-conditioned cognition, not generic memory.
```
