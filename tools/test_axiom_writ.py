import copy
import unittest

from tools import axiom_writ


ROOTFIELD = "0x" + "11" * 32
COMMITMENT = "0x" + "22" * 32


def evidence_record(**overrides):
    record = {
        "schema": "flowmemory.uniswap_v4_swap_signal.v0",
        "status": "l2_confirmed",
        "validation": [],
        "eventName": "FlowPulse",
        "hookAddress": "0x0000000000000000000000000000000000000001",
        "blockNumber": "123456",
        "txHash": "0x" + "aa" * 32,
        "logIndex": "7",
        "receiptStatus": "success",
        "finality": {"status": "l2_confirmed", "confirmations": 24, "requiredConfirmations": 20},
        "pulseId": "0x" + "33" * 32,
        "rootfieldId": ROOTFIELD,
        "subjectPoolId": "0x" + "44" * 32,
        "commitment": COMMITMENT,
        "parentPulseId": axiom_writ.ZERO32,
    }
    record.update(overrides)
    return {
        "schema": "flowmemory.hook_log_reader.v0",
        "chainId": "84532",
        "hookAddress": "0x0000000000000000000000000000000000000001",
        "records": [record],
    }


def claim(**overrides):
    payload = {
        "claimType": "flowpulse_after_swap_boundary_observed",
        "rootfieldId": ROOTFIELD,
        "commitment": COMMITMENT,
        "statement": "A FlowPulse was emitted for this rootfield and commitment from a Uniswap v4 afterSwap boundary.",
    }
    payload.update(overrides)
    return payload


def policy():
    return {
        "allowedVerbsByProofTier": {
            "receipt_bound_flowpulse": ["believe", "cite", "reuse_context", "plan_with"],
            "receipt_attached_flowpulse": ["believe", "cite"],
        },
        "deniedVerbs": ["claim_semantic_truth", "execute_onchain_action"],
        "scope": {
            "validForRootfieldOnly": True,
            "validForAgentOnly": True,
            "expiresAt": None,
            "maxDerivedDepth": 2,
        },
    }


class AxiomWritTest(unittest.TestCase):
    def test_mints_and_verifies_active_writ(self):
        writ = axiom_writ.mint_writ(evidence_record(), claim(), policy(), "demo-agent")
        verification = axiom_writ.verify_writ(writ)

        self.assertEqual(writ["status"], "active")
        self.assertEqual(writ["proofAnchor"]["proofTier"], "receipt_bound_flowpulse")
        self.assertIn("believe", writ["allowedVerbs"])
        self.assertIn("claim_semantic_truth", writ["deniedVerbs"])
        self.assertEqual(verification["status"], "valid")

    def test_tamper_detection(self):
        writ = axiom_writ.mint_writ(evidence_record(), claim(), policy(), "demo-agent")
        tampered = copy.deepcopy(writ)
        tampered["allowedVerbs"].append("execute_onchain_action")

        verification = axiom_writ.verify_writ(tampered)

        self.assertEqual(verification["status"], "invalid")
        self.assertIn("writIdMatches", verification["failedChecks"])

    def test_rejects_missing_reader_attached_tx_hash(self):
        evidence = evidence_record(txHash="")
        writ = axiom_writ.mint_writ(evidence, claim(), policy(), "demo-agent")

        self.assertEqual(writ["status"], "rejected")
        self.assertEqual(writ["allowedVerbs"], [])
        self.assertFalse(writ["checks"]["txHashReaderAttached"])

    def test_rejects_rootfield_mismatch(self):
        writ = axiom_writ.mint_writ(evidence_record(), claim(rootfieldId="0x" + "99" * 32), policy(), "demo-agent")

        self.assertEqual(writ["status"], "rejected")
        self.assertFalse(writ["checks"]["flowPulseRecordFound"])

    def test_apply_allows_citation_and_denies_action(self):
        writ = axiom_writ.mint_writ(evidence_record(), claim(), policy(), "demo-agent")
        allowed_plan = {
            "planId": "allowed",
            "agentId": "demo-agent",
            "rootfieldId": ROOTFIELD,
            "requiredClaimHashes": [writ["claim"]["claimHash"]],
            "requestedVerbs": ["believe", "cite"],
        }
        denied_plan = {
            "planId": "denied",
            "agentId": "demo-agent",
            "rootfieldId": ROOTFIELD,
            "requiredClaimHashes": [writ["claim"]["claimHash"]],
            "requestedVerbs": ["execute_onchain_action", "claim_semantic_truth"],
        }

        allowed = axiom_writ.apply_writ(writ, allowed_plan)
        denied = axiom_writ.apply_writ(writ, denied_plan)

        self.assertTrue(allowed["allowed"])
        self.assertFalse(denied["allowed"])
        self.assertIn("execute_onchain_action", denied["deniedVerbs"])
        self.assertIn("claim_semantic_truth", denied["deniedVerbs"])


if __name__ == "__main__":
    unittest.main()
