#!/usr/bin/env python3
"""
FMM-0 Witness Pack.

Builds a deterministic local evidence packet from the FMM-0 conformance
harnesses. This hardens launch evidence quality without claiming production
verification.
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
        flow_litmus,
        fmm0_boundary_bisim,
        fmm0_closure_lab,
        fmm0_counterexample_forge,
        fmm0_forbidden_core,
        fmm0_phase_table,
        memory_consistency_card,
        verify_release_evidence,
    )
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore
    import flow_litmus  # type: ignore
    import fmm0_boundary_bisim  # type: ignore
    import fmm0_closure_lab  # type: ignore
    import fmm0_counterexample_forge  # type: ignore
    import fmm0_forbidden_core  # type: ignore
    import fmm0_phase_table  # type: ignore
    import memory_consistency_card  # type: ignore
    import verify_release_evidence  # type: ignore


PACK_SCHEMA = "flowmemory.fmm0_witness_pack.v0"
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


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def litmus_manifest() -> Path:
    return repo_root() / "examples" / "flow-litmus" / "litmus.manifest.json"


def check(name: str, status: str, metric: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "metric": metric,
        "digest": digest(payload),
    }


def phase_status() -> tuple[str, str, dict[str, Any]]:
    table = fmm0_phase_table.load_table()
    demo = fmm0_phase_table.build_demo(table)
    expected = {
        "pre_receipt_local_output": "PRE-LOCAL-SPEC",
        "reader_derived_flowpulse": "POST-READER-LIVE",
        "fmm0_conforming_history": "FMM0-LIVE",
        "illegal_receipt_smuggle": "INVALID",
    }
    classifications = {item["artifactId"]: item["cellId"] for item in demo["classifications"]}
    status = "PASS" if classifications == expected and demo.get("forbiddenCaught", 0) >= 2 else "FAIL"
    return status, "illegal phase jumps caught", demo


def build_pack() -> dict[str, Any]:
    phase_state, phase_metric, phase_payload = phase_status()
    forge = fmm0_counterexample_forge.build_report()
    closure = fmm0_closure_lab.build_report()
    bisim = fmm0_boundary_bisim.build_report()
    core = fmm0_forbidden_core.build_report()
    litmus = flow_litmus.run_suite(litmus_manifest())
    card = memory_consistency_card.build_card(run_litmus=True)
    release = verify_release_evidence.build_report()

    checks = [
        check("FMM-0 Phase Space", phase_state, phase_metric, phase_payload),
        check("FMM-0 Counterexample Forge", "PASS" if forge["status"] == "pass" else "FAIL", f"{forge['caughtByFmm0']}/{forge['generatedCounterexamples']} caught", forge),
        check("FMM-0 Closure Lab", "PASS" if closure["status"] == "pass" else "FAIL", f"{closure['validClosuresPreserved'] + closure['invalidClosuresRejected']}/{closure['closureLawsChecked']} laws", closure),
        check("FMM-0 Boundary Bisimulation", "PASS" if bisim["status"] == "pass" else "FAIL", f"{bisim['bisimulationsPreserved'] + bisim['driftCasesRejected']}/{bisim['projectionChecks']} projections", bisim),
        check("FMM-0 Forbidden Core Extractor", "PASS" if core["status"] == "pass" else "FAIL", f"{core['minimalCoresFound']}/{core['invalidHistoriesChecked']} cores", core),
        check("FlowLitmus", "PASS" if litmus["status"] == "pass" else "FAIL", f"{litmus['passed']}/{litmus['total']} forbidden outcomes", litmus),
        check("Memory Consistency Card", "PASS" if card["localStatus"] == "pass" else "FAIL", "local surface pass", card),
        check("Public Base Sepolia Evidence", release["verdict"]["publicBaseSepoliaReceiptEvidence"], "release evidence pending-safe", release),
    ]
    local_checks = [item for item in checks if item["name"] != "Public Base Sepolia Evidence"]
    local_passed = sum(1 for item in local_checks if item["status"] == "PASS")
    escaped = int(forge["escaped"]) + int(closure["escaped"]) + int(bisim["escaped"]) + int(core["escapedFaults"])
    body = {
        "schema": PACK_SCHEMA,
        "title": "FMM-0 Witness Pack",
        "status": "pass" if local_passed == len(local_checks) and escaped == 0 else "fail",
        "localConformancePassed": local_passed,
        "localConformanceTotal": len(local_checks),
        "publicBaseSepoliaEvidence": release["verdict"]["publicBaseSepoliaReceiptEvidence"],
        "escapedFaults": escaped,
        "checks": checks,
        "result": "FlowMemory has a reproducible local FMM-0 witness pack.",
        "notClaims": NON_CLAIMS,
    }
    body["witnessPackId"] = digest(body)
    return body


def render_pack(pack: dict[str, Any]) -> str:
    rows = ["FMM-0 Witness Pack", "", "Checks:"]
    for item in pack["checks"]:
        rows.append(f"  {item['name']:<36} {item['status']:<8} {item['metric']}")
    rows.extend(
        [
            "",
            "Summary:",
            f"  local conformance layers passed: {pack['localConformancePassed']}/{pack['localConformanceTotal']}",
            f"  public Base Sepolia evidence: {pack['publicBaseSepoliaEvidence']}",
            f"  escaped faults: {pack['escapedFaults']}",
            "",
            "Result:",
            f"  {pack['result']}",
            "",
            f"Witness Pack ID: {pack['witnessPackId']}",
        ]
    )
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the FMM-0 local witness pack.")
    parser.add_argument("command", choices=["demo"], help="Run the witness pack demo.")
    parser.add_argument("--pretty", action="store_true", help="Text output is already readable; JSON uses indentation.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--write", help="Write terminal text output to a file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pack = build_pack()
    text = render_pack(pack)
    if args.write:
        output_path = Path(args.write)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(pack, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(text)
    return 0 if pack["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
