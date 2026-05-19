#!/usr/bin/env python3
"""
FlowMMU: receipt-backed virtual memory for machine reality.

Agents can hold virtual FlowPulse pointers before receipt metadata exists. They
cannot dereference receipt-only fields until reader-attached evidence maps the
pointer into a read-only receipt page.
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


TABLE_SCHEMA = "flowmemory.pulse_page_table.v0"
POINTER_SCHEMA = "flowmemory.pulse_pointer.v0"
PAGE_SCHEMA = "flowmemory.receipt_page.v0"
FAULT_SCHEMA = "flowmemory.receipt_page_fault.v0"
READ_SCHEMA = "flowmemory.flow_mmu_read.v0"
FORBIDDEN_RECEIPT_FIELDS = ["txHash", "logIndex", "transactionIndex", "blockHash", "receiptStatus"]
VIRTUAL_FIELDS = ["rootfieldId", "commitment", "hookAddress", "subjectPoolId", "parentPulseId", "boundary"]
PAGE_FIELDS = [
    "txHash",
    "logIndex",
    "transactionIndex",
    "blockHash",
    "blockNumber",
    "receiptStatus",
    "rootfieldId",
    "commitment",
    "hookAddress",
    "subjectPoolId",
    "parentPulseId",
    "chainId",
]


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


def table_identity(agent_id: str, rootfield_id: str) -> dict[str, Any]:
    return {
        "schema": TABLE_SCHEMA,
        "agentId": agent_id,
        "rootfieldId": normalize_hex(rootfield_id),
        "tableType": "receipt_backed_flowpulse_page_table",
    }


def init_table(agent_id: str, rootfield_id: str) -> dict[str, Any]:
    identity = table_identity(agent_id, rootfield_id)
    return {**identity, "tableId": axiom_writ.digest(identity), "entries": [], "faults": []}


def pointer_body(request: dict[str, Any]) -> dict[str, Any]:
    virtual = request.get("virtualAddress") if isinstance(request.get("virtualAddress"), dict) else {}
    return {
        "schema": POINTER_SCHEMA,
        "pointerType": "virtual_flowpulse_address",
        "state": "unmapped",
        "agentId": request.get("agentId"),
        "virtualAddress": {
            "boundary": virtual.get("boundary", "uniswap_v4_afterSwap"),
            "rootfieldId": normalize_hex(virtual.get("rootfieldId")),
            "commitment": normalize_hex(virtual.get("commitment")),
            "hookAddress": normalize_hex(virtual.get("hookAddress")),
            "subjectPoolId": normalize_hex(virtual.get("subjectPoolId")),
            "parentPulseId": normalize_hex(virtual.get("parentPulseId")),
        },
        "forbiddenAtAllocation": FORBIDDEN_RECEIPT_FIELDS,
        "allowedReadsBeforeMapping": VIRTUAL_FIELDS,
        "forbiddenReadsBeforeMapping": FORBIDDEN_RECEIPT_FIELDS,
        "notClaims": [
            "not_receipt_bound_yet",
            "not_semantic_truth",
            "not_swap_control",
            "not_custody",
            "not_gpu_attestation",
        ],
    }


def alloc_pointer(table: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    paths = forbidden_paths(request)
    if paths:
        raise ValueError(f"pulse pointer contains receipt-only fields: {', '.join(paths)}")
    body = pointer_body(request)
    if normalize_hex(body["virtualAddress"]["rootfieldId"]) != normalize_hex(table.get("rootfieldId")):
        raise ValueError("pointer rootfieldId must match page table rootfieldId")
    body["pointerId"] = axiom_writ.digest(body)
    updated = copy.deepcopy(table)
    updated.setdefault("entries", []).append({"pointerId": body["pointerId"], "state": "unmapped", "pageId": None, "pointer": body})
    return updated


def select_flowpulse_record(evidence: dict[str, Any]) -> dict[str, Any] | None:
    records = evidence.get("records", [])
    if not isinstance(records, list):
        return None
    for record in records:
        if isinstance(record, dict) and record.get("eventName") == "FlowPulse":
            return record
    return None


def physical_address(record: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
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


def make_fault(pointer_id: str | None, operation: str, field: str, fault_type: str, reason: str) -> dict[str, Any]:
    body = {
        "schema": FAULT_SCHEMA,
        "faultType": fault_type,
        "pointerId": pointer_id,
        "attemptedAccess": {"operation": operation, "field": field},
        "reason": reason,
        "requiredResolution": [
            "provide FlowPulse evidence",
            "require reader-attached txHash",
            "require reader-attached logIndex",
            "require matching rootfieldId",
            "require matching commitment",
        ],
        "handlerHint": "map_with_flowpulse_receipt_or_treat_as_unresolved_external_fact",
    }
    body["faultId"] = axiom_writ.digest(body)
    return body


def find_entry(table: dict[str, Any], pointer_id: str) -> dict[str, Any] | None:
    for entry in table.get("entries", []):
        if isinstance(entry, dict) and entry.get("pointerId") == pointer_id:
            return entry
    return None


def compare_pointer(pointer: dict[str, Any], address: dict[str, Any], record: dict[str, Any] | None) -> tuple[dict[str, bool], list[str]]:
    virtual = pointer.get("virtualAddress") if isinstance(pointer.get("virtualAddress"), dict) else {}
    checks = {
        "flowPulseRecordFound": record is not None,
        "readerAttachedTxHash": truthy_hex(address.get("txHash")),
        "readerAttachedLogIndex": address.get("logIndex") not in (None, ""),
        "receiptStatusSuccess": address.get("receiptStatus") == "success",
        "rootfieldMatches": normalize_hex(virtual.get("rootfieldId")) == normalize_hex(address.get("rootfieldId")),
        "commitmentMatches": normalize_hex(virtual.get("commitment")) == normalize_hex(address.get("commitment")),
        "hookAddressMatches": normalize_hex(virtual.get("hookAddress")) == normalize_hex(address.get("hookAddress")),
        "subjectPoolMatches": normalize_hex(virtual.get("subjectPoolId")) == normalize_hex(address.get("subjectPoolId")),
    }
    return checks, [key for key, ok in checks.items() if not ok]


def build_page(pointer: dict[str, Any], address: dict[str, Any], checks: dict[str, bool]) -> dict[str, Any]:
    body = {
        "schema": PAGE_SCHEMA,
        "pointerId": pointer.get("pointerId"),
        "state": "mapped",
        "pageType": "read_only_flowpulse_receipt_page",
        "mappedBy": {"mapper": "reader_verifier", "source": "flowpulse_evidence"},
        "physicalAddress": address,
        "readOnly": True,
        "allowedReadsAfterMapping": PAGE_FIELDS,
        "causalAddress": axiom_writ.digest(
            {
                "chainId": address.get("chainId"),
                "hookAddress": address.get("hookAddress"),
                "txHash": address.get("txHash"),
                "logIndex": address.get("logIndex"),
                "rootfieldId": address.get("rootfieldId"),
                "commitment": address.get("commitment"),
                "subjectPoolId": address.get("subjectPoolId"),
            }
        ),
        "checks": {**checks, "pageIdMatches": True},
    }
    page_id = axiom_writ.digest(body)
    body["pageId"] = page_id
    body["checks"]["pageIdMatches"] = True
    return body


def map_pointer(table: dict[str, Any], evidence: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    record = select_flowpulse_record(evidence)
    address = physical_address(record or {}, evidence)
    updated = copy.deepcopy(table)
    for entry in updated.get("entries", []):
        if not isinstance(entry, dict) or entry.get("state") != "unmapped":
            continue
        pointer = entry.get("pointer") if isinstance(entry.get("pointer"), dict) else {}
        checks, failures = compare_pointer(pointer, address, record)
        if not checks["flowPulseRecordFound"]:
            fault = make_fault(entry.get("pointerId"), "map", "receipt", "generic_log_not_mappable", "no FlowPulse record found")
            updated.setdefault("faults", []).append(fault)
            return updated, fault
        if not checks["readerAttachedTxHash"] or not checks["readerAttachedLogIndex"]:
            fault = make_fault(entry.get("pointerId"), "map", "receipt", "missing_receipt_metadata", "reader-attached receipt metadata is required")
            updated.setdefault("faults", []).append(fault)
            return updated, fault
        if failures:
            fault = make_fault(entry.get("pointerId"), "map", "receipt", "address_mismatch", ",".join(failures))
            updated.setdefault("faults", []).append(fault)
            return updated, fault
        page = build_page(pointer, address, checks)
        entry["state"] = "mapped"
        entry["pageId"] = page["pageId"]
        entry["receiptPage"] = page
        return updated, page
    fault = make_fault(None, "map", "receipt", "unmapped_pointer", "no unmapped pointer available")
    updated.setdefault("faults", []).append(fault)
    return updated, fault


def deref(table: dict[str, Any], pointer_id: str, field: str) -> dict[str, Any]:
    entry = find_entry(table, pointer_id)
    if not entry:
        return make_fault(pointer_id, "read", field, "unmapped_pointer", "pointer is not allocated")
    pointer = entry.get("pointer") if isinstance(entry.get("pointer"), dict) else {}
    if entry.get("state") == "unmapped":
        virtual = pointer.get("virtualAddress") if isinstance(pointer.get("virtualAddress"), dict) else {}
        if field in VIRTUAL_FIELDS:
            return {"schema": READ_SCHEMA, "allowed": True, "field": field, "value": virtual.get(field), "source": "pulse_pointer"}
        return make_fault(pointer_id, "read", field, "forbidden_pre_receipt_read", f"{field} is receipt metadata and cannot be read before reader mapping")
    page = entry.get("receiptPage") if isinstance(entry.get("receiptPage"), dict) else {}
    address = page.get("physicalAddress") if isinstance(page.get("physicalAddress"), dict) else {}
    if field in address and field in PAGE_FIELDS:
        return {"schema": READ_SCHEMA, "allowed": True, "field": field, "value": address.get(field), "source": "receipt_page"}
    return make_fault(pointer_id, "read", field, "unknown_field", f"{field} is not readable from this pointer")


def write(table: dict[str, Any], pointer_id: str, field: str, value: str) -> dict[str, Any]:
    entry = find_entry(table, pointer_id)
    if not entry:
        return make_fault(pointer_id, "write", field, "unmapped_pointer", "pointer is not allocated")
    if entry.get("state") == "mapped":
        return make_fault(pointer_id, "write", field, "illegal_write", "receipt pages are read-only")
    return make_fault(pointer_id, "write", field, "illegal_write", "FlowPulse pointers are immutable")


def verify_page(page: dict[str, Any]) -> dict[str, Any]:
    body = copy.deepcopy(page)
    page_id = body.pop("pageId", None)
    checks = {
        "schemaMatches": page.get("schema") == PAGE_SCHEMA,
        "pageIdMatches": axiom_writ.digest(body) == page_id,
        "readOnly": page.get("readOnly") is True,
        "hasReceiptCoordinates": truthy_hex((page.get("physicalAddress") or {}).get("txHash"))
        and (page.get("physicalAddress") or {}).get("logIndex") not in (None, ""),
    }
    failed = [key for key, ok in checks.items() if not ok]
    return {"schema": "flowmemory.receipt_page_verification.v0", "status": "valid" if not failed else "invalid", "pageId": page_id, "checks": checks, "failedChecks": failed}


def example_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "examples" / "flow-mmu"


def demo() -> dict[str, Any]:
    base = example_dir()
    table = read_json(base / "page-table.initial.json")
    table = alloc_pointer(table, read_json(base / "pulse-pointer.request.json"))
    pointer_id = table["entries"][0]["pointerId"]
    before = deref(table, pointer_id, "txHash")
    mapped_table, page = map_pointer(table, read_json(base / "flowpulse.matching.json"))
    after = deref(mapped_table, pointer_id, "txHash")
    illegal = write(mapped_table, pointer_id, "txHash", "0xdead")
    _, mismatch = map_pointer(table, read_json(base / "flowpulse.mismatched.json"))
    return {
        "schema": "flowmemory.flow_mmu_demo.v0",
        "pointerId": pointer_id,
        "beforeMapping": before,
        "mapping": page,
        "afterMapping": after,
        "illegalWrite": illegal,
        "mismatch": mismatch,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FlowMMU receipt-backed dereference utility.")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--agent-id", required=True)
    init.add_argument("--rootfield-id", required=True)
    init.add_argument("--out")
    init.add_argument("--pretty", action="store_true")
    alloc = sub.add_parser("alloc")
    alloc.add_argument("--table", required=True)
    alloc.add_argument("--pointer", required=True)
    alloc.add_argument("--out")
    alloc.add_argument("--pretty", action="store_true")
    map_cmd = sub.add_parser("map")
    map_cmd.add_argument("--table", required=True)
    map_cmd.add_argument("--flowpulse", required=True)
    map_cmd.add_argument("--out")
    map_cmd.add_argument("--page-out")
    map_cmd.add_argument("--pretty", action="store_true")
    deref_cmd = sub.add_parser("deref")
    deref_cmd.add_argument("--table", required=True)
    deref_cmd.add_argument("--pointer-id", required=True)
    deref_cmd.add_argument("--field", required=True)
    deref_cmd.add_argument("--out")
    deref_cmd.add_argument("--pretty", action="store_true")
    write_cmd = sub.add_parser("write")
    write_cmd.add_argument("--table", required=True)
    write_cmd.add_argument("--pointer-id", required=True)
    write_cmd.add_argument("--field", required=True)
    write_cmd.add_argument("--value", required=True)
    write_cmd.add_argument("--out")
    write_cmd.add_argument("--pretty", action="store_true")
    verify = sub.add_parser("verify-page")
    verify.add_argument("--page", required=True)
    verify.add_argument("--pretty", action="store_true")
    demo_cmd = sub.add_parser("demo")
    demo_cmd.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "init":
        write_json(init_table(args.agent_id, args.rootfield_id), args.out, args.pretty)
        return 0
    if args.command == "alloc":
        write_json(alloc_pointer(read_json(args.table), read_json(args.pointer)), args.out, args.pretty)
        return 0
    if args.command == "map":
        table, result = map_pointer(read_json(args.table), read_json(args.flowpulse))
        if args.page_out and result.get("schema") == PAGE_SCHEMA:
            write_json(result, args.page_out, args.pretty)
        output_payload = table if result.get("schema") == PAGE_SCHEMA else result
        write_json(output_payload if args.out else result, args.out, args.pretty)
        return 0 if result.get("schema") == PAGE_SCHEMA else 2
    if args.command == "deref":
        result = deref(read_json(args.table), args.pointer_id, args.field)
        write_json(result, args.out, args.pretty)
        return 0 if result.get("schema") == READ_SCHEMA and result.get("allowed") else 2
    if args.command == "write":
        result = write(read_json(args.table), args.pointer_id, args.field, args.value)
        write_json(result, args.out, args.pretty)
        return 2
    if args.command == "verify-page":
        verification = verify_page(read_json(args.page))
        write_json(verification, None, args.pretty)
        return 0 if verification["status"] == "valid" else 2
    if args.command == "demo":
        write_json(demo(), None, args.pretty)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
