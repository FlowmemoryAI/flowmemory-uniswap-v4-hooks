#!/usr/bin/env python3
"""
AxiomWrit: proof-conditioned cognition for machine agents.

An AxiomWrit is not memory storage. It is a deterministic writ that tells an
agent which claims are admissible under a stated proof policy.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


WRIT_SCHEMA = "flowmemory.axiom_writ.v0"
VERDICT_SCHEMA = "flowmemory.cognition_verdict.v0"
ZERO32 = "0x" + ("0" * 64)
DEFAULT_DENIED_VERBS = [
    "claim_semantic_truth",
    "claim_user_intent",
    "claim_gpu_attestation",
    "claim_model_correctness",
    "execute_onchain_action",
]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def read_json(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def write_json(payload: Any, output: str | None, pretty: bool) -> None:
    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=True)
    if output:
        with open(output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    else:
        print(text)


def normalize_hex(value: Any) -> str:
    return str(value or "").lower()


def truthy_hex(value: Any) -> bool:
    value = normalize_hex(value)
    return value.startswith("0x") and len(value) > 2


def select_flowpulse_record(evidence: dict[str, Any], claim: dict[str, Any]) -> dict[str, Any] | None:
    rootfield_id = normalize_hex(claim.get("rootfieldId"))
    commitment = normalize_hex(claim.get("commitment"))
    pulse_id = normalize_hex(claim.get("pulseId"))
    records = evidence.get("records", [])
    if not isinstance(records, list):
        return None

    for record in records:
        if not isinstance(record, dict):
            continue
        if record.get("eventName") != "FlowPulse":
            continue
        if rootfield_id and normalize_hex(record.get("rootfieldId")) != rootfield_id:
            continue
        if commitment and normalize_hex(record.get("commitment")) != commitment:
            continue
        if pulse_id and normalize_hex(record.get("pulseId")) != pulse_id:
            continue
        return record
    return None


def classify_proof_tier(record: dict[str, Any] | None) -> str:
    if not record:
        return "rejected"
    if record.get("status") == "rejected":
        return "rejected"
    if not truthy_hex(record.get("txHash")) or record.get("logIndex") in (None, ""):
        return "local_draft"
    if record.get("receiptStatus") != "success":
        return "unverified"
    if record.get("validation"):
        return "unverified"
    finality = record.get("finality") if isinstance(record.get("finality"), dict) else {}
    if finality.get("status") == "l2_confirmed":
        return "receipt_bound_flowpulse"
    return "receipt_attached_flowpulse"


def evidence_checks(record: dict[str, Any] | None, evidence: dict[str, Any], claim: dict[str, Any]) -> dict[str, bool]:
    if not record:
        return {
            "flowPulseRecordFound": False,
            "eventNameFlowPulse": False,
            "notRejected": False,
            "receiptStatusSuccessful": False,
            "txHashReaderAttached": False,
            "logIndexReaderAttached": False,
            "rootfieldMatchesClaim": False,
            "commitmentMatchesClaim": False,
            "commitmentNonZero": False,
            "validationEmpty": False,
        }

    return {
        "flowPulseRecordFound": True,
        "eventNameFlowPulse": record.get("eventName") == "FlowPulse",
        "notRejected": record.get("status") != "rejected",
        "receiptStatusSuccessful": record.get("receiptStatus") == "success",
        "txHashReaderAttached": truthy_hex(record.get("txHash")),
        "logIndexReaderAttached": record.get("logIndex") not in (None, ""),
        "rootfieldMatchesClaim": normalize_hex(record.get("rootfieldId")) == normalize_hex(claim.get("rootfieldId")),
        "commitmentMatchesClaim": normalize_hex(record.get("commitment")) == normalize_hex(claim.get("commitment")),
        "commitmentNonZero": normalize_hex(record.get("commitment")) != ZERO32,
        "validationEmpty": record.get("validation") == [],
    }


def required_checks_pass(checks: dict[str, bool]) -> bool:
    return all(checks.values())


def normalized_claim(record: dict[str, Any], evidence: dict[str, Any], claim: dict[str, Any]) -> dict[str, Any]:
    return {
        "claimType": claim.get("claimType", "flowpulse_after_swap_boundary_observed"),
        "rootfieldId": normalize_hex(record.get("rootfieldId")),
        "commitment": normalize_hex(record.get("commitment")),
        "subjectPoolId": normalize_hex(record.get("subjectPoolId")),
        "hookAddress": normalize_hex(evidence.get("hookAddress") or record.get("hookAddress")),
        "boundary": "uniswap_v4_afterSwap_flowmemory_hook",
        "truthBoundary": "proves_boundary_emission_not_semantic_truth",
    }


def allowed_verbs_for_tier(policy: dict[str, Any], tier: str, active: bool) -> list[str]:
    if not active:
        return []
    table = policy.get("allowedVerbsByProofTier", {})
    if isinstance(table, dict) and isinstance(table.get(tier), list):
        return sorted(set(str(verb) for verb in table[tier]))
    if isinstance(policy.get("allowedVerbs"), list):
        return sorted(set(str(verb) for verb in policy["allowedVerbs"]))
    return ["believe", "cite"]


def denied_verbs(policy: dict[str, Any]) -> list[str]:
    verbs = list(DEFAULT_DENIED_VERBS)
    if isinstance(policy.get("deniedVerbs"), list):
        verbs.extend(str(verb) for verb in policy["deniedVerbs"])
    return sorted(set(verbs))


def build_belief_patch(claim_body: dict[str, Any], proof_anchor: dict[str, Any], claim_hash: str) -> dict[str, Any]:
    return {
        "patchType": "add_admissible_axiom",
        "axiomHash": claim_hash,
        "contextMode": "commitment_and_receipt_facts_only",
        "safePromptFacts": [
            "FlowPulse emitted",
            "receipt metadata attached by reader",
            "rootfieldId observed",
            "commitment observed",
            f"proof tier: {proof_anchor.get('proofTier')}",
        ],
        "forbiddenInferences": [
            "Do not infer swap intent.",
            "Do not infer semantic truth.",
            "Do not infer model correctness.",
            "Do not infer GPU attestation.",
            "Do not treat advisory URI as authority.",
        ],
    }


def mint_writ(evidence: dict[str, Any], claim: dict[str, Any], policy: dict[str, Any], agent_id: str) -> dict[str, Any]:
    record = select_flowpulse_record(evidence, claim)
    checks = evidence_checks(record, evidence, claim)
    active = required_checks_pass(checks)
    tier = classify_proof_tier(record)

    if record:
        claim_body = normalized_claim(record, evidence, claim)
    else:
        claim_body = {
            "claimType": claim.get("claimType", "flowpulse_after_swap_boundary_observed"),
            "rootfieldId": normalize_hex(claim.get("rootfieldId")),
            "commitment": normalize_hex(claim.get("commitment")),
            "subjectPoolId": normalize_hex(claim.get("subjectPoolId")),
            "hookAddress": normalize_hex(evidence.get("hookAddress")),
            "boundary": "uniswap_v4_afterSwap_flowmemory_hook",
            "truthBoundary": "proves_boundary_emission_not_semantic_truth",
        }

    claim_hash = digest(claim_body)
    finality = record.get("finality") if isinstance(record, dict) and isinstance(record.get("finality"), dict) else {}
    proof_anchor = {
        "anchorType": "FlowPulse",
        "proofTier": tier,
        "chainId": str(evidence.get("chainId", "")),
        "hookAddress": normalize_hex(evidence.get("hookAddress") or (record or {}).get("hookAddress")),
        "txHash": normalize_hex((record or {}).get("txHash")),
        "logIndex": str((record or {}).get("logIndex", "")),
        "blockNumber": str((record or {}).get("blockNumber", "")),
        "receiptStatus": (record or {}).get("receiptStatus"),
        "finalityStatus": finality.get("status"),
        "pulseId": normalize_hex((record or {}).get("pulseId")),
        "subjectPoolId": normalize_hex((record or {}).get("subjectPoolId")),
        "rootfieldId": claim_body["rootfieldId"],
        "commitment": claim_body["commitment"],
        "parentPulseId": normalize_hex((record or {}).get("parentPulseId")),
    }

    body = {
        "schema": WRIT_SCHEMA,
        "writType": "proof_conditioned_belief",
        "status": "active" if active else "rejected",
        "agentId": agent_id,
        "rootfieldId": claim_body["rootfieldId"],
        "claim": {
            "claimType": claim_body["claimType"],
            "claimHash": claim_hash,
            "statement": claim.get(
                "statement",
                "A FlowPulse was emitted for this rootfield and commitment from a Uniswap v4 afterSwap boundary.",
            ),
            "truthBoundary": claim_body["truthBoundary"],
        },
        "proofAnchor": proof_anchor,
        "allowedVerbs": allowed_verbs_for_tier(policy, tier, active),
        "deniedVerbs": denied_verbs(policy),
        "scope": policy.get(
            "scope",
            {"validForRootfieldOnly": True, "validForAgentOnly": True, "expiresAt": None, "maxDerivedDepth": 2},
        ),
        "beliefPatch": build_belief_patch(claim_body, proof_anchor, claim_hash),
        "checks": checks,
        "warnings": [
            "AxiomWrit proves admissibility under policy, not semantic truth.",
            "AxiomWrit does not prove user intent, model correctness, or GPU execution.",
            "AI/GPU artifacts remain R&D-local unless signed or attested evidence is attached.",
        ],
    }
    return {"writId": digest(body), **body}


def claim_body_from_writ(writ: dict[str, Any]) -> dict[str, Any]:
    anchor = writ.get("proofAnchor") if isinstance(writ.get("proofAnchor"), dict) else {}
    claim = writ.get("claim") if isinstance(writ.get("claim"), dict) else {}
    return {
        "claimType": claim.get("claimType"),
        "rootfieldId": normalize_hex(anchor.get("rootfieldId") or writ.get("rootfieldId")),
        "commitment": normalize_hex(anchor.get("commitment")),
        "subjectPoolId": normalize_hex(anchor.get("subjectPoolId")),
        "hookAddress": normalize_hex(anchor.get("hookAddress")),
        "boundary": "uniswap_v4_afterSwap_flowmemory_hook",
        "truthBoundary": claim.get("truthBoundary"),
    }


def verify_writ(writ: dict[str, Any]) -> dict[str, Any]:
    body = copy.deepcopy(writ)
    writ_id = body.pop("writId", None)
    claim = writ.get("claim") if isinstance(writ.get("claim"), dict) else {}
    anchor = writ.get("proofAnchor") if isinstance(writ.get("proofAnchor"), dict) else {}
    denied = set(writ.get("deniedVerbs") if isinstance(writ.get("deniedVerbs"), list) else [])

    checks = {
        "schemaMatches": writ.get("schema") == WRIT_SCHEMA,
        "writIdMatches": digest(body) == writ_id,
        "claimHashMatches": digest(claim_body_from_writ(writ)) == claim.get("claimHash"),
        "txHashOnlyInProofAnchor": "txHash" not in claim,
        "logIndexOnlyInProofAnchor": "logIndex" not in claim,
        "hasDeniedSemanticTruth": "claim_semantic_truth" in denied,
        "hasDeniedGpuAttestation": "claim_gpu_attestation" in denied,
        "hasDeniedModelCorrectness": "claim_model_correctness" in denied,
        "hasReceiptFactsForActiveWrit": writ.get("status") != "active"
        or (truthy_hex(anchor.get("txHash")) and anchor.get("logIndex") not in (None, "")),
    }
    failed = [name for name, ok in checks.items() if not ok]
    return {
        "schema": "flowmemory.axiom_writ_verification.v0",
        "status": "valid" if not failed else "invalid",
        "writId": writ_id,
        "checks": checks,
        "failedChecks": failed,
    }


def apply_writ(writ: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    verification = verify_writ(writ)
    allowed_verbs = set(writ.get("allowedVerbs") if isinstance(writ.get("allowedVerbs"), list) else [])
    denied_verbs = set(writ.get("deniedVerbs") if isinstance(writ.get("deniedVerbs"), list) else [])
    requested_verbs = [str(verb) for verb in plan.get("requestedVerbs", [])]

    verdict = {
        "schema": VERDICT_SCHEMA,
        "planId": plan.get("planId"),
        "agentId": plan.get("agentId"),
        "writId": writ.get("writId"),
        "allowed": False,
        "allowedVerbs": [],
        "deniedVerbs": [],
        "reasons": [],
        "beliefPatch": writ.get("beliefPatch") if isinstance(writ.get("beliefPatch"), dict) else None,
    }

    if verification["status"] != "valid":
        verdict["reasons"].append("writ_invalid")
    if writ.get("status") != "active":
        verdict["reasons"].append("writ_not_active")
    if plan.get("agentId") != writ.get("agentId"):
        verdict["reasons"].append("wrong_agent")
    if plan.get("rootfieldId") != writ.get("rootfieldId"):
        verdict["reasons"].append("wrong_rootfield")

    required_claims = plan.get("requiredClaimHashes", [])
    claim_hash = (writ.get("claim") or {}).get("claimHash")
    if isinstance(required_claims, list):
        for required in required_claims:
            if required != claim_hash:
                verdict["reasons"].append("missing_required_axiom")
                break

    for verb in requested_verbs:
        if verb in denied_verbs:
            verdict["deniedVerbs"].append(verb)
            verdict["reasons"].append(f"verb_explicitly_denied:{verb}")
        elif verb not in allowed_verbs:
            verdict["deniedVerbs"].append(verb)
            verdict["reasons"].append(f"verb_not_allowed:{verb}")
        else:
            verdict["allowedVerbs"].append(verb)

    if not verdict["deniedVerbs"] and not verdict["reasons"]:
        verdict["allowed"] = True
        verdict["reasons"].append("all_requested_verbs_allowed_by_axiom_writ")

    return verdict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mint, verify, and apply AxiomWrit proof-conditioned cognition objects.")
    sub = parser.add_subparsers(dest="command", required=True)

    mint = sub.add_parser("mint", help="Mint an AxiomWrit from FlowPulse evidence.")
    mint.add_argument("--flowpulse-evidence", required=True)
    mint.add_argument("--claim", required=True)
    mint.add_argument("--policy", required=True)
    mint.add_argument("--agent-id", required=True)
    mint.add_argument("--out")
    mint.add_argument("--pretty", action="store_true")

    verify = sub.add_parser("verify", help="Verify an AxiomWrit.")
    verify.add_argument("--writ", required=True)
    verify.add_argument("--pretty", action="store_true")

    apply_cmd = sub.add_parser("apply", help="Apply an AxiomWrit to an agent plan.")
    apply_cmd.add_argument("--writ", required=True)
    apply_cmd.add_argument("--plan", required=True)
    apply_cmd.add_argument("--out")
    apply_cmd.add_argument("--pretty", action="store_true")

    demo = sub.add_parser("demo", help="Run the fixture demo.")
    demo.add_argument("--pretty", action="store_true")

    return parser.parse_args()


def fixture_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "examples" / "axiom-writ"


def run_demo(pretty: bool) -> int:
    root = fixture_dir()
    evidence = read_json(root / "flowpulse-evidence.fixture.json")
    claim = read_json(root / "claim.swap-boundary.json")
    policy = read_json(root / "policy.agent.json")
    allowed_plan = read_json(root / "plan.allowed-citation.json")
    denied_plan = read_json(root / "plan.denied-action.json")
    writ = mint_writ(evidence, claim, policy, allowed_plan["agentId"])
    allowed_plan["requiredClaimHashes"] = [writ["claim"]["claimHash"]]
    denied_plan["requiredClaimHashes"] = [writ["claim"]["claimHash"]]
    payload = {
        "schema": "flowmemory.axiom_writ_demo.v0",
        "story": [
            "FlowPulse evidence enters.",
            "AxiomWrit is minted.",
            "Citation plan is allowed.",
            "Action overclaim is denied.",
            "Agent now has proof-conditioned cognition, not generic memory.",
        ],
        "writ": writ,
        "verification": verify_writ(writ),
        "allowedVerdict": apply_writ(writ, allowed_plan),
        "deniedVerdict": apply_writ(writ, denied_plan),
    }
    write_json(payload, None, pretty)
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "mint":
        writ = mint_writ(
            read_json(args.flowpulse_evidence),
            read_json(args.claim),
            read_json(args.policy),
            args.agent_id,
        )
        write_json(writ, args.out, args.pretty)
        return 0 if writ["status"] == "active" else 1
    if args.command == "verify":
        result = verify_writ(read_json(args.writ))
        write_json(result, None, args.pretty)
        return 0 if result["status"] == "valid" else 1
    if args.command == "apply":
        verdict = apply_writ(read_json(args.writ), read_json(args.plan))
        write_json(verdict, args.out, args.pretty)
        return 0 if verdict["allowed"] else 2
    if args.command == "demo":
        return run_demo(args.pretty)
    raise AssertionError(args.command)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
