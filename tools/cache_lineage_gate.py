#!/usr/bin/env python3
"""
Cache Lineage Gate.

Checks whether a KV/context cache artifact can be reused by an AI request
without trusting raw cache bytes, dashboards, or scheduler labels.
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


REQUEST_SCHEMA = "flowmemory.cache_reuse_request.v0"
LEDGER_SCHEMA = "flowmemory.cache_lineage_ledger.v0"
POLICY_SCHEMA = "flowmemory.cache_lineage_policy.v0"
CACHE_PULSE_SCHEMA = "flowmemory.cachepulse.v0"
VERDICT_SCHEMA = "flowmemory.cache_lineage_verdict.v0"
ZERO32 = "0x" + ("0" * 64)
MATCH_FIELDS = [
    "rootfieldId",
    "modelCommitment",
    "tokenizerCommitment",
    "runtimeCommitment",
    "prefixCommitment",
    "sideInputCommitment",
    "adapterCommitment",
    "cachePolicyCommitment",
]
NON_CLAIMS = [
    "not_kv_cache_storage",
    "not_gpu_acceleration",
    "not_model_correctness",
    "not_semantic_truth",
    "not_attestation_verifier",
    "not_payload_disclosure",
]
BANNED_OUTPUT_PHRASES = [
    "stores kv tensors",
    "makes gpu faster",
    "model correctness guaranteed",
    "semantic truth verified",
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
    if not isinstance(ledger.get("cachePulses"), list):
        raise ValueError(f"{path} must contain cachePulses[]")
    return ledger


def load_policy(path: str | Path) -> dict[str, Any]:
    policy = read_json(path)
    if policy.get("schema") != POLICY_SCHEMA:
        raise ValueError(f"{path} must use schema {POLICY_SCHEMA}")
    return policy


def cache_id(cache: dict[str, Any]) -> str:
    if cache.get("cachePulseId"):
        return str(cache["cachePulseId"])
    body = {key: value for key, value in cache.items() if key not in {"cachePulseId", "checks"}}
    return digest(body)


def freshness(request: dict[str, Any], cache: dict[str, Any], policy: dict[str, Any]) -> tuple[bool, bool]:
    requested_at = as_int(request.get("requestedAt"))
    completed_at = as_int(cache.get("completedAt"))
    max_age = policy.get("maxAgeSeconds")
    not_from_future = completed_at <= requested_at
    if max_age in (None, ""):
        return not_from_future, not_from_future
    fresh_enough = requested_at - completed_at <= int(max_age)
    return not_from_future, not_from_future and fresh_enough


def allowed(value: Any, allowed_values: list[Any] | None) -> bool:
    if not allowed_values:
        return True
    return normalize(value) in {normalize(item) for item in allowed_values}


def cache_checks(request: dict[str, Any], cache: dict[str, Any], policy: dict[str, Any]) -> dict[str, bool]:
    not_from_future, fresh_enough = freshness(request, cache, policy)
    require_attestation = bool(request.get("requireAttestationRef") or policy.get("requireAttestationRef"))
    checks = {
        "schemaCachePulse": cache.get("schema") == CACHE_PULSE_SCHEMA,
        "statusVerified": cache.get("status") == "verified",
        "reuseAllowed": cache.get("reuseAllowed") is True,
        "kvBlockCommitmentPresent": truthy_hex(cache.get("kvBlockCommitment")) and normalize(cache.get("kvBlockCommitment")) != ZERO32,
        "notFromFuture": not_from_future,
        "freshEnough": fresh_enough,
        "executorAllowed": allowed(cache.get("executor"), policy.get("allowedExecutors")),
        "attestationSatisfied": (not require_attestation) or truthy(cache.get("attestationRef")),
        "uriAdvisoryOnly": True,
    }
    for field in MATCH_FIELDS:
        checks[f"{field}Matches"] = normalize(request.get(field)) == normalize(cache.get(field))
    return checks


def failed(checks: dict[str, bool]) -> list[str]:
    return [key for key, value in checks.items() if not value]


def candidate(request: dict[str, Any], cache: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    checks = cache_checks(request, cache, policy)
    reasons = failed(checks)
    return {
        "cachePulseId": cache_id(cache),
        "status": "eligible" if not reasons else "rejected",
        "reasons": reasons,
        "checks": checks,
        "completedAt": cache.get("completedAt"),
        "kvBlockCommitment": cache.get("kvBlockCommitment"),
    }


def sort_key(item: dict[str, Any]) -> tuple[int, str]:
    return (as_int(item.get("completedAt")), str(item.get("cachePulseId")))


def nearest_rejected_key(item: dict[str, Any]) -> tuple[int, int, str]:
    checks = item.get("checks", {})
    prefix_penalty = 0 if checks.get("prefixCommitmentMatches") else 1
    return (len(item.get("reasons", [])), prefix_penalty, str(item.get("cachePulseId")))


def decide(request: dict[str, Any], ledger: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    if request.get("schema") != REQUEST_SCHEMA:
        raise ValueError(f"request must use schema {REQUEST_SCHEMA}")
    candidates = [candidate(request, cache, policy) for cache in ledger.get("cachePulses", []) if isinstance(cache, dict)]
    eligible = sorted((item for item in candidates if item["status"] == "eligible"), key=sort_key, reverse=True)
    selected = eligible[0] if eligible else None
    rejected = [item for item in candidates if item["status"] == "rejected"]
    nearest = sorted(rejected, key=nearest_rejected_key)[0] if rejected else None
    body = {
        "schema": VERDICT_SCHEMA,
        "status": "reuse_cache" if selected else "run_prefill",
        "decision": "REUSE_CACHE" if selected else "RUN_PREFILL",
        "requestId": request.get("requestId") or digest(request),
        "candidatesChecked": len(candidates),
        "eligibleCandidates": len(eligible),
        "selectedCachePulseId": selected.get("cachePulseId") if selected else None,
        "selectedKvBlockCommitment": selected.get("kvBlockCommitment") if selected else None,
        "nearestRejectedCandidate": nearest,
        "rejectedCandidates": rejected,
        "cacheReusesAccepted": 1 if selected else 0,
        "unsafeReuseBasis": "all_lineage_commitments_match" if selected else "no_safe_cache_lineage",
        "notClaims": NON_CLAIMS,
    }
    body["verdictId"] = digest(body)
    return body


def demo_paths() -> tuple[Path, Path, Path]:
    base = repo_root() / "examples" / "cache-lineage-gate"
    return base / "requests.example.json", base / "ledger.example.json", base / "policy.example.json"


def build_demo() -> dict[str, Any]:
    requests_path, ledger_path, policy_path = demo_paths()
    requests = read_json(requests_path).get("requests", [])
    ledger = load_ledger(ledger_path)
    policy = load_policy(policy_path)
    verdicts = [decide(request, ledger, policy) for request in requests if isinstance(request, dict)]
    accepted = sum(1 for verdict in verdicts if verdict["status"] == "reuse_cache")
    run_prefill = sum(1 for verdict in verdicts if verdict["status"] == "run_prefill")
    rejected = sum(1 for verdict in verdicts if verdict["status"] == "run_prefill" and verdict["nearestRejectedCandidate"])
    body = {
        "schema": "flowmemory.cache_lineage_gate_demo.v0",
        "status": "pass" if accepted == 1 and run_prefill == 4 and rejected == 4 else "fail",
        "requestsChecked": len(verdicts),
        "cacheReuseAccepted": accepted,
        "prefillRequired": run_prefill,
        "unsafeCacheReuseRejected": rejected,
        "unsafeCacheReuseRejectedTotal": run_prefill,
        "verdicts": verdicts,
        "result": "FlowMemory can make KV/context reuse proof-carried without exposing cache payloads.",
        "notClaims": NON_CLAIMS,
    }
    body["demoId"] = digest(body)
    return body


def render_verdict(verdict: dict[str, Any]) -> str:
    if verdict["status"] == "reuse_cache":
        target = verdict.get("selectedCachePulseId")
    else:
        nearest = verdict.get("nearestRejectedCandidate") or {}
        target = ",".join(sorted(set(nearest.get("reasons", [])))[:3]) or "no_candidate"
    return f"  {verdict['requestId']:<28} {verdict['decision']:<14} {target}"


def render_demo(demo: dict[str, Any]) -> str:
    rows = ["Cache Lineage Gate", "", "Verdicts:"]
    rows.extend(render_verdict(verdict) for verdict in demo["verdicts"])
    rows.extend(
        [
            "",
            "Summary:",
            f"  requests checked: {demo['requestsChecked']}",
            f"  cache reuse accepted: {demo['cacheReuseAccepted']}",
            f"  prefill required: {demo['prefillRequired']}",
            f"  unsafe cache reuse rejected: {demo['unsafeCacheReuseRejected']}/{demo['unsafeCacheReuseRejectedTotal']}",
            "",
            "Result:",
            f"  {demo['result']}",
        ]
    )
    return "\n".join(rows)


def verify_verdict(verdict: dict[str, Any]) -> dict[str, Any]:
    copied = dict(verdict)
    claimed = copied.pop("verdictId", None)
    actual = digest(copied)
    checks = {
        "schemaMatches": verdict.get("schema") == VERDICT_SCHEMA,
        "verdictIdMatches": claimed == actual,
        "decisionKnown": verdict.get("decision") in {"REUSE_CACHE", "RUN_PREFILL"},
        "notClaimsPresent": all(claim in verdict.get("notClaims", []) for claim in NON_CLAIMS),
    }
    return {
        "schema": "flowmemory.cache_lineage_verdict_verification.v0",
        "status": "valid" if all(checks.values()) else "invalid",
        "checks": checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gate KV/context cache reuse through FlowMemory lineage commitments.")
    sub = parser.add_subparsers(dest="command", required=True)
    gate = sub.add_parser("gate", help="Gate one cache reuse request.")
    gate.add_argument("--request", required=True)
    gate.add_argument("--ledger", required=True)
    gate.add_argument("--policy", required=True)
    gate.add_argument("--out")
    gate.add_argument("--pretty", action="store_true")

    demo = sub.add_parser("demo", help="Run the deterministic cache-lineage demo.")
    demo.add_argument("--json", action="store_true")
    demo.add_argument("--pretty", action="store_true")
    demo.add_argument("--write")

    verify = sub.add_parser("verify-verdict", help="Verify a persisted cache-lineage verdict.")
    verify.add_argument("--verdict", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "gate":
        verdict = decide(read_json(args.request), load_ledger(args.ledger), load_policy(args.policy))
        write_json(verdict, args.out, args.pretty)
        return 0 if verdict["status"] in {"reuse_cache", "run_prefill"} else 2
    if args.command == "verify-verdict":
        verification = verify_verdict(read_json(args.verdict))
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
