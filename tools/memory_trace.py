#!/usr/bin/env python3
"""
Proof-carried agent memory utilities.

This module turns a MachineMemoryTrace into an Agent Memory Pack: a compact,
deterministic recall surface that an agent can cite, route through, and verify.
It is intentionally dependency-light and works on draft R&D traces.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


TRACE_SCHEMA = "flowmemory.machine_memory_trace.v0"
PACK_SCHEMA = "flowmemory.agent_memory_pack.v0"
ALLOWED_ARTIFACT_TYPES = {"FlowPulse", "ComputePulse", "CachePulse", "ModelPulse", "AgentPulse"}
ALLOWED_EDGE_TYPES = {"observed_by", "uses", "reuses", "produces", "summarizes", "verifies"}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: Any, domain: str) -> str:
    payload = f"{domain}:{canonical_json(value)}".encode("utf-8")
    return "0x" + hashlib.sha256(payload).hexdigest()


def load_json(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("trace must be a JSON object")
    return payload


def _is_non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _add_issue(issues: list[dict[str, str]], severity: str, code: str, message: str) -> None:
    issues.append({"severity": severity, "code": code, "message": message})


def validate_trace(trace: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if trace.get("schema") != TRACE_SCHEMA:
        _add_issue(issues, "error", "schema_mismatch", f"expected {TRACE_SCHEMA}")

    rootfield_id = trace.get("rootfieldId")
    if not _is_non_empty(rootfield_id):
        _add_issue(issues, "error", "missing_rootfield", "trace must include rootfieldId")

    artifacts = trace.get("artifacts")
    edges = trace.get("edges")
    if not isinstance(artifacts, list) or not artifacts:
        _add_issue(issues, "error", "missing_artifacts", "trace must include artifacts")
        artifacts = []
    if not isinstance(edges, list):
        _add_issue(issues, "error", "missing_edges", "trace must include edges")
        edges = []

    artifact_ids: set[str] = set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            _add_issue(issues, "error", "invalid_artifact", f"artifact {index} must be an object")
            continue

        artifact_type = artifact.get("type")
        artifact_id = artifact.get("id")
        memory = artifact.get("memory")
        envelope = artifact.get("proofEnvelope")

        if artifact_type not in ALLOWED_ARTIFACT_TYPES:
            _add_issue(issues, "error", "unknown_artifact_type", f"artifact {index} has unknown type {artifact_type}")
        if not _is_non_empty(artifact_id):
            _add_issue(issues, "error", "missing_artifact_id", f"artifact {index} must include id")
        elif artifact_id in artifact_ids:
            _add_issue(issues, "error", "duplicate_artifact_id", f"duplicate artifact id {artifact_id}")
        else:
            artifact_ids.add(artifact_id)
        if not _is_non_empty(artifact.get("boundary")):
            _add_issue(issues, "error", "missing_boundary", f"{artifact_id or index} must include boundary")
        if not isinstance(memory, dict):
            _add_issue(issues, "error", "missing_memory", f"{artifact_id or index} must include memory object")
            memory = {}
        if not isinstance(envelope, dict):
            _add_issue(issues, "error", "missing_proof_envelope", f"{artifact_id or index} must include proofEnvelope")
            envelope = {}

        status = str(artifact.get("status", "")).lower()
        if "mock" in status or "rd" in status:
            _add_issue(
                issues,
                "info",
                "rd_artifact",
                f"{artifact_id or index} is labeled as R&D/example material, not a deployed verifier claim",
            )

        if artifact_type == "FlowPulse":
            for required in ("chainId", "txHash", "logIndex", "hookAddress"):
                if required not in envelope:
                    _add_issue(issues, "error", "flowpulse_envelope_incomplete", f"FlowPulse {artifact_id} missing {required}")
            if envelope.get("readerAttachedReceiptMetadata") is not True:
                _add_issue(
                    issues,
                    "warning",
                    "flowpulse_receipt_metadata_not_attached",
                    f"FlowPulse {artifact_id} should mark receipt metadata as reader-attached",
                )
            if memory.get("rootfieldId") != rootfield_id:
                _add_issue(issues, "warning", "rootfield_mismatch", f"FlowPulse {artifact_id} rootfield differs from trace")
            if not _is_non_empty(memory.get("commitment")):
                _add_issue(issues, "error", "missing_commitment", f"FlowPulse {artifact_id} must include commitment")

        if artifact_type == "ComputePulse":
            for required in ("jobId", "executor"):
                if required not in envelope:
                    _add_issue(issues, "warning", "computepulse_envelope_incomplete", f"ComputePulse {artifact_id} missing {required}")
            for required in ("modelCommitment", "inputCommitment", "outputCommitment"):
                if not _is_non_empty(memory.get(required)):
                    _add_issue(issues, "warning", "computepulse_memory_incomplete", f"ComputePulse {artifact_id} missing {required}")

        if artifact_type == "ModelPulse":
            source = envelope.get("sourceComputePulse")
            if source and source not in artifact_ids:
                # A later artifact may not have appeared yet, so this is checked again after the artifact loop.
                pass
            if not _is_non_empty(memory.get("artifact")):
                _add_issue(issues, "warning", "modelpulse_memory_incomplete", f"ModelPulse {artifact_id} should describe artifact")

    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            _add_issue(issues, "error", "invalid_edge", f"edge {index} must be an object")
            continue
        edge_type = edge.get("type")
        source = edge.get("from")
        target = edge.get("to")
        if edge_type not in ALLOWED_EDGE_TYPES:
            _add_issue(issues, "error", "unknown_edge_type", f"edge {index} has unknown type {edge_type}")
        if source not in artifact_ids:
            _add_issue(issues, "error", "edge_missing_source", f"edge {index} source does not match an artifact")
        if target not in artifact_ids:
            _add_issue(issues, "error", "edge_missing_target", f"edge {index} target does not match an artifact")

    for artifact in artifacts:
        if isinstance(artifact, dict) and artifact.get("type") == "ModelPulse":
            source = (artifact.get("proofEnvelope") or {}).get("sourceComputePulse")
            if source and source not in artifact_ids:
                _add_issue(
                    issues,
                    "warning",
                    "modelpulse_source_missing",
                    f"ModelPulse {artifact.get('id')} references missing ComputePulse {source}",
                )

    return issues


def severity_counts(issues: list[dict[str, str]]) -> dict[str, int]:
    return {
        "error": sum(1 for issue in issues if issue["severity"] == "error"),
        "warning": sum(1 for issue in issues if issue["severity"] == "warning"),
        "info": sum(1 for issue in issues if issue["severity"] == "info"),
    }


def artifact_score(artifact: dict[str, Any], edge_count: int) -> int:
    base_scores = {
        "AgentPulse": 45,
        "FlowPulse": 42,
        "ComputePulse": 38,
        "CachePulse": 36,
        "ModelPulse": 32,
    }
    score = base_scores.get(artifact.get("type"), 10)
    envelope = artifact.get("proofEnvelope") or {}
    memory = artifact.get("memory") or {}

    score += min(15, edge_count * 5)
    score += min(12, len([value for value in envelope.values() if value not in (None, "", [])]) * 2)
    score += min(12, len([value for value in memory.values() if value not in (None, "", [])]) * 2)

    status = str(artifact.get("status", "")).lower()
    if "mock" in status or "rd" in status:
        score -= 18
    if artifact.get("type") == "FlowPulse" and envelope.get("readerAttachedReceiptMetadata") is True:
        score += 10
    return max(0, min(100, score))


def build_agent_memory_pack(trace: dict[str, Any]) -> dict[str, Any]:
    issues = validate_trace(trace)
    counts = severity_counts(issues)
    artifacts = trace.get("artifacts") if isinstance(trace.get("artifacts"), list) else []
    edges = trace.get("edges") if isinstance(trace.get("edges"), list) else []

    edge_counts: dict[str, int] = {}
    for edge in edges:
        if isinstance(edge, dict):
            edge_counts[str(edge.get("from"))] = edge_counts.get(str(edge.get("from")), 0) + 1
            edge_counts[str(edge.get("to"))] = edge_counts.get(str(edge.get("to")), 0) + 1

    recall_cards = []
    reusable_compute = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        artifact_id = str(artifact.get("id", ""))
        card = {
            "artifactId": artifact_id,
            "artifactType": artifact.get("type"),
            "boundary": artifact.get("boundary"),
            "status": artifact.get("status"),
            "fingerprint": digest(artifact, "FlowMemoryArtifact"),
            "recallScore": artifact_score(artifact, edge_counts.get(artifact_id, 0)),
            "agentUse": agent_use_for_artifact(artifact),
        }
        recall_cards.append(card)
        if artifact.get("type") == "ComputePulse":
            reusable_compute.append(
                {
                    "artifactId": artifact_id,
                    "fingerprint": card["fingerprint"],
                    "jobId": (artifact.get("proofEnvelope") or {}).get("jobId"),
                    "modelCommitment": (artifact.get("memory") or {}).get("modelCommitment"),
                    "inputCommitment": (artifact.get("memory") or {}).get("inputCommitment"),
                    "outputCommitment": (artifact.get("memory") or {}).get("outputCommitment"),
                    "reusePolicy": "verify commitments and policy before reuse",
                }
            )

    recall_cards.sort(key=lambda item: (-int(item["recallScore"]), str(item["artifactId"])))

    return {
        "schema": PACK_SCHEMA,
        "status": pack_status(counts),
        "traceFingerprint": digest(trace, "MachineMemoryTrace"),
        "rootfieldId": trace.get("rootfieldId"),
        "summary": trace.get("summary"),
        "counts": {
            "artifacts": len(artifacts),
            "edges": len(edges),
            **counts,
        },
        "artifactTypes": sorted({artifact.get("type") for artifact in artifacts if isinstance(artifact, dict)}),
        "recallCards": recall_cards,
        "routing": {
            "reusableComputeCandidates": reusable_compute,
            "nextBestAction": next_best_action(counts, artifacts),
            "principle": "Agents should cite pulse fingerprints and proof envelopes, not vague memory text.",
        },
        "issues": issues,
    }


def pack_status(counts: dict[str, int]) -> str:
    if counts["error"]:
        return "rejected"
    if counts["warning"]:
        return "verified_with_warnings"
    if counts["info"]:
        return "verified_with_notes"
    return "verified"


def agent_use_for_artifact(artifact: dict[str, Any]) -> str:
    artifact_type = artifact.get("type")
    if artifact_type == "FlowPulse":
        return "Use as receipt-bound DeFi execution memory."
    if artifact_type == "ComputePulse":
        return "Use as compute provenance and possible reuse candidate."
    if artifact_type == "CachePulse":
        return "Use as context/KV lineage before recomputing."
    if artifact_type == "ModelPulse":
        return "Use as model-output provenance, not semantic truth by itself."
    if artifact_type == "AgentPulse":
        return "Use as an auditable agent step in a larger workflow."
    return "Use only after schema review."


def next_best_action(counts: dict[str, int], artifacts: list[Any]) -> str:
    if counts["error"]:
        return "Fix trace errors before agent use."
    has_flowpulse = any(isinstance(artifact, dict) and artifact.get("type") == "FlowPulse" for artifact in artifacts)
    has_compute = any(isinstance(artifact, dict) and artifact.get("type") == "ComputePulse" for artifact in artifacts)
    has_model = any(isinstance(artifact, dict) and artifact.get("type") == "ModelPulse" for artifact in artifacts)
    if has_flowpulse and not has_compute:
        return "Add a ComputePulse that analyzes or reacts to the FlowPulse."
    if has_compute and not has_model:
        return "Add a ModelPulse that commits the compute output."
    if has_flowpulse and has_compute and has_model:
        return "Promote this trace into a Rootflow-indexed agent memory pack."
    return "Add at least one FlowPulse or ComputePulse artifact."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build proof-carried agent memory packs from FlowMemory traces.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify = subparsers.add_parser("verify-trace", help="Validate a MachineMemoryTrace and emit an Agent Memory Pack.")
    verify.add_argument("trace", help="Path to trace JSON.")
    verify.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    verify.add_argument("--output", help="Optional output path.")

    fingerprint = subparsers.add_parser("fingerprint", help="Print the deterministic MachineMemoryTrace fingerprint.")
    fingerprint.add_argument("trace", help="Path to trace JSON.")

    return parser.parse_args()


def emit(payload: Any, pretty: bool, output: str | None = None) -> None:
    text = json.dumps(payload, indent=2 if pretty else None, sort_keys=True)
    if output:
        with open(output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    else:
        print(text)


def main() -> int:
    args = parse_args()
    trace = load_json(args.trace)
    if args.command == "verify-trace":
        pack = build_agent_memory_pack(trace)
        emit(pack, args.pretty, args.output)
        return 1 if pack["status"] == "rejected" else 0
    if args.command == "fingerprint":
        print(digest(trace, "MachineMemoryTrace"))
        return 0
    raise AssertionError(f"unknown command {args.command}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - command-line boundary
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
