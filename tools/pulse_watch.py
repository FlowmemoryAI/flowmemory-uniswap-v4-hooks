#!/usr/bin/env python3
"""PulseWatch: always-on FlowPulse reader/verifier loop.

The hook runs only inside Uniswap v4 transactions. PulseWatch is the 24/7 layer:
it watches the hook logs, attaches receipt metadata, deduplicates already-seen
logs, advances a block cursor, and writes append-only memory records.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import read_flowpulse_logs as reader
except ModuleNotFoundError:  # pragma: no cover
    import read_flowpulse_logs as reader  # type: ignore


WATCH_SCHEMA = "flowmemory.pulsewatch.v0"
STATE_SCHEMA = "flowmemory.pulsewatch_state.v0"
MEMORY_RECORD_SCHEMA = "flowmemory.pulsewatch_memory_record.v0"


def build_demo() -> dict[str, Any]:
    """Build a deterministic demo with synthetic reader-derived hook evidence."""

    hook_address = "0x1234567890123456789012345678901234567890"
    latest_block = 130
    records = [
        reader.normalize_log(
            hook_address,
            _flowpulse_log(hook_address, block_number=120, tx_fill="ab", log_index=7),
            {"status": "0x1"},
            latest_block,
            finality_confirmations=5,
        ),
        reader.normalize_log(
            hook_address,
            _after_swap_log(hook_address, block_number=121, tx_fill="cd", log_index=8),
            {"status": "0x1"},
            latest_block,
            finality_confirmations=5,
        ),
    ]
    reader_output = {
        "schema": "flowmemory.hook_log_reader.v0",
        "chainId": "84532",
        "hookAddress": hook_address,
        "fromBlock": "120",
        "toBlock": "121",
        "latestBlock": str(latest_block),
        "eventTopics": {
            "FlowPulse": reader.FLOWPULSE_TOPIC,
            "AfterSwapObserved": reader.AFTER_SWAP_OBSERVED_TOPIC,
        },
        "counts": {
            "records": len(records),
            "flowPulse": sum(1 for record in records if record["eventName"] == "FlowPulse"),
            "afterSwapObserved": sum(1 for record in records if record["eventName"] == "AfterSwapObserved"),
            "rejected": sum(1 for record in records if record["status"] == "rejected"),
        },
        "records": records,
    }
    state = empty_state(chain_id="84532", hook_address=hook_address, cursor_block=119)
    report, next_state, memory_records = ingest_reader_output(reader_output, state)
    return {
        "schema": "flowmemory.pulsewatch_demo.v0",
        "thesis": "The hook emits during transactions; PulseWatch keeps the memory layer alive 24/7.",
        "readerOutput": reader_output,
        "watchReport": report,
        "nextState": next_state,
        "memoryRecords": memory_records,
        "status": "pass" if not report["validationFaults"] else "fail",
        "notClaims": [
            "not_hook_runs_without_transactions",
            "not_production_verifier",
            "not_live_base_deployment",
            "not_custody",
            "not_fund_protection",
        ],
    }


def empty_state(*, chain_id: str, hook_address: str, cursor_block: int) -> dict[str, Any]:
    return {
        "schema": STATE_SCHEMA,
        "chainId": chain_id,
        "hookAddress": hook_address.lower(),
        "cursorBlock": cursor_block,
        "seenLogIds": [],
        "recordsObserved": 0,
        "memoryRecordsWritten": 0,
        "rejectedRecords": 0,
    }


def ingest_reader_output(reader_output: dict[str, Any], state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    faults = validate_reader_output(reader_output)
    seen = set(state.get("seenLogIds", []))
    memory_records: list[dict[str, Any]] = []
    accepted = 0
    duplicates = 0
    rejected = 0
    latest_seen_block = int(state.get("cursorBlock", 0))

    for record in reader_output.get("records", []):
        log_id = log_record_id(record)
        block_number = _safe_int(record.get("blockNumber"))
        if block_number is not None:
            latest_seen_block = max(latest_seen_block, block_number)
        if log_id in seen:
            duplicates += 1
            continue
        seen.add(log_id)
        if record.get("status") == "rejected":
            rejected += 1
            continue
        memory_record = memory_record_from_reader_record(reader_output, record)
        memory_records.append(memory_record)
        accepted += 1

    next_state = {
        **state,
        "schema": STATE_SCHEMA,
        "chainId": str(reader_output.get("chainId", state.get("chainId", ""))),
        "hookAddress": str(reader_output.get("hookAddress", state.get("hookAddress", ""))).lower(),
        "cursorBlock": latest_seen_block,
        "seenLogIds": sorted(seen),
        "recordsObserved": int(state.get("recordsObserved", 0)) + len(reader_output.get("records", [])),
        "memoryRecordsWritten": int(state.get("memoryRecordsWritten", 0)) + accepted,
        "rejectedRecords": int(state.get("rejectedRecords", 0)) + rejected,
    }
    report = {
        "schema": WATCH_SCHEMA,
        "mode": "continuous_reader",
        "chainId": next_state["chainId"],
        "hookAddress": next_state["hookAddress"],
        "fromBlock": reader_output.get("fromBlock"),
        "toBlock": reader_output.get("toBlock"),
        "latestBlock": reader_output.get("latestBlock"),
        "cursorBlockBefore": state.get("cursorBlock"),
        "cursorBlockAfter": next_state["cursorBlock"],
        "recordsSeen": len(reader_output.get("records", [])),
        "recordsAccepted": accepted,
        "recordsRejected": rejected,
        "duplicatesSkipped": duplicates,
        "memoryRecordsWritten": len(memory_records),
        "flowPulseMemoryRecords": sum(1 for item in memory_records if item.get("eventName") == "FlowPulse"),
        "afterSwapObservedRecords": sum(1 for item in memory_records if item.get("eventName") == "AfterSwapObserved"),
        "validationFaults": faults,
        "result": "PulseWatch advanced the memory cursor." if not faults else "PulseWatch rejected the reader batch.",
    }
    return report, next_state, memory_records


def validate_reader_output(reader_output: dict[str, Any]) -> list[str]:
    faults: list[str] = []
    if reader_output.get("schema") != "flowmemory.hook_log_reader.v0":
        faults.append("reader_schema_mismatch")
    if not reader_output.get("hookAddress"):
        faults.append("hook_address_missing")
    if not reader_output.get("chainId"):
        faults.append("chain_id_missing")
    for record in reader_output.get("records", []):
        if record.get("schema") != reader.FLOWPULSE_SCHEMA:
            faults.append("record_schema_mismatch")
        if record.get("hookAddress") != reader_output.get("hookAddress"):
            faults.append("record_hook_mismatch")
        if not record.get("txHash"):
            faults.append("record_txhash_missing")
        if record.get("logIndex") in {None, "None"}:
            faults.append("record_logindex_missing")
        if record.get("eventName") == "FlowPulse":
            if record.get("source") == "hook_time":
                faults.append("hook_time_receipt_metadata_smuggled")
            if record.get("rootfieldId") == reader.ZERO32:
                faults.append("zero_rootfield")
            if record.get("commitment") == reader.ZERO32:
                faults.append("zero_commitment")
        if record.get("status") == "rejected" and not record.get("validation"):
            faults.append("rejected_without_reason")
    return sorted(set(faults))


def memory_record_from_reader_record(reader_output: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "schema": MEMORY_RECORD_SCHEMA,
        "chainId": reader_output["chainId"],
        "hookAddress": reader_output["hookAddress"],
        "eventName": record["eventName"],
        "status": record["status"],
        "txHash": record["txHash"],
        "logIndex": record["logIndex"],
        "blockNumber": record["blockNumber"],
        "finality": record["finality"],
        "pulseId": record.get("pulseId"),
        "rootfieldId": record.get("rootfieldId"),
        "commitment": record.get("commitment"),
        "proofEnvelope": {
            "transactionIndex": record.get("transactionIndex"),
            "receiptStatus": record.get("receiptStatus"),
            "blockHash": record.get("blockHash"),
        },
    }
    payload["memoryRecordId"] = _digest(payload)
    return payload


def pull_reader_output(
    *,
    rpc_url: str,
    hook_address: str,
    from_block: str,
    to_block: str,
    finality_confirmations: int,
) -> dict[str, Any]:
    normalized_hook = reader.normalize_address(hook_address)
    logs = reader.rpc(
        rpc_url,
        "eth_getLogs",
        [{"address": normalized_hook, "fromBlock": reader.block_tag(from_block), "toBlock": reader.block_tag(to_block)}],
    )
    chain_id = reader.hex_int(reader.rpc(rpc_url, "eth_chainId", []))
    latest_block = reader.hex_int(reader.rpc(rpc_url, "eth_blockNumber", []))
    records = []
    for log in logs:
        topic0 = log["topics"][0].lower()
        if topic0 not in {reader.FLOWPULSE_TOPIC, reader.AFTER_SWAP_OBSERVED_TOPIC}:
            continue
        receipt = reader.rpc(rpc_url, "eth_getTransactionReceipt", [log["transactionHash"]])
        records.append(reader.normalize_log(normalized_hook, log, receipt, latest_block, finality_confirmations))

    return {
        "schema": "flowmemory.hook_log_reader.v0",
        "chainId": str(chain_id),
        "hookAddress": normalized_hook,
        "fromBlock": from_block,
        "toBlock": to_block,
        "latestBlock": str(latest_block),
        "eventTopics": {
            "FlowPulse": reader.FLOWPULSE_TOPIC,
            "AfterSwapObserved": reader.AFTER_SWAP_OBSERVED_TOPIC,
        },
        "counts": {
            "records": len(records),
            "flowPulse": sum(1 for record in records if record.get("eventName") == "FlowPulse"),
            "afterSwapObserved": sum(1 for record in records if record.get("eventName") == "AfterSwapObserved"),
            "rejected": sum(1 for record in records if record.get("status") == "rejected"),
        },
        "records": records,
    }


def log_record_id(record: dict[str, Any]) -> str:
    return f"{record.get('txHash')}:{record.get('logIndex')}"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def load_state(path: Path, *, chain_id: str, hook_address: str, cursor_block: int) -> dict[str, Any]:
    if path.exists():
        return load_json(path)
    return empty_state(chain_id=chain_id, hook_address=hook_address, cursor_block=cursor_block)


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_memory_records(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def _flowpulse_log(hook_address: str, *, block_number: int, tx_fill: str, log_index: int) -> dict[str, Any]:
    uri = "flowmemory://uniswap-v4/after-swap"
    data = (
        "0x"
        + _hex_word(reader.SWAP_MEMORY_SIGNAL)
        + ("33" * 32)
        + ("44" * 32)
        + ("55" * 32)
        + _hex_word(7)
        + _hex_word(123)
        + _hex_word(7 * 32)
        + _abi_string_tail(uri)
    )
    return {
        "address": hook_address,
        "topics": [
            reader.FLOWPULSE_TOPIC,
            _bytes32("11"),
            _bytes32("22"),
            _topic_address("0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"),
        ],
        "data": data,
        "blockNumber": hex(block_number),
        "blockHash": "0x" + ("aa" * 32),
        "transactionHash": "0x" + (tx_fill * 32),
        "transactionIndex": "0x1",
        "logIndex": hex(log_index),
    }


def _after_swap_log(hook_address: str, *, block_number: int, tx_fill: str, log_index: int) -> dict[str, Any]:
    return {
        "address": hook_address,
        "topics": [
            reader.AFTER_SWAP_OBSERVED_TOPIC,
            _topic_address("0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"),
            _topic_address("0xcccccccccccccccccccccccccccccccccccccccc"),
            _bytes32("dd"),
        ],
        "data": "0x" + ("22" * 32) + ("44" * 32) + ("66" * 32),
        "blockNumber": hex(block_number),
        "blockHash": "0x" + ("bb" * 32),
        "transactionHash": "0x" + (tx_fill * 32),
        "transactionIndex": "0x2",
        "logIndex": hex(log_index),
    }


def _hex_word(value: int) -> str:
    return f"{value:064x}"


def _bytes32(fill: str) -> str:
    return "0x" + (fill * 32)


def _topic_address(address: str) -> str:
    return "0x" + ("0" * 24) + address[2:].lower()


def _abi_string_tail(value: str) -> str:
    raw = value.encode("utf-8").hex()
    padded_len = ((len(raw) + 63) // 64) * 64
    return _hex_word(len(value.encode("utf-8"))) + raw.ljust(padded_len, "0")


def _safe_int(value: Any) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    import hashlib

    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def render_demo(demo: dict[str, Any]) -> str:
    report = demo["watchReport"]
    lines = [
        "FlowMemory PulseWatch",
        "",
        "Thesis:",
        f"  {demo['thesis']}",
        "",
        "Watch report:",
        f"  status: {demo['status'].upper()}",
        f"  records seen: {report['recordsSeen']}",
        f"  records accepted: {report['recordsAccepted']}",
        f"  memory records written: {report['memoryRecordsWritten']}",
        f"  cursor: {report['cursorBlockBefore']} -> {report['cursorBlockAfter']}",
        f"  flowPulse memory records: {report['flowPulseMemoryRecords']}",
        f"  duplicates skipped: {report['duplicatesSkipped']}",
        "",
        "Result:",
        "  The hook is transaction-triggered. PulseWatch is the always-on memory layer.",
        "",
        "Non-claims:",
        "  no production verifier, no live deployment claim, no custody, no fund protection.",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run or verify the always-on FlowPulse reader.")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Run deterministic PulseWatch demo.")
    demo.add_argument("--json", action="store_true")
    demo.add_argument("--pretty", action="store_true")

    verify = sub.add_parser("verify", help="Verify a PulseWatch demo or watch report JSON file.")
    verify.add_argument("--input", required=True)

    run = sub.add_parser("run", help="Run a live PulseWatch polling loop.")
    run.add_argument("--rpc-url", required=True)
    run.add_argument("--hook-address", required=True)
    run.add_argument("--state", required=True)
    run.add_argument("--memory-store", required=True)
    run.add_argument("--from-block", type=int, required=True)
    run.add_argument("--to-block", default="latest")
    run.add_argument("--finality-confirmations", type=int, default=20)
    run.add_argument("--poll-seconds", type=float, default=30.0)
    run.add_argument("--once", action="store_true")
    run.add_argument("--json", action="store_true")
    run.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "demo":
        demo = build_demo()
        if args.json:
            print(json.dumps(demo, indent=2 if args.pretty else None, sort_keys=True))
        else:
            print(render_demo(demo))
        return 0 if demo["status"] == "pass" else 1

    if args.command == "verify":
        payload = load_json(Path(args.input))
        report = payload.get("watchReport", payload)
        faults = report.get("validationFaults", [])
        if faults:
            print("PulseWatch verify: FAIL")
            for fault in faults:
                print(f"  {fault}")
            return 1
        print("PulseWatch verify: PASS")
        return 0

    if args.command == "run":
        state_path = Path(args.state)
        memory_path = Path(args.memory_store)
        state = load_state(
            state_path,
            chain_id="unknown",
            hook_address=args.hook_address,
            cursor_block=args.from_block - 1,
        )
        reports = []
        while True:
            from_block = str(int(state.get("cursorBlock", args.from_block - 1)) + 1)
            reader_output = pull_reader_output(
                rpc_url=args.rpc_url,
                hook_address=args.hook_address,
                from_block=from_block,
                to_block=args.to_block,
                finality_confirmations=args.finality_confirmations,
            )
            report, state, memory_records = ingest_reader_output(reader_output, state)
            append_memory_records(memory_path, memory_records)
            write_state(state_path, state)
            reports.append(report)
            if args.once:
                break
            time.sleep(args.poll_seconds)

        if args.json:
            print(json.dumps({"schema": "flowmemory.pulsewatch_run.v0", "reports": reports}, indent=2 if args.pretty else None, sort_keys=True))
        else:
            latest = reports[-1]
            print(f"PulseWatch run: {latest['recordsAccepted']} accepted, cursor={latest['cursorBlockAfter']}")
        return 0 if not reports[-1]["validationFaults"] else 1

    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
