import copy
import unittest

from tools import pulse_retire


ROOTFIELD = "0x" + "1" * 64
COMMITMENT = "0x" + "2" * 64
POOL_ID = "0x" + "3" * 64
HOOK = "0x0000000000000000000000000000000000000001"


def queue(rootfield: str = ROOTFIELD) -> dict:
    return pulse_retire.create_queue("demo-agent", rootfield)


def artifact(
    artifact_id: str = "model-output-001",
    commitment: str = COMMITMENT,
    rootfield: str = ROOTFIELD,
    hook: str = HOOK,
    pool: str = POOL_ID,
) -> dict:
    return {
        "artifactId": artifact_id,
        "artifactType": "ModelPulseDraft",
        "artifactCommitment": "sha256:model-output",
        "expectedPulse": {
            "boundary": "uniswap_v4_afterSwap",
            "rootfieldId": rootfield,
            "commitment": commitment,
            "hookAddress": hook,
            "subjectPoolId": pool,
            "parentPulseId": "0x" + "0" * 64,
        },
        "onRetire": ["release_model_output", "allow_as_live_context"],
        "onSquash": ["withhold_model_output", "require_fresh_compute"],
    }


def evidence(
    commitment: str = COMMITMENT,
    rootfield: str = ROOTFIELD,
    hook: str = HOOK,
    pool: str = POOL_ID,
    tx_hash: str | None = "0x" + "a" * 64,
    log_index: str | None = "7",
    receipt_status: str = "success",
) -> dict:
    record = {
        "eventName": "FlowPulse",
        "chainId": "84532",
        "hookAddress": hook,
        "txHash": tx_hash,
        "logIndex": log_index,
        "blockNumber": "123456",
        "receiptStatus": receipt_status,
        "rootfieldId": rootfield,
        "commitment": commitment,
        "subjectPoolId": pool,
        "parentPulseId": "0x" + "0" * 64,
        "validation": [],
    }
    return {"schema": "flowmemory.hook_log_reader.v0", "records": [record]}


