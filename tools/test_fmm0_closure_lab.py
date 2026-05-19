import json
import subprocess
import sys
import unittest

from tools import fmm0_closure_lab


class Fmm0ClosureLabTest(unittest.TestCase):
    def test_report_checks_closure_laws(self):
        report = fmm0_closure_lab.build_report()
        self.assertEqual(fmm0_closure_lab.REPORT_SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(8, report["closureLawsChecked"])
        self.assertEqual(4, report["validClosuresPreserved"])
        self.assertEqual(4, report["invalidClosuresRejected"])
        self.assertEqual(0, report["escaped"])

    def test_required_laws_are_present(self):
        report = fmm0_closure_lab.build_report()
        ids = {item["caseId"] for item in report["cases"]}
        for case_id in ["CL-001", "CL-002", "CL-003", "CL-004", "CL-005", "CL-006", "CL-007", "CL-008"]:
            self.assertIn(case_id, ids)

    def test_invalid_laws_name_expected_faults(self):
        report = fmm0_closure_lab.build_report()
        faults = {item["fault"] for item in report["cases"] if item["fault"]}
        self.assertIn("rootfield_rollback", faults)
        self.assertIn("split_brain_write", faults)
        self.assertIn("receipt_field_smuggled_before_reader_attachment", faults)
        self.assertIn("operation_forbidden_in_phase", faults)

    def test_demo_output_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_closure_lab.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Closure laws checked: 8", completed.stdout)
        self.assertIn("Valid closures preserved: 4/4", completed.stdout)
        self.assertIn("Invalid closures rejected: 4/4", completed.stdout)
        self.assertIn("Escaped: 0", completed.stdout)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_closure_lab.py", "demo", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(0, payload["escaped"])

    def test_nonclaims_avoid_overstating_closure(self):
        report = fmm0_closure_lab.build_report()
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
        text = fmm0_closure_lab.render_report(fmm0_closure_lab.build_report()).lower()
        for phrase in fmm0_closure_lab.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
