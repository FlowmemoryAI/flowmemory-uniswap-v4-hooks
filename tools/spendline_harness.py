#!/usr/bin/env python3
"""
SpendLine Harness.

SpendLine checks whether an autonomous agent spend claim can be serialized
against receipt-bound FlowPulse memory before a downstream system treats the
spend as memory-consistent.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ, flow_serial
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore
    import flow_serial  # type: ignore


CASE_SCHEMA = "flowmemory.spendline_case.v0"
REPORT_SCHEMA = "flowmemory.spendline_report.v0"
REQUEST_SCHEMA = "flowmemory.spendline_request.v0"
LEDGER_SCHEMA = "flowmemory.spendline_ledger.v0"
ZERO32 = "0x" + ("0" * 64)
ROOTFIELD = "0x" + ("1" * 64)
COMMITMENT = "0x" + ("2" * 64)
SPEND = "0x" + ("3" * 64)
INTENT = "0x" + ("4" * 64)
INTENT_REPLAY = "0x" + ("5" * 64)
POOL = "0x" + ("6" * 64)
WALLET = "0x00000000000000000000000000000000000000aa"
HOOK = "0x0000000000000000000000000000000000000001"
HEAD_A = "flowpulse-head-a"
HEAD_B = "flowpulse-head-b"
NON_CLAIMS = [
    "not_wallet_authorization",
    "not_custody",
    "not_fund_protection",
    "not_swap_control",
    "not_semantic_truth",
    "not_model_correctness",
    "not_live_mainnet_claim",
    "not_production_verifier_infrastructure",
]
BANNED_OUTPUT_PHRASES = [
    "protects funds",
    "authorizes wallets",
    "guarantees payment safety",
    "semantic truth verified",
    "live base mainnet",
]


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def write_json(payload: Any, output: str | None, pretty: bool) -> None:
    axiom_writ.write_json(payload, output, pretty)


def truthy_hex(value: Any) -> bool:
    return axiom_writ.truthy_hex(value)


def boundary(boundary_id: str = HEAD_A, order: int = 2, log_index: int = 7, tx_char: str = "a") -> dict[str, Any]:
    return {
        "schema": flow_serial.BOUNDARY_SCHEMA,
        "boundaryId": boundary_id,
        "artifactType": "FlowPulse",
        "boundary": "uniswap_v4_afterSwap",
        "declaredOrder": order,
        "chainId": "84532",
        "hookAddress": HOOK,
        "txHash": "0x" + (tx_char * 64),
        "transactionIndex": order,
        "logIndex": log_index,
        "blockNumber": 100000 + order,
        "blockHash": "0x" + (str(order % 10) * 64),
        "receiptStatus": "success",
        "rootfieldId": ROOTFIELD,
        "commitment": COMMITMENT,
        "subjectPoolId": POOL,
        "parentPulseId": ZERO32,
    }


def base_request(**overrides: Any) -> dict[str, Any]:
    body = {
        "schema": REQUEST_SCHEMA,
        "requestId": "spendline-request",
        "agentId": "agent-base-001",
        "agentIdentity": "erc8004:8453:42",
        "wallet": WALLET,
        "rootfieldId": ROOTFIELD,
        "currentMemoryHead": HEAD_A,
        "spendIntentCommitment": INTENT,
        "proposedSpendCommitment": SPEND,
        "asset": "USDC",
        "amount": "0.010000",
        "target": "x402://market-data.example",
        "spendSurface": "x402_payment",
        "requestedAction": "approve_for_wallet_submission",
        "axiomPatchVerdict": "allowed",
        "paymentRequirement": {"asset": "USDC", "amount": "0.010000", "recipient": "x402://market-data.example"},
        "computeReuseVerdict": "NOT_APPLICABLE",
        "cacheLineageVerdict": "NOT_APPLICABLE",
        "declaredOrder": 3,
        "observedBoundaries": [HEAD_A],
        "claimedReceiptFacts": [{"field": "txHash", "boundaryId": HEAD_A}, {"field": "logIndex", "boundaryId": HEAD_A}],
        "postSpendFlowPulse": HEAD_A,
    }
    body.update(overrides)
    return body


def base_ledger(**overrides: Any) -> dict[str, Any]:
    body = {
        "schema": LEDGER_SCHEMA,
        "ledgerId": "spendline-ledger",
        "rootfieldId": ROOTFIELD,
        "wallet": WALLET,
        "currentMemoryHead": HEAD_A,
        "spentIntentCommitments": [],
        "receiptBoundaries": [boundary()],
    }
    body.update(overrides)
    return body


def spend_event(request: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    current_head = str(request.get("currentMemoryHead") or "")
    event_order = int(case.get("eventDeclaredOrder", request.get("declaredOrder", 3)))
    before_boundary = bool(case.get("retrocausal"))
    write_head = case.get("eventWriteHead", current_head)
    return {
        "schema": flow_serial.EVENT_SCHEMA,
        "eventId": f"{case.get('caseId', 'SPL')}-spend",
        "eventType": "autonomous_spend_claim",
        "agentId": request.get("agentId"),
        "rootfieldId": request.get("rootfieldId"),
        "declaredOrder": event_order,
        "observedBoundaries": request.get("observedBoundaries", []),
        "claimedReceiptFacts": request.get("claimedReceiptFacts", []),
        "writes": [{"key": "rootfieldHead", "value": write_head}],
        "exclusiveWriteKey": f"spend:{request.get('wallet')}:{request.get('spendIntentCommitment')}",
        "mustPrecede": [current_head] if before_boundary else [],
        "mustFollow": [] if before_boundary else [current_head],
        "spendIntentCommitment": request.get("spendIntentCommitment"),
        "proposedSpendCommitment": request.get("proposedSpendCommitment"),
    }


def history_for_case(case: dict[str, Any], request: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    boundaries = list(ledger.get("receiptBoundaries") or [])
    events = []
    if case.get("rootfieldRollback"):
        boundaries = [boundary(HEAD_A, 2, 7, "a"), boundary(HEAD_B, 3, 8, "b")]
        events.append(
            {
                "schema": flow_serial.EVENT_SCHEMA,
                "eventId": f"{case['caseId']}-advance",
                "eventType": "memory_head_advance",
                "agentId": request.get("agentId"),
                "rootfieldId": request.get("rootfieldId"),
                "declaredOrder": 4,
                "observedBoundaries": [HEAD_B],
                "claimedReceiptFacts": [{"field": "txHash", "boundaryId": HEAD_B}],
                "writes": [{"key": "rootfieldHead", "value": HEAD_B}],
                "mustPrecede": [],
                "mustFollow": [HEAD_B],
            }
        )
    events.append(spend_event(request, case))
    return {
        "schema": flow_serial.HISTORY_SCHEMA,
        "historyId": f"{case.get('caseId', 'SPL')}-history",
        "agentId": request.get("agentId"),
        "rootfieldId": request.get("rootfieldId"),
        "declaredConsistency": "flow_serializable",
        "boundaries": boundaries,
        "events": events,
        "notClaims": flow_serial.non_claims(),
    }


def build_cases() -> list[dict[str, Any]]:
    return [
        {
            "schema": CASE_SCHEMA,
            "caseId": "SPL-OK-001",
            "title": "valid spend after memory head",
            "expectedDecision": "ACCEPT_SPENDLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "SPL-BAD-001",
            "title": "stale memory head spend",
            "request": {"currentMemoryHead": "flowpulse-stale-head", "observedBoundaries": ["flowpulse-stale-head"]},
            "expectedDecision": "REJECT_SPENDLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "SPL-BAD-002",
            "title": "duplicate intent replay",
            "request": {"spendIntentCommitment": INTENT_REPLAY},
            "ledger": {"spentIntentCommitments": [INTENT_REPLAY]},
            "expectedDecision": "REJECT_SPENDLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "SPL-BAD-003",
            "title": "hallucinated receipt claim before receipt boundary",
            "retrocausal": True,
            "eventDeclaredOrder": 1,
            "expectedDecision": "REJECT_SPENDLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "SPL-BAD-004",
            "title": "post-spend FlowPulse missing",
            "request": {"postSpendFlowPulse": ""},
            "expectedDecision": "REJECT_SPENDLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "SPL-BAD-005",
            "title": "rootfield rollback spend",
            "request": {
                "currentMemoryHead": HEAD_B,
                "observedBoundaries": [HEAD_B],
                "claimedReceiptFacts": [{"field": "txHash", "boundaryId": HEAD_B}, {"field": "logIndex", "boundaryId": HEAD_B}],
                "postSpendFlowPulse": HEAD_B,
            },
            "ledger": {"currentMemoryHead": HEAD_B, "receiptBoundaries": [boundary(HEAD_A, 2, 7, "a"), boundary(HEAD_B, 3, 8, "b")]},
            "rootfieldRollback": True,
            "eventWriteHead": HEAD_A,
            "eventDeclaredOrder": 5,
            "expectedDecision": "REJECT_SPENDLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "SPL-BAD-006",
            "title": "AxiomPatch downgrade ignored",
            "request": {"axiomPatchVerdict": "downgraded_to_propose_unsigned_action"},
            "expectedDecision": "REJECT_SPENDLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "SPL-BAD-007",
            "title": "x402 payment requirement mismatch",
            "request": {"paymentRequirement": {"asset": "USDC", "amount": "0.020000", "recipient": "x402://market-data.example"}},
            "expectedDecision": "REJECT_SPENDLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "SPL-BAD-008",
            "title": "compute reuse inconsistent for paid work",
            "request": {"spendSurface": "compute_service_payment", "computeReuseVerdict": "RECOMPUTE_REQUIRED"},
            "expectedDecision": "REJECT_SPENDLINE",
        },
    ]


def hydrate_case(case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    request = base_request(**case.get("request", {}))
    ledger = base_ledger(**case.get("ledger", {}))
    return request, ledger


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    request, ledger = hydrate_case(case)
    serial = flow_serial.certify(history_for_case(case, request, ledger))
    current_head = str(request.get("currentMemoryHead") or "")
    ledger_head = str(ledger.get("currentMemoryHead") or "")
    post_spend_head = str(request.get("postSpendFlowPulse") or "")
    spent_intents = {str(item) for item in ledger.get("spentIntentCommitments", [])}
    payment_requirement = request.get("paymentRequirement") if isinstance(request.get("paymentRequirement"), dict) else {}
    axiom_patch_verdict = str(request.get("axiomPatchVerdict") or "")
    spend_surface = str(request.get("spendSurface") or "")
    requested_action = str(request.get("requestedAction") or "")
    compute_reuse_verdict = str(request.get("computeReuseVerdict") or "NOT_APPLICABLE")
    cache_lineage_verdict = str(request.get("cacheLineageVerdict") or "NOT_APPLICABLE")

    checks = {
        "caseSchemaMatches": case.get("schema", CASE_SCHEMA) == CASE_SCHEMA,
        "requestSchemaMatches": request.get("schema") == REQUEST_SCHEMA,
        "ledgerSchemaMatches": ledger.get("schema") == LEDGER_SCHEMA,
        "nonzeroRootfieldId": request.get("rootfieldId") not in ("", None, ZERO32),
        "walletPresent": bool(request.get("wallet")),
        "spendIntentPresent": truthy_hex(request.get("spendIntentCommitment")),
        "proposedSpendPresent": truthy_hex(request.get("proposedSpendCommitment")),
        "currentMemoryHeadMatchesLedger": bool(current_head) and current_head == ledger_head,
        "postSpendFlowPulsePresent": bool(post_spend_head),
        "postSpendFlowPulseMatchesCurrentHead": bool(post_spend_head) and post_spend_head == current_head,
        "intentNotReplayed": str(request.get("spendIntentCommitment")) not in spent_intents,
        "axiomPatchAllowsSpendSurface": axiom_patch_verdict == "allowed"
        or (axiom_patch_verdict == "not_required" and requested_action != "approve_for_wallet_submission"),
        "paymentRequirementMatchesSpend": not payment_requirement
        or (
            str(payment_requirement.get("asset")) == str(request.get("asset"))
            and str(payment_requirement.get("amount")) == str(request.get("amount"))
            and str(payment_requirement.get("recipient")) == str(request.get("target"))
        ),
        "computeReuseConsistentIfUsed": spend_surface != "compute_service_payment"
        or (compute_reuse_verdict not in {"RECOMPUTE_REQUIRED", "RUN_GPU_JOB"} and cache_lineage_verdict != "CACHE_REUSE_REJECTED"),
        "flowSerialSerializable": serial.get("status") == "serializable",
    }
    failed = [key for key, ok in checks.items() if not ok]
    decision = "ACCEPT_SPENDLINE" if not failed else "REJECT_SPENDLINE"
    reason = "all_spendline_gates_passed" if not failed else failed[0]
    if not checks["flowSerialSerializable"] and failed == ["flowSerialSerializable"]:
        reason = str(serial.get("faultType", "impossible_history"))

    return {
        "caseId": case["caseId"],
        "title": case["title"],
        "expectedDecision": case["expectedDecision"],
        "observedDecision": decision,
        "status": "PASS" if decision == case["expectedDecision"] else "FAIL",
        "reason": reason,
        "checks": checks,
        "failedChecks": failed,
        "serialStatus": serial.get("status"),
        "serialFaultType": serial.get("faultType"),
    }


def build_report(cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    selected_cases = cases or build_cases()
    results = [evaluate_case(case) for case in selected_cases]
    passed = sum(1 for result in results if result["status"] == "PASS")
    valid_cases = [result for result in results if result["expectedDecision"] == "ACCEPT_SPENDLINE"]
    unsafe_cases = [result for result in results if result["expectedDecision"] != "ACCEPT_SPENDLINE"]
    valid_accepted = sum(1 for result in valid_cases if result["observedDecision"] == "ACCEPT_SPENDLINE")
    unsafe_rejected = sum(1 for result in unsafe_cases if result["observedDecision"] == "REJECT_SPENDLINE")
    body = {
        "schema": REPORT_SCHEMA,
        "title": "SpendLine Harness",
        "status": "pass" if passed == len(results) else "fail",
        "casesPassed": passed,
        "casesTotal": len(results),
        "validSpendsAccepted": valid_accepted,
        "validSpendsTotal": len(valid_cases),
        "unsafeSpendsRejected": unsafe_rejected,
        "unsafeSpendsTotal": len(unsafe_cases),
        "escapedUnsafeSpends": len(unsafe_cases) - unsafe_rejected,
        "results": results,
        "result": "Autonomous spend must be memory-linearizable.",
        "notClaims": NON_CLAIMS,
    }
    body["reportId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = ["SpendLine Harness", "", "Valid spend:"]
    for result in report["results"]:
        if result["expectedDecision"] == "ACCEPT_SPENDLINE":
            rows.append(f"  {result['caseId']:<11} {result['status']:<5} {result['observedDecision']:<18} {result['reason']}")
    rows.extend(["", "Unsafe spends:"])
    for result in report["results"]:
        if result["expectedDecision"] != "ACCEPT_SPENDLINE":
            rows.append(f"  {result['caseId']:<11} {result['status']:<5} {result['observedDecision']:<18} {result['reason']}")
    rows.extend(
        [
            "",
            "Summary:",
            f"  spend cases checked: {report['casesTotal']}",
            f"  valid spends accepted: {report['validSpendsAccepted']}/{report['validSpendsTotal']}",
            f"  unsafe spends rejected: {report['unsafeSpendsRejected']}/{report['unsafeSpendsTotal']}",
            f"  escaped unsafe spends: {report['escapedUnsafeSpends']}",
            "",
            "Result:",
            f"  {report['result']}",
        ]
    )
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SpendLine autonomous spend consistency cases.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="Run the built-in SpendLine harness.")
    demo.add_argument("--json", action="store_true")
    demo.add_argument("--pretty", action="store_true")
    demo.add_argument("--write")

    check = subparsers.add_parser("check", help="Run one SpendLine case file.")
    check.add_argument("--case", required=True)
    check.add_argument("--json", action="store_true")
    check.add_argument("--pretty", action="store_true")
    check.add_argument("--write")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "check":
        report = build_report([read_json(args.case)])
    else:
        report = build_report()
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
