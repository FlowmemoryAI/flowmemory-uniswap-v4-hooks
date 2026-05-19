import copy
import unittest

from tools import flow_quiesce


ROOTFIELD = "0x" + "1" * 64
COMMITMENT = "0x" + "2" * 64
POOL_ID = "0x" + "3" * 64
HOOK = "0x0000000000000000000000000000000000000001"


def evidence(**overrides) -> dict:
    record = {
        "eventName": "FlowPulse",
        "chainId": "84532",
        "hookAddress": HOOK,
        "txHash": "0x" + "a" * 64,
        "logIndex": "7",
        "transactionIndex": "3",
        "blockNumber": "123456",
        "blockHash": "0x" + "b" * 64,
        "receiptStatus": "success",
        "pulseId": "0x" + "4" * 64,
        "rootfieldId": ROOTFIELD,
        "commitment": COMMITMENT,
        "subjectPoolId": POOL_ID,
        "parentPulseId": "0x" + "0" * 64,
        "validation": [],
    }
    record.update(overrides)
    return {"schema": "flowmemory.hook_log_reader.v0", "records": [record]}


def previous_epoch() -> dict:
    return {"schema": "flowmemory.receipt_epoch.v0", "epochId": "sha256:epoch-0", "epochNumber": 0, "rootfieldId": ROOTFIELD}


def frames() -> dict:
    return {
        "schema": "flowmemory.agent_frames.v0",
        "frames": [
            {
                "schema": "flowmemory.agent_frame.v0",
                "frameId": "frame-001",
                "agentId": "demo-agent",
                "frameType": "agent",
                "state": "active",
                "openedAtEpochId": "sha256:epoch-0",
                "rootfieldReads": [ROOTFIELD],
                "pendingOutputs": [{"outputId": "output-001", "type": "ModelPulseDraft", "commitment": "sha256:aaa"}],
            },
            {
                "schema": "flowmemory.agent_frame.v0",
                "frameId": "frame-002",
                "agentId": "demo-agent",
                "frameType": "gpu_workflow",
                "state": "active",
                "openedAtEpochId": "sha256:epoch-0",
                "rootfieldReads": ["0x" + "f" * 64],
                "pendingOutputs": [{"outputId": "output-002", "type": "ComputePulseDraft", "commitment": "sha256:bbb"}],
            },
            {
                "schema": "flowmemory.agent_frame.v0",
                "frameId": "frame-003",
                "agentId": "demo-agent",
                "frameType": "agent",
                "state": "quiescent",
                "openedAtEpochId": "sha256:epoch-0",
                "rootfieldReads": [ROOTFIELD],
                "pendingOutputs": [{"outputId": "output-003", "type": "ModelPulseDraft", "commitment": "sha256:ccc"}],
            },
        ],
    }


