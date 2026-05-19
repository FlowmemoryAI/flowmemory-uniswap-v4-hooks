# Obligation Membrane v0

Status: R&D draft.

Obligation Membrane is a local consistency model for multi-agent obligation
chains. It does not custody funds, escrow payments, authorize wallets, prove
work quality, verify semantic truth, guarantee model correctness, accelerate
GPUs, or claim production verifier readiness.

It checks whether an obligation preserves its memory constraints as it moves
through subagents, compute providers, delegated work, aggregate closures, and
payment settlement.

## Schema

```json
{
  "schema": "flowmemory.obligation_chain.v0",
  "chainId": "obligation-chain-001",
  "rootfieldId": "bytes32",
  "parentObligation": {
    "obligationId": "obl-parent-001",
    "type": "buy_agent_work",
    "requiredFmm0State": "FMM0_LIVE",
    "computePolicy": "FRESH_COMPUTE"
  },
  "childObligations": [
    {
      "obligationId": "obl-child-work-001",
      "type": "deliver_work",
      "rootfieldId": "bytes32",
      "fmm0State": "FMM0_LIVE",
      "computePolicy": "FRESH_COMPUTE",
      "status": "closed",
      "authorAgent": "worker-agent-001",
      "payeeAgent": "worker-agent-001"
    }
  ],
  "delegations": [
    {
      "delegationId": "del-work-001",
      "parentObligationId": "obl-parent-001",
      "childObligationId": "obl-child-work-001"
    }
  ],
  "parentClosure": {
    "closureType": "delivered",
    "sequence": 3,
    "aggregateChildIds": ["obl-child-work-001"]
  },
  "paymentClosure": {
    "closureType": "paid",
    "obligationId": "obl-parent-001",
    "sequence": 4
  }
}
```

## Decisions

`MEMBRANE_ACCEPTED`: the obligation chain preserves the parent's constraints.

`REJECTED`: at least one membrane invariant fails.

## Invariants

- `OM-I1`: Constraint Monotonicity.
- `OM-I2`: Delegation Lineage Conservation.
- `OM-I3`: No Compute Policy Laundering.
- `OM-I4`: No Memory Phase Laundering.
- `OM-I5`: Payee Spine Integrity.
- `OM-I6`: Child Refusal Propagation.
- `OM-I7`: No Silent Aggregation.
- `OM-I8`: Rootfield Firebreak.
- `OM-I9`: No Semantic Upgrade.
- `OM-I10`: Closure Before Payment.

## Forbidden Cases

- downgraded FMM-0 requirement;
- fresh compute requirement laundered into reuse;
- missing child obligation;
- broken payee spine;
- unresolved child obligation under a closed parent;
- child refusal swallowed by parent delivery;
- rootfield drift across delegation;
- aggregate work omits failed child;
- semantic truth or model-correctness upgrade.

## Non-Claims

Obligation Membrane does not claim custody, escrow, wallet authorization, fund
protection, work-quality proof, semantic truth, model correctness, GPU
acceleration, production verifier readiness, or live mainnet deployment.
