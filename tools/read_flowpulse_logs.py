#!/usr/bin/env python3
"""
Dependency-light FlowMemory log reader.

This script turns Base Sepolia hook logs into a public proof-envelope record.
It does not need private keys and it does not submit transactions.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any


FLOWPULSE_TOPIC = "0x5d07190b9ae441b4d7b16259a48424acd451492b12f5f99a29f5bfd992c13e43"
AFTER_SWAP_OBSERVED_TOPIC = "0x348453213c80549a1d7c3083b39bbe1cbf143add02d35d0f419ec0bca68f6cf9"
FLOWPULSE_SCHEMA = "flowmemory.uniswap_v4_swap_signal.v0"
SWAP_MEMORY_SIGNAL = 4
ZERO32 = "0x" + ("0" * 64)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read FlowMemoryAfterSwapHook logs and attach receipt-derived proof-envelope facts."
    )
    parser.add_argument("--rpc-url", default=os.getenv("FLOWMEMORY_RPC_URL"), help="JSON-RPC URL.")
    parser.add_argument("--hook-address", default=os.getenv("FLOWMEMORY_HOOK_ADDRESS"), help="Hook contract address.")
    parser.add_argument("--from-block", default=os.getenv("FLOWMEMORY_FROM_BLOCK"), help="Start block number.")
    parser.add_argument("--to-block", default=os.getenv("FLOWMEMORY_TO_BLOCK", "latest"), help="End block number.")
    parser.add_argument(
        "--finality-confirmations",
        type=int,
        default=int(os.getenv("FLOWMEMORY_FINALITY_CONFIRMATIONS", "20")),
        help="Confirmation depth required for l2_confirmed status.",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--output", help="Optional output path for the JSON record.")
    return parser.parse_args()


def require_args(args: argparse.Namespace) -> None:
    missing = []
    if not args.rpc_url:
        missing.append("--rpc-url or FLOWMEMORY_RPC_URL")
    if not args.hook_address:
        missing.append("--hook-address or FLOWMEMORY_HOOK_ADDRESS")
    if not args.from_block:
        missing.append("--from-block or FLOWMEMORY_FROM_BLOCK")
    if missing:
        raise SystemExit("Missing required argument(s): " + ", ".join(missing))


def rpc(url: str, method: str, params: list[Any]) -> Any:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers={"content-type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"RPC request failed for {method}: {exc}") from exc

    if "error" in payload:
        raise RuntimeError(f"RPC error for {method}: {payload['error']}")
    return payload["result"]


def block_tag(value: str) -> str:
    if value in {"latest", "earliest", "pending", "safe", "finalized"}:
        return value
    if value.startswith("0x"):
        return value
    return hex(int(value))


def hex_int(value: str | None) -> int | None:
    if value is None:
        return None
    return int(value, 16)


def normalize_address(value: str) -> str:
    value = value.lower()
    if not value.startswith("0x") or len(value) != 42:
        raise ValueError(f"invalid address: {value}")
    return value


def topic_to_address(topic: str) -> str:
    return "0x" + topic[-40:].lower()


def word(data: str, index: int) -> str:
    raw = data[2:] if data.startswith("0x") else data
    start = index * 64
    end = start + 64
    if end > len(raw):
        raise ValueError(f"event data missing word {index}")
    return raw[start:end]


def word_hex(data: str, index: int) -> str:
    return "0x" + word(data, index)


def word_uint(data: str, index: int) -> int:
    return int(word(data, index), 16)


def decode_abi_string(data: str, offset_word_index: int) -> str:
    offset_bytes = word_uint(data, offset_word_index)
    length_word_index = offset_bytes // 32
    length = word_uint(data, length_word_index)
    raw = data[2:] if data.startswith("0x") else data
    start = (length_word_index + 1) * 64
    byte_hex_len = length * 2
    return bytes.fromhex(raw[start : start + byte_hex_len]).decode("utf-8", errors="replace")


def decode_flowpulse(log: dict[str, Any]) -> dict[str, Any]:
    topics = log["topics"]
    if len(topics) != 4:
        raise ValueError("FlowPulse log should have 4 topics")

    data = log["data"]
    pulse_type = word_uint(data, 0)
    rootfield_id = topics[2].lower()
    commitment = word_hex(data, 2).lower()

    validation = []
    if pulse_type != SWAP_MEMORY_SIGNAL:
        validation.append("wrong_pulse_type")
    if rootfield_id == ZERO32:
        validation.append("zero_rootfield")
    if commitment == ZERO32:
        validation.append("zero_commitment")

    return {
        "eventName": "FlowPulse",
        "pulseType": "SWAP_MEMORY_SIGNAL" if pulse_type == SWAP_MEMORY_SIGNAL else str(pulse_type),
        "pulseTypeValue": pulse_type,
        "pulseId": topics[1].lower(),
        "rootfieldId": rootfield_id,
        "actor": topic_to_address(topics[3]),
        "subjectPoolId": word_hex(data, 1).lower(),
        "commitment": commitment,
        "parentPulseId": word_hex(data, 3).lower(),
        "sequence": str(word_uint(data, 4)),
        "occurredAt": str(word_uint(data, 5)),
        "uri": decode_abi_string(data, 6),
        "validation": validation,
    }


def decode_after_swap_observed(log: dict[str, Any]) -> dict[str, Any]:
    topics = log["topics"]
    if len(topics) != 4:
        raise ValueError("AfterSwapObserved log should have 4 topics")

    data = log["data"]
    return {
        "eventName": "AfterSwapObserved",
        "caller": topic_to_address(topics[1]),
        "sender": topic_to_address(topics[2]),
        "poolId": topics[3].lower(),
        "rootfieldId": word_hex(data, 0).lower(),
        "commitment": word_hex(data, 1).lower(),
        "hookDataHash": word_hex(data, 2).lower(),
        "validation": [],
    }


def classify_finality(block_number: int | None, latest_block: int | None, confirmations_required: int) -> dict[str, Any]:
    if block_number is None or latest_block is None:
        return {"status": "receipt_attached", "confirmations": None, "requiredConfirmations": confirmations_required}

    confirmations = max(0, latest_block - block_number + 1)
    status = "l2_confirmed" if confirmations >= confirmations_required else "receipt_attached"
    return {"status": status, "confirmations": confirmations, "requiredConfirmations": confirmations_required}


def normalize_log(
    hook_address: str,
    log: dict[str, Any],
    receipt: dict[str, Any] | None,
    latest_block: int | None,
    finality_confirmations: int,
) -> dict[str, Any]:
    topic0 = log["topics"][0].lower()
    if topic0 == FLOWPULSE_TOPIC:
        decoded = decode_flowpulse(log)
    elif topic0 == AFTER_SWAP_OBSERVED_TOPIC:
        decoded = decode_after_swap_observed(log)
    else:
        decoded = {"eventName": "Unknown", "validation": ["unexpected_topic"]}

    receipt_status = receipt.get("status") if receipt else None
    validation = list(decoded.pop("validation", []))
    if normalize_address(log["address"]) != hook_address:
        validation.append("unexpected_contract")
    if receipt is None:
        validation.append("receipt_missing")
    elif receipt_status != "0x1":
        validation.append("receipt_reverted")

    finality = classify_finality(hex_int(log.get("blockNumber")), latest_block, finality_confirmations)
    status = "rejected" if validation else finality["status"]

    return {
        "schema": FLOWPULSE_SCHEMA,
        "status": status,
        "validation": validation,
        "hookAddress": hook_address,
        "blockNumber": str(hex_int(log.get("blockNumber"))),
        "blockHash": log.get("blockHash"),
        "txHash": log.get("transactionHash"),
        "transactionIndex": str(hex_int(log.get("transactionIndex"))),
        "logIndex": str(hex_int(log.get("logIndex"))),
        "receiptStatus": "success" if receipt_status == "0x1" else receipt_status,
        "finality": finality,
        "rawLog": {
            "address": log.get("address"),
            "topics": log.get("topics"),
            "data": log.get("data"),
        },
        **decoded,
    }


def main() -> int:
    args = parse_args()
    require_args(args)

    hook_address = normalize_address(args.hook_address)
    logs = rpc(
        args.rpc_url,
        "eth_getLogs",
        [{"address": hook_address, "fromBlock": block_tag(args.from_block), "toBlock": block_tag(args.to_block)}],
    )
    chain_id = hex_int(rpc(args.rpc_url, "eth_chainId", []))
    latest_block = hex_int(rpc(args.rpc_url, "eth_blockNumber", []))

    records = []
    for log in logs:
        topic0 = log["topics"][0].lower()
        if topic0 not in {FLOWPULSE_TOPIC, AFTER_SWAP_OBSERVED_TOPIC}:
            continue
        receipt = rpc(args.rpc_url, "eth_getTransactionReceipt", [log["transactionHash"]])
        records.append(normalize_log(hook_address, log, receipt, latest_block, args.finality_confirmations))

    output = {
        "schema": "flowmemory.hook_log_reader.v0",
        "chainId": str(chain_id),
        "hookAddress": hook_address,
        "fromBlock": args.from_block,
        "toBlock": args.to_block,
        "latestBlock": str(latest_block),
        "eventTopics": {
            "FlowPulse": FLOWPULSE_TOPIC,
            "AfterSwapObserved": AFTER_SWAP_OBSERVED_TOPIC,
        },
        "counts": {
            "records": len(records),
            "flowPulse": sum(1 for record in records if record.get("eventName") == "FlowPulse"),
            "afterSwapObserved": sum(1 for record in records if record.get("eventName") == "AfterSwapObserved"),
            "rejected": sum(1 for record in records if record.get("status") == "rejected"),
        },
        "records": records,
    }

    text = json.dumps(output, indent=2 if args.pretty else None, sort_keys=True)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - command-line guardrail
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
