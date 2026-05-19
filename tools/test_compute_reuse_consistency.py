import json
import subprocess
import sys
import unittest

from tools import compute_reuse_consistency


class ComputeReuseConsistencyTest(unittest.TestCase):
    def test_report_passes_all_cases(self):
        report = compute_reuse_consistency.build_report()
        self.assertEqual(compute_reuse_consistency.REPORT_SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(5, report["casesPassed"])
        self.assertEqual(5, report["casesTotal"])
        self.assertEqual(4, report["unsafeReuseBlocked"])
        self.assertEqual(4, report["unsafeReuseTotal"])

    def test_safe_case_accepts_reuse(self):
        result = compute_reuse_consistency.evaluate_case(compute_reuse_consistency.build_cases()[0])
        self.assertEqual("ACCEPT_REUSE", result["observedDecision"])
        self.assertEqual("all_consistency_gates_passed", result["reason"])

    def test_cache_drift_blocks_reuse(self):
        result = compute_reuse_consistency.evaluate_case(compute_reuse_consistency.build_cases()[1])
        self.assertEqual("BLOCK_CACHE_REUSE", result["observedDecision"])
        self.assertIn("tokenizerCommitmentMatches", result["reason"])

    def test_compute_drift_requires_gpu_job(self):
        result = compute_reuse_consistency.evaluate_case(compute_reuse_consistency.build_cases()[2])
        self.assertEqual("RUN_GPU_JOB", result["observedDecision"])
        self.assertIn("runtimeCommitmentMatches", result["reason"])

    def test_retrocausal_history_blocks_reuse(self):
        result = compute_reuse_consistency.evaluate_case(compute_reuse_consistency.build_cases()[3])
        self.assertEqual("BLOCK_IMPOSSIBLE_HISTORY", result["observedDecision"])
        self.assertEqual("retrocausal_receipt_claim", result["reason"])

    def test_attestation_requirement_blocks_cache_reuse(self):
        result = compute_reuse_consistency.evaluate_case(compute_reuse_consistency.build_cases()[4])
        self.assertEqual("BLOCK_CACHE_REUSE", result["observedDecision"])
        self.assertIn("attestationSatisfied", result["reason"])

    def test_demo_output_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/compute_reuse_consistency.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Compute Reuse Consistency Harness", completed.stdout)
        self.assertIn("cases passed: 5/5", completed.stdout)
        self.assertIn("unsafe reuse blocked: 4/4", completed.stdout)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/compute_reuse_consistency.py", "demo", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])

    def test_nonclaims_are_present(self):
        report = compute_reuse_consistency.build_report()
        for claim in compute_reuse_consistency.NON_CLAIMS:
            self.assertIn(claim, report["notClaims"])

    def test_rendered_output_avoids_banned_claims(self):
        text = compute_reuse_consistency.render_report(compute_reuse_consistency.build_report()).lower()
        for phrase in compute_reuse_consistency.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
