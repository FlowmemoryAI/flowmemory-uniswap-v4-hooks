import copy
import unittest

from tools import axiom_patch
from tools.test_axiom_writ import ROOTFIELD, claim, evidence_record


def patch_policy():
    return {
        "verbGrantsByProofTier": {
            "receipt_bound_flowpulse": {
                "allow": ["observe_boundary_fact", "cite_boundary_fact", "propose_unsigned_action"],
                "deny": ["sign_transaction", "move_funds"],
                "downgrade": {
                    "submit_onchain_transaction": "propose_unsigned_action",
                    "claim_semantic_truth": "cite_boundary_fact_only",
                },
            }
        },
        "writPolicy": {
            "allowedVerbsByProofTier": {
                "receipt_bound_flowpulse": ["believe", "cite", "plan_with"],
            },
            "deniedVerbs": ["claim_semantic_truth", "execute_onchain_action"],
        },
    }


class AxiomPatchTest(unittest.TestCase):
    def test_mints_and_verifies_patch(self):
        patch = axiom_patch.mint_patch(evidence_record(), claim(), patch_policy(), "demo-agent")
        verification = axiom_patch.verify_patch(patch)

        self.assertEqual(patch["status"], "active")
        self.assertEqual(verification["status"], "valid")
        self.assertIn("ActionAuthorization", patch["beliefDelta"]["doesNotAdd"])
        self.assertIn("submit_onchain_transaction", patch["verbGrants"]["downgrade"])

    def test_downgrades_onchain_submission(self):
        patch = axiom_patch.mint_patch(evidence_record(), claim(), patch_policy(), "demo-agent")
        verdict = axiom_patch.apply_patch(
            patch,
            {
                "planId": "submit",
                "agentId": "demo-agent",
                "rootfieldId": ROOTFIELD,
                "requestedActions": ["submit_onchain_transaction"],
            },
        )

        self.assertEqual(verdict["decision"], "downgrade")
        self.assertEqual(verdict["downgradedActions"][0]["to"], "propose_unsigned_action")
        self.assertEqual(verdict["deniedActions"], [])

    def test_allows_boundary_citation(self):
        patch = axiom_patch.mint_patch(evidence_record(), claim(), patch_policy(), "demo-agent")
        verdict = axiom_patch.apply_patch(
            patch,
            {
                "planId": "cite",
                "agentId": "demo-agent",
                "rootfieldId": ROOTFIELD,
                "requestedActions": ["cite_boundary_fact"],
            },
        )

        self.assertEqual(verdict["decision"], "allow")
        self.assertEqual(verdict["allowedActions"], ["cite_boundary_fact"])

    def test_denies_fund_movement(self):
        patch = axiom_patch.mint_patch(evidence_record(), claim(), patch_policy(), "demo-agent")
        verdict = axiom_patch.apply_patch(
            patch,
            {
                "planId": "move",
                "agentId": "demo-agent",
                "rootfieldId": ROOTFIELD,
                "requestedActions": ["move_funds"],
            },
        )

        self.assertEqual(verdict["decision"], "deny")
        self.assertEqual(verdict["deniedActions"][0]["action"], "move_funds")

    def test_tamper_detection(self):
        patch = axiom_patch.mint_patch(evidence_record(), claim(), patch_policy(), "demo-agent")
        tampered = copy.deepcopy(patch)
        tampered["beliefDelta"]["adds"].append("ActionAuthorization")

        verification = axiom_patch.verify_patch(tampered)

        self.assertEqual(verification["status"], "invalid")
        self.assertIn("patchIdMatches", verification["failedChecks"])


if __name__ == "__main__":
    unittest.main()
