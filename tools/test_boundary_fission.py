import copy
import unittest

from tools import boundary_fission


ROOTFIELD = "0x" + "1" * 64
COMMITMENT = "0x" + "2" * 64
PULSE_ID = "0x" + "3" * 64
POOL_ID = "0x" + "4" * 64
OTHER_ROOTFIELD = "0x" + "9" * 64


def evidence() -> dict:
    return {
        "schema": "flowmemory.hook_log_reader.v0",
        "chainId": "84532",
        "hookAddress": "0x0000000000000000000000000000000000000001",
        "records": [
            {
                "schema": "flowmemory.uniswap_v4_swap_signal.v0",
                "status": "l2_confirmed",
                "validation": [],
                "eventName": "FlowPulse",
                "hookAddress": "0x0000000000000000000000000000000000000001",
                "blockNumber": "123456",
                "txHash": "0x" + "a" * 64,
                "logIndex": "7",
                "receiptStatus": "success",
                "finality": {"status": "l2_confirmed", "confirmations": 24, "requiredConfirmations": 20},
                "pulseId": PULSE_ID,
                "rootfieldId": ROOTFIELD,
                "subjectPoolId": POOL_ID,
                "commitment": COMMITMENT,
                "parentPulseId": "0x" + "0" * 64,
            }
        ],
    }


def working_memory() -> dict:
    return {
        "schema": "flowmemory.agent_working_memory.v0",
        "agentId": "demo-agent",
        "rootfieldId": ROOTFIELD,
        "items": [
            {
                "memoryId": "mem-old-model-output",
                "type": "ModelPulseDraft",
                "proofTier": "local_draft",
                "createdBeforeBoundary": True,
                "rootfieldId": ROOTFIELD,
                "rawText": "The trader likely intended to accumulate exposure.",
                "containsUnsupportedIntentInference": True,
                "sourceCommitment": "sha256:old-model-output",
            },
            {
                "memoryId": "mem-cache-hint",
                "type": "CacheHint",
                "proofTier": "unverified",
                "rootfieldId": ROOTFIELD,
                "action": "reuse_compute_result",
            },
            {
                "memoryId": "mem-intent-claim",
                "type": "IntentClaim",
                "rootfieldId": ROOTFIELD,
                "claim": "Trader intended accumulation.",
            },
            {
                "memoryId": "plan-submit-swap",
                "type": "AgentPlan",
                "rootfieldId": ROOTFIELD,
                "action": "submit_onchain_transaction",
                "referencesCurrentPulse": False,
            },
            {
                "memoryId": "mem-other-rootfield",
                "type": "LocalNote",
                "rootfieldId": OTHER_ROOTFIELD,
                "rawText": "This belongs to another rootfield.",
            },
        ],
    }


