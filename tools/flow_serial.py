#!/usr/bin/env python3
"""
FlowSerial: receipt-linearizability for machine cognition.

FlowSerial compiles agent events, tool calls, model outputs, and state writes
into a serial history around receipt-bound FlowPulse boundaries. If the history
cannot be serialized, it emits a typed impossibility fault.
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore


BOUNDARY_SCHEMA = "flowmemory.receipt_boundary.v0"
EVENT_SCHEMA = "flowmemory.machine_event.v0"
HISTORY_SCHEMA = "flowmemory.flow_serial_history.v0"
CERT_SCHEMA = "flowmemory.flow_serial_certificate.v0"
FAULT_SCHEMA = "flowmemory.flow_serial_fault.v0"
VERIFY_SCHEMA = "flowmemory.flow_serial_certificate_verification.v0"
ZERO32 = "0x" + ("0" * 64)
RECEIPT_ONLY_FIELDS = {"txHash", "transactionIndex", "logIndex", "blockHash", "blockNumber", "receiptStatus"}
ROOTFIELD_HEAD_KEYS = {"rootfieldHead", "rootfield_head"}


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def write_json(payload: Any, output: str | None, pretty: bool) -> None:
    axiom_writ.write_json(payload, output, pretty)


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def normalize_hex(value: Any) -> str:
    return axiom_writ.normalize_hex(value)


def truthy_hex(value: Any) -> bool:
    return axiom_writ.truthy_hex(value)


def as_int(value: Any, default: int = -1) -> int:
    if value in (None, ""):
        return default
    return int(value)


def boundary_order_key(boundary: dict[str, Any]) -> list[Any]:
    return [
        str(boundary.get("chainId", "")),
        as_int(boundary.get("blockNumber")),
        as_int(boundary.get("transactionIndex")),
        as_int(boundary.get("logIndex")),
    ]


def boundary_id_body(boundary: dict[str, Any]) -> dict[str, Any]:
    body = copy.deepcopy(boundary)
    body.pop("boundaryId", None)
    body.pop("checks", None)
    return body


def ensure_boundary_id(boundary: dict[str, Any]) -> dict[str, Any]:
    body = copy.deepcopy(boundary)
    if not body.get("boundaryId"):
        body["boundaryId"] = digest(boundary_id_body(body))
    if not body.get("receiptOrderKey"):
        body["receiptOrderKey"] = boundary_order_key(body)
    return body


def boundary_checks(boundary: dict[str, Any]) -> dict[str, bool]:
    return {
        "schemaMatches": boundary.get("schema") == BOUNDARY_SCHEMA,
        "artifactTypeFlowPulse": boundary.get("artifactType") == "FlowPulse",
        "afterSwapBoundary": boundary.get("boundary") == "uniswap_v4_afterSwap",
        "readerAttachedTxHash": truthy_hex(boundary.get("txHash")),
        "readerAttachedLogIndex": boundary.get("logIndex") not in (None, ""),
        "receiptStatusSuccess": boundary.get("receiptStatus") == "success",
        "nonzeroRootfieldId": normalize_hex(boundary.get("rootfieldId")) != ZERO32,
        "nonzeroCommitment": normalize_hex(boundary.get("commitment")) != ZERO32,
        "declaredOrderPresent": boundary.get("declaredOrder") not in (None, ""),
    }


def fault(
    fault_type: str,
    history_id: str | None,
    reason: str,
    event_id: str | None = None,
    boundary_id: str | None = None,
    repair_hints: list[str] | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = {
        "schema": FAULT_SCHEMA,
        "faultType": fault_type,
        "historyId": history_id,
        "eventId": event_id,
        "boundaryId": boundary_id,
        "reason": reason,
        "repairHints": repair_hints
        or [
            "move the event after the receipt boundary",
            "remove receipt-only claims from pre-boundary output",
            "mark the output as a pre-boundary draft",
            "recompute from post-boundary context",
        ],
        "details": details or {},
        "notClaims": non_claims(),
    }
    body["faultId"] = digest(body)
    return body


def non_claims() -> list[str]:
    return [
        "not_semantic_truth",
        "not_model_correctness",
        "not_gpu_attestation",
        "not_hardware_acceleration",
        "not_swap_control",
        "not_custody",
        "not_fund_protection",
        "not_live_mainnet_claim",
        "not_consensus_replacement",
        "not_workflow_engine_replacement",
    ]


def validate_boundaries(history: dict[str, Any]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    normalized: list[dict[str, Any]] = []
    history_id = history.get("historyId")
    for raw in history.get("boundaries", []):
        if not isinstance(raw, dict):
            return fault("missing_receipt_metadata", history_id, "boundary entry is not a JSON object"), []
        boundary = ensure_boundary_id(raw)
        checks = boundary_checks(boundary)
        boundary["checks"] = {**checks, "boundaryIdMatches": True}
        if not checks["schemaMatches"] or not checks["artifactTypeFlowPulse"] or not checks["afterSwapBoundary"]:
            return fault(
                "failed_receipt_boundary",
                history_id,
                "only receipt-attached FlowPulse events from the Uniswap v4 afterSwap boundary can anchor FlowSerial",
                boundary_id=boundary.get("boundaryId"),
                details={"checks": checks},
            ), []
        if not checks["receiptStatusSuccess"]:
            return fault(
                "failed_receipt_boundary",
                history_id,
                "receipt boundary is not a successful FlowPulse receipt",
                boundary_id=boundary.get("boundaryId"),
                details={"checks": checks},
            ), []
        missing_receipt = [
            key
            for key in ["readerAttachedTxHash", "readerAttachedLogIndex", "nonzeroRootfieldId", "nonzeroCommitment", "declaredOrderPresent"]
            if not checks[key]
        ]
        if missing_receipt:
            return fault(
                "missing_receipt_metadata",
                history_id,
                "receipt boundary is missing reader-attached ordering metadata",
                boundary_id=boundary.get("boundaryId"),
                details={"checks": checks, "missing": missing_receipt},
            ), []
        normalized.append(boundary)
    return None, normalized


def boundary_index(boundaries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(boundary.get("boundaryId")): boundary for boundary in boundaries}


def boundary_rank(boundaries: list[dict[str, Any]]) -> dict[str, int]:
    ordered = sorted(boundaries, key=lambda item: tuple(item.get("receiptOrderKey") or boundary_order_key(item)))
    return {str(boundary.get("boundaryId")): index for index, boundary in enumerate(ordered)}


def declared_order(item: dict[str, Any]) -> int:
    return as_int(item.get("declaredOrder"))


def event_boundary_sets(event: dict[str, Any]) -> tuple[set[str], set[str]]:
    return set(str(item) for item in event.get("mustPrecede", []) if item), set(str(item) for item in event.get("mustFollow", []) if item)


def event_before_boundary(event: dict[str, Any], boundary: dict[str, Any]) -> bool:
    boundary_id = str(boundary.get("boundaryId"))
    must_precede, must_follow = event_boundary_sets(event)
    if boundary_id in must_follow:
        return False
    if boundary_id in must_precede:
        return True
    return declared_order(event) < declared_order(boundary)


def validate_order_constraints(history: dict[str, Any], boundaries: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    history_id = history.get("historyId")
    for event in history.get("events", []):
        if not isinstance(event, dict):
            return fault("impossible_schedule", history_id, "event entry is not a JSON object")
        must_precede, must_follow = event_boundary_sets(event)
        overlap = sorted(must_precede.intersection(must_follow))
        if overlap:
            return fault(
                "impossible_schedule",
                history_id,
                "event requires the same FlowPulse boundary to be both before and after it",
                event_id=event.get("eventId"),
                boundary_id=overlap[0],
                details={"contradictoryBoundaries": overlap},
            )
        for boundary_id in sorted(must_precede.union(must_follow)):
            boundary = boundaries.get(boundary_id)
            if boundary is None:
                return fault(
                    "impossible_schedule",
                    history_id,
                    "event references a boundary that is not in the history",
                    event_id=event.get("eventId"),
                    boundary_id=boundary_id,
                )
            if boundary_id in must_precede and declared_order(event) >= declared_order(boundary):
                return fault(
                    "impossible_schedule",
                    history_id,
                    "event declared order violates mustPrecede boundary constraint",
                    event_id=event.get("eventId"),
                    boundary_id=boundary_id,
                )
            if boundary_id in must_follow and declared_order(event) <= declared_order(boundary):
                return fault(
                    "impossible_schedule",
                    history_id,
                    "event declared order violates mustFollow boundary constraint",
                    event_id=event.get("eventId"),
                    boundary_id=boundary_id,
                )
    return None


def validate_receipt_claims(history: dict[str, Any], boundaries: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    history_id = history.get("historyId")
    for event in history.get("events", []):
        claims = event.get("claimedReceiptFacts", [])
        if not isinstance(claims, list):
            continue
        for claim in claims:
            if not isinstance(claim, dict):
                continue
            field = str(claim.get("field", ""))
            boundary_id = str(claim.get("boundaryId", ""))
            if field not in RECEIPT_ONLY_FIELDS:
                continue
            boundary = boundaries.get(boundary_id)
            if boundary is None:
                return fault(
                    "impossible_schedule",
                    history_id,
                    "event claims a receipt fact for a boundary that is not in the history",
                    event_id=event.get("eventId"),
                    boundary_id=boundary_id,
                )
            if event_before_boundary(event, boundary):
                return fault(
                    "retrocausal_receipt_claim",
                    history_id,
                    f"event claims {field} for a FlowPulse receipt boundary before that receipt boundary is available",
                    event_id=event.get("eventId"),
                    boundary_id=boundary_id,
                    details={"claimedField": field},
                )
    return None


def head_rank(head: Any, ranks: dict[str, int]) -> int:
    if head in (None, "", "none", "null", ZERO32):
        return -1
    return ranks.get(str(head), -1)


def validate_rootfield_heads(history: dict[str, Any], boundaries: dict[str, dict[str, Any]], ranks: dict[str, int]) -> dict[str, Any] | None:
    heads: dict[str, str | None] = {}
    history_id = history.get("historyId")
    for event in sorted(history.get("events", []), key=declared_order):
        rootfield = normalize_hex(event.get("rootfieldId") or history.get("rootfieldId"))
        writes = event.get("writes", [])
        if not isinstance(writes, list):
            continue
        for write in writes:
            if not isinstance(write, dict) or str(write.get("key")) not in ROOTFIELD_HEAD_KEYS:
                continue
            value = write.get("value")
            previous = heads.get(rootfield)
            if value in (None, "", "none", "null", ZERO32):
                if previous not in (None, "", "none", "null", ZERO32):
                    return fault(
                        "rootfield_rollback",
                        history_id,
                        "later event clears a rootfield head after a receipt-bound FlowPulse already advanced it",
                        event_id=event.get("eventId"),
                        boundary_id=previous,
                        details={"rootfieldId": rootfield, "previousHead": previous, "attemptedHead": value},
                    )
                heads[rootfield] = None
                continue
            boundary_id = str(value)
            if boundary_id not in boundaries:
                return fault(
                    "rootfield_rollback",
                    history_id,
                    "event writes a rootfield head that is not a receipt boundary in this history",
                    event_id=event.get("eventId"),
                    boundary_id=boundary_id,
                    details={"rootfieldId": rootfield},
                )
            if head_rank(previous, ranks) > head_rank(boundary_id, ranks):
                return fault(
                    "rootfield_rollback",
                    history_id,
                    "later event moves rootfield head behind an already observed FlowPulse boundary",
                    event_id=event.get("eventId"),
                    boundary_id=boundary_id,
                    details={"rootfieldId": rootfield, "previousHead": previous, "attemptedHead": boundary_id},
                )
            heads[rootfield] = boundary_id
    return None


def latest_observed_head(event: dict[str, Any], ranks: dict[str, int]) -> str | None:
    observed = [str(item) for item in event.get("observedBoundaries", []) if item]
    if not observed:
        return None
    return max(observed, key=lambda item: ranks.get(item, -1))


def validate_exclusive_writes(history: dict[str, Any], ranks: dict[str, int]) -> dict[str, Any] | None:
    seen: dict[str, dict[str, Any]] = {}
    history_id = history.get("historyId")
    for event in sorted(history.get("events", []), key=declared_order):
        key = event.get("exclusiveWriteKey")
        if not key:
            continue
        key = str(key)
        head = latest_observed_head(event, ranks)
        previous = seen.get(key)
        if previous and previous.get("head") != head:
            return fault(
                "split_brain_write",
                history_id,
                "two events claim the same exclusive machine-state write under incompatible FlowPulse heads",
                event_id=event.get("eventId"),
                boundary_id=head,
                details={
                    "exclusiveWriteKey": key,
                    "previousEventId": previous.get("eventId"),
                    "previousHead": previous.get("head"),
                    "attemptedHead": head,
                },
            )
        seen[key] = {"eventId": event.get("eventId"), "head": head}
    return None


def serial_schedule(history: dict[str, Any], boundaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for boundary in boundaries:
        entries.append({"kind": "receipt_boundary", "id": boundary.get("boundaryId"), "declaredOrder": declared_order(boundary)})
    for event in history.get("events", []):
        entries.append({"kind": "machine_event", "id": event.get("eventId"), "declaredOrder": declared_order(event)})
    return [{key: value for key, value in item.items() if key != "declaredOrder"} for item in sorted(entries, key=lambda item: (item["declaredOrder"], item["kind"]))]


def rootfield_heads(history: dict[str, Any], ranks: dict[str, int]) -> dict[str, str]:
    heads: dict[str, str] = {}
    for event in sorted(history.get("events", []), key=declared_order):
        rootfield = normalize_hex(event.get("rootfieldId") or history.get("rootfieldId"))
        head = latest_observed_head(event, ranks)
        if head and (not heads.get(rootfield) or head_rank(head, ranks) >= head_rank(heads[rootfield], ranks)):
            heads[rootfield] = head
    return heads


def certificate(history: dict[str, Any], boundaries: list[dict[str, Any]], ranks: dict[str, int]) -> dict[str, Any]:
    body = {
        "schema": CERT_SCHEMA,
        "historyId": history.get("historyId"),
        "agentId": history.get("agentId"),
        "rootfieldId": normalize_hex(history.get("rootfieldId")),
        "status": "serializable",
        "category": "receipt_linearizable_machine_history",
        "serialSchedule": serial_schedule(history, boundaries),
        "rootfieldHeads": rootfield_heads(history, ranks),
        "checks": {
            "allReceiptBoundariesHaveTxHash": True,
            "allReceiptBoundariesHaveLogIndex": True,
            "allReceiptStatusesSuccessful": True,
            "noRetrocausalReceiptClaims": True,
            "noRootfieldRollback": True,
            "noSplitBrainExclusiveWrites": True,
            "certificateIdMatches": True,
        },
        "faults": [],
        "notClaims": non_claims(),
    }
    body["certificateId"] = digest(body)
    body["checks"]["certificateIdMatches"] = True
    return body


def certify(history: dict[str, Any]) -> dict[str, Any]:
    fail, boundaries = validate_boundaries(history)
    if fail:
        return fail
    by_id = boundary_index(boundaries)
    ranks = boundary_rank(boundaries)
    for check in [
        validate_order_constraints(history, by_id),
        validate_receipt_claims(history, by_id),
        validate_rootfield_heads(history, by_id, ranks),
        validate_exclusive_writes(history, ranks),
    ]:
        if check:
            return check
    return certificate(history, boundaries, ranks)


def verify_certificate(certificate_doc: dict[str, Any]) -> dict[str, Any]:
    body = copy.deepcopy(certificate_doc)
    certificate_id = body.pop("certificateId", None)
    checks = {
        "schemaMatches": certificate_doc.get("schema") == CERT_SCHEMA,
        "statusSerializable": certificate_doc.get("status") == "serializable",
        "certificateIdMatches": digest(body) == certificate_id,
        "nonClaimsPresent": set(non_claims()).issubset(set(certificate_doc.get("notClaims", []))),
    }
    failed = [key for key, ok in checks.items() if not ok]
    return {
        "schema": VERIFY_SCHEMA,
        "status": "valid" if not failed else "invalid",
        "certificateId": certificate_id,
        "checks": checks,
        "failedChecks": failed,
    }


def example_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "examples" / "flow-serial"


def demo() -> dict[str, Any]:
    base = example_dir()
    return {
        "schema": "flowmemory.flow_serial_demo.v0",
        "valid": certify(read_json(base / "history.valid.json")),
        "retrocausal": certify(read_json(base / "history.retrocausal.json")),
        "rollback": certify(read_json(base / "history.rollback.json")),
        "splitBrain": certify(read_json(base / "history.split-brain.json")),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FlowSerial receipt-linearizability utility.")
    sub = parser.add_subparsers(dest="command", required=True)
    cert = sub.add_parser("certify")
    cert.add_argument("--history", required=True)
    cert.add_argument("--out")
    cert.add_argument("--pretty", action="store_true")
    verify = sub.add_parser("verify-certificate")
    verify.add_argument("--certificate", required=True)
    verify.add_argument("--out")
    verify.add_argument("--pretty", action="store_true")
    demo_cmd = sub.add_parser("demo")
    demo_cmd.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "certify":
            write_json(certify(read_json(args.history)), args.out, args.pretty)
            return 0
        if args.command == "verify-certificate":
            result = verify_certificate(read_json(args.certificate))
            write_json(result, args.out, args.pretty)
            return 0 if result["status"] == "valid" else 2
        if args.command == "demo":
            write_json(demo(), None, args.pretty)
            return 0
    except ValueError as error:
        write_json({"schema": "flowmemory.flow_serial_error.v0", "error": str(error)}, None, True)
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
