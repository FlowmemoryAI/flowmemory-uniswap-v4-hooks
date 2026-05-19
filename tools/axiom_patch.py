#!/usr/bin/env python3
"""
AxiomPatch: proof-conditioned cognitive state transitions for agents.

AxiomPatch wraps an AxiomWrit and converts proof-backed memory into typed
agent-action decisions: allow, deny, or downgrade.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover - supports script and package execution
    from tools import axiom_writ
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore


PATCH_SCHEMA = "flowmemory.axiom_patch.v0"
PATCH_VERDICT_SCHEMA = "flowmemory.axiom_patch_verdict.v0"
ACTION_TYPES = {
    "observe_boundary_fact": "BoundaryFact",
    "cite_boundary_fact": "BoundaryFact",
    "believe": "BoundaryFact",
    "cite": "BoundaryFact",
    "reuse_as_agent_context": "CommitmentFact",
    "reuse_context": "CommitmentFact",
    "summarize_with_receipt_citation": "ReceiptFact",
    "create_agentpulse_draft": "BoundaryFact",
    "propose_unsigned_action": "BoundaryFact",
    "plan_with": "BoundaryFact",
    "claim_semantic_truth": "SemanticClaim",
    "claim_user_intent": "IntentClaim",
    "claim_gpu_attestation": "AttestationClaim",
    "claim_model_correctness": "AttestationClaim",
    "submit_onchain_transaction": "ActionAuthorization",
    "sign_transaction": "ActionAuthorization",
    "move_funds": "ActionAuthorization",
}


def default_patch_policy() -> dict[str, Any]:
    return {
        "verbGrantsByProofTier": {
            "receipt_bound_flowpulse": {
                "allow": [
                    "observe_boundary_fact",
                    "cite_boundary_fact",
                    "reuse_as_agent_context",
                    "summarize_with_receipt_citation",
                    "create_agentpulse_draft",
                    "propose_unsigned_action",
                ],
                "deny": ["sign_transaction", "move_funds"],
                "downgrade": {
                    "submit_onchain_transaction": "propose_unsigned_action",
                    "claim_user_intent": "state_no_intent_inference_available",
                    "claim_semantic_truth": "cite_boundary_fact_only",
                    "claim_gpu_attestation": "state_compute_attestation_absent",
                    "claim_model_correctness": "state_model_correctness_unproven",
                },
            }
        },
        "scope": {"validForRootfieldOnly": True, "validForAgentOnly": True, "maxDerivedDepth": 2},
    }


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def write_json(payload: Any, output: str | None, pretty: bool) -> None:
    axiom_writ.write_json(payload, output, pretty)


def verb_grants(policy: dict[str, Any], proof_tier: str) -> dict[str, Any]:
    tier_grants = (policy.get("verbGrantsByProofTier") or {}).get(proof_tier)
    if isinstance(tier_grants, dict):
        return {
            "allow": sorted(set(str(item) for item in tier_grants.get("allow", []))),
            "deny": sorted(set(str(item) for item in tier_grants.get("deny", []))),
            "downgrade": {str(k): str(v) for k, v in (tier_grants.get("downgrade", {}) or {}).items()},
        }
    defaults = default_patch_policy()["verbGrantsByProofTier"]["receipt_bound_flowpulse"]
    return copy.deepcopy(defaults)


def build_proof_mask(proof_anchor: dict[str, Any]) -> dict[str, Any]:
    visible = ["rootfieldId", "commitment", "hookAddress", "txHash", "logIndex", "receiptStatus", "proofTier"]
    return {
        "visibleFacts": {key: proof_anchor.get(key) for key in visible},
        "commitmentOnlyFields": ["payload", "uri"],
        "forbiddenInferences": [
            "Do not infer trader intent.",
            "Do not infer strategy correctness.",
            "Do not infer GPU execution.",
            "Do not treat advisory URI as authority.",
        ],
    }


def build_belief_delta() -> dict[str, Any]:
    return {
        "operation": "add_scoped_axiom",
        "adds": ["BoundaryFact", "ReceiptFact", "CommitmentFact"],
        "doesNotAdd": ["IntentClaim", "SemanticClaim", "AttestationClaim", "ActionAuthorization"],
    }


def mint_patch(evidence: dict[str, Any], claim: dict[str, Any], policy: dict[str, Any], agent_id: str) -> dict[str, Any]:
    writ = axiom_writ.mint_writ(evidence, claim, policy.get("writPolicy", policy), agent_id)
    proof_tier = (writ.get("proofAnchor") or {}).get("proofTier", "rejected")
    grants = verb_grants(policy, proof_tier)
    proof_anchor = writ.get("proofAnchor") if isinstance(writ.get("proofAnchor"), dict) else {}
    claim_hash = (writ.get("claim") or {}).get("claimHash")
    proof_anchor_hash = axiom_writ.digest(proof_anchor)
    policy_hash = axiom_writ.digest(policy)
    grants_hash = axiom_writ.digest(grants)
    axiom_cell = axiom_writ.digest(
        {
            "version": PATCH_SCHEMA,
            "proofAnchorHash": proof_anchor_hash,
            "claimHash": claim_hash,
            "rootfieldId": writ.get("rootfieldId"),
            "verbGrantsHash": grants_hash,
            "policyHash": policy_hash,
        }
    )

    body = {
        "schema": PATCH_SCHEMA,
        "patchType": "proof_conditioned_cognitive_state_transition",
        "status": "active" if writ.get("status") == "active" else "rejected",
        "agentId": agent_id,
        "rootfieldId": writ.get("rootfieldId"),
        "sourceWritId": writ.get("writId"),
        "axiomCell": axiom_cell,
        "claim": writ.get("claim"),
        "proofAnchor": proof_anchor,
        "verbGrants": grants,
        "beliefDelta": build_belief_delta(),
        "proofMask": build_proof_mask(proof_anchor),
        "agentPulseDraft": {
            "pulseType": "AgentPulse",
            "status": "draft",
            "sourcePatchId": None,
            "sourceWritId": writ.get("writId"),
            "rootfieldId": writ.get("rootfieldId"),
            "allowedUse": "record_agent_use_after_runtime_accepts_verdict",
        },
        "sourceWrit": writ,
    }
    patch_id = axiom_writ.digest(body)
    body["patchId"] = patch_id
    body["agentPulseDraft"]["sourcePatchId"] = patch_id
    return body


def verify_patch(patch: dict[str, Any]) -> dict[str, Any]:
    body = copy.deepcopy(patch)
    patch_id = body.pop("patchId", None)
    if isinstance(body.get("agentPulseDraft"), dict):
        body["agentPulseDraft"]["sourcePatchId"] = patch_id
        # Rebuild the pre-id body shape used during minting.
        body["agentPulseDraft"]["sourcePatchId"] = None
    source_writ = patch.get("sourceWrit") if isinstance(patch.get("sourceWrit"), dict) else {}
    writ_verification = axiom_writ.verify_writ(source_writ) if source_writ else {"status": "invalid"}
    checks = {
        "schemaMatches": patch.get("schema") == PATCH_SCHEMA,
        "patchIdMatches": axiom_writ.digest(body) == patch_id,
        "sourceWritValid": writ_verification["status"] == "valid",
        "activeRequiresActiveWrit": patch.get("status") != "active" or source_writ.get("status") == "active",
        "hasDowngradeRules": bool(((patch.get("verbGrants") or {}).get("downgrade") or {})),
        "beliefDeltaDoesNotAddActionAuthorization": "ActionAuthorization"
        in ((patch.get("beliefDelta") or {}).get("doesNotAdd") or []),
    }
    failed = [key for key, ok in checks.items() if not ok]
    return {
        "schema": "flowmemory.axiom_patch_verification.v0",
        "status": "valid" if not failed else "invalid",
        "patchId": patch_id,
        "checks": checks,
        "failedChecks": failed,
        "sourceWritVerification": writ_verification,
    }


def required_epistemic_type(action: str) -> str:
    return ACTION_TYPES.get(action, "UnknownClaim")


def apply_patch(patch: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    verification = verify_patch(patch)
    grants = patch.get("verbGrants") if isinstance(patch.get("verbGrants"), dict) else {}
    allow = set(grants.get("allow") if isinstance(grants.get("allow"), list) else [])
    deny = set(grants.get("deny") if isinstance(grants.get("deny"), list) else [])
    downgrade = grants.get("downgrade") if isinstance(grants.get("downgrade"), dict) else {}
    belief_adds = set((patch.get("beliefDelta") or {}).get("adds") or [])
    actions = [str(action) for action in plan.get("requestedActions", plan.get("requestedVerbs", []))]

    verdict = {
        "schema": PATCH_VERDICT_SCHEMA,
        "planId": plan.get("planId"),
        "agentId": plan.get("agentId"),
        "patchId": patch.get("patchId"),
        "decision": "deny",
        "allowedActions": [],
        "downgradedActions": [],
        "deniedActions": [],
        "reasons": [],
        "proofMaskedContext": patch.get("proofMask"),
        "agentPulseDraft": patch.get("agentPulseDraft"),
    }

    if verification["status"] != "valid":
        verdict["reasons"].append("patch_invalid")
    if patch.get("status") != "active":
        verdict["reasons"].append("patch_not_active")
    if plan.get("agentId") != patch.get("agentId"):
        verdict["reasons"].append("wrong_agent")
    if plan.get("rootfieldId") != patch.get("rootfieldId"):
        verdict["reasons"].append("wrong_rootfield")

    for action in actions:
        required_type = required_epistemic_type(action)
        if action in allow and required_type in belief_adds:
            verdict["allowedActions"].append(action)
        elif action in downgrade:
            verdict["downgradedActions"].append({"from": action, "to": downgrade[action], "requiredType": required_type})
            verdict["reasons"].append(f"action_downgraded:{action}->{downgrade[action]}")
        elif action in deny:
            verdict["deniedActions"].append({"action": action, "requiredType": required_type})
            verdict["reasons"].append(f"action_denied:{action}")
        else:
            verdict["deniedActions"].append({"action": action, "requiredType": required_type})
            verdict["reasons"].append(f"action_not_admissible:{action}")

    if verdict["deniedActions"]:
        verdict["decision"] = "deny"
    elif verdict["downgradedActions"]:
        verdict["decision"] = "downgrade"
    elif not verdict["reasons"]:
        verdict["decision"] = "allow"
        verdict["reasons"].append("all_requested_actions_allowed_by_axiom_patch")
    else:
        verdict["decision"] = "deny"
    return verdict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mint, verify, and apply AxiomPatch cognitive state transitions.")
    sub = parser.add_subparsers(dest="command", required=True)

    mint = sub.add_parser("mint", help="Mint an AxiomPatch from FlowPulse evidence.")
    mint.add_argument("--flowpulse-evidence", required=True)
    mint.add_argument("--claim", required=True)
    mint.add_argument("--policy", required=True)
    mint.add_argument("--agent-id", required=True)
    mint.add_argument("--out")
    mint.add_argument("--pretty", action="store_true")

    verify = sub.add_parser("verify", help="Verify an AxiomPatch.")
    verify.add_argument("--patch", required=True)
    verify.add_argument("--pretty", action="store_true")

    apply_cmd = sub.add_parser("apply", help="Apply an AxiomPatch to an agent plan.")
    apply_cmd.add_argument("--patch", required=True)
    apply_cmd.add_argument("--plan", required=True)
    apply_cmd.add_argument("--out")
    apply_cmd.add_argument("--pretty", action="store_true")

    demo = sub.add_parser("demo", help="Run the fixture demo.")
    demo.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def fixture_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "examples" / "axiom-patch"


def run_demo(pretty: bool) -> int:
    root = fixture_dir()
    patch = mint_patch(
        read_json(root / "flowpulse-evidence.fixture.json"),
        read_json(root / "claim.swap-boundary.json"),
        read_json(root / "policy.patch.json"),
        "demo-agent",
    )
    mixed_plan = read_json(root / "plan.mixed-actions.json")
    payload = {
        "schema": "flowmemory.axiom_patch_demo.v0",
        "story": [
            "FlowPulse evidence enters.",
            "AxiomPatch is minted.",
            "Citation-like actions are allowed.",
            "Transaction submission is downgraded to an unsigned proposal.",
            "Semantic and custody overclaims are denied or downgraded.",
        ],
        "patch": patch,
        "verification": verify_patch(patch),
        "verdict": apply_patch(patch, mixed_plan),
    }
    write_json(payload, None, pretty)
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "mint":
        patch = mint_patch(
            read_json(args.flowpulse_evidence),
            read_json(args.claim),
            read_json(args.policy),
            args.agent_id,
        )
        write_json(patch, args.out, args.pretty)
        return 0 if patch["status"] == "active" else 1
    if args.command == "verify":
        result = verify_patch(read_json(args.patch))
        write_json(result, None, args.pretty)
        return 0 if result["status"] == "valid" else 1
    if args.command == "apply":
        verdict = apply_patch(read_json(args.patch), read_json(args.plan))
        write_json(verdict, args.out, args.pretty)
        if verdict["decision"] == "allow":
            return 0
        if verdict["decision"] == "downgrade":
            return 3
        return 2
    if args.command == "demo":
        return run_demo(args.pretty)
    raise AssertionError(args.command)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
