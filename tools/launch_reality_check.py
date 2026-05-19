#!/usr/bin/env python3
"""
FlowMemory Reality Check.

A screenshot-ready launch harness that shows the FlowMemory boundary model,
hook invariant surface, and FlowLitmus runtime consistency suite in one command.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ, flow_litmus
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore
    import flow_litmus  # type: ignore


REPORT_SCHEMA = "flowmemory.launch_reality_check.v0"
REQUIRED_FILES = [
    "README.md",
    "CHANGELOG.md",
    "FLOWMEMORY_PUBLIC_TECHNICAL_REPORT.md",
    "FLOWMEMORY_PUBLIC_TECHNICAL_REPORT.pdf",
    "contracts/FlowMemoryAfterSwapHook.sol",
    "contracts/FlowPulse.sol",
    "specs/FlowPulse-BoundaryABI.v0.md",
    "specs/FMM-0.v0.md",
    "specs/FMM-0-PhaseTable.v0.md",
    "specs/FMM-0-CounterexampleForge.v0.md",
    "specs/FMM-0-ClosureLab.v0.md",
    "specs/FMM-0-BoundaryBisimulation.v0.md",
    "specs/FMM-0-ForbiddenCore.v0.md",
    "specs/FMM-0-WitnessPack.v0.md",
    "specs/CacheLineageGate.v0.md",
    "specs/ComputeReuseConsistency.v0.md",
    "specs/ComputeReuseRouter.v0.md",
    "specs/FlowMemoryReleaseTranscript.v0.md",
    "docs/FLOW_SERIAL.md",
    "docs/FLOWLITMUS_LAUNCH_DEMO.md",
    "docs/FLOWLITMUS_FORBIDDEN_OUTCOMES.md",
    "docs/FLOWMEMORY_RUNTIME_MODEL.md",
    "docs/FLOWMEMORY_MEMORY_MODEL.md",
    "docs/FLOWPULSE_BOUNDARY_ABI.md",
    "docs/FLOWMEMORY_RELEASE_TRANSCRIPT.md",
    "docs/FMM_0_CONFORMANCE_MATRIX.md",
    "docs/FMM_0_PHASE_TABLE.md",
    "docs/FMM_0_COUNTEREXAMPLE_FORGE.md",
    "docs/FMM_0_CLOSURE_LAB.md",
    "docs/FMM_0_BOUNDARY_BISIMULATION.md",
    "docs/FMM_0_FORBIDDEN_CORE_EXTRACTOR.md",
    "docs/FMM_0_WITNESS_PACK.md",
    "docs/CACHE_LINEAGE_GATE.md",
    "docs/COMPUTE_REUSE_CONSISTENCY.md",
    "docs/COMPUTE_REUSE_ROUTER.md",
    "docs/SKEPTIC_REVIEW_WALKTHROUGH.md",
    "docs/LAUNCH_CLAIM_LEDGER.md",
    "docs/REVIEWER_QUICKSTART.md",
    "docs/PUBLIC_TECHNICAL_REPORT.css",
    "examples/flow-litmus/litmus.manifest.json",
    "examples/flow-litmus/flowlitmus-casebook.json",
    "examples/memory-model/fmm0.manifest.json",
    "examples/flowpulse-boundary-abi/expected-output.txt",
    "examples/fmm0-phase-table/phase-table.json",
    "examples/fmm0-counterexample-forge/expected-output.txt",
    "examples/fmm0-closure-lab/expected-output.txt",
    "examples/fmm0-boundary-bisimulation/expected-output.txt",
    "examples/fmm0-forbidden-core/expected-output.txt",
    "examples/fmm0-witness-pack/expected-output.txt",
    "examples/cache-lineage-gate/expected-output.txt",
    "examples/compute-reuse-router/expected-output.txt",
    "examples/compute-reuse-consistency/expected-output.txt",
    "examples/release-transcript/expected-output.txt",
    "examples/reviewer-walkthrough/fmm0-claim-ledger.json",
    "tools/flow_litmus.py",
    "tools/flowpulse_boundary_abi.py",
    "tools/fmm0_phase_table.py",
    "tools/fmm0_counterexample_forge.py",
    "tools/fmm0_closure_lab.py",
    "tools/fmm0_boundary_bisim.py",
    "tools/fmm0_forbidden_core.py",
    "tools/fmm0_witness_pack.py",
    "tools/cache_lineage_gate.py",
    "tools/compute_reuse_consistency.py",
    "tools/compute_reuse_router.py",
    "tools/flowmemory_release_transcript.py",
    "tools/public_claim_gate.py",
    "tools/memory_consistency_card.py",
    "tools/render_fmm0_matrix.py",
    "tools/reviewer_walkthrough.py",
    "tools/verify_release_evidence.py",
    "tools/render_flowlitmus_casebook.py",
    "releases/base-sepolia/RELEASE_EVIDENCE.template.json",
]
BOUNDARY_LINES = [
    "swap != memory",
    "transaction = proof envelope",
    "FlowPulse = memory artifact",
    "hook does not know txHash/logIndex",
    "reader/verifier attaches receipt metadata later",
]
HOOK_INVARIANTS = [
    "afterSwap-only",
    "PoolManager-gated",
    "required hookData",
    "required rootfieldId",
    "required commitment",
    "zero hook delta",
    "no custody / no fees / no routing / no custom accounting",
]
RUNTIME_LINES = [
    "FMM-0: FlowMemory Agent Memory Model",
    "FMM-0 Phase Space: machine-state phase diagram",
    "FMM-0 Counterexample Forge: adversarial impossible-history generation",
    "FMM-0 Closure Lab: executable memory algebra closure checks",
    "FMM-0 Boundary Bisimulation: hook-to-receipt-to-runtime projection checks",
    "FMM-0 Forbidden Core Extractor: minimal failing-core diagnostics",
    "FMM-0 Witness Pack: reproducible local evidence bundle",
    "FlowPulse Boundary ABI: Solidity event and runtime model conformance",
    "FlowSerial: receipt-linearizability for machine cognition",
    "FlowLitmus: executable forbidden outcomes",
    "Cache Lineage Gate: proof-carried KV/context reuse decisions",
    "Compute Reuse Router: proof-backed GPU workflow reuse decisions",
    "Compute Reuse Consistency: cache, compute, and receipt-history gates",
    "Release Transcript: canonical launch state in one offline object",
    "Public Claim Gate: launch copy overclaims stay fenced as non-claims",
]
NON_CLAIMS = [
    "no live mainnet deployment claim",
    "no audited production claim",
    "no custody",
    "no swap control",
    "no semantic truth",
    "no model correctness",
    "no GPU acceleration",
    "no production verifier claim",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def artifact_checks() -> list[dict[str, Any]]:
    root = repo_root()
    return [{"path": path, "exists": (root / path).exists()} for path in REQUIRED_FILES]


def litmus_manifest() -> Path:
    return repo_root() / "examples" / "flow-litmus" / "litmus.manifest.json"


def build_report(run_litmus: bool = True) -> dict[str, Any]:
    checks = artifact_checks()
    litmus_result: dict[str, Any] | None = None
    warnings: list[str] = []
    if run_litmus:
        litmus_result = flow_litmus.run_suite(litmus_manifest())
    else:
        warnings.append("FlowLitmus suite was not executed because --no-subprocess was selected.")
    status = "pass" if all(item["exists"] for item in checks) and (litmus_result is None or litmus_result.get("status") == "pass") else "fail"
    body = {
        "schema": REPORT_SCHEMA,
        "status": status,
        "title": "FlowMemory Reality Check",
        "boundaryModel": BOUNDARY_LINES,
        "hookInvariantSurface": HOOK_INVARIANTS,
        "runtimeModel": RUNTIME_LINES,
        "artifactChecks": checks,
        "litmus": litmus_result,
        "warnings": warnings,
        "launchClaim": "FlowMemory can tell impossible histories from live ones using receipt-bound FlowPulse boundaries.",
        "technicalClaim": "FlowSerial gives receipt-linearizability; FlowLitmus makes the forbidden outcomes executable.",
        "nonClaims": NON_CLAIMS,
    }
    body["reportId"] = digest(body)
    return body


def status_line(ok: bool, label: str) -> str:
    return f"  {'PASS' if ok else 'FAIL'}  {label}"


def litmus_rows(litmus: dict[str, Any] | None) -> list[str]:
    if not litmus:
        return ["FlowLitmus Runtime Consistency Suite", "", "SKIPPED  run without --no-subprocess for litmus results"]
    rows = ["FlowLitmus Runtime Consistency Suite", ""]
    for result in litmus.get("results", []):
        observed = result.get("observed", {})
        fault = ", ".join(str(item) for item in observed.get("faultTypes", []))
        rows.append(f"{result.get('caseId', ''):<11} {str(result.get('title', '')):<38} {result.get('status', '').upper():<5} {fault}")
    rows.extend(["", f"{litmus.get('passed')}/{litmus.get('total')} passed"])
    return rows


def render_report(report: dict[str, Any]) -> str:
    rows = [
        "FlowMemory Reality Check",
        "",
        "Boundary model",
    ]
    rows.extend(status_line(True, line) for line in report["boundaryModel"])
    rows.extend(["", "Hook invariant surface"])
    rows.extend(status_line(True, line) for line in report["hookInvariantSurface"])
    rows.extend(["", "Runtime model"])
    rows.extend(status_line(True, line) for line in report["runtimeModel"])
    rows.extend(["", "Required launch artifacts"])
    rows.extend(status_line(bool(item["exists"]), item["path"]) for item in report["artifactChecks"])
    rows.extend(["", *litmus_rows(report.get("litmus")), "", f"Result: {report['launchClaim']}", "", "Do not claim"])
    rows.extend(f"  {claim}" for claim in report["nonClaims"])
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the FlowMemory launch reality check.")
    parser.add_argument("--pretty", action="store_true", help="Kept for CLI symmetry; text output is always readable.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of terminal text.")
    parser.add_argument("--no-subprocess", action="store_true", help="Skip the FlowLitmus suite and only render static launch checks.")
    parser.add_argument("--write", help="Write terminal text output to a file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(run_litmus=not args.no_subprocess)
    text = render_report(report)
    if args.write:
        Path(args.write).parent.mkdir(parents=True, exist_ok=True)
        Path(args.write).write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(text)
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
