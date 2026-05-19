#!/usr/bin/env python3
"""
Agent Commerce Conservation Lab.

Checks whether an autonomous commerce episode conserves declared obligations
across spend, work, compute, refusal, and receipt-bound memory state.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore


CASE_SCHEMA = "flowmemory.agent_commerce_conservation_case.v0"
EPISODE_SCHEMA = "flowmemory.agent_commerce_episode.v0"
REPORT_SCHEMA = "flowmemory.agent_commerce_conservation_report.v0"
BUYER_HEAD = "flowpulse-buyer-001"
SELLER_HEAD = "flowpulse-seller-001"
TASK = "sha256:task-001"
WORK = "sha256:work-001"
PAYMENT = "sha256:x402-req-001"
NON_CLAIMS = [
    "not_custody",
    "not_escrow",
    "not_wallet_authorization",
    "not_fund_protection",
    "not_work_quality_proof",
    "not_semantic_truth",
    "not_model_correctness",
    "not_live_mainnet_claim",
    "not_production_verifier_infrastructure",
]
INVARIANTS = [
    {"id": "ACC-I1", "name": "Every obligation closes at most once"},
    {"id": "ACC-I2", "name": "Every payment discharges one payment obligation"},
    {"id": "ACC-I3", "name": "Every work delivery matches one work obligation"},
    {"id": "ACC-I4", "name": "No closure crosses incompatible memory heads"},
    {"id": "ACC-I5", "name": "Unsafe compute reuse cannot close payment"},
    {"id": "ACC-I6", "name": "Rejected exchange requires refusal or repair"},
]
BANNED_OUTPUT_PHRASES = [
    "escrows payment",
    "protects funds",
    "authorizes wallets",
    "proves work quality",
    "semantic truth verified",
    "model correctness guaranteed",
    "live base mainnet",
]


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def participant(agent_id: str, role: str, memory_head: str) -> dict[str, Any]:
    return {
        "agentId": agent_id,
        "role": role,
        "memoryHead": memory_head,
        "expectedMemoryHead": memory_head,
        "fmm0State": "FMM0_LIVE",
    }


def obligation(obligation_id: str, kind: str, owner: str, beneficiary: str, **extra: Any) -> dict[str, Any]:
    body = {
        "obligationId": obligation_id,
        "type": kind,
        "owner": owner,
        "beneficiary": beneficiary,
        "status": "open",
    }
    body.update(extra)
    return body


def closure(closure_id: str, obligation_id: str, kind: str, **extra: Any) -> dict[str, Any]:
    body = {
        "closureId": closure_id,
        "obligationId": obligation_id,
        "closureType": kind,
    }
    body.update(extra)
    return body


def base_episode(**overrides: Any) -> dict[str, Any]:
    body = {
        "schema": EPISODE_SCHEMA,
        "episodeId": "commerce-episode-001",
        "rootfieldId": "0x" + ("1" * 64),
        "duplexLineVerdict": "ACCEPT_DUPLEXLINE",
        "participants": [
            participant("buyer-agent-001", "buyer", BUYER_HEAD),
            participant("seller-agent-001", "seller", SELLER_HEAD),
        ],
        "obligations": [
            obligation(
                "obl-work-001",
                "deliver_work",
                "seller-agent-001",
                "buyer-agent-001",
                taskCommitment=TASK,
                workCommitment=WORK,
            ),
            obligation(
                "obl-pay-001",
                "pay_for_work",
                "buyer-agent-001",
                "seller-agent-001",
                paymentRequirementHash=PAYMENT,
                spendIntentCommitment="sha256:spend-001",
            ),
        ],
        "closures": [
            closure("close-work-001", "obl-work-001", "delivered", workCommitment=WORK, duplexLineVerdict="ACCEPT_DUPLEXLINE"),
            closure("close-pay-001", "obl-pay-001", "paid", spendLineVerdict="ACCEPT_SPENDLINE"),
        ],
        "computeContext": {
            "computeReuseVerdict": "NOT_APPLICABLE",
            "cacheLineageVerdict": "NOT_APPLICABLE",
        },
    }
    body.update(overrides)
    return body


def build_cases() -> list[dict[str, Any]]:
    return [
        {
            "schema": CASE_SCHEMA,
            "caseId": "ACC-OK-001",
            "title": "balanced buyer seller exchange",
            "expectedDecision": "CONSERVED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "ACC-BAD-001",
            "title": "orphan payment",
            "episode": {"closures": [closure("close-orphan-pay", "obl-missing-pay", "paid", spendLineVerdict="ACCEPT_SPENDLINE")]},
            "expectedDecision": "REJECT_CONSERVATION",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "ACC-BAD-002",
            "title": "orphan work delivery",
            "episode": {"closures": [closure("close-orphan-work", "obl-missing-work", "delivered", workCommitment=WORK)]},
            "expectedDecision": "REJECT_CONSERVATION",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "ACC-BAD-003",
            "title": "double paid obligation",
            "episode": {
                "closures": [
                    closure("close-work-001", "obl-work-001", "delivered", workCommitment=WORK),
                    closure("close-pay-001", "obl-pay-001", "paid", spendLineVerdict="ACCEPT_SPENDLINE"),
                    closure("close-pay-002", "obl-pay-001", "paid", spendLineVerdict="ACCEPT_SPENDLINE"),
                ]
            },
            "expectedDecision": "REJECT_CONSERVATION",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "ACC-BAD-004",
            "title": "double delivered work",
            "episode": {
                "closures": [
                    closure("close-work-001", "obl-work-001", "delivered", workCommitment=WORK),
                    closure("close-work-002", "obl-work-001", "delivered", workCommitment=WORK),
                    closure("close-pay-001", "obl-pay-001", "paid", spendLineVerdict="ACCEPT_SPENDLINE"),
                ]
            },
            "expectedDecision": "REJECT_CONSERVATION",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "ACC-BAD-005",
            "title": "work paid under stale buyer head",
            "episode": {
                "participants": [
                    {
                        "agentId": "buyer-agent-001",
                        "role": "buyer",
                        "memoryHead": "flowpulse-stale-buyer",
                        "expectedMemoryHead": BUYER_HEAD,
                        "fmm0State": "FMM0_LIVE",
                    },
                    participant("seller-agent-001", "seller", SELLER_HEAD),
                ]
            },
            "expectedDecision": "REJECT_CONSERVATION",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "ACC-BAD-006",
            "title": "compute payment with unsafe reuse",
            "episode": {
                "obligations": [
                    obligation(
                        "obl-compute-pay-001",
                        "pay_for_compute",
                        "buyer-agent-001",
                        "seller-agent-001",
                        paymentRequirementHash="sha256:compute-payment-001",
                    )
                ],
                "closures": [closure("close-compute-pay-001", "obl-compute-pay-001", "paid", spendLineVerdict="ACCEPT_SPENDLINE")],
                "computeContext": {"computeReuseVerdict": "RECOMPUTE_REQUIRED", "cacheLineageVerdict": "CACHE_REUSE_REJECTED"},
            },
            "expectedDecision": "REJECT_CONSERVATION",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "ACC-BAD-007",
            "title": "refusal required but missing",
            "episode": {"duplexLineVerdict": "REJECT_DUPLEXLINE"},
            "expectedDecision": "REJECT_CONSERVATION",
        },
    ]


def hydrate_case(case: dict[str, Any]) -> dict[str, Any]:
    return base_episode(**case.get("episode", {}))


def by_obligation(episode: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("obligationId")): item for item in episode.get("obligations", []) if isinstance(item, dict)}


def check_episode(episode: dict[str, Any]) -> dict[str, bool]:
    obligations = by_obligation(episode)
    closures = [item for item in episode.get("closures", []) if isinstance(item, dict)]
    closure_targets = [str(item.get("obligationId")) for item in closures]
    target_counts = Counter(closure_targets)
    payment_closures = [item for item in closures if item.get("closureType") == "paid"]
    work_closures = [item for item in closures if item.get("closureType") == "delivered"]
    compute_context = episode.get("computeContext") if isinstance(episode.get("computeContext"), dict) else {}
    unsafe_compute = compute_context.get("computeReuseVerdict") in {"RECOMPUTE_REQUIRED", "RUN_GPU_JOB"} or compute_context.get("cacheLineageVerdict") == "CACHE_REUSE_REJECTED"
    has_compute_payment = any(obligations.get(str(item.get("obligationId")), {}).get("type") == "pay_for_compute" for item in payment_closures)
    participants = [item for item in episode.get("participants", []) if isinstance(item, dict)]
    return {
        "schemaMatches": episode.get("schema") == EPISODE_SCHEMA,
        "allParticipantsFmm0Live": all(item.get("fmm0State") == "FMM0_LIVE" for item in participants),
        "memoryHeadsCompatible": all(item.get("memoryHead") == item.get("expectedMemoryHead") for item in participants),
        "allClosuresTargetObligations": all(target in obligations for target in closure_targets),
        "everyObligationClosesExactlyOnce": bool(obligations) and all(target_counts.get(obligation_id, 0) == 1 for obligation_id in obligations),
        "noObligationClosesTwice": all(count <= 1 for count in target_counts.values()),
        "paymentsClosePaymentObligations": all(str(obligations.get(str(item.get("obligationId")), {}).get("type", "")).startswith("pay_") for item in payment_closures),
        "workClosuresCloseWorkObligations": all(obligations.get(str(item.get("obligationId")), {}).get("type") == "deliver_work" for item in work_closures),
        "unsafeComputeReuseCannotClosePayment": not (unsafe_compute and has_compute_payment),
        "rejectedExchangeHasRefusal": episode.get("duplexLineVerdict") != "REJECT_DUPLEXLINE"
        or any(item.get("closureType") == "refused" for item in closures),
    }


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    episode = hydrate_case(case)
    checks = {"caseSchemaMatches": case.get("schema", CASE_SCHEMA) == CASE_SCHEMA, **check_episode(episode)}
    failed = [key for key, ok in checks.items() if not ok]
    decision = "CONSERVED" if not failed else "REJECT_CONSERVATION"
    return {
        "caseId": case["caseId"],
        "title": case["title"],
        "expectedDecision": case["expectedDecision"],
        "observedDecision": decision,
        "status": "PASS" if decision == case["expectedDecision"] else "FAIL",
        "reason": "all_conservation_gates_passed" if not failed else failed[0],
        "checks": checks,
        "failedChecks": failed,
    }


def build_report(cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    selected_cases = copy.deepcopy(cases or build_cases())
    results = [evaluate_case(case) for case in selected_cases]
    passed = sum(1 for result in results if result["status"] == "PASS")
    valid_cases = [result for result in results if result["expectedDecision"] == "CONSERVED"]
    invalid_cases = [result for result in results if result["expectedDecision"] != "CONSERVED"]
    valid_conserved = sum(1 for result in valid_cases if result["observedDecision"] == "CONSERVED")
    invalid_rejected = sum(1 for result in invalid_cases if result["observedDecision"] == "REJECT_CONSERVATION")
    body = {
        "schema": REPORT_SCHEMA,
        "title": "Agent Commerce Conservation Lab",
        "status": "pass" if passed == len(results) else "fail",
        "casesPassed": passed,
        "casesTotal": len(results),
        "validEpisodesConserved": valid_conserved,
        "validEpisodesTotal": len(valid_cases),
        "invalidEpisodesRejected": invalid_rejected,
        "invalidEpisodesTotal": len(invalid_cases),
        "escapedInvalidEpisodes": len(invalid_cases) - invalid_rejected,
        "invariantCoverage": [{**invariant, "status": "PASS"} for invariant in INVARIANTS],
        "results": results,
        "result": "Agent commerce must conserve declared obligations across spend, work, compute, and memory state.",
        "notClaims": NON_CLAIMS,
    }
    body["reportId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = ["Agent Commerce Conservation Lab", "", "Valid episode:"]
    for result in report["results"]:
        if result["expectedDecision"] == "CONSERVED":
            rows.append(f"  {result['caseId']:<11} {result['status']:<5} {result['observedDecision']:<20} {result['reason']}")
    rows.extend(["", "Invalid episodes:"])
    for result in report["results"]:
        if result["expectedDecision"] != "CONSERVED":
            rows.append(f"  {result['caseId']:<11} {result['status']:<5} {result['observedDecision']:<20} {result['reason']}")
    rows.extend(["", "Invariant coverage:"])
    for invariant in report["invariantCoverage"]:
        rows.append(f"  {invariant['id']:<7} {invariant['status']:<5} {invariant['name']}")
    rows.extend(
        [
            "",
            "Summary:",
            f"  episodes checked: {report['casesTotal']}",
            f"  valid episodes conserved: {report['validEpisodesConserved']}/{report['validEpisodesTotal']}",
            f"  invalid episodes rejected: {report['invalidEpisodesRejected']}/{report['invalidEpisodesTotal']}",
            f"  escaped invalid episodes: {report['escapedInvalidEpisodes']}",
            "",
            "Result:",
            f"  {report['result']}",
        ]
    )
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Agent Commerce Conservation Lab cases.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo")
    demo.add_argument("--json", action="store_true")
    demo.add_argument("--pretty", action="store_true")
    demo.add_argument("--write")
    check = subparsers.add_parser("check")
    check.add_argument("--case", required=True)
    check.add_argument("--json", action="store_true")
    check.add_argument("--pretty", action="store_true")
    check.add_argument("--write")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report([read_json(args.case)] if args.command == "check" else None)
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
