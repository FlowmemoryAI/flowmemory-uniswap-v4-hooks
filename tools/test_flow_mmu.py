import copy
import unittest

from tools import flow_mmu


ROOTFIELD = "0x" + "1" * 64
COMMITMENT = "0x" + "2" * 64
POOL_ID = "0x" + "3" * 64
HOOK = "0x0000000000000000000000000000000000000001"


def table() -> dict:
    return flow_mmu.init_table("demo-agent", ROOTFIELD)


def pointer_request(**overrides) -> dict:
    virtual = {
        "boundary": "uniswap_v4_afterSwap",
        "rootfieldId": ROOTFIELD,
        "commitment": COMMITMENT,
        "hookAddress": HOOK,
        "subjectPoolId": POOL_ID,
        "parentPulseId": "0x" + "0" * 64,
    }
    virtual.update(overrides)
    return {"schema": "flowmemory.pulse_pointer_request.v0", "agentId": "demo-agent", "virtualAddress": virtual}


def evidence(**overrides) -> dict:
    record = {
        "eventName": "FlowPulse",
        "artifactType": "FlowPulse",
        "boundary": "uniswap_v4_afterSwap",
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


def allocated() -> tuple[dict, str]:
    tbl = flow_mmu.alloc_pointer(table(), pointer_request())
    return tbl, tbl["entries"][0]["pointerId"]


class FlowMMUTest(unittest.TestCase):
    def test_pointer_allocation_succeeds_without_receipt_fields(self):
        tbl, pointer_id = allocated()
        self.assertTrue(pointer_id.startswith("sha256:"))
        self.assertEqual("unmapped", tbl["entries"][0]["state"])

    def test_pointer_allocation_rejects_receipt_fields(self):
        for key in ["txHash", "logIndex", "transactionIndex", "blockHash", "receiptStatus"]:
            request = pointer_request(**{key: "forbidden"})
            with self.assertRaises(ValueError):
                flow_mmu.alloc_pointer(table(), request)

    def test_unmapped_pointer_allows_virtual_reads_only(self):
        tbl, pointer_id = allocated()
        ok = flow_mmu.deref(tbl, pointer_id, "rootfieldId")
        fault = flow_mmu.deref(tbl, pointer_id, "txHash")
        self.assertTrue(ok["allowed"])
        self.assertEqual(ROOTFIELD, ok["value"])
        self.assertEqual("flowmemory.receipt_page_fault.v0", fault["schema"])
        self.assertEqual("forbidden_pre_receipt_read", fault["faultType"])

    def test_unmapped_pointer_faults_for_log_index(self):
        tbl, pointer_id = allocated()
        fault = flow_mmu.deref(tbl, pointer_id, "logIndex")
        self.assertEqual("forbidden_pre_receipt_read", fault["faultType"])

    def test_matching_flowpulse_maps_receipt_page(self):
        tbl, pointer_id = allocated()
        mapped, page = flow_mmu.map_pointer(tbl, evidence())
        self.assertEqual("flowmemory.receipt_page.v0", page["schema"])
        self.assertEqual("mapped", mapped["entries"][0]["state"])
        self.assertEqual("valid", flow_mmu.verify_page(page)["status"])
        read = flow_mmu.deref(mapped, pointer_id, "txHash")
        self.assertTrue(read["allowed"])
        self.assertEqual("receipt_page", read["source"])

    def test_mapping_requires_reader_attached_metadata(self):
        for field in ["txHash", "logIndex"]:
            tbl, _ = allocated()
            bad = evidence(**{field: None})
            _, fault = flow_mmu.map_pointer(tbl, bad)
            self.assertEqual("missing_receipt_metadata", fault["faultType"])

    def test_failed_receipt_faults(self):
        tbl, _ = allocated()
        _, fault = flow_mmu.map_pointer(tbl, evidence(receiptStatus="reverted"))
        self.assertEqual("address_mismatch", fault["faultType"])
        self.assertIn("receiptStatusSuccess", fault["reason"])

    def test_address_mismatches_fault(self):
        cases = [
            ("commitment", evidence(commitment="0x" + "9" * 64), "commitmentMatches"),
            ("rootfield", evidence(rootfieldId="0x" + "9" * 64), "rootfieldMatches"),
            ("hook", evidence(hookAddress="0x0000000000000000000000000000000000000009"), "hookAddressMatches"),
            ("pool", evidence(subjectPoolId="0x" + "9" * 64), "subjectPoolMatches"),
        ]
        for _, bad_evidence, reason in cases:
            tbl, _ = allocated()
            _, fault = flow_mmu.map_pointer(tbl, bad_evidence)
            self.assertEqual("address_mismatch", fault["faultType"])
            self.assertIn(reason, fault["reason"])

    def test_generic_api_log_cannot_map_pointer(self):
        tbl, _ = allocated()
        _, fault = flow_mmu.map_pointer(tbl, {"records": [{"eventName": "ApiLog"}]})
        self.assertEqual("generic_log_not_mappable", fault["faultType"])

    def test_mapped_receipt_page_allows_receipt_reads_and_rejects_writes(self):
        tbl, pointer_id = allocated()
        mapped, _ = flow_mmu.map_pointer(tbl, evidence())
        self.assertTrue(flow_mmu.deref(mapped, pointer_id, "logIndex")["allowed"])
        fault = flow_mmu.write(mapped, pointer_id, "txHash", "0xdead")
        self.assertEqual("illegal_write", fault["faultType"])

    def test_page_and_fault_ids_are_deterministic(self):
        tbl, pointer_id = allocated()
        _, first_page = flow_mmu.map_pointer(tbl, evidence())
        _, second_page = flow_mmu.map_pointer(tbl, evidence())
        first_fault = flow_mmu.deref(tbl, pointer_id, "txHash")
        second_fault = flow_mmu.deref(tbl, pointer_id, "txHash")
        self.assertEqual(first_page["pageId"], second_page["pageId"])
        self.assertEqual(first_fault["faultId"], second_fault["faultId"])

    def test_tampered_receipt_page_fails_verification(self):
        tbl, _ = allocated()
        _, page = flow_mmu.map_pointer(tbl, evidence())
        tampered = copy.deepcopy(page)
        tampered["physicalAddress"]["txHash"] = "0x" + "c" * 64
        self.assertEqual("invalid", flow_mmu.verify_page(tampered)["status"])

    def test_no_semantic_claims_are_produced(self):
        tbl, _ = allocated()
        _, page = flow_mmu.map_pointer(tbl, evidence())
        rendered = flow_mmu.axiom_writ.canonical_json(page)
        self.assertNotIn("semantic truth", rendered.lower())
        self.assertTrue(page["readOnly"])


if __name__ == "__main__":
    unittest.main()
