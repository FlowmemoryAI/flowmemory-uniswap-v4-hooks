#!/usr/bin/env python3
"""Safe Base Sepolia deployment manifest tooling.

This tool does not deploy contracts and does not read private keys. It creates
and validates sanitized deployment manifests around the Foundry/Base Sepolia
runbook.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "flowmemory.base_sepolia_deployment_manifest.v0"
BASE_SEPOLIA_CHAIN_ID = 84532
BASE_SEPOLIA_POOL_MANAGER = "0x05E73354cFDd6745C338b50BcFDfA3Aa6fA03408"
CREATE2_DEPLOYER = "0x4e59b44847b379578588920cA78FbF26c0B4956C"
STATUS_VALUES = {
    "local_only",
    "dry_run",
    "deployed_testnet_unverified",
    "deployed_testnet_verified",
    "blocked_missing_environment",
}
SECRET_MARKERS = ("private", "secret", "token", "key", "rpc_url", "apikey", "password", "mnemonic")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root(), text=True).strip()
    except Exception:  # pragma: no cover
        return "unknown"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def is_secret_name(name: str) -> bool:
    lowered = name.lower()
    return any(marker in lowered for marker in SECRET_MARKERS)


def redact_value(name: str, value: Any) -> Any:
    if value is None or value == "":
        return value
    return "<redacted>" if is_secret_name(name) else value


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: redact_value(key, sanitize(child)) for key, child in value.items()}
    if isinstance(value, list):
        return [sanitize(child) for child in value]
    return value


def assert_base_sepolia(chain_id: int) -> None:
    if chain_id != BASE_SEPOLIA_CHAIN_ID:
        raise ValueError(f"Base Sepolia deployment requires chainId {BASE_SEPOLIA_CHAIN_ID}, got {chain_id}")


def assert_status(status: str) -> None:
    if status not in STATUS_VALUES:
        raise ValueError(f"invalid deployment status {status}; expected one of {sorted(STATUS_VALUES)}")


def build_manifest(
    *,
    status: str = "dry_run",
    chain_id: int = BASE_SEPOLIA_CHAIN_ID,
    pool_manager: str = BASE_SEPOLIA_POOL_MANAGER,
    deployer_address: str | None = None,
    hook_address: str | None = None,
    block_number: str | None = None,
    create2_salt: str | None = None,
    init_code_hash: str | None = None,
    source_verification_status: str = "not_submitted",
    notes: str | None = None,
) -> dict[str, Any]:
    assert_status(status)
    assert_base_sepolia(chain_id)
    body = {
        "schema": SCHEMA,
        "network": "Base Sepolia",
        "chainId": chain_id,
        "status": status,
        "gitCommit": git_commit(),
        "generatedAt": now_iso(),
        "contract": "FlowMemoryAfterSwapHook",
        "poolManager": pool_manager,
        "create2Deployer": CREATE2_DEPLOYER,
        "deployerAddress": deployer_address or os.getenv("BASE_SEPOLIA_DEPLOYER_ADDRESS", ""),
        "hookAddress": hook_address or "",
        "blockNumber": block_number or "",
        "constructorArgs": {"poolManager": pool_manager},
        "create2": {
            "salt": create2_salt or "",
            "initCodeHash": init_code_hash or "",
            "requiresAfterSwapOnlyFlag": True,
        },
        "sourceVerification": {
            "status": source_verification_status,
            "explorerUrl": "",
        },
        "commands": {
            "build": "forge build",
            "test": "forge test -vvv",
            "dryRun": 'forge script script/DeployBaseSepolia.s.sol:DeployBaseSepolia --sig "run(address)" "$BASE_SEPOLIA_POOL_MANAGER" --rpc-url "$BASE_SEPOLIA_RPC_URL"',
            "broadcast": 'forge script script/DeployBaseSepolia.s.sol:DeployBaseSepolia --sig "run(address)" "$BASE_SEPOLIA_POOL_MANAGER" --rpc-url "$BASE_SEPOLIA_RPC_URL" --broadcast',
            "verifyReadOnly": 'forge script script/VerifyBaseSepolia.s.sol:VerifyBaseSepolia --sig "verify(address)" "$FLOWMEMORY_HOOK_ADDRESS" --rpc-url "$BASE_SEPOLIA_RPC_URL"',
        },
        "notClaims": [
            "not_base_mainnet",
            "not_custody",
            "not_wallet_authorization",
            "not_fund_protection",
            "not_semantic_truth",
            "not_model_correctness",
            "not_production_verifier_network",
        ],
        "notes": notes or "Sanitized manifest. No private keys, RPC URLs, API tokens, or .env contents are recorded.",
    }
    return sanitize(body)


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if manifest.get("schema") != SCHEMA:
        issues.append("schema_mismatch")
    if manifest.get("chainId") != BASE_SEPOLIA_CHAIN_ID:
        issues.append("chain_id_not_base_sepolia")
    if manifest.get("status") not in STATUS_VALUES:
        issues.append("invalid_status")
    text = json.dumps(manifest, sort_keys=True)
    forbidden = ["PRIVATE_" + "KEY=", "SECRET_" + "KEY=", "gho_", "https://", "wss://"]
    for token in forbidden:
        if token in text:
            issues.append(f"possible_secret_or_rpc_url:{token}")
    return sorted(set(issues))


def check_chain(rpc_url: str) -> dict[str, Any]:
    try:
        from tools import read_flowpulse_logs as reader
    except ModuleNotFoundError:  # pragma: no cover
        import read_flowpulse_logs as reader  # type: ignore

    chain_id = reader.hex_int(reader.rpc(rpc_url, "eth_chainId", []))
    return {
        "schema": "flowmemory.base_sepolia_chain_check.v0",
        "expectedChainId": BASE_SEPOLIA_CHAIN_ID,
        "actualChainId": chain_id,
        "status": "PASS" if chain_id == BASE_SEPOLIA_CHAIN_ID else "FAIL",
    }


def render_manifest(manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "FlowMemory Base Sepolia Deployment Manifest",
            "",
            f"network: {manifest['network']}",
            f"chainId: {manifest['chainId']}",
            f"status: {manifest['status']}",
            f"poolManager: {manifest['poolManager']}",
            f"hookAddress: {manifest['hookAddress'] or 'not_recorded'}",
            f"sourceVerification: {manifest['sourceVerification']['status']}",
            "",
            "Result:",
            "  Manifest is sanitized and Base Sepolia scoped.",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create and validate sanitized Base Sepolia deployment manifests.")
    sub = parser.add_subparsers(dest="command", required=True)

    dry = sub.add_parser("dry-run-manifest")
    dry.add_argument("--output", default="deployments/base-sepolia/deployment-manifest.dry-run.json")
    dry.add_argument("--status", default="dry_run", choices=sorted(STATUS_VALUES))
    dry.add_argument("--deployer-address")
    dry.add_argument("--hook-address")
    dry.add_argument("--block-number")
    dry.add_argument("--create2-salt")
    dry.add_argument("--init-code-hash")
    dry.add_argument("--source-verification-status", default="not_submitted")
    dry.add_argument("--json", action="store_true")
    dry.add_argument("--pretty", action="store_true")

    validate = sub.add_parser("validate")
    validate.add_argument("--input", required=True)

    chain = sub.add_parser("check-chain")
    chain.add_argument("--rpc-url", required=True)
    chain.add_argument("--json", action="store_true")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "dry-run-manifest":
        manifest = build_manifest(
            status=args.status,
            deployer_address=args.deployer_address,
            hook_address=args.hook_address,
            block_number=args.block_number,
            create2_salt=args.create2_salt,
            init_code_hash=args.init_code_hash,
            source_verification_status=args.source_verification_status,
        )
        output_path = repo_root() / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(manifest, indent=2 if args.pretty else None, sort_keys=True))
        else:
            print(render_manifest(manifest))
            print(f"\nWrote: {args.output}")
        return 0

    if args.command == "validate":
        path = Path(args.input)
        if not path.is_absolute():
            path = repo_root() / path
        manifest = json.loads(path.read_text(encoding="utf-8"))
        issues = validate_manifest(manifest)
        print("Deployment manifest validate: " + ("PASS" if not issues else "FAIL"))
        for issue in issues:
            print(f"  {issue}")
        return 0 if not issues else 1

    if args.command == "check-chain":
        report = check_chain(args.rpc_url)
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(f"Base Sepolia chain check: {report['status']} ({report['actualChainId']})")
        return 0 if report["status"] == "PASS" else 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
