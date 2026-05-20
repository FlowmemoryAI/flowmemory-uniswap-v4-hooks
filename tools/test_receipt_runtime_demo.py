import json
import subprocess
import sys
import unittest

from tools import receipt_runtime_demo


class ReceiptRuntimeDemoTest(unittest.TestCase):
    def test_demo_passes_and_selects_private_bonded_provider(self):
        report = receipt_runtime_demo.build_report()
        self.assertEqual(receipt_runtime_demo.SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual("provider.private-bonded", report["selectedRoute"])
        self.assertEqual("ALLOW", report["pulsePermitVerdict"]["status"])
        self.assertEqual("OUTCOME_SETTLED", report["outcomePulse"]["status"])

    def test_stale_memory_head_denies_permit(self):
        report = receipt_runtime_demo.build_report(current_memory_head="pulse.old")
        self.assertEqual("fail", report["status"])
        self.assertEqual("DENY", report["pulsePermitVerdict"]["status"])
        self.assertIn("stale_memory_head", report["pulsePermitVerdict"]["reasons"])

    def test_action_intent_mismatch_denies_permit(self):
        policy = receipt_runtime_demo.build_policy_card()
        action = receipt_runtime_demo.build_action_intent(policy)
        permit = receipt_runtime_demo.issue_pulse_permit(policy, action)
        tampered = dict(action)
        tampered["actionIntentHash"] = "sha256:tampered"
        verdict = receipt_runtime_demo.evaluate_pulse_permit(
            policy,
            permit,
            tampered,
            policy["requiredMemoryHead"],
        )
        self.assertEqual("DENY", verdict["status"])
        self.assertIn("action_intent_hash_mismatch", verdict["reasons"])

    def test_cheapest_provider_loses_when_not_bonded(self):
        report = receipt_runtime_demo.build_report()
        cheap = next(
            item
            for item in report["routeScore"]["candidates"]
            if item["providerId"] == "provider.cheap-unbonded"
        )
        self.assertEqual("ROUTE_REJECTED", cheap["status"])
        self.assertIn("missing_required_provider_bond", cheap["reasons"])
        self.assertNotEqual("provider.cheap-unbonded", report["selectedRoute"])

    def test_pulsepass_hides_provider_and_txhash(self):
        report = receipt_runtime_demo.build_report()
        disclosure = report["pulsePassClaim"]["disclosure"]
        self.assertEqual("hidden", disclosure["providerId"])
        self.assertEqual("hidden", disclosure["txHash"])
        self.assertEqual("revealed", disclosure["predicate"])

    def test_cli_text_output_is_review_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/receipt_runtime_demo.py", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FlowMemory Receipt Runtime Demo", completed.stdout)
        self.assertIn("status: PASS", completed.stdout)
        self.assertIn("Selected route: provider.private-bonded", completed.stdout)
        self.assertIn("Receipt-bound memory gated the action", completed.stdout)

    def test_cli_json_output_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/receipt_runtime_demo.py", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual("provider.private-bonded", payload["selectedRoute"])


if __name__ == "__main__":
    unittest.main()

