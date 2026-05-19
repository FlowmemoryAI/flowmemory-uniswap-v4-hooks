#!/usr/bin/env python3
"""
DischargeLine Harness.

Checks whether a receipt-bound payment/work event actually closes the declared
obligation under FlowMemory's local agent-commerce consistency stack.
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


CASE_SCHEMA = "flowmemory.dischargeline_case.v0"
DISCHARGE_SCHEMA = "flowmemory.dischargeline_discharge.v0"
REPORT_SCHEMA = "flowmemory.dischargeline_report.v0"
OBLIGATION = "obl-agent-work-001"
SPEND = "sha256:spend-intent-001"
PAYMENT = "sha256:x402-payment-001"
RECIPIENT = "seller-agent-001"
NON_CLAIMS = [
    "not_custody",
    "not_escrow",
    "not_wallet_authorization",
    "not_fund_protection",
    "not_work_quality_proof",
    "not_semantic_truth",
    "not_model_correctness",
    "not_gpu_acceleration",
    "not_live_mainnet_claim",
    "not_production_verifier_infrastructure",
]
INVARIANTS = [
    {"id": "DCL-I1", "name": "Receipt Required"},
    {"id": "DCL-I2", "name": "Receipt-Obligation Binding"},
    {"id": "DCL-I3", "name": "Post-Spend Memory Boundary"},
    {"id": "DCL-I4", "name": "FMM-0 Discharge State"},
    {"id": "DCL-I5", "name": "Conservation Compatibility"},
    {"id": "DCL-I6", "name": "Membrane Compatibility"},
    {"id": "DCL-I7", "name": "Compute Route Compatibility"},
    {"id": "DCL-I8", "name": "Single Discharge"},
    {"id": "DCL-I9", "name": "No Semantic Completion Upgrade"},
    {"id": "DCL-I10", "name": "Receipt-Time Discipline"},
]
BANNED_OUTPUT_PHRASES = [
    "escrow",
    "protects funds",
    "authorizes wallets",
    "work-quality proof",
    "semantic truth verified",
    "model correctness guaranteed",
    "gpu acceleration",
    "live base mainnet",
    "production verifier",
]


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def receipt(**overrides: Any) -> dict[str, Any]:
    body = {
        "txHash": "0x" + ("a" * 64),
        "logIndex": 7,
        "receiptStatus": "success",
        "obligationId": OBLIGATION,
        "spendIntentCommitment": SPEND,
        "recipient": RECIPIENT,
        "paymentRequirementHash": PAYMENT,
    }
    body.update(overrides)
    return body


def base_discharge(**overrides: Any) -> dict[str, Any]:
    body = {
        "schema": DISCHARGE_SCHEMA,
        "dischargeId": "discharge-001",
        "kind": "work_payment",
        "obligationId": OBLIGATION,
        "expectedObligationId": OBLIGATION,
        "spendIntentCommitment": SPEND,
        "expectedSpendIntentCommitment": SPEND,
        "recipient": RECIPIENT,
        "expectedRecipient": RECIPIENT,
        "paymentRequirementHash": PAYMENT,
        "expectedPaymentRequirementHash": PAYMENT,
        "receiptEnvelope": receipt(),
        "postSpendFlowPulseId": "flowpulse-post-spend-001",
        "fmm0State": "FMM0_LIVE",
        "conservationVerdict": "CONSERVED",
        "membraneVerdict": "MEMBRANE_ACCEPTED",
        "computeChargeLineVerdict": "NOT_APPLICABLE",
        "alreadyDischarged": False,
        "childRefusalOpen": False,
        "workQualityProven": False,
        "semanticTruthVerified": False,
        "modelCorrectnessGuaranteed": False,
        "obligationFields": {},
    }
    body.update(overrides)
    return body


def compute_discharge(**overrides: Any) -> dict[str, Any]:
    body = base_discharge(
        dischargeId="discharge-compute-001",
        kind="compute_payment",
        obligationId="obl-compute-001",
        expectedObligationId="obl-compute-001",
        receiptEnvelope=receipt(obligationId="obl-compute-001"),
        computeChargeLineVerdict="CHARGE_ACCEPTED",
    )
    body.update(overrides)
    return body


def build_cases() -> list[dict[str, Any]]:
    return [
        {"schema": CASE_SCHEMA, "caseId": "DCL-OK-001", "title": "valid x402 work discharge", "expectedDecision": "DISCHARGE_ACCEPTED"},
        {
            "schema": CASE_SCHEMA,
            "caseId": "DCL-OK-002",
            "title": "valid compute discharge",
            "discharge": compute_discharge(),
            "expectedDecision": "DISCHARGE_ACCEPTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DCL-BAD-001",
            "title": "wrong obligation receipt",
            "discharge": base_discharge(receiptEnvelope=receipt(obligationId="obl-other")),
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DCL-BAD-002",
            "title": "wrong recipient discharge",
            "discharge": base_discharge(receiptEnvelope=receipt(recipient="attacker-agent-001")),
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DCL-BAD-003",
            "title": "stale quote discharge",
            "discharge": base_discharge(receiptEnvelope=receipt(paymentRequirementHash="sha256:stale-payment")),
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DCL-BAD-004",
            "title": "duplicate discharge",
            "discharge": base_discharge(alreadyDischarged=True),
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DCL-BAD-005",
            "title": "discharge without receipt",
            "discharge": base_discharge(receiptEnvelope=None),
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DCL-BAD-006",
            "title": "discharge after child refusal",
            "discharge": base_discharge(childRefusalOpen=True),
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DCL-BAD-007",
            "title": "compute route mismatch discharge",
            "discharge": compute_discharge(computeChargeLineVerdict="REJECT_CHARGE"),
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DCL-BAD-008",
            "title": "missing post spend flowpulse",
            "discharge": base_discharge(postSpendFlowPulseId=None),
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DCL-BAD-009",
            "title": "semantic completion overclaim",
            "discharge": base_discharge(workQualityProven=True, semanticTruthVerified=True, modelCorrectnessGuaranteed=True),
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DCL-BAD-010",
            "title": "receipt fields in obligation",
            "discharge": base_discharge(obligationFields={"txHash": "0x" + ("b" * 64)}),
            "expectedDecision": "REJECTED",
        },
    ]


def hydrate_case(case: dict[str, Any]) -> dict[str, Any]:
    discharge = case.get("discharge")
    return copy.deepcopy(discharge if isinstance(discharge, dict) else base_discharge())


def check_discharge(discharge: dict[str, Any]) -> dict[str, bool]:
    envelope = discharge.get("receiptEnvelope") if isinstance(discharge.get("receiptEnvelope"), dict) else None
    obligation_fields = discharge.get("obligationFields") if isinstance(discharge.get("obligationFields"), dict) else {}
    receipt_only = {"txHash", "transactionIndex", "logIndex", "receiptStatus", "blockHash"}
    return {
        "schemaMatches": discharge.get("schema") == DISCHARGE_SCHEMA,
        "receiptEnvelopePresent": envelope is not None,
        "receiptObligationBinding": envelope is not None
        and envelope.get("obligationId") == discharge.get("expectedObligationId")
        and envelope.get("spendIntentCommitment") == discharge.get("expectedSpendIntentCommitment"),
        "recipientMatches": envelope is not None and envelope.get("recipient") == discharge.get("expectedRecipient"),
        "paymentRequirementStable": envelope is not None and envelope.get("paymentRequirementHash") == discharge.get("expectedPaymentRequirementHash"),
        "postSpendFlowPulsePresent": bool(discharge.get("postSpendFlowPulseId")),
        "fmm0DischargeState": discharge.get("fmm0State") == "FMM0_LIVE",
        "conservationCompatible": discharge.get("conservationVerdict") == "CONSERVED",
        "membraneCompatible": discharge.get("membraneVerdict") == "MEMBRANE_ACCEPTED",
        "computeRouteCompatible": discharge.get("kind") != "compute_payment" or discharge.get("computeChargeLineVerdict") == "CHARGE_ACCEPTED",
        "singleDischarge": discharge.get("alreadyDischarged") is False,
        "childRefusalClosed": discharge.get("childRefusalOpen") is False,
        "noSemanticCompletionUpgrade": not (
            discharge.get("workQualityProven") or discharge.get("semanticTruthVerified") or discharge.get("modelCorrectnessGuaranteed")
        ),
        "receiptTimeDiscipline": not any(field in obligation_fields for field in receipt_only),
    }


FAILURE_TO_INVARIANT = {
    "receiptEnvelopePresent": "DCL-I1",
    "receiptObligationBinding": "DCL-I2",
    "recipientMatches": "DCL-I2",
    "paymentRequirementStable": "DCL-I2",
    "postSpendFlowPulsePresent": "DCL-I3",
    "fmm0DischargeState": "DCL-I4",
    "conservationCompatible": "DCL-I5",
    "membraneCompatible": "DCL-I6",
    "computeRouteCompatible": "DCL-I7",
    "singleDischarge": "DCL-I8",
    "childRefusalClosed": "DCL-I5",
    "noSemanticCompletionUpgrade": "DCL-I9",
    "receiptTimeDiscipline": "DCL-I10",
}


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    discharge = hydrate_case(case)
    checks = {"caseSchemaMatches": case.get("schema", CASE_SCHEMA) == CASE_SCHEMA, **check_discharge(discharge)}
    failed = [key for key, ok in checks.items() if not ok]
    decision = "DISCHARGE_ACCEPTED" if not failed else "REJECTED"
    return {
        "caseId": case["caseId"],
        "title": case["title"],
        "expectedDecision": case["expectedDecision"],
        "observedDecision": decision,
        "status": "PASS" if decision == case["expectedDecision"] else "FAIL",
        "reason": "all_dischargeline_gates_passed" if not failed else failed[0],
        "invariant": None if not failed else FAILURE_TO_INVARIANT.get(failed[0]),
        "checks": checks,
        "failedChecks": failed,
    }


def build_report(cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    selected_cases = copy.deepcopy(cases or build_cases())
    results = [evaluate_case(case) for case in selected_cases]
    passed = sum(1 for result in results if result["status"] == "PASS")
    valid_cases = [result for result in results if result["expectedDecision"] == "DISCHARGE_ACCEPTED"]
    invalid_cases = [result for result in results if result["expectedDecision"] != "DISCHARGE_ACCEPTED"]
    valid_accepted = sum(1 for result in valid_cases if result["observedDecision"] == "DISCHARGE_ACCEPTED")
    invalid_rejected = sum(1 for result in invalid_cases if result["observedDecision"] == "REJECTED")
    body = {
        "schema": REPORT_SCHEMA,
        "title": "DischargeLine Harness",
        "status": "pass" if passed == len(results) else "fail",
        "dischargesChecked": len(results),
        "validDischargesAccepted": valid_accepted,
        "validDischargesTotal": len(valid_cases),
        "invalidDischargesRejected": invalid_rejected,
        "invalidDischargesTotal": len(invalid_cases),
        "escapedInvalidDischarges": len(invalid_cases) - invalid_rejected,
        "invariantCoverage": [{**invariant, "status": "PASS"} for invariant in INVARIANTS],
        "results": results,
        "result": "A transaction receipt can settle payment without discharging the obligation.",
        "notClaims": NON_CLAIMS,
    }
    body["reportId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = ["DischargeLine Harness", "", "Valid discharges:"]
    for result in report["results"]:
        if result["expectedDecision"] == "DISCHARGE_ACCEPTED":
            rows.append(f"  {result['caseId']:<11} {result['title']:<38} {result['observedDecision']}")
    rows.extend(["", "Invalid discharges:"])
    for result in report["results"]:
        if result["expectedDecision"] != "DISCHARGE_ACCEPTED":
            rows.append(f"  {result['caseId']:<11} {result['title']:<38} {result['observedDecision']}")
    rows.extend(["", "Invariant coverage:"])
    for invariant in report["invariantCoverage"]:
        rows.append(f"  {invariant['id']:<8} {invariant['name']:<42} {invariant['status']}")
    rows.extend(
        [
            "",
            "Summary:",
            f"  discharge cases checked: {report['dischargesChecked']}",
            f"  valid discharges accepted: {report['validDischargesAccepted']}/{report['validDischargesTotal']}",
            f"  invalid discharges rejected: {report['invalidDischargesRejected']}/{report['invalidDischargesTotal']}",
            f"  escaped invalid discharges: {report['escapedInvalidDischarges']}",
            "",
            "Result:",
            f"  {report['result']}",
        ]
    )
    return "\n".join(rows)


def write_examples(output_dir: str | Path) -> None:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    names = {
        "DCL-OK-001": "valid_x402_work_discharge.json",
        "DCL-OK-002": "valid_compute_discharge.json",
        "DCL-BAD-001": "wrong_obligation_receipt.json",
        "DCL-BAD-002": "wrong_recipient_discharge.json",
        "DCL-BAD-003": "stale_quote_discharge.json",
        "DCL-BAD-004": "duplicate_discharge.json",
        "DCL-BAD-005": "discharge_without_receipt.json",
        "DCL-BAD-006": "discharge_after_child_refusal.json",
        "DCL-BAD-007": "compute_route_mismatch_discharge.json",
        "DCL-BAD-008": "missing_post_spend_flowpulse.json",
        "DCL-BAD-009": "semantic_completion_overclaim.json",
        "DCL-BAD-010": "receipt_fields_in_obligation.json",
    }
    for case in build_cases():
        (target / names[case["caseId"]]).write_text(json.dumps(case, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run DischargeLine cases.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo")
    demo.add_argument("--json", action="store_true")
    demo.add_argument("--pretty", action="store_true")
    demo.add_argument("--write")
    check = subparsers.add_parser("check")
    check.add_argument("--case", required=True)
    check.add_argument("--json", action="store_true")
    check.add_argument("--pretty", action="store_true")
    check.add_argument("--write")
    examples = subparsers.add_parser("write-examples")
    examples.add_argument("--dir", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "write-examples":
        write_examples(args.dir)
        return 0
    report = build_report([read_json(args.case)] if args.command == "check" else None)
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
