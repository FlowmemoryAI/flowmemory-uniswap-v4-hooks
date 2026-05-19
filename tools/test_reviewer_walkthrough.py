import json
import subprocess
import sys
import unittest

from tools import reviewer_walkthrough


LEDGER = "examples/reviewer-walkthrough/fmm0-claim-ledger.json"


class ReviewerWalkthroughTest(unittest.TestCase):
    def test_ledger_loads_and_has_required_claims(self):
        ledger = reviewer_walkthrough.load_ledger(LEDGER)
        self.assertEqual(reviewer_walkthrough.LEDGER_SCHEMA, ledger["schema"])
        ids = {claim["id"] for claim in ledger["claims"]}
        self.assertTrue(reviewer_walkthrough.REQUIRED_CLAIM_IDS.issubset(ids))

    def test_claim_ids_are_unique(self):
        ledger = reviewer_walkthrough.load_ledger(LEDGER)
        ids = [claim["id"] for claim in ledger["claims"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_claim_has_required_shape(self):
        ledger = reviewer_walkthrough.load_ledger(LEDGER)
        for claim in ledger["claims"]:
            self.assertIn(claim["status"], reviewer_walkthrough.ALLOWED_STATUSES)
            for field in ["id", "claim", "category", "status", "evidenceFiles", "commands", "expected", "nonClaims"]:
                self.assertIn(field, claim)

    def test_report_marks_pending_and_not_claimed_explicitly(self):
        report = reviewer_walkthrough.build_report(LEDGER, run_subprocess=False)
        verdict = report["verdict"]
        self.assertEqual("PENDING", verdict["publicBaseSepoliaReceiptEvidence"])
        self.assertEqual("NOT_CLAIMED", verdict["productionVerifierInfrastructure"])

    def test_output_contains_boundary_model(self):
        text = reviewer_walkthrough.render_text(reviewer_walkthrough.build_report(LEDGER, run_subprocess=False))
        for phrase in [
            "the swap is not the memory",
            "the transaction is the proof envelope",
            "the FlowPulse is the memory artifact",
            "the hook does not know txHash/logIndex",
            "reader/verifier attaches receipt metadata later",
        ]:
            self.assertIn(phrase, text)

    def test_output_contains_required_status_lines(self):
        text = reviewer_walkthrough.render_text(reviewer_walkthrough.build_report(LEDGER, run_subprocess=True))
        self.assertIn("Local FMM-0 consistency surface: PASS", text)
        self.assertIn("FlowLitmus forbidden outcomes: PASS", text)
        self.assertIn("Public Base Sepolia receipt evidence: PENDING", text)
        self.assertIn("Production verifier infrastructure: NOT_CLAIMED", text)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/reviewer_walkthrough.py", "--json", "--pretty", "--no-subprocess"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(reviewer_walkthrough.REPORT_SCHEMA, payload["schema"])
        self.assertEqual("PENDING", payload["verdict"]["publicBaseSepoliaReceiptEvidence"])

    def test_forbidden_overclaim_phrases_are_not_marked_pass(self):
        text = reviewer_walkthrough.render_text(reviewer_walkthrough.build_report(LEDGER, run_subprocess=True)).lower()
        for phrase in ["audited custody", "fund protection: pass", "semantic truth: pass", "model correctness guarantee", "live base mainnet: pass"]:
            self.assertNotIn(phrase, text)

    def test_markdown_render_is_deterministic(self):
        report = reviewer_walkthrough.build_report(LEDGER, run_subprocess=False)
        self.assertEqual(reviewer_walkthrough.render_markdown(report), reviewer_walkthrough.render_markdown(report))


if __name__ == "__main__":
    unittest.main()
