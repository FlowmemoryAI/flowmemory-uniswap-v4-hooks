#!/usr/bin/env python3
"""Mainnet candidate gate for the FlowMemory hook repo.

The gate is intentionally strict. It can report local launch readiness while
blocking any mainnet-ready claim until external evidence is supplied.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import launch_reality_check, public_claim_gate
except ModuleNotFoundError:  # pragma: no cover
    import launch_reality_check  # type: ignore
    import public_claim_gate  # type: ignore


MAINNET_GATES = [
    {
        "gate": "verified_mainnet_poolmanager",
        "why": "Mainnet PoolManager and deployment assumptions must be re-checked against official Uniswap records.",
    },
    {
        "gate": "mainnet_hook_deployment",
        "why": "A production candidate needs an actual verified deployment record.",
    },
    {
        "gate": "source_verification",
        "why": "Hook bytecode and source must be visible on the target explorer.",
    },
    {
        "gate": "observed_after_swap_log",
        "why": "At least one finalized AfterSwapObserved log must exist.",
    },
    {
        "gate": "observed_flowpulse_log",
        "why": "At least one finalized FlowPulse log must exist.",
    },
    {
        "gate": "reader_verifier_evidence",
        "why": "Receipt-derived txHash/logIndex/finality evidence must be attached by reader infrastructure.",
    },
    {
        "gate": "incident_response_owner",
        "why": "Mainnet candidates need an operator and incident escalation owner.",
    },
    {
        "gate": "security_review",
        "why": "A production claim needs independent review of hook, deployment, and reader assumptions.",
    },
]


def build_report(satisfied_gates: set[str] | None = None) -> dict[str, Any]:
    satisfied_gates = satisfied_gates or set()
    claim_report = public_claim_gate.build_report()
    reality_report = launch_reality_check.build_report()
    gates = [
        {
            "gate": gate["gate"],
            "passed": gate["gate"] in satisfied_gates,
            "status": "SATISFIED" if gate["gate"] in satisfied_gates else "BLOCKING",
            "why": gate["why"],
        }
        for gate in MAINNET_GATES
    ]
    local_ready = claim_report["status"] == "pass" and reality_report["status"] == "pass"
    mainnet_ready = local_ready and all(gate["passed"] for gate in gates)
    return {
        "schema": "flowmemory.mainnet_candidate_gate.v0",
        "localLaunchReady": local_ready,
        "mainnetCandidateReady": mainnet_ready,
        "releaseMode": "MAINNET_CANDIDATE" if mainnet_ready else "LOCAL_LAUNCH_READY_ONLY",
        "blockingGateCount": sum(1 for gate in gates if not gate["passed"]),
        "mainnetGates": gates,
        "claimGate": {
            "status": claim_report["status"],
            "unguardedOverclaims": claim_report["summary"]["unguardedOverclaims"],
        },
        "realityCheck": {
            "status": reality_report["status"],
            "reportId": reality_report["reportId"],
        },
        "notClaims": [
            "no_live_mainnet_deployment_claim",
            "no_production_verifier_claim",
            "no_custody",
            "no_fund_protection",
            "no_audited_production_claim",
        ],
    }


def render_report(report: dict[str, Any]) -> str:
    rows = [
        "FlowMemory Mainnet Candidate Gate",
        "",
        f"localLaunchReady:      {report['localLaunchReady']}",
        f"mainnetCandidateReady: {report['mainnetCandidateReady']}",
        f"releaseMode:           {report['releaseMode']}",
        f"blockingGateCount:     {report['blockingGateCount']}",
        "",
        "Mainnet gates:",
    ]
    for gate in report["mainnetGates"]:
        status = "PASS" if gate["passed"] else "BLOCK"
        rows.append(f"  {gate['gate']:<34} {status}")
        if not gate["passed"]:
            rows.append(f"    {gate['why']}")
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check mainnet candidate readiness without claiming deployment.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--satisfied-gate", action="append", default=[])
    parser.add_argument("--require-mainnet-candidate", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(set(args.satisfied_gate))
    if args.json and not args.pretty:
        print(json.dumps(report, sort_keys=True))
    elif args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_report(report))
    if args.require_mainnet_candidate:
        return 0 if report["mainnetCandidateReady"] else 1
    return 0 if report["localLaunchReady"] else 1


if __name__ == "__main__":
    sys.exit(main())
