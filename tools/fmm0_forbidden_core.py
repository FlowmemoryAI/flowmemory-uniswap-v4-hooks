#!/usr/bin/env python3
"""
FMM-0 Forbidden Core Extractor.

Shrinks invalid FMM-0 machine artifacts into minimal mutation cores that still
produce the same forbidden fault. This is deterministic diagnostic minimization,
not formal verification.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ, fmm0_counterexample_forge, fmm0_phase_table
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore
    import fmm0_counterexample_forge  # type: ignore
    import fmm0_phase_table  # type: ignore


REPORT_SCHEMA = "flowmemory.fmm0_forbidden_core_report.v0"
CORE_RESULT_SCHEMA = "flowmemory.fmm0_forbidden_core_result.v0"
MANIFEST_SCHEMA = "flowmemory.fmm0_forbidden_core_manifest.v0"
MANIFEST_PATH = "examples/fmm0-forbidden-core/core-manifest.json"
PRE_LOCAL = "examples/fmm0-phase-table/artifacts/pre_receipt_local_output.json"
READER_FLOWPULSE = "examples/fmm0-phase-table/artifacts/reader_derived_flowpulse.json"
VALID_ATTACHMENT = "examples/fmm0-phase-table/transitions/valid_reader_attachment.json"
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
    "model correctness guaranteed",
    "gpu acceleration",
    "base mainnet",
    "audited custody",
    "fund protection",
    "production verifier",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(fmm0_phase_table.resolve_path(path))


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def get_path(root: dict[str, Any], path: str) -> Any:
    cursor: Any = root
    for part in path.split("."):
        if not isinstance(cursor, dict) or part not in cursor:
            return None
        cursor = cursor[part]
    return cursor


def set_path(root: dict[str, Any], path: str, value: Any) -> None:
    cursor: dict[str, Any] = root
    parts = path.split(".")
    for part in parts[:-1]:
        existing = cursor.get(part)
        if not isinstance(existing, dict):
            existing = {}
            cursor[part] = existing
        cursor = existing
    cursor[parts[-1]] = value


def del_path(root: dict[str, Any], path: str) -> None:
    cursor: Any = root
    parts = path.split(".")
    for part in parts[:-1]:
        cursor = cursor.get(part) if isinstance(cursor, dict) else None
        if cursor is None:
            return
    if isinstance(cursor, dict):
        cursor.pop(parts[-1], None)


def apply_atoms(base: dict[str, Any], atoms: list[dict[str, Any]]) -> dict[str, Any]:
    value = copy.deepcopy(base)
    for atom in atoms:
        if atom.get("absent"):
            del_path(value, str(atom["path"]))
        else:
            set_path(value, str(atom["path"]), copy.deepcopy(atom.get("value")))
    return value


def observed_fault(kind: str, value: dict[str, Any]) -> str | None:
    table = fmm0_phase_table.load_table()
    if kind == "classification":
        result = fmm0_phase_table.classify_artifact(table, value)
        if result.get("fault"):
            return str(result["fault"])
        faults = [str(item.get("fault")) for item in result.get("requestedOperationFaults", [])]
        return faults[0] if faults else None
    if kind == "transition":
        result = fmm0_phase_table.evaluate_transition(table, value)
        return str(result["fault"]) if result.get("fault") else None
    if kind == "anneal_rootfield":
        artifact = read_json(PRE_LOCAL)
        result = fmm0_phase_table.anneal(table, artifact, value)
        faults = [str(item) for item in result.get("faults", [])]
        return faults[0] if faults else None
    raise ValueError(f"unsupported forbidden core kind: {kind}")


def extract_core(case_def: dict[str, Any]) -> dict[str, Any]:
    atoms = [copy.deepcopy(atom) for atom in case_def["atoms"]]
    expected_fault = str(case_def["expectedFault"])
    kind = str(case_def["kind"])
    full_value = apply_atoms(case_def["base"], atoms)
    full_fault = observed_fault(kind, full_value)
    if full_fault != expected_fault:
        return result(case_def, atoms, full_fault, "expected_fault_not_observed", False)

    core = atoms[:]
    changed = True
    while changed:
        changed = False
        for index in range(len(core)):
            candidate = core[:index] + core[index + 1 :]
            candidate_fault = observed_fault(kind, apply_atoms(case_def["base"], candidate))
            if candidate_fault == expected_fault:
                core = candidate
                changed = True
                break

    one_minimal = True
    for index in range(len(core)):
        candidate = core[:index] + core[index + 1 :]
        if observed_fault(kind, apply_atoms(case_def["base"], candidate)) == expected_fault:
            one_minimal = False
            break

    return result(case_def, core, expected_fault, "minimal_core_found", one_minimal)


def result(
    case_def: dict[str, Any],
    core: list[dict[str, Any]],
    observed: str | None,
    status: str,
    one_minimal: bool,
) -> dict[str, Any]:
    core_paths = {str(atom["path"]) for atom in core}
    removed = [str(atom["path"]) for atom in case_def["atoms"] if str(atom["path"]) not in core_paths]
    body = {
        "schema": CORE_RESULT_SCHEMA,
        "caseId": case_def["caseId"],
        "name": case_def["name"],
        "kind": case_def["kind"],
        "status": status,
        "expectedFault": case_def["expectedFault"],
        "observedFault": observed,
        "fullAtomCount": len(case_def["atoms"]),
        "coreAtomCount": len(core),
        "minimality": "one_minimal" if one_minimal else "not_minimal",
        "minimalCore": core,
        "removedAtoms": removed,
        "meaning": case_def["meaning"],
        "notClaims": NON_CLAIMS,
    }
    body["coreId"] = digest(body)
    return body


def atom(path: str, value: Any = None, *, absent: bool = False) -> dict[str, Any]:
    body = {"path": path}
    if absent:
        body["absent"] = True
    else:
        body["value"] = value
    return body


def base_classification() -> dict[str, Any]:
    return {
        "schema": fmm0_phase_table.ARTIFACT_SCHEMA,
        "artifactId": "forbidden_core_candidate",
        "artifactType": "FlowPulse",
        "receiptStage": "after_receipt",
        "realityPhase": "live",
        "authorityLevel": "reader_derived",
        "fields": {
            "rootfieldId": "0x" + "11" * 32,
            "commitment": "0x" + "22" * 32,
        },
        "requestedOperations": ["cite_receipt_fact"],
    }


def build_cases() -> list[dict[str, Any]]:
    reader = read_json(READER_FLOWPULSE)
    valid_attachment = read_json(VALID_ATTACHMENT)
    valid_fmm0 = read_json(VALID_FMM0)
    return [
        {
            "caseId": "CORE-001",
            "name": "pre_receipt_txHash_smuggle",
            "kind": "classification",
            "base": base_classification(),
            "atoms": [
                atom("receiptStage", "before_receipt"),
                atom("authorityLevel", "local_only"),
                atom("fields.txHash", "0x" + "aa" * 32),
                atom("fields.rootfieldId", "0x" + "11" * 32),
                atom("fields.commitment", "0x" + "22" * 32),
            ],
            "expectedFault": "receipt_field_smuggled_before_reader_attachment",
            "meaning": "A before-receipt artifact cannot contain reader-derived txHash.",
        },
        {
            "caseId": "CORE-002",
            "name": "pre_receipt_logIndex_smuggle",
            "kind": "classification",
            "base": base_classification(),
            "atoms": [
                atom("receiptStage", "before_receipt"),
                atom("authorityLevel", "local_only"),
                atom("fields.logIndex", 7),
                atom("fields.rootfieldId", "0x" + "11" * 32),
                atom("fields.commitment", "0x" + "22" * 32),
            ],
            "expectedFault": "receipt_field_smuggled_before_reader_attachment",
            "meaning": "A before-receipt artifact cannot contain reader-derived logIndex.",
        },
        {
            "caseId": "CORE-003",
            "name": "local_to_fmm0_without_reader",
            "kind": "transition",
            "base": valid_attachment,
            "atoms": [
                atom("toCell", "FMM0-LIVE"),
                atom("receiptEvidenceAttached", False),
                atom("consistencyChecksPassed", False),
                atom("flowSerialCertificatePresent", False),
            ],
            "expectedFault": "missing_reader_derived_receipt_metadata",
            "meaning": "Local speculative state cannot jump to FMM-0 live without reader-derived receipt metadata.",
        },
        {
            "caseId": "CORE-004",
            "name": "reader_to_fmm0_without_serial",
            "kind": "transition",
            "base": valid_fmm0,
            "atoms": [
                atom("consistencyChecksPassed", False),
                atom("flowSerialCertificatePresent", False),
                atom("receiptEvidenceAttached", True),
                atom("toCell", "FMM0-LIVE"),
            ],
            "expectedFault": "missing_fmm0_consistency_checks",
            "meaning": "Reader-derived evidence cannot become FMM-0 live without consistency evidence.",
        },
        {
            "caseId": "CORE-005",
            "name": "reader_flowpulse_missing_txHash",
            "kind": "classification",
            "base": reader,
            "atoms": [
                atom("fields.txHash", absent=True),
                atom("authorityLevel", "reader_derived"),
                atom("receiptStage", "after_receipt"),
                atom("realityPhase", "live"),
            ],
            "expectedFault": "missing_reader_derived_receipt_metadata",
            "meaning": "Reader-derived FlowPulse evidence cannot omit txHash.",
        },
        {
            "caseId": "CORE-006",
            "name": "reader_flowpulse_missing_logIndex",
            "kind": "classification",
            "base": reader,
            "atoms": [
                atom("fields.logIndex", absent=True),
                atom("authorityLevel", "reader_derived"),
                atom("receiptStage", "after_receipt"),
                atom("realityPhase", "live"),
            ],
            "expectedFault": "missing_reader_derived_receipt_metadata",
            "meaning": "Reader-derived FlowPulse evidence cannot omit logIndex.",
        },
        {
            "caseId": "CORE-007",
            "name": "rootfield_drift",
            "kind": "anneal_rootfield",
            "base": reader,
            "atoms": [
                atom("fields.rootfieldId", "0x" + "99" * 32),
                atom("fields.commitment", get_path(reader, "fields.commitment")),
                atom("fields.txHash", get_path(reader, "fields.txHash")),
            ],
            "expectedFault": "rootfield_or_commitment_mismatch",
            "meaning": "Reader receipt evidence cannot anneal a local draft with a different rootfield.",
        },
        {
            "caseId": "CORE-008",
            "name": "commitment_drift",
            "kind": "anneal_rootfield",
            "base": reader,
            "atoms": [
                atom("fields.commitment", "0x" + "88" * 32),
                atom("fields.rootfieldId", get_path(reader, "fields.rootfieldId")),
                atom("fields.txHash", get_path(reader, "fields.txHash")),
            ],
            "expectedFault": "rootfield_or_commitment_mismatch",
            "meaning": "Reader receipt evidence cannot anneal a local draft with a different commitment.",
        },
        {
            "caseId": "CORE-009",
            "name": "semantic_truth_operation",
            "kind": "classification",
            "base": reader,
            "atoms": [
                atom("requestedOperations", ["claim_semantic_truth"]),
                atom("authorityLevel", "reader_derived"),
                atom("receiptStage", "after_receipt"),
            ],
            "expectedFault": "operation_forbidden_in_phase",
            "meaning": "FlowPulse evidence does not verify semantic truth.",
        },
        {
            "caseId": "CORE-010",
            "name": "model_correctness_operation",
            "kind": "classification",
            "base": reader,
            "atoms": [
                atom("requestedOperations", ["claim_model_correctness"]),
                atom("authorityLevel", "reader_derived"),
                atom("receiptStage", "after_receipt"),
            ],
            "expectedFault": "operation_forbidden_in_phase",
            "meaning": "FlowPulse evidence does not prove model correctness.",
        },
    ]


def load_manifest(path: str | Path = MANIFEST_PATH) -> dict[str, Any]:
    manifest = read_json(path)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError(f"unsupported forbidden core manifest schema: {manifest.get('schema')}")
    ids = {item["caseId"] for item in build_cases()}
    manifest_ids = {item.get("caseId") for item in manifest.get("cases", [])}
    missing = ids - manifest_ids
    if missing:
        raise ValueError(f"forbidden core manifest missing cases: {sorted(missing)}")
    return manifest


def build_report() -> dict[str, Any]:
    load_manifest()
    results = [extract_core(case_def) for case_def in build_cases()]
    minimal = sum(1 for item in results if item["status"] == "minimal_core_found")
    one_minimal = sum(1 for item in results if item["minimality"] == "one_minimal")
    escaped = len(results) - minimal
    body = {
        "schema": REPORT_SCHEMA,
        "title": "FMM-0 Forbidden Core Extractor",
        "status": "pass" if escaped == 0 and one_minimal == len(results) else "fail",
        "invalidHistoriesChecked": len(results),
        "minimalCoresFound": minimal,
        "oneMinimalCores": one_minimal,
        "escapedFaults": escaped,
        "results": results,
        "result": "FMM-0 can reduce impossible machine histories to minimal forbidden cores.",
        "notClaims": NON_CLAIMS,
    }
    body["forbiddenCoreReportId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = ["FMM-0 Forbidden Core Extractor", "", "Cases:"]
    for item in report["results"]:
        status = "CORE" if item["status"] == "minimal_core_found" else "MISS"
        rows.append(
            f"  {item['caseId']} {item['name']:<42} {status:<4} "
            f"{item['coreAtomCount']}/{item['fullAtomCount']} atoms  {item['minimality'].replace('_', '-')}"
        )
    rows.extend(
        [
            "",
            "Summary:",
            f"  invalid histories checked: {report['invalidHistoriesChecked']}",
            f"  minimal cores found: {report['minimalCoresFound']}/{report['invalidHistoriesChecked']}",
            f"  one-minimal cores: {report['oneMinimalCores']}/{report['invalidHistoriesChecked']}",
            f"  escaped faults: {report['escapedFaults']}",
            "",
            "Result:",
            f"  {report['result']}",
        ]
    )
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract minimal forbidden cores from FMM-0 invalid histories.")
    parser.add_argument("command", choices=["demo"], help="Run the forbidden core demo.")
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
