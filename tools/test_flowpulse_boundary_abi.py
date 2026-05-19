import json
import subprocess
import sys
import unittest

from tools import flowpulse_boundary_abi


class FlowPulseBoundaryAbiTest(unittest.TestCase):
    def test_report_passes(self):
        report = flowpulse_boundary_abi.build_report()
        self.assertEqual(flowpulse_boundary_abi.REPORT_SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(report["checksTotal"], report["checksPassed"])
        self.assertEqual([], report["receiptOnlyFieldsExposed"])

    def test_flowpulse_fields_match_expected_order(self):
        report = flowpulse_boundary_abi.build_report()
        self.assertEqual(
            [item["name"] for item in flowpulse_boundary_abi.EXPECTED_FLOWPULSE],
            [item["name"] for item in report["flowPulseFields"]],
        )

    def test_indexed_fields_match_boundary_identity(self):
        report = flowpulse_boundary_abi.build_report()
        indexed = {item["name"] for item in report["flowPulseFields"] if item["indexed"]}
        self.assertEqual({"pulseId", "rootfieldId", "actor"}, indexed)

    def test_receipt_only_fields_are_absent(self):
        report = flowpulse_boundary_abi.build_report()
        field_names = {item["name"] for item in report["flowPulseFields"] + report["afterSwapObservedFields"]}
        self.assertFalse(field_names & flowpulse_boundary_abi.RECEIPT_ONLY_FIELDS)

    def test_core_fields_are_present(self):
        report = flowpulse_boundary_abi.build_report()
        field_names = {item["name"] for item in report["flowPulseFields"]}
        self.assertIn("rootfieldId", field_names)
        self.assertIn("commitment", field_names)
        self.assertIn("sequence", field_names)
        self.assertIn("occurredAt", field_names)

    def test_cli_output_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/flowpulse_boundary_abi.py", "check", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("ABI checks passed:", completed.stdout)
        self.assertIn("receipt-only fields exposed: 0", completed.stdout)
        self.assertIn("status: PASS", completed.stdout)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/flowpulse_boundary_abi.py", "check", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual([], payload["receiptOnlyFieldsExposed"])

    def test_rendered_output_avoids_banned_claims(self):
        text = flowpulse_boundary_abi.render_report(flowpulse_boundary_abi.build_report()).lower()
        for phrase in flowpulse_boundary_abi.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
