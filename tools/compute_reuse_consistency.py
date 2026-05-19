#!/usr/bin/env python3
"""
Compute Reuse Consistency Harness.

Combines FlowSerial, Cache Lineage Gate, and Compute Reuse Router. The claim is
specific: safe autonomous compute reuse requires cache lineage, compute
fingerprint compatibility, and receipt-bound memory consistency.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ, cache_lineage_gate, compute_reuse_router, flow_serial
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore
    import cache_lineage_gate  # type: ignore
    import compute_reuse_router  # type: ignore
    import flow_serial  # type: ignore


REPORT_SCHEMA = "flowmemory.compute_reuse_consistency_report.v0"
ZERO32 = "0x" + ("0" * 64)
ROOTFIELD = "0x" + ("1" * 64)
MODEL = "0x" + ("2" * 64)
INPUT = "0x" + ("3" * 64)
RUNTIME = "0x" + ("4" * 64)
PREFIX = "0x" + ("5" * 64)
SIDE = "0x" + ("6" * 64)
ADAPTER = "0x" + ("7" * 64)
CACHE_POLICY = "0x" + ("8" * 64)
KV_BLOCK = "0x" + ("9" * 64)
OUTPUT = "0x" + ("a" * 64)
COMMITMENT = "0x" + ("b" * 64)
POOL = "0x" + ("c" * 64)
HOOK = "0x0000000000000000000000000000000000000001"
BOUNDARY_ID = "boundary-flowpulse-compute-reuse"
NON_CLAIMS = [
    "not_gpu_acceleration",
    "not_kv_cache_storage",
    "not_model_correctness",
    "not_semantic_truth",
    "not_production_attestation",
]
BANNED_OUTPUT_PHRASES = [
    "makes gpu faster",
    "verified compute",
    "model correctness guaranteed",
    "semantic truth verified",
]


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def boundary() -> dict[str, Any]:
    return {
        "schema": flow_serial.BOUNDARY_SCHEMA,
        "boundaryId": BOUNDARY_ID,
        "artifactType": "FlowPulse",
        "boundary": "uniswap_v4_afterSwap",
        "declaredOrder": 2,
        "chainId": "84532",
        "hookAddress": HOOK,
        "txHash": "0x" + ("d" * 64),
        "transactionIndex": 2,
        "logIndex": 9,
        "blockNumber": 123456,
        "blockHash": "0x" + ("e" * 64),
        "receiptStatus": "success",
        "rootfieldId": ROOTFIELD,
        "commitment": COMMITMENT,
        "subjectPoolId": POOL,
        "parentPulseId": ZERO32,
    }


def machine_event(retrocausal: bool = False) -> dict[str, Any]:
    if retrocausal:
        return {
            "schema": flow_serial.EVENT_SCHEMA,
            "eventId": "event-retrocausal-reuse",
            "eventType": "compute_reuse_decision",
            "agentId": "demo-agent",
            "rootfieldId": ROOTFIELD,
            "declaredOrder": 1,
            "observedBoundaries": [],
            "claimedReceiptFacts": [{"field": "txHash", "boundaryId": BOUNDARY_ID}],
            "writes": [],
            "mustPrecede": [BOUNDARY_ID],
            "mustFollow": [],
            "outputCommitment": OUTPUT,
        }
    return {
        "schema": flow_serial.EVENT_SCHEMA,
        "eventId": "event-safe-reuse",
        "eventType": "compute_reuse_decision",
        "agentId": "demo-agent",
        "rootfieldId": ROOTFIELD,
        "declaredOrder": 3,
        "observedBoundaries": [BOUNDARY_ID],
        "claimedReceiptFacts": [{"field": "txHash", "boundaryId": BOUNDARY_ID}, {"field": "logIndex", "boundaryId": BOUNDARY_ID}],
        "writes": [{"key": "rootfieldHead", "value": BOUNDARY_ID}],
        "mustPrecede": [],
        "mustFollow": [BOUNDARY_ID],
        "outputCommitment": OUTPUT,
    }


def history(retrocausal: bool = False) -> dict[str, Any]:
    return {
        "schema": flow_serial.HISTORY_SCHEMA,
        "historyId": "compute-reuse-history",
        "agentId": "demo-agent",
        "rootfieldId": ROOTFIELD,
        "declaredConsistency": "flow_serializable",
        "boundaries": [boundary()],
        "events": [machine_event(retrocausal)],
        "notClaims": flow_serial.non_claims(),
    }


def cache_request(**overrides: Any) -> dict[str, Any]:
    body = {
        "schema": cache_lineage_gate.REQUEST_SCHEMA,
        "requestId": "cache-request",
        "rootfieldId": ROOTFIELD,
        "modelCommitment": MODEL,
        "tokenizerCommitment": INPUT,
        "runtimeCommitment": RUNTIME,
        "prefixCommitment": PREFIX,
        "sideInputCommitment": SIDE,
        "adapterCommitment": ADAPTER,
        "cachePolicyCommitment": CACHE_POLICY,
        "requestedAt": 1100,
    }
    body.update(overrides)
    return body


def cache_pulse(**overrides: Any) -> dict[str, Any]:
    body = {
        "schema": cache_lineage_gate.CACHE_PULSE_SCHEMA,
        "cachePulseId": "cache-pulse-consistent",
        "status": "verified",
        "rootfieldId": ROOTFIELD,
        "modelCommitment": MODEL,
        "tokenizerCommitment": INPUT,
        "runtimeCommitment": RUNTIME,
        "prefixCommitment": PREFIX,
        "sideInputCommitment": SIDE,
        "adapterCommitment": ADAPTER,
        "cachePolicyCommitment": CACHE_POLICY,
        "kvBlockCommitment": KV_BLOCK,
        "completedAt": 1000,
        "executor": "executor-a",
        "attestationRef": "nras://cache-attestation",
        "reuseAllowed": True,
    }
    body.update(overrides)
    return body


def compute_request(**overrides: Any) -> dict[str, Any]:
    body = {
        "schema": compute_reuse_router.REQUEST_SCHEMA,
        "requestId": "compute-request",
        "rootfieldId": ROOTFIELD,
        "modelCommitment": MODEL,
        "inputCommitment": INPUT,
        "runtimeCommitment": RUNTIME,
        "sourceCachePulse": "cache-pulse-consistent",
        "requestedAt": 1100,
    }
    body.update(overrides)
    return body


def compute_pulse(**overrides: Any) -> dict[str, Any]:
    body = {
        "schema": compute_reuse_router.COMPUTE_PULSE_SCHEMA,
        "computePulseId": "compute-pulse-consistent",
        "status": "verified",
        "rootfieldId": ROOTFIELD,
        "modelCommitment": MODEL,
        "inputCommitment": INPUT,
        "runtimeCommitment": RUNTIME,
        "sourceCachePulse": "cache-pulse-consistent",
        "outputCommitment": OUTPUT,
        "hardwareClass": "H100-class",
        "executor": "executor-a",
        "attestationRef": "nras://compute-attestation",
        "completedAt": 1000,
        "reuseAllowed": True,
    }
    body.update(overrides)
    return body


def cache_policy(**overrides: Any) -> dict[str, Any]:
    body = {
        "schema": cache_lineage_gate.POLICY_SCHEMA,
        "maxAgeSeconds": 3600,
        "requireAttestationRef": False,
        "allowedExecutors": ["executor-a"],
    }
    body.update(overrides)
    return body


def compute_policy(**overrides: Any) -> dict[str, Any]:
    body = {
        "schema": compute_reuse_router.POLICY_SCHEMA,
        "maxAgeSeconds": 3600,
        "requireAttestationRef": False,
        "allowedHardwareClasses": ["H100-class"],
        "allowedExecutors": ["executor-a"],
        "allowCrossRootfield": False,
    }
    body.update(overrides)
    return body


def build_cases() -> list[dict[str, Any]]:
    return [
        {
            "caseId": "CRC-OK-001",
            "title": "safe cache and compute reuse after FlowPulse boundary",
            "expectedDecision": "ACCEPT_REUSE",
        },
        {
            "caseId": "CRC-KV-001",
            "title": "tokenizer drift blocks cache reuse",
            "cacheRequest": {"tokenizerCommitment": "0x" + ("f" * 64)},
            "expectedDecision": "BLOCK_CACHE_REUSE",
        },
        {
            "caseId": "CRC-GPU-001",
            "title": "runtime drift blocks compute reuse",
            "computeRequest": {"runtimeCommitment": "0x" + ("f" * 64)},
            "expectedDecision": "RUN_GPU_JOB",
        },
        {
            "caseId": "CRC-SER-001",
            "title": "retrocausal receipt claim blocks reuse",
            "retrocausal": True,
            "expectedDecision": "BLOCK_IMPOSSIBLE_HISTORY",
        },
        {
            "caseId": "CRC-ATT-001",
            "title": "missing cache attestation blocks reuse when required",
            "cachePulse": {"attestationRef": ""},
            "cacheRequest": {"requireAttestationRef": True},
            "expectedDecision": "BLOCK_CACHE_REUSE",
        },
    ]


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    serial = flow_serial.certify(history(retrocausal=bool(case.get("retrocausal"))))
    cache_verdict = cache_lineage_gate.decide(
        cache_request(**case.get("cacheRequest", {})),
        {"schema": cache_lineage_gate.LEDGER_SCHEMA, "cachePulses": [cache_pulse(**case.get("cachePulse", {}))]},
        cache_policy(**case.get("cachePolicy", {})),
    )
    compute_verdict = compute_reuse_router.route(
        compute_request(**case.get("computeRequest", {})),
        {"schema": compute_reuse_router.LEDGER_SCHEMA, "computePulses": [compute_pulse(**case.get("computePulse", {}))]},
        compute_policy(**case.get("computePolicy", {})),
    )

    serial_status = serial.get("status", "fault")
    if serial_status != "serializable":
        decision = "BLOCK_IMPOSSIBLE_HISTORY"
        reason = serial.get("faultType")
    elif cache_verdict["status"] != "reuse_cache":
        decision = "BLOCK_CACHE_REUSE"
        reason = ",".join(cache_verdict.get("nearestRejectedCandidate", {}).get("reasons", []))
    elif compute_verdict["status"] != "reuse":
        decision = "RUN_GPU_JOB"
        reason = ",".join(compute_verdict.get("nearestRejectedCandidate", {}).get("reasons", []))
    else:
        decision = "ACCEPT_REUSE"
        reason = "all_consistency_gates_passed"

    return {
        "caseId": case["caseId"],
        "title": case["title"],
        "expectedDecision": case["expectedDecision"],
        "observedDecision": decision,
        "status": "PASS" if decision == case["expectedDecision"] else "FAIL",
        "reason": reason,
        "serialStatus": serial_status,
        "cacheStatus": cache_verdict["status"],
        "computeStatus": compute_verdict["status"],
    }


def build_report() -> dict[str, Any]:
    results = [evaluate_case(case) for case in build_cases()]
    passed = sum(1 for result in results if result["status"] == "PASS")
    unsafe_cases = [result for result in results if result["expectedDecision"] != "ACCEPT_REUSE"]
    unsafe_blocked = sum(1 for result in unsafe_cases if result["status"] == "PASS")
    body = {
        "schema": REPORT_SCHEMA,
        "title": "Compute Reuse Consistency Harness",
        "status": "pass" if passed == len(results) else "fail",
        "casesPassed": passed,
        "casesTotal": len(results),
        "unsafeReuseBlocked": unsafe_blocked,
        "unsafeReuseTotal": len(unsafe_cases),
        "results": results,
        "result": "FlowMemory is not trying to make GPUs faster. It is making compute reuse harder to get wrong.",
        "notClaims": NON_CLAIMS,
    }
    body["reportId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = ["Compute Reuse Consistency Harness", "", "Cases:"]
    for result in report["results"]:
        rows.append(f"  {result['caseId']:<11} {result['status']:<5} {result['observedDecision']:<26} {result['reason']}")
    rows.extend(
        [
            "",
            "Summary:",
            f"  cases passed: {report['casesPassed']}/{report['casesTotal']}",
            f"  unsafe reuse blocked: {report['unsafeReuseBlocked']}/{report['unsafeReuseTotal']}",
            "",
            "Result:",
            f"  {report['result']}",
        ]
    )
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run compute reuse consistency cases.")
    parser.add_argument("command", choices=["demo"], help="Run the consistency harness.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--write")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    text = render_report(report)
    if args.write:
        output_path = Path(args.write)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(text)
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
