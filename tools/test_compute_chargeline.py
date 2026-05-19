import json
from pathlib import Path
import subprocess
import sys
import unittest

from tools import compute_chargeline


class ComputeChargeLineTest(unittest.TestCase):
    def test_report_passes_all_cases(self):
        report = compute_chargeline.build_report()
        self.assertEqual(compute_chargeline.REPORT_SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(10, report["chargesChecked"])
        self.assertEqual(2, report["validChargesAccepted"])
        self.assertEqual(2, report["validChargesTotal"])
        self.assertEqual(8, report["invalidChargesRejected"])
        self.assertEqual(8, report["invalidChargesTotal"])
        self.assertEqual(0, report["escapedInvalidCharges"])

    def test_fresh_compute_charge_accepted(self):
        result = compute_chargeline.evaluate_case(compute_chargeline.build_cases()[0])
        self.assertEqual("CHARGE_ACCEPTED", result["observedDecision"])

    def test_safe_reuse_charge_accepted(self):
        result = compute_chargeline.evaluate_case(compute_chargeline.build_cases()[1])
        self.assertEqual("CHARGE_ACCEPTED", result["observedDecision"])

    def test_reuse_route_charged_as_fresh_rejected(self):
        result = compute_chargeline.evaluate_case(compute_chargeline.build_cases()[2])
        self.assertEqual("REJECT_CHARGE", result["observedDecision"])
        self.assertEqual("paymentModeMatchesRoute", result["reason"])

    def test_unsafe_reuse_charged_rejected(self):
        result = compute_chargeline.evaluate_case(compute_chargeline.build_cases()[3])
        self.assertEqual("REJECT_CHARGE", result["observedDecision"])
        self.assertEqual("unsafeReuseCannotClosePayment", result["reason"])

    def test_buyer_requires_fresh_seller_reuses_rejected(self):
        result = compute_chargeline.evaluate_case(compute_chargeline.build_cases()[4])
        self.assertEqual("REJECT_CHARGE", result["observedDecision"])
        self.assertEqual("freshPolicyNotLaundered", result["reason"])

    def test_duplicate_compute_charge_rejected(self):
        result = compute_chargeline.evaluate_case(compute_chargeline.build_cases()[5])
        self.assertEqual("REJECT_CHARGE", result["observedDecision"])
        self.assertEqual("computeChargeSingleUse", result["reason"])

    def test_missing_required_attestation_rejected(self):
        result = compute_chargeline.evaluate_case(compute_chargeline.build_cases()[6])
        self.assertEqual("REJECT_CHARGE", result["observedDecision"])
        self.assertEqual("requiredAttestationPresent", result["reason"])

    def test_runtime_drift_rejected(self):
        result = compute_chargeline.evaluate_case(compute_chargeline.build_cases()[7])
        self.assertEqual("REJECT_CHARGE", result["observedDecision"])
        self.assertEqual("runtimeCommitmentStable", result["reason"])

    def test_payment_requirement_drift_rejected(self):
        result = compute_chargeline.evaluate_case(compute_chargeline.build_cases()[8])
        self.assertEqual("REJECT_CHARGE", result["observedDecision"])
        self.assertEqual("paymentRequirementStable", result["reason"])

    def test_stale_buyer_memory_head_rejected(self):
        result = compute_chargeline.evaluate_case(compute_chargeline.build_cases()[9])
        self.assertEqual("REJECT_CHARGE", result["observedDecision"])
        self.assertEqual("buyerMemoryHeadCurrent", result["reason"])

    def test_json_output_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/compute_chargeline.py", "demo", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])

    def test_pretty_output_deterministic(self):
        completed = subprocess.run(
            [sys.executable, "tools/compute_chargeline.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Compute ChargeLine", completed.stdout)
        self.assertIn("valid charges accepted: 2/2", completed.stdout)
        self.assertIn("invalid charges rejected: 8/8", completed.stdout)
        self.assertIn("escaped invalid charges: 0", completed.stdout)

    def test_check_cli_reads_case_file(self):
        completed = subprocess.run(
            [
                sys.executable,
                "tools/compute_chargeline.py",
                "check",
                "--case",
                "examples/compute-chargeline/fresh_compute_charged_as_fresh.json",
                "--pretty",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("CCL-OK-001", completed.stdout)
        self.assertIn("CHARGE_ACCEPTED", completed.stdout)

    def test_all_example_case_files_match_expected_decisions(self):
        for path in sorted(Path("examples/compute-chargeline").glob("*.json")):
            with self.subTest(path=str(path)):
                case = compute_chargeline.read_json(path)
                result = compute_chargeline.evaluate_case(case)
                self.assertEqual("PASS", result["status"])

    def test_all_invariants_covered(self):
        report = compute_chargeline.build_report()
        observed = {item["id"] for item in report["invariantCoverage"]}
        expected = {item["id"] for item in compute_chargeline.INVARIANTS}
        self.assertEqual(expected, observed)

    def test_nonclaims_are_present(self):
        report = compute_chargeline.build_report()
        for claim in compute_chargeline.NON_CLAIMS:
            self.assertIn(claim, report["notClaims"])

    def test_no_banned_claims_in_rendered_output(self):
        text = compute_chargeline.render_report(compute_chargeline.build_report()).lower()
        for phrase in compute_chargeline.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
