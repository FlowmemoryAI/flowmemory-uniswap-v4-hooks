import json
import subprocess
import sys
import unittest

from tools import launch_reality_check


class LaunchRealityCheckTest(unittest.TestCase):
    def test_no_subprocess_mode_runs(self):
        report = launch_reality_check.build_report(run_litmus=False)
        self.assertEqual("pass", report["status"])
        self.assertTrue(report["warnings"])

    def test_output_includes_hard_boundary_lines(self):
        text = launch_reality_check.render_report(launch_reality_check.build_report(run_litmus=False))
        for phrase in ["swap != memory", "transaction = proof envelope", "FlowPulse = memory artifact", "hook does not know txHash/logIndex"]:
            self.assertIn(phrase, text)

    def test_output_includes_non_claims(self):
        text = launch_reality_check.render_report(launch_reality_check.build_report(run_litmus=False))
        for phrase in ["no custody", "no swap control", "no semantic truth", "no model correctness", "no GPU acceleration"]:
            self.assertIn(phrase, text)

    def test_output_includes_flowserial_and_flowlitmus(self):
        text = launch_reality_check.render_report(launch_reality_check.build_report(run_litmus=False))
        self.assertIn("FlowSerial", text)
        self.assertIn("FlowLitmus", text)
        self.assertIn("FMM-0 Phase Space", text)
        self.assertIn("FMM-0 Counterexample Forge", text)
        self.assertIn("FMM-0 Closure Lab", text)
        self.assertIn("FMM-0 Boundary Bisimulation", text)
        self.assertIn("FMM-0 Forbidden Core Extractor", text)
        self.assertIn("FMM-0 Witness Pack", text)

    def test_output_includes_litmus_case_ids_when_suite_runs(self):
        text = launch_reality_check.render_report(launch_reality_check.build_report(run_litmus=True))
        for case_id in ["FM-LB-001", "FM-SER-001", "FM-QS-001", "FM-RT-001", "FM-FIS-001", "FM-SER-002", "FM-SER-003", "FM-OK-001"]:
            self.assertIn(case_id, text)

    def test_json_mode_returns_parseable_object(self):
        completed = subprocess.run(
            [sys.executable, "tools/launch_reality_check.py", "--json", "--no-subprocess"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(launch_reality_check.REPORT_SCHEMA, payload["schema"])
        self.assertEqual("pass", payload["status"])

    def test_missing_optional_tools_warning_not_false_pass(self):
        report = launch_reality_check.build_report(run_litmus=False)
        self.assertIn("FlowLitmus suite was not executed", report["warnings"][0])
        self.assertIsNone(report["litmus"])

    def test_script_avoids_forbidden_overclaims(self):
        text = launch_reality_check.render_report(launch_reality_check.build_report(run_litmus=True)).lower()
        for forbidden in ["mainnet deployed", "audited custody", "protects funds", "controls swaps", "semantic truth proven"]:
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
