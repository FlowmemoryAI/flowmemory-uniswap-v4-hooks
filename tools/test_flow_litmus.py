import copy
import unittest

from tools import flow_litmus


MANIFEST = "examples/flow-litmus/litmus.manifest.json"


def load_case(case_id: str) -> dict:
    manifest = flow_litmus.read_suite(MANIFEST)
    match = next(path for path in manifest["cases"] if case_id in path)
    return flow_litmus.read_json(flow_litmus.resolve_path(match))


class FlowLitmusTest(unittest.TestCase):
    def test_loads_manifest_and_all_case_files(self):
        manifest = flow_litmus.read_suite(MANIFEST)
        self.assertEqual(flow_litmus.SUITE_SCHEMA, manifest["schema"])
        self.assertEqual(8, len(manifest["cases"]))
        for path in manifest["cases"]:
            case = flow_litmus.read_json(flow_litmus.resolve_path(path))
            self.assertEqual(flow_litmus.CASE_SCHEMA, case["schema"])

    def test_rejects_case_missing_case_id(self):
        case = load_case("FM-OK-001")
        case.pop("caseId")
        with self.assertRaises(ValueError):
            flow_litmus.run_case(case)

    def test_rejects_case_missing_expected_outcome(self):
        case = load_case("FM-OK-001")
        case["expected"] = {}
        with self.assertRaises(ValueError):
            flow_litmus.run_case(case)

    def test_detects_pre_receipt_dereference_case(self):
        result = flow_litmus.run_case(load_case("FM-LB-001"))
        self.assertEqual("pass", result["status"])
        self.assertEqual(["forbidden_pre_receipt_read"], result["observed"]["faultTypes"])

    def test_detects_retrocausal_receipt_claim(self):
        result = flow_litmus.run_case(load_case("FM-SER-001"))
        self.assertEqual("pass", result["status"])
        self.assertEqual(["retrocausal_receipt_claim"], result["observed"]["faultTypes"])

    def test_detects_unquiesced_output_case(self):
        result = flow_litmus.run_case(load_case("FM-QS-001"))
        self.assertEqual("pass", result["status"])
        self.assertEqual(["QuiescenceViolation"], result["observed"]["faultTypes"])

    def test_detects_unretired_output_escape(self):
        result = flow_litmus.run_case(load_case("FM-RT-001"))
        self.assertEqual("pass", result["status"])
        self.assertEqual(["RetirementViolation"], result["observed"]["faultTypes"])

    def test_detects_stale_output_surviving_boundary_fission_expectation(self):
        result = flow_litmus.run_case(load_case("FM-FIS-001"))
        self.assertEqual("pass", result["status"])
        self.assertEqual(["BoundaryFissionViolation"], result["observed"]["faultTypes"])

    def test_detects_rootfield_rollback(self):
        result = flow_litmus.run_case(load_case("FM-SER-002"))
        self.assertEqual("pass", result["status"])
        self.assertEqual(["rootfield_rollback"], result["observed"]["faultTypes"])

    def test_detects_split_brain_canonical_write(self):
        result = flow_litmus.run_case(load_case("FM-SER-003"))
        self.assertEqual("pass", result["status"])
        self.assertEqual(["split_brain_write"], result["observed"]["faultTypes"])

    def test_accepts_valid_boundary_history(self):
        result = flow_litmus.run_case(load_case("FM-OK-001"))
        self.assertEqual("pass", result["status"])
        self.assertEqual("valid_history_accepted", result["observed"]["outcome"])
        self.assertEqual(["Serializable"], result["observed"]["faultTypes"])

    def test_requires_txhash_for_receipt_bound_cases(self):
        case = load_case("FM-SER-001")
        history = flow_litmus.read_json(flow_litmus.resolve_path(case["artifacts"]["history"]))
        history["boundaries"][0]["txHash"] = None
        self.assertEqual("missing_receipt_metadata", flow_litmus.flow_serial.certify(history)["faultType"])

    def test_requires_logindex_for_receipt_bound_cases(self):
        case = load_case("FM-SER-001")
        history = flow_litmus.read_json(flow_litmus.resolve_path(case["artifacts"]["history"]))
        history["boundaries"][0]["logIndex"] = None
        self.assertEqual("missing_receipt_metadata", flow_litmus.flow_serial.certify(history)["faultType"])

    def test_requires_successful_receipt_status_for_receipt_bound_cases(self):
        case = load_case("FM-SER-001")
        history = flow_litmus.read_json(flow_litmus.resolve_path(case["artifacts"]["history"]))
        history["boundaries"][0]["receiptStatus"] = "reverted"
        self.assertEqual("failed_receipt_boundary", flow_litmus.flow_serial.certify(history)["faultType"])

    def test_rejects_generic_api_log_as_flowpulse_boundary(self):
        case = load_case("FM-SER-001")
        history = flow_litmus.read_json(flow_litmus.resolve_path(case["artifacts"]["history"]))
        history["boundaries"][0]["artifactType"] = "ApiLog"
        self.assertEqual("failed_receipt_boundary", flow_litmus.flow_serial.certify(history)["faultType"])

    def test_verifies_expected_fault_matches_observed_fault(self):
        result = flow_litmus.run_case(load_case("FM-SER-003"))
        self.assertEqual(result["expected"]["faultTypes"], result["observed"]["faultTypes"])

    def test_fails_case_if_expected_fault_is_not_observed(self):
        case = load_case("FM-SER-003")
        case["expected"] = {"outcome": "forbidden_outcome_detected", "faultTypes": ["rootfield_rollback"]}
        result = flow_litmus.run_case(case)
        self.assertEqual("fail", result["status"])
        self.assertIn("fault_type_mismatch", result["problems"])

    def test_fails_case_if_unexpected_outcome_appears(self):
        case = load_case("FM-OK-001")
        case["expected"] = {"outcome": "forbidden_outcome_detected", "faultTypes": ["retrocausal_receipt_claim"]}
        result = flow_litmus.run_case(case)
        self.assertEqual("fail", result["status"])
        self.assertIn("outcome_mismatch", result["problems"])

    def test_produces_deterministic_result_hash_for_same_case(self):
        case = load_case("FM-SER-001")
        self.assertEqual(flow_litmus.run_case(case)["resultId"], flow_litmus.run_case(case)["resultId"])

    def test_preserves_hard_non_claims(self):
        rendered = flow_litmus.axiom_writ.canonical_json(flow_litmus.run_suite(MANIFEST))
        for phrase in ["not_semantic_truth", "not_model_correctness", "not_gpu_attestation", "not_custody", "not_swap_control", "not_fund_protection"]:
            self.assertIn(phrase, rendered)
        self.assertNotIn("protects funds", rendered.lower())
        self.assertNotIn("controls swaps", rendered.lower())

    def test_render_table_contains_all_cases(self):
        table = flow_litmus.render_table(flow_litmus.run_suite(MANIFEST))
        self.assertIn("FlowLitmus Runtime Consistency Suite", table)
        self.assertIn("FM-LB-001", table)
        self.assertIn("FM-OK-001", table)
        self.assertIn("8/8 passed", table)

    def test_explain_renders_invariant(self):
        explanation = flow_litmus.explain(load_case("FM-SER-001"))
        self.assertIn("Invariant:", explanation)
        self.assertIn("Why FlowPulse matters:", explanation)

    def test_mutated_case_copy_does_not_change_original_result(self):
        case = load_case("FM-OK-001")
        mutated = copy.deepcopy(case)
        mutated["title"] = "Changed title"
        self.assertEqual("pass", flow_litmus.run_case(case)["status"])
        self.assertEqual("pass", flow_litmus.run_case(mutated)["status"])


if __name__ == "__main__":
    unittest.main()
