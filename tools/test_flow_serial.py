import copy
import unittest

from tools import flow_serial


ROOTFIELD = "0x" + "1" * 64
ROOTFIELD_ALT = "0x" + "9" * 64
COMMITMENT = "0x" + "2" * 64
COMMITMENT_B = "0x" + "5" * 64
POOL_ID = "0x" + "3" * 64
HOOK = "0x0000000000000000000000000000000000000001"
BOUNDARY_A = "boundary-flowpulse-001"
BOUNDARY_B = "boundary-flowpulse-002"


def boundary(**overrides) -> dict:
    body = {
        "schema": flow_serial.BOUNDARY_SCHEMA,
        "boundaryId": BOUNDARY_A,
        "artifactType": "FlowPulse",
        "boundary": "uniswap_v4_afterSwap",
        "declaredOrder": 2,
        "chainId": "84532",
        "hookAddress": HOOK,
        "txHash": "0x" + "a" * 64,
        "transactionIndex": 3,
        "logIndex": 7,
        "blockNumber": 123456,
        "blockHash": "0x" + "b" * 64,
        "receiptStatus": "success",
        "rootfieldId": ROOTFIELD,
        "commitment": COMMITMENT,
        "subjectPoolId": POOL_ID,
        "parentPulseId": "0x" + "0" * 64,
    }
    body.update(overrides)
    return body


def event(event_id: str, declared_order: int, **overrides) -> dict:
    body = {
        "schema": flow_serial.EVENT_SCHEMA,
        "eventId": event_id,
        "eventType": "model_output",
        "agentId": "demo-agent",
        "rootfieldId": ROOTFIELD,
        "declaredOrder": declared_order,
        "observedBoundaries": [],
        "claimedReceiptFacts": [],
        "writes": [],
        "mustPrecede": [],
        "mustFollow": [],
        "outputCommitment": f"sha256:{event_id}",
    }
    body.update(overrides)
    return body


def history(boundaries=None, events=None, **overrides) -> dict:
    body = {
        "schema": flow_serial.HISTORY_SCHEMA,
        "historyId": "history-test",
        "agentId": "demo-agent",
        "rootfieldId": ROOTFIELD,
        "declaredConsistency": "flow_serializable",
        "boundaries": boundaries if boundaries is not None else [boundary()],
        "events": events if events is not None else [],
        "notClaims": flow_serial.non_claims(),
    }
    body.update(overrides)
    return body


