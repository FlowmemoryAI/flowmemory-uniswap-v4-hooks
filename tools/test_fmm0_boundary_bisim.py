import json
import subprocess
import sys
import unittest

from tools import fmm0_boundary_bisim


class Fmm0BoundaryBisimulationTest(unittest.TestCase):
    def test_report_checks_boundary_bisimulation(self):
        report = fmm0_boundary_bisim.build_report()
        self.assertEqual(fmm0_boundary_bisim.REPORT_SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(8, report["projectionChecks"])
        self.assertEqual(4, report["bisimulationsPreserved"])
        self.assertEqual(4, report["driftCasesRejected"])
        self.assertEqual(0, report["escaped"])

    def test_required_cases_are_present(self):
        report = fmm0_boundary_bisim.build_report()
        ids = {item["caseId"] for item in report["cases"]}
        for case_id in ["BS-001", "BS-002", "BS-003", "BS-004", "BS-005", "BS-006", "BS-007", "BS-008"]:
            self.assertIn(case_id, ids)

    def test_drift_cases_name_faults(self):
        report = fmm0_boundary_bisim.build_report()
        faults = {item["fault"] for item in report["cases"] if item["fault"]}
        self.assertIn("rootfieldId_drift", faults)
        self.assertIn("commitment_drift", faults)
        self.assertIn("runtime_receipt_drift", faults)
        self.assertIn("hook_projection_contains_receipt_metadata", faults)

    def test_demo_output_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_boundary_bisim.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Projection checks: 8", completed.stdout)
        self.assertIn("Bisimulations preserved: 4/4", completed.stdout)
        self.assertIn("Drift cases rejected: 4/4", completed.stdout)
        self.assertIn("Escaped: 0", completed.stdout)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_boundary_bisim.py", "demo", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(0, payload["escaped"])

    def test_hook_projection_has_no_receipt_metadata(self):
        hook = fmm0_boundary_bisim.hook_projection(fmm0_boundary_bisim.load_flowpulse_record())
        for field in fmm0_boundary_bisim.RECEIPT_ONLY_FIELDS:
            self.assertNotIn(field, hook)

    def test_nonclaims_avoid_overstating_bisimulation(self):
        report = fmm0_boundary_bisim.build_report()
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
        text = fmm0_boundary_bisim.render_report(fmm0_boundary_bisim.build_report()).lower()
        for phrase in fmm0_boundary_bisim.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
