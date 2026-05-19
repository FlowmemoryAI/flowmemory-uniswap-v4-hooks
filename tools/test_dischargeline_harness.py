import json
from pathlib import Path
import subprocess
import sys
import unittest

from tools import dischargeline_harness


class DischargeLineHarnessTest(unittest.TestCase):
    def test_report_passes_all_cases(self):
        report = dischargeline_harness.build_report()
        self.assertEqual(dischargeline_harness.REPORT_SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(12, report["dischargesChecked"])
        self.assertEqual(2, report["validDischargesAccepted"])
        self.assertEqual(2, report["validDischargesTotal"])
        self.assertEqual(10, report["invalidDischargesRejected"])
        self.assertEqual(10, report["invalidDischargesTotal"])
        self.assertEqual(0, report["escapedInvalidDischarges"])

    def test_valid_x402_work_discharge_accepted(self):
        result = dischargeline_harness.evaluate_case(dischargeline_harness.build_cases()[0])
        self.assertEqual("DISCHARGE_ACCEPTED", result["observedDecision"])

    def test_valid_compute_discharge_accepted(self):
        result = dischargeline_harness.evaluate_case(dischargeline_harness.build_cases()[1])
        self.assertEqual("DISCHARGE_ACCEPTED", result["observedDecision"])

    def test_wrong_obligation_receipt_rejected(self):
        result = dischargeline_harness.evaluate_case(dischargeline_harness.build_cases()[2])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("receiptObligationBinding", result["reason"])

    def test_wrong_recipient_discharge_rejected(self):
        result = dischargeline_harness.evaluate_case(dischargeline_harness.build_cases()[3])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("recipientMatches", result["reason"])

    def test_stale_quote_discharge_rejected(self):
        result = dischargeline_harness.evaluate_case(dischargeline_harness.build_cases()[4])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("paymentRequirementStable", result["reason"])

    def test_duplicate_discharge_rejected(self):
        result = dischargeline_harness.evaluate_case(dischargeline_harness.build_cases()[5])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("singleDischarge", result["reason"])

    def test_discharge_without_receipt_rejected(self):
        result = dischargeline_harness.evaluate_case(dischargeline_harness.build_cases()[6])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("receiptEnvelopePresent", result["reason"])

    def test_discharge_after_child_refusal_rejected(self):
        result = dischargeline_harness.evaluate_case(dischargeline_harness.build_cases()[7])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("childRefusalClosed", result["reason"])

    def test_compute_route_mismatch_discharge_rejected(self):
        result = dischargeline_harness.evaluate_case(dischargeline_harness.build_cases()[8])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("computeRouteCompatible", result["reason"])

    def test_missing_post_spend_flowpulse_rejected(self):
        result = dischargeline_harness.evaluate_case(dischargeline_harness.build_cases()[9])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("postSpendFlowPulsePresent", result["reason"])

    def test_semantic_completion_overclaim_rejected(self):
        result = dischargeline_harness.evaluate_case(dischargeline_harness.build_cases()[10])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("noSemanticCompletionUpgrade", result["reason"])

    def test_receipt_fields_in_obligation_rejected(self):
        result = dischargeline_harness.evaluate_case(dischargeline_harness.build_cases()[11])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("receiptTimeDiscipline", result["reason"])

    def test_json_output_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/dischargeline_harness.py", "demo", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])

    def test_pretty_output_deterministic(self):
        completed = subprocess.run(
            [sys.executable, "tools/dischargeline_harness.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("DischargeLine Harness", completed.stdout)
        self.assertIn("valid discharges accepted: 2/2", completed.stdout)
        self.assertIn("invalid discharges rejected: 10/10", completed.stdout)
        self.assertIn("escaped invalid discharges: 0", completed.stdout)

    def test_check_cli_reads_case_file(self):
        completed = subprocess.run(
            [
                sys.executable,
                "tools/dischargeline_harness.py",
                "check",
                "--case",
                "examples/dischargeline/valid_x402_work_discharge.json",
                "--pretty",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("DCL-OK-001", completed.stdout)
        self.assertIn("DISCHARGE_ACCEPTED", completed.stdout)

    def test_all_example_case_files_match_expected_decisions(self):
        for path in sorted(Path("examples/dischargeline").glob("*.json")):
            with self.subTest(path=str(path)):
                case = dischargeline_harness.read_json(path)
                result = dischargeline_harness.evaluate_case(case)
                self.assertEqual("PASS", result["status"])

    def test_all_invariants_covered(self):
        report = dischargeline_harness.build_report()
        observed = {item["id"] for item in report["invariantCoverage"]}
        expected = {item["id"] for item in dischargeline_harness.INVARIANTS}
        self.assertEqual(expected, observed)

    def test_nonclaims_are_present(self):
        report = dischargeline_harness.build_report()
        for claim in dischargeline_harness.NON_CLAIMS:
            self.assertIn(claim, report["notClaims"])

    def test_no_banned_claims_in_rendered_output(self):
        text = dischargeline_harness.render_report(dischargeline_harness.build_report()).lower()
        for phrase in dischargeline_harness.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
