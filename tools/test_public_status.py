import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools import public_status, pulse_watch, release_evidence


class PublicStatusTest(unittest.TestCase):
    def test_missing_packet_is_blocked_but_testnet_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            status = public_status.build_status(Path(tmp) / "missing.json")
            self.assertEqual("blocked_no_release_packet", status["status"])
            self.assertTrue(status["testnetOnly"])

    def test_status_from_packet_includes_public_fields(self):
        packet = release_evidence.build_packet(
            pulse_watch.build_demo()["readerOutput"],
            observed_at="2026-05-20T00:00:00Z",
        )
        with tempfile.TemporaryDirectory() as tmp:
            packet_path = Path(tmp) / "packet.json"
            packet_path.write_text(json.dumps(packet), encoding="utf-8")
            status = public_status.build_status(packet_path)
            self.assertEqual("testnet_packet_ready", status["status"])
            self.assertEqual(1, status["observedFlowPulseCount"])
            self.assertTrue(status["exampleProofEnvelope"]["txHash"].startswith("0x"))

    def test_markdown_says_testnet_only_and_non_claims(self):
        status = public_status.build_status(Path("missing.json"))
        markdown = public_status.render_markdown(status)
        self.assertIn("testnet-only", markdown)
        self.assertIn("Not Base mainnet", markdown)
        self.assertIn("Not custody", markdown)

    def test_cli_writes_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "status.md"
            subprocess.run(
                [sys.executable, "tools/public_status.py", "--packet", str(Path(tmp) / "missing.json"), "--output", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            text = output.read_text(encoding="utf-8")
            self.assertIn("FlowMemory Base Sepolia Public Status", text)
            self.assertIn("testnet-only", text)


if __name__ == "__main__":
    unittest.main()
