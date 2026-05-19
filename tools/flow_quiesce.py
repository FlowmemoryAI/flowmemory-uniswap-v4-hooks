#!/usr/bin/env python3
"""
FlowQuiesce: receipt-triggered quiescence epochs for agent runtimes.

A receipt-bound FlowPulse advances an external reality epoch. Active frames that
read the old rootfield must reach a safe point before their outputs can join the
post-boundary state.
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


EPOCH_SCHEMA = "flowmemory.receipt_epoch.v0"
REQUEST_SCHEMA = "flowmemory.quiescence_request.v0"
ACK_SCHEMA = "flowmemory.quiescence_ack.v0"
CERT_SCHEMA = "flowmemory.quiescence_certificate.v0"
ZERO32 = "0x" + ("0" * 64)
ACK_MODES = ["revalidated", "forked", "abandoned", "readonly_internal"]


def read_json(path: str | Path) -> dict[str, Any]:
    return axiom_writ.read_json(path)


def write_json(payload: Any, output: str | None, pretty: bool) -> None:
    axiom_writ.write_json(payload, output, pretty)


def normalize_hex(value: Any) -> str:
    return axiom_writ.normalize_hex(value)


def truthy_hex(value: Any) -> bool:
    return axiom_writ.truthy_hex(value)


def select_flowpulse_record(evidence: dict[str, Any]) -> dict[str, Any] | None:
    records = evidence.get("records", [])
    if not isinstance(records, list):
        return None
    for record in records:
        if isinstance(record, dict) and record.get("eventName") == "FlowPulse":
            return record
    return None


def trigger(record: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifactType": "FlowPulse",
        "boundary": "uniswap_v4_afterSwap",
        "chainId": str(record.get("chainId") or evidence.get("chainId", "")),
        "hookAddress": normalize_hex(record.get("hookAddress") or evidence.get("hookAddress")),
        "txHash": normalize_hex(record.get("txHash")),
        "logIndex": None if record.get("logIndex") in (None, "") else str(record.get("logIndex")),
        "transactionIndex": None if record.get("transactionIndex") in (None, "") else str(record.get("transactionIndex")),
        "blockNumber": None if record.get("blockNumber") in (None, "") else str(record.get("blockNumber")),
        "blockHash": normalize_hex(record.get("blockHash")),
        "receiptStatus": record.get("receiptStatus"),
        "pulseId": normalize_hex(record.get("pulseId")),
        "rootfieldId": normalize_hex(record.get("rootfieldId")),
        "commitment": normalize_hex(record.get("commitment")),
        "subjectPoolId": normalize_hex(record.get("subjectPoolId")),
        "parentPulseId": normalize_hex(record.get("parentPulseId")),
    }


def epoch_checks(anchor: dict[str, Any], record: dict[str, Any] | None) -> dict[str, bool]:
    return {
        "flowPulseRecordFound": record is not None,
        "readerAttachedTxHash": truthy_hex(anchor.get("txHash")),
        "readerAttachedLogIndex": anchor.get("logIndex") not in (None, ""),
        "receiptStatusSuccess": anchor.get("receiptStatus") == "success",
        "nonzeroRootfieldId": normalize_hex(anchor.get("rootfieldId")) != ZERO32,
        "nonzeroCommitment": normalize_hex(anchor.get("commitment")) != ZERO32,
    }


def advance_epoch(evidence: dict[str, Any], previous_epoch: dict[str, Any] | None = None) -> dict[str, Any]:
    record = select_flowpulse_record(evidence)
    anchor = trigger(record or {}, evidence)
    checks = epoch_checks(anchor, record)
    if not all(checks.values()):
        raise ValueError("FlowPulse receipt evidence is not sufficient to advance epoch")
    previous_id = previous_epoch.get("epochId") if isinstance(previous_epoch, dict) else None
    previous_number = int(previous_epoch.get("epochNumber", -1)) if isinstance(previous_epoch, dict) else -1
    body = {
        "schema": EPOCH_SCHEMA,
        "epochType": "flowpulse_receipt_epoch",
        "epochNumber": previous_number + 1,
        "previousEpochId": previous_id,
        "rootfieldId": anchor.get("rootfieldId"),
        "trigger": anchor,
        "checks": {**checks, "epochIdMatches": True},
        "notClaims": [
            "not_semantic_truth",
            "not_swap_control",
            "not_custody",
            "not_fund_protection",
            "not_model_correctness",
            "not_gpu_attestation",
            "not_hardware_acceleration",
        ],
    }
    epoch_id = axiom_writ.digest(body)
    body["epochId"] = epoch_id
    body["checks"]["epochIdMatches"] = True
    return body


def frame_outputs(frame: dict[str, Any]) -> list[str]:
    outputs = frame.get("pendingOutputs", [])
    if not isinstance(outputs, list):
        return []
    return [str(item.get("outputId")) for item in outputs if isinstance(item, dict) and item.get("outputId")]


def scan_frames(epoch: dict[str, Any], frames_doc: dict[str, Any]) -> dict[str, Any]:
    rootfield = normalize_hex(epoch.get("rootfieldId"))
    required: list[dict[str, Any]] = []
    unaffected: list[dict[str, Any]] = []
    blocked_outputs: list[str] = []
    frames = frames_doc.get("frames", [])
    if not isinstance(frames, list):
        frames = []
    for frame in frames:
        if not isinstance(frame, dict):
            continue
        reads = [normalize_hex(item) for item in frame.get("rootfieldReads", [])]
        if frame.get("state") == "active" and rootfield in reads:
            outputs = frame_outputs(frame)
            required.append(
                {
                    "frameId": frame.get("frameId"),
                    "reason": "active_pre_boundary_reader_for_rootfield",
                    "requiredSafePoint": "quiesce | revalidate | fork | abandon",
                    "pendingOutputs": outputs,
                }
            )
            blocked_outputs.extend(outputs)
        else:
            unaffected.append({"frameId": frame.get("frameId"), "reason": "different_rootfield_or_already_quiescent"})
    body = {
        "schema": REQUEST_SCHEMA,
        "epochId": epoch.get("epochId"),
        "rootfieldId": rootfield,
        "requiredFrames": required,
        "unaffectedFrames": unaffected,
        "blockedJoinUntilQuiescent": blocked_outputs,
    }
    body["requestId"] = axiom_writ.digest(body)
    return body


def ack_frame(request: dict[str, Any], frame_id: str, mode: str) -> dict[str, Any]:
    if mode not in ACK_MODES:
        raise ValueError(f"ack mode must be one of: {', '.join(ACK_MODES)}")
    required = request.get("requiredFrames", [])
    match = next((item for item in required if isinstance(item, dict) and item.get("frameId") == frame_id), None)
    if not match:
        raise ValueError("frame is not required for this quiescence request")
    disposition = {output_id: f"{mode}_for_epoch" for output_id in match.get("pendingOutputs", [])}
    body = {
        "schema": ACK_SCHEMA,
        "requestId": request.get("requestId"),
        "epochId": request.get("epochId"),
        "frameId": frame_id,
        "ackMode": mode,
        "frameStateAfter": "quiescent",
        "outputDisposition": disposition,
        "checks": {"frameWasRequired": True, "epochMatches": True, "ackIdMatches": True},
    }
    body["ackId"] = axiom_writ.digest(body)
    body["checks"]["ackIdMatches"] = True
    return body


def verify_ack(ack: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    body = copy.deepcopy(ack)
    ack_id = body.pop("ackId", None)
    required_ids = {item.get("frameId") for item in request.get("requiredFrames", []) if isinstance(item, dict)}
    checks = {
        "schemaMatches": ack.get("schema") == ACK_SCHEMA,
        "ackIdMatches": axiom_writ.digest(body) == ack_id,
        "frameWasRequired": ack.get("frameId") in required_ids,
        "epochMatches": ack.get("epochId") == request.get("epochId"),
        "requestMatches": ack.get("requestId") == request.get("requestId"),
    }
    failed = [key for key, ok in checks.items() if not ok]
    return {"schema": "flowmemory.quiescence_ack_verification.v0", "status": "valid" if not failed else "invalid", "ackId": ack_id, "checks": checks, "failedChecks": failed}


def certify(request: dict[str, Any], acks: list[dict[str, Any]]) -> dict[str, Any]:
    valid_acks = [ack for ack in acks if verify_ack(ack, request)["status"] == "valid"]
    acked = {ack.get("frameId") for ack in valid_acks}
    required = [item for item in request.get("requiredFrames", []) if isinstance(item, dict)]
    blocked = [item.get("frameId") for item in required if item.get("frameId") not in acked]
    safe_outputs: list[str] = []
    for ack in valid_acks:
        safe_outputs.extend(list((ack.get("outputDisposition") or {}).keys()))
    unsafe = list(request.get("blockedJoinUntilQuiescent", []))
    if not blocked:
        unsafe = [item for item in unsafe if item not in set(safe_outputs)]
    body = {
        "schema": CERT_SCHEMA,
        "epochId": request.get("epochId"),
        "requestId": request.get("requestId"),
        "status": "grace_period_closed" if not blocked else "grace_period_open",
        "requiredFrameCount": len(required),
        "ackedFrameCount": len(valid_acks),
        "blockedFrames": blocked,
        "safeToJoinPostBoundaryState": not blocked,
        "safeOutputs": safe_outputs if not blocked else [],
        "unsafeOutputs": unsafe,
        "checks": {
            "allRequiredFramesAcked": not blocked,
            "noActivePreBoundaryReaders": not blocked,
            "certificateIdMatches": True,
        },
    }
    body["certificateId"] = axiom_writ.digest(body)
    body["checks"]["certificateIdMatches"] = True
    return body


def example_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "examples" / "flow-quiesce"


def demo() -> dict[str, Any]:
    base = example_dir()
    epoch = advance_epoch(read_json(base / "flowpulse.matching.json"), read_json(base / "epoch.0.json"))
    request = scan_frames(epoch, read_json(base / "agent-frames.active.json"))
    open_cert = certify(request, [])
    ack = ack_frame(request, "frame-001", "revalidated")
    closed = certify(request, [ack])
    return {"schema": "flowmemory.flow_quiesce_demo.v0", "epoch": epoch, "request": request, "beforeAck": open_cert, "ack": ack, "afterAck": closed}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FlowQuiesce receipt-triggered quiescence utility.")
    sub = parser.add_subparsers(dest="command", required=True)
    adv = sub.add_parser("advance")
    adv.add_argument("--flowpulse", required=True)
    adv.add_argument("--previous-epoch")
    adv.add_argument("--out")
    adv.add_argument("--pretty", action="store_true")
    scan = sub.add_parser("scan")
    scan.add_argument("--epoch", required=True)
    scan.add_argument("--frames", required=True)
    scan.add_argument("--out")
    scan.add_argument("--pretty", action="store_true")
    ack = sub.add_parser("ack")
    ack.add_argument("--request", required=True)
    ack.add_argument("--frame-id", required=True)
    ack.add_argument("--mode", required=True)
    ack.add_argument("--out")
    ack.add_argument("--pretty", action="store_true")
    cert = sub.add_parser("certify")
    cert.add_argument("--request", required=True)
    cert.add_argument("--acks", nargs="*")
    cert.add_argument("--out")
    cert.add_argument("--pretty", action="store_true")
    demo_cmd = sub.add_parser("demo")
    demo_cmd.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "advance":
            previous = read_json(args.previous_epoch) if args.previous_epoch else None
            write_json(advance_epoch(read_json(args.flowpulse), previous), args.out, args.pretty)
            return 0
        if args.command == "scan":
            write_json(scan_frames(read_json(args.epoch), read_json(args.frames)), args.out, args.pretty)
            return 0
        if args.command == "ack":
            write_json(ack_frame(read_json(args.request), args.frame_id, args.mode), args.out, args.pretty)
            return 0
        if args.command == "certify":
            acks = [read_json(path) for path in (args.acks or [])]
            write_json(certify(read_json(args.request), acks), args.out, args.pretty)
            return 0
        if args.command == "demo":
            write_json(demo(), None, args.pretty)
            return 0
    except ValueError as error:
        write_json({"schema": "flowmemory.flow_quiesce_error.v0", "error": str(error)}, None, True)
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
