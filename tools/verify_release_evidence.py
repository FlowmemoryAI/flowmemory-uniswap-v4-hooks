#!/usr/bin/env python3
"""
Verify the Base Sepolia release evidence packet.

This is a pending-safe gate. If the public release packet is missing, the tool
prints PENDING instead of fabricating a launch claim.
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


RELEASE_SCHEMA = "flowmemory.release_evidence.v0"
REPORT_SCHEMA = "flowmemory.release_evidence_report.v0"
DEFAULT_RELEASE = "releases/base-sepolia/RELEASE_EVIDENCE.json"
REQUIRED_NOT_CLAIMS = {
    "not_live_base_mainnet",
    "not_production_verifier_infrastructure",
    "not_audited_custody",
    "not_fund_protection",
    "not_semantic_truth",
    "not_model_correctness",
    "not_gpu_acceleration",
    "not_swap_control",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else repo_root() / candidate


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def find_key(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            found = find_key(child, key)
            if found is not None:
                return found
    if isinstance(value, list):
        for child in value:
            found = find_key(child, key)
            if found is not None:
                return found
    return None


def present(value: Any) -> bool:
    if isinstance(value, (dict, list)):
        return bool(value)
    return value not in {None, "", "0x", "0x0"}


def pending_report(release_path: Path) -> dict[str, Any]:
    body = {
        "schema": REPORT_SCHEMA,
        "title": "FlowMemory Base Sepolia Release Evidence",
        "releasePath": str(release_path),
        "status": "pending",
        "network": "Base Sepolia",
        "releaseStatus": "missing_release_packet",
        "boundaryModel": [
            "swap transaction != memory",
            "transaction = proof envelope",
            "FlowPulse = memory artifact",
            "hook does not know txHash/logIndex",
            "reader/verifier attaches receipt metadata later",
        ],
        "checks": [
            {"label": "release packet present", "status": "PENDING"},
            {"label": "txHash present", "status": "PENDING"},
            {"label": "logIndex present", "status": "PENDING"},
            {"label": "FlowPulse artifact present", "status": "PENDING"},
            {"label": "rootfieldId present", "status": "PENDING"},
            {"label": "commitment present", "status": "PENDING"},
        ],
        "verdict": {
            "publicBaseSepoliaReceiptEvidence": "PENDING",
            "productionVerifierInfrastructure": "NOT_CLAIMED",
            "semanticTruth": "NOT_CLAIMED",
            "custodyFundProtection": "NOT_CLAIMED",
        },
    }
    body["reportId"] = axiom_writ.digest(body)
    return body


def load_release(release_path: Path) -> dict[str, Any]:
    release = read_json(release_path)
    if release.get("schema") != RELEASE_SCHEMA:
        raise ValueError(f"unsupported release schema: {release.get('schema')}")
    return release


def evidence_file(base: Path, release: dict[str, Any], key: str) -> Path | None:
    files = release.get("evidenceFiles", {})
    value = files.get(key)
    if not value:
        return None
    return base / value


def build_report(release: str | Path = DEFAULT_RELEASE) -> dict[str, Any]:
    release_path = resolve_path(release)
    if not release_path.exists():
        return pending_report(release_path)
    release_payload = load_release(release_path)
    release_dir = release_path.parent
    not_claims = set(release_payload.get("release", {}).get("notClaims", []))
    missing_not_claims = sorted(REQUIRED_NOT_CLAIMS - not_claims)
    receipt_path = evidence_file(release_dir, release_payload, "receipt")
    pulse_path = evidence_file(release_dir, release_payload, "flowPulseEvidence")
    fmm0_path = evidence_file(release_dir, release_payload, "fmm0Verdict")
    referenced = [path for path in [receipt_path, pulse_path, fmm0_path] if path is not None]
    missing_files = [path.name for path in referenced if not path.exists()]
    receipt = read_json(receipt_path) if receipt_path and receipt_path.exists() else {}
    pulse = read_json(pulse_path) if pulse_path and pulse_path.exists() else {}
    fmm0 = read_json(fmm0_path) if fmm0_path and fmm0_path.exists() else {}
    tx_hash = find_key(receipt, "txHash") or find_key(pulse, "txHash")
    log_index = find_key(receipt, "logIndex") or find_key(pulse, "logIndex")
    receipt_status = find_key(receipt, "receiptStatus") or find_key(receipt, "status")
    rootfield_id = find_key(pulse, "rootfieldId")
    commitment = find_key(pulse, "commitment")
    flowpulse = find_key(pulse, "FlowPulse") or find_key(pulse, "flowPulse") or find_key(pulse, "pulseId")
    expected = release_payload.get("expected", {})
    hook_knows_txhash = bool(expected.get("hookKnowsTxHashDuringExecution"))
    hook_knows_logindex = bool(expected.get("hookKnowsLogIndexDuringExecution"))
    checks = [
        {"label": "release packet present", "status": "PASS"},
        {"label": "network is Base Sepolia", "status": "PASS" if release_payload.get("release", {}).get("network") == "Base Sepolia" else "FAIL"},
        {"label": "release status is public_testnet_evidence", "status": "PASS" if release_payload.get("release", {}).get("status") == "public_testnet_evidence" else "FAIL"},
        {"label": "required non-claims present", "status": "PASS" if not missing_not_claims else "FAIL", "missing": missing_not_claims},
        {"label": "referenced evidence files present", "status": "PASS" if not missing_files else "PENDING", "missing": missing_files},
        {"label": "txHash present", "status": "PASS" if present(tx_hash) else "PENDING"},
        {"label": "logIndex present", "status": "PASS" if present(log_index) else "PENDING"},
        {"label": "receipt status successful", "status": "PASS" if str(receipt_status).lower() in {"1", "0x1", "success", "successful"} else "PENDING"},
        {"label": "FlowPulse artifact present", "status": "PASS" if present(flowpulse) else "PENDING"},
        {"label": "rootfieldId present", "status": "PASS" if present(rootfield_id) else "PENDING"},
        {"label": "commitment present", "status": "PASS" if present(commitment) else "PENDING"},
        {"label": "hook-time txHash claim absent", "status": "PASS" if not hook_knows_txhash else "FAIL"},
        {"label": "hook-time logIndex claim absent", "status": "PASS" if not hook_knows_logindex else "FAIL"},
        {"label": "FMM-0 verdict present", "status": "PASS" if fmm0.get("publicBaseSepoliaReceiptEvidence") == "PASS" else "PENDING"},
    ]
    statuses = {check["status"] for check in checks}
    public_status = "FAIL" if "FAIL" in statuses else "PENDING" if "PENDING" in statuses else "PASS"
    body = {
        "schema": REPORT_SCHEMA,
        "title": "FlowMemory Base Sepolia Release Evidence",
        "releasePath": str(release_path),
        "status": public_status.lower(),
        "network": release_payload.get("release", {}).get("network", "Base Sepolia"),
        "releaseStatus": release_payload.get("release", {}).get("status", "unknown"),
        "boundaryModel": [
            "swap transaction != memory",
            "transaction = proof envelope",
            "FlowPulse = memory artifact",
            "hook does not know txHash/logIndex",
            "reader/verifier attaches receipt metadata later",
        ],
        "checks": checks,
        "verdict": {
            "publicBaseSepoliaReceiptEvidence": public_status,
            "productionVerifierInfrastructure": "NOT_CLAIMED",
            "semanticTruth": "NOT_CLAIMED",
            "custodyFundProtection": "NOT_CLAIMED",
        },
    }
    body["reportId"] = axiom_writ.digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = [
        "FlowMemory Base Sepolia Release Evidence",
        "",
        f"Network: {report['network']}",
        f"Status: {report['releaseStatus']}",
        "",
        "Boundary model:",
    ]
    rows.extend(f"  {line}" for line in report["boundaryModel"])
    rows.extend(["", "Receipt checks:"])
    rows.extend(f"  {check['label']:<35} {check['status']}" for check in report["checks"])
    verdict = report["verdict"]
    rows.extend(
        [
            "",
            "FMM-0 release verdict:",
            f"  Public Base Sepolia receipt evidence: {verdict['publicBaseSepoliaReceiptEvidence']}",
            f"  Production verifier infrastructure: {verdict['productionVerifierInfrastructure']}",
            f"  Semantic truth: {verdict['semanticTruth']}",
            f"  Custody/fund protection: {verdict['custodyFundProtection']}",
            "",
            f"Result: release evidence packet is {report['status']}.",
            "",
            f"Report ID: {report['reportId']}",
        ]
    )
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the FlowMemory Base Sepolia release evidence packet.")
    parser.add_argument("--release", default=DEFAULT_RELEASE, help="Path to RELEASE_EVIDENCE.json.")
    parser.add_argument("--pretty", action="store_true", help="Kept for CLI symmetry; text output is always readable.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--require-pass", action="store_true", help="Exit nonzero unless receipt evidence status is PASS.")
    parser.add_argument("--write", help="Write terminal text output to a file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.release)
    text = render_report(report)
    if args.write:
        output_path = resolve_path(args.write)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(text)
    if args.require_pass and report["verdict"]["publicBaseSepoliaReceiptEvidence"] != "PASS":
        return 2
    return 0 if report["status"] != "fail" else 2


if __name__ == "__main__":
    sys.exit(main())
