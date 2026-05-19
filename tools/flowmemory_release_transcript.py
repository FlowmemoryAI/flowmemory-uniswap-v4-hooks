#!/usr/bin/env python3
"""
FlowMemory Release Transcript.

Builds one deterministic launch transcript from the local evidence gates. This
is intentionally offline: no live RPC, no production claims, no hidden
deployment assumptions.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import (
        axiom_writ,
        cache_lineage_gate,
        compute_reuse_consistency,
        compute_reuse_router,
        fmm0_witness_pack,
        launch_reality_check,
        verify_release_evidence,
    )
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore
    import cache_lineage_gate  # type: ignore
    import compute_reuse_consistency  # type: ignore
    import compute_reuse_router  # type: ignore
    import fmm0_witness_pack  # type: ignore
    import launch_reality_check  # type: ignore
    import verify_release_evidence  # type: ignore


TRANSCRIPT_SCHEMA = "flowmemory.release_transcript.v0"
NON_CLAIMS = [
    "no_live_base_mainnet_claim",
    "no_audited_custody_claim",
    "no_fund_protection_claim",
    "no_swap_control_claim",
    "no_semantic_truth_claim",
    "no_model_correctness_claim",
    "no_hardware_speedup_claim",
    "no_production_verifier_claim",
]
BANNED_OUTPUT_PHRASES = [
    "base mainnet deployed",
    "audited custody",
    "protects funds",
    "semantic truth verified",
    "model correctness guaranteed",
    "production verifier ready",
    "makes gpu faster",
]


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def status_from_bool(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def evidence_item(name: str, status: str, metric: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "metric": metric,
        "digest": digest(payload),
    }


def build_transcript() -> dict[str, Any]:
    witness = fmm0_witness_pack.build_pack()
    reality = launch_reality_check.build_report(run_litmus=True)
    compute = compute_reuse_router.build_demo()
    cache = cache_lineage_gate.build_demo()
    consistency = compute_reuse_consistency.build_report()
    release = verify_release_evidence.build_report()

    local_items = [
        evidence_item(
            "FMM-0 Witness Pack",
            status_from_bool(witness["status"] == "pass"),
            f"{witness['localConformancePassed']}/{witness['localConformanceTotal']} local layers, {witness['escapedFaults']} escaped faults",
            witness,
        ),
        evidence_item(
            "Launch Reality Check",
            status_from_bool(reality["status"] == "pass"),
            "boundary model, hook invariants, artifacts, and FlowLitmus",
            reality,
        ),
        evidence_item(
            "Compute Reuse Router",
            status_from_bool(compute["status"] == "pass"),
            f"{compute['priorComputeReused']} reuse, {compute['unsafeReuseRejected']}/{compute['unsafeReuseRejectedTotal']} unsafe reuse rejected",
            compute,
        ),
        evidence_item(
            "Cache Lineage Gate",
            status_from_bool(cache["status"] == "pass"),
            f"{cache['cacheReuseAccepted']} cache reuse, {cache['unsafeCacheReuseRejected']}/{cache['unsafeCacheReuseRejectedTotal']} unsafe reuse rejected",
            cache,
        ),
        evidence_item(
            "Compute Reuse Consistency",
            status_from_bool(consistency["status"] == "pass"),
            f"{consistency['casesPassed']}/{consistency['casesTotal']} cases, {consistency['unsafeReuseBlocked']}/{consistency['unsafeReuseTotal']} unsafe reuse blocked",
            consistency,
        ),
    ]
    public_status = release["verdict"]["publicBaseSepoliaReceiptEvidence"]
    public_items = [
        evidence_item(
            "Public Base Sepolia Receipt Evidence",
            public_status,
            "pending-safe public release evidence gate",
            release,
        )
    ]
    local_pass = all(item["status"] == "PASS" for item in local_items)
    body = {
        "schema": TRANSCRIPT_SCHEMA,
        "title": "FlowMemory Release Transcript",
        "thesis": "The transaction is the proof envelope. The FlowPulse is the memory artifact.",
        "localStatus": "PASS" if local_pass else "FAIL",
        "publicReceiptEvidence": public_status,
        "launchReadiness": "local_ready_public_evidence_pending" if local_pass and public_status == "PENDING" else "needs_review",
        "localEvidence": local_items,
        "publicEvidence": public_items,
        "result": "FlowMemory's local FMM-0 consistency surface is launch-ready; public receipt evidence remains pending and is not claimed.",
        "notClaims": NON_CLAIMS,
    }
    body["transcriptId"] = digest(body)
    return body


def render_transcript(transcript: dict[str, Any]) -> str:
    rows = [
        "FlowMemory Release Transcript",
        "",
        "Thesis:",
        f"  {transcript['thesis']}",
        "",
        "Local evidence:",
    ]
    for item in transcript["localEvidence"]:
        rows.append(f"  {item['name']:<28} {item['status']:<8} {item['metric']}")
    rows.extend(["", "Public evidence:"])
    for item in transcript["publicEvidence"]:
        rows.append(f"  {item['name']:<28} {item['status']:<8} {item['metric']}")
    rows.extend(
        [
            "",
            "Result:",
            f"  {transcript['result']}",
            "",
            "Do not claim:",
            "  live Base mainnet deployment",
            "  custody audit or fund-safety guarantees",
            "  swap control, semantic truth, model correctness, hardware speedup, or production verifier readiness",
        ]
    )
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the FlowMemory offline release transcript.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON; text output is already readable.")
    parser.add_argument("--write", help="Write terminal text output to a file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    transcript = build_transcript()
    text = render_transcript(transcript)
    if args.write:
        output_path = Path(args.write)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(transcript, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(text)
    return 0 if transcript["localStatus"] == "PASS" and transcript["publicReceiptEvidence"] in {"PENDING", "PASS"} else 2


if __name__ == "__main__":
    sys.exit(main())
