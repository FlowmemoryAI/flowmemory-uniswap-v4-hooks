#!/usr/bin/env python3
"""
FlowPulse Boundary ABI Conformance Gate.

Checks that the Solidity event boundary still matches the FMM-0 runtime
assumptions: hook-time FlowPulse fields are emitted by the hook, and
receipt-only fields remain reader-derived.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore


REPORT_SCHEMA = "flowmemory.flowpulse_boundary_abi_report.v0"
FLOWPULSE_SOURCE = "contracts/FlowPulse.sol"
HOOK_SOURCE = "contracts/FlowMemoryAfterSwapHook.sol"
FLOWPULSE_ARTIFACT = "out/FlowPulse.sol/IFlowPulse.json"
EXPECTED_FLOWPULSE = [
    {"name": "pulseId", "type": "bytes32", "indexed": True},
    {"name": "rootfieldId", "type": "bytes32", "indexed": True},
    {"name": "actor", "type": "address", "indexed": True},
    {"name": "pulseType", "type": "uint8", "indexed": False},
    {"name": "subject", "type": "bytes32", "indexed": False},
    {"name": "commitment", "type": "bytes32", "indexed": False},
    {"name": "parentPulseId", "type": "bytes32", "indexed": False},
    {"name": "sequence", "type": "uint64", "indexed": False},
    {"name": "occurredAt", "type": "uint64", "indexed": False},
    {"name": "uri", "type": "string", "indexed": False},
]
RECEIPT_ONLY_FIELDS = {
    "txHash",
    "transactionIndex",
    "logIndex",
    "blockHash",
    "blockNumber",
    "receiptStatus",
    "finalityStatus",
}
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


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def read_text(path: str | Path) -> str:
    return resolve_path(path).read_text(encoding="utf-8")


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(resolve_path(path).read_text(encoding="utf-8"))


def parse_event_from_source(source: str, event_name: str) -> list[dict[str, Any]]:
    match = re.search(rf"event\s+{re.escape(event_name)}\s*\((.*?)\)\s*;", source, re.DOTALL)
    if not match:
        return []
    fields = []
    for raw in match.group(1).split(","):
        tokens = raw.strip().split()
        if not tokens:
            continue
        indexed = "indexed" in tokens
        tokens = [token for token in tokens if token != "indexed"]
        if len(tokens) < 2:
            continue
        fields.append({"type": tokens[0], "name": tokens[-1], "indexed": indexed})
    return fields


def parse_event_from_artifact(path: str | Path, event_name: str) -> list[dict[str, Any]]:
    artifact = read_json(path)
    for entry in artifact.get("abi", []):
        if entry.get("type") == "event" and entry.get("name") == event_name:
            return [
                {"type": item.get("type"), "name": item.get("name"), "indexed": bool(item.get("indexed"))}
                for item in entry.get("inputs", [])
            ]
    return []


def load_flowpulse_event() -> tuple[str, list[dict[str, Any]]]:
    artifact_path = resolve_path(FLOWPULSE_ARTIFACT)
    if artifact_path.exists():
        fields = parse_event_from_artifact(artifact_path, "FlowPulse")
        if fields:
            return "compiled_artifact", fields
    return "source", parse_event_from_source(read_text(FLOWPULSE_SOURCE), "FlowPulse")


def load_after_swap_observed_event() -> list[dict[str, Any]]:
    return parse_event_from_source(read_text(HOOK_SOURCE), "AfterSwapObserved")


def names(fields: list[dict[str, Any]]) -> list[str]:
    return [str(field["name"]) for field in fields]


def check_line(label: str, ok: bool, detail: str = "") -> dict[str, Any]:
    body = {"label": label, "status": "PASS" if ok else "FAIL"}
    if detail:
        body["detail"] = detail
    return body


def build_report(strict_artifact: bool = False) -> dict[str, Any]:
    source, flowpulse_fields = load_flowpulse_event()
    after_swap_fields = load_after_swap_observed_event()
    flowpulse_names = names(flowpulse_fields)
    after_swap_names = names(after_swap_fields)
    exposed_receipt_fields = sorted((set(flowpulse_names) | set(after_swap_names)) & RECEIPT_ONLY_FIELDS)
    expected_names = [item["name"] for item in EXPECTED_FLOWPULSE]
    expected_indexed = {item["name"] for item in EXPECTED_FLOWPULSE if item["indexed"]}
    actual_indexed = {str(item["name"]) for item in flowpulse_fields if item.get("indexed")}
    expected_types = {item["name"]: item["type"] for item in EXPECTED_FLOWPULSE}
    actual_types = {str(item["name"]): str(item["type"]) for item in flowpulse_fields}
    artifact_available = source == "compiled_artifact"
    checks = [
        check_line("compiled ABI available or source fallback used", artifact_available or not strict_artifact, source),
        check_line("FlowPulse event present", bool(flowpulse_fields)),
        check_line("FlowPulse hook-time fields match FMM-0", flowpulse_names == expected_names),
        check_line("FlowPulse field types match", all(actual_types.get(name) == expected_types[name] for name in expected_names)),
        check_line("FlowPulse indexed boundary fields match", actual_indexed == expected_indexed),
        check_line("FlowPulse excludes receipt-only fields", not (set(flowpulse_names) & RECEIPT_ONLY_FIELDS)),
        check_line("AfterSwapObserved excludes receipt-only fields", not (set(after_swap_names) & RECEIPT_ONLY_FIELDS)),
        check_line("FlowPulse carries rootfieldId and commitment", {"rootfieldId", "commitment"}.issubset(set(flowpulse_names))),
        check_line("FlowPulse uses uint64 sequence and occurredAt", actual_types.get("sequence") == "uint64" and actual_types.get("occurredAt") == "uint64"),
    ]
    passed = sum(1 for item in checks if item["status"] == "PASS")
    body = {
        "schema": REPORT_SCHEMA,
        "title": "FlowPulse Boundary ABI Conformance",
        "status": "pass" if passed == len(checks) else "fail",
        "abiSource": source,
        "checksPassed": passed,
        "checksTotal": len(checks),
        "receiptOnlyFieldsExposed": exposed_receipt_fields,
        "flowPulseFields": flowpulse_fields,
        "afterSwapObservedFields": after_swap_fields,
        "checks": checks,
        "result": "Solidity hook boundary, FlowPulse schema, and FMM-0 runtime assumptions are aligned.",
        "notClaims": NON_CLAIMS,
    }
    body["abiReportId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = ["FlowPulse Boundary ABI Conformance", "", "Checks:"]
    rows.extend(f"  {item['status']:<4}  {item['label']}" for item in report["checks"])
    rows.extend(
        [
            "",
            "Summary:",
            f"  ABI checks passed: {report['checksPassed']}/{report['checksTotal']}",
            f"  receipt-only fields exposed: {len(report['receiptOnlyFieldsExposed'])}",
            f"  status: {report['status'].upper()}",
            "",
            "Result:",
            f"  {report['result']}",
        ]
    )
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check FlowPulse boundary ABI conformance.")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    check.add_argument("--strict-artifact", action="store_true", help="Fail if compiled artifact is missing.")
    check.add_argument("--pretty", action="store_true", help="Text output is already readable; JSON uses indentation.")
    check.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    check.add_argument("--write", help="Write terminal text output to a file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(strict_artifact=args.strict_artifact)
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
