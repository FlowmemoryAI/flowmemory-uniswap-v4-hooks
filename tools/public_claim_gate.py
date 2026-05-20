"""Public launch copy claim gate.

This is a deterministic copy guard for the public launch surface. It does not
judge whether a claim is true in the world. It checks whether dangerous launch
claims appear only inside explicit non-claim / do-not-claim contexts.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]

PUBLIC_CLAIM_FILES = [
    "README.md",
    "CHANGELOG.md",
    "FLOWMEMORY_PUBLIC_TECHNICAL_REPORT.md",
    "docs/PUBLIC_LAUNCH_COPY.md",
    "docs/MARKETING_POSITIONING.md",
    "docs/PUBLIC_RELEASE_PATH.md",
    "docs/PUBLIC_CANARY_TEMPLATE.md",
    "docs/LAUNCH_DAY_CHECKLIST.md",
    "docs/REVIEWER_QUICKSTART.md",
    "docs/EXTERNAL_DEVELOPER_REVIEW_PACKET.md",
    "docs/AGENT_COMMERCE_MEMORY.md",
    "docs/AGENT_COMMERCE_STACK.md",
    "docs/AGENT_COMMERCE_SKEPTIC_RESPONSES.md",
    "docs/AGENT_COMMERCE_DIFFERENTIAL.md",
    "docs/LOCAL_CONFORMANCE_NOT_ENFORCEMENT.md",
    "docs/AGENT_COMMERCE_INVARIANTS.md",
    "docs/LAUNCH_REVIEW_FAQ.md",
    "docs/REPO_BOUNDARY_AND_FUTURE_RUNTIME.md",
    "docs/COMPUTE_CHARGELINE.md",
    "docs/DISCHARGELINE.md",
    "docs/SPENDLINE.md",
    "docs/DUPLEXLINE.md",
    "docs/AGENT_COMMERCE_CONSERVATION.md",
    "docs/OBLIGATION_MEMBRANE.md",
    "docs/PRODUCTION_READINESS_ARCHITECTURE.md",
    "docs/INCIDENT_RESPONSE.md",
    "docs/SIGNER_CUSTODY_BOUNDARIES.md",
    "docs/MAINNET_CANDIDATE_GATE.md",
    "docs/SLO_OBSERVABILITY.md",
]

GUARD_START_RE = re.compile(
    r"(do not claim|do not say|not acceptable|must not say|claims not allowed|"
    r"not allowed|not allowed from this repo|what this.*does not|what .*does not prove|"
    r"does not prove|precision boundaries|false claims|avoid|non-claims|"
    r"public evidence status)",
    re.IGNORECASE,
)

NEGATION_RE = re.compile(
    r"\b(no|not|without|does not|do not|cannot|must not|is not|are not|not_claimed|pending)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RiskPattern:
    identifier: str
    pattern: re.Pattern[str]


RISK_PATTERNS = [
    RiskPattern("live_mainnet", re.compile(r"\b(live|production|verified|deployed)\s+Base mainnet\b|\bBase mainnet\b.*\b(live|production|verified|deployed)\b", re.IGNORECASE)),
    RiskPattern("audited_custody", re.compile(r"\baudited\b.*\b(custody|infrastructure|production)\b|\b(custody|infrastructure|production)\b.*\baudited\b", re.IGNORECASE)),
    RiskPattern("fund_protection", re.compile(r"\b(protects?|protected|protection|fund-safety|fund safety)\b.*\bfunds?\b|\bfunds?\b.*\b(protects?|protected|protection|guarantees?)\b", re.IGNORECASE)),
    RiskPattern("swap_control", re.compile(r"\b(controls?|control|controlling)\b.*\bswaps?\b|\bswaps?\b.*\b(controls?|control|controlling)\b", re.IGNORECASE)),
    RiskPattern("hook_time_receipt_metadata", re.compile(r"\bhook\b.*\b(knows?|has|emits?)\b.*\b(txHash|transactionIndex|logIndex)\b|\b(txHash|transactionIndex|logIndex)\b.*\b(inside|during)\b.*\bhook\b", re.IGNORECASE)),
    RiskPattern("ordinary_swaps_auto_memory", re.compile(r"\bevery ordinary Uniswap transaction automatically becomes FlowMemory\b", re.IGNORECASE)),
    RiskPattern("swap_is_memory", re.compile(r"\bswap transaction itself is (the )?memory\b|\bswap is (the )?memory\b", re.IGNORECASE)),
    RiskPattern("semantic_truth", re.compile(r"\bsemantic truth\b", re.IGNORECASE)),
    RiskPattern("model_correctness", re.compile(r"\bmodel correctness\b", re.IGNORECASE)),
    RiskPattern("gpu_speedup", re.compile(r"\bGPU (hardware )?(acceleration|speedup)\b|\bhardware speedup\b|\bmakes? GPUs? faster\b", re.IGNORECASE)),
    RiskPattern("production_verifier", re.compile(r"\bproduction verifier\b|\bverifier network is live\b", re.IGNORECASE)),
]


def is_guarded_line(line: str, guarded_block: bool) -> bool:
    lowered = line.lower()
    if guarded_block:
        return True
    if NEGATION_RE.search(lowered):
        return True
    return False


def scan_lines(path: str, lines: Iterable[str]) -> dict:
    issues = []
    guarded_hits = []
    guarded_block = False
    paragraph_guard = False

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if not stripped:
            paragraph_guard = False
            continue

        if stripped.startswith("#"):
            guarded_block = bool(GUARD_START_RE.search(stripped))
            paragraph_guard = False
        elif GUARD_START_RE.search(stripped):
            guarded_block = True
            paragraph_guard = True

        line_guarded = is_guarded_line(line, guarded_block) or paragraph_guard or "?" in stripped

        for risk in RISK_PATTERNS:
            if not risk.pattern.search(line):
                continue

            hit = {
                "path": path,
                "line": line_number,
                "risk": risk.identifier,
                "text": stripped,
            }

            if line_guarded:
                guarded_hits.append(hit)
            else:
                issues.append(hit)

        paragraph_guard = line_guarded and not stripped.startswith("- ")

    return {
        "path": path,
        "unguardedOverclaims": issues,
        "guardedRiskMentions": guarded_hits,
    }


def build_report(root: Path = ROOT, paths: Iterable[str] | None = None) -> dict:
    checked_paths = list(paths or PUBLIC_CLAIM_FILES)
    scans = []
    for relative_path in checked_paths:
        file_path = root / relative_path
        lines = file_path.read_text(encoding="utf-8").splitlines()
        scans.append(scan_lines(relative_path, lines))

    issues = [issue for scan in scans for issue in scan["unguardedOverclaims"]]
    guarded = [hit for scan in scans for hit in scan["guardedRiskMentions"]]

    return {
        "schema": "flowmemory.public-claim-gate.v0",
        "status": "pass" if not issues else "fail",
        "filesChecked": checked_paths,
        "unguardedOverclaims": issues,
        "guardedRiskMentions": guarded,
        "summary": {
            "filesChecked": len(checked_paths),
            "unguardedOverclaims": len(issues),
            "guardedRiskMentions": len(guarded),
        },
        "result": "Public launch copy is claim-safe." if not issues else "Public launch copy has unguarded overclaims.",
    }


def render_report(report: dict) -> str:
    lines = [
        "Public Claim Gate",
        "",
        "Summary:",
        f"  files checked: {report['summary']['filesChecked']}",
        f"  guarded risk mentions: {report['summary']['guardedRiskMentions']}",
        f"  unguarded overclaims: {report['summary']['unguardedOverclaims']}",
    ]

    if report["unguardedOverclaims"]:
        lines.extend(["", "Unguarded overclaims:"])
        for issue in report["unguardedOverclaims"]:
            lines.append(f"  FAIL  {issue['path']}:{issue['line']}  {issue['risk']}  {issue['text']}")

    lines.extend(["", "Result:", f"  {report['result']}"])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check public launch copy for unguarded overclaims.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--pretty", action="store_true", help="Print human-readable output.")
    parser.add_argument("--path", action="append", dest="paths", help="Relative path to scan. Can be repeated.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(paths=args.paths)
    if args.json and not args.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_report(report))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
