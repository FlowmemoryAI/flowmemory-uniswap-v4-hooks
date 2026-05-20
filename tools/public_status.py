#!/usr/bin/env python3
"""Generate a claim-safe public Base Sepolia status page."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import release_evidence
except ModuleNotFoundError:  # pragma: no cover
    import release_evidence  # type: ignore


STATUS_SCHEMA = "flowmemory.public_status.v0"
DEFAULT_PACKET = "release-evidence/base-sepolia/RELEASE_PACKET.json"
DEFAULT_OUTPUT = "public/status/base-sepolia.md"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else repo_root() / candidate


def build_status(packet_path: str | Path = DEFAULT_PACKET) -> dict[str, Any]:
    path = resolve(packet_path)
    if not path.exists():
        return {
            "schema": STATUS_SCHEMA,
            "status": "blocked_no_release_packet",
            "network": "Base Sepolia",
            "testnetOnly": True,
            "packetPath": str(path),
            "hookAddress": "",
            "chainId": "84532",
            "releasePacketHash": "",
            "observedFlowPulseCount": 0,
            "latestObservedBlock": "",
            "finalityDistribution": {},
            "exampleProofEnvelope": None,
            "notClaims": release_evidence.NOT_CLAIMS,
        }
    packet = json.loads(path.read_text(encoding="utf-8"))
    issues = release_evidence.verify_packet(packet)
    records = packet.get("records", [])
    return {
        "schema": STATUS_SCHEMA,
        "status": "testnet_packet_ready" if not issues else "blocked_invalid_release_packet",
        "network": "Base Sepolia",
        "testnetOnly": True,
        "packetPath": str(path),
        "hookAddress": packet.get("hookAddress", ""),
        "chainId": packet.get("chainId", "84532"),
        "releasePacketHash": packet.get("releasePacketHash", ""),
        "observedFlowPulseCount": packet.get("counts", {}).get("flowPulse", 0),
        "latestObservedBlock": packet.get("latestBlock", ""),
        "finalityDistribution": packet.get("finalityDistribution", {}),
        "exampleProofEnvelope": records[0] if records else None,
        "validationIssues": issues,
        "notClaims": packet.get("notClaims", release_evidence.NOT_CLAIMS),
    }


def render_markdown(status: dict[str, Any]) -> str:
    example = status.get("exampleProofEnvelope") or {}
    lines = [
        "# FlowMemory Base Sepolia Public Status",
        "",
        "**Status:** " + status["status"],
        "",
        "This page is testnet-only. It is not a Base mainnet deployment claim.",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Network | {status['network']} |",
        f"| Chain ID | {status['chainId']} |",
        f"| Hook address | {status['hookAddress'] or 'not available'} |",
        f"| Release packet hash | {status['releasePacketHash'] or 'not available'} |",
        f"| Observed FlowPulse count | {status['observedFlowPulseCount']} |",
        f"| Latest observed block | {status['latestObservedBlock'] or 'not available'} |",
        f"| Finality distribution | `{json.dumps(status['finalityDistribution'], sort_keys=True)}` |",
        "",
        "## Example Proof Envelope",
        "",
    ]
    if example:
        lines.extend(
            [
                "| Field | Value |",
                "| --- | --- |",
                f"| Proof envelope ID | `{example.get('proofEnvelopeId')}` |",
                f"| txHash | `{example.get('txHash')}` |",
                f"| logIndex | `{example.get('logIndex')}` |",
                f"| blockNumber | `{example.get('blockNumber')}` |",
                f"| eventName | `{example.get('eventName')}` |",
            ]
        )
    else:
        lines.append("No observed proof envelope is available yet.")
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Not Base mainnet.",
            "- Not custody.",
            "- Not wallet authorization.",
            "- Not fund protection.",
            "- Not escrow.",
            "- Not semantic truth.",
            "- Not model correctness.",
            "- Not GPU acceleration.",
            "- Not a production verifier network.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate public Base Sepolia status markdown.")
    parser.add_argument("--packet", default=DEFAULT_PACKET)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    status = build_status(args.packet)
    if args.json:
        print(json.dumps(status, indent=2 if args.pretty else None, sort_keys=True))
    else:
        output = resolve(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_markdown(status), encoding="utf-8")
        print(f"Public status generated: {args.output}")
        print(f"status: {status['status']}")
    return 0 if not str(status["status"]).startswith("blocked_invalid") else 1


if __name__ == "__main__":
    sys.exit(main())
