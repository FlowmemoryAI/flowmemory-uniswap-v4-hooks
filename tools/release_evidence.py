#!/usr/bin/env python3
"""Build and verify Base Sepolia release evidence packets.

Observed packets must come from reader output with real FlowPulse logs. Fixture
packets are allowed only when fixture mode is explicit.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import pulse_watch
except ModuleNotFoundError:  # pragma: no cover
    import pulse_watch  # type: ignore


PACKET_SCHEMA = "flowmemory.base_sepolia_release_packet.v0"
BASE_SEPOLIA_CHAIN_ID = "84532"
ALLOWED_SOURCE_TYPES = {"observed_testnet", "fixture"}
ALLOWED_FINALITY_STATES = {"observed", "receipt_attached", "l2_confirmed", "finalized", "testnet_verified", "rejected"}
NOT_CLAIMS = [
    "not_base_mainnet",
    "not_custody",
    "not_wallet_authorization",
    "not_fund_protection",
    "not_escrow",
    "not_semantic_truth",
    "not_model_correctness",
    "not_gpu_acceleration",
    "not_production_verifier_network",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: Any) -> str:
    import hashlib

    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def proof_envelope_id(chain_id: str, record: dict[str, Any]) -> str:
    tx_hash = record.get("txHash")
    log_index = record.get("logIndex")
    if not tx_hash or log_index in {None, "None", ""}:
        raise ValueError("proof envelope identity requires txHash and logIndex")
    return f"{chain_id}:{str(tx_hash).lower()}:{str(log_index)}"


def finality_status(record: dict[str, Any]) -> str:
    finality = record.get("finality", {})
    if isinstance(finality, dict):
        status = str(finality.get("status", "observed"))
    else:
        status = str(finality or "observed")
    return status if status in ALLOWED_FINALITY_STATES else "observed"


def canonical_record(chain_id: str, hook_address: str, record: dict[str, Any]) -> dict[str, Any]:
    topic0 = None
    raw_log = record.get("rawLog") or {}
    topics = raw_log.get("topics") or []
    if topics:
        topic0 = str(topics[0]).lower()
    return {
        "proofEnvelopeId": proof_envelope_id(chain_id, record),
        "chainId": chain_id,
        "hookAddress": hook_address.lower(),
        "eventName": record.get("eventName"),
        "status": record.get("status"),
        "finalityState": finality_status(record),
        "txHash": str(record.get("txHash")).lower(),
        "logIndex": str(record.get("logIndex")),
        "blockHash": record.get("blockHash"),
        "blockNumber": record.get("blockNumber"),
        "transactionIndex": record.get("transactionIndex"),
        "receiptStatus": record.get("receiptStatus"),
        "contractAddress": record.get("hookAddress", hook_address).lower(),
        "eventTopic0": topic0,
        "rawLog": raw_log,
        "pulseId": record.get("pulseId"),
        "rootfieldId": record.get("rootfieldId"),
        "commitment": record.get("commitment"),
    }


def dedupe_records(chain_id: str, hook_address: str, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    output = []
    for record in records:
        if record.get("status") == "rejected":
            continue
        item = canonical_record(chain_id, hook_address, record)
        if item["proofEnvelopeId"] in seen:
            continue
        seen.add(item["proofEnvelopeId"])
        output.append(item)
    return output


def finality_distribution(records: list[dict[str, Any]]) -> dict[str, int]:
    distribution: dict[str, int] = {}
    for record in records:
        state = record["finalityState"]
        distribution[state] = distribution.get(state, 0) + 1
    return dict(sorted(distribution.items()))


def build_packet(
    reader_output: dict[str, Any],
    *,
    source_type: str = "observed_testnet",
    fixture_mode: bool = False,
    observed_at: str | None = None,
    source_rpc_label: str = "operator_configured_rpc",
    deployment_manifest: str = "",
) -> dict[str, Any]:
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError(f"source_type must be one of {sorted(ALLOWED_SOURCE_TYPES)}")
    if source_type == "fixture" and not fixture_mode:
        raise ValueError("fixture source requires explicit fixture_mode")
    chain_id = str(reader_output.get("chainId"))
    if chain_id != BASE_SEPOLIA_CHAIN_ID:
        raise ValueError(f"release evidence requires Base Sepolia chainId {BASE_SEPOLIA_CHAIN_ID}, got {chain_id}")
    hook_address = str(reader_output.get("hookAddress", "")).lower()
    records = dedupe_records(chain_id, hook_address, list(reader_output.get("records", [])))
    flowpulse_count = sum(1 for record in records if record.get("eventName") == "FlowPulse")
    if source_type == "observed_testnet" and flowpulse_count == 0:
        raise ValueError("observed release evidence requires at least one observed FlowPulse record")

    body = {
        "schema": PACKET_SCHEMA,
        "network": "Base Sepolia",
        "chainId": chain_id,
        "status": "observed_testnet" if source_type == "observed_testnet" else "fixture_only",
        "sourceType": source_type,
        "fixtureMode": fixture_mode,
        "observedAt": observed_at or now_iso(),
        "sourceRpcLabel": source_rpc_label,
        "hookAddress": hook_address,
        "deploymentManifest": deployment_manifest,
        "fromBlock": reader_output.get("fromBlock"),
        "toBlock": reader_output.get("toBlock"),
        "latestBlock": reader_output.get("latestBlock"),
        "counts": {
            "records": len(records),
            "flowPulse": flowpulse_count,
            "afterSwapObserved": sum(1 for record in records if record.get("eventName") == "AfterSwapObserved"),
            "duplicatesRemoved": len(reader_output.get("records", [])) - len(records),
        },
        "finalityDistribution": finality_distribution(records),
        "records": records,
        "notClaims": NOT_CLAIMS,
    }
    body["releasePacketHash"] = digest(body)
    return body


def verify_packet(packet: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if packet.get("schema") != PACKET_SCHEMA:
        issues.append("schema_mismatch")
    if str(packet.get("chainId")) != BASE_SEPOLIA_CHAIN_ID:
        issues.append("chain_id_not_base_sepolia")
    if packet.get("sourceType") == "fixture" and not packet.get("fixtureMode"):
        issues.append("fixture_without_fixture_mode")
    if packet.get("sourceType") == "observed_testnet" and packet.get("counts", {}).get("flowPulse", 0) < 1:
        issues.append("observed_packet_missing_flowpulse")
    record_ids = [record.get("proofEnvelopeId") for record in packet.get("records", [])]
    if len(record_ids) != len(set(record_ids)):
        issues.append("duplicate_proof_envelope_id")
    for record in packet.get("records", []):
        if record.get("finalityState") not in ALLOWED_FINALITY_STATES:
            issues.append("unknown_finality_state")
        if record.get("finalityState") == "testnet_verified" and packet.get("sourceType") != "observed_testnet":
            issues.append("fixture_cannot_be_testnet_verified")
    expected_hash = packet.get("releasePacketHash")
    without_hash = {key: value for key, value in packet.items() if key != "releasePacketHash"}
    if expected_hash != digest(without_hash):
        issues.append("release_packet_hash_mismatch")
    missing_non_claims = sorted(set(NOT_CLAIMS) - set(packet.get("notClaims", [])))
    issues.extend(f"missing_non_claim:{claim}" for claim in missing_non_claims)
    return sorted(set(issues))


def render_packet(packet: dict[str, Any]) -> str:
    return "\n".join(
        [
            "FlowMemory Base Sepolia Release Packet",
            "",
            f"status: {packet['status']}",
            f"chainId: {packet['chainId']}",
            f"hookAddress: {packet['hookAddress']}",
            f"releasePacketHash: {packet['releasePacketHash']}",
            f"observed FlowPulse count: {packet['counts']['flowPulse']}",
            f"latestBlock: {packet['latestBlock']}",
            f"finalityDistribution: {packet['finalityDistribution']}",
            "",
            "Non-claims:",
            "  testnet-only, no custody, no wallet authorization, no fund protection, no production verifier network.",
        ]
    )


def load_json(path: str | Path) -> dict[str, Any]:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = repo_root() / candidate
    return json.loads(candidate.read_text(encoding="utf-8"))


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = repo_root() / candidate
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return candidate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and verify Base Sepolia release evidence packets.")
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate")
    generate.add_argument("--reader-output", required=True)
    generate.add_argument("--output", default="release-evidence/base-sepolia/RELEASE_PACKET.json")
    generate.add_argument("--source-type", default="observed_testnet", choices=sorted(ALLOWED_SOURCE_TYPES))
    generate.add_argument("--fixture-mode", action="store_true")
    generate.add_argument("--observed-at")
    generate.add_argument("--source-rpc-label", default="operator_configured_rpc")
    generate.add_argument("--deployment-manifest", default="")
    generate.add_argument("--json", action="store_true")
    generate.add_argument("--pretty", action="store_true")

    scan = sub.add_parser("scan")
    scan.add_argument("--rpc-url", required=True)
    scan.add_argument("--hook-address", required=True)
    scan.add_argument("--from-block", required=True)
    scan.add_argument("--to-block", default="latest")
    scan.add_argument("--finality-confirmations", type=int, default=20)
    scan.add_argument("--output", default="release-evidence/base-sepolia/RELEASE_PACKET.json")

    verify = sub.add_parser("verify")
    verify.add_argument("--input", required=True)

    replay = sub.add_parser("replay")
    replay.add_argument("--input", required=True)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "generate":
        packet = build_packet(
            load_json(args.reader_output),
            source_type=args.source_type,
            fixture_mode=args.fixture_mode,
            observed_at=args.observed_at,
            source_rpc_label=args.source_rpc_label,
            deployment_manifest=args.deployment_manifest,
        )
        output = write_json(args.output, packet)
        if args.json:
            print(json.dumps(packet, indent=2 if args.pretty else None, sort_keys=True))
        else:
            print(render_packet(packet))
            print(f"\nWrote: {output}")
        return 0

    if args.command == "scan":
        reader_output = pulse_watch.pull_reader_output(
            rpc_url=args.rpc_url,
            hook_address=args.hook_address,
            from_block=args.from_block,
            to_block=args.to_block,
            finality_confirmations=args.finality_confirmations,
        )
        packet = build_packet(reader_output)
        output = write_json(args.output, packet)
        print(render_packet(packet))
        print(f"\nWrote: {output}")
        return 0

    if args.command == "verify":
        issues = verify_packet(load_json(args.input))
        print("Release evidence verify: " + ("PASS" if not issues else "FAIL"))
        for issue in issues:
            print(f"  {issue}")
        return 0 if not issues else 1

    if args.command == "replay":
        packet = load_json(args.input)
        replay_hash = digest({key: value for key, value in packet.items() if key != "releasePacketHash"})
        print("Release evidence replay: " + ("PASS" if replay_hash == packet.get("releasePacketHash") else "FAIL"))
        print(f"  replayHash: {replay_hash}")
        return 0 if replay_hash == packet.get("releasePacketHash") else 1

    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
