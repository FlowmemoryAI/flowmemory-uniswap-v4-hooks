import json
import subprocess
import sys
import unittest

from tools import fmm0_forbidden_core


class Fmm0ForbiddenCoreTest(unittest.TestCase):
    def test_manifest_loads(self):
        manifest = fmm0_forbidden_core.load_manifest()
        self.assertEqual(fmm0_forbidden_core.MANIFEST_SCHEMA, manifest["schema"])
        self.assertEqual(10, len(manifest["cases"]))

    def test_report_finds_all_minimal_cores(self):
        report = fmm0_forbidden_core.build_report()
        self.assertEqual(fmm0_forbidden_core.REPORT_SCHEMA, report["schema"])
        self.assertEqual("pass", report["status"])
        self.assertEqual(10, report["invalidHistoriesChecked"])
        self.assertEqual(10, report["minimalCoresFound"])
        self.assertEqual(10, report["oneMinimalCores"])
        self.assertEqual(0, report["escapedFaults"])

    def test_every_case_has_required_shape(self):
        for case in fmm0_forbidden_core.build_cases():
            for field in ["caseId", "name", "kind", "base", "atoms", "expectedFault", "meaning"]:
                self.assertIn(field, case)
            self.assertTrue(case["atoms"])

    def test_full_artifacts_produce_expected_faults(self):
        for case in fmm0_forbidden_core.build_cases():
            full_value = fmm0_forbidden_core.apply_atoms(case["base"], case["atoms"])
            self.assertEqual(case["expectedFault"], fmm0_forbidden_core.observed_fault(case["kind"], full_value))

    def test_cores_are_non_empty_and_one_minimal(self):
        for result in fmm0_forbidden_core.build_report()["results"]:
            self.assertGreater(result["coreAtomCount"], 0)
            self.assertEqual("one_minimal", result["minimality"])

    def test_core_is_smaller_than_full_for_most_cases(self):
        results = fmm0_forbidden_core.build_report()["results"]
        smaller = [item for item in results if item["coreAtomCount"] < item["fullAtomCount"]]
        self.assertGreaterEqual(len(smaller), 8)

    def test_pre_receipt_txhash_core_names_boundary_and_field(self):
        result = next(item for item in fmm0_forbidden_core.build_report()["results"] if item["caseId"] == "CORE-001")
        paths = {atom["path"] for atom in result["minimalCore"]}
        self.assertIn("receiptStage", paths)
        self.assertIn("fields.txHash", paths)

    def test_pre_receipt_logindex_core_names_boundary_and_field(self):
        result = next(item for item in fmm0_forbidden_core.build_report()["results"] if item["caseId"] == "CORE-002")
        paths = {atom["path"] for atom in result["minimalCore"]}
        self.assertIn("receiptStage", paths)
        self.assertIn("fields.logIndex", paths)

    def test_transition_cores_name_missing_evidence_faults(self):
        results = {item["caseId"]: item for item in fmm0_forbidden_core.build_report()["results"]}
        self.assertEqual("missing_reader_derived_receipt_metadata", results["CORE-003"]["expectedFault"])
        self.assertEqual("missing_fmm0_consistency_checks", results["CORE-004"]["expectedFault"])

    def test_missing_receipt_metadata_cores_name_absence_atoms(self):
        results = {item["caseId"]: item for item in fmm0_forbidden_core.build_report()["results"]}
        self.assertTrue(any(atom.get("absent") and atom["path"] == "fields.txHash" for atom in results["CORE-005"]["minimalCore"]))
        self.assertTrue(any(atom.get("absent") and atom["path"] == "fields.logIndex" for atom in results["CORE-006"]["minimalCore"]))

    def test_drift_cores_name_rootfield_and_commitment(self):
        results = {item["caseId"]: item for item in fmm0_forbidden_core.build_report()["results"]}
        self.assertTrue(any(atom["path"] == "fields.rootfieldId" for atom in results["CORE-007"]["minimalCore"]))
        self.assertTrue(any(atom["path"] == "fields.commitment" for atom in results["CORE-008"]["minimalCore"]))

    def test_overclaim_cores_name_forbidden_operations(self):
        results = {item["caseId"]: item for item in fmm0_forbidden_core.build_report()["results"]}
        self.assertTrue(any(atom["path"] == "requestedOperations" for atom in results["CORE-009"]["minimalCore"]))
        self.assertTrue(any(atom["path"] == "requestedOperations" for atom in results["CORE-010"]["minimalCore"]))

    def test_demo_output_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_forbidden_core.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("minimal cores found: 10/10", completed.stdout)
        self.assertIn("one-minimal cores: 10/10", completed.stdout)
        self.assertIn("escaped faults: 0", completed.stdout)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_forbidden_core.py", "demo", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(0, payload["escapedFaults"])

    def test_nonclaims_avoid_overstating_core_extraction(self):
        report = fmm0_forbidden_core.build_report()
        for claim in [
            "not_semantic_truth",
            "not_model_correctness",
            "not_gpu_acceleration",
            "not_custody",
            "not_fund_protection",
            "not_base_mainnet",
            "not_production_verifier_infrastructure",
        ]:
            self.assertIn(claim, report["notClaims"])

    def test_rendered_output_avoids_banned_claims(self):
        text = fmm0_forbidden_core.render_report(fmm0_forbidden_core.build_report()).lower()
        for phrase in fmm0_forbidden_core.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
