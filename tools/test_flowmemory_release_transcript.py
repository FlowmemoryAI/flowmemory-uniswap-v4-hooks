import json
import subprocess
import sys
import unittest

from tools import flowmemory_release_transcript


class FlowMemoryReleaseTranscriptTest(unittest.TestCase):
    def test_transcript_summarizes_local_pass_and_public_pending(self):
        transcript = flowmemory_release_transcript.build_transcript()
        self.assertEqual(flowmemory_release_transcript.TRANSCRIPT_SCHEMA, transcript["schema"])
        self.assertEqual("PASS", transcript["localStatus"])
        self.assertEqual("PENDING", transcript["publicReceiptEvidence"])
        self.assertEqual("local_ready_public_evidence_pending", transcript["launchReadiness"])

    def test_transcript_includes_required_evidence_layers(self):
        transcript = flowmemory_release_transcript.build_transcript()
        local_names = {item["name"] for item in transcript["localEvidence"]}
        public_names = {item["name"] for item in transcript["publicEvidence"]}
        self.assertIn("FMM-0 Witness Pack", local_names)
        self.assertIn("Launch Reality Check", local_names)
        self.assertIn("Compute Reuse Router", local_names)
        self.assertIn("Cache Lineage Gate", local_names)
        self.assertIn("Compute Reuse Consistency", local_names)
        self.assertIn("SpendLine Harness", local_names)
        self.assertIn("DuplexLine Harness", local_names)
        self.assertIn("Public Base Sepolia Receipt Evidence", public_names)

    def test_evidence_items_are_digest_bound(self):
        transcript = flowmemory_release_transcript.build_transcript()
        for item in transcript["localEvidence"] + transcript["publicEvidence"]:
            self.assertTrue(item["digest"].startswith("sha256:"))

    def test_nonclaims_are_present(self):
        transcript = flowmemory_release_transcript.build_transcript()
        for claim in flowmemory_release_transcript.NON_CLAIMS:
            self.assertIn(claim, transcript["notClaims"])

    def test_demo_output_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/flowmemory_release_transcript.py", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FlowMemory Release Transcript", completed.stdout)
        self.assertIn("FMM-0 Witness Pack", completed.stdout)
        self.assertIn("Compute Reuse Router", completed.stdout)
        self.assertIn("public receipt evidence remains pending", completed.stdout)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/flowmemory_release_transcript.py", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("PASS", payload["localStatus"])
        self.assertEqual("PENDING", payload["publicReceiptEvidence"])

    def test_rendered_output_avoids_banned_claims(self):
        text = flowmemory_release_transcript.render_transcript(flowmemory_release_transcript.build_transcript()).lower()
        for phrase in flowmemory_release_transcript.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
