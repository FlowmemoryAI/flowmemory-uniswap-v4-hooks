#!/usr/bin/env python3
"""
PulseRetire Queue: receipt-driven retirement for speculative cognition.

Agents and GPU workflows can compute ahead, but speculative artifacts do not
become live until a matching receipt-bound FlowPulse retires them.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover - supports script and package execution
    from tools import axiom_writ
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore


QUEUE_SCHEMA = "flowmemory.pulse_retire_queue.v0"
RETIREMENT_SCHEMA = "flowmemory.pulse_retirement.v0"
ENFORCEMENT_SCHEMA = "flowmemory.pulse_retire_enforcement.v0"
ZERO32 = "0x" + ("0" * 64)
FORBIDDEN_RECEIPT_FIELDS = ["txHash", "logIndex", "transactionIndex", "blockHash"]


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def write_json(payload: Any, output: str | None, pretty: bool) -> None:
    axiom_writ.write_json(payload, output, pretty)


def normalize_hex(value: Any) -> str:
    return axiom_writ.normalize_hex(value)


def truthy_hex(value: Any) -> bool:
    return axiom_writ.truthy_hex(value)


def forbidden_paths(value: Any, prefix: str = "$") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            current = f"{prefix}.{key}"
            if key in FORBIDDEN_RECEIPT_FIELDS and nested not in (None, ""):
                paths.append(current)
            paths.extend(forbidden_paths(nested, current))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            paths.extend(forbidden_paths(nested, f"{prefix}[{index}]"))
    return paths


def queue_identity(agent_id: str, rootfield_id: str, retirement_mode: str = "in_order") -> dict[str, Any]:
    return {
        "schema": QUEUE_SCHEMA,
        "queueType": "receipt_driven_retirement_queue",
        "agentId": agent_id,
        "rootfieldId": normalize_hex(rootfield_id),
        "retirementMode": retirement_mode,
    }


def create_queue(agent_id: str, rootfield_id: str, retirement_mode: str = "in_order") -> dict[str, Any]:
    identity = queue_identity(agent_id, rootfield_id, retirement_mode)
    return {
        **identity,
        "queueId": axiom_writ.digest(identity),
        "entries": [],
        "notClaims": [
            "not_financial_debt",
            "not_token",
            "not_custody",
            "not_swap_control",
            "not_semantic_truth",
            "not_gpu_attestation",
            "not_hardware_acceleration",
        ],
    }


def verify_queue(queue: dict[str, Any]) -> dict[str, Any]:
    expected_queue_id = axiom_writ.digest(
        queue_identity(str(queue.get("agentId", "")), str(queue.get("rootfieldId", "")), str(queue.get("retirementMode", "in_order")))
    )
    entry_checks = []
    for entry in queue.get("entries", []):
        if not isinstance(entry, dict):
            entry_checks.append(False)
            continue
        body = copy.deepcopy(entry)
        entry_id = body.pop("entryId", None)
        entry_checks.append(axiom_writ.digest(body) == entry_id)
    checks = {
        "schemaMatches": queue.get("schema") == QUEUE_SCHEMA,
        "queueIdMatches": queue.get("queueId") == expected_queue_id,
        "entriesValid": all(entry_checks),
        "hasNotClaims": "not_semantic_truth" in (queue.get("notClaims") or []),
    }
    failed = [key for key, ok in checks.items() if not ok]
    return {
        "schema": "flowmemory.pulse_retire_queue_verification.v0",
        "status": "valid" if not failed else "invalid",
        "queueId": queue.get("queueId"),
        "checks": checks,
        "failedChecks": failed,
    }


def entry_body(queue: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    expected = artifact.get("expectedPulse") if isinstance(artifact.get("expectedPulse"), dict) else {}
    return {
        "queuePosition": len(queue.get("entries", [])),
        "artifactId": artifact.get("artifactId"),
        "artifactType": artifact.get("artifactType"),
        "artifactState": "speculative",
        "createdBeforeReceipt": True,
        "artifactCommitment": artifact.get("artifactCommitment") or artifact.get("commitment"),
        "expectedPulse": {
            "boundary": expected.get("boundary", "uniswap_v4_afterSwap"),
            "rootfieldId": normalize_hex(expected.get("rootfieldId")),
            "commitment": normalize_hex(expected.get("commitment")),
            "hookAddress": normalize_hex(expected.get("hookAddress")),
            "subjectPoolId": normalize_hex(expected.get("subjectPoolId")),
            "parentPulseId": normalize_hex(expected.get("parentPulseId")),
        },
        "forbiddenAtEnqueue": FORBIDDEN_RECEIPT_FIELDS,
        "onRetire": artifact.get("onRetire", ["allow_as_live_context"]),
        "onSquash": artifact.get("onSquash", ["withhold_artifact", "require_fresh_compute"]),
    }


def enqueue_artifact(queue: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    paths = forbidden_paths(artifact)
    if paths:
        raise ValueError(f"speculative artifact contains receipt-only fields: {', '.join(paths)}")
    expected = artifact.get("expectedPulse") if isinstance(artifact.get("expectedPulse"), dict) else {}
    if normalize_hex(expected.get("rootfieldId")) != normalize_hex(queue.get("rootfieldId")):
        raise ValueError("artifact expectedPulse.rootfieldId must match queue rootfieldId")
    body = entry_body(queue, artifact)
    body["entryId"] = axiom_writ.digest(body)
    updated = copy.deepcopy(queue)
    updated.setdefault("entries", []).append(body)
    return updated


def select_flowpulse_record(evidence: dict[str, Any]) -> dict[str, Any] | None:
    records = evidence.get("records", [])
    if not isinstance(records, list):
        return None
    for record in records:
        if isinstance(record, dict) and record.get("eventName") == "FlowPulse":
            return record
    return None


def trigger_anchor(record: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifactType": "FlowPulse",
        "boundary": "uniswap_v4_afterSwap",
        "chainId": str(record.get("chainId") or evidence.get("chainId", "")),
        "hookAddress": normalize_hex(record.get("hookAddress") or evidence.get("hookAddress")),
        "txHash": normalize_hex(record.get("txHash")),
        "logIndex": None if record.get("logIndex") in (None, "") else str(record.get("logIndex")),
        "blockNumber": str(record.get("blockNumber", "")),
        "receiptStatus": record.get("receiptStatus"),
        "pulseId": normalize_hex(record.get("pulseId")),
        "rootfieldId": normalize_hex(record.get("rootfieldId")),
        "commitment": normalize_hex(record.get("commitment")),
        "subjectPoolId": normalize_hex(record.get("subjectPoolId")),
        "parentPulseId": normalize_hex(record.get("parentPulseId")),
    }


def causal_nonce(anchor: dict[str, Any]) -> str:
    return axiom_writ.digest(
        {
            "chainId": anchor.get("chainId"),
            "hookAddress": anchor.get("hookAddress"),
            "txHash": anchor.get("txHash"),
            "logIndex": anchor.get("logIndex"),
            "rootfieldId": anchor.get("rootfieldId"),
            "commitment": anchor.get("commitment"),
            "subjectPoolId": anchor.get("subjectPoolId"),
        }
    )


def compare_entry_to_anchor(entry: dict[str, Any], anchor: dict[str, Any], record: dict[str, Any] | None) -> tuple[dict[str, bool], list[str]]:
    expected = entry.get("expectedPulse") if isinstance(entry.get("expectedPulse"), dict) else {}
    checks = {
        "flowPulseRecordFound": record is not None,
        "readerAttachedTxHash": truthy_hex(anchor.get("txHash")),
        "readerAttachedLogIndex": anchor.get("logIndex") not in (None, ""),
        "receiptStatusSuccess": anchor.get("receiptStatus") == "success",
        "rootfieldMatches": normalize_hex(expected.get("rootfieldId")) == normalize_hex(anchor.get("rootfieldId")),
        "commitmentMatches": normalize_hex(expected.get("commitment")) == normalize_hex(anchor.get("commitment")),
        "hookAddressMatches": normalize_hex(expected.get("hookAddress")) == normalize_hex(anchor.get("hookAddress")),
        "subjectPoolMatches": normalize_hex(expected.get("subjectPoolId")) == normalize_hex(anchor.get("subjectPoolId")),
        "noReceiptFieldsAtEnqueue": not forbidden_paths(expected),
    }
    reasons = [key for key, ok in checks.items() if not ok]
    return checks, reasons


def build_retirement(
    queue: dict[str, Any],
    entry: dict[str, Any],
    anchor: dict[str, Any],
    checks: dict[str, bool],
    status: str,
    reasons: list[str],
) -> dict[str, Any]:
    body = {
        "schema": RETIREMENT_SCHEMA,
        "queueId": queue.get("queueId"),
        "entryId": entry.get("entryId"),
        "artifactId": entry.get("artifactId"),
        "status": status,
        "retiredBy": anchor if status == "retired" else None,
        "causalNonce": causal_nonce(anchor) if status == "retired" else None,
        "effects": entry.get("onRetire") if status == "retired" else entry.get("onSquash"),
        "squashReasons": reasons if status == "squashed" else [],
        "checks": checks,
    }
    body["retirementId"] = axiom_writ.digest(body)
    return body


def retire_queue(queue: dict[str, Any], evidence: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    record = select_flowpulse_record(evidence)
    anchor = trigger_anchor(record or {}, evidence)
    updated = copy.deepcopy(queue)
    retirements: list[dict[str, Any]] = []

    for entry in updated.get("entries", []):
        if not isinstance(entry, dict) or entry.get("artifactState") != "speculative":
            continue
        checks, reasons = compare_entry_to_anchor(entry, anchor, record)
        if not checks["flowPulseRecordFound"] or not checks["readerAttachedTxHash"] or not checks["readerAttachedLogIndex"]:
            if updated.get("retirementMode") == "in_order":
                break
            continue
        if all(checks.values()):
            entry["artifactState"] = "live"
            retirement = build_retirement(updated, entry, anchor, checks, "retired", [])
            entry["retirementId"] = retirement["retirementId"]
            entry["causalNonce"] = retirement["causalNonce"]
            retirements.append(retirement)
            continue
        entry["artifactState"] = "squashed"
        retirement = build_retirement(updated, entry, anchor, checks, "squashed", reasons)
        entry["retirementId"] = retirement["retirementId"]
        retirements.append(retirement)

    report = {
        "schema": "flowmemory.pulse_retirement_batch.v0",
        "queueId": queue.get("queueId"),
        "status": "retired" if retirements and all(item["status"] == "retired" for item in retirements) else "squashed"
        if retirements and any(item["status"] == "squashed" for item in retirements)
        else "immature",
        "retirements": retirements,
        "retiredCount": len([item for item in retirements if item["status"] == "retired"]),
        "squashedCount": len([item for item in retirements if item["status"] == "squashed"]),
        "speculativeCount": len([entry for entry in updated.get("entries", []) if entry.get("artifactState") == "speculative"]),
    }
    report["batchId"] = axiom_writ.digest(report)
    return updated, report


def verify_retirement(report: dict[str, Any]) -> dict[str, Any]:
    body = copy.deepcopy(report)
    batch_id = body.pop("batchId", None)
    retirement_checks = []
    for retirement in report.get("retirements", []):
        if not isinstance(retirement, dict):
            retirement_checks.append(False)
            continue
        item = copy.deepcopy(retirement)
        retirement_id = item.pop("retirementId", None)
        retirement_checks.append(axiom_writ.digest(item) == retirement_id)
    checks = {
        "batchIdMatches": axiom_writ.digest(body) == batch_id,
        "retirementIdsMatch": all(retirement_checks),
        "hasKnownStatus": report.get("status") in ["retired", "squashed", "immature"],
    }
    failed = [key for key, ok in checks.items() if not ok]
    return {
        "schema": "flowmemory.pulse_retirement_verification.v0",
        "status": "valid" if not failed else "invalid",
        "batchId": batch_id,
        "checks": checks,
        "failedChecks": failed,
    }


def enforce(queue: dict[str, Any], artifact_id: str) -> dict[str, Any]:
    for entry in queue.get("entries", []):
        if not isinstance(entry, dict) or entry.get("artifactId") != artifact_id:
            continue
        allowed = entry.get("artifactState") == "live"
        return {
            "schema": ENFORCEMENT_SCHEMA,
            "allowed": allowed,
            "reason": "artifact_retired_by_flowpulse" if allowed else "artifact_not_retired",
            "artifactId": artifact_id,
            "artifactState": entry.get("artifactState"),
            "causalNonce": entry.get("causalNonce") if allowed else None,
        }
    return {
        "schema": ENFORCEMENT_SCHEMA,
        "allowed": False,
        "reason": "artifact_not_bound_to_queue",
        "artifactId": artifact_id,
        "causalNonce": None,
    }


def example_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "examples" / "pulse-retire"


def demo_report() -> dict[str, Any]:
    base = example_dir()
    queue = read_json(base / "queue.initial.json")
    for name in ["speculative-model-output.json", "speculative-cache-reuse.json", "speculative-agent-action.json"]:
        queue = enqueue_artifact(queue, read_json(base / name))
    matching_queue, matching = retire_queue(queue, read_json(base / "flowpulse.matching.json"))
    _, mismatched = retire_queue(queue, read_json(base / "flowpulse.mismatched.json"))
    return {
        "schema": "flowmemory.pulse_retire_demo.v0",
        "queuedArtifacts": [entry.get("artifactId") for entry in queue.get("entries", [])],
        "beforeFlowPulse": {entry.get("artifactId"): entry.get("artifactState") for entry in queue.get("entries", [])},
        "matchingFlowPulse": matching,
        "afterMatching": {entry.get("artifactId"): entry.get("artifactState") for entry in matching_queue.get("entries", [])},
        "mismatchedFlowPulse": mismatched,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage PulseRetire speculative cognition queues.")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Initialize a PulseRetire queue.")
    init.add_argument("--agent-id", required=True)
    init.add_argument("--rootfield-id", required=True)
    init.add_argument("--out")
    init.add_argument("--pretty", action="store_true")

    enqueue = sub.add_parser("enqueue", help="Enqueue a speculative artifact.")
    enqueue.add_argument("--queue", required=True)
    enqueue.add_argument("--artifact", required=True)
    enqueue.add_argument("--out")
    enqueue.add_argument("--pretty", action="store_true")

    retire = sub.add_parser("retire", help="Retire or squash queued artifacts with FlowPulse evidence.")
    retire.add_argument("--queue", required=True)
    retire.add_argument("--flowpulse", required=True)
    retire.add_argument("--out")
    retire.add_argument("--queue-out")
    retire.add_argument("--pretty", action="store_true")

    verify = sub.add_parser("verify", help="Verify a PulseRetirement batch.")
    verify.add_argument("--retirement", required=True)
    verify.add_argument("--pretty", action="store_true")

    enforce_cmd = sub.add_parser("enforce", help="Check whether an artifact is live.")
    enforce_cmd.add_argument("--queue", required=True)
    enforce_cmd.add_argument("--artifact-id", required=True)
    enforce_cmd.add_argument("--pretty", action="store_true")

    demo = sub.add_parser("demo", help="Run the PulseRetire demo.")
    demo.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "init":
        write_json(create_queue(args.agent_id, args.rootfield_id), args.out, args.pretty)
        return 0
    if args.command == "enqueue":
        write_json(enqueue_artifact(read_json(args.queue), read_json(args.artifact)), args.out, args.pretty)
        return 0
    if args.command == "retire":
        queue, report = retire_queue(read_json(args.queue), read_json(args.flowpulse))
        if args.queue_out:
            write_json(queue, args.queue_out, args.pretty)
        write_json(report, args.out, args.pretty)
        return 0 if report["status"] == "retired" else 2
    if args.command == "verify":
        verification = verify_retirement(read_json(args.retirement))
        write_json(verification, None, args.pretty)
        return 0 if verification["status"] == "valid" else 2
    if args.command == "enforce":
        verdict = enforce(read_json(args.queue), args.artifact_id)
        write_json(verdict, None, args.pretty)
        return 0 if verdict["allowed"] else 2
    if args.command == "demo":
        write_json(demo_report(), None, args.pretty)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
