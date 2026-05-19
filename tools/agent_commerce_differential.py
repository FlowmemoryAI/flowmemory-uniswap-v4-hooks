#!/usr/bin/env python3
"""
Agent Commerce Differential Harness.

Compares ordinary agent-commerce rails against FlowMemory memory consistency.
The harness is local deterministic conformance only. It does not implement
wallets, x402, custody, escrow, or production verifier infrastructure.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore


CASE_SCHEMA = "flowmemory.agent_commerce_differential_case.v0"
REPORT_SCHEMA = "flowmemory.agent_commerce_differential_report.v0"
ACCEPTED_FLOWMEMORY_DECISIONS = {
    "SPENDLINE_ACCEPTED",
    "DUPLEXLINE_ACCEPTED",
    "CONSERVATION_ACCEPTED",
    "MEMBRANE_ACCEPTED",
    "DISCHARGE_ACCEPTED",
    "CHARGE_ACCEPTED",
    "NOT_APPLICABLE",
}
NON_CLAIMS = [
    "not_a_real_wallet_implementation",
    "not_x402_implementation",
    "not_custody",
    "not_escrow",
    "not_wallet_authorization",
    "not_fund_protection",
    "not_semantic_truth",
    "not_model_correctness",
    "not_gpu_acceleration",
    "not_live_mainnet_claim",
    "not_production_verifier_infrastructure",
]
BANNED_OUTPUT_PHRASES = [
    "custodies funds",
    "escrows payment",
    "authorizes wallets",
    "protects funds",
    "semantic truth verified",
    "model correctness guaranteed",
    "accelerates gpu",
    "base mainnet live",
    "production verifier is live",
]


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def ordinary_rails(**overrides: Any) -> dict[str, bool]:
    body = {
        "walletSignatureValid": True,
        "spendPermissionInScope": True,
        "sessionKeyInScope": True,
        "x402PaymentRequirementSatisfied": True,
        "identityPresent": True,
        "receiptObservedByIndexer": True,
        "cacheFingerprintMatches": True,
    }
    body.update(overrides)
    return body


def flowmemory_checks(**overrides: Any) -> dict[str, Any]:
    body = {
        "spendLineDecision": "SPENDLINE_ACCEPTED",
        "duplexLineDecision": "DUPLEXLINE_ACCEPTED",
        "commerceConservationDecision": "CONSERVATION_ACCEPTED",
        "obligationMembraneDecision": "MEMBRANE_ACCEPTED",
        "dischargeLineDecision": "DISCHARGE_ACCEPTED",
        "computeChargeLineDecision": "CHARGE_ACCEPTED",
        "fmm0Faults": [],
    }
    body.update(overrides)
    return body


def bad_case(case_id: str, name: str, reason: str, fault: str, **overrides: Any) -> dict[str, Any]:
    checks = flowmemory_checks(fmm0Faults=[fault], **overrides)
    return {
        "schema": CASE_SCHEMA,
        "caseId": case_id,
        "name": name,
        "description": f"Ordinary rails accept the action surface, but FlowMemory rejects: {reason}.",
        "ordinaryRails": ordinary_rails(),
        "flowmemoryChecks": checks,
        "expected": {
            "ordinaryRailDecision": "ACCEPT",
            "flowmemoryDecision": "REJECT",
            "differentialReason": reason,
        },
        "notClaims": NON_CLAIMS,
    }


def build_cases() -> list[dict[str, Any]]:
    return [
        {
            "schema": CASE_SCHEMA,
            "caseId": "DIF-OK-001",
            "name": "valid_all_rails_and_fmm0",
            "description": "Ordinary rails accept and FlowMemory accepts the same admissible machine history.",
            "ordinaryRails": ordinary_rails(),
            "flowmemoryChecks": flowmemory_checks(),
            "expected": {
                "ordinaryRailDecision": "ACCEPT",
                "flowmemoryDecision": "ACCEPT",
                "differentialReason": "all_rails_and_fmm0_consistent",
            },
            "notClaims": NON_CLAIMS,
        },
        bad_case(
            "DIF-BAD-001",
            "valid_signature_stale_memory_head",
            "valid_signature_does_not_imply_memory_currentness",
            "stale_rootfield_head",
            spendLineDecision="SPENDLINE_REJECTED",
            duplexLineDecision="NOT_APPLICABLE",
            commerceConservationDecision="NOT_APPLICABLE",
            obligationMembraneDecision="NOT_APPLICABLE",
            dischargeLineDecision="NOT_APPLICABLE",
            computeChargeLineDecision="NOT_APPLICABLE",
        ),
        bad_case(
            "DIF-BAD-002",
            "x402_payment_wrong_obligation",
            "payment_settlement_is_not_obligation_discharge",
            "obligation_receipt_mismatch",
            dischargeLineDecision="DISCHARGE_REJECTED",
        ),
        bad_case(
            "DIF-BAD-003",
            "identity_valid_payee_spine_broken",
            "identity_does_not_guarantee_payee_work_binding",
            "payee_spine_broken",
            duplexLineDecision="DUPLEXLINE_REJECTED",
            obligationMembraneDecision="MEMBRANE_REJECTED",
        ),
        bad_case(
            "DIF-BAD-004",
            "spend_permission_in_scope_duplicate_intent",
            "permission_scope_does_not_catch_declared_intent_replay",
            "duplicate_intent_commitment",
            spendLineDecision="SPENDLINE_REJECTED",
        ),
        bad_case(
            "DIF-BAD-005",
            "cache_fingerprint_match_memory_inconsistent",
            "compute_reuse_needs_memory_consistency_not_only_fingerprint_similarity",
            "source_artifact_not_fmm0_conforming",
            computeChargeLineDecision="CHARGE_REJECTED",
        ),
        bad_case(
            "DIF-BAD-006",
            "indexer_receipt_missing_post_spend_flowpulse",
            "observed_receipt_does_not_close_memory_obligation",
            "missing_post_spend_flowpulse",
            dischargeLineDecision="DISCHARGE_REJECTED",
        ),
        bad_case(
            "DIF-BAD-007",
            "session_key_in_scope_axiompatch_downgrade",
            "authorization_scope_and_memory_state_admissibility_are_different",
            "axiompatch_downgrade_ignored",
            spendLineDecision="SPENDLINE_REJECTED",
        ),
        bad_case(
            "DIF-BAD-008",
            "compute_payment_receipt_route_mismatch",
            "paying_for_compute_is_not_the_same_as_matching_the_declared_route",
            "compute_route_discharge_mismatch",
            computeChargeLineDecision="CHARGE_REJECTED",
            dischargeLineDecision="DISCHARGE_REJECTED",
        ),
        bad_case(
            "DIF-BAD-009",
            "child_permission_valid_refusal_swallowed",
            "delegated_obligations_must_propagate_refusal_state",
            "child_refusal_not_propagated",
            obligationMembraneDecision="MEMBRANE_REJECTED",
            commerceConservationDecision="CONSERVATION_REJECTED",
        ),
    ]


def ordinary_decision(rails: dict[str, Any]) -> str:
    return "ACCEPT" if rails and all(value is True for value in rails.values()) else "REJECT"


def flowmemory_decision(checks: dict[str, Any]) -> str:
    decisions = [value for key, value in checks.items() if key.endswith("Decision")]
    faults = checks.get("fmm0Faults")
    no_faults = isinstance(faults, list) and not faults
    accepted = all(decision in ACCEPTED_FLOWMEMORY_DECISIONS for decision in decisions)
    return "ACCEPT" if accepted and no_faults else "REJECT"


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    selected = copy.deepcopy(case)
    rails = selected.get("ordinaryRails") if isinstance(selected.get("ordinaryRails"), dict) else {}
    checks = selected.get("flowmemoryChecks") if isinstance(selected.get("flowmemoryChecks"), dict) else {}
    expected = selected.get("expected") if isinstance(selected.get("expected"), dict) else {}
    ordinary = ordinary_decision(rails)
    fmm0 = flowmemory_decision(checks)
    expected_ordinary = expected.get("ordinaryRailDecision")
    expected_fmm0 = expected.get("flowmemoryDecision")
    differential = ordinary == "ACCEPT" and fmm0 == "REJECT"
    return {
        "caseId": selected["caseId"],
        "name": selected["name"],
        "ordinaryRailDecision": ordinary,
        "flowmemoryDecision": fmm0,
        "expectedOrdinaryRailDecision": expected_ordinary,
        "expectedFlowmemoryDecision": expected_fmm0,
        "status": "PASS" if ordinary == expected_ordinary and fmm0 == expected_fmm0 else "FAIL",
        "differential": differential,
        "reason": expected.get("differentialReason", "not_declared"),
        "faults": checks.get("fmm0Faults", []),
        "notClaims": selected.get("notClaims", []),
    }


def build_report(cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    selected_cases = copy.deepcopy(cases or build_cases())
    results = [evaluate_case(case) for case in selected_cases]
    passed = sum(1 for result in results if result["status"] == "PASS")
    valid_cases = [result for result in results if result["expectedFlowmemoryDecision"] == "ACCEPT"]
    differential_cases = [result for result in results if result["expectedFlowmemoryDecision"] == "REJECT"]
    valid_accepted = sum(
        1
        for result in valid_cases
        if result["ordinaryRailDecision"] == "ACCEPT" and result["flowmemoryDecision"] == "ACCEPT"
    )
    differential_caught = sum(1 for result in differential_cases if result["differential"])
    body = {
        "schema": REPORT_SCHEMA,
        "title": "Agent Commerce Differential Harness",
        "status": "pass" if passed == len(results) else "fail",
        "casesChecked": len(results),
        "validCasesAcceptedByBoth": valid_accepted,
        "validCasesTotal": len(valid_cases),
        "differentialFailuresCaught": differential_caught,
        "differentialFailuresTotal": len(differential_cases),
        "unsafeHistoriesAcceptedByOrdinaryBaselineOnly": differential_caught,
        "escapedUnsafeHistories": len(differential_cases) - differential_caught,
        "results": results,
        "result": "Ordinary rails can accept an action surface while FlowMemory rejects the machine history.",
        "notClaims": NON_CLAIMS,
    }
    body["reportId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = ["Agent Commerce Differential Harness", "", "Valid case:"]
    for result in report["results"]:
        if result["expectedFlowmemoryDecision"] == "ACCEPT":
            rows.append(
                f"  {result['caseId']:<11} {result['name']:<48} "
                f"ORDINARY_{result['ordinaryRailDecision']:<6} FMM0_{result['flowmemoryDecision']:<6} {result['status']}"
            )
    rows.extend(["", "Differential cases:"])
    for result in report["results"]:
        if result["expectedFlowmemoryDecision"] == "REJECT":
            rows.append(
                f"  {result['caseId']:<11} {result['name']:<48} "
                f"ORDINARY_{result['ordinaryRailDecision']:<6} FMM0_{result['flowmemoryDecision']:<6} "
                f"{'CAUGHT' if result['differential'] else 'ESCAPED'}"
            )
    rows.extend(
        [
            "",
            "Summary:",
            f"  cases checked: {report['casesChecked']}",
            f"  valid cases accepted by both: {report['validCasesAcceptedByBoth']}/{report['validCasesTotal']}",
            f"  differential failures caught by FlowMemory: {report['differentialFailuresCaught']}/{report['differentialFailuresTotal']}",
            f"  unsafe histories accepted by ordinary baseline only: {report['unsafeHistoriesAcceptedByOrdinaryBaselineOnly']}",
            f"  escaped unsafe histories: {report['escapedUnsafeHistories']}",
            "",
            "Result:",
            f"  {report['result']}",
            "",
            "Non-claims:",
            "  local baseline simulator only; no custody, no escrow, no wallet authorization, no fund protection, no semantic truth, no model correctness, no GPU acceleration, no live mainnet claim, no production verifier infrastructure.",
        ]
    )
    return "\n".join(rows)


def write_examples(output_dir: str | Path) -> None:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    cases = build_cases()
    (target / "differential-cases.json").write_text(json.dumps(cases, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for case in cases:
        (target / f"{case['caseId'].lower()}.json").write_text(json.dumps(case, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Agent Commerce Differential Harness cases.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo")
    demo.add_argument("--json", action="store_true")
    demo.add_argument("--pretty", action="store_true")
    demo.add_argument("--write")
    run = subparsers.add_parser("run")
    run.add_argument("--cases", required=True)
    run.add_argument("--json", action="store_true")
    run.add_argument("--pretty", action="store_true")
    run.add_argument("--write")
    examples = subparsers.add_parser("write-examples")
    examples.add_argument("--dir", required=True)
    return parser.parse_args()


def load_cases(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object or array")
    return [payload]


def main() -> int:
    args = parse_args()
    if args.command == "write-examples":
        write_examples(args.dir)
        return 0
    report = build_report(load_cases(args.cases) if args.command == "run" else None)
    text = render_report(report)
    if args.write:
        output_path = Path(args.write)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(text)
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
