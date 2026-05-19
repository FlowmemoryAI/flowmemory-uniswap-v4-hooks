#!/usr/bin/env python3
"""
FMM-0 Skeptic Walkthrough.

Renders a claim-to-evidence review packet for skeptical engineers. The goal is
to make the launch claim reviewable without adding another primitive.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ, flow_litmus, memory_consistency_card
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore
    import flow_litmus  # type: ignore
    import memory_consistency_card  # type: ignore


LEDGER_SCHEMA = "flowmemory.fmm0.claim_ledger.v0"
REPORT_SCHEMA = "flowmemory.fmm0.skeptic_walkthrough.v0"
DEFAULT_LEDGER = "examples/reviewer-walkthrough/fmm0-claim-ledger.json"
ALLOWED_STATUSES = {"PASS", "PENDING", "NOT_CLAIMED", "REVIEW_ONLY", "FAIL"}
REQUIRED_CLAIM_IDS = {
    "FM-C01",
    "FM-C02",
    "FM-C03",
    "FM-C04",
    "FM-C05",
    "FM-C06",
    "FM-C07",
    "FM-C08",
    "FM-C09",
    "FM-C10",
    "FM-C11",
}
FORBIDDEN_PASS_PHRASES = [
    "audited custody",
    "fund protection",
    "semantic truth guarantee",
    "model correctness guarantee",
    "live Base mainnet",
    "hook knows txHash",
    "hook knows logIndex",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else repo_root() / candidate


def load_ledger(path: str | Path = DEFAULT_LEDGER) -> dict[str, Any]:
    ledger = read_json(resolve_path(path))
    if ledger.get("schema") != LEDGER_SCHEMA:
        raise ValueError(f"unsupported ledger schema: {ledger.get('schema')}")
    claims = ledger.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ValueError("ledger must contain claims")
    validate_claims(claims)
    return ledger


def validate_claims(claims: list[dict[str, Any]]) -> None:
    seen: set[str] = set()
    for claim in claims:
        for field in ["id", "claim", "category", "status", "evidenceFiles", "commands", "expected", "nonClaims"]:
            if field not in claim:
                raise ValueError(f"claim missing {field}: {claim}")
        if claim["id"] in seen:
            raise ValueError(f"duplicate claim id: {claim['id']}")
        seen.add(claim["id"])
        if claim["status"] not in ALLOWED_STATUSES:
            raise ValueError(f"unsupported status for {claim['id']}: {claim['status']}")
    missing = REQUIRED_CLAIM_IDS - seen
    if missing:
        raise ValueError(f"ledger missing required claims: {sorted(missing)}")


def evidence_status(claim: dict[str, Any]) -> list[dict[str, Any]]:
    status = []
    for path in claim["evidenceFiles"]:
        exists = resolve_path(path).exists()
        status.append({"path": path, "exists": exists})
    return status


def build_report(ledger_path: str | Path = DEFAULT_LEDGER, run_subprocess: bool = True) -> dict[str, Any]:
    ledger = load_ledger(ledger_path)
    claims = [{**claim, "evidence": evidence_status(claim)} for claim in ledger["claims"]]
    litmus_status = "skipped"
    litmus_passed = None
    litmus_total = None
    local_status = "PASS"
    public_status = "PENDING"
    if run_subprocess:
        litmus = flow_litmus.run_suite(resolve_path("examples/flow-litmus/litmus.manifest.json"))
        litmus_status = "PASS" if litmus["status"] == "pass" else "FAIL"
        litmus_passed = litmus["passed"]
        litmus_total = litmus["total"]
        card = memory_consistency_card.build_card(run_litmus=False)
        public_status = card["publicChainEvidence"].upper()
        local_status = "PASS" if litmus_status == "PASS" and all(
            claim["status"] != "FAIL" for claim in claims if claim["category"] != "public_release_evidence"
        ) else "FAIL"
    missing_required = [
        claim["id"]
        for claim in claims
        if claim["status"] == "PASS" and any(not item["exists"] for item in claim["evidence"])
    ]
    if missing_required:
        local_status = "FAIL"
    body = {
        "schema": REPORT_SCHEMA,
        "title": "FMM-0 Skeptic Walkthrough",
        "safeLaunchWording": ledger["safeLaunchWording"],
        "boundaryModel": ledger["boundaryModel"],
        "verdict": {
            "localFmm0ConsistencySurface": local_status,
            "flowLitmusForbiddenOutcomes": litmus_status,
            "publicBaseSepoliaReceiptEvidence": public_status,
            "productionVerifierInfrastructure": "NOT_CLAIMED",
        },
        "litmus": {"status": litmus_status, "passed": litmus_passed, "total": litmus_total},
        "claims": claims,
        "missingRequiredEvidence": missing_required,
    }
    body["walkthroughId"] = axiom_writ.digest(body)
    return body


def render_text(report: dict[str, Any]) -> str:
    verdict = report["verdict"]
    rows = [
        "FMM-0 Skeptic Walkthrough",
        "",
        "Verdict:",
        f"  Local FMM-0 consistency surface: {verdict['localFmm0ConsistencySurface']}",
        f"  FlowLitmus forbidden outcomes: {verdict['flowLitmusForbiddenOutcomes']}",
        f"  Public Base Sepolia receipt evidence: {verdict['publicBaseSepoliaReceiptEvidence']}",
        f"  Production verifier infrastructure: {verdict['productionVerifierInfrastructure']}",
        "",
        "Boundary model:",
    ]
    rows.extend(f"  {line}" for line in report["boundaryModel"])
    rows.extend(["", "Claims:"])
    for claim in report["claims"]:
        rows.append(f"  {claim['id']} {claim['claim']:<70} {claim['status']}")
    rows.extend(
        [
            "",
            "Launch-safe wording:",
            f"  {report['safeLaunchWording']}",
            "",
            "Do not claim:",
            "  semantic truth, model correctness, fund protection, custody, GPU acceleration, or production verifier infrastructure.",
            "",
            f"Walkthrough ID: {report['walkthroughId']}",
        ]
    )
    return "\n".join(rows)


def render_markdown(report: dict[str, Any]) -> str:
    rows = [
        "# FMM-0 Skeptic Walkthrough",
        "",
        "This document is a 10-minute review path for FlowMemory's public launch repo.",
        "",
        "The goal is not to ask reviewers to believe the category language. The goal is to show exactly which claims are supported by local code, tests, specs, and examples, and exactly which claims are not being made.",
        "",
        "## Core Boundary Model",
        "",
    ]
    rows.extend(f"- {line};" for line in report["boundaryModel"])
    verdict = report["verdict"]
    rows.extend(
        [
            "",
            "## Verdict",
            "",
            f"- Local FMM-0 consistency surface: **{verdict['localFmm0ConsistencySurface']}**",
            f"- FlowLitmus forbidden outcomes: **{verdict['flowLitmusForbiddenOutcomes']}**",
            f"- Public Base Sepolia receipt evidence: **{verdict['publicBaseSepoliaReceiptEvidence']}**",
            f"- Production verifier infrastructure: **{verdict['productionVerifierInfrastructure']}**",
            "",
            "## Claim Ledger",
            "",
            "| Claim | Status | Evidence | Commands | Expected | Non-claims |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for claim in report["claims"]:
        evidence = "<br>".join(f"`{item['path']}`" for item in claim["evidence"])
        commands = "<br>".join(f"`{command}`" for command in claim["commands"]) or "-"
        non_claims = ", ".join(f"`{item}`" for item in claim["nonClaims"])
        rows.append(f"| `{claim['id']}` {claim['claim']} | {claim['status']} | {evidence} | {commands} | {claim['expected']} | {non_claims} |")
    rows.extend(
        [
            "",
            "## Launch-Safe Wording",
            "",
            f"> {report['safeLaunchWording']}",
            "",
            "## Do Not Claim",
            "",
            "- semantic truth;",
            "- model correctness;",
            "- fund protection;",
            "- custody;",
            "- GPU acceleration;",
            "- production verifier infrastructure;",
            "- live Base mainnet deployment.",
            "",
            f"Walkthrough ID: `{report['walkthroughId']}`",
            "",
        ]
    )
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the FMM-0 skeptic walkthrough.")
    parser.add_argument("--ledger", default=DEFAULT_LEDGER, help="Path to the claim ledger JSON.")
    parser.add_argument("--pretty", action="store_true", help="Kept for CLI symmetry; text output is always readable.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--no-subprocess", action="store_true", help="Skip FlowLitmus/card checks and use ledger-derived status.")
    parser.add_argument("--write", help="Write terminal text output to a file.")
    parser.add_argument("--markdown", help="Write markdown walkthrough output to a file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.ledger, run_subprocess=not args.no_subprocess)
    text = render_text(report)
    if args.write:
        output_path = resolve_path(args.write)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    if args.markdown:
        markdown_path = resolve_path(args.markdown)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_markdown(report), encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    elif not args.markdown:
        print(text)
    return 0 if report["verdict"]["localFmm0ConsistencySurface"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
