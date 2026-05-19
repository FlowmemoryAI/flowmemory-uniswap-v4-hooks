#!/usr/bin/env python3
"""
Render the FMM-0 conformance matrix.

The matrix is a launch artifact, not a new runtime primitive. It maps each
FlowMemory Agent Memory Model rule to concrete repository evidence.
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


MANIFEST_SCHEMA = "flowmemory.fmm0.manifest.v0"
DEFAULT_MANIFEST = "examples/memory-model/fmm0.manifest.json"


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_repo_path(path: str) -> Path:
    return repo_root() / path


def load_manifest(path: str | Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    manifest_path = Path(path)
    if not manifest_path.is_absolute():
        manifest_path = repo_root() / manifest_path
    manifest = read_json(manifest_path)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError(f"unsupported manifest schema: {manifest.get('schema')}")
    if manifest.get("model") != "FMM-0":
        raise ValueError("manifest model must be FMM-0")
    if not manifest.get("rules"):
        raise ValueError("manifest must contain rules")
    return manifest


def evaluate_rule(rule: dict[str, Any]) -> dict[str, Any]:
    evidence = [{"path": path, "exists": resolve_repo_path(path).exists()} for path in rule.get("evidence", [])]
    missing = [item["path"] for item in evidence if not item["exists"]]
    status = "pass" if not missing else rule.get("statusWhenMissing", "fail")
    return {**rule, "status": status, "evidence": evidence, "missing": missing}


def evaluate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    rules = [evaluate_rule(rule) for rule in manifest["rules"]]
    blocking = [rule for rule in rules if rule["status"] == "fail"]
    pending = [rule for rule in rules if rule["status"] == "pending"]
    body = {
        "schema": "flowmemory.fmm0.conformance_matrix.v0",
        "model": manifest["model"],
        "title": manifest["title"],
        "thesis": manifest["thesis"],
        "safeLaunchClaim": manifest["safeLaunchClaim"],
        "anchor": manifest["anchor"],
        "rules": rules,
        "status": "pass" if not blocking else "fail",
        "pending": [rule["id"] for rule in pending],
        "nonClaims": manifest.get("nonClaims", []),
    }
    body["matrixId"] = axiom_writ.digest(body)
    return body


def render_status(status: str) -> str:
    return status.upper()


def render_matrix(matrix: dict[str, Any]) -> str:
    rows = [
        "# FMM-0 Conformance Matrix",
        "",
        f"Model: `{matrix['model']}`",
        "",
        matrix["thesis"],
        "",
        "Safe launch claim:",
        "",
        f"> {matrix['safeLaunchClaim']}",
        "",
        "## Anchor",
        "",
        f"- Boundary: `{matrix['anchor']['boundary']}`",
        f"- Signal: `{matrix['anchor']['signal']}`",
        f"- Proof envelope: `{matrix['anchor']['proofEnvelope']}`",
        f"- Memory artifact: `{matrix['anchor']['memoryArtifact']}`",
        "",
        "## Matrix",
        "",
        "| Rule | Status | Invariant | Evidence | Litmus |",
        "| --- | --- | --- | --- | --- |",
    ]
    for rule in matrix["rules"]:
        evidence = "<br>".join(f"`{item['path']}`" for item in rule["evidence"])
        litmus = ", ".join(f"`{case}`" for case in rule.get("litmusCases", [])) or "-"
        rows.append(f"| `{rule['id']}` {rule['name']} | {render_status(rule['status'])} | {rule['invariant']} | {evidence} | {litmus} |")
    rows.extend(
        [
            "",
            "## Result",
            "",
            f"Local model status: **{render_status(matrix['status'])}**.",
            "",
            "Pending release evidence: " + (", ".join(f"`{item}`" for item in matrix["pending"]) if matrix["pending"] else "none") + ".",
            "",
            "## Non-Claims",
            "",
        ]
    )
    rows.extend(f"- `{claim}`" for claim in matrix["nonClaims"])
    rows.extend(["", f"Matrix ID: `{matrix['matrixId']}`", ""])
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the FMM-0 conformance matrix.")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="Path to the FMM-0 manifest.")
    parser.add_argument("--out", help="Write markdown output to a file.")
    parser.add_argument("--json", action="store_true", help="Emit evaluated matrix JSON.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--check", action="store_true", help="Exit nonzero if required local evidence is missing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    matrix = evaluate_manifest(load_manifest(args.manifest))
    if args.json:
        output = json.dumps(matrix, indent=2 if args.pretty else None, sort_keys=True)
    else:
        output = render_matrix(matrix)
    if args.out:
        output_path = Path(args.out)
        if not output_path.is_absolute():
            output_path = repo_root() / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0 if matrix["status"] == "pass" or not args.check else 2


if __name__ == "__main__":
    sys.exit(main())
