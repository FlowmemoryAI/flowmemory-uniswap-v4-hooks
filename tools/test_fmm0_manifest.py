import json
import subprocess
import sys
import unittest
from pathlib import Path

from tools import render_fmm0_matrix


MANIFEST = "examples/memory-model/fmm0.manifest.json"


class Fmm0ManifestTest(unittest.TestCase):
    def test_manifest_loads(self):
        manifest = render_fmm0_matrix.load_manifest(MANIFEST)
        self.assertEqual(render_fmm0_matrix.MANIFEST_SCHEMA, manifest["schema"])
        self.assertEqual("FMM-0", manifest["model"])
        self.assertGreaterEqual(len(manifest["rules"]), 7)

    def test_matrix_has_pending_public_release_evidence_only(self):
        matrix = render_fmm0_matrix.evaluate_manifest(render_fmm0_matrix.load_manifest(MANIFEST))
        self.assertEqual("pass", matrix["status"])
        self.assertEqual(["FMM-0.R7"], matrix["pending"])
        failing = [rule["id"] for rule in matrix["rules"] if rule["status"] == "fail"]
        self.assertEqual([], failing)

    def test_every_local_evidence_path_exists(self):
        matrix = render_fmm0_matrix.evaluate_manifest(render_fmm0_matrix.load_manifest(MANIFEST))
        for rule in matrix["rules"]:
            if rule["status"] == "pending":
                continue
            self.assertFalse(rule["missing"], rule["id"])

    def test_rendered_matrix_contains_launch_thesis(self):
        matrix = render_fmm0_matrix.evaluate_manifest(render_fmm0_matrix.load_manifest(MANIFEST))
        text = render_fmm0_matrix.render_matrix(matrix)
        self.assertIn("Everyone treated agent memory like retrieval", text)
        self.assertIn("FMM-0.R5", text)
        self.assertIn("FMM-0.R7", text)
        self.assertIn("PENDING", text)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/render_fmm0_matrix.py", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("flowmemory.fmm0.conformance_matrix.v0", payload["schema"])
        self.assertEqual("pass", payload["status"])

    def test_check_mode_allows_pending_release_evidence(self):
        completed = subprocess.run(
            [sys.executable, "tools/render_fmm0_matrix.py", "--check", "--out", "examples/memory-model/fmm0.matrix.tmp.md"],
            check=False,
            capture_output=True,
            text=True,
        )
        try:
            self.assertEqual(0, completed.returncode, completed.stderr)
        finally:
            Path("examples/memory-model/fmm0.matrix.tmp.md").unlink(missing_ok=True)

    def test_nonclaims_avoid_overstating_model(self):
        manifest = render_fmm0_matrix.load_manifest(MANIFEST)
        for claim in ["not_semantic_truth", "not_model_correctness", "not_mainnet_proven", "not_gpu_acceleration"]:
            self.assertIn(claim, manifest["nonClaims"])


if __name__ == "__main__":
    unittest.main()
