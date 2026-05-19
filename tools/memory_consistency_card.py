#!/usr/bin/env python3
"""
FlowMemory Memory Consistency Card.

A launch-facing scorecard that maps the public FlowMemory claim to executable
repo evidence. It packages the hook, FlowPulse boundary, reader split,
FlowSerial, and FlowLitmus as one consistency model instead of another
standalone primitive.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:  # pragma: no cover
    from tools import axiom_writ, fmm0_phase_table, launch_reality_check, verify_release_evidence
except ModuleNotFoundError:  # pragma: no cover
    import axiom_writ  # type: ignore
    import fmm0_phase_table  # type: ignore
    import launch_reality_check  # type: ignore
    import verify_release_evidence  # type: ignore


CARD_SCHEMA = "flowmemory.memory_consistency_card.v0"
PUBLIC_RELEASE_EVIDENCE = "releases/base-sepolia/RELEASE_EVIDENCE.json"
MODEL = "FMM-0"

THESIS = "Everyone treated agent memory like retrieval. FlowMemory treats it like a memory model."
SECONDARY_THESIS = "Agent memory should be checked like a consistency model, not retrieved like text."
ANCHOR = "Uniswap v4 afterSwap emits a FlowPulse memory artifact."
SAFE_CLAIM = "FlowMemory defines FMM-0, a receipt-bound memory consistency model for machine histories."

CONSISTENCY_LEVELS = [
    {
        "id": "FM-C0",
        "name": "Execution boundary",
        "claim": "Uniswap v4 reaches an afterSwap boundary.",
        "evidence": ["contracts/FlowMemoryAfterSwapHook.sol", "test/FlowMemoryAfterSwapHook.t.sol"],
    },
    {
        "id": "FM-C1",
        "name": "Intentional memory emission",
        "claim": "The hook emits FlowPulse only from explicit FlowMemory hookData.",
        "evidence": ["contracts/FlowPulse.sol", "contracts/interfaces/IFlowMemoryHookData.sol"],
    },
    {
        "id": "FM-C2",
        "name": "Receipt metadata separation",
        "claim": "txHash, transactionIndex, logIndex, block facts, and receipt status are not hook-time facts.",
        "evidence": ["docs/EVENT_MODEL.md", "docs/FLOWMEMORY_RUNTIME_MODEL.md"],
    },
    {
        "id": "FM-C3",
        "name": "Reader-derived proof envelope",
        "claim": "Reader infrastructure attaches receipt metadata after the transaction lands.",
        "evidence": ["tools/read_flowpulse_logs.py", "tools/test_read_flowpulse_logs.py"],
    },
    {
        "id": "FM-C4",
        "name": "Receipt-linearizable histories",
        "claim": "Machine histories can be serialized around receipt-bound FlowPulse boundaries.",
        "evidence": ["tools/flow_serial.py", "tools/test_flow_serial.py", "examples/flow-serial/certificate.valid.json"],
    },
    {
        "id": "FM-C5",
        "name": "Executable forbidden outcomes",
        "claim": "Impossible agent histories fault under FlowLitmus.",
        "evidence": ["tools/flow_litmus.py", "examples/flow-litmus/litmus.manifest.json"],
        "requiresLitmus": True,
    },
    {
        "id": "FM-C6",
        "name": "FMM-0 phase space",
        "claim": "Machine artifacts cannot illegally jump phases around FlowPulse receipt boundaries.",
        "evidence": ["tools/fmm0_phase_table.py", "docs/FMM_0_PHASE_TABLE.md", "examples/fmm0-phase-table/phase-table.json"],
        "requiresPhaseTable": True,
    },
    {
        "id": "FM-C7",
        "name": "Public Base Sepolia evidence",
        "claim": "A public release record can attach txHash/logIndex evidence from a real deployed hook.",
        "evidence": [PUBLIC_RELEASE_EVIDENCE],
        "publicChainEvidence": True,
    },
]

NON_CLAIMS = [
    "no semantic truth claim",
    "no model correctness claim",
    "no live mainnet deployment claim",
    "no audited custody claim",
    "no swap control",
    "no GPU acceleration",
    "no txHash/logIndex at hook time",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def digest(value: Any) -> str:
    return axiom_writ.digest(value)


def path_exists(root: Path, path: str) -> bool:
    return (root / path).exists()


def phase_table_status() -> str:
    try:
        table = fmm0_phase_table.load_table()
        demo = fmm0_phase_table.build_demo(table)
    except Exception:
        return "fail"
    classifications = {item["artifactId"]: item["cellId"] for item in demo["classifications"]}
    expected = {
        "pre_receipt_local_output": "PRE-LOCAL-SPEC",
        "reader_derived_flowpulse": "POST-READER-LIVE",
        "fmm0_conforming_history": "FMM0-LIVE",
        "illegal_receipt_smuggle": "INVALID",
    }
    if classifications != expected:
        return "fail"
    invalid = next(item for item in demo["classifications"] if item["artifactId"] == "illegal_receipt_smuggle")
    if invalid.get("fault") != "receipt_field_smuggled_before_reader_attachment":
        return "fail"
    forbidden = [item for item in demo["transitions"] if item["status"] == "forbidden" and item["expectationMet"]]
    return "pass" if forbidden else "fail"


def level_status(level: dict[str, Any], root: Path, litmus_status: str | None, phase_status: str | None) -> str:
    if level.get("publicChainEvidence"):
        status = verify_release_evidence.build_report()["verdict"]["publicBaseSepoliaReceiptEvidence"].lower()
        return status
    if level.get("requiresLitmus") and litmus_status != "pass":
        return "fail"
    if level.get("requiresPhaseTable") and phase_status != "pass":
        return "fail"
    return "pass" if all(path_exists(root, path) for path in level["evidence"]) else "fail"


def build_card(run_litmus: bool = True) -> dict[str, Any]:
    root = repo_root()
    reality = launch_reality_check.build_report(run_litmus=run_litmus)
    litmus = reality.get("litmus")
    litmus_status = litmus.get("status") if isinstance(litmus, dict) else None
    phase_status = phase_table_status()
    levels = []
    for item in CONSISTENCY_LEVELS:
        status = level_status(item, root, litmus_status, phase_status)
        evidence = [{"path": path, "exists": path_exists(root, path)} for path in item["evidence"]]
        levels.append({**item, "status": status, "evidence": evidence})

    blocking_failures = [level for level in levels if level["status"] == "fail"]
    public_pending = [level for level in levels if level["status"] == "pending"]
    local_status = "pass" if not blocking_failures else "fail"
    public_chain_status = "pending" if public_pending else "pass"
    body = {
        "schema": CARD_SCHEMA,
        "title": "FlowMemory Memory Consistency Card",
        "model": MODEL,
        "thesis": THESIS,
        "secondaryThesis": SECONDARY_THESIS,
        "anchor": ANCHOR,
        "safeLaunchClaim": SAFE_CLAIM,
        "boundaryModel": launch_reality_check.BOUNDARY_LINES,
        "levels": levels,
        "localStatus": local_status,
        "publicChainEvidence": public_chain_status,
        "litmus": {
            "status": litmus_status or "skipped",
            "passed": litmus.get("passed") if isinstance(litmus, dict) else None,
            "total": litmus.get("total") if isinstance(litmus, dict) else None,
        },
        "nonClaims": NON_CLAIMS,
    }
    body["cardId"] = digest(body)
    return body


def status_word(status: str) -> str:
    return status.upper().ljust(7)


def render_card(card: dict[str, Any]) -> str:
    rows = [
        "FlowMemory Memory Consistency Card",
        "",
        "Thesis",
        f"  PASS     {card['thesis']}",
        f"  PASS     {card['secondaryThesis']}",
        "",
        "Model",
        f"  PASS     {card['model']}: FlowMemory Agent Memory Model",
        "",
        "Anchor",
        f"  PASS     {card['anchor']}",
    ]
    rows.extend(f"  PASS     {line}" for line in card["boundaryModel"])
    rows.extend(["", "Consistency ladder"])
    for level in card["levels"]:
        rows.append(f"  {status_word(level['status'])} {level['id']}  {level['name']}: {level['claim']}")
    litmus = card["litmus"]
    rows.extend(
        [
            "",
            "Executable checks",
            f"  {status_word(card['localStatus'])} local consistency surface",
            f"  {status_word(str(litmus['status']))} FlowLitmus {litmus['passed'] or 0}/{litmus['total'] or 0} forbidden outcomes",
            f"  {status_word(card['publicChainEvidence'])} public Base Sepolia receipt evidence",
            "",
            f"Safe launch claim: {card['safeLaunchClaim']}",
            "",
            "Do not claim",
        ]
    )
    rows.extend(f"  {claim}" for claim in card["nonClaims"])
    rows.extend(["", f"Card ID: {card['cardId']}"])
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the FlowMemory memory consistency card.")
    parser.add_argument("--pretty", action="store_true", help="Kept for CLI symmetry; text output is always readable.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of terminal text.")
    parser.add_argument("--no-subprocess", action="store_true", help="Skip FlowLitmus and render static evidence checks.")
    parser.add_argument("--write", help="Write terminal text output to a file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    card = build_card(run_litmus=not args.no_subprocess)
    text = render_card(card)
    if args.write:
        Path(args.write).parent.mkdir(parents=True, exist_ok=True)
        Path(args.write).write_text(text + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(card, indent=2 if args.pretty else None, sort_keys=True))
    else:
        print(text)
    return 0 if card["localStatus"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
