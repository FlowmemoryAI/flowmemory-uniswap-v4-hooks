#!/usr/bin/env python3
"""
FMM-0 Closure Lab.

Checks whether FMM-0 stays closed under valid memory-history composition and
rejects invalid composition. This is deliberately local: it does not claim
semantic truth, model correctness, production verifier infrastructure, custody,
or GPU acceleration.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ, fmm0_phase_table
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore
    import fmm0_phase_table  # type: ignore


REPORT_SCHEMA = "flowmemory.fmm0_closure_lab_result.v0"
CLOSURE_CASE_SCHEMA = "flowmemory.fmm0_closure_case.v0"
PRE_LOCAL = "examples/fmm0-phase-table/artifacts/pre_receipt_local_output.json"
READER_FLOWPULSE = "examples/fmm0-phase-table/artifacts/reader_derived_flowpulse.json"
FMM0_HISTORY = "examples/fmm0-phase-table/artifacts/fmm0_conforming_history.json"
VALID_FMM0 = "examples/fmm0-phase-table/transitions/valid_reader_to_fmm0.json"
NON_CLAIMS = [
    "not_semantic_truth",
    "not_model_correctness",
    "not_gpu_acceleration",
    "not_custody",
    "not_fund_protection",
    "not_base_mainnet",
    "not_production_verifier_infrastructure",
]
BANNED_OUTPUT_PHRASES = [
    "semantic truth verified",
    "model correctness proven",
    "gpu acceleration",
    "base mainnet deployed",
    "audited custody",
    "protects funds",
    "production verifier",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(fmm0_phase_table.resolve_path(path))


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def fields(artifact: dict[str, Any]) -> dict[str, Any]:
    return fmm0_phase_table.fields(artifact)


def fmm0_history(
    artifact_id: str,
    rootfield_id: str,
    commitment: str,
    sequence: int,
) -> dict[str, Any]:
    history = copy.deepcopy(read_json(FMM0_HISTORY))
    history["artifactId"] = artifact_id
    history["fields"]["rootfieldId"] = rootfield_id
    history["fields"]["commitment"] = commitment
    history["fields"]["sequence"] = sequence
    history["fields"]["sourceFlowPulse"] = {
        "txHash": "0x" + format(sequence, "064x"),
        "logIndex": sequence,
    }
    return history


def case(
    case_id: str,
    law: str,
    expectation: str,
    actual_status: str,
    fault: str | None,
    details: dict[str, Any],
) -> dict[str, Any]:
    passed = (
        expectation == "preserve" and actual_status == "closed"
    ) or (
        expectation == "reject" and actual_status == "rejected"
    )
    body = {
        "schema": CLOSURE_CASE_SCHEMA,
        "caseId": case_id,
        "law": law,
        "expectation": expectation,
        "status": "pass" if passed else "fail",
        "actualStatus": actual_status,
        "fault": fault,
        "details": details,
        "notClaims": NON_CLAIMS,
    }
    body["closureCaseId"] = digest(body)
    return body


def classify_cell(table: dict[str, Any], artifact: dict[str, Any]) -> tuple[str, str]:
    result = fmm0_phase_table.classify_artifact(table, artifact)
    return str(result.get("status")), str(result.get("cellId"))


def append_histories(table: dict[str, Any], left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_status, left_cell = classify_cell(table, left)
    right_status, right_cell = classify_cell(table, right)
    if left_status != "pass" or right_status != "pass" or left_cell != "FMM0-LIVE" or right_cell != "FMM0-LIVE":
        return {"status": "rejected", "fault": "non_fmm0_live_history"}
    if fields(left).get("rootfieldId") != fields(right).get("rootfieldId"):
        return {"status": "rejected", "fault": "append_requires_same_rootfield"}
    left_sequence = int(fields(left).get("sequence", 0))
    right_sequence = int(fields(right).get("sequence", 0))
    if right_sequence <= left_sequence:
        return {"status": "rejected", "fault": "rootfield_rollback"}
    if right_sequence != left_sequence + 1:
        return {"status": "rejected", "fault": "rootfield_sequence_gap"}
    return {
        "status": "closed",
        "fault": None,
        "head": {
            "rootfieldId": fields(right).get("rootfieldId"),
            "commitment": fields(right).get("commitment"),
            "sequence": right_sequence,
        },
    }


def merge_histories(table: dict[str, Any], left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_status, left_cell = classify_cell(table, left)
    right_status, right_cell = classify_cell(table, right)
    if left_status != "pass" or right_status != "pass" or left_cell != "FMM0-LIVE" or right_cell != "FMM0-LIVE":
        return {"status": "rejected", "fault": "non_fmm0_live_history"}

    left_key = (fields(left).get("rootfieldId"), fields(left).get("sequence"))
    right_key = (fields(right).get("rootfieldId"), fields(right).get("sequence"))
    if left_key == right_key and fields(left).get("commitment") != fields(right).get("commitment"):
        return {"status": "rejected", "fault": "split_brain_write"}

    heads = sorted(
        [
            {
                "rootfieldId": fields(left).get("rootfieldId"),
                "commitment": fields(left).get("commitment"),
                "sequence": int(fields(left).get("sequence", 0)),
            },
            {
                "rootfieldId": fields(right).get("rootfieldId"),
                "commitment": fields(right).get("commitment"),
                "sequence": int(fields(right).get("sequence", 0)),
            },
        ],
        key=lambda item: (str(item["rootfieldId"]), int(item["sequence"]), str(item["commitment"])),
    )
    return {"status": "closed", "fault": None, "mergeId": digest(heads), "heads": heads}


def build_cases() -> list[dict[str, Any]]:
    table = fmm0_phase_table.load_table()
    pre_local = read_json(PRE_LOCAL)
    reader = read_json(READER_FLOWPULSE)

    anneal_result = fmm0_phase_table.anneal(table, pre_local, reader)
    attachment_status = "closed" if anneal_result.get("status") == "pass" else "rejected"

    promotion_result = fmm0_phase_table.evaluate_transition(table, read_json(VALID_FMM0))
    promotion_status = "closed" if promotion_result.get("status") == "allowed" else "rejected"

    rootfield_a = "0x" + "11" * 32
    rootfield_b = "0x" + "33" * 32
    history_a1 = fmm0_history("history_a1", rootfield_a, "0x" + "21" * 32, 1)
    history_a2 = fmm0_history("history_a2", rootfield_a, "0x" + "22" * 32, 2)
    history_b1 = fmm0_history("history_b1", rootfield_b, "0x" + "44" * 32, 1)
    history_a1_conflict = fmm0_history("history_a1_conflict", rootfield_a, "0x" + "55" * 32, 1)

    append_valid = append_histories(table, history_a1, history_a2)
    merge_valid_lr = merge_histories(table, history_a1, history_b1)
    merge_valid_rl = merge_histories(table, history_b1, history_a1)
    merge_commutative = merge_valid_lr.get("status") == "closed" and merge_valid_lr.get("mergeId") == merge_valid_rl.get("mergeId")

    rollback = append_histories(table, history_a2, history_a1)
    split_brain = merge_histories(table, history_a1, history_a1_conflict)

    pre_smuggle = copy.deepcopy(pre_local)
    pre_smuggle["fields"]["txHash"] = "0x" + "aa" * 32
    pre_smuggle_result = fmm0_phase_table.classify_artifact(table, pre_smuggle)

    semantic_overclaim = copy.deepcopy(reader)
    semantic_overclaim["requestedOperations"] = ["claim_semantic_truth"]
    semantic_result = fmm0_phase_table.classify_artifact(table, semantic_overclaim)
    semantic_faults = [item["fault"] for item in semantic_result.get("requestedOperationFaults", [])]

    return [
        case(
            "CL-001",
            "receipt attachment preserves a matching local draft",
            "preserve",
            attachment_status,
            None if attachment_status == "closed" else ",".join(anneal_result.get("faults", [])),
            {"after": anneal_result.get("after"), "fmm0Status": anneal_result.get("fmm0Status")},
        ),
        case(
            "CL-002",
            "reader-derived FlowPulse can promote only with consistency evidence",
            "preserve",
            promotion_status,
            promotion_result.get("fault"),
            {"transition": promotion_result.get("transitionId"), "reason": promotion_result.get("reason")},
        ),
        case(
            "CL-003",
            "same-rootfield append preserves monotonic sequence",
            "preserve",
            append_valid["status"],
            append_valid.get("fault"),
            {"head": append_valid.get("head")},
        ),
        case(
            "CL-004",
            "independent rootfield merge is commutative",
            "preserve",
            "closed" if merge_commutative else "rejected",
            None if merge_commutative else "merge_not_commutative",
            {"mergeId": merge_valid_lr.get("mergeId")},
        ),
        case(
            "CL-005",
            "same-rootfield append rejects rollback",
            "reject",
            rollback["status"],
            rollback.get("fault"),
            {"attempted": "sequence 2 -> sequence 1"},
        ),
        case(
            "CL-006",
            "same-rootfield same-sequence merge rejects split-brain heads",
            "reject",
            split_brain["status"],
            split_brain.get("fault"),
            {"attempted": "same rootfield and sequence with different commitments"},
        ),
        case(
            "CL-007",
            "pre-receipt composition rejects receipt-only facts",
            "reject",
            "rejected" if pre_smuggle_result.get("status") == "invalid" else "closed",
            pre_smuggle_result.get("fault"),
            {"forbiddenFields": pre_smuggle_result.get("forbiddenFields", [])},
        ),
        case(
            "CL-008",
            "reader-derived evidence cannot close over semantic truth",
            "reject",
            "rejected" if "operation_forbidden_in_phase" in semantic_faults else "closed",
            "operation_forbidden_in_phase" if "operation_forbidden_in_phase" in semantic_faults else None,
            {"requestedOperations": semantic_overclaim["requestedOperations"]},
        ),
    ]


def build_report() -> dict[str, Any]:
    cases = build_cases()
    valid_cases = [item for item in cases if item["expectation"] == "preserve"]
    invalid_cases = [item for item in cases if item["expectation"] == "reject"]
    valid_passed = sum(1 for item in valid_cases if item["status"] == "pass")
    invalid_passed = sum(1 for item in invalid_cases if item["status"] == "pass")
    escaped = len(cases) - valid_passed - invalid_passed
    body = {
        "schema": REPORT_SCHEMA,
        "title": "FMM-0 Closure Lab",
        "status": "pass" if escaped == 0 else "fail",
        "closureLawsChecked": len(cases),
        "validClosuresPreserved": valid_passed,
        "validClosuresTotal": len(valid_cases),
        "invalidClosuresRejected": invalid_passed,
        "invalidClosuresTotal": len(invalid_cases),
        "escaped": escaped,
        "cases": cases,
        "result": "FMM-0 is closed under valid receipt-bound composition and rejects invalid memory algebra.",
        "notClaims": NON_CLAIMS,
    }
    body["closureLabId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = [
        "FMM-0 Closure Lab",
        "",
        f"Closure laws checked: {report['closureLawsChecked']}",
        f"Valid closures preserved: {report['validClosuresPreserved']}/{report['validClosuresTotal']}",
        f"Invalid closures rejected: {report['invalidClosuresRejected']}/{report['invalidClosuresTotal']}",
        f"Escaped: {report['escaped']}",
        "",
    ]
    for item in report["cases"]:
        status = "PASS" if item["status"] == "pass" else "FAIL"
        fault = item["fault"] or "-"
        rows.append(f"{item['caseId']} {item['law']:<67} {status:<4} {fault}")
    rows.extend(["", f"Result: {report['result']}"])
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FMM-0 closure law checks.")
    parser.add_argument("command", choices=["demo"], help="Run the closure lab demo.")
    parser.add_argument("--pretty", action="store_true", help="Text output is already readable; JSON uses indentation.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(render_report(report))
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
