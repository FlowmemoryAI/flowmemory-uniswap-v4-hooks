# Agent Commerce Conservation v0

Status: R&D draft.

Agent Commerce Conservation is a local consistency model for autonomous
commerce episodes. It does not custody funds, escrow payment, authorize
wallets, prove work quality, or prove semantic truth. It checks whether
declared obligations conserve across spend, work, compute, refusal, and memory
state.

## Schema

```json
{
  "schema": "flowmemory.agent_commerce_episode.v0",
  "episodeId": "commerce-episode-001",
  "rootfieldId": "bytes32",
  "duplexLineVerdict": "ACCEPT_DUPLEXLINE",
  "participants": [
    {
      "agentId": "buyer-agent-001",
      "role": "buyer",
      "memoryHead": "flowpulse-buyer-001",
      "expectedMemoryHead": "flowpulse-buyer-001",
      "fmm0State": "FMM0_LIVE"
    }
  ],
  "obligations": [
    {
      "obligationId": "obl-work-001",
      "type": "deliver_work",
      "owner": "seller-agent-001",
      "beneficiary": "buyer-agent-001",
      "taskCommitment": "sha256:task-001",
      "workCommitment": "sha256:work-001",
      "status": "open"
    }
  ],
  "closures": [
    {
      "closureId": "close-work-001",
      "obligationId": "obl-work-001",
      "closureType": "delivered",
      "workCommitment": "sha256:work-001"
    }
  ],
  "computeContext": {
    "computeReuseVerdict": "NOT_APPLICABLE",
    "cacheLineageVerdict": "NOT_APPLICABLE"
  }
}
```

## Decisions

`CONSERVED`: the episode conserves declared obligations.

`REJECT_CONSERVATION`: the episode violates a conservation invariant.

## Invariants

- `ACC-I1`: Every obligation closes at most once.
- `ACC-I2`: Every payment discharges one payment obligation.
- `ACC-I3`: Every work delivery matches one work obligation.
- `ACC-I4`: No closure crosses incompatible memory heads.
- `ACC-I5`: Unsafe compute reuse cannot close payment.
- `ACC-I6`: Rejected exchange requires refusal or repair.

## Forbidden Cases

- orphan payment;
- orphan work delivery;
- double-paid obligation;
- double-delivered work;
- work paid under stale buyer head;
- compute payment with unsafe reuse;
- refusal required but missing.

## Non-Claims

Agent Commerce Conservation does not claim custody, escrow, wallet
authorization, fund protection, work-quality proof, semantic truth, model
correctness, production verifier readiness, or live mainnet deployment.
