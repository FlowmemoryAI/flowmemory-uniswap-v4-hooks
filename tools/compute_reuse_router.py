#!/usr/bin/env python3
"""
Compute Reuse Router.

This is the executable R&D bridge from "GPUs compute, FlowMemory remembers" to
a useful scheduler decision: reuse prior committed compute only when the
commitments, evidence tier, lineage, and policy all allow it.
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


REQUEST_SCHEMA = "flowmemory.compute_reuse_request.v0"
LEDGER_SCHEMA = "flowmemory.compute_pulse_ledger.v0"
POLICY_SCHEMA = "flowmemory.compute_reuse_policy.v0"
DECISION_SCHEMA = "flowmemory.compute_reuse_decision.v0"
COMPUTE_PULSE_SCHEMA = "flowmemory.computepulse.v0"
ZERO32 = "0x" + ("0" * 64)
COMMITMENT_FIELDS = ["rootfieldId", "modelCommitment", "inputCommitment", "runtimeCommitment"]
OPTIONAL_LINEAGE_FIELDS = ["sourceCachePulse", "parentPulseId"]
NON_CLAIMS = [
    "not_gpu_acceleration",
    "not_cuda_optimizer",
    "not_kv_cache_storage",
    "not_semantic_truth",
    "not_model_correctness",
    "not_attestation_verifier",
    "not_public_deployment_evidence",
]
BANNED_OUTPUT_PHRASES = [
    "makes gpu faster",
    "accelerates cuda",
    "stores kv cache",
    "semantic truth verified",
    "model correctness guaranteed",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def write_json(payload: Any, output: str | None, pretty: bool) -> None:
    axiom_writ.write_json(payload, output, pretty)


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def normalize(value: Any) -> str:
    return str(value or "").lower()


def truthy(value: Any) -> bool:
    return value not in (None, "", [], {})


def truthy_hex(value: Any) -> bool:
    return axiom_writ.truthy_hex(value)


def as_int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    return int(value)


def load_ledger(path: str | Path) -> dict[str, Any]:
    ledger = read_json(path)
    if ledger.get("schema") != LEDGER_SCHEMA:
        raise ValueError(f"{path} must use schema {LEDGER_SCHEMA}")
    if not isinstance(ledger.get("computePulses"), list):
        raise ValueError(f"{path} must contain computePulses[]")
    return ledger


def load_policy(path: str | Path) -> dict[str, Any]:
    policy = read_json(path)
    if policy.get("schema") != POLICY_SCHEMA:
        raise ValueError(f"{path} must use schema {POLICY_SCHEMA}")
    return policy


def request_id_body(request: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in request.items() if key not in {"requestId", "checks"}}


def ensure_request_id(request: dict[str, Any]) -> str:
    if request.get("requestId"):
        return str(request["requestId"])
    return digest(request_id_body(request))


def pulse_id(pulse: dict[str, Any]) -> str:
    if pulse.get("computePulseId"):
        return str(pulse["computePulseId"])
    body = {key: value for key, value in pulse.items() if key not in {"computePulseId", "checks"}}
    return digest(body)


def lineage_matches(request: dict[str, Any], pulse: dict[str, Any]) -> bool:
    for field in OPTIONAL_LINEAGE_FIELDS:
        if truthy(request.get(field)) and normalize(request.get(field)) != normalize(pulse.get(field)):
            return False
    return True


def allowed_by_list(value: Any, allowed: list[Any] | None) -> bool:
    if not allowed:
        return True
    return normalize(value) in {normalize(item) for item in allowed}


def freshness_check(request: dict[str, Any], pulse: dict[str, Any], policy: dict[str, Any]) -> tuple[bool, bool]:
    requested_at = as_int(request.get("requestedAt"))
    completed_at = as_int(pulse.get("completedAt"))
    max_age = policy.get("maxAgeSeconds")
    not_from_future = completed_at <= requested_at
    if max_age in (None, ""):
        return not_from_future, not_from_future
    fresh_enough = requested_at - completed_at <= int(max_age)
    return not_from_future, not_from_future and fresh_enough


def pulse_checks(request: dict[str, Any], pulse: dict[str, Any], policy: dict[str, Any]) -> dict[str, bool]:
    not_from_future, fresh_enough = freshness_check(request, pulse, policy)
    require_attestation = bool(request.get("requireAttestationRef") or policy.get("requireAttestationRef"))
    allow_cross_rootfield = bool(policy.get("allowCrossRootfield"))
    rootfield_matches = normalize(request.get("rootfieldId")) == normalize(pulse.get("rootfieldId"))

    return {
        "schemaComputePulse": pulse.get("schema") == COMPUTE_PULSE_SCHEMA,
        "statusVerified": pulse.get("status") == "verified",
        "reuseAllowed": pulse.get("reuseAllowed") is True,
        "rootfieldMatches": rootfield_matches or allow_cross_rootfield,
        "modelCommitmentMatches": normalize(request.get("modelCommitment")) == normalize(pulse.get("modelCommitment")),
        "inputCommitmentMatches": normalize(request.get("inputCommitment")) == normalize(pulse.get("inputCommitment")),
        "runtimeCommitmentMatches": normalize(request.get("runtimeCommitment")) == normalize(pulse.get("runtimeCommitment")),
        "outputCommitmentPresent": truthy_hex(pulse.get("outputCommitment")) and normalize(pulse.get("outputCommitment")) != ZERO32,
        "notFromFuture": not_from_future,
        "freshEnough": fresh_enough,
        "hardwareAllowed": allowed_by_list(pulse.get("hardwareClass"), policy.get("allowedHardwareClasses")),
        "executorAllowed": allowed_by_list(pulse.get("executor"), policy.get("allowedExecutors")),
        "attestationSatisfied": (not require_attestation) or truthy(pulse.get("attestationRef")),
        "lineageMatches": lineage_matches(request, pulse),
        "uriAdvisoryOnly": True,
    }


def failed_reasons(checks: dict[str, bool]) -> list[str]:
    return [key for key, value in checks.items() if not value]


def candidate_report(request: dict[str, Any], pulse: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    checks = pulse_checks(request, pulse, policy)
    reasons = failed_reasons(checks)
    return {
        "computePulseId": pulse_id(pulse),
        "status": "eligible" if not reasons else "rejected",
        "reasons": reasons,
        "checks": checks,
        "completedAt": pulse.get("completedAt"),
        "outputCommitment": pulse.get("outputCommitment"),
        "hardwareClass": pulse.get("hardwareClass"),
        "executor": pulse.get("executor"),
    }


def sort_key(candidate: dict[str, Any]) -> tuple[int, str]:
    return (as_int(candidate.get("completedAt")), str(candidate.get("computePulseId")))


def route(request: dict[str, Any], ledger: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    if request.get("schema") != REQUEST_SCHEMA:
        raise ValueError(f"request must use schema {REQUEST_SCHEMA}")

    candidates = [candidate_report(request, pulse, policy) for pulse in ledger.get("computePulses", []) if isinstance(pulse, dict)]
    eligible = sorted((item for item in candidates if item["status"] == "eligible"), key=sort_key, reverse=True)
    selected = eligible[0] if eligible else None
    decision = "REUSE_PRIOR_COMPUTE" if selected else "RUN_GPU_JOB"
    rejected = [item for item in candidates if item["status"] == "rejected"]
    nearest_rejected = None
    if rejected:
        nearest_rejected = sorted(rejected, key=lambda item: (len(item.get("reasons", [])), str(item.get("computePulseId"))))[0]
    body: dict[str, Any] = {
        "schema": DECISION_SCHEMA,
        "status": "reuse" if selected else "run_required",
        "decision": decision,
        "requestId": ensure_request_id(request),
        "rootfieldId": request.get("rootfieldId"),
        "modelCommitment": request.get("modelCommitment"),
        "inputCommitment": request.get("inputCommitment"),
        "runtimeCommitment": request.get("runtimeCommitment"),
        "candidatesChecked": len(candidates),
        "eligibleCandidates": len(eligible),
        "rejectedCandidates": rejected,
        "nearestRejectedCandidate": nearest_rejected,
        "selectedComputePulseId": selected.get("computePulseId") if selected else None,
        "selectedOutputCommitment": selected.get("outputCommitment") if selected else None,
        "gpuJobsAvoided": 1 if selected else 0,
        "reuseBasis": "commitment_policy_match" if selected else "no_safe_prior_compute",
        "workUnitClaim": "local deterministic routing only; not a performance benchmark",
        "notClaims": NON_CLAIMS,
    }
    body["decisionId"] = digest(body)
    return body


def demo_paths() -> tuple[Path, Path, Path]:
    base = repo_root() / "examples" / "compute-reuse-router"
    return base / "requests.example.json", base / "ledger.example.json", base / "policy.example.json"


def build_demo() -> dict[str, Any]:
    requests_path, ledger_path, policy_path = demo_paths()
    requests_doc = read_json(requests_path)
    ledger = load_ledger(ledger_path)
    policy = load_policy(policy_path)
    requests = requests_doc.get("requests", [])
    decisions = [route(request, ledger, policy) for request in requests if isinstance(request, dict)]
    reused = sum(1 for decision in decisions if decision["status"] == "reuse")
    run_required = sum(1 for decision in decisions if decision["status"] == "run_required")
    unsafe_rejected = sum(1 for decision in decisions if decision["status"] == "run_required" and decision["rejectedCandidates"])
    body = {
        "schema": "flowmemory.compute_reuse_router_demo.v0",
        "status": "pass" if reused == 1 and run_required == 4 and unsafe_rejected == 4 else "fail",
        "requestsChecked": len(decisions),
        "priorComputeReused": reused,
        "gpuJobsAvoided": sum(decision["gpuJobsAvoided"] for decision in decisions),
        "unsafeReuseRejected": unsafe_rejected,
        "unsafeReuseRejectedTotal": run_required,
        "decisions": decisions,
        "result": "FlowMemory can route compute reuse from proof-backed memory without claiming hardware speedup.",
        "notClaims": NON_CLAIMS,
    }
    body["demoId"] = digest(body)
    return body


def render_decision(decision: dict[str, Any]) -> str:
    if decision["status"] == "reuse":
        target = decision.get("selectedComputePulseId")
    else:
        nearest = decision.get("nearestRejectedCandidate") or {}
        reasons = nearest.get("reasons", [])
        target = ",".join(sorted(set(reasons))[:3]) or "no_candidate"
    return f"  {decision['requestId']:<28} {decision['decision']:<22} {target}"


def render_demo(demo: dict[str, Any]) -> str:
    rows = ["Compute Reuse Router", "", "Decisions:"]
    rows.extend(render_decision(decision) for decision in demo["decisions"])
    rows.extend(
        [
            "",
            "Summary:",
            f"  requests checked: {demo['requestsChecked']}",
            f"  prior compute reused: {demo['priorComputeReused']}",
            f"  GPU jobs avoided: {demo['gpuJobsAvoided']}",
            f"  unsafe reuse rejected: {demo['unsafeReuseRejected']}/{demo['unsafeReuseRejectedTotal']}",
            "",
            "Result:",
            f"  {demo['result']}",
        ]
    )
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route AI/GPU compute reuse through FlowMemory commitments.")
    sub = parser.add_subparsers(dest="command", required=True)

    route_cmd = sub.add_parser("route", help="Route one compute request against a ComputePulse ledger.")
    route_cmd.add_argument("--request", required=True)
    route_cmd.add_argument("--ledger", required=True)
    route_cmd.add_argument("--policy", required=True)
    route_cmd.add_argument("--out")
    route_cmd.add_argument("--pretty", action="store_true")

    demo_cmd = sub.add_parser("demo", help="Run the deterministic launch demo.")
    demo_cmd.add_argument("--json", action="store_true")
    demo_cmd.add_argument("--pretty", action="store_true")
    demo_cmd.add_argument("--write")

    verify_cmd = sub.add_parser("verify-decision", help="Verify a persisted router decision.")
    verify_cmd.add_argument("--decision", required=True)
    return parser.parse_args()


def verify_decision(decision: dict[str, Any]) -> dict[str, Any]:
    copied = dict(decision)
    claimed = copied.pop("decisionId", None)
    actual = digest(copied)
    checks = {
        "schemaMatches": decision.get("schema") == DECISION_SCHEMA,
        "decisionIdMatches": claimed == actual,
        "decisionKnown": decision.get("decision") in {"REUSE_PRIOR_COMPUTE", "RUN_GPU_JOB"},
        "notClaimsPresent": all(claim in decision.get("notClaims", []) for claim in NON_CLAIMS),
    }
    return {
        "schema": "flowmemory.compute_reuse_decision_verification.v0",
        "status": "valid" if all(checks.values()) else "invalid",
        "checks": checks,
    }


def main() -> int:
    args = parse_args()
    if args.command == "route":
        decision = route(read_json(args.request), load_ledger(args.ledger), load_policy(args.policy))
        write_json(decision, args.out, args.pretty)
        return 0 if decision["status"] in {"reuse", "run_required"} else 2
    if args.command == "verify-decision":
        verification = verify_decision(read_json(args.decision))
        print(json.dumps(verification, indent=2, sort_keys=True))
        return 0 if verification["status"] == "valid" else 2
    demo = build_demo()
    text = render_demo(demo)
    if args.write:
        output_path = Path(args.write)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(demo, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(text)
    return 0 if demo["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
