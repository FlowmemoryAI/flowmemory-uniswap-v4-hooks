# CognitivePolicy v0 Draft Spec

CognitivePolicy defines what an AxiomWrit may allow an agent to do with a proof-backed claim.

## Purpose

The policy converts proof tier into cognitive permission.

The same FlowPulse can support different agent behaviors depending on policy:

- cite the boundary;
- believe the boundary happened;
- reuse context;
- plan with the boundary;
- deny semantic overclaims;
- deny on-chain action authority.

## Core Fields

```json
{
  "schema": "flowmemory.cognitive_policy.v0",
  "allowedVerbsByProofTier": {
    "receipt_bound_flowpulse": ["believe", "cite", "reuse_context", "plan_with"],
    "receipt_attached_flowpulse": ["believe", "cite"],
    "local_draft": ["cite"]
  },
  "deniedVerbs": [
    "claim_semantic_truth",
    "claim_user_intent",
    "claim_gpu_attestation",
    "claim_model_correctness",
    "execute_onchain_action"
  ],
  "scope": {
    "validForRootfieldOnly": true,
    "validForAgentOnly": true,
    "expiresAt": null,
    "maxDerivedDepth": 2
  }
}
```

## Design Line

Retrieval asks what is relevant.

CognitivePolicy asks what is admissible.
