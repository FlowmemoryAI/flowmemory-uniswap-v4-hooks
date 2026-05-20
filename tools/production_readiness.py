#!/usr/bin/env python3
"""Production-like Base Sepolia readiness gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import base_sepolia_deploy, public_claim_gate, public_status, release_evidence
except ModuleNotFoundError:  # pragma: no cover
    import base_sepolia_deploy  # type: ignore
    import public_claim_gate  # type: ignore
    import public_status  # type: ignore
    import release_evidence  # type: ignore


SCHEMA = "flowmemory.production_readiness.v0"
REQUIRED_DOCS = [
    "docs/BASE_SEPOLIA_DEPLOYMENT_RUNBOOK.md",
    "docs/PULSEWATCH_OPERATIONS.md",
    "docs/RELEASE_EVIDENCE.md",
    "docs/PUBLIC_STATUS.md",
    "docs/PRODUCTION_READINESS.md",
    "docs/NON_CLAIMS.md",
    "docs/SLOS.md",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def path_exists(path: str) -> bool:
    return (repo_root() / path).exists()


def build_report(
    *,
    deployment_manifest: str = "deployments/base-sepolia/deployment-manifest.dry-run.json",
    release_packet: str = "release-evidence/base-sepolia/RELEASE_PACKET.json",
    public_status_path: str = "public/status/base-sepolia.md",
) -> dict[str, Any]:
    claim_report = public_claim_gate.build_report()
    checks = []
    for doc in REQUIRED_DOCS:
        checks.append({"gate": f"doc:{doc}", "status": "PASS" if path_exists(doc) else "BLOCKED"})

    manifest_path = repo_root() / deployment_manifest
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_issues = base_sepolia_deploy.validate_manifest(manifest)
        checks.append({"gate": "deployment_manifest_sanitized", "status": "PASS" if not manifest_issues else "FAIL", "issues": manifest_issues})
    else:
        checks.append({"gate": "deployment_manifest_sanitized", "status": "BLOCKED", "issues": ["missing_manifest"]})

    packet_path = repo_root() / release_packet
    if packet_path.exists():
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        packet_issues = release_evidence.verify_packet(packet)
        checks.append({"gate": "release_packet_valid", "status": "PASS" if not packet_issues else "FAIL", "issues": packet_issues})
    else:
        checks.append({"gate": "release_packet_valid", "status": "BLOCKED", "issues": ["missing_observed_release_packet"]})

    status = public_status.build_status(release_packet)
    checks.append({"gate": "public_status_testnet_only", "status": "PASS" if status["testnetOnly"] else "FAIL"})
    checks.append({"gate": "claim_gate", "status": "PASS" if claim_report["status"] == "pass" else "FAIL"})

    statuses = {check["status"] for check in checks}
    if "FAIL" in statuses:
        readiness = "fail"
    elif "BLOCKED" in statuses:
        readiness = "testnet_path_ready_evidence_blocked"
    else:
        readiness = "testnet_path_ready"
    return {
        "schema": SCHEMA,
        "readiness": readiness,
        "checks": checks,
        "publicStatusPath": public_status_path,
        "notClaims": [
            "not_base_mainnet",
            "not_custody",
            "not_wallet_authorization",
            "not_fund_protection",
            "not_semantic_truth",
            "not_model_correctness",
            "not_gpu_acceleration",
            "not_production_verifier_network",
        ],
    }


def render_report(report: dict[str, Any]) -> str:
    lines = ["FlowMemory Production Readiness", "", f"readiness: {report['readiness']}", "", "Checks:"]
    for check in report["checks"]:
        lines.append(f"  {check['gate']:<45} {check['status']}")
        for issue in check.get("issues", []):
            lines.append(f"    {issue}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Base Sepolia production-like readiness.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(render_report(report))
    return 0 if report["readiness"] != "fail" else 1


if __name__ == "__main__":
    sys.exit(main())
