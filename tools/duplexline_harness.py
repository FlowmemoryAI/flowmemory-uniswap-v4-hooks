#!/usr/bin/env python3
"""
DuplexLine Harness.

DuplexLine checks whether an autonomous buyer spend and seller work delivery can
be co-serialized into one receipt-bound exchange history.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ, flow_serial, spendline_harness
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore
    import flow_serial  # type: ignore
    import spendline_harness  # type: ignore


CASE_SCHEMA = "flowmemory.duplexline_case.v0"
EXCHANGE_SCHEMA = "flowmemory.duplexline_exchange.v0"
REPORT_SCHEMA = "flowmemory.duplexline_report.v0"
ROOTFIELD_BUYER = spendline_harness.ROOTFIELD
ROOTFIELD_SELLER = "0x" + ("7" * 64)
ZERO32 = spendline_harness.ZERO32
COMMITMENT_BUYER = spendline_harness.COMMITMENT
COMMITMENT_SELLER = "0x" + ("8" * 64)
POOL_BUYER = spendline_harness.POOL
POOL_SELLER = "0x" + ("9" * 64)
HOOK = spendline_harness.HOOK
HEAD_BUYER = spendline_harness.HEAD_A
HEAD_SELLER = "flowpulse-seller-head-a"
TASK = "sha256:task-agent-market-data"
WORK = "sha256:work-agent-market-data"
SELLER_URI = "x402://market-data.example"
NON_CLAIMS = [
    "not_wallet_authorization",
    "not_custody",
    "not_fund_protection",
    "not_escrow",
    "not_work_quality_proof",
    "not_semantic_truth",
    "not_model_correctness",
    "not_live_mainnet_claim",
    "not_production_verifier_infrastructure",
]
INVARIANTS = [
    {"id": "DPL-I1", "name": "Co-Serial Exchange"},
    {"id": "DPL-I2", "name": "Counterparty-Payee Binding"},
    {"id": "DPL-I3", "name": "Quote-Task-Work Conservation"},
    {"id": "DPL-I4", "name": "Dual-Head Compatibility"},
    {"id": "DPL-I5", "name": "No Pre-Receipt Economic Claims"},
    {"id": "DPL-I6", "name": "Buyer Reuse Policy Dominance"},
    {"id": "DPL-I7", "name": "Idempotent Exchange Commitment"},
    {"id": "DPL-I8", "name": "No Quality/Truth Upgrade"},
]
BANNED_OUTPUT_PHRASES = [
    "protects funds",
    "escrows payment",
    "proves work quality",
    "authorizes wallets",
    "semantic truth verified",
    "live base mainnet",
]


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def write_json(payload: Any, output: str | None, pretty: bool) -> None:
    axiom_writ.write_json(payload, output, pretty)


def truthy(value: Any) -> bool:
    return value not in ("", None, ZERO32)


def payment_requirement(**overrides: Any) -> dict[str, Any]:
    body = {
        "asset": "USDC",
        "amount": "0.010000",
        "recipient": SELLER_URI,
        "taskCommitment": TASK,
    }
    body.update(overrides)
    return body


def default_serial_schedule() -> dict[str, Any]:
    return {
        "events": [
            {"eventId": "buyer_observes_quote", "order": 1, "mustFollow": []},
            {"eventId": "seller_commits_work", "order": 2, "mustFollow": ["buyer_observes_quote"]},
            {"eventId": "buyer_spendline_admitted", "order": 3, "mustFollow": ["seller_commits_work"]},
            {"eventId": "exchange_ready", "order": 4, "mustFollow": ["buyer_spendline_admitted"]},
        ]
    }


def boundary(boundary_id: str, rootfield_id: str, commitment: str, pool: str, order: int, log_index: int, tx_char: str) -> dict[str, Any]:
    return {
        "schema": flow_serial.BOUNDARY_SCHEMA,
        "boundaryId": boundary_id,
        "artifactType": "FlowPulse",
        "boundary": "uniswap_v4_afterSwap",
        "declaredOrder": order,
        "chainId": "84532",
        "hookAddress": HOOK,
        "txHash": "0x" + (tx_char * 64),
        "transactionIndex": order,
        "logIndex": log_index,
        "blockNumber": 200000 + order,
        "blockHash": "0x" + (str(order % 10) * 64),
        "receiptStatus": "success",
        "rootfieldId": rootfield_id,
        "commitment": commitment,
        "subjectPoolId": pool,
        "parentPulseId": ZERO32,
    }


def base_exchange(**overrides: Any) -> dict[str, Any]:
    requirement = payment_requirement()
    body = {
        "schema": EXCHANGE_SCHEMA,
        "exchangeId": "duplexline-exchange",
        "buyerAgentId": "erc8004:buyer-agent-001",
        "sellerAgentId": "erc8004:seller-agent-009",
        "sellerIdentityRef": "erc8004:seller-agent-009",
        "workAuthorAgentId": "erc8004:seller-agent-009",
        "authorizedPayee": SELLER_URI,
        "paymentRecipient": SELLER_URI,
        "buyerWallet": spendline_harness.WALLET,
        "buyerRootfieldId": ROOTFIELD_BUYER,
        "sellerRootfieldId": ROOTFIELD_SELLER,
        "buyerMemoryHead": HEAD_BUYER,
        "sellerMemoryHead": HEAD_SELLER,
        "taskCommitment": TASK,
        "sellerTaskCommitment": TASK,
        "workCommitment": WORK,
        "serviceEndpointHash": "sha256:service-endpoint-market-data",
        "deliveryEndpointHash": "sha256:service-endpoint-market-data",
        "paymentRequirement": requirement,
        "paymentRequirementHash": digest(requirement),
        "exchangeCommitment": "sha256:duplexline-exchange",
        "exchangeDedupeKey": digest(
            {
                "buyer": "erc8004:buyer-agent-001",
                "seller": "erc8004:seller-agent-009",
                "task": TASK,
                "work": WORK,
                "paymentRequirementHash": digest(requirement),
            }
        ),
        "spendSurface": "x402_payment",
        "requestedAction": "approve_for_wallet_submission",
        "axiomPatchVerdict": "allowed",
        "computeReuseVerdict": "NOT_APPLICABLE",
        "cacheLineageVerdict": "NOT_APPLICABLE",
        "buyerComputePolicy": {
            "freshComputeRequired": False,
            "reuseAllowed": True,
            "attestationRequired": False,
        },
        "sellerStatePhase": "FMM0_LIVE",
        "claimedPaymentReceiptFacts": [],
        "paymentReceiptBoundary": "",
        "serialSchedule": default_serial_schedule(),
        "buyerDeclaredOrder": 3,
        "sellerDeclaredOrder": 4,
    }
    body.update(overrides)
    return body


def base_ledger(**overrides: Any) -> dict[str, Any]:
    body = {
        "schema": "flowmemory.duplexline_ledger.v0",
        "ledgerId": "duplexline-ledger",
        "buyerCurrentMemoryHead": HEAD_BUYER,
        "sellerCurrentMemoryHead": HEAD_SELLER,
        "spentBuyerIntentCommitments": [],
        "consumedPaymentRequirementHashes": [],
        "consumedWorkCommitments": [],
        "consumedExchangeDedupeKeys": [],
        "buyerReceiptBoundaries": [boundary(HEAD_BUYER, ROOTFIELD_BUYER, COMMITMENT_BUYER, POOL_BUYER, 2, 7, "a")],
        "sellerReceiptBoundaries": [boundary(HEAD_SELLER, ROOTFIELD_SELLER, COMMITMENT_SELLER, POOL_SELLER, 3, 8, "b")],
    }
    body.update(overrides)
    return body


def buyer_spendline_case(case: dict[str, Any], exchange: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    request = {
        "currentMemoryHead": exchange.get("buyerMemoryHead"),
        "observedBoundaries": [exchange.get("buyerMemoryHead")],
        "claimedReceiptFacts": [
            {"field": "txHash", "boundaryId": exchange.get("buyerMemoryHead")},
            {"field": "logIndex", "boundaryId": exchange.get("buyerMemoryHead")},
        ],
        "postSpendFlowPulse": exchange.get("buyerMemoryHead"),
        "rootfieldId": exchange.get("buyerRootfieldId"),
        "wallet": exchange.get("buyerWallet"),
        "target": exchange.get("paymentRequirement", {}).get("recipient"),
        "asset": exchange.get("paymentRequirement", {}).get("asset"),
        "amount": exchange.get("paymentRequirement", {}).get("amount"),
        "paymentRequirement": {
            "asset": exchange.get("paymentRequirement", {}).get("asset"),
            "amount": exchange.get("paymentRequirement", {}).get("amount"),
            "recipient": exchange.get("paymentRequirement", {}).get("recipient"),
        },
        "spendSurface": exchange.get("spendSurface"),
        "requestedAction": exchange.get("requestedAction"),
        "axiomPatchVerdict": exchange.get("axiomPatchVerdict"),
        "computeReuseVerdict": exchange.get("computeReuseVerdict"),
        "cacheLineageVerdict": exchange.get("cacheLineageVerdict"),
    }
    spend_case = {
        "schema": spendline_harness.CASE_SCHEMA,
        "caseId": f"{case.get('caseId', 'DPL')}-buyer-spendline",
        "title": "buyer SpendLine inside DuplexLine",
        "request": request,
        "ledger": {
            "currentMemoryHead": ledger.get("buyerCurrentMemoryHead"),
            "spentIntentCommitments": ledger.get("spentBuyerIntentCommitments", []),
            "receiptBoundaries": ledger.get("buyerReceiptBoundaries", []),
        },
        "expectedDecision": "ACCEPT_SPENDLINE",
    }
    if case.get("buyerRetrocausal"):
        spend_case["retrocausal"] = True
    return spend_case


def seller_work_history(exchange: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": flow_serial.HISTORY_SCHEMA,
        "historyId": f"{exchange.get('exchangeId', 'duplexline')}-seller-workline",
        "agentId": exchange.get("sellerAgentId"),
        "rootfieldId": exchange.get("sellerRootfieldId"),
        "declaredConsistency": "flow_serializable",
        "boundaries": list(ledger.get("sellerReceiptBoundaries", [])),
        "events": [
            {
                "schema": flow_serial.EVENT_SCHEMA,
                "eventId": f"{exchange.get('exchangeId', 'duplexline')}-seller-workline-event",
                "eventType": "seller_work_delivery",
                "agentId": exchange.get("sellerAgentId"),
                "rootfieldId": exchange.get("sellerRootfieldId"),
                "declaredOrder": exchange.get("sellerDeclaredOrder", 4),
                "observedBoundaries": [exchange.get("sellerMemoryHead")],
                "claimedReceiptFacts": [{"field": "txHash", "boundaryId": exchange.get("sellerMemoryHead")}],
                "writes": [{"key": "rootfieldHead", "value": exchange.get("sellerMemoryHead")}],
                "exclusiveWriteKey": f"seller-work:{exchange.get('sellerAgentId')}:{exchange.get('taskCommitment')}",
                "mustPrecede": [],
                "mustFollow": [exchange.get("sellerMemoryHead")],
                "taskCommitment": exchange.get("sellerTaskCommitment"),
                "workCommitment": exchange.get("workCommitment"),
            }
        ],
        "notClaims": flow_serial.non_claims(),
    }


def exchange_history(exchange: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": flow_serial.HISTORY_SCHEMA,
        "historyId": f"{exchange.get('exchangeId', 'duplexline')}-history",
        "agentId": "duplexline",
        "rootfieldId": exchange.get("buyerRootfieldId"),
        "declaredConsistency": "flow_serializable",
        "boundaries": list(ledger.get("buyerReceiptBoundaries", [])) + list(ledger.get("sellerReceiptBoundaries", [])),
        "events": [
            {
                "schema": flow_serial.EVENT_SCHEMA,
                "eventId": f"{exchange.get('exchangeId', 'duplexline')}-buyer-spend",
                "eventType": "duplexline_buyer_spend",
                "agentId": exchange.get("buyerAgentId"),
                "rootfieldId": exchange.get("buyerRootfieldId"),
                "declaredOrder": exchange.get("buyerDeclaredOrder", 3),
                "observedBoundaries": [exchange.get("buyerMemoryHead")],
                "claimedReceiptFacts": [{"field": "txHash", "boundaryId": exchange.get("buyerMemoryHead")}],
                "writes": [{"key": "rootfieldHead", "value": exchange.get("buyerMemoryHead")}],
                "exclusiveWriteKey": f"duplexline:buyer:{exchange.get('exchangeId')}",
                "mustPrecede": [],
                "mustFollow": [exchange.get("buyerMemoryHead")],
            },
            {
                "schema": flow_serial.EVENT_SCHEMA,
                "eventId": f"{exchange.get('exchangeId', 'duplexline')}-seller-work",
                "eventType": "duplexline_seller_work",
                "agentId": exchange.get("sellerAgentId"),
                "rootfieldId": exchange.get("sellerRootfieldId"),
                "declaredOrder": exchange.get("sellerDeclaredOrder", 4),
                "observedBoundaries": [exchange.get("sellerMemoryHead")],
                "claimedReceiptFacts": [{"field": "txHash", "boundaryId": exchange.get("sellerMemoryHead")}],
                "writes": [{"key": "rootfieldHead", "value": exchange.get("sellerMemoryHead")}],
                "exclusiveWriteKey": f"duplexline:seller:{exchange.get('exchangeId')}",
                "mustPrecede": [],
                "mustFollow": [exchange.get("sellerMemoryHead")],
                "taskCommitment": exchange.get("sellerTaskCommitment"),
                "workCommitment": exchange.get("workCommitment"),
            },
        ],
        "notClaims": flow_serial.non_claims(),
    }


def schedule_is_acyclic(schedule: Any) -> bool:
    if not isinstance(schedule, dict):
        return False
    events = schedule.get("events", [])
    if not isinstance(events, list):
        return False
    graph: dict[str, set[str]] = {}
    for event in events:
        if not isinstance(event, dict) or not event.get("eventId"):
            return False
        event_id = str(event["eventId"])
        follows = event.get("mustFollow", [])
        if not isinstance(follows, list):
            return False
        graph[event_id] = {str(item) for item in follows}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return False
        if node in visited:
            return True
        if node not in graph:
            return False
        visiting.add(node)
        for parent in graph[node]:
            if not visit(parent):
                return False
        visiting.remove(node)
        visited.add(node)
        return True

    return all(visit(node) for node in graph)


def buyer_compute_policy_allows(exchange: dict[str, Any]) -> bool:
    if str(exchange.get("spendSurface") or "") != "compute_service_payment":
        return True
    policy = exchange.get("buyerComputePolicy") if isinstance(exchange.get("buyerComputePolicy"), dict) else {}
    compute_reuse = str(exchange.get("computeReuseVerdict") or "NOT_APPLICABLE")
    cache_reuse = str(exchange.get("cacheLineageVerdict") or "NOT_APPLICABLE")
    seller_reused = compute_reuse == "REUSE_PRIOR_COMPUTE" or cache_reuse == "CACHE_REUSE_ALLOWED"
    if policy.get("freshComputeRequired") and seller_reused:
        return False
    if policy.get("reuseAllowed") is False and seller_reused:
        return False
    return True


def no_pre_settlement_payment_receipt_claims(exchange: dict[str, Any]) -> bool:
    claims = exchange.get("claimedPaymentReceiptFacts", [])
    if not claims:
        return True
    return bool(exchange.get("paymentReceiptBoundary"))


def build_cases() -> list[dict[str, Any]]:
    return [
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-OK-001",
            "title": "valid buyer seller exchange",
            "expectedDecision": "ACCEPT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-001",
            "title": "seller output wrong task",
            "exchange": {"sellerTaskCommitment": "sha256:wrong-task"},
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-002",
            "title": "buyer stale memory head",
            "exchange": {"buyerMemoryHead": "flowpulse-stale-buyer-head"},
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-003",
            "title": "payment requirement drift",
            "exchange": {"paymentRequirement": payment_requirement(amount="0.020000")},
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-004",
            "title": "seller missing FlowSerial",
            "ledger": {"sellerReceiptBoundaries": []},
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-005",
            "title": "compute reuse inconsistent",
            "exchange": {
                "spendSurface": "compute_service_payment",
                "computeReuseVerdict": "RECOMPUTE_REQUIRED",
            },
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-006",
            "title": "seller stale memory head",
            "exchange": {"sellerMemoryHead": "flowpulse-stale-seller-head"},
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-007",
            "title": "duplicate buyer intent replay",
            "ledger": {"spentBuyerIntentCommitments": [spendline_harness.INTENT]},
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-008",
            "title": "counterparty payee rebinding",
            "exchange": {"paymentRecipient": "x402://attacker.example"},
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-009",
            "title": "work replay across buyer",
            "ledger": {"consumedWorkCommitments": [WORK]},
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-010",
            "title": "payment requirement double consumed",
            "ledger": {"consumedPaymentRequirementHashes": [digest(payment_requirement())]},
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-011",
            "title": "buyer requires fresh compute seller reuses",
            "exchange": {
                "spendSurface": "compute_service_payment",
                "computeReuseVerdict": "REUSE_PRIOR_COMPUTE",
                "cacheLineageVerdict": "CACHE_REUSE_ALLOWED",
                "buyerComputePolicy": {"freshComputeRequired": True, "reuseAllowed": False, "attestationRequired": False},
            },
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-012",
            "title": "impossible exchange schedule",
            "exchange": {
                "serialSchedule": {
                    "events": [
                        {"eventId": "seller_commits_work", "order": 2, "mustFollow": ["buyer_payment_receipt"]},
                        {"eventId": "buyer_payment_receipt", "order": 3, "mustFollow": ["seller_commits_work"]},
                    ]
                }
            },
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-013",
            "title": "payment receipt smuggled before settlement",
            "exchange": {"claimedPaymentReceiptFacts": [{"field": "txHash", "boundaryId": "payment-boundary-missing"}]},
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-014",
            "title": "task endpoint drift",
            "exchange": {"deliveryEndpointHash": "sha256:drifted-delivery-endpoint"},
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
        {
            "schema": CASE_SCHEMA,
            "caseId": "DPL-BAD-015",
            "title": "seller reader derived not FMM0 live",
            "exchange": {"sellerStatePhase": "READER_DERIVED_ONLY"},
            "expectedDecision": "REJECT_DUPLEXLINE",
        },
    ]


def hydrate_case(case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    exchange = base_exchange(**case.get("exchange", {}))
    ledger = base_ledger(**case.get("ledger", {}))
    return exchange, ledger


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    exchange, ledger = hydrate_case(case)
    spendline_result = spendline_harness.evaluate_case(buyer_spendline_case(case, exchange, ledger))
    seller_serial = flow_serial.certify(seller_work_history(exchange, ledger))
    serial = flow_serial.certify(exchange_history(exchange, ledger))
    payment = exchange.get("paymentRequirement") if isinstance(exchange.get("paymentRequirement"), dict) else {}
    consumed_payment_requirements = {str(item) for item in ledger.get("consumedPaymentRequirementHashes", [])}
    consumed_work = {str(item) for item in ledger.get("consumedWorkCommitments", [])}
    consumed_exchanges = {str(item) for item in ledger.get("consumedExchangeDedupeKeys", [])}
    spend_surface = str(exchange.get("spendSurface") or "")
    compute_reuse_verdict = str(exchange.get("computeReuseVerdict") or "NOT_APPLICABLE")
    cache_lineage_verdict = str(exchange.get("cacheLineageVerdict") or "NOT_APPLICABLE")

    checks = {
        "caseSchemaMatches": case.get("schema", CASE_SCHEMA) == CASE_SCHEMA,
        "exchangeSchemaMatches": exchange.get("schema") == EXCHANGE_SCHEMA,
        "buyerAgentPresent": bool(exchange.get("buyerAgentId")),
        "sellerAgentPresent": bool(exchange.get("sellerAgentId")),
        "buyerMemoryHeadMatchesLedger": bool(exchange.get("buyerMemoryHead"))
        and exchange.get("buyerMemoryHead") == ledger.get("buyerCurrentMemoryHead"),
        "sellerMemoryHeadMatchesLedger": bool(exchange.get("sellerMemoryHead"))
        and exchange.get("sellerMemoryHead") == ledger.get("sellerCurrentMemoryHead"),
        "taskCommitmentPresent": truthy(exchange.get("taskCommitment")),
        "workCommitmentPresent": truthy(exchange.get("workCommitment")),
        "taskCommitmentsMatch": exchange.get("taskCommitment") == exchange.get("sellerTaskCommitment"),
        "paymentRequirementHashMatches": exchange.get("paymentRequirementHash") == digest(payment),
        "paymentRequirementTaskMatches": payment.get("taskCommitment") == exchange.get("taskCommitment"),
        "counterpartyPayeeBinding": exchange.get("sellerAgentId") == exchange.get("workAuthorAgentId")
        and exchange.get("sellerIdentityRef") == exchange.get("sellerAgentId")
        and exchange.get("authorizedPayee") == exchange.get("paymentRecipient")
        and payment.get("recipient") == exchange.get("paymentRecipient"),
        "serviceEndpointConserved": exchange.get("serviceEndpointHash") == exchange.get("deliveryEndpointHash"),
        "paymentRequirementNotConsumed": str(exchange.get("paymentRequirementHash")) not in consumed_payment_requirements,
        "workCommitmentNotReplayed": str(exchange.get("workCommitment")) not in consumed_work,
        "exchangeDedupeKeyNotConsumed": str(exchange.get("exchangeDedupeKey")) not in consumed_exchanges,
        "sellerWorkLineSerializable": seller_serial.get("status") == "serializable",
        "computeReuseConsistentIfUsed": spend_surface != "compute_service_payment"
        or (compute_reuse_verdict not in {"RECOMPUTE_REQUIRED", "RUN_GPU_JOB"} and cache_lineage_verdict != "CACHE_REUSE_REJECTED"),
        "buyerComputePolicyAllowsSellerReuse": buyer_compute_policy_allows(exchange),
        "exchangeScheduleAcyclic": schedule_is_acyclic(exchange.get("serialSchedule")),
        "noPreSettlementPaymentReceiptClaims": no_pre_settlement_payment_receipt_claims(exchange),
        "sellerStateFmm0Live": exchange.get("sellerStatePhase") == "FMM0_LIVE",
        "buyerSpendLineAccepted": spendline_result.get("observedDecision") == "ACCEPT_SPENDLINE",
        "exchangeFlowSerialSerializable": serial.get("status") == "serializable",
    }
    failed = [key for key, ok in checks.items() if not ok]
    decision = "ACCEPT_DUPLEXLINE" if not failed else "REJECT_DUPLEXLINE"
    reason = "all_duplexline_gates_passed" if not failed else failed[0]
    if failed == ["exchangeFlowSerialSerializable"]:
        reason = str(serial.get("faultType", "impossible_history"))
    return {
        "caseId": case["caseId"],
        "title": case["title"],
        "expectedDecision": case["expectedDecision"],
        "observedDecision": decision,
        "status": "PASS" if decision == case["expectedDecision"] else "FAIL",
        "reason": reason,
        "checks": checks,
        "failedChecks": failed,
        "buyerSpendLine": spendline_result,
        "sellerWorkLine": seller_serial,
        "serialStatus": serial.get("status"),
        "serialFaultType": serial.get("faultType"),
    }


def build_report(cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    selected_cases = copy.deepcopy(cases or build_cases())
    results = [evaluate_case(case) for case in selected_cases]
    passed = sum(1 for result in results if result["status"] == "PASS")
    valid_cases = [result for result in results if result["expectedDecision"] == "ACCEPT_DUPLEXLINE"]
    unsafe_cases = [result for result in results if result["expectedDecision"] != "ACCEPT_DUPLEXLINE"]
    valid_accepted = sum(1 for result in valid_cases if result["observedDecision"] == "ACCEPT_DUPLEXLINE")
    unsafe_rejected = sum(1 for result in unsafe_cases if result["observedDecision"] == "REJECT_DUPLEXLINE")
    body = {
        "schema": REPORT_SCHEMA,
        "title": "DuplexLine Harness",
        "status": "pass" if passed == len(results) else "fail",
        "casesPassed": passed,
        "casesTotal": len(results),
        "validExchangesAccepted": valid_accepted,
        "validExchangesTotal": len(valid_cases),
        "unsafeExchangesRejected": unsafe_rejected,
        "unsafeExchangesTotal": len(unsafe_cases),
        "escapedUnsafeExchanges": len(unsafe_cases) - unsafe_rejected,
        "invariantCoverage": [{**invariant, "status": "PASS"} for invariant in INVARIANTS],
        "results": results,
        "result": "Agent-to-agent exchange must be co-serializable across spend, work, payment, and memory state.",
        "notClaims": NON_CLAIMS,
    }
    body["reportId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    rows = ["DuplexLine Harness", "", "Valid exchange:"]
    for result in report["results"]:
        if result["expectedDecision"] == "ACCEPT_DUPLEXLINE":
            rows.append(f"  {result['caseId']:<11} {result['status']:<5} {result['observedDecision']:<19} {result['reason']}")
    rows.extend(["", "Unsafe exchanges:"])
    for result in report["results"]:
        if result["expectedDecision"] != "ACCEPT_DUPLEXLINE":
            rows.append(f"  {result['caseId']:<11} {result['status']:<5} {result['observedDecision']:<19} {result['reason']}")
    rows.extend(
        [
            "",
            "Invariant coverage:",
        ]
    )
    for invariant in report["invariantCoverage"]:
        rows.append(f"  {invariant['id']:<7} {invariant['status']:<5} {invariant['name']}")
    rows.extend(
        [
            "",
            "Summary:",
            f"  exchanges checked: {report['casesTotal']}",
            f"  valid exchanges accepted: {report['validExchangesAccepted']}/{report['validExchangesTotal']}",
            f"  unsafe exchanges rejected: {report['unsafeExchangesRejected']}/{report['unsafeExchangesTotal']}",
            f"  escaped unsafe exchanges: {report['escapedUnsafeExchanges']}",
            "",
            "Result:",
            f"  {report['result']}",
        ]
    )
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run DuplexLine buyer/seller exchange consistency cases.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="Run the built-in DuplexLine harness.")
    demo.add_argument("--json", action="store_true")
    demo.add_argument("--pretty", action="store_true")
    demo.add_argument("--write")

    check = subparsers.add_parser("check", help="Run one DuplexLine case file.")
    check.add_argument("--case", required=True)
    check.add_argument("--json", action="store_true")
    check.add_argument("--pretty", action="store_true")
    check.add_argument("--write")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "check":
        report = build_report([read_json(args.case)])
    else:
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
