import json
from pathlib import Path
import subprocess
import sys
import unittest

from tools import duplexline_harness


class DuplexLineHarnessTest(unittest.TestCase):
    def test_report_passes_all_cases(self):
        report = duplexline_harness.build_report()
        self.assertEqual(duplexline_harness.REPORT_SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(16, report["casesPassed"])
        self.assertEqual(16, report["casesTotal"])
        self.assertEqual(1, report["validExchangesAccepted"])
        self.assertEqual(1, report["validExchangesTotal"])
        self.assertEqual(15, report["unsafeExchangesRejected"])
        self.assertEqual(15, report["unsafeExchangesTotal"])
        self.assertEqual(0, report["escapedUnsafeExchanges"])

    def test_valid_exchange_is_accepted(self):
        result = duplexline_harness.evaluate_case(duplexline_harness.build_cases()[0])
        self.assertEqual("ACCEPT_DUPLEXLINE", result["observedDecision"])
        self.assertEqual("all_duplexline_gates_passed", result["reason"])

    def test_seller_wrong_task_is_rejected(self):
        result = duplexline_harness.evaluate_case(duplexline_harness.build_cases()[1])
        self.assertEqual("REJECT_DUPLEXLINE", result["observedDecision"])
        self.assertEqual("taskCommitmentsMatch", result["reason"])

    def test_buyer_stale_memory_head_is_rejected(self):
        result = duplexline_harness.evaluate_case(duplexline_harness.build_cases()[2])
        self.assertEqual("REJECT_DUPLEXLINE", result["observedDecision"])
        self.assertEqual("buyerMemoryHeadMatchesLedger", result["reason"])

    def test_payment_requirement_drift_is_rejected(self):
        result = duplexline_harness.evaluate_case(duplexline_harness.build_cases()[3])
        self.assertEqual("REJECT_DUPLEXLINE", result["observedDecision"])
        self.assertEqual("paymentRequirementHashMatches", result["reason"])

    def test_seller_missing_flowserial_is_rejected(self):
        result = duplexline_harness.evaluate_case(duplexline_harness.build_cases()[4])
        self.assertEqual("REJECT_DUPLEXLINE", result["observedDecision"])
        self.assertEqual("sellerWorkLineSerializable", result["reason"])

    def test_compute_reuse_inconsistency_is_rejected(self):
        result = duplexline_harness.evaluate_case(duplexline_harness.build_cases()[5])
        self.assertEqual("REJECT_DUPLEXLINE", result["observedDecision"])
        self.assertEqual("computeReuseConsistentIfUsed", result["reason"])

    def test_seller_stale_memory_head_is_rejected(self):
        result = duplexline_harness.evaluate_case(duplexline_harness.build_cases()[6])
        self.assertEqual("REJECT_DUPLEXLINE", result["observedDecision"])
        self.assertEqual("sellerMemoryHeadMatchesLedger", result["reason"])

    def test_duplicate_buyer_intent_is_rejected(self):
        result = duplexline_harness.evaluate_case(duplexline_harness.build_cases()[7])
        self.assertEqual("REJECT_DUPLEXLINE", result["observedDecision"])
        self.assertEqual("buyerSpendLineAccepted", result["reason"])

    def test_counterparty_payee_rebinding_is_rejected(self):
        result = duplexline_harness.evaluate_case(duplexline_harness.build_cases()[8])
        self.assertEqual("REJECT_DUPLEXLINE", result["observedDecision"])
        self.assertEqual("counterpartyPayeeBinding", result["reason"])

    def test_impossible_exchange_schedule_is_rejected(self):
        result = duplexline_harness.evaluate_case(duplexline_harness.build_cases()[12])
        self.assertEqual("REJECT_DUPLEXLINE", result["observedDecision"])
        self.assertEqual("exchangeScheduleAcyclic", result["reason"])

    def test_payment_receipt_smuggle_is_rejected(self):
        result = duplexline_harness.evaluate_case(duplexline_harness.build_cases()[13])
        self.assertEqual("REJECT_DUPLEXLINE", result["observedDecision"])
        self.assertEqual("noPreSettlementPaymentReceiptClaims", result["reason"])

    def test_demo_output_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/duplexline_harness.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("DuplexLine Harness", completed.stdout)
        self.assertIn("valid exchanges accepted: 1/1", completed.stdout)
        self.assertIn("unsafe exchanges rejected: 15/15", completed.stdout)
        self.assertIn("escaped unsafe exchanges: 0", completed.stdout)
        self.assertIn("DPL-I1", completed.stdout)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/duplexline_harness.py", "demo", "--json", "--pretty"],
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
                "tools/duplexline_harness.py",
                "check",
                "--case",
                "examples/duplexline/valid_buyer_seller_exchange.json",
                "--pretty",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("DPL-OK-001", completed.stdout)
        self.assertIn("ACCEPT_DUPLEXLINE", completed.stdout)

    def test_all_example_case_files_match_expected_decisions(self):
        for path in sorted(Path("examples/duplexline").glob("*.json")):
            with self.subTest(path=str(path)):
                case = duplexline_harness.read_json(path)
                result = duplexline_harness.evaluate_case(case)
                self.assertEqual("PASS", result["status"])

    def test_nonclaims_are_present(self):
        report = duplexline_harness.build_report()
        for claim in duplexline_harness.NON_CLAIMS:
            self.assertIn(claim, report["notClaims"])

    def test_invariant_coverage_lists_all_invariants(self):
        report = duplexline_harness.build_report()
        observed = {item["id"] for item in report["invariantCoverage"]}
        expected = {item["id"] for item in duplexline_harness.INVARIANTS}
        self.assertEqual(expected, observed)

    def test_rendered_output_avoids_banned_claims(self):
        text = duplexline_harness.render_report(duplexline_harness.build_report()).lower()
        for phrase in duplexline_harness.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
