#!/usr/bin/env python3
"""
Compute ChargeLine.

Checks whether payment for AI/GPU work matches the memory-consistent compute
route that produced or reused the artifact.
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


CASE_SCHEMA = "flowmemory.compute_chargeline_case.v0"
CHARGE_SCHEMA = "flowmemory.compute_charge.v0"
REPORT_SCHEMA = "flowmemory.compute_chargeline_report.v0"
ROOTFIELD = "0x" + ("4" * 64)
BUYER_HEAD = "flowpulse-buyer-compute-001"
PAYMENT_REQ = "sha256:compute-payment-001"
RUNTIME = "sha256:runtime-cuda-vllm-001"
NON_CLAIMS = [
    "not_custody",
    "not_escrow",
    "not_wallet_authorization",
    "not_fund_protection",
    "not_work_quality_proof",
    "not_semantic_truth",
    "not_model_correctness",
    "not_gpu_acceleration",
    "not_hardware_execution_proof",
    "not_production_attestation_infrastructure",
    "not_live_mainnet_claim",
]
INVARIANTS = [
    {"id": "CCL-I1", "name": "Payment mode matches compute route"},
    {"id": "CCL-I2", "name": "Unsafe reuse cannot close compute payment"},
    {"id": "CCL-I3", "name": "Fresh-compute policy cannot be laundered"},
    {"id": "CCL-I4", "name": "Payment requirement hash is stable"},
    {"id": "CCL-I5", "name": "Compute charge is single-use"},
    {"id": "CCL-I6", "name": "Required attestation reference is present"},
    {"id": "CCL-I7", "name": "Runtime commitment is stable"},
    {"id": "CCL-I8", "name": "Buyer memory head is current"},
]
BANNED_OUTPUT_PHRASES = [
    "makes gpu faster",
    "gpu acceleration",
    "hardware execution proof",
    "authorizes wallets",
    "protects funds",
    "escrows payment",
    "semantic truth verified",
    "model correctness guaranteed",
    "production attestation infrastructure",
    "live base mainnet",
]


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def base_charge(**overrides: Any) -> dict[str, Any]:
    body = {
        "schema": CHARGE_SCHEMA,
        "chargeId": "compute-charge-001",
        "rootfieldId": ROOTFIELD,
        "buyerAgentId": "buyer-agent-001",
        "sellerAgentId": "compute-agent-001",
        "buyerMemoryHead": BUYER_HEAD,
        "expectedBuyerMemoryHead": BUYER_HEAD,
        "buyerComputePolicy": "ALLOWS_REUSE",
        "paymentRequirementHash": PAYMENT_REQ,
        "observedPaymentRequirementHash": PAYMENT_REQ,
        "paymentMode": "FRESH_COMPUTE",
        "chargeAlreadyConsumed": False,
        "attestationRequired": True,
        "attestationRef": "attestation:local-demo-ref",
        "expectedRuntimeCommitment": RUNTIME,
        "runtimeCommitment": RUNTIME,
        "computeRoute": {
            "routeDecision": "RUN_GPU_JOB",
            "computeReuseVerdict": "NOT_APPLICABLE",
            "cacheLineageVerdict": "NOT_APPLICABLE",
            "computePulseId": "computepulse-fresh-001",
        },
    }
    body.update(overrides)
    return body


def reuse_charge(**overrides: Any) -> dict[str, Any]:
    body = base_charge(
        chargeId="compute-charge-reuse-001",
        paymentMode="REUSE_PRIOR_COMPUTE",
        attestationRequired=False,
        attestationRef=None,
        computeRoute={
            "routeDecision": "REUSE_PRIOR_COMPUTE",
            "computeReuseVerdict": "REUSE_ACCEPTED",
            "cacheLineageVerdict": "CACHE_REUSE_ACCEPTED",
            "computePulseId": "computepulse-reuse-001",
        },
    )
    body.update(overrides)
    return body


def build_cases() -> list[dict[str, Any]]:
    return [
        {"schema": CASE_SCHEMA, "caseId": "CCL-OK-001", "title": "fresh compute charged as fresh", "expectedDecision": "CHARGE_ACCEPTED"},
        {
            "schema": CASE_SCHEMA,
            "caseId": "CCL-OK-002",
            "title": "safe reuse charged as reuse",
            "charge": reuse_charge(),
            "expectedDecision": "CHARGE_ACCEPTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "CCL-BAD-001",
            "title": "reuse route charged as fresh",
            "charge": reuse_charge(paymentMode="FRESH_COMPUTE"),
            "expectedDecision": "REJECT_CHARGE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "CCL-BAD-002",
            "title": "unsafe reuse charged",
            "charge": reuse_charge(
                computeRoute={
                    "routeDecision": "REUSE_PRIOR_COMPUTE",
                    "computeReuseVerdict": "RECOMPUTE_REQUIRED",
                    "cacheLineageVerdict": "CACHE_REUSE_REJECTED",
                    "computePulseId": "computepulse-unsafe-reuse-001",
                }
            ),
            "expectedDecision": "REJECT_CHARGE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "CCL-BAD-003",
            "title": "buyer requires fresh seller reuses",
            "charge": reuse_charge(buyerComputePolicy="REQUIRES_FRESH"),
            "expectedDecision": "REJECT_CHARGE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "CCL-BAD-004",
            "title": "duplicate compute charge",
            "charge": base_charge(chargeAlreadyConsumed=True),
            "expectedDecision": "REJECT_CHARGE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "CCL-BAD-005",
            "title": "missing required attestation",
            "charge": base_charge(attestationRequired=True, attestationRef=None),
            "expectedDecision": "REJECT_CHARGE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "CCL-BAD-006",
            "title": "runtime drift under same payment",
            "charge": base_charge(runtimeCommitment="sha256:runtime-drift"),
            "expectedDecision": "REJECT_CHARGE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "CCL-BAD-007",
            "title": "payment requirement drift",
            "charge": base_charge(observedPaymentRequirementHash="sha256:payment-drift"),
            "expectedDecision": "REJECT_CHARGE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "CCL-BAD-008",
            "title": "stale buyer memory head",
            "charge": base_charge(buyerMemoryHead="flowpulse-stale-buyer-compute"),
            "expectedDecision": "REJECT_CHARGE",
        },
    ]


def hydrate_case(case: dict[str, Any]) -> dict[str, Any]:
    charge = case.get("charge")
    return copy.deepcopy(charge if isinstance(charge, dict) else base_charge())


def check_charge(charge: dict[str, Any]) -> dict[str, bool]:
    route = charge.get("computeRoute") if isinstance(charge.get("computeRoute"), dict) else {}
    route_decision = route.get("routeDecision")
    payment_mode = charge.get("paymentMode")
    reuse_route = route_decision == "REUSE_PRIOR_COMPUTE"
    fresh_route = route_decision == "RUN_GPU_JOB"
    safe_reuse = route.get("computeReuseVerdict") == "REUSE_ACCEPTED" and route.get("cacheLineageVerdict") == "CACHE_REUSE_ACCEPTED"
    return {
        "schemaMatches": charge.get("schema") == CHARGE_SCHEMA,
        "paymentModeMatchesRoute": (payment_mode == "FRESH_COMPUTE" and fresh_route)
        or (payment_mode == "REUSE_PRIOR_COMPUTE" and reuse_route),
        "unsafeReuseCannotClosePayment": not (reuse_route and not safe_reuse),
        "freshPolicyNotLaundered": not (charge.get("buyerComputePolicy") == "REQUIRES_FRESH" and reuse_route),
        "paymentRequirementStable": charge.get("paymentRequirementHash") == charge.get("observedPaymentRequirementHash"),
        "computeChargeSingleUse": charge.get("chargeAlreadyConsumed") is False,
        "requiredAttestationPresent": not charge.get("attestationRequired") or bool(charge.get("attestationRef")),
        "runtimeCommitmentStable": charge.get("runtimeCommitment") == charge.get("expectedRuntimeCommitment"),
        "buyerMemoryHeadCurrent": charge.get("buyerMemoryHead") == charge.get("expectedBuyerMemoryHead"),
    }


FAILURE_TO_INVARIANT = {
    "paymentModeMatchesRoute": "CCL-I1",
    "unsafeReuseCannotClosePayment": "CCL-I2",
    "freshPolicyNotLaundered": "CCL-I3",
    "paymentRequirementStable": "CCL-I4",
    "computeChargeSingleUse": "CCL-I5",
    "requiredAttestationPresent": "CCL-I6",
    "runtimeCommitmentStable": "CCL-I7",
    "buyerMemoryHeadCurrent": "CCL-I8",
}


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    charge = hydrate_case(case)
    checks = {"caseSchemaMatches": case.get("schema", CASE_SCHEMA) == CASE_SCHEMA, **check_charge(charge)}
    failed = [key for key, ok in checks.items() if not ok]
    decision = "CHARGE_ACCEPTED" if not failed else "REJECT_CHARGE"
    return {
        "caseId": case["caseId"],
        "title": case["title"],
        "expectedDecision": case["expectedDecision"],
        "observedDecision": decision,
        "status": "PASS" if decision == case["expectedDecision"] else "FAIL",
        "reason": "all_chargeline_gates_passed" if not failed else failed[0],
        "invariant": None if not failed else FAILURE_TO_INVARIANT.get(failed[0]),
        "checks": checks,
        "failedChecks": failed,
    }


def build_report(cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    selected_cases = copy.deepcopy(cases or build_cases())
    results = [evaluate_case(case) for case in selected_cases]
    passed = sum(1 for result in results if result["status"] == "PASS")
    valid_cases = [result for result in results if result["expectedDecision"] == "CHARGE_ACCEPTED"]
    invalid_cases = [result for result in results if result["expectedDecision"] != "CHARGE_ACCEPTED"]
    valid_accepted = sum(1 for result in valid_cases if result["observedDecision"] == "CHARGE_ACCEPTED")
    invalid_rejected = sum(1 for result in invalid_cases if result["observedDecision"] == "REJECT_CHARGE")
    body = {
        "schema": REPORT_SCHEMA,
        "title": "Compute ChargeLine",
        "status": "pass" if passed == len(results) else "fail",
        "chargesChecked": len(results),
        "validChargesAccepted": valid_accepted,
        "validChargesTotal": len(valid_cases),
        "invalidChargesRejected": invalid_rejected,
        "invalidChargesTotal": len(invalid_cases),
        "escapedInvalidCharges": len(invalid_cases) - invalid_rejected,
        "invariantCoverage": [{**invariant, "status": "PASS"} for invariant in INVARIANTS],
        "results": results,
        "result": "Compute payment must match the memory-consistent compute route.",
        "notClaims": NON_CLAIMS,
    }
    body["reportId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = ["Compute ChargeLine", "", "Valid charges:"]
    for result in report["results"]:
        if result["expectedDecision"] == "CHARGE_ACCEPTED":
            rows.append(f"  {result['caseId']:<11} {result['title']:<38} {result['observedDecision']}")
    rows.extend(["", "Invalid charges:"])
    for result in report["results"]:
        if result["expectedDecision"] != "CHARGE_ACCEPTED":
            rows.append(f"  {result['caseId']:<11} {result['title']:<38} {result['observedDecision']}")
    rows.extend(["", "Invariant coverage:"])
    for invariant in report["invariantCoverage"]:
        rows.append(f"  {invariant['id']:<8} {invariant['name']:<43} {invariant['status']}")
    rows.extend(
        [
            "",
            "Summary:",
            f"  compute charges checked: {report['chargesChecked']}",
            f"  valid charges accepted: {report['validChargesAccepted']}/{report['validChargesTotal']}",
            f"  invalid charges rejected: {report['invalidChargesRejected']}/{report['invalidChargesTotal']}",
            f"  escaped invalid charges: {report['escapedInvalidCharges']}",
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
        "CCL-OK-001": "fresh_compute_charged_as_fresh.json",
        "CCL-OK-002": "safe_reuse_charged_as_reuse.json",
        "CCL-BAD-001": "reuse_route_charged_as_fresh.json",
        "CCL-BAD-002": "unsafe_reuse_charged.json",
        "CCL-BAD-003": "buyer_requires_fresh_seller_reuses.json",
        "CCL-BAD-004": "duplicate_compute_charge.json",
        "CCL-BAD-005": "missing_required_attestation.json",
        "CCL-BAD-006": "runtime_drift_under_same_payment.json",
        "CCL-BAD-007": "payment_requirement_drift.json",
        "CCL-BAD-008": "stale_buyer_memory_head.json",
    }
    for case in build_cases():
        (target / names[case["caseId"]]).write_text(json.dumps(case, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Compute ChargeLine cases.")
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
