# AxiomWrit v0 Draft Spec

AxiomWrit is a proof-conditioned belief object.

It is the first FlowMemory R&D primitive designed specifically for AI-agent cognition.

## What It Is

AxiomWrit is a small canonical artifact that grants an agent scoped permission to believe, cite, reuse, or plan with a claim derived from a FlowPulse proof envelope.

FlowPulse is remembered.

AxiomWrit is believed.

## What It Is Not

- Not truth.
- Not intent.
- Not AI correctness.
- Not GPU attestation.
- Not on-chain enforcement.
- Not memory storage.
- Not a vector database.
- Not a proof that the swap was meaningful.

## Required Inputs

- FlowPulse evidence record from the reader.
- Claim object.
- Cognitive policy object.
- Agent id.

## Required Output

- `writId`;
- `claimHash`;
- `proofAnchor`;
- `allowedVerbs`;
- `deniedVerbs`;
- `beliefPatch`;
- evidence checks;
- warnings.

## Proof Tiers

| Tier | Meaning |
| --- | --- |
| `receipt_bound_flowpulse` | FlowPulse has successful receipt facts and reader-attached `txHash`/`logIndex`. |
| `receipt_attached_flowpulse` | Receipt facts exist but finality policy is not complete. |
| `local_draft` | Boundary payload exists without reader-attached receipt facts. |
| `rd_mock` | Explicit R&D/example material. |
| `unverified` | Evidence exists but does not satisfy the policy. |
| `rejected` | Required evidence is missing or invalid. |

## Verbs

Allowed verbs are positive cognitive permissions:

- `believe`;
- `cite`;
- `reuse_context`;
- `plan_with`.

Denied verbs block overclaims:

- `claim_semantic_truth`;
- `claim_user_intent`;
- `claim_gpu_attestation`;
- `claim_model_correctness`;
- `execute_onchain_action`.

## Belief Patch

The belief patch is the safe prompt fragment an agent runtime may use.

It contains:

- safe prompt facts;
- forbidden inferences;
- the claim hash;
- context mode.

This makes AxiomWrit more than a memory record. It is a cognition boundary.

## Design Line

AxiomWrit is not truth.

It is proof-conditioned admissibility.