class FlowSerialTest(unittest.TestCase):
    def test_valid_history_produces_certificate(self):
        doc = history(
            events=[
                event("event-draft-001", 1),
                event(
                    "event-model-output-001",
                    3,
                    observedBoundaries=[BOUNDARY_A],
                    claimedReceiptFacts=[{"field": "txHash", "boundaryId": BOUNDARY_A}, {"field": "logIndex", "boundaryId": BOUNDARY_A}],
                    writes=[{"key": "rootfieldHead", "value": BOUNDARY_A}],
                    mustFollow=[BOUNDARY_A],
                    exclusiveWriteKey="rootfield:demo:canonical_summary",
                ),
            ]
        )
        cert = flow_serial.certify(doc)
        self.assertEqual(flow_serial.CERT_SCHEMA, cert["schema"])
        self.assertEqual("serializable", cert["status"])
        self.assertEqual(["event-draft-001", BOUNDARY_A, "event-model-output-001"], [item["id"] for item in cert["serialSchedule"]])

    def test_certificate_id_is_deterministic(self):
        doc = history(events=[event("event-model-output-001", 3, observedBoundaries=[BOUNDARY_A], mustFollow=[BOUNDARY_A])])
        self.assertEqual(flow_serial.certify(doc)["certificateId"], flow_serial.certify(doc)["certificateId"])

    def test_boundary_id_is_deterministic_when_missing(self):
        first = flow_serial.ensure_boundary_id({key: value for key, value in boundary().items() if key != "boundaryId"})
        second = flow_serial.ensure_boundary_id({key: value for key, value in boundary().items() if key != "boundaryId"})
        self.assertEqual(first["boundaryId"], second["boundaryId"])
        self.assertTrue(first["boundaryId"].startswith("sha256:"))

    def test_receipt_boundary_requires_txhash_logindex_and_success(self):
        for bad_boundary in [boundary(txHash=None), boundary(logIndex=None), boundary(receiptStatus="reverted")]:
            result = flow_serial.certify(history(boundaries=[bad_boundary]))
            self.assertIn(result["faultType"], {"missing_receipt_metadata", "failed_receipt_boundary"})

    def test_generic_api_event_cannot_become_receipt_boundary(self):
        result = flow_serial.certify(history(boundaries=[boundary(artifactType="ApiLog")]))
        self.assertEqual("failed_receipt_boundary", result["faultType"])

    def test_event_cannot_claim_txhash_or_logindex_before_boundary(self):
        for field in ["txHash", "logIndex"]:
            result = flow_serial.certify(
                history(
                    events=[
                        event(
                            "event-retrocausal-output",
                            1,
                            claimedReceiptFacts=[{"field": field, "boundaryId": BOUNDARY_A}],
                            mustPrecede=[BOUNDARY_A],
                        )
                    ]
                )
            )
            self.assertEqual("retrocausal_receipt_claim", result["faultType"])

    def test_event_can_claim_receipt_facts_after_boundary(self):
        result = flow_serial.certify(
            history(
                events=[
                    event(
                        "event-post-boundary-output",
                        3,
                        observedBoundaries=[BOUNDARY_A],
                        claimedReceiptFacts=[{"field": "txHash", "boundaryId": BOUNDARY_A}, {"field": "logIndex", "boundaryId": BOUNDARY_A}],
                        mustFollow=[BOUNDARY_A],
                    )
                ]
            )
        )
        self.assertEqual("serializable", result["status"])

    def test_must_follow_and_must_precede_are_respected(self):
        before_violation = flow_serial.certify(history(events=[event("event-bad-before", 3, mustPrecede=[BOUNDARY_A])]))
        after_violation = flow_serial.certify(history(events=[event("event-bad-after", 1, mustFollow=[BOUNDARY_A])]))
        self.assertEqual("impossible_schedule", before_violation["faultType"])
        self.assertEqual("impossible_schedule", after_violation["faultType"])

    def test_contradictory_precede_follow_emits_impossible_schedule(self):
        result = flow_serial.certify(history(events=[event("event-contradiction", 3, mustPrecede=[BOUNDARY_A], mustFollow=[BOUNDARY_A])]))
        self.assertEqual("impossible_schedule", result["faultType"])

    def test_rootfield_head_may_advance(self):
        result = flow_serial.certify(history(events=[event("event-head", 3, observedBoundaries=[BOUNDARY_A], writes=[{"key": "rootfieldHead", "value": BOUNDARY_A}], mustFollow=[BOUNDARY_A])]))
        self.assertEqual("serializable", result["status"])
        self.assertEqual(BOUNDARY_A, result["rootfieldHeads"][ROOTFIELD])

    def test_rootfield_head_may_not_roll_back(self):
        result = flow_serial.certify(
            history(
                events=[
                    event("event-head", 3, observedBoundaries=[BOUNDARY_A], writes=[{"key": "rootfieldHead", "value": BOUNDARY_A}], mustFollow=[BOUNDARY_A]),
                    event("event-rollback", 4, observedBoundaries=[BOUNDARY_A], writes=[{"key": "rootfieldHead", "value": "none"}]),
                ]
            )
        )
        self.assertEqual("rootfield_rollback", result["faultType"])

    def test_exclusive_writes_with_same_head_are_accepted(self):
        result = flow_serial.certify(
            history(
                events=[
                    event("event-canonical-a", 3, observedBoundaries=[BOUNDARY_A], exclusiveWriteKey="rootfield:demo:canonical_summary", mustFollow=[BOUNDARY_A]),
                    event("event-canonical-b", 4, observedBoundaries=[BOUNDARY_A], exclusiveWriteKey="rootfield:demo:canonical_summary", mustFollow=[BOUNDARY_A]),
                ]
            )
        )
        self.assertEqual("serializable", result["status"])

    def test_incompatible_exclusive_writes_emit_split_brain(self):
        boundary_b = boundary(boundaryId=BOUNDARY_B, declaredOrder=4, txHash="0x" + "c" * 64, logIndex=8, transactionIndex=4, commitment=COMMITMENT_B)
        result = flow_serial.certify(
            history(
                boundaries=[boundary(), boundary_b],
                events=[
                    event("event-canonical-a", 3, observedBoundaries=[BOUNDARY_A], exclusiveWriteKey="rootfield:demo:canonical_summary", mustFollow=[BOUNDARY_A]),
                    event("event-canonical-b", 5, observedBoundaries=[BOUNDARY_B], exclusiveWriteKey="rootfield:demo:canonical_summary", mustFollow=[BOUNDARY_B]),
                ],
            )
        )
        self.assertEqual("split_brain_write", result["faultType"])

    def test_events_in_different_rootfields_do_not_cause_rollback_faults(self):
        boundary_b = boundary(boundaryId=BOUNDARY_B, declaredOrder=4, txHash="0x" + "c" * 64, logIndex=8, transactionIndex=4, commitment=COMMITMENT_B, rootfieldId=ROOTFIELD_ALT)
        result = flow_serial.certify(
            history(
                boundaries=[boundary(), boundary_b],
                events=[
                    event("event-root-a", 3, observedBoundaries=[BOUNDARY_A], writes=[{"key": "rootfieldHead", "value": BOUNDARY_A}], mustFollow=[BOUNDARY_A]),
                    event("event-root-b", 5, rootfieldId=ROOTFIELD_ALT, observedBoundaries=[BOUNDARY_B], writes=[{"key": "rootfieldHead", "value": BOUNDARY_B}], mustFollow=[BOUNDARY_B]),
                ],
            )
        )
        self.assertEqual("serializable", result["status"])

    def test_fault_id_is_deterministic(self):
        doc = history(events=[event("event-retrocausal-output", 1, claimedReceiptFacts=[{"field": "txHash", "boundaryId": BOUNDARY_A}], mustPrecede=[BOUNDARY_A])])
        self.assertEqual(flow_serial.certify(doc)["faultId"], flow_serial.certify(doc)["faultId"])

    def test_tampered_certificate_fails_verification(self):
        cert = flow_serial.certify(history(events=[event("event-post", 3, observedBoundaries=[BOUNDARY_A], mustFollow=[BOUNDARY_A])]))
        self.assertEqual("valid", flow_serial.verify_certificate(cert)["status"])
        tampered = copy.deepcopy(cert)
        tampered["status"] = "serializable_but_changed"
        self.assertEqual("invalid", flow_serial.verify_certificate(tampered)["status"])

    def test_outputs_do_not_claim_semantic_truth_model_correctness_or_custody(self):
        rendered_cert = flow_serial.axiom_writ.canonical_json(flow_serial.certify(history(events=[event("event-post", 3, observedBoundaries=[BOUNDARY_A], mustFollow=[BOUNDARY_A])])))
        rendered_fault = flow_serial.axiom_writ.canonical_json(
            flow_serial.certify(history(events=[event("event-retrocausal-output", 1, claimedReceiptFacts=[{"field": "txHash", "boundaryId": BOUNDARY_A}], mustPrecede=[BOUNDARY_A])]))
        )
        for rendered in [rendered_cert, rendered_fault]:
            self.assertIn("not_semantic_truth", rendered)
            self.assertIn("not_model_correctness", rendered)
            self.assertIn("not_custody", rendered)
            self.assertNotIn("protects funds", rendered.lower())
            self.assertNotIn("controls swaps", rendered.lower())

    def test_hook_time_and_receipt_time_fields_remain_separated(self):
        pre_boundary = flow_serial.certify(history(events=[event("event-pre", 1, claimedReceiptFacts=[{"field": "txHash", "boundaryId": BOUNDARY_A}], mustPrecede=[BOUNDARY_A])]))
        post_boundary = flow_serial.certify(history(events=[event("event-post", 3, claimedReceiptFacts=[{"field": "txHash", "boundaryId": BOUNDARY_A}], mustFollow=[BOUNDARY_A])]))
        self.assertEqual("retrocausal_receipt_claim", pre_boundary["faultType"])
        self.assertEqual("serializable", post_boundary["status"])


if __name__ == "__main__":
    unittest.main()
