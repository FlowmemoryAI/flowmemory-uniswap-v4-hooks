#!/usr/bin/env python3
"""
FMM-0 Counterexample Forge.

Generates deterministic adversarial counterexamples against FMM-0 Phase Space
and verifies that the local model catches them.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable

try:  # pragma: no cover
    from tools import axiom_writ, fmm0_phase_table
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore
    import fmm0_phase_table  # type: ignore


RESULT_SCHEMA = "flowmemory.fmm0_counterexample_forge_result.v0"
COUNTEREXAMPLE_SCHEMA = "flowmemory.fmm0_counterexample.v0"
PRE_LOCAL = "examples/fmm0-phase-table/artifacts/pre_receipt_local_output.json"
READER_FLOWPULSE = "examples/fmm0-phase-table/artifacts/reader_derived_flowpulse.json"
INVALID_LOCAL_FMM0 = "examples/fmm0-phase-table/transitions/invalid_local_to_fmm0.json"
INVALID_READER_FMM0 = "examples/fmm0-phase-table/transitions/invalid_reader_to_fmm0_missing_checks.json"
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


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else repo_root() / candidate


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(resolve_path(path))


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def set_field(artifact: dict[str, Any], key: str, value: Any) -> dict[str, Any]:
    mutated = copy.deepcopy(artifact)
    mutated.setdefault("fields", {})[key] = value
    return mutated


def set_operations(artifact: dict[str, Any], operations: list[str]) -> dict[str, Any]:
    mutated = copy.deepcopy(artifact)
    mutated["requestedOperations"] = operations
    return mutated


def mutated_receipt_mismatch(receipt: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(receipt)
    mutated["fields"]["rootfieldId"] = "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    return mutated


def mutated_commitment_mismatch(receipt: dict[str, Any]) -> dict[str, Any]:
    mutated = copy.deepcopy(receipt)
    mutated["fields"]["commitment"] = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    return mutated


def remove_field(artifact: dict[str, Any], key: str) -> dict[str, Any]:
    mutated = copy.deepcopy(artifact)
    mutated.setdefault("fields", {}).pop(key, None)
    return mutated


def caught_classification(
    table: dict[str, Any],
    case_id: str,
    title: str,
    artifact: dict[str, Any],
    expected_fault: str,
) -> dict[str, Any]:
    result = fmm0_phase_table.classify_artifact(table, artifact)
    faults = []
    if result.get("fault"):
        faults.append(str(result["fault"]))
    faults.extend(str(item.get("fault")) for item in result.get("requestedOperationFaults", []))
    caught = expected_fault in faults
    return counterexample(case_id, title, "classification", expected_fault, faults, caught, result)


def caught_transition(
    table: dict[str, Any],
    case_id: str,
    title: str,
    transition: dict[str, Any],
    expected_fault: str,
) -> dict[str, Any]:
    result = fmm0_phase_table.evaluate_transition(table, transition)
    faults = [str(result["fault"])] if result.get("fault") else []
    caught = result.get("status") == "forbidden" and expected_fault in faults
    return counterexample(case_id, title, "transition", expected_fault, faults, caught, result)


def caught_anneal(
    table: dict[str, Any],
    case_id: str,
    title: str,
    artifact: dict[str, Any],
    receipt: dict[str, Any],
    expected_fault: str,
) -> dict[str, Any]:
    result = fmm0_phase_table.anneal(table, artifact, receipt)
    faults = [str(item) for item in result.get("faults", [])]
    caught = result.get("status") == "fail" and expected_fault in faults
    return counterexample(case_id, title, "anneal", expected_fault, faults, caught, result)


def counterexample(
    case_id: str,
    title: str,
    target: str,
    expected_fault: str,
    observed_faults: list[str],
    caught: bool,
    raw_result: dict[str, Any],
) -> dict[str, Any]:
    body = {
        "schema": COUNTEREXAMPLE_SCHEMA,
        "caseId": case_id,
        "title": title,
        "target": target,
        "expectedFault": expected_fault,
        "observedFaults": observed_faults,
        "caught": caught,
        "rawResultSchema": raw_result.get("schema"),
        "notClaims": NON_CLAIMS,
    }
    body["counterexampleId"] = digest(body)
    return body


def generate_cases(table: dict[str, Any]) -> list[dict[str, Any]]:
    pre_local = read_json(PRE_LOCAL)
    reader = read_json(READER_FLOWPULSE)
    return [
        caught_classification(
            table,
            "CE-001",
            "pre-receipt txHash smuggle",
            set_field(pre_local, "txHash", "0x" + "a" * 64),
            "receipt_field_smuggled_before_reader_attachment",
        ),
        caught_classification(
            table,
            "CE-002",
            "pre-receipt logIndex smuggle",
            set_field(pre_local, "logIndex", 7),
            "receipt_field_smuggled_before_reader_attachment",
        ),
        caught_classification(
            table,
            "CE-003",
            "pre-receipt receiptStatus smuggle",
            set_field(pre_local, "receiptStatus", "success"),
            "receipt_field_smuggled_before_reader_attachment",
        ),
        caught_classification(
            table,
            "CE-004",
            "local-only publish_as_live",
            set_operations(pre_local, ["publish_as_live"]),
            "operation_forbidden_in_phase",
        ),
        caught_transition(
            table,
            "CE-005",
            "local-only -> FMM-0 live without receipt metadata",
            read_json(INVALID_LOCAL_FMM0),
            "missing_reader_derived_receipt_metadata",
        ),
        caught_transition(
            table,
            "CE-006",
            "reader-derived -> FMM-0 live without consistency",
            read_json(INVALID_READER_FMM0),
            "missing_fmm0_consistency_checks",
        ),
        caught_classification(
            table,
            "CE-007",
            "reader-derived FlowPulse missing txHash",
            remove_field(reader, "txHash"),
            "missing_reader_derived_receipt_metadata",
        ),
        caught_classification(
            table,
            "CE-008",
            "reader-derived FlowPulse missing logIndex",
            remove_field(reader, "logIndex"),
            "missing_reader_derived_receipt_metadata",
        ),
        caught_anneal(
            table,
            "CE-009",
            "rootfield mismatch",
            pre_local,
            mutated_receipt_mismatch(reader),
            "rootfield_or_commitment_mismatch",
        ),
        caught_anneal(
            table,
            "CE-010",
            "commitment mismatch",
            pre_local,
            mutated_commitment_mismatch(reader),
            "rootfield_or_commitment_mismatch",
        ),
        caught_classification(
            table,
            "CE-011",
            "reader-derived semantic truth overclaim",
            set_operations(reader, ["claim_semantic_truth"]),
            "operation_forbidden_in_phase",
        ),
        caught_classification(
            table,
            "CE-012",
            "reader-derived model correctness overclaim",
            set_operations(reader, ["claim_model_correctness"]),
            "operation_forbidden_in_phase",
        ),
    ]


def build_report() -> dict[str, Any]:
    table = fmm0_phase_table.load_table()
    cases = generate_cases(table)
    caught = sum(1 for item in cases if item["caught"])
    body = {
        "schema": RESULT_SCHEMA,
        "title": "FMM-0 Counterexample Forge",
        "status": "pass" if caught == len(cases) else "fail",
        "generatedCounterexamples": len(cases),
        "caughtByFmm0": caught,
        "escaped": len(cases) - caught,
        "uncaught": len(cases) - caught,
        "cases": cases,
        "result": "FMM-0 is not just a claim; it has adversarial counterexamples.",
        "notClaims": NON_CLAIMS,
    }
    body["forgeId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = [
        "FMM-0 Counterexample Forge",
        "",
        f"Generated counterexamples: {report['generatedCounterexamples']}",
        f"Caught by FMM-0: {report['caughtByFmm0']}/{report['generatedCounterexamples']}",
        f"Escaped: {report['escaped']}",
        "",
    ]
    for item in report["cases"]:
        status = "CAUGHT" if item["caught"] else "MISSED"
        faults = ", ".join(item["observedFaults"]) or "-"
        rows.append(f"{item['caseId']} {item['title']:<55} {status:<6} {faults}")
    rows.extend(["", f"Result: {report['result']}"])
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FMM-0 adversarial counterexamples.")
    parser.add_argument("command", choices=["demo", "generate"], help="Run or write the counterexample demo.")
    parser.add_argument("--out", help="Directory for generated counterexample JSON files.")
    parser.add_argument("--pretty", action="store_true", help="Text output is already readable; JSON uses indentation.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.command == "generate":
        if not args.out:
            raise ValueError("generate requires --out")
        output_dir = Path(args.out)
        if not output_dir.is_absolute():
            output_dir = repo_root() / output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "report.json").write_text(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
        case_dir = output_dir / "cases"
        case_dir.mkdir(exist_ok=True)
        for item in report["cases"]:
            (case_dir / f"{item['caseId']}.json").write_text(json.dumps(item, indent=2 if args.pretty else None, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {report['generatedCounterexamples']} counterexamples to {output_dir}")
        return 0 if report["status"] == "pass" else 2
    if args.json:
        print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(render_report(report))
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
