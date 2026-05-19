import json
from pathlib import Path
import subprocess
import sys
import unittest

from tools import spendline_harness


class SpendLineHarnessTest(unittest.TestCase):
    def test_report_passes_all_cases(self):
        report = spendline_harness.build_report()
        self.assertEqual(spendline_harness.REPORT_SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(9, report["casesPassed"])
        self.assertEqual(9, report["casesTotal"])
        self.assertEqual(1, report["validSpendsAccepted"])
        self.assertEqual(1, report["validSpendsTotal"])
        self.assertEqual(8, report["unsafeSpendsRejected"])
        self.assertEqual(8, report["unsafeSpendsTotal"])
        self.assertEqual(0, report["escapedUnsafeSpends"])

    def test_valid_spend_is_accepted(self):
        result = spendline_harness.evaluate_case(spendline_harness.build_cases()[0])
        self.assertEqual("ACCEPT_SPENDLINE", result["observedDecision"])
        self.assertEqual("all_spendline_gates_passed", result["reason"])

    def test_stale_memory_head_rejected(self):
        result = spendline_harness.evaluate_case(spendline_harness.build_cases()[1])
        self.assertEqual("REJECT_SPENDLINE", result["observedDecision"])
        self.assertEqual("currentMemoryHeadMatchesLedger", result["reason"])

    def test_duplicate_intent_rejected(self):
        result = spendline_harness.evaluate_case(spendline_harness.build_cases()[2])
        self.assertEqual("REJECT_SPENDLINE", result["observedDecision"])
        self.assertEqual("intentNotReplayed", result["reason"])

    def test_hallucinated_receipt_claim_rejected_by_flowserial(self):
        result = spendline_harness.evaluate_case(spendline_harness.build_cases()[3])
        self.assertEqual("REJECT_SPENDLINE", result["observedDecision"])
        self.assertEqual("retrocausal_receipt_claim", result["reason"])

    def test_missing_post_spend_flowpulse_rejected(self):
        result = spendline_harness.evaluate_case(spendline_harness.build_cases()[4])
        self.assertEqual("REJECT_SPENDLINE", result["observedDecision"])
        self.assertEqual("postSpendFlowPulsePresent", result["reason"])

    def test_rootfield_rollback_rejected_by_flowserial(self):
        result = spendline_harness.evaluate_case(spendline_harness.build_cases()[5])
        self.assertEqual("REJECT_SPENDLINE", result["observedDecision"])
        self.assertEqual("rootfield_rollback", result["reason"])

    def test_axiompatch_downgrade_ignored_is_rejected(self):
        result = spendline_harness.evaluate_case(spendline_harness.build_cases()[6])
        self.assertEqual("REJECT_SPENDLINE", result["observedDecision"])
        self.assertEqual("axiomPatchAllowsSpendSurface", result["reason"])

    def test_x402_payment_requirement_mismatch_is_rejected(self):
        result = spendline_harness.evaluate_case(spendline_harness.build_cases()[7])
        self.assertEqual("REJECT_SPENDLINE", result["observedDecision"])
        self.assertEqual("paymentRequirementMatchesSpend", result["reason"])

    def test_compute_reuse_inconsistency_is_rejected(self):
        result = spendline_harness.evaluate_case(spendline_harness.build_cases()[8])
        self.assertEqual("REJECT_SPENDLINE", result["observedDecision"])
        self.assertEqual("computeReuseConsistentIfUsed", result["reason"])

    def test_demo_output_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/spendline_harness.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("SpendLine Harness", completed.stdout)
        self.assertIn("valid spends accepted: 1/1", completed.stdout)
        self.assertIn("unsafe spends rejected: 8/8", completed.stdout)
        self.assertIn("escaped unsafe spends: 0", completed.stdout)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/spendline_harness.py", "demo", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])

    def test_check_cli_reads_case_file(self):
        completed = subprocess.run(
            [
                sys.executable,
                "tools/spendline_harness.py",
                "check",
                "--case",
                "examples/spendline/valid_spend_after_memory_head.json",
                "--pretty",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("SPL-OK-001", completed.stdout)
        self.assertIn("ACCEPT_SPENDLINE", completed.stdout)

    def test_all_example_case_files_match_expected_decisions(self):
        for path in sorted(Path("examples/spendline").glob("*.json")):
            with self.subTest(path=str(path)):
                case = spendline_harness.read_json(path)
                result = spendline_harness.evaluate_case(case)
                self.assertEqual("PASS", result["status"])

    def test_nonclaims_are_present(self):
        report = spendline_harness.build_report()
        for claim in spendline_harness.NON_CLAIMS:
            self.assertIn(claim, report["notClaims"])

    def test_rendered_output_avoids_banned_claims(self):
        text = spendline_harness.render_report(spendline_harness.build_report()).lower()
        for phrase in spendline_harness.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
