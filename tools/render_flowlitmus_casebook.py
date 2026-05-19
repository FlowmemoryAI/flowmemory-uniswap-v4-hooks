#!/usr/bin/env python3
"""
Render the FlowLitmus forbidden outcomes casebook.
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


CASEBOOK_SCHEMA = "flowmemory.flowlitmus.casebook.v0"
DEFAULT_CASEBOOK = "examples/flow-litmus/flowlitmus-casebook.json"


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else repo_root() / candidate


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_casebook(path: str | Path = DEFAULT_CASEBOOK) -> dict[str, Any]:
    casebook = read_json(resolve_path(path))
    if casebook.get("schema") != CASEBOOK_SCHEMA:
        raise ValueError(f"unsupported casebook schema: {casebook.get('schema')}")
    if not casebook.get("cases"):
        raise ValueError("casebook must contain cases")
    ids = [case["id"] for case in casebook["cases"]]
    if len(ids) != len(set(ids)):
        raise ValueError("casebook contains duplicate case ids")
    return casebook


def evaluate_casebook(casebook: dict[str, Any]) -> dict[str, Any]:
    cases = []
    for case in casebook["cases"]:
        exists = resolve_path(case["caseFile"]).exists()
        cases.append({**case, "caseFileExists": exists, "status": "PASS" if exists else "FAIL"})
    body = {
        "schema": "flowmemory.flowlitmus.casebook_report.v0",
        "title": casebook["title"],
        "thesis": casebook["thesis"],
        "suite": casebook["suite"],
        "cases": cases,
        "status": "pass" if all(case["status"] == "PASS" for case in cases) else "fail",
        "nonClaims": casebook.get("nonClaims", []),
    }
    body["casebookId"] = axiom_writ.digest(body)
    return body


def render_markdown(report: dict[str, Any]) -> str:
    rows = [
        "# FlowLitmus Forbidden Outcomes",
        "",
        report["thesis"],
        "",
        "FlowLitmus is not a dashboard, not retrieval, and not semantic truth. It is a casebook for FMM-0: each case names a machine history that should be impossible around receipt-bound FlowPulse boundaries.",
        "",
        "Run the suite:",
        "",
        "```bash",
        "python tools/flow_litmus.py run --suite examples/flow-litmus/litmus.manifest.json",
        "```",
        "",
        "Expected:",
        "",
        "```text",
        "8/8 passed",
        "```",
        "",
        "## Casebook",
        "",
    ]
    for case in report["cases"]:
        rows.extend(
            [
                f"### {case['id']}: {case['title']}",
                "",
                f"Category: `{case['category']}`",
                "",
                f"Impossible history: {case['impossibleHistory']}",
                "",
                f"Why FlowPulse matters: {case['whyFlowPulseMatters']}",
                "",
                f"Detected by: `{case['detectedBy']}`",
                "",
                f"Expected result: `{case['expected']}`",
                "",
                f"Case file: `{case['caseFile']}`",
                "",
            ]
        )
    rows.extend(
        [
            "## Non-Claims",
            "",
        ]
    )
    rows.extend(f"- `{claim}`" for claim in report["nonClaims"])
    rows.extend(["", f"Casebook ID: `{report['casebookId']}`", ""])
    return "\n".join(rows)


def render_text(report: dict[str, Any]) -> str:
    rows = [
        "FlowLitmus Forbidden Outcomes Casebook",
        "",
        report["thesis"],
        "",
        "Cases:",
    ]
    for case in report["cases"]:
        rows.append(f"  {case['id']:<11} {case['title']:<38} {case['status']:<5} {case['expected']}")
    rows.extend(["", f"Result: {len(report['cases'])}/{len(report['cases'])} case descriptions ready.", "", f"Casebook ID: {report['casebookId']}"])
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the FlowLitmus forbidden outcomes casebook.")
    parser.add_argument("--casebook", default=DEFAULT_CASEBOOK, help="Path to flowlitmus-casebook.json.")
    parser.add_argument("--out", help="Write markdown output to a file.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--check", action="store_true", help="Exit nonzero if case files are missing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = evaluate_casebook(load_casebook(args.casebook))
    if args.json:
        output = json.dumps(report, indent=2 if args.pretty else None, sort_keys=True)
        print(output)
    elif args.out:
        output_path = resolve_path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_markdown(report), encoding="utf-8")
    else:
        print(render_text(report))
    return 0 if report["status"] == "pass" or not args.check else 2


if __name__ == "__main__":
    sys.exit(main())