class FlowQuiesceTest(unittest.TestCase):
    def test_epoch_requires_receipt_metadata_and_success(self):
        for bad in [evidence(txHash=None), evidence(logIndex=None), evidence(receiptStatus="reverted"), {"records": [{"eventName": "ApiLog"}]}]:
            with self.assertRaises(ValueError):
                flow_quiesce.advance_epoch(bad, previous_epoch())

    def test_epoch_id_is_deterministic_and_receipt_sensitive(self):
        first = flow_quiesce.advance_epoch(evidence(), previous_epoch())
        second = flow_quiesce.advance_epoch(evidence(), previous_epoch())
        changed_tx = flow_quiesce.advance_epoch(evidence(txHash="0x" + "c" * 64), previous_epoch())
        changed_log = flow_quiesce.advance_epoch(evidence(logIndex="8"), previous_epoch())
        self.assertEqual(first["epochId"], second["epochId"])
        self.assertNotEqual(first["epochId"], changed_tx["epochId"])
        self.assertNotEqual(first["epochId"], changed_log["epochId"])

    def test_scan_selects_active_same_rootfield_only(self):
        epoch = flow_quiesce.advance_epoch(evidence(), previous_epoch())
        request = flow_quiesce.scan_frames(epoch, frames())
        required = [item["frameId"] for item in request["requiredFrames"]]
        unaffected = [item["frameId"] for item in request["unaffectedFrames"]]
        self.assertEqual(["frame-001"], required)
        self.assertIn("frame-002", unaffected)
        self.assertIn("frame-003", unaffected)
        self.assertEqual(["output-001"], request["blockedJoinUntilQuiescent"])

    def test_request_and_ack_ids_are_deterministic(self):
        epoch = flow_quiesce.advance_epoch(evidence(), previous_epoch())
        request_a = flow_quiesce.scan_frames(epoch, frames())
        request_b = flow_quiesce.scan_frames(epoch, frames())
        ack_a = flow_quiesce.ack_frame(request_a, "frame-001", "revalidated")
        ack_b = flow_quiesce.ack_frame(request_a, "frame-001", "revalidated")
        self.assertEqual(request_a["requestId"], request_b["requestId"])
        self.assertEqual(ack_a["ackId"], ack_b["ackId"])

    def test_ack_rejects_non_required_frame_and_invalid_mode(self):
        epoch = flow_quiesce.advance_epoch(evidence(), previous_epoch())
        request = flow_quiesce.scan_frames(epoch, frames())
        with self.assertRaises(ValueError):
            flow_quiesce.ack_frame(request, "frame-002", "revalidated")
        with self.assertRaises(ValueError):
            flow_quiesce.ack_frame(request, "frame-001", "invalid")

    def test_verify_ack_detects_wrong_epoch_and_tamper(self):
        epoch = flow_quiesce.advance_epoch(evidence(), previous_epoch())
        request = flow_quiesce.scan_frames(epoch, frames())
        ack = flow_quiesce.ack_frame(request, "frame-001", "revalidated")
        self.assertEqual("valid", flow_quiesce.verify_ack(ack, request)["status"])
        tampered = copy.deepcopy(ack)
        tampered["epochId"] = "sha256:wrong"
        self.assertEqual("invalid", flow_quiesce.verify_ack(tampered, request)["status"])
        tampered_id = copy.deepcopy(ack)
        tampered_id["ackMode"] = "abandoned"
        self.assertEqual("invalid", flow_quiesce.verify_ack(tampered_id, request)["status"])

    def test_certificate_open_until_all_required_frames_ack(self):
        epoch = flow_quiesce.advance_epoch(evidence(), previous_epoch())
        request = flow_quiesce.scan_frames(epoch, frames())
        open_cert = flow_quiesce.certify(request, [])
        ack = flow_quiesce.ack_frame(request, "frame-001", "revalidated")
        closed_cert = flow_quiesce.certify(request, [ack])
        self.assertEqual("grace_period_open", open_cert["status"])
        self.assertEqual(["output-001"], open_cert["unsafeOutputs"])
        self.assertEqual("grace_period_closed", closed_cert["status"])
        self.assertEqual(["output-001"], closed_cert["safeOutputs"])
        self.assertTrue(closed_cert["safeToJoinPostBoundaryState"])

    def test_gpu_frame_is_unaffected_without_gpu_attestation_claim(self):
        epoch = flow_quiesce.advance_epoch(evidence(), previous_epoch())
        request = flow_quiesce.scan_frames(epoch, frames())
        rendered = flow_quiesce.axiom_writ.canonical_json(request)
        self.assertIn("frame-002", rendered)
        self.assertNotIn("gpu attestation", rendered.lower())

    def test_no_semantic_truth_or_custody_claims(self):
        epoch = flow_quiesce.advance_epoch(evidence(), previous_epoch())
        rendered = flow_quiesce.axiom_writ.canonical_json(epoch)
        self.assertIn("not_semantic_truth", rendered)
        self.assertIn("not_custody", rendered)
        self.assertNotIn("protects funds", rendered.lower())


if __name__ == "__main__":
    unittest.main()
