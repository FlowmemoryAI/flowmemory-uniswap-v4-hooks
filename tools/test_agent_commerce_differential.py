import json
import subprocess
import sys
import unittest

from tools import agent_commerce_differential


class AgentCommerceDifferentialTest(unittest.TestCase):
    def test_report_passes_all_cases(self):
        report = agent_commerce_differential.build_report()
        self.assertEqual(agent_commerce_differential.REPORT_SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(10, report["casesChecked"])
        self.assertEqual(1, report["validCasesAcceptedByBoth"])
        self.assertEqual(1, report["validCasesTotal"])
        self.assertEqual(9, report["differentialFailuresCaught"])
        self.assertEqual(9, report["differentialFailuresTotal"])
        self.assertEqual(9, report["unsafeHistoriesAcceptedByOrdinaryBaselineOnly"])
        self.assertEqual(0, report["escapedUnsafeHistories"])

    def test_case_ids_unique(self):
        cases = agent_commerce_differential.build_cases()
        ids = [case["caseId"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))

    def test_valid_case_accepted_by_both(self):
        result = agent_commerce_differential.evaluate_case(agent_commerce_differential.build_cases()[0])
        self.assertEqual("ACCEPT", result["ordinaryRailDecision"])
        self.assertEqual("ACCEPT", result["flowmemoryDecision"])

    def test_valid_signature_stale_memory_rejected_by_fmm0(self):
        result = agent_commerce_differential.evaluate_case(agent_commerce_differential.build_cases()[1])
        self.assertEqual("ACCEPT", result["ordinaryRailDecision"])
        self.assertEqual("REJECT", result["flowmemoryDecision"])
        self.assertIn("stale_rootfield_head", result["faults"])

    def test_x402_payment_wrong_obligation_rejected_by_fmm0(self):
        result = agent_commerce_differential.evaluate_case(agent_commerce_differential.build_cases()[2])
        self.assertIn("obligation_receipt_mismatch", result["faults"])

    def test_identity_valid_payee_spine_broken_rejected_by_fmm0(self):
        result = agent_commerce_differential.evaluate_case(agent_commerce_differential.build_cases()[3])
        self.assertIn("payee_spine_broken", result["faults"])

    def test_spend_permission_duplicate_intent_rejected_by_fmm0(self):
        result = agent_commerce_differential.evaluate_case(agent_commerce_differential.build_cases()[4])
        self.assertIn("duplicate_intent_commitment", result["faults"])

    def test_cache_fingerprint_memory_inconsistent_rejected_by_fmm0(self):
        result = agent_commerce_differential.evaluate_case(agent_commerce_differential.build_cases()[5])
        self.assertIn("source_artifact_not_fmm0_conforming", result["faults"])

    def test_indexer_receipt_missing_post_spend_flowpulse_rejected_by_fmm0(self):
        result = agent_commerce_differential.evaluate_case(agent_commerce_differential.build_cases()[6])
        self.assertIn("missing_post_spend_flowpulse", result["faults"])

    def test_session_key_axiompatch_downgrade_rejected_by_fmm0(self):
        result = agent_commerce_differential.evaluate_case(agent_commerce_differential.build_cases()[7])
        self.assertIn("axiompatch_downgrade_ignored", result["faults"])

    def test_compute_payment_route_mismatch_rejected_by_fmm0(self):
        result = agent_commerce_differential.evaluate_case(agent_commerce_differential.build_cases()[8])
        self.assertIn("compute_route_discharge_mismatch", result["faults"])

    def test_child_refusal_swallowed_rejected_by_fmm0(self):
        result = agent_commerce_differential.evaluate_case(agent_commerce_differential.build_cases()[9])
        self.assertIn("child_refusal_not_propagated", result["faults"])

    def test_all_differential_cases_have_ordinary_accept_and_fmm0_reject(self):
        for case in agent_commerce_differential.build_cases()[1:]:
            with self.subTest(case=case["caseId"]):
                result = agent_commerce_differential.evaluate_case(case)
                self.assertTrue(result["differential"])
                self.assertEqual("ACCEPT", result["ordinaryRailDecision"])
                self.assertEqual("REJECT", result["flowmemoryDecision"])

    def test_json_output_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/agent_commerce_differential.py", "demo", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])

    def test_pretty_output_deterministic(self):
        completed = subprocess.run(
            [sys.executable, "tools/agent_commerce_differential.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Agent Commerce Differential Harness", completed.stdout)
        self.assertIn("valid cases accepted by both: 1/1", completed.stdout)
        self.assertIn("differential failures caught by FlowMemory: 9/9", completed.stdout)
        self.assertIn("escaped unsafe histories: 0", completed.stdout)

    def test_case_manifest_loads(self):
        completed = subprocess.run(
            [
                sys.executable,
                "tools/agent_commerce_differential.py",
                "run",
                "--cases",
                "examples/agent-commerce-differential/differential-cases.json",
                "--pretty",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("differential failures caught by FlowMemory: 9/9", completed.stdout)

    def test_no_banned_claims_in_rendered_output(self):
        text = agent_commerce_differential.render_report(agent_commerce_differential.build_report()).lower()
        for phrase in agent_commerce_differential.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)

    def test_nonclaims_are_present(self):
        report = agent_commerce_differential.build_report()
        for claim in agent_commerce_differential.NON_CLAIMS:
            self.assertIn(claim, report["notClaims"])


if __name__ == "__main__":
    unittest.main()
