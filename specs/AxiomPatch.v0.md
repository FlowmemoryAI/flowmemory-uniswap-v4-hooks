# AxiomPatch v0 Draft Spec

AxiomPatch is a proof-conditioned cognitive state transition.

It is the operational form of AxiomWrit.

## Category

AxiomWrit says a claim is admissible.

AxiomPatch changes what an agent is allowed to do with that admissible claim.

It can:

- allow;
- deny;
- downgrade.

That third state is the important one.

Memory storage can retrieve context.

AxiomPatch can turn an unsafe action into a safer action.

## Example

```text
requested action: submit_onchain_transaction
proof available: receipt-bound FlowPulse boundary fact
missing proof: action authorization
decision: downgrade to propose_unsigned_action
```

This is not just policy gating.

It is proof-conditioned cognition.

## Required Fields

| Field | Meaning |
| --- | --- |
| `patchId` | Deterministic patch id. |
| `sourceWritId` | AxiomWrit used as source admissibility object. |
| `axiomCell` | Digest over proof anchor, claim, grants, and policy. |
| `claim` | Admissible claim. |
| `proofAnchor` | Receipt-bound FlowPulse facts. |
| `verbGrants` | Allow, deny, and downgrade action map. |
| `beliefDelta` | Epistemic types added and not added. |
| `proofMask` | Facts visible to the agent plus forbidden inferences. |
| `agentPulseDraft` | Draft record of agent use. |

## Epistemic Types

Actions require epistemic types:

- `BoundaryFact`;
- `ReceiptFact`;
- `CommitmentFact`;
- `IntentClaim`;
- `SemanticClaim`;
- `AttestationClaim`;
- `ActionAuthorization`.

A FlowPulse-derived AxiomPatch can add boundary, receipt, and commitment facts.

It does not add intent, semantic truth, attestation, or action authorization.

## Monotonic Downgrade

If the proof does not satisfy the requested action, the patch should downgrade before denying when a safe downgrade exists.

```text
submit_onchain_transaction -> propose_unsigned_action
claim_semantic_truth -> cite_boundary_fact_only
claim_gpu_attestation -> state_compute_attestation_absent
```

## Design Line

FlowMemory turns execution receipts into cognitive patches: proof-conditioned axioms that change what agents are allowed to believe, cite, reuse, downgrade, or do.
