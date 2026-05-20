#!/usr/bin/env python3
"""Receipt Runtime MVP demo.

This is the architecture loop identified as the missing product primitive:
memory does not only get observed after execution; it gates an action before
execution and settles the result after receipt evidence exists.

The demo is deterministic and local. It does not authorize wallets, custody
funds, settle real payments, prove semantic truth, or claim production
verifier readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any


SCHEMA = "flowmemory.receipt_runtime_demo.v0"
NON_CLAIMS = [
    "no_wallet_authorization",
    "no_custody",
    "no_escrow",
    "no_fund_protection",
    "no_semantic_truth",
    "no_model_correctness",
    "no_live_payment_settlement",
    "no_onchain_bond_escrow",
    "no_tee_or_zk_privacy_claim",
    "no_live_base_mainnet_claim",
]


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: Any) -> str:
    return "sha256:" + sha256(canonical(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Provider:
    provider_id: str
    label: str
    quoted_cost_usd: str
    privacy_mode: str
    has_required_bond: bool
    expected_policy_pass: bool
    expected_flowpulse_link: bool


def build_policy_card() -> dict[str, Any]:
    body = {
        "schema": "flowmemory.policy_card.v0",
        "policyId": "policy.safe-swap-demo",
        "rootfieldId": "rootfield.demo.safe-swap",
        "allowedActor": "agent.demo",
        "actionClass": "uniswap_v4_safe_swap_memory_signal",
        "requiredMemoryHead": "pulse.head.001",
        "maxSpendUsd": "25.00",
        "requiresProviderBond": True,
        "requiresPostActionFlowPulse": True,
        "expiresAt": "2026-05-21T00:00:00Z",
    }
    body["policyHash"] = digest(body)
    return body


def build_action_intent(policy: dict[str, Any]) -> dict[str, Any]:
    body = {
        "schema": "flowmemory.action_intent.v0",
        "actor": policy["allowedActor"],
        "actionClass": policy["actionClass"],
        "rootfieldId": policy["rootfieldId"],
        "memoryHeadBefore": policy["requiredMemoryHead"],
        "requestedSpendUsd": "12.00",
        "subject": "base-sepolia-uniswap-v4-demo-pool",
        "commitment": "sha256:demo-action-commitment",
    }
    body["actionIntentHash"] = digest(body)
    return body


def issue_pulse_permit(policy: dict[str, Any], action_intent: dict[str, Any]) -> dict[str, Any]:
    body = {
        "schema": "flowmemory.pulse_permit.v0",
        "permitId": "permit.safe-swap-demo.001",
        "policyHash": policy["policyHash"],
        "actor": policy["allowedActor"],
        "rootfieldId": policy["rootfieldId"],
        "headBefore": policy["requiredMemoryHead"],
        "actionIntentHash": action_intent["actionIntentHash"],
        "requiresProviderBond": policy["requiresProviderBond"],
        "requiresPostActionFlowPulse": policy["requiresPostActionFlowPulse"],
        "expiresAt": policy["expiresAt"],
    }
    body["permitHash"] = digest(body)
    return body


def evaluate_pulse_permit(
    policy: dict[str, Any],
    permit: dict[str, Any],
    action_intent: dict[str, Any],
    current_memory_head: str,
) -> dict[str, Any]:
    reasons: list[str] = []
    if permit["policyHash"] != policy["policyHash"]:
        reasons.append("policy_hash_mismatch")
    if permit["headBefore"] != current_memory_head:
        reasons.append("stale_memory_head")
    if permit["actionIntentHash"] != action_intent["actionIntentHash"]:
        reasons.append("action_intent_hash_mismatch")
    if permit["actor"] != action_intent["actor"]:
        reasons.append("actor_mismatch")
    return {
        "schema": "flowmemory.pulse_permit_verdict.v0",
        "status": "ALLOW" if not reasons else "DENY",
        "reasons": reasons,
        "permitHash": permit["permitHash"],
        "currentMemoryHead": current_memory_head,
    }


def demo_providers() -> list[Provider]:
    return [
        Provider(
            provider_id="provider.cheap-unbonded",
            label="cheap provider",
            quoted_cost_usd="0.001",
            privacy_mode="none",
            has_required_bond=False,
            expected_policy_pass=False,
            expected_flowpulse_link=False,
        ),
        Provider(
            provider_id="provider.private-bonded",
            label="private bonded provider",
            quoted_cost_usd="0.012",
            privacy_mode="scoped_private_claim",
            has_required_bond=True,
            expected_policy_pass=True,
            expected_flowpulse_link=True,
        ),
        Provider(
            provider_id="provider.expensive-bonded",
            label="expensive provider",
            quoted_cost_usd="0.090",
            privacy_mode="public_receipt",
            has_required_bond=True,
            expected_policy_pass=True,
            expected_flowpulse_link=True,
        ),
    ]


def route_providers(policy: dict[str, Any], providers: list[Provider]) -> dict[str, Any]:
    candidates = []
    for provider in providers:
        reasons = []
        if policy["requiresProviderBond"] and not provider.has_required_bond:
            reasons.append("missing_required_provider_bond")
        if not provider.expected_policy_pass:
            reasons.append("provider_expected_policy_failure")
        if policy["requiresPostActionFlowPulse"] and not provider.expected_flowpulse_link:
            reasons.append("missing_expected_flowpulse_link")
        status = "ROUTE_ACCEPTED" if not reasons else "ROUTE_REJECTED"
        cost = float(provider.quoted_cost_usd)
        cost_per_success = cost if status == "ROUTE_ACCEPTED" else None
        candidates.append(
            {
                "providerId": provider.provider_id,
                "label": provider.label,
                "quotedCostUsd": provider.quoted_cost_usd,
                "privacyMode": provider.privacy_mode,
                "status": status,
                "reasons": reasons,
                "costPerSuccessfulOutcomeUsd": cost_per_success,
            }
        )

    accepted = [item for item in candidates if item["status"] == "ROUTE_ACCEPTED"]
    selected = min(accepted, key=lambda item: item["costPerSuccessfulOutcomeUsd"])
    return {
        "schema": "flowmemory.route_score.v0",
        "candidates": candidates,
        "selectedProviderId": selected["providerId"],
        "selectedReason": "lowest_cost_per_policy_successful_outcome",
    }


def build_action_pulse(permit: dict[str, Any], action_intent: dict[str, Any], route: dict[str, Any]) -> dict[str, Any]:
    body = {
        "schema": "flowmemory.action_pulse.v0",
        "actionPulseId": "actionpulse.safe-swap-demo.001",
        "permitHash": permit["permitHash"],
        "actionIntentHash": action_intent["actionIntentHash"],
        "selectedProviderId": route["selectedProviderId"],
        "status": "ACTION_PROPOSED",
    }
    body["actionPulseHash"] = digest(body)
    return body


def build_flowpulse_link(action_pulse: dict[str, Any]) -> dict[str, Any]:
    body = {
        "schema": "flowmemory.flowpulse_link.v0",
        "actionPulseHash": action_pulse["actionPulseHash"],
        "flowPulseId": "pulse.demo.after-swap.001",
        "chainId": "84532",
        "hookAddress": "0x0000000000000000000000000000000000000040",
        "txHash": "0x1111111111111111111111111111111111111111111111111111111111111111",
        "logIndex": "2",
        "receiptStatus": "success",
        "finality": "receipt_attached",
    }
    body["flowPulseLinkHash"] = digest(body)
    return body


def settle_outcome(
    action_pulse: dict[str, Any],
    flowpulse_link: dict[str, Any],
    route: dict[str, Any],
) -> dict[str, Any]:
    selected = next(
        item for item in route["candidates"] if item["providerId"] == route["selectedProviderId"]
    )
    body = {
        "schema": "flowmemory.outcome_pulse.v0",
        "outcomePulseId": "outcome.safe-swap-demo.001",
        "actionPulseHash": action_pulse["actionPulseHash"],
        "flowPulseLinkHash": flowpulse_link["flowPulseLinkHash"],
        "selectedProviderId": route["selectedProviderId"],
        "costPerSuccessfulOutcomeUsd": selected["costPerSuccessfulOutcomeUsd"],
        "status": "OUTCOME_SETTLED",
    }
    body["outcomePulseHash"] = digest(body)
    return body


def build_pulsepass_claim(outcome: dict[str, Any], route: dict[str, Any]) -> dict[str, Any]:
    public_source = {
        "outcomePulseHash": outcome["outcomePulseHash"],
        "selectedProviderId": route["selectedProviderId"],
    }
    body = {
        "schema": "flowmemory.pulsepass_claim.v0",
        "claimId": "pulsepass.safe-swap-demo.001",
        "predicate": "bonded_policy_safe_swap_count >= 1",
        "owner": "user.demo",
        "sourcePulseSetHash": digest(public_source),
        "disclosure": {
            "providerId": "hidden",
            "txHash": "hidden",
            "amount": "hidden",
            "predicate": "revealed",
        },
        "unlocks": [
            "higher_agent_spend_limit",
            "lower_required_provider_bond",
            "claim_gated_agent_access",
        ],
    }
    body["claimHash"] = digest(body)
    return body


def build_report(current_memory_head: str = "pulse.head.001") -> dict[str, Any]:
    policy = build_policy_card()
    action_intent = build_action_intent(policy)
    permit = issue_pulse_permit(policy, action_intent)
    permit_verdict = evaluate_pulse_permit(policy, permit, action_intent, current_memory_head)
    route = route_providers(policy, demo_providers())
    action_pulse = build_action_pulse(permit, action_intent, route)
    flowpulse_link = build_flowpulse_link(action_pulse)
    outcome = settle_outcome(action_pulse, flowpulse_link, route)
    claim = build_pulsepass_claim(outcome, route)

    pass_conditions = [
        permit_verdict["status"] == "ALLOW",
        route["selectedProviderId"] == "provider.private-bonded",
        outcome["status"] == "OUTCOME_SETTLED",
        claim["disclosure"]["providerId"] == "hidden",
        claim["disclosure"]["txHash"] == "hidden",
    ]

    body = {
        "schema": SCHEMA,
        "status": "pass" if all(pass_conditions) else "fail",
        "thesis": "Memory should gate the action before execution and settle the outcome after receipt evidence.",
        "policyCard": policy,
        "actionIntent": action_intent,
        "pulsePermit": permit,
        "pulsePermitVerdict": permit_verdict,
        "routeScore": route,
        "actionPulse": action_pulse,
        "flowPulseLink": flowpulse_link,
        "outcomePulse": outcome,
        "pulsePassClaim": claim,
        "selectedRoute": route["selectedProviderId"],
        "userUnlocks": claim["unlocks"],
        "notClaims": NON_CLAIMS,
    }
    body["demoId"] = digest(body)
    return body


def render_report(report: dict[str, Any]) -> str:
    route = report["routeScore"]
    rows = [
        "FlowMemory Receipt Runtime Demo",
        "",
        f"status: {report['status'].upper()}",
        "",
        "Loop:",
        "  1. PolicyCard created",
        "  2. PulsePermit issued from current memory head",
        "  3. Providers evaluated by policy success, bond status, and cost per successful outcome",
        "  4. ActionPulse created for selected route",
        "  5. FlowPulse receipt linked",
        "  6. OutcomePulse settled",
        "  7. PulsePass claim generated with scoped disclosure",
        "",
        "Provider routes:",
    ]
    for item in route["candidates"]:
        cost = item["costPerSuccessfulOutcomeUsd"]
        cost_text = "infinite" if cost is None else f"${cost:.3f}"
        rows.append(
            f"  {item['label']:<24} {item['status']:<15} quoted ${item['quotedCostUsd']:<6} cost/success {cost_text}"
        )
        for reason in item["reasons"]:
            rows.append(f"    reject: {reason}")
    rows.extend(
        [
            "",
            f"Selected route: {route['selectedProviderId']}",
            f"PulsePermit:    {report['pulsePermitVerdict']['status']}",
            f"OutcomePulse:   {report['outcomePulse']['status']}",
            "PulsePass:",
            f"  predicate: {report['pulsePassClaim']['predicate']}",
            f"  provider:  {report['pulsePassClaim']['disclosure']['providerId']}",
            f"  txHash:    {report['pulsePassClaim']['disclosure']['txHash']}",
            "",
            "Result:",
            "  Receipt-bound memory gated the action, selected the best successful route, settled the outcome, and produced a private portable claim.",
        ]
    )
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the FlowMemory receipt runtime MVP demo.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON; text output is already readable.")
    parser.add_argument("--current-memory-head", default="pulse.head.001")
    parser.add_argument("--write", help="Write text output to a file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.current_memory_head)
    text = render_report(report)
    if args.write:
        output_path = Path(args.write)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
