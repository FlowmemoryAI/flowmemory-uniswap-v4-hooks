#!/usr/bin/env python3
"""
FMM-0 Boundary Bisimulation.

Checks that the same FlowPulse boundary survives projection from hook-time
signal, to reader-attached receipt envelope, to FMM-0 runtime state. This is a
local cross-layer conformance harness, not a production verifier.
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


REPORT_SCHEMA = "flowmemory.fmm0_boundary_bisimulation_result.v0"
CASE_SCHEMA = "flowmemory.fmm0_boundary_bisimulation_case.v0"
FLOWPULSE_EVIDENCE = "examples/axiom-writ/flowpulse-evidence.fixture.json"
FMM0_HISTORY = "examples/fmm0-phase-table/artifacts/fmm0_conforming_history.json"
RECEIPT_ONLY_FIELDS = {"txHash", "logIndex", "transactionIndex", "blockHash", "blockNumber", "receiptStatus", "finality"}
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


def normalize(value: Any) -> str:
    return str(value or "").lower()


def non_empty(value: Any) -> bool:
    return value not in (None, "", [], {})


def load_flowpulse_record() -> dict[str, Any]:
    evidence = read_json(FLOWPULSE_EVIDENCE)
    for record in evidence.get("records", []):
        if isinstance(record, dict) and record.get("eventName") == "FlowPulse":
            return copy.deepcopy(record)
    raise ValueError("fixture missing FlowPulse record")


def hook_projection(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "flowmemory.boundary_projection.hook.v0",
        "layer": "hook",
        "eventName": record.get("eventName"),
        "boundary": "uniswap_v4_afterSwap",
        "hookAddress": record.get("hookAddress"),
        "pulseId": record.get("pulseId"),
        "rootfieldId": record.get("rootfieldId"),
        "subjectPoolId": record.get("subjectPoolId"),
        "commitment": record.get("commitment"),
        "parentPulseId": record.get("parentPulseId"),
    }


def receipt_projection(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "flowmemory.boundary_projection.receipt.v0",
        "layer": "receipt",
        "eventName": record.get("eventName"),
        "boundary": "uniswap_v4_afterSwap",
        "hookAddress": record.get("hookAddress"),
        "pulseId": record.get("pulseId"),
        "rootfieldId": record.get("rootfieldId"),
        "subjectPoolId": record.get("subjectPoolId"),
        "commitment": record.get("commitment"),
        "parentPulseId": record.get("parentPulseId"),
        "txHash": record.get("txHash"),
        "logIndex": record.get("logIndex"),
        "blockNumber": record.get("blockNumber"),
        "receiptStatus": record.get("receiptStatus"),
        "finality": record.get("finality"),
    }


def runtime_projection(record: dict[str, Any]) -> dict[str, Any]:
    runtime = copy.deepcopy(read_json(FMM0_HISTORY))
    runtime_fields = runtime.setdefault("fields", {})
    runtime_fields["rootfieldId"] = record.get("rootfieldId")
    runtime_fields["commitment"] = record.get("commitment")
    runtime_fields["sourceFlowPulse"] = {
        "txHash": record.get("txHash"),
        "logIndex": record.get("logIndex"),
    }
    return runtime


def validate_hook(projection: dict[str, Any]) -> tuple[bool, str | None]:
    if projection.get("eventName") != "FlowPulse":
        return False, "hook_projection_not_flowpulse"
    for field in RECEIPT_ONLY_FIELDS:
        if non_empty(projection.get(field)):
            return False, "hook_projection_contains_receipt_metadata"
    if not non_empty(projection.get("rootfieldId")) or not non_empty(projection.get("commitment")):
        return False, "hook_projection_missing_boundary_identity"
    return True, None


def validate_receipt(hook: dict[str, Any], receipt: dict[str, Any]) -> tuple[bool, str | None]:
    ok, fault = validate_hook(hook)
    if not ok:
        return False, fault
    for field in ["rootfieldId", "commitment", "pulseId", "hookAddress"]:
        if normalize(hook.get(field)) != normalize(receipt.get(field)):
            return False, f"{field}_drift"
    if not non_empty(receipt.get("txHash")):
        return False, "receipt_missing_txHash"
    if not non_empty(receipt.get("logIndex")):
        return False, "receipt_missing_logIndex"
    return True, None


def validate_runtime(table: dict[str, Any], receipt: dict[str, Any], runtime: dict[str, Any]) -> tuple[bool, str | None]:
    classification = fmm0_phase_table.classify_artifact(table, runtime)
    if classification.get("cellId") != "FMM0-LIVE" or classification.get("status") != "pass":
        return False, "runtime_not_fmm0_live"
    runtime_fields = fmm0_phase_table.fields(runtime)
    for field in ["rootfieldId", "commitment"]:
        if normalize(runtime_fields.get(field)) != normalize(receipt.get(field)):
            return False, f"runtime_{field}_drift"
    source = runtime_fields.get("sourceFlowPulse", {})
    if normalize(source.get("txHash")) != normalize(receipt.get("txHash")):
        return False, "runtime_receipt_drift"
    if str(source.get("logIndex")) != str(receipt.get("logIndex")):
        return False, "runtime_receipt_drift"
    return True, None


def validate_end_to_end(table: dict[str, Any], hook: dict[str, Any], receipt: dict[str, Any], runtime: dict[str, Any]) -> tuple[bool, str | None]:
    ok, fault = validate_receipt(hook, receipt)
    if not ok:
        return False, fault
    return validate_runtime(table, receipt, runtime)


def case(case_id: str, law: str, expectation: str, ok: bool, fault: str | None, details: dict[str, Any]) -> dict[str, Any]:
    passed = (expectation == "preserve" and ok) or (expectation == "reject" and not ok)
    body = {
        "schema": CASE_SCHEMA,
        "caseId": case_id,
        "law": law,
        "expectation": expectation,
        "status": "pass" if passed else "fail",
        "fault": fault,
        "details": details,
        "notClaims": NON_CLAIMS,
    }
    body["bisimulationCaseId"] = digest(body)
    return body


def build_cases() -> list[dict[str, Any]]:
    table = fmm0_phase_table.load_table()
    record = load_flowpulse_record()
    hook = hook_projection(record)
    receipt = receipt_projection(record)
    runtime = runtime_projection(record)

    hook_ok, hook_fault = validate_hook(hook)
    receipt_ok, receipt_fault = validate_receipt(hook, receipt)
    runtime_ok, runtime_fault = validate_runtime(table, receipt, runtime)
    e2e_ok, e2e_fault = validate_end_to_end(table, hook, receipt, runtime)

    receipt_rootfield_drift = copy.deepcopy(receipt)
    receipt_rootfield_drift["rootfieldId"] = "0x" + "99" * 32
    rootfield_ok, rootfield_fault = validate_receipt(hook, receipt_rootfield_drift)

    receipt_commitment_drift = copy.deepcopy(receipt)
    receipt_commitment_drift["commitment"] = "0x" + "88" * 32
    commitment_ok, commitment_fault = validate_receipt(hook, receipt_commitment_drift)

    runtime_tx_drift = copy.deepcopy(runtime)
    runtime_tx_drift["fields"]["sourceFlowPulse"]["txHash"] = "0x" + "77" * 32
    runtime_drift_ok, runtime_drift_fault = validate_runtime(table, receipt, runtime_tx_drift)

    hook_receipt_smuggle = copy.deepcopy(hook)
    hook_receipt_smuggle["txHash"] = record.get("txHash")
    hook_smuggle_ok, hook_smuggle_fault = validate_hook(hook_receipt_smuggle)

    return [
        case("BS-001", "hook projection preserves FlowPulse boundary identity without receipt facts", "preserve", hook_ok, hook_fault, {"layer": "hook"}),
        case("BS-002", "receipt projection preserves hook identity and attaches proof-envelope facts", "preserve", receipt_ok, receipt_fault, {"layer": "receipt"}),
        case("BS-003", "runtime projection preserves receipt identity inside FMM-0 live state", "preserve", runtime_ok, runtime_fault, {"layer": "runtime"}),
        case("BS-004", "end-to-end boundary bisimulation preserves hook-to-receipt-to-runtime identity", "preserve", e2e_ok, e2e_fault, {"layers": ["hook", "receipt", "runtime"]}),
        case("BS-005", "receipt projection rejects rootfield drift", "reject", rootfield_ok, rootfield_fault, {"mutated": "rootfieldId"}),
        case("BS-006", "receipt projection rejects commitment drift", "reject", commitment_ok, commitment_fault, {"mutated": "commitment"}),
        case("BS-007", "runtime projection rejects receipt metadata drift", "reject", runtime_drift_ok, runtime_drift_fault, {"mutated": "sourceFlowPulse.txHash"}),
        case("BS-008", "hook projection rejects receipt metadata smuggling", "reject", hook_smuggle_ok, hook_smuggle_fault, {"mutated": "hook.txHash"}),
    ]


def build_report() -> dict[str, Any]:
    cases = build_cases()
    preserved = [item for item in cases if item["expectation"] == "preserve"]
    rejected = [item for item in cases if item["expectation"] == "reject"]
    preserved_passed = sum(1 for item in preserved if item["status"] == "pass")
    rejected_passed = sum(1 for item in rejected if item["status"] == "pass")
    escaped = len(cases) - preserved_passed - rejected_passed
    body = {
        "schema": REPORT_SCHEMA,
        "title": "FMM-0 Boundary Bisimulation",
        "status": "pass" if escaped == 0 else "fail",
        "projectionChecks": len(cases),
        "bisimulationsPreserved": preserved_passed,
        "bisimulationsTotal": len(preserved),
        "driftCasesRejected": rejected_passed,
        "driftCasesTotal": len(rejected),
        "escaped": escaped,
        "cases": cases,
        "result": "FlowPulse boundary semantics survive hook-to-receipt-to-runtime projection and reject cross-layer drift.",
        "notClaims": NON_CLAIMS,
    }
    body["bisimulationId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = [
        "FMM-0 Boundary Bisimulation",
        "",
        f"Projection checks: {report['projectionChecks']}",
        f"Bisimulations preserved: {report['bisimulationsPreserved']}/{report['bisimulationsTotal']}",
        f"Drift cases rejected: {report['driftCasesRejected']}/{report['driftCasesTotal']}",
        f"Escaped: {report['escaped']}",
        "",
    ]
    for item in report["cases"]:
        status = "PASS" if item["status"] == "pass" else "FAIL"
        fault = item["fault"] or "-"
        rows.append(f"{item['caseId']} {item['law']:<76} {status:<4} {fault}")
    rows.extend(["", f"Result: {report['result']}"])
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FMM-0 boundary bisimulation checks.")
    parser.add_argument("command", choices=["demo"], help="Run the boundary bisimulation demo.")
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
