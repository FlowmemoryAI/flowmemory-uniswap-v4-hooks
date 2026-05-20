#!/usr/bin/env python3
"""Review the FlowMemory system architecture manifest.

This is a deterministic architecture gate. It does not prove production
readiness. It checks whether the launch repo contains the minimum system map a
reviewer needs before FlowMemory is split into runtime packages.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "examples" / "system-architecture" / "architecture-manifest.json"

ARCHITECTURE_SCHEMA = "flowmemory.system_architecture.v0"
REQUIRED_LAYERS = [
    "execution_boundary",
    "pulse_emission",
    "reader_24_7",
    "evidence",
    "memory_model",
    "policy_action",
    "product_api",
    "operations",
]
REQUIRED_INVARIANTS = [
    "hooks_and_adapters_do_not_invent_receipt_metadata",
    "receipt_metadata_is_reader_derived",
    "hook_is_transaction_triggered_not_24_7",
    "reader_is_the_24_7_process",
    "memory_records_are_append_only",
    "uri_content_is_advisory_unless_verified",
    "wallet_and_payment_rails_are_external",
    "compute_reuse_stores_commitments_and_lineage_not_gpu_memory",
    "public_release_claims_are_evidence_gated",
    "pulse_permits_bind_policy_actor_action_and_memory_head",
    "outcome_pulses_require_receipt_bound_flowpulse_links",
    "pulsepass_claims_can_hide_provider_txhash_and_amount",
]
REQUIRED_NON_CLAIMS = [
    "no_custody",
    "no_escrow",
    "no_fund_protection",
    "no_wallet_authorization",
    "no_hook_time_txhash_transactionindex_or_logindex",
    "no_semantic_truth",
    "no_model_correctness",
    "no_gpu_hardware_acceleration",
    "no_live_base_mainnet_without_release_evidence",
    "no_production_verifier_network_without_operator_evidence",
]
REQUIRED_READINESS_PATH = [
    "local_conformance",
    "public_testnet_evidence",
    "public_canary",
    "production_candidate",
]


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ids(items: list[dict[str, Any]]) -> set[str]:
    return {str(item.get("id", "")) for item in items}


def build_report(manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    manifest = manifest or load_manifest()
    layer_ids = _ids(manifest.get("layers", []))
    invariants = set(manifest.get("invariants", []))
    non_claims = set(manifest.get("nonClaims", []))
    readiness_path = manifest.get("readinessPath", [])
    components = [
        component
        for layer in manifest.get("layers", [])
        for component in layer.get("components", [])
    ]

    issues: list[dict[str, str]] = []
    if manifest.get("schema") != ARCHITECTURE_SCHEMA:
        issues.append({"code": "wrong_schema", "detail": str(manifest.get("schema"))})

    for layer in REQUIRED_LAYERS:
        if layer not in layer_ids:
            issues.append({"code": "missing_layer", "detail": layer})

    for invariant in REQUIRED_INVARIANTS:
        if invariant not in invariants:
            issues.append({"code": "missing_invariant", "detail": invariant})

    for non_claim in REQUIRED_NON_CLAIMS:
        if non_claim not in non_claims:
            issues.append({"code": "missing_non_claim", "detail": non_claim})

    if readiness_path != REQUIRED_READINESS_PATH:
        issues.append(
            {
                "code": "wrong_readiness_path",
                "detail": " -> ".join(str(item) for item in readiness_path),
            }
        )

    return {
        "schema": "flowmemory.system_architecture_review.v0",
        "status": "PASS" if not issues else "FAIL",
        "manifestSchema": manifest.get("schema"),
        "layersChecked": len(layer_ids.intersection(REQUIRED_LAYERS)),
        "layersRequired": len(REQUIRED_LAYERS),
        "componentsChecked": len(components),
        "invariantsChecked": len(invariants.intersection(REQUIRED_INVARIANTS)),
        "invariantsRequired": len(REQUIRED_INVARIANTS),
        "nonClaimsChecked": len(non_claims.intersection(REQUIRED_NON_CLAIMS)),
        "nonClaimsRequired": len(REQUIRED_NON_CLAIMS),
        "readinessPath": readiness_path,
        "issues": issues,
        "result": "Architecture packet is complete for launch review."
        if not issues
        else "Architecture packet is missing required review structure.",
    }


def render_report(report: dict[str, Any]) -> str:
    rows = [
        "FlowMemory System Architecture Review",
        "",
        f"status: {report['status']}",
        f"layers checked: {report['layersChecked']}/{report['layersRequired']}",
        f"components checked: {report['componentsChecked']}",
        f"invariants checked: {report['invariantsChecked']}/{report['invariantsRequired']}",
        f"non-claims checked: {report['nonClaimsChecked']}/{report['nonClaimsRequired']}",
        f"readiness path: {' -> '.join(report['readinessPath'])}",
    ]
    if report["issues"]:
        rows.extend(["", "Issues:"])
        for issue in report["issues"]:
            rows.append(f"  {issue['code']}: {issue['detail']}")
    rows.extend(["", "Result:", f"  {report['result']}"])
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review the FlowMemory system architecture manifest.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Path to architecture manifest JSON.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON; text output is already readable.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(load_manifest(Path(args.manifest)))
    if args.json:
        print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(render_report(report))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
