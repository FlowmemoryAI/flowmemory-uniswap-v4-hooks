import unittest

from tools import public_claim_gate


class PublicClaimGateTest(unittest.TestCase):
    def test_public_claim_files_pass(self):
        report = public_claim_gate.build_report()
        self.assertEqual("pass", report["status"])
        self.assertEqual(0, report["summary"]["unguardedOverclaims"])
        self.assertGreater(report["summary"]["guardedRiskMentions"], 0)

    def test_unguarded_mainnet_claim_fails(self):
        scan = public_claim_gate.scan_lines(
            "demo.md",
            ["FlowMemory has a production Base mainnet Uniswap v4 hook."],
        )
        self.assertEqual(1, len(scan["unguardedOverclaims"]))
        self.assertEqual("live_mainnet", scan["unguardedOverclaims"][0]["risk"])

    def test_guarded_non_claim_block_passes(self):
        scan = public_claim_gate.scan_lines(
            "demo.md",
            [
                "## Do Not Claim",
                "- live Base mainnet deployment;",
                "- audited custody;",
                "- GPU hardware speedup;",
            ],
        )
        self.assertEqual([], scan["unguardedOverclaims"])
        self.assertEqual(3, len(scan["guardedRiskMentions"]))

    def test_inline_negation_passes(self):
        scan = public_claim_gate.scan_lines(
            "demo.md",
            [
                "The hook does not control swaps.",
                "No GPU acceleration.",
                "FMM-0 is not semantic truth.",
            ],
        )
        self.assertEqual([], scan["unguardedOverclaims"])
        self.assertEqual(3, len(scan["guardedRiskMentions"]))

    def test_render_report_names_result(self):
        text = public_claim_gate.render_report(public_claim_gate.build_report())
        self.assertIn("Public Claim Gate", text)
        self.assertIn("unguarded overclaims: 0", text)
        self.assertIn("Public launch copy is claim-safe.", text)


if __name__ == "__main__":
    unittest.main()