class PulseRetireTest(unittest.TestCase):
    def test_queue_id_is_deterministic_and_rootfield_sensitive(self):
        self.assertEqual(queue()["queueId"], queue()["queueId"])
        self.assertNotEqual(queue()["queueId"], queue("0x" + "9" * 64)["queueId"])
        self.assertEqual("valid", pulse_retire.verify_queue(queue())["status"])

    def test_enqueue_rejects_receipt_fields(self):
        for key in ["txHash", "logIndex", "transactionIndex", "blockHash"]:
            bad = artifact()
            bad[key] = "forbidden"
            with self.assertRaises(ValueError):
                pulse_retire.enqueue_artifact(queue(), bad)

    def test_enqueue_rejects_receipt_fields_inside_expected_pulse(self):
        bad = artifact()
        bad["expectedPulse"]["txHash"] = "0x" + "a" * 64
        with self.assertRaises(ValueError):
            pulse_retire.enqueue_artifact(queue(), bad)

    def test_entry_id_is_deterministic(self):
        first = pulse_retire.enqueue_artifact(queue(), artifact())
        second = pulse_retire.enqueue_artifact(queue(), artifact())
        self.assertEqual(first["entries"][0]["entryId"], second["entries"][0]["entryId"])

    def test_matching_flowpulse_retires_artifact(self):
        queued = pulse_retire.enqueue_artifact(queue(), artifact())
        updated, report = pulse_retire.retire_queue(queued, evidence())

        self.assertEqual("retired", report["status"])
        self.assertEqual("live", updated["entries"][0]["artifactState"])
        self.assertTrue(updated["entries"][0]["causalNonce"].startswith("sha256:"))
        self.assertEqual("valid", pulse_retire.verify_retirement(report)["status"])

    def test_missing_tx_hash_keeps_artifact_speculative(self):
        queued = pulse_retire.enqueue_artifact(queue(), artifact())
        updated, report = pulse_retire.retire_queue(queued, evidence(tx_hash=None))

        self.assertEqual("immature", report["status"])
        self.assertEqual("speculative", updated["entries"][0]["artifactState"])

    def test_missing_log_index_keeps_artifact_speculative(self):
        queued = pulse_retire.enqueue_artifact(queue(), artifact())
        updated, report = pulse_retire.retire_queue(queued, evidence(log_index=None))

        self.assertEqual("immature", report["status"])
        self.assertEqual("speculative", updated["entries"][0]["artifactState"])

    def test_failed_receipt_squashes_artifact(self):
        queued = pulse_retire.enqueue_artifact(queue(), artifact())
        updated, report = pulse_retire.retire_queue(queued, evidence(receipt_status="reverted"))

        self.assertEqual("squashed", report["status"])
        self.assertEqual("squashed", updated["entries"][0]["artifactState"])
        self.assertIn("receiptStatusSuccess", report["retirements"][0]["squashReasons"])

    def test_mismatches_squash_artifact(self):
        cases = [
            ("commitment", evidence(commitment="0x" + "9" * 64), "commitmentMatches"),
            ("rootfield", evidence(rootfield="0x" + "9" * 64), "rootfieldMatches"),
            ("hook", evidence(hook="0x0000000000000000000000000000000000000009"), "hookAddressMatches"),
            ("pool", evidence(pool="0x" + "9" * 64), "subjectPoolMatches"),
        ]
        for _, bad_evidence, reason in cases:
            queued = pulse_retire.enqueue_artifact(queue(), artifact())
            updated, report = pulse_retire.retire_queue(queued, bad_evidence)
            self.assertEqual("squashed", report["status"])
            self.assertEqual("squashed", updated["entries"][0]["artifactState"])
            self.assertIn(reason, report["retirements"][0]["squashReasons"])

    def test_generic_api_log_cannot_retire(self):
        queued = pulse_retire.enqueue_artifact(queue(), artifact())
        updated, report = pulse_retire.retire_queue(queued, {"records": [{"eventName": "ApiLog"}]})

        self.assertEqual("immature", report["status"])
        self.assertEqual("speculative", updated["entries"][0]["artifactState"])

    def test_causal_nonce_is_absent_before_retirement_and_present_after(self):
        queued = pulse_retire.enqueue_artifact(queue(), artifact())
        self.assertNotIn("causalNonce", queued["entries"][0])
        updated, _ = pulse_retire.retire_queue(queued, evidence())
        self.assertTrue(updated["entries"][0]["causalNonce"].startswith("sha256:"))

    def test_in_order_blocks_later_entry_if_head_is_pending(self):
        queued = pulse_retire.enqueue_artifact(queue(), artifact("head", commitment="0x" + "8" * 64))
        queued = pulse_retire.enqueue_artifact(queued, artifact("second"))
        updated, report = pulse_retire.retire_queue(queued, evidence(tx_hash=None))

        self.assertEqual("immature", report["status"])
        self.assertEqual("speculative", updated["entries"][0]["artifactState"])
        self.assertEqual("speculative", updated["entries"][1]["artifactState"])

    def test_squashed_head_allows_later_entry_to_retire(self):
        queued = pulse_retire.enqueue_artifact(queue(), artifact("head", commitment="0x" + "8" * 64))
        queued = pulse_retire.enqueue_artifact(queued, artifact("second"))
        updated, report = pulse_retire.retire_queue(queued, evidence())

        self.assertEqual("squashed", report["status"])
        self.assertEqual("squashed", updated["entries"][0]["artifactState"])
        self.assertEqual("live", updated["entries"][1]["artifactState"])

    def test_enforce_allows_only_retired_artifact(self):
        queued = pulse_retire.enqueue_artifact(queue(), artifact())
        self.assertFalse(pulse_retire.enforce(queued, "model-output-001")["allowed"])
        updated, _ = pulse_retire.retire_queue(queued, evidence())
        self.assertTrue(pulse_retire.enforce(updated, "model-output-001")["allowed"])
        self.assertFalse(pulse_retire.enforce(updated, "missing")["allowed"])
        squashed, _ = pulse_retire.retire_queue(queued, evidence(commitment="0x" + "9" * 64))
        self.assertFalse(pulse_retire.enforce(squashed, "model-output-001")["allowed"])

    def test_tampered_retirement_fails_verification(self):
        queued = pulse_retire.enqueue_artifact(queue(), artifact())
        _, report = pulse_retire.retire_queue(queued, evidence())
        tampered = copy.deepcopy(report)
        tampered["retirements"][0]["status"] = "squashed"
        self.assertEqual("invalid", pulse_retire.verify_retirement(tampered)["status"])

    def test_tampered_queue_entry_fails_verification(self):
        queued = pulse_retire.enqueue_artifact(queue(), artifact())
        queued["entries"][0]["artifactState"] = "live"
        self.assertEqual("invalid", pulse_retire.verify_queue(queued)["status"])


if __name__ == "__main__":
    unittest.main()
