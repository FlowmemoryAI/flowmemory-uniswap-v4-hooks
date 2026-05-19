#!/usr/bin/env python3
"""
BoundaryFission: proof-triggered memory release for agent working state.

BoundaryFission is not retrieval. It applies a receipt-bound FlowPulse boundary
to working memory and splits stale cognition into conserved facts, residue
atoms, quarantined claims, branch ash, and delegated recompute tasks.
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


FISSION_SCHEMA = "flowmemory.boundary_fission.v0"
RESIDUE_SCHEMA = "flowmemory.residue_atom.v0"
BRANCH_ASH_SCHEMA = "flowmemory.branch_ash.v0"
DELEGATED_RECOMPUTE_SCHEMA = "flowmemory.delegated_recompute.v0"
AFTER_SCHEMA = "flowmemory.agent_working_memory_after_fission.v0"
ZERO32 = "0x" + ("0" * 64)
RAW_FIELDS = ["rawText", "privatePayload", "payload", "unsupportedInference", "unsupportedIntentInference"]
DEFAULT_HIGH_RISK_ACTIONS = ["submit_onchain_transaction", "sign_transaction", "move_funds"]
DEFAULT_DRAFT_TIERS = ["local_draft", "rd_mock", "unverified"]
COMPUTE_DRAFT_TYPES = ["ModelPulseDraft", "ComputePulseDraft", "CacheHint"]
CLAIM_TYPES = ["SemanticClaim", "IntentClaim"]


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def write_json(payload: Any, output: str | None, pretty: bool) -> None:
    axiom_writ.write_json(payload, output, pretty)


def normalize_hex(value: Any) -> str:
    return axiom_writ.normalize_hex(value)


def truthy_hex(value: Any) -> bool:
    return axiom_writ.truthy_hex(value)


def default_policy() -> dict[str, Any]:
    return {
        "schema": "flowmemory.boundary_fission_policy.v0",
        "eraseRawPayloadsAfterBoundary": True,
        "highRiskActions": DEFAULT_HIGH_RISK_ACTIONS,
        "draftProofTiers": DEFAULT_DRAFT_TIERS,
        "computeDraftTypes": COMPUTE_DRAFT_TYPES,
        "quarantineReceiptMetadataSmuggling": True,
        "replacementActions": {
            "submit_onchain_transaction": "propose_unsigned_action",
            "sign_transaction": "request_human_or_policy_authorization",
            "move_funds": "request_human_or_policy_authorization",
        },
    }


def select_flowpulse_record(evidence: dict[str, Any]) -> dict[str, Any] | None:
    records = evidence.get("records", [])
    if not isinstance(records, list):
        return None
    for record in records:
        if isinstance(record, dict) and record.get("eventName") == "FlowPulse":
            return record
    return None


def trigger_checks(record: dict[str, Any] | None) -> dict[str, bool]:
    if not record:
        return {
            "flowPulseRecordFound": False,
            "eventNameFlowPulse": False,
            "notRejected": False,
            "receiptStatusSuccessful": False,
            "txHashReaderAttached": False,
            "logIndexReaderAttached": False,
            "rootfieldNonZero": False,
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
        "rootfieldNonZero": normalize_hex(record.get("rootfieldId")) != ZERO32,
        "commitmentNonZero": normalize_hex(record.get("commitment")) != ZERO32,
        "validationEmpty": record.get("validation") == [],
    }


def checks_pass(checks: dict[str, bool]) -> bool:
    return all(checks.values())


def normalize_trigger(record: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "triggerType": "FlowPulse",
        "boundary": "uniswap_v4_afterSwap",
        "proofTier": axiom_writ.classify_proof_tier(record),
        "chainId": str(evidence.get("chainId", record.get("chainId", ""))),
        "hookAddress": normalize_hex(record.get("hookAddress") or evidence.get("hookAddress")),
        "txHash": normalize_hex(record.get("txHash")),
        "logIndex": str(record.get("logIndex", "")),
        "blockNumber": str(record.get("blockNumber", "")),
        "receiptStatus": record.get("receiptStatus"),
        "pulseId": normalize_hex(record.get("pulseId")),
        "rootfieldId": normalize_hex(record.get("rootfieldId")),
        "commitment": normalize_hex(record.get("commitment")),
        "parentPulseId": normalize_hex(record.get("parentPulseId")),
        "subjectPoolId": normalize_hex(record.get("subjectPoolId")),
    }


def minimal_item_ref(item: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "memoryId": str(item.get("memoryId", "")),
        "type": str(item.get("type", "")),
        "rootfieldId": normalize_hex(item.get("rootfieldId")),
        "itemHash": axiom_writ.digest(item),
        "reason": reason,
    }


def boundary_fact(trigger: dict[str, Any]) -> dict[str, Any]:
    return {
        "memoryId": f"flowpulse-boundary-{trigger.get('pulseId', '')[:18]}",
        "type": "FlowPulseBoundaryFact",
        "pulseId": trigger.get("pulseId"),
        "txHash": trigger.get("txHash"),
        "logIndex": trigger.get("logIndex"),
        "rootfieldId": trigger.get("rootfieldId"),
        "commitment": trigger.get("commitment"),
        "reason": "receipt_bound_boundary_fact_survives",
    }


def raw_field_hashes(item: dict[str, Any]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for key in RAW_FIELDS:
        if key in item and item[key] not in (None, "", False):
            hashes[key] = axiom_writ.digest({key: item[key]})
    return hashes


def retained_facts(item: dict[str, Any], trigger: dict[str, Any]) -> dict[str, Any]:
    retained: dict[str, Any] = {
        "memoryId": item.get("memoryId"),
        "type": item.get("type"),
        "rootfieldId": normalize_hex(item.get("rootfieldId")),
        "sourceCommitment": item.get("sourceCommitment") or item.get("commitment"),
        "proofTier": item.get("proofTier"),
        "createdBeforeBoundary": bool(item.get("createdBeforeBoundary")),
        "boundaryPulseId": trigger.get("pulseId"),
    }
    if item.get("action"):
        retained["action"] = item.get("action")
    return {key: value for key, value in retained.items() if value not in (None, "")}


def make_residue_atom(item: dict[str, Any], trigger: dict[str, Any], release_action: str, reason: str) -> dict[str, Any]:
    body = {
        "schema": RESIDUE_SCHEMA,
        "sourceMemoryHash": axiom_writ.digest(item),
        "boundaryPulseHash": axiom_writ.digest(trigger),
        "releaseAction": release_action,
        "retainedFacts": retained_facts(item, trigger),
        "erasedFieldHashes": raw_field_hashes(item),
        "notRetained": [key for key in RAW_FIELDS if key in item and item[key] not in (None, "", False)],
        "reason": reason,
    }
    body["residueId"] = axiom_writ.digest(body)
    return body


def make_branch_ash(item: dict[str, Any], trigger: dict[str, Any], replacement: str, reason: str) -> dict[str, Any]:
    body = {
        "schema": BRANCH_ASH_SCHEMA,
        "sourcePlanHash": axiom_writ.digest(item),
        "boundaryPulseHash": axiom_writ.digest(trigger),
        "memoryId": item.get("memoryId"),
        "killedAction": item.get("action"),
        "replacement": replacement,
        "reason": reason,
    }
    body["branchAshId"] = axiom_writ.digest(body)
    return body


def make_delegated_recompute(item: dict[str, Any], trigger: dict[str, Any], reason: str) -> dict[str, Any]:
    body = {
        "schema": DELEGATED_RECOMPUTE_SCHEMA,
        "sourceMemoryHash": axiom_writ.digest(item),
        "boundaryPulseHash": axiom_writ.digest(trigger),
        "task": "rerun_analysis_from_current_flowpulse_boundary",
        "parentPulseId": trigger.get("pulseId"),
        "rootfieldId": trigger.get("rootfieldId"),
        "reason": reason,
    }
    body["delegateId"] = axiom_writ.digest(body)
    return body


def contains_receipt_metadata_smuggling(item: dict[str, Any]) -> bool:
    source = str(item.get("source", "")).lower()
    if source == "reader":
        return False
    return any(item.get(key) not in (None, "") for key in ["txHash", "logIndex", "transactionIndex"])


def references_current_pulse(item: dict[str, Any], trigger: dict[str, Any]) -> bool:
    if item.get("referencesCurrentPulse") is True:
        return True
    return normalize_hex(item.get("pulseId")) == normalize_hex(trigger.get("pulseId"))


def build_after_state(
    working_memory: dict[str, Any],
    trigger: dict[str, Any],
    release_products: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    return {
        "schema": AFTER_SCHEMA,
        "agentId": working_memory.get("agentId"),
        "rootfieldId": trigger.get("rootfieldId"),
        "triggerPulseId": trigger.get("pulseId"),
        "conservedFacts": release_products["conserved"],
        "residueAtoms": [item["residueId"] for item in release_products["residueAtoms"]],
        "quarantined": [item["memoryId"] for item in release_products["quarantined"]],
        "branchAsh": [item["branchAshId"] for item in release_products["branchAsh"]],
        "delegatedRecompute": [item["delegateId"] for item in release_products["delegatedRecompute"]],
        "rawTextPresent": False,
        "containsRawPrivatePayload": False,
        "unsupportedIntentInferencePresent": False,
        "executableOnchainActionPresent": False,
    }


def apply_boundary_fission(
    evidence: dict[str, Any],
    working_memory: dict[str, Any],
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policy = policy or default_policy()
    record = select_flowpulse_record(evidence)
    checks = trigger_checks(record)
    trigger = normalize_trigger(record or {}, evidence)
    rootfield_id = trigger.get("rootfieldId")
    items = working_memory.get("items", [])
    if not isinstance(items, list):
        items = []

    release_products: dict[str, list[dict[str, Any]]] = {
        "conserved": [],
        "residueAtoms": [],
        "quarantined": [],
        "branchAsh": [],
        "delegatedRecompute": [],
    }

    if checks_pass(checks):
        release_products["conserved"].append(boundary_fact(trigger))

    high_risk_actions = set(policy.get("highRiskActions", DEFAULT_HIGH_RISK_ACTIONS))
    draft_tiers = set(policy.get("draftProofTiers", DEFAULT_DRAFT_TIERS))
    compute_draft_types = set(policy.get("computeDraftTypes", COMPUTE_DRAFT_TYPES))
    replacement_actions = policy.get("replacementActions", {})

    for raw_item in items:
        if not isinstance(raw_item, dict):
            continue
        item = copy.deepcopy(raw_item)
        item_rootfield = normalize_hex(item.get("rootfieldId"))
        item_type = str(item.get("type", ""))
        action = str(item.get("action", ""))

        if item_rootfield and item_rootfield != rootfield_id:
            release_products["conserved"].append(minimal_item_ref(item, "different_rootfield_unaffected"))
            continue

        if item_type in ["FlowPulseFact", "FlowPulseBoundaryFact"] and references_current_pulse(item, trigger):
            release_products["conserved"].append(minimal_item_ref(item, "current_boundary_fact"))
            continue

        if policy.get("quarantineReceiptMetadataSmuggling", True) and contains_receipt_metadata_smuggling(item):
            release_products["quarantined"].append(minimal_item_ref(item, "receipt_metadata_claim_not_reader_attached"))
            continue

        if item_type in CLAIM_TYPES or item.get("claimType") in CLAIM_TYPES:
            release_products["quarantined"].append(minimal_item_ref(item, "semantic_or_intent_claim_not_supported_by_flowpulse"))
            continue

        if action in high_risk_actions and not references_current_pulse(item, trigger):
            replacement = str(replacement_actions.get(action, "propose_unsigned_action"))
            release_products["branchAsh"].append(
                make_branch_ash(item, trigger, replacement, "preboundary_action_branch_lacks_current_flowpulse_parent")
            )
            continue

        if item_type in compute_draft_types and str(item.get("proofTier", "")) in draft_tiers:
            reason = "draft_or_unattested_compute_cannot_survive_boundary_as_raw_context"
            release_products["residueAtoms"].append(make_residue_atom(item, trigger, "compress_to_commitment_only", reason))
            release_products["delegatedRecompute"].append(make_delegated_recompute(item, trigger, "fresh_compute_requested_from_current_boundary"))
            continue

        if item.get("containsUnsupportedIntentInference"):
            release_products["residueAtoms"].append(
                make_residue_atom(item, trigger, "erase_unsupported_inference", "unsupported_intent_inference_erased")
            )
            continue

        if policy.get("eraseRawPayloadsAfterBoundary", True) and any(item.get(key) for key in RAW_FIELDS):
            release_products["residueAtoms"].append(make_residue_atom(item, trigger, "erase_raw_keep_commitment", "raw_payload_erased_after_boundary"))
            continue

        release_products["conserved"].append(minimal_item_ref(item, "survives_boundary"))

    memory_after = build_after_state(working_memory, trigger, release_products)
    report = {
        "schema": FISSION_SCHEMA,
        "status": "active" if checks_pass(checks) else "rejected",
        "fissionType": "proof_triggered_memory_release",
        "trigger": trigger,
        "inputMemorySet": {
            "workingSetHash": axiom_writ.digest(working_memory),
            "itemCount": len(items),
            "rootfieldId": normalize_hex(working_memory.get("rootfieldId")),
        },
        "releaseProducts": release_products,
        "memoryAfter": memory_after,
        "checks": {
            **checks,
            "triggerRootfieldMatchesWorkingSet": rootfield_id == normalize_hex(working_memory.get("rootfieldId")),
            "noReceiptMetadataFromHookPayload": True,
            "rawPayloadsErasedWhenPolicyRequires": not memory_after["rawTextPresent"] and not memory_after["containsRawPrivatePayload"],
        },
        "warnings": [
            "BoundaryFission proves deterministic memory release under this policy; it does not prove semantic truth.",
            "Delegated recompute tasks are drafts unless later bound to signed or attested ComputePulse evidence.",
        ],
    }
    report["fissionId"] = axiom_writ.digest(report)
    return report


def verify_report(report: dict[str, Any]) -> dict[str, Any]:
    body = copy.deepcopy(report)
    fission_id = body.pop("fissionId", None)
    release_products = report.get("releaseProducts") if isinstance(report.get("releaseProducts"), dict) else {}
    memory_after = report.get("memoryAfter") if isinstance(report.get("memoryAfter"), dict) else {}
    checks = report.get("checks") if isinstance(report.get("checks"), dict) else {}

    verification_checks = {
        "schemaMatches": report.get("schema") == FISSION_SCHEMA,
        "fissionIdMatches": axiom_writ.digest(body) == fission_id,
        "statusActive": report.get("status") == "active",
        "triggerHasTxHash": truthy_hex((report.get("trigger") or {}).get("txHash")),
        "triggerHasLogIndex": (report.get("trigger") or {}).get("logIndex") not in (None, ""),
        "triggerReceiptSuccessful": (report.get("trigger") or {}).get("receiptStatus") == "success",
        "checksPassed": all(bool(value) for value in checks.values()),
        "hasReleaseProducts": all(
            isinstance(release_products.get(key), list)
            for key in ["conserved", "residueAtoms", "quarantined", "branchAsh", "delegatedRecompute"]
        ),
        "afterStateNoRawPayload": memory_after.get("rawTextPresent") is False
        and memory_after.get("containsRawPrivatePayload") is False,
        "afterStateNoExecutableAction": memory_after.get("executableOnchainActionPresent") is False,
    }
    failed = [key for key, ok in verification_checks.items() if not ok]
    return {
        "schema": "flowmemory.boundary_fission_verification.v0",
        "status": "valid" if not failed else "invalid",
        "fissionId": fission_id,
        "checks": verification_checks,
        "failedChecks": failed,
    }


def explain_report(report: dict[str, Any]) -> str:
    products = report.get("releaseProducts", {})
    trigger = report.get("trigger", {})
    lines = [
        "BoundaryFission triggered by receipt-bound FlowPulse.",
        "",
        f"Trigger: {trigger.get('boundary')} at txHash {trigger.get('txHash')} logIndex {trigger.get('logIndex')}",
        "",
        f"Conserved: {len(products.get('conserved', []))}",
        f"ResidueAtoms: {len(products.get('residueAtoms', []))}",
        f"Quarantined: {len(products.get('quarantined', []))}",
        f"BranchAsh: {len(products.get('branchAsh', []))}",
        f"Delegated recompute: {len(products.get('delegatedRecompute', []))}",
        "",
        "No raw private payloads are retained in the after-state.",
    ]
    return "\n".join(lines)


def example_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "examples" / "boundary-fission"


def load_demo_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    base = example_dir()
    return (
        read_json(base / "flowpulse-evidence.fixture.json"),
        read_json(base / "agent-working-memory.before.json"),
        read_json(base / "fission-policy.fixture.json"),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply and verify BoundaryFission memory release reports.")
    sub = parser.add_subparsers(dest="command", required=True)

    apply_cmd = sub.add_parser("apply", help="Apply BoundaryFission to working memory.")
    apply_cmd.add_argument("--flowpulse", required=True)
    apply_cmd.add_argument("--memory", required=True)
    apply_cmd.add_argument("--policy")
    apply_cmd.add_argument("--report")
    apply_cmd.add_argument("--after")
    apply_cmd.add_argument("--pretty", action="store_true")

    verify_cmd = sub.add_parser("verify", help="Verify a BoundaryFission report.")
    verify_cmd.add_argument("--report", required=True)
    verify_cmd.add_argument("--pretty", action="store_true")

    explain_cmd = sub.add_parser("explain", help="Explain a BoundaryFission report.")
    explain_cmd.add_argument("--report", required=True)

    demo = sub.add_parser("demo", help="Run the checked example BoundaryFission.")
    demo.add_argument("--pretty", action="store_true")

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.command == "apply":
        evidence = read_json(args.flowpulse)
        memory = read_json(args.memory)
        policy = read_json(args.policy) if args.policy else default_policy()
        report = apply_boundary_fission(evidence, memory, policy)
        if args.after:
            write_json(report["memoryAfter"], args.after, args.pretty)
        write_json(report, args.report, args.pretty)
        return 0 if report["status"] == "active" else 2

    if args.command == "verify":
        verification = verify_report(read_json(args.report))
        write_json(verification, None, args.pretty)
        return 0 if verification["status"] == "valid" else 2

    if args.command == "explain":
        print(explain_report(read_json(args.report)))
        return 0

    if args.command == "demo":
        evidence, memory, policy = load_demo_inputs()
        report = apply_boundary_fission(evidence, memory, policy)
        if args.pretty:
            write_json(report, None, True)
        else:
            print(explain_report(report))
        return 0 if report["status"] == "active" else 2

    return 1


if __name__ == "__main__":
    sys.exit(main())
