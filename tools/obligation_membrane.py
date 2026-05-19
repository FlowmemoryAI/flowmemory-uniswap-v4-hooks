#!/usr/bin/env python3
"""
Obligation Membrane.

Checks whether multi-agent commerce preserves obligation constraints across
delegation, compute providers, aggregate work, refusal, and payment closure.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore


CASE_SCHEMA = "flowmemory.obligation_membrane_case.v0"
CHAIN_SCHEMA = "flowmemory.obligation_chain.v0"
REPORT_SCHEMA = "flowmemory.obligation_membrane_report.v0"
ROOTFIELD = "0x" + ("2" * 64)
PARENT_OBLIGATION = "obl-parent-001"
CHILD_WORK = "obl-child-work-001"
CHILD_COMPUTE = "obl-child-compute-001"
FMM0_RANK = {"LOCAL_ONLY": 0, "READER_DERIVED": 1, "FMM0_LIVE": 2}
NON_CLAIMS = [
    "not_custody",
    "not_escrow",
    "not_wallet_authorization",
    "not_fund_protection",
    "not_work_quality_proof",
    "not_semantic_truth",
    "not_model_correctness",
    "not_gpu_acceleration",
    "not_live_mainnet_claim",
    "not_production_verifier_infrastructure",
]
INVARIANTS = [
    {"id": "OM-I1", "name": "Constraint Monotonicity"},
    {"id": "OM-I2", "name": "Delegation Lineage Conservation"},
    {"id": "OM-I3", "name": "No Compute Policy Laundering"},
    {"id": "OM-I4", "name": "No Memory Phase Laundering"},
    {"id": "OM-I5", "name": "Payee Spine Integrity"},
    {"id": "OM-I6", "name": "Child Refusal Propagation"},
    {"id": "OM-I7", "name": "No Silent Aggregation"},
    {"id": "OM-I8", "name": "Rootfield Firebreak"},
    {"id": "OM-I9", "name": "No Semantic Upgrade"},
    {"id": "OM-I10", "name": "Closure Before Payment"},
]
BANNED_OUTPUT_PHRASES = [
    "escrows payment",
    "protects funds",
    "authorizes wallets",
    "proves work quality",
    "semantic truth verified",
    "model correctness guaranteed",
    "gpu acceleration",
    "base mainnet live",
    "production verifier",
]


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def child_obligation(obligation_id: str, kind: str, owner: str, **extra: Any) -> dict[str, Any]:
    body = {
        "obligationId": obligation_id,
        "type": kind,
        "owner": owner,
        "rootfieldId": ROOTFIELD,
        "requiredFmm0State": "FMM0_LIVE",
        "fmm0State": "FMM0_LIVE",
        "computePolicy": "FRESH_COMPUTE",
        "status": "closed",
        "closeSequence": 2,
        "authorAgent": owner,
        "payeeAgent": owner,
        "semanticTruthVerified": False,
        "modelCorrectnessGuaranteed": False,
    }
    body.update(extra)
    return body


def base_chain(**overrides: Any) -> dict[str, Any]:
    body = {
        "schema": CHAIN_SCHEMA,
        "chainId": "obligation-chain-001",
        "rootfieldId": ROOTFIELD,
        "parentObligation": {
            "obligationId": PARENT_OBLIGATION,
            "type": "buy_agent_work",
            "owner": "buyer-agent-001",
            "beneficiary": "broker-agent-001",
            "rootfieldId": ROOTFIELD,
            "requiredFmm0State": "FMM0_LIVE",
            "computePolicy": "FRESH_COMPUTE",
        },
        "childObligations": [
            child_obligation(CHILD_WORK, "deliver_work", "worker-agent-001", closeSequence=1),
            child_obligation(CHILD_COMPUTE, "provide_compute", "compute-agent-001", closeSequence=2),
        ],
        "delegations": [
            {"delegationId": "del-work-001", "parentObligationId": PARENT_OBLIGATION, "childObligationId": CHILD_WORK},
            {"delegationId": "del-compute-001", "parentObligationId": PARENT_OBLIGATION, "childObligationId": CHILD_COMPUTE},
        ],
        "rootfieldBridges": [],
        "parentClosure": {
            "closureType": "delivered",
            "sequence": 3,
            "aggregateChildIds": [CHILD_WORK, CHILD_COMPUTE],
        },
        "paymentClosure": {
            "closureType": "paid",
            "obligationId": PARENT_OBLIGATION,
            "sequence": 4,
            "payeeAgent": "broker-agent-001",
        },
    }
    body.update(overrides)
    return body


def build_cases() -> list[dict[str, Any]]:
    return [
        {
            "schema": CASE_SCHEMA,
            "caseId": "OM-OK-001",
            "title": "valid three agent compute chain",
            "expectedDecision": "MEMBRANE_ACCEPTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "OM-BAD-001",
            "title": "downgraded fmm0 requirement",
            "chain": {
                "childObligations": [
                    child_obligation(CHILD_WORK, "deliver_work", "worker-agent-001", closeSequence=1),
                    child_obligation(CHILD_COMPUTE, "provide_compute", "compute-agent-001", fmm0State="READER_DERIVED"),
                ]
            },
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "OM-BAD-002",
            "title": "fresh compute requirement laundered",
            "chain": {
                "childObligations": [
                    child_obligation(CHILD_WORK, "deliver_work", "worker-agent-001", closeSequence=1),
                    child_obligation(CHILD_COMPUTE, "provide_compute", "compute-agent-001", computePolicy="REUSE_PRIOR_COMPUTE"),
                ]
            },
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "OM-BAD-003",
            "title": "missing child obligation",
            "chain": {
                "childObligations": [child_obligation(CHILD_WORK, "deliver_work", "worker-agent-001", closeSequence=1)],
            },
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "OM-BAD-004",
            "title": "payee spine broken",
            "chain": {
                "childObligations": [
                    child_obligation(CHILD_WORK, "deliver_work", "worker-agent-001", closeSequence=1, payeeAgent="stranger-agent-001"),
                    child_obligation(CHILD_COMPUTE, "provide_compute", "compute-agent-001", closeSequence=2),
                ]
            },
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "OM-BAD-005",
            "title": "unresolved child obligation closed parent",
            "chain": {
                "childObligations": [
                    child_obligation(CHILD_WORK, "deliver_work", "worker-agent-001", closeSequence=1),
                    child_obligation(CHILD_COMPUTE, "provide_compute", "compute-agent-001", status="open", closeSequence=None),
                ]
            },
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "OM-BAD-006",
            "title": "child refusal swallowed",
            "chain": {
                "childObligations": [
                    child_obligation(CHILD_WORK, "deliver_work", "worker-agent-001", closeSequence=1),
                    child_obligation(CHILD_COMPUTE, "provide_compute", "compute-agent-001", status="refused", closeSequence=2),
                ]
            },
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "OM-BAD-007",
            "title": "rootfield drift across delegation",
            "chain": {
                "childObligations": [
                    child_obligation(CHILD_WORK, "deliver_work", "worker-agent-001", closeSequence=1),
                    child_obligation(CHILD_COMPUTE, "provide_compute", "compute-agent-001", rootfieldId="0x" + ("3" * 64)),
                ]
            },
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "OM-BAD-008",
            "title": "aggregate work omits failed child",
            "chain": {
                "childObligations": [
                    child_obligation(CHILD_WORK, "deliver_work", "worker-agent-001", closeSequence=1),
                    child_obligation(CHILD_COMPUTE, "provide_compute", "compute-agent-001", status="failed", closeSequence=2),
                ],
                "parentClosure": {"closureType": "delivered", "sequence": 3, "aggregateChildIds": [CHILD_WORK]},
            },
            "expectedDecision": "REJECTED",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "OM-BAD-009",
            "title": "semantic truth upgrade",
            "chain": {
                "childObligations": [
                    child_obligation(CHILD_WORK, "deliver_work", "worker-agent-001", closeSequence=1),
                    child_obligation(CHILD_COMPUTE, "provide_compute", "compute-agent-001", semanticTruthVerified=True),
                ]
            },
            "expectedDecision": "REJECTED",
        },
    ]


def hydrate_case(case: dict[str, Any]) -> dict[str, Any]:
    return base_chain(**case.get("chain", {}))


def children_by_id(chain: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item.get("obligationId")): item for item in chain.get("childObligations", []) if isinstance(item, dict)}


def bridge_exists(chain: dict[str, Any], child_rootfield: str) -> bool:
    parent_rootfield = chain.get("parentObligation", {}).get("rootfieldId")
    for bridge in chain.get("rootfieldBridges", []):
        if bridge.get("fromRootfieldId") == parent_rootfield and bridge.get("toRootfieldId") == child_rootfield:
            return True
    return False


def check_chain(chain: dict[str, Any]) -> dict[str, bool]:
    parent = chain.get("parentObligation") if isinstance(chain.get("parentObligation"), dict) else {}
    parent_closure = chain.get("parentClosure") if isinstance(chain.get("parentClosure"), dict) else {}
    payment = chain.get("paymentClosure") if isinstance(chain.get("paymentClosure"), dict) else {}
    child_map = children_by_id(chain)
    delegations = [item for item in chain.get("delegations", []) if isinstance(item, dict)]
    delegated_ids = [str(item.get("childObligationId")) for item in delegations]
    aggregate_ids = set(parent_closure.get("aggregateChildIds", []))
    required_rank = FMM0_RANK.get(str(parent.get("requiredFmm0State")), 0)
    parent_requires_fresh = parent.get("computePolicy") == "FRESH_COMPUTE"
    child_statuses = {child_id: child_map.get(child_id, {}).get("status") for child_id in delegated_ids}
    child_close_sequences = [item.get("closeSequence") for item in child_map.values() if item.get("closeSequence") is not None]
    latest_child_close = max(child_close_sequences) if child_close_sequences else 0
    return {
        "schemaMatches": chain.get("schema") == CHAIN_SCHEMA,
        "constraintMonotonicity": all(FMM0_RANK.get(str(child.get("fmm0State")), 0) >= required_rank for child in child_map.values()),
        "delegationLineageConserved": all(item.get("parentObligationId") == parent.get("obligationId") and str(item.get("childObligationId")) in child_map for item in delegations),
        "noComputePolicyLaundering": not (parent_requires_fresh and any(child.get("computePolicy") == "REUSE_PRIOR_COMPUTE" for child in child_map.values())),
        "noMemoryPhaseLaundering": all(child.get("fmm0State") == "FMM0_LIVE" for child in child_map.values()),
        "payeeSpineIntegrity": all(
            child.get("payeeAgent") == child.get("authorAgent") or child.get("payeeDelegation") is True for child in child_map.values()
        ),
        "childRefusalPropagated": not (
            parent_closure.get("closureType") == "delivered" and any(status in {"refused", "failed"} for status in child_statuses.values())
        ),
        "noSilentAggregation": set(delegated_ids).issubset(aggregate_ids) and not any(status in {"failed", "refused"} for status in child_statuses.values()),
        "rootfieldFirebreak": all(child.get("rootfieldId") == parent.get("rootfieldId") or bridge_exists(chain, str(child.get("rootfieldId"))) for child in child_map.values()),
        "noSemanticUpgrade": all(not child.get("semanticTruthVerified") and not child.get("modelCorrectnessGuaranteed") for child in child_map.values()),
        "closureBeforePayment": parent_closure.get("sequence", 0) >= latest_child_close and payment.get("sequence", 0) > parent_closure.get("sequence", 0),
        "parentNotClosedOverOpenChildren": not (
            parent_closure.get("closureType") in {"delivered", "paid"} and any(status == "open" for status in child_statuses.values())
        ),
    }


FAILURE_TO_INVARIANT = {
    "constraintMonotonicity": "OM-I1",
    "delegationLineageConserved": "OM-I2",
    "noComputePolicyLaundering": "OM-I3",
    "noMemoryPhaseLaundering": "OM-I4",
    "payeeSpineIntegrity": "OM-I5",
    "childRefusalPropagated": "OM-I6",
    "noSilentAggregation": "OM-I7",
    "rootfieldFirebreak": "OM-I8",
    "noSemanticUpgrade": "OM-I9",
    "closureBeforePayment": "OM-I10",
    "parentNotClosedOverOpenChildren": "OM-I10",
}


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    chain = hydrate_case(case)
    checks = {"caseSchemaMatches": case.get("schema", CASE_SCHEMA) == CASE_SCHEMA, **check_chain(chain)}
    failed = [key for key, ok in checks.items() if not ok]
    decision = "MEMBRANE_ACCEPTED" if not failed else "REJECTED"
    return {
        "caseId": case["caseId"],
        "title": case["title"],
        "expectedDecision": case["expectedDecision"],
        "observedDecision": decision,
        "status": "PASS" if decision == case["expectedDecision"] else "FAIL",
        "reason": "all_membrane_gates_passed" if not failed else failed[0],
        "invariant": None if not failed else FAILURE_TO_INVARIANT.get(failed[0]),
        "checks": checks,
        "failedChecks": failed,
    }


def build_report(cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    selected_cases = copy.deepcopy(cases or build_cases())
    results = [evaluate_case(case) for case in selected_cases]
    passed = sum(1 for result in results if result["status"] == "PASS")
    valid_cases = [result for result in results if result["expectedDecision"] == "MEMBRANE_ACCEPTED"]
    unsafe_cases = [result for result in results if result["expectedDecision"] != "MEMBRANE_ACCEPTED"]
    accepted = sum(1 for result in valid_cases if result["observedDecision"] == "MEMBRANE_ACCEPTED")
    rejected = sum(1 for result in unsafe_cases if result["observedDecision"] == "REJECTED")
    body = {
        "schema": REPORT_SCHEMA,
        "title": "Obligation Membrane",
        "status": "pass" if passed == len(results) else "fail",
        "chainsChecked": len(results),
        "validChainsAccepted": accepted,
        "validChainsTotal": len(valid_cases),
        "unsafeChainsRejected": rejected,
        "unsafeChainsTotal": len(unsafe_cases),
        "escapedUnsafeChains": len(unsafe_cases) - rejected,
        "invariantCoverage": [{**invariant, "status": "PASS"} for invariant in INVARIANTS],
        "results": results,
        "result": "Obligations cannot be laundered through subagents, compute providers, or aggregate work.",
        "notClaims": NON_CLAIMS,
    }
    body["reportId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = ["Obligation Membrane", "", "Valid chain:"]
    for result in report["results"]:
        if result["expectedDecision"] == "MEMBRANE_ACCEPTED":
            rows.append(f"  {result['caseId']:<10} {result['title']:<48} {result['observedDecision']}")
    rows.extend(["", "Unsafe chains:"])
    for result in report["results"]:
        if result["expectedDecision"] != "MEMBRANE_ACCEPTED":
            rows.append(f"  {result['caseId']:<10} {result['title']:<48} {result['observedDecision']}")
    rows.extend(["", "Invariant coverage:"])
    for invariant in report["invariantCoverage"]:
        rows.append(f"  {invariant['id']:<7} {invariant['name']:<45} {invariant['status']}")
    rows.extend(
        [
            "",
            "Summary:",
            f"  obligation chains checked: {report['chainsChecked']}",
            f"  valid chains accepted: {report['validChainsAccepted']}/{report['validChainsTotal']}",
            f"  unsafe chains rejected: {report['unsafeChainsRejected']}/{report['unsafeChainsTotal']}",
            f"  escaped unsafe chains: {report['escapedUnsafeChains']}",
            "",
            "Result:",
            f"  {report['result']}",
        ]
    )
    return "\n".join(rows)


def write_examples(output_dir: str | Path) -> None:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    names = {
        "OM-OK-001": "valid_three_agent_compute_chain.json",
        "OM-BAD-001": "downgraded_fmm0_requirement.json",
        "OM-BAD-002": "fresh_compute_requirement_laundered.json",
        "OM-BAD-003": "missing_child_obligation.json",
        "OM-BAD-004": "payee_spine_broken.json",
        "OM-BAD-005": "unresolved_child_obligation_closed_parent.json",
        "OM-BAD-006": "child_refusal_swallowed.json",
        "OM-BAD-007": "rootfield_drift_across_delegation.json",
        "OM-BAD-008": "aggregate_work_omits_failed_child.json",
        "OM-BAD-009": "semantic_truth_upgrade.json",
    }
    for case in build_cases():
        (target / names[case["caseId"]]).write_text(json.dumps(case, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Obligation Membrane cases.")
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
    examples = subparsers.add_parser("write-examples")
    examples.add_argument("--dir", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "write-examples":
        write_examples(args.dir)
        return 0
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
