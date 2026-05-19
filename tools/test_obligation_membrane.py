import json
from pathlib import Path
import subprocess
import sys
import unittest

from tools import obligation_membrane


class ObligationMembraneTest(unittest.TestCase):
    def test_report_passes_all_cases(self):
        report = obligation_membrane.build_report()
        self.assertEqual(obligation_membrane.REPORT_SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(10, report["chainsChecked"])
        self.assertEqual(1, report["validChainsAccepted"])
        self.assertEqual(1, report["validChainsTotal"])
        self.assertEqual(9, report["unsafeChainsRejected"])
        self.assertEqual(9, report["unsafeChainsTotal"])
        self.assertEqual(0, report["escapedUnsafeChains"])

    def test_valid_three_agent_chain_accepted(self):
        result = obligation_membrane.evaluate_case(obligation_membrane.build_cases()[0])
        self.assertEqual("MEMBRANE_ACCEPTED", result["observedDecision"])
        self.assertEqual("all_membrane_gates_passed", result["reason"])

    def test_downgraded_fmm0_requirement_rejected(self):
        result = obligation_membrane.evaluate_case(obligation_membrane.build_cases()[1])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("constraintMonotonicity", result["reason"])

    def test_fresh_compute_requirement_laundered_rejected(self):
        result = obligation_membrane.evaluate_case(obligation_membrane.build_cases()[2])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("noComputePolicyLaundering", result["reason"])

    def test_missing_child_obligation_rejected(self):
        result = obligation_membrane.evaluate_case(obligation_membrane.build_cases()[3])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("delegationLineageConserved", result["reason"])

    def test_payee_spine_broken_rejected(self):
        result = obligation_membrane.evaluate_case(obligation_membrane.build_cases()[4])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("payeeSpineIntegrity", result["reason"])

    def test_unresolved_child_obligation_closed_parent_rejected(self):
        result = obligation_membrane.evaluate_case(obligation_membrane.build_cases()[5])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("parentNotClosedOverOpenChildren", result["reason"])

    def test_child_refusal_swallowed_rejected(self):
        result = obligation_membrane.evaluate_case(obligation_membrane.build_cases()[6])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("childRefusalPropagated", result["reason"])

    def test_rootfield_drift_across_delegation_rejected(self):
        result = obligation_membrane.evaluate_case(obligation_membrane.build_cases()[7])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("rootfieldFirebreak", result["reason"])

    def test_aggregate_work_omits_failed_child_rejected(self):
        result = obligation_membrane.evaluate_case(obligation_membrane.build_cases()[8])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("childRefusalPropagated", result["reason"])

    def test_semantic_truth_upgrade_rejected(self):
        result = obligation_membrane.evaluate_case(obligation_membrane.build_cases()[9])
        self.assertEqual("REJECTED", result["observedDecision"])
        self.assertEqual("noSemanticUpgrade", result["reason"])

    def test_json_output_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/obligation_membrane.py", "demo", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])

    def test_pretty_output_deterministic(self):
        completed = subprocess.run(
            [sys.executable, "tools/obligation_membrane.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Obligation Membrane", completed.stdout)
        self.assertIn("valid chains accepted: 1/1", completed.stdout)
        self.assertIn("unsafe chains rejected: 9/9", completed.stdout)
        self.assertIn("escaped unsafe chains: 0", completed.stdout)

    def test_check_cli_reads_case_file(self):
        completed = subprocess.run(
            [
                sys.executable,
                "tools/obligation_membrane.py",
                "check",
                "--case",
                "examples/obligation-membrane/valid_three_agent_compute_chain.json",
                "--pretty",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("OM-OK-001", completed.stdout)
        self.assertIn("MEMBRANE_ACCEPTED", completed.stdout)

    def test_all_example_case_files_match_expected_decisions(self):
        for path in sorted(Path("examples/obligation-membrane").glob("*.json")):
            with self.subTest(path=str(path)):
                case = obligation_membrane.read_json(path)
                result = obligation_membrane.evaluate_case(case)
                self.assertEqual("PASS", result["status"])

    def test_all_invariants_covered(self):
        report = obligation_membrane.build_report()
        observed = {item["id"] for item in report["invariantCoverage"]}
        expected = {item["id"] for item in obligation_membrane.INVARIANTS}
        self.assertEqual(expected, observed)

    def test_nonclaims_are_present(self):
        report = obligation_membrane.build_report()
        for claim in obligation_membrane.NON_CLAIMS:
            self.assertIn(claim, report["notClaims"])

    def test_no_banned_claims_in_rendered_output(self):
        text = obligation_membrane.render_report(obligation_membrane.build_report()).lower()
        for phrase in obligation_membrane.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
