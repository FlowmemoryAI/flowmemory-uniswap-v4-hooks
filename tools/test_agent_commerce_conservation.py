import json
from pathlib import Path
import subprocess
import sys
import unittest

from tools import agent_commerce_conservation


class AgentCommerceConservationTest(unittest.TestCase):
    def test_report_passes_all_cases(self):
        report = agent_commerce_conservation.build_report()
        self.assertEqual(agent_commerce_conservation.REPORT_SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(8, report["casesPassed"])
        self.assertEqual(8, report["casesTotal"])
        self.assertEqual(1, report["validEpisodesConserved"])
        self.assertEqual(1, report["validEpisodesTotal"])
        self.assertEqual(7, report["invalidEpisodesRejected"])
        self.assertEqual(7, report["invalidEpisodesTotal"])
        self.assertEqual(0, report["escapedInvalidEpisodes"])

    def test_valid_episode_is_conserved(self):
        result = agent_commerce_conservation.evaluate_case(agent_commerce_conservation.build_cases()[0])
        self.assertEqual("CONSERVED", result["observedDecision"])
        self.assertEqual("all_conservation_gates_passed", result["reason"])

    def test_orphan_payment_is_rejected(self):
        result = agent_commerce_conservation.evaluate_case(agent_commerce_conservation.build_cases()[1])
        self.assertEqual("REJECT_CONSERVATION", result["observedDecision"])
        self.assertEqual("allClosuresTargetObligations", result["reason"])

    def test_double_paid_obligation_is_rejected(self):
        result = agent_commerce_conservation.evaluate_case(agent_commerce_conservation.build_cases()[3])
        self.assertEqual("REJECT_CONSERVATION", result["observedDecision"])
        self.assertEqual("everyObligationClosesExactlyOnce", result["reason"])

    def test_stale_buyer_head_is_rejected(self):
        result = agent_commerce_conservation.evaluate_case(agent_commerce_conservation.build_cases()[5])
        self.assertEqual("REJECT_CONSERVATION", result["observedDecision"])
        self.assertEqual("memoryHeadsCompatible", result["reason"])

    def test_unsafe_compute_payment_is_rejected(self):
        result = agent_commerce_conservation.evaluate_case(agent_commerce_conservation.build_cases()[6])
        self.assertEqual("REJECT_CONSERVATION", result["observedDecision"])
        self.assertEqual("unsafeComputeReuseCannotClosePayment", result["reason"])

    def test_refusal_required_but_missing_is_rejected(self):
        result = agent_commerce_conservation.evaluate_case(agent_commerce_conservation.build_cases()[7])
        self.assertEqual("REJECT_CONSERVATION", result["observedDecision"])
        self.assertEqual("rejectedExchangeHasRefusal", result["reason"])

    def test_demo_output_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/agent_commerce_conservation.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Agent Commerce Conservation Lab", completed.stdout)
        self.assertIn("valid episodes conserved: 1/1", completed.stdout)
        self.assertIn("invalid episodes rejected: 7/7", completed.stdout)
        self.assertIn("escaped invalid episodes: 0", completed.stdout)
        self.assertIn("ACC-I1", completed.stdout)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/agent_commerce_conservation.py", "demo", "--json", "--pretty"],
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
                "tools/agent_commerce_conservation.py",
                "check",
                "--case",
                "examples/agent-commerce-conservation/valid_balanced_exchange.json",
                "--pretty",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("ACC-OK-001", completed.stdout)
        self.assertIn("CONSERVED", completed.stdout)

    def test_all_example_case_files_match_expected_decisions(self):
        for path in sorted(Path("examples/agent-commerce-conservation").glob("*.json")):
            with self.subTest(path=str(path)):
                case = agent_commerce_conservation.read_json(path)
                result = agent_commerce_conservation.evaluate_case(case)
                self.assertEqual("PASS", result["status"])

    def test_invariant_coverage_lists_all_invariants(self):
        report = agent_commerce_conservation.build_report()
        observed = {item["id"] for item in report["invariantCoverage"]}
        expected = {item["id"] for item in agent_commerce_conservation.INVARIANTS}
        self.assertEqual(expected, observed)

    def test_nonclaims_are_present(self):
        report = agent_commerce_conservation.build_report()
        for claim in agent_commerce_conservation.NON_CLAIMS:
            self.assertIn(claim, report["notClaims"])

    def test_rendered_output_avoids_banned_claims(self):
        text = agent_commerce_conservation.render_report(agent_commerce_conservation.build_report()).lower()
        for phrase in agent_commerce_conservation.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
