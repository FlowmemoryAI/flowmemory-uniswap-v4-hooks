import json
import subprocess
import sys
import unittest

from tools import fmm0_counterexample_forge


class Fmm0CounterexampleForgeTest(unittest.TestCase):
    def test_report_catches_all_counterexamples(self):
        report = fmm0_counterexample_forge.build_report()
        self.assertEqual(fmm0_counterexample_forge.RESULT_SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(12, report["generatedCounterexamples"])
        self.assertEqual(12, report["caughtByFmm0"])
        self.assertEqual(0, report["uncaught"])
        self.assertEqual(0, report["escaped"])

    def test_required_counterexamples_exist(self):
        report = fmm0_counterexample_forge.build_report()
        ids = {item["caseId"] for item in report["cases"]}
        for case_id in [
            "CE-001",
            "CE-002",
            "CE-003",
            "CE-004",
            "CE-005",
            "CE-006",
            "CE-007",
            "CE-008",
            "CE-009",
            "CE-010",
            "CE-011",
            "CE-012",
        ]:
            self.assertIn(case_id, ids)

    def test_counterexamples_cover_receipt_smuggling_and_overclaiming(self):
        report = fmm0_counterexample_forge.build_report()
        faults = {fault for item in report["cases"] for fault in item["observedFaults"]}
        self.assertIn("receipt_field_smuggled_before_reader_attachment", faults)
        self.assertIn("operation_forbidden_in_phase", faults)
        self.assertIn("missing_reader_derived_receipt_metadata", faults)
        self.assertIn("missing_fmm0_consistency_checks", faults)
        self.assertIn("rootfield_or_commitment_mismatch", faults)

    def test_demo_output_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_counterexample_forge.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Generated counterexamples: 12", completed.stdout)
        self.assertIn("Caught by FMM-0: 12/12", completed.stdout)
        self.assertIn("Escaped: 0", completed.stdout)
        self.assertIn("Result: FMM-0 is not just a claim; it has adversarial counterexamples.", completed.stdout)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_counterexample_forge.py", "demo", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(0, payload["uncaught"])

    def test_generate_writes_report_and_cases(self):
        out_dir = "examples/fmm0-counterexample-forge/generated.tmp"
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_counterexample_forge.py", "generate", "--out", out_dir, "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Wrote 12 counterexamples", completed.stdout)
        from pathlib import Path

        root = Path("examples/fmm0-counterexample-forge/generated.tmp")
        try:
            self.assertTrue((root / "report.json").exists())
            self.assertTrue((root / "cases" / "CE-012.json").exists())
        finally:
            for path in sorted(root.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            if root.exists():
                root.rmdir()

    def test_nonclaims_avoid_overstating_counterexamples(self):
        report = fmm0_counterexample_forge.build_report()
        for claim in [
            "not_semantic_truth",
            "not_model_correctness",
            "not_gpu_acceleration",
            "not_custody",
            "not_fund_protection",
            "not_base_mainnet",
            "not_production_verifier_infrastructure",
        ]:
            self.assertIn(claim, report["notClaims"])

    def test_rendered_output_avoids_banned_claims(self):
        text = fmm0_counterexample_forge.render_report(fmm0_counterexample_forge.build_report()).lower()
        for phrase in fmm0_counterexample_forge.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
