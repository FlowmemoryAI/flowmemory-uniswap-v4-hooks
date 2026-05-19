#!/usr/bin/env python3
"""
FlowLitmus: executable forbidden outcomes for FlowMemory runtime semantics.

FlowLitmus runs named consistency cases against the local FlowMemory R&D tools.
It is a launch-facing conformance suite: the repo can show which machine
histories are impossible once FlowPulse receipt boundaries exist.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ, boundary_fission, flow_mmu, flow_quiesce, flow_serial, pulse_retire
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore
    import boundary_fission  # type: ignore
    import flow_mmu  # type: ignore
    import flow_quiesce  # type: ignore
    import flow_serial  # type: ignore
    import pulse_retire  # type: ignore


CASE_SCHEMA = "flowmemory.flow_litmus_case.v0"
RESULT_SCHEMA = "flowmemory.flow_litmus_result.v0"
SUITE_SCHEMA = "flowmemory.flow_litmus_suite.v0"
SUITE_RESULT_SCHEMA = "flowmemory.flow_litmus_suite_result.v0"
RUNNERS = {
    "flow_mmu_pre_receipt_read",
    "flow_serial",
    "flow_quiesce_open_certificate",
    "pulse_retire_enforcement",
    "boundary_fission_stale_survival",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def write_json(payload: Any, output: str | None, pretty: bool) -> None:
    axiom_writ.write_json(payload, output, pretty)


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def non_claims() -> list[str]:
    return [
        "not_semantic_truth",
        "not_model_correctness",
        "not_gpu_attestation",
        "not_hardware_acceleration",
        "not_swap_control",
        "not_custody",
        "not_fund_protection",
        "not_live_mainnet_claim",
        "not_production_safety_claim",
    ]


def resolve_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return repo_root() / candidate


def require_case(case: dict[str, Any]) -> None:
    if case.get("schema") != CASE_SCHEMA:
        raise ValueError("FlowLitmus case schema mismatch")
    if not case.get("caseId"):
        raise ValueError("FlowLitmus case missing caseId")
    if case.get("runner") not in RUNNERS:
        raise ValueError("FlowLitmus case has unknown runner")
    expected = case.get("expected")
    if not isinstance(expected, dict) or not expected.get("outcome"):
        raise ValueError("FlowLitmus case missing expected outcome")


def flow_serial_observation(case: dict[str, Any]) -> dict[str, Any]:
    history = read_json(resolve_path(case["artifacts"]["history"]))
    output = flow_serial.certify(history)
    if output.get("schema") == flow_serial.CERT_SCHEMA:
        return {
            "outcome": "valid_history_accepted",
            "faultTypes": ["Serializable"],
            "artifactSchema": output.get("schema"),
            "artifactId": output.get("certificateId"),
            "reason": "machine history serialized around FlowPulse receipt boundary",
        }
    return {
        "outcome": "forbidden_outcome_detected",
        "faultTypes": [output.get("faultType")],
        "artifactSchema": output.get("schema"),
        "artifactId": output.get("faultId"),
        "reason": output.get("reason"),
    }


def flow_mmu_observation(case: dict[str, Any]) -> dict[str, Any]:
    artifacts = case["artifacts"]
    output = flow_mmu.deref(read_json(resolve_path(artifacts["table"])), artifacts["pointerId"], artifacts.get("field", "txHash"))
    if output.get("schema") == flow_mmu.FAULT_SCHEMA:
        return {
            "outcome": "forbidden_outcome_detected",
            "faultTypes": [output.get("faultType")],
            "artifactSchema": output.get("schema"),
            "artifactId": output.get("faultId"),
            "reason": output.get("reason"),
        }
    return {
        "outcome": "valid_history_accepted",
        "faultTypes": ["ReceiptReadAllowed"],
        "artifactSchema": output.get("schema"),
        "artifactId": output.get("readId"),
        "reason": "receipt field read was allowed",
    }


def flow_quiesce_observation(case: dict[str, Any]) -> dict[str, Any]:
    cert = read_json(resolve_path(case["artifacts"]["certificate"]))
    if cert.get("schema") != flow_quiesce.CERT_SCHEMA:
        raise ValueError("quiescence artifact is not a certificate")
    if not cert.get("safeToJoinPostBoundaryState"):
        return {
            "outcome": "forbidden_outcome_detected",
            "faultTypes": ["QuiescenceViolation"],
            "artifactSchema": cert.get("schema"),
            "artifactId": cert.get("certificateId"),
            "reason": "post-boundary output is unsafe while the quiescence grace period is open",
        }
    return {
        "outcome": "valid_history_accepted",
        "faultTypes": ["QuiescenceClosed"],
        "artifactSchema": cert.get("schema"),
        "artifactId": cert.get("certificateId"),
        "reason": "all required frames reached a safe point",
    }


def pulse_retire_observation(case: dict[str, Any]) -> dict[str, Any]:
    enforcement = read_json(resolve_path(case["artifacts"]["enforcement"]))
    if enforcement.get("schema") != "flowmemory.pulse_retire_enforcement.v0":
        raise ValueError("pulse-retire artifact is not an enforcement result")
    if not enforcement.get("allowed"):
        return {
            "outcome": "forbidden_outcome_detected",
            "faultTypes": ["RetirementViolation"],
            "artifactSchema": enforcement.get("schema"),
            "artifactId": enforcement.get("artifactId"),
            "reason": enforcement.get("reason"),
        }
    return {
        "outcome": "valid_history_accepted",
        "faultTypes": ["RetiredArtifactAllowed"],
        "artifactSchema": enforcement.get("schema"),
        "artifactId": enforcement.get("artifactId"),
        "reason": "artifact was retired before live use",
    }


def boundary_fission_observation(case: dict[str, Any]) -> dict[str, Any]:
    report = read_json(resolve_path(case["artifacts"]["report"]))
    verification = boundary_fission.verify_report(report)
    after = report.get("memoryAfter", {}) if isinstance(report.get("memoryAfter"), dict) else {}
    stale_survived = after.get("rawTextPresent") or after.get("executableOnchainActionPresent") or after.get("unsupportedIntentInferencePresent")
    if verification.get("status") == "valid" and not stale_survived:
        return {
            "outcome": "forbidden_outcome_detected",
            "faultTypes": ["BoundaryFissionViolation"],
            "artifactSchema": report.get("schema"),
            "artifactId": report.get("fissionId"),
            "reason": "stale or unsupported working-memory payloads were prevented from surviving the boundary",
        }
    return {
        "outcome": "unexpected_outcome",
        "faultTypes": ["StaleMemorySurvived"],
        "artifactSchema": report.get("schema"),
        "artifactId": report.get("fissionId"),
        "reason": "stale working memory appears to have survived the boundary",
    }


def observe(case: dict[str, Any]) -> dict[str, Any]:
    runner = case.get("runner")
    if runner == "flow_serial":
        return flow_serial_observation(case)
    if runner == "flow_mmu_pre_receipt_read":
        return flow_mmu_observation(case)
    if runner == "flow_quiesce_open_certificate":
        return flow_quiesce_observation(case)
    if runner == "pulse_retire_enforcement":
        return pulse_retire_observation(case)
    if runner == "boundary_fission_stale_survival":
        return boundary_fission_observation(case)
    raise ValueError("unknown FlowLitmus runner")


def expected_matches(observed: dict[str, Any], expected: dict[str, Any]) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if observed.get("outcome") != expected.get("outcome"):
        problems.append("outcome_mismatch")
    expected_faults = set(str(item) for item in expected.get("faultTypes", []))
    observed_faults = set(str(item) for item in observed.get("faultTypes", []))
    if expected_faults and expected_faults != observed_faults:
        problems.append("fault_type_mismatch")
    return not problems, problems


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    require_case(case)
    observed = observe(case)
    expected = case["expected"]
    ok, problems = expected_matches(observed, expected)
    body = {
        "schema": RESULT_SCHEMA,
        "caseId": case.get("caseId"),
        "title": case.get("title"),
        "category": case.get("category"),
        "status": "pass" if ok else "fail",
        "observed": observed,
        "expected": expected,
        "problems": problems,
        "invariant": case.get("invariant"),
        "whyFlowPulseMatters": case.get("whyFlowPulseMatters"),
        "notClaims": non_claims(),
    }
    body["resultId"] = digest(body)
    return body


def read_suite(manifest_path: str | Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    if manifest.get("schema") != SUITE_SCHEMA:
        raise ValueError("FlowLitmus manifest schema mismatch")
    if not isinstance(manifest.get("cases"), list) or not manifest["cases"]:
        raise ValueError("FlowLitmus manifest contains no cases")
    return manifest


def run_suite(manifest_path: str | Path) -> dict[str, Any]:
    manifest = read_suite(manifest_path)
    results = [run_case(read_json(resolve_path(path))) for path in manifest["cases"]]
    passed = sum(1 for result in results if result.get("status") == "pass")
    body = {
        "schema": SUITE_RESULT_SCHEMA,
        "suiteId": manifest.get("suiteId"),
        "title": manifest.get("title"),
        "status": "pass" if passed == len(results) else "fail",
        "passed": passed,
        "failed": len(results) - passed,
        "total": len(results),
        "results": results,
        "notClaims": non_claims(),
    }
    body["suiteResultId"] = digest(body)
    return body


def render_table(suite_result: dict[str, Any]) -> str:
    rows = ["FlowLitmus Runtime Consistency Suite", ""]
    for result in suite_result.get("results", []):
        observed = result.get("observed", {})
        fault = ", ".join(str(item) for item in observed.get("faultTypes", []))
        rows.append(f"{result.get('caseId', ''):<11} {str(result.get('title', '')):<38} {result.get('status', '').upper():<5} {fault}")
    rows.extend(["", f"{suite_result.get('passed')}/{suite_result.get('total')} passed"])
    return "\n".join(rows)


def explain(case: dict[str, Any]) -> str:
    require_case(case)
    forbidden = case.get("forbiddenOutcome", {}) if isinstance(case.get("forbiddenOutcome"), dict) else {}
    expected = case.get("expected", {}) if isinstance(case.get("expected"), dict) else {}
    return "\n".join(
        [
            f"Case: {case.get('caseId')} - {case.get('title')}",
            "",
            "Invariant:",
            f"  {case.get('invariant')}",
            "",
            "Why FlowPulse matters:",
            f"  {case.get('whyFlowPulseMatters')}",
            "",
            "Forbidden outcome:",
            f"  {forbidden.get('description')}",
            "",
            "Expected:",
            f"  {expected.get('outcome')} / {', '.join(str(item) for item in expected.get('faultTypes', []))}",
        ]
    )


def example_dir() -> Path:
    return repo_root() / "examples" / "flow-litmus"


def demo() -> dict[str, Any]:
    return run_suite(example_dir() / "litmus.manifest.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FlowLitmus runtime consistency suite.")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--suite", required=True)
    run.add_argument("--out")
    run.add_argument("--pretty", action="store_true")
    run.add_argument("--json", action="store_true")
    case = sub.add_parser("run-case")
    case.add_argument("--case", required=True)
    case.add_argument("--out")
    case.add_argument("--pretty", action="store_true")
    case.add_argument("--json", action="store_true")
    explain_cmd = sub.add_parser("explain")
    explain_cmd.add_argument("--case", required=True)
    demo_cmd = sub.add_parser("demo")
    demo_cmd.add_argument("--pretty", action="store_true")
    demo_cmd.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "run":
            result = run_suite(args.suite)
            if args.json or args.out:
                write_json(result, args.out, args.pretty)
            else:
                print(render_table(result))
            return 0 if result["status"] == "pass" else 2
        if args.command == "run-case":
            result = run_case(read_json(args.case))
            if args.json or args.out:
                write_json(result, args.out, args.pretty)
            else:
                print(render_table({"results": [result], "passed": 1 if result["status"] == "pass" else 0, "total": 1}))
            return 0 if result["status"] == "pass" else 2
        if args.command == "explain":
            print(explain(read_json(args.case)))
            return 0
        if args.command == "demo":
            result = demo()
            if args.json:
                write_json(result, None, args.pretty)
            else:
                print(render_table(result))
            return 0 if result["status"] == "pass" else 2
    except ValueError as error:
        write_json({"schema": "flowmemory.flow_litmus_error.v0", "error": str(error)}, None, True)
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
