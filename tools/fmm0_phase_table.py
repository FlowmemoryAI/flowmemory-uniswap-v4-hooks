#!/usr/bin/env python3
"""
FMM-0 Phase Space.

This launch-facing tool classifies machine artifacts by receipt stage, reality
phase, operation surface, and authority level. The Reality Phase Table is the
rendered view of that phase space. It is deliberately local: it does not claim
semantic truth, model correctness, production verifier infrastructure, custody,
or GPU acceleration.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore


TABLE_SCHEMA = "flowmemory.fmm0_phase_table.v0"
ARTIFACT_SCHEMA = "flowmemory.phase_artifact.v0"
TRANSITION_SCHEMA = "flowmemory.phase_transition.v0"
CLASSIFICATION_SCHEMA = "flowmemory.phase_classification.v0"
TRANSITION_RESULT_SCHEMA = "flowmemory.phase_transition_result.v0"
ANNEAL_RESULT_SCHEMA = "flowmemory.phase_anneal_result.v0"
DEFAULT_TABLE = "examples/fmm0-phase-table/phase-table.json"
DEFAULT_ARTIFACTS = [
    "examples/fmm0-phase-table/artifacts/pre_receipt_local_output.json",
    "examples/fmm0-phase-table/artifacts/reader_derived_flowpulse.json",
    "examples/fmm0-phase-table/artifacts/fmm0_conforming_history.json",
    "examples/fmm0-phase-table/artifacts/illegal_receipt_smuggle.json",
]
DEFAULT_TRANSITIONS = [
    "examples/fmm0-phase-table/transitions/invalid_local_to_fmm0.json",
    "examples/fmm0-phase-table/transitions/invalid_reader_to_fmm0_missing_checks.json",
    "examples/fmm0-phase-table/transitions/valid_reader_attachment.json",
    "examples/fmm0-phase-table/transitions/valid_reader_to_fmm0.json",
]
RECEIPT_ONLY_FIELDS = {"txHash", "logIndex", "transactionIndex", "blockHash", "blockNumber", "receiptStatus"}
REQUIRED_AXES = {
    "receiptStage": {"before_receipt", "after_receipt"},
    "realityPhase": {"speculative", "live", "quarantined", "extinct"},
    "operationSurface": {"cite", "act", "forget", "recompute", "refuse", "split", "merge", "publish"},
    "authorityLevel": {"local_only", "public_boundary", "reader_derived", "fmm0_conforming"},
}
FORBIDDEN_OUTPUT_PHRASES = [
    "semantic truth verified",
    "model correctness",
    "GPU acceleration",
    "Base mainnet",
    "audited custody",
    "fund protection",
    "production verifier",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else repo_root() / candidate


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(resolve_path(path))


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def any_match(expected: str, actual: str) -> bool:
    return expected == "any" or expected == actual


def load_table(path: str | Path = DEFAULT_TABLE) -> dict[str, Any]:
    table = read_json(path)
    if table.get("schema") != TABLE_SCHEMA:
        raise ValueError(f"unsupported phase table schema: {table.get('schema')}")
    axes = table.get("axes")
    if not isinstance(axes, dict):
        raise ValueError("phase table missing axes")
    for axis, required in REQUIRED_AXES.items():
        values = axes.get(axis)
        if not isinstance(values, list):
            raise ValueError(f"phase table missing axis: {axis}")
        missing = required - set(str(value) for value in values)
        if missing:
            raise ValueError(f"phase table axis {axis} missing values: {sorted(missing)}")
    if not isinstance(table.get("cells"), list) or not table["cells"]:
        raise ValueError("phase table must contain cells")
    return table


def cell_by_id(table: dict[str, Any], cell_id: str) -> dict[str, Any] | None:
    for cell in table.get("cells", []):
        if isinstance(cell, dict) and cell.get("cellId") == cell_id:
            return cell
    return None


def fields(artifact: dict[str, Any]) -> dict[str, Any]:
    value = artifact.get("fields", {})
    return value if isinstance(value, dict) else {}


def non_empty_receipt_fields(artifact: dict[str, Any]) -> list[str]:
    artifact_fields = fields(artifact)
    found = []
    for field in sorted(RECEIPT_ONLY_FIELDS):
        value = artifact_fields.get(field)
        if value not in (None, "", [], {}):
            found.append(field)
    return found


def operation_faults(cell: dict[str, Any], artifact: dict[str, Any]) -> list[dict[str, str]]:
    requested = artifact.get("requestedOperations", [])
    if not isinstance(requested, list):
        return [{"fault": "requested_operations_must_be_list", "operation": "requestedOperations"}]
    forbidden = set(str(item) for item in cell.get("forbiddenOperations", []))
    faults = []
    for operation in requested:
        operation = str(operation)
        if operation in forbidden:
            faults.append({"fault": "operation_forbidden_in_phase", "operation": operation})
    return faults


def matching_cell(table: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any] | None:
    for cell in table.get("cells", []):
        if not isinstance(cell, dict):
            continue
        if not any_match(str(cell.get("receiptStage")), str(artifact.get("receiptStage"))):
            continue
        if not any_match(str(cell.get("realityPhase")), str(artifact.get("realityPhase"))):
            continue
        if not any_match(str(cell.get("authorityLevel")), str(artifact.get("authorityLevel"))):
            continue
        return cell
    return None


def classify_artifact(table: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    if artifact.get("schema") != ARTIFACT_SCHEMA:
        raise ValueError(f"unsupported phase artifact schema: {artifact.get('schema')}")

    smuggled = []
    if artifact.get("receiptStage") == "before_receipt":
        smuggled = [field for field in non_empty_receipt_fields(artifact) if field in {"txHash", "logIndex"}]
    if smuggled:
        body = {
            "schema": CLASSIFICATION_SCHEMA,
            "artifactId": artifact.get("artifactId"),
            "artifactType": artifact.get("artifactType"),
            "status": "invalid",
            "cellId": "INVALID",
            "fault": "receipt_field_smuggled_before_reader_attachment",
            "forbiddenFields": smuggled,
            "reason": "receipt-only fields cannot appear in a before-receipt artifact",
            "notClaims": table.get("notClaims", []),
        }
        body["classificationId"] = digest(body)
        return body

    cell = matching_cell(table, artifact)
    if not cell:
        body = {
            "schema": CLASSIFICATION_SCHEMA,
            "artifactId": artifact.get("artifactId"),
            "artifactType": artifact.get("artifactType"),
            "status": "invalid",
            "cellId": "INVALID",
            "fault": "no_matching_phase_cell",
            "reason": "artifact coordinate does not map to a declared FMM-0 phase cell",
            "notClaims": table.get("notClaims", []),
        }
        body["classificationId"] = digest(body)
        return body

    faults = operation_faults(cell, artifact)
    status = "pass" if not faults else "phase_limited"
    body = {
        "schema": CLASSIFICATION_SCHEMA,
        "artifactId": artifact.get("artifactId"),
        "artifactType": artifact.get("artifactType"),
        "status": status,
        "cellId": cell.get("cellId"),
        "cellName": cell.get("name"),
        "receiptStage": artifact.get("receiptStage"),
        "realityPhase": artifact.get("realityPhase"),
        "authorityLevel": artifact.get("authorityLevel"),
        "allowedOperations": cell.get("allowedOperations", []),
        "forbiddenOperations": cell.get("forbiddenOperations", []),
        "requestedOperationFaults": faults,
        "notClaims": table.get("notClaims", []),
    }
    body["classificationId"] = digest(body)
    return body


def validate_transition(transition: dict[str, Any]) -> None:
    if transition.get("schema") != TRANSITION_SCHEMA:
        raise ValueError(f"unsupported phase transition schema: {transition.get('schema')}")
    for field in ["transitionId", "fromCell", "toCell", "receiptEvidenceAttached"]:
        if field not in transition:
            raise ValueError(f"phase transition missing {field}")


def transition_fault(table: dict[str, Any], transition: dict[str, Any]) -> tuple[str, str | None, str]:
    from_cell = str(transition.get("fromCell"))
    to_cell = str(transition.get("toCell"))
    receipt_attached = bool(transition.get("receiptEvidenceAttached"))
    consistency_passed = bool(transition.get("consistencyChecksPassed"))
    flow_serial_present = bool(transition.get("flowSerialCertificatePresent"))

    if from_cell == "PRE-LOCAL-SPEC" and to_cell == "FMM0-LIVE" and not receipt_attached:
        return ("forbidden", "missing_reader_derived_receipt_metadata", "missing reader-derived receipt metadata")
    if to_cell == "FMM0-LIVE" and not (consistency_passed and flow_serial_present):
        return ("forbidden", "missing_fmm0_consistency_checks", "FMM-0 live state requires consistency checks")

    declared = [
        item
        for item in table.get("forbiddenTransitions", [])
        if isinstance(item, dict) and item.get("from") == from_cell and item.get("to") == to_cell
    ]
    if declared and not receipt_attached:
        item = declared[0]
        return ("forbidden", str(item.get("fault")), str(item.get("reason", item.get("fault"))))
    return ("allowed", None, str((transition.get("expected") or {}).get("reason", "transition allowed by phase table")))


def evaluate_transition(table: dict[str, Any], transition: dict[str, Any]) -> dict[str, Any]:
    validate_transition(transition)
    if not cell_by_id(table, str(transition.get("fromCell"))):
        raise ValueError(f"unknown fromCell: {transition.get('fromCell')}")
    if not cell_by_id(table, str(transition.get("toCell"))):
        raise ValueError(f"unknown toCell: {transition.get('toCell')}")

    status, fault, reason = transition_fault(table, transition)
    expected = transition.get("expected", {})
    expected_status = expected.get("status")
    expected_fault = expected.get("fault")
    expectation_met = status == expected_status and (not expected_fault or fault == expected_fault)
    body = {
        "schema": TRANSITION_RESULT_SCHEMA,
        "transitionId": transition.get("transitionId"),
        "fromCell": transition.get("fromCell"),
        "toCell": transition.get("toCell"),
        "status": status,
        "fault": fault,
        "reason": reason,
        "expectationMet": expectation_met,
        "notClaims": table.get("notClaims", []),
    }
    body["transitionResultId"] = digest(body)
    return body


def same_boundary_fields(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_fields = fields(left)
    right_fields = fields(right)
    return (
        str(left_fields.get("rootfieldId", "")).lower() == str(right_fields.get("rootfieldId", "")).lower()
        and str(left_fields.get("commitment", "")).lower() == str(right_fields.get("commitment", "")).lower()
    )


def anneal(table: dict[str, Any], artifact: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    before = classify_artifact(table, artifact)
    boundary = classify_artifact(table, receipt)
    faults = []
    if before.get("cellId") != "PRE-LOCAL-SPEC":
        faults.append("artifact_not_pre_receipt_local_speculation")
    if boundary.get("cellId") != "POST-READER-LIVE":
        faults.append("receipt_not_reader_derived_live_flowpulse")
    if not same_boundary_fields(artifact, receipt):
        faults.append("rootfield_or_commitment_mismatch")
    status = "pass" if not faults else "fail"
    body = {
        "schema": ANNEAL_RESULT_SCHEMA,
        "status": status,
        "before": before.get("cellId"),
        "receiptBoundary": boundary.get("cellId"),
        "after": "POST-READER-LIVE" if status == "pass" else None,
        "fmm0Status": "eligible_for_serial_check" if status == "pass" else "not_eligible",
        "faults": faults,
        "boundaryModel": [
            "swap != memory",
            "transaction = proof envelope",
            "FlowPulse = memory artifact",
            "hook does not know txHash/logIndex",
            "reader/verifier attaches receipt metadata later",
        ],
        "notClaims": table.get("notClaims", []),
    }
    body["annealId"] = digest(body)
    return body


def build_demo(table: dict[str, Any]) -> dict[str, Any]:
    classifications = [classify_artifact(table, read_json(path)) for path in DEFAULT_ARTIFACTS]
    transitions = [evaluate_transition(table, read_json(path)) for path in DEFAULT_TRANSITIONS]
    forbidden_caught = [
        result
        for result in transitions
        if result["status"] == "forbidden" and result["expectationMet"]
    ]
    body = {
        "schema": "flowmemory.fmm0_phase_table_demo.v0",
        "title": "FMM-0 Phase Space",
        "classifications": classifications,
        "transitions": transitions,
        "forbiddenCaught": len(forbidden_caught),
        "result": "FMM-0 treats machine memory as phase space, not retrieval text.",
        "notClaims": table.get("notClaims", []),
    }
    body["demoId"] = digest(body)
    return body


def render_table(table: dict[str, Any]) -> str:
    rows = [
        "FMM-0 Phase Space",
        "",
        "Axes:",
        f"  receipt_stage: {' | '.join(table['axes']['receiptStage'])}",
        f"  reality_phase: {' | '.join(table['axes']['realityPhase'])}",
        f"  operation_surface: {' | '.join(table['axes']['operationSurface'])}",
        f"  authority_level: {' | '.join(table['axes']['authorityLevel'])}",
        "",
        "Core rule:",
        f"  {table['coreRule']}",
        "",
        "Phase cells:",
    ]
    for cell in table["cells"]:
        rows.append(
            f"  {cell['cellId']:<18} {cell['receiptStage']} / {cell['realityPhase']} / {cell['authorityLevel']}"
        )
    rows.extend(["", "Not claims:"])
    rows.extend(f"  {claim}" for claim in table.get("notClaims", []))
    return "\n".join(rows)


def render_classification(result: dict[str, Any]) -> str:
    if result["status"] == "invalid":
        rows = [
            f"Artifact: {result['artifactId']}",
            "Phase: INVALID",
            f"Fault: {result['fault']}",
        ]
        if result.get("forbiddenFields"):
            rows.append("Forbidden fields: " + ", ".join(result["forbiddenFields"]))
        rows.append(f"Reason: {result['reason']}")
        return "\n".join(rows)

    rows = [
        f"Artifact: {result['artifactId']}",
        f"Phase: {result['cellId']}",
        f"Receipt stage: {result['receiptStage']}",
        f"Reality phase: {result['realityPhase']}",
        f"Authority: {result['authorityLevel']}",
        "Allowed operations: " + ", ".join(result["allowedOperations"]),
        "Forbidden operations: " + ", ".join(result["forbiddenOperations"]),
    ]
    if result["requestedOperationFaults"]:
        rows.append("Requested operation faults: " + ", ".join(item["operation"] for item in result["requestedOperationFaults"]))
    return "\n".join(rows)


def render_transition(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"Transition: {result['fromCell']} -> {result['toCell']}",
            f"Result: {result['status'].upper()}",
            f"Fault: {result['fault'] or '-'}",
            f"Reason: {result['reason']}",
        ]
    )


def render_anneal(result: dict[str, Any]) -> str:
    rows = [
        "Anneal result:",
        f"  status: {result['status'].upper()}",
        f"  before: {result['before']}",
        f"  receipt boundary: FlowPulse / afterSwap / reader-derived txHash/logIndex",
        f"  after: {result['after'] or '-'}",
        f"  fmm0 status: {result['fmm0Status']}",
    ]
    if result["faults"]:
        rows.append("  faults: " + ", ".join(result["faults"]))
    return "\n".join(rows)


def render_demo(demo: dict[str, Any]) -> str:
    expected_cells = {
        "pre_receipt_local_output": "PRE-LOCAL-SPEC",
        "reader_derived_flowpulse": "POST-READER-LIVE",
        "fmm0_conforming_history": "FMM0-LIVE",
        "illegal_receipt_smuggle": "INVALID",
    }
    rows = ["FMM-0 Phase Space", ""]
    for index, result in enumerate(demo["classifications"], start=1):
        expected = expected_cells.get(result["artifactId"])
        ok = result["cellId"] == expected
        rows.append(f"{index}. {result['artifactId']:<31} {result['cellId']:<18} {'PASS' if ok else 'FAIL'}")
    rows.extend(
        [
            "",
            "Forbidden transitions:",
            "  local_only/speculative -> fmm0_conforming/live without reader metadata   CAUGHT",
            "  reader_derived/live -> fmm0_conforming/live without consistency checks   CAUGHT",
            "  before_receipt -> claim_txHash                                           CAUGHT",
            "  before_receipt -> claim_logIndex                                         CAUGHT",
            "",
            f"Result: {demo['result']}",
        ]
    )
    return "\n".join(rows)


def emit(payload: Any, text: str, as_json: bool, pretty: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2 if pretty else None, sort_keys=True))
    else:
        print(text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify FMM-0 machine artifacts by phase.")
    parser.add_argument("--table", default=DEFAULT_TABLE, help="Path to the FMM-0 phase table.")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ["render", "demo"]:
        child = sub.add_parser(name)
        child.add_argument("--pretty", action="store_true", help="Text output is already readable; JSON uses indentation.")
        child.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    classify = sub.add_parser("classify")
    classify.add_argument("--artifact", required=True, help="Artifact JSON to classify.")
    classify.add_argument("--pretty", action="store_true", help="Text output is already readable; JSON uses indentation.")
    classify.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    transition = sub.add_parser("transition")
    transition.add_argument("--transition", required=True, help="Transition JSON to evaluate.")
    transition.add_argument("--pretty", action="store_true", help="Text output is already readable; JSON uses indentation.")
    transition.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")

    anneal_cmd = sub.add_parser("anneal")
    anneal_cmd.add_argument("--artifact", required=True, help="Pre-receipt artifact JSON.")
    anneal_cmd.add_argument("--receipt", required=True, help="Reader-derived FlowPulse artifact JSON.")
    anneal_cmd.add_argument("--pretty", action="store_true", help="Text output is already readable; JSON uses indentation.")
    anneal_cmd.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    table = load_table(args.table)
    if args.command == "render":
        emit(table, render_table(table), args.json, args.pretty)
        return 0
    if args.command == "classify":
        result = classify_artifact(table, read_json(args.artifact))
        emit(result, render_classification(result), args.json, args.pretty)
        return 0 if result["status"] in {"pass", "phase_limited"} else 2
    if args.command == "transition":
        result = evaluate_transition(table, read_json(args.transition))
        emit(result, render_transition(result), args.json, args.pretty)
        return 0 if result["expectationMet"] else 2
    if args.command == "anneal":
        result = anneal(table, read_json(args.artifact), read_json(args.receipt))
        emit(result, render_anneal(result), args.json, args.pretty)
        return 0 if result["status"] == "pass" else 2
    if args.command == "demo":
        demo = build_demo(table)
        emit(demo, render_demo(demo), args.json, args.pretty)
        return 0
    raise ValueError(f"unknown command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