class BoundaryFissionTest(unittest.TestCase):
    def test_valid_fission_splits_working_memory(self):
        report = boundary_fission.apply_boundary_fission(evidence(), working_memory(), boundary_fission.default_policy())

        self.assertEqual("active", report["status"])
        self.assertEqual("valid", boundary_fission.verify_report(report)["status"])
        products = report["releaseProducts"]
        self.assertGreaterEqual(len(products["conserved"]), 2)
        self.assertEqual(2, len(products["residueAtoms"]))
        self.assertEqual(1, len(products["quarantined"]))
        self.assertEqual(1, len(products["branchAsh"]))
        self.assertEqual(2, len(products["delegatedRecompute"]))

    def test_requires_reader_attached_tx_hash(self):
        bad = evidence()
        bad["records"][0].pop("txHash")
        report = boundary_fission.apply_boundary_fission(bad, working_memory(), boundary_fission.default_policy())

        self.assertEqual("rejected", report["status"])
        self.assertFalse(report["checks"]["txHashReaderAttached"])
        self.assertEqual("invalid", boundary_fission.verify_report(report)["status"])

    def test_requires_reader_attached_log_index(self):
        bad = evidence()
        bad["records"][0].pop("logIndex")
        report = boundary_fission.apply_boundary_fission(bad, working_memory(), boundary_fission.default_policy())

        self.assertEqual("rejected", report["status"])
        self.assertFalse(report["checks"]["logIndexReaderAttached"])

    def test_requires_successful_receipt(self):
        bad = evidence()
        bad["records"][0]["receiptStatus"] = "reverted"
        report = boundary_fission.apply_boundary_fission(bad, working_memory(), boundary_fission.default_policy())

        self.assertEqual("rejected", report["status"])
        self.assertFalse(report["checks"]["receiptStatusSuccessful"])

    def test_normal_api_log_without_receipt_cannot_trigger_active_fission(self):
        bad = {"records": [{"eventName": "FlowPulse", "rootfieldId": ROOTFIELD, "commitment": COMMITMENT}]}
        report = boundary_fission.apply_boundary_fission(bad, working_memory(), boundary_fission.default_policy())

        self.assertEqual("rejected", report["status"])
        self.assertFalse(report["checks"]["txHashReaderAttached"])

    def test_raw_model_output_does_not_survive_report(self):
        report = boundary_fission.apply_boundary_fission(evidence(), working_memory(), boundary_fission.default_policy())
        rendered = boundary_fission.axiom_writ.canonical_json(report)

        self.assertNotIn("The trader likely intended to accumulate exposure.", rendered)
        self.assertFalse(report["memoryAfter"]["rawTextPresent"])
        self.assertFalse(report["memoryAfter"]["containsRawPrivatePayload"])

    def test_rootfield_isolation_conserves_other_rootfield(self):
        report = boundary_fission.apply_boundary_fission(evidence(), working_memory(), boundary_fission.default_policy())
        conserved = report["releaseProducts"]["conserved"]

        self.assertTrue(any(item["memoryId"] == "mem-other-rootfield" for item in conserved))
        self.assertTrue(any(item["reason"] == "different_rootfield_unaffected" for item in conserved))

    def test_deterministic_fission_id(self):
        first = boundary_fission.apply_boundary_fission(evidence(), working_memory(), boundary_fission.default_policy())
        second = boundary_fission.apply_boundary_fission(evidence(), working_memory(), boundary_fission.default_policy())

        self.assertEqual(first["fissionId"], second["fissionId"])
        self.assertEqual(first["releaseProducts"]["residueAtoms"][0]["residueId"], second["releaseProducts"]["residueAtoms"][0]["residueId"])
        self.assertEqual(first["releaseProducts"]["branchAsh"][0]["branchAshId"], second["releaseProducts"]["branchAsh"][0]["branchAshId"])

    def test_tamper_detection(self):
        report = boundary_fission.apply_boundary_fission(evidence(), working_memory(), boundary_fission.default_policy())
        tampered = copy.deepcopy(report)
        tampered["releaseProducts"]["residueAtoms"][0]["releaseAction"] = "retain_raw_text"

        verification = boundary_fission.verify_report(tampered)
        self.assertEqual("invalid", verification["status"])
        self.assertIn("fissionIdMatches", verification["failedChecks"])

    def test_receipt_metadata_smuggling_is_quarantined(self):
        memory = working_memory()
        memory["items"].append(
            {
                "memoryId": "mem-smuggled-receipt",
                "type": "ModelNote",
                "rootfieldId": ROOTFIELD,
                "source": "model",
                "txHash": "0x" + "b" * 64,
                "logIndex": "9",
            }
        )
        report = boundary_fission.apply_boundary_fission(evidence(), memory, boundary_fission.default_policy())

        quarantined = report["releaseProducts"]["quarantined"]
        self.assertTrue(any(item["memoryId"] == "mem-smuggled-receipt" for item in quarantined))


if __name__ == "__main__":
    unittest.main()
