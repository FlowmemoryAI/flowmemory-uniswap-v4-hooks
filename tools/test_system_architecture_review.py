import json
import subprocess
import sys
import unittest

from tools import system_architecture_review


class SystemArchitectureReviewTest(unittest.TestCase):
    def test_default_manifest_passes_architecture_review(self):
        report = system_architecture_review.build_report()
        self.assertEqual("flowmemory.system_architecture_review.v0", report["schema"])
        self.assertEqual("PASS", report["status"])
        self.assertEqual(report["layersRequired"], report["layersChecked"])
        self.assertEqual(report["invariantsRequired"], report["invariantsChecked"])
        self.assertEqual(report["nonClaimsRequired"], report["nonClaimsChecked"])
        self.assertEqual(system_architecture_review.REQUIRED_READINESS_PATH, report["readinessPath"])

    def test_missing_required_layer_fails(self):
        manifest = system_architecture_review.load_manifest()
        manifest["layers"] = [
            layer for layer in manifest["layers"] if layer["id"] != "operations"
        ]
        report = system_architecture_review.build_report(manifest)
        self.assertEqual("FAIL", report["status"])
        self.assertIn(
            {"code": "missing_layer", "detail": "operations"},
            report["issues"],
        )

    def test_missing_receipt_separation_invariant_fails(self):
        manifest = system_architecture_review.load_manifest()
        manifest["invariants"].remove("receipt_metadata_is_reader_derived")
        report = system_architecture_review.build_report(manifest)
        self.assertEqual("FAIL", report["status"])
        self.assertIn(
            {"code": "missing_invariant", "detail": "receipt_metadata_is_reader_derived"},
            report["issues"],
        )

    def test_missing_nonclaim_fails(self):
        manifest = system_architecture_review.load_manifest()
        manifest["nonClaims"].remove("no_custody")
        report = system_architecture_review.build_report(manifest)
        self.assertEqual("FAIL", report["status"])
        self.assertIn(
            {"code": "missing_non_claim", "detail": "no_custody"},
            report["issues"],
        )

    def test_cli_text_output_is_review_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/system_architecture_review.py", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FlowMemory System Architecture Review", completed.stdout)
        self.assertIn("status: PASS", completed.stdout)
        self.assertIn("Architecture packet is complete for launch review.", completed.stdout)

    def test_cli_json_output_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/system_architecture_review.py", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("PASS", payload["status"])
        self.assertEqual(system_architecture_review.REQUIRED_READINESS_PATH, payload["readinessPath"])


if __name__ == "__main__":
    unittest.main()

