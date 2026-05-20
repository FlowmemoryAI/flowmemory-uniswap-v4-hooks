import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools import pulse_watch, release_evidence


class ReleaseEvidenceTest(unittest.TestCase):
    def reader_output(self):
        return pulse_watch.build_demo()["readerOutput"]

    def test_build_packet_from_observed_reader_output(self):
        packet = release_evidence.build_packet(
            self.reader_output(),
            observed_at="2026-05-20T00:00:00Z",
        )
        self.assertEqual(release_evidence.PACKET_SCHEMA, packet["schema"])
        self.assertEqual("observed_testnet", packet["sourceType"])
        self.assertEqual(1, packet["counts"]["flowPulse"])
        self.assertEqual([], release_evidence.verify_packet(packet))

    def test_proof_envelope_identity_is_chain_tx_log(self):
        record = self.reader_output()["records"][0]
        identity = release_evidence.proof_envelope_id("84532", record)
        self.assertEqual(f"84532:{record['txHash'].lower()}:{record['logIndex']}", identity)

    def test_duplicate_logs_are_idempotent(self):
        reader_output = self.reader_output()
        reader_output["records"].append(dict(reader_output["records"][0]))
        packet = release_evidence.build_packet(reader_output, observed_at="2026-05-20T00:00:00Z")
        self.assertEqual(1, packet["counts"]["duplicatesRemoved"])
        self.assertEqual(len(packet["records"]), len({record["proofEnvelopeId"] for record in packet["records"]}))

    def test_observed_packet_requires_flowpulse(self):
        reader_output = self.reader_output()
        reader_output["records"] = [record for record in reader_output["records"] if record["eventName"] != "FlowPulse"]
        with self.assertRaises(ValueError):
            release_evidence.build_packet(reader_output)

    def test_fixture_requires_explicit_fixture_mode(self):
        with self.assertRaises(ValueError):
            release_evidence.build_packet(self.reader_output(), source_type="fixture")

    def test_release_packet_hash_is_deterministic(self):
        packet_a = release_evidence.build_packet(self.reader_output(), observed_at="2026-05-20T00:00:00Z")
        packet_b = release_evidence.build_packet(self.reader_output(), observed_at="2026-05-20T00:00:00Z")
        self.assertEqual(packet_a["releasePacketHash"], packet_b["releasePacketHash"])

    def test_no_silent_verified_upgrade_for_fixture(self):
        packet = release_evidence.build_packet(
            self.reader_output(),
            source_type="fixture",
            fixture_mode=True,
            observed_at="2026-05-20T00:00:00Z",
        )
        packet["records"][0]["finalityState"] = "testnet_verified"
        issues = release_evidence.verify_packet(packet)
        self.assertIn("fixture_cannot_be_testnet_verified", issues)

    def test_cli_generate_verify_and_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            reader_path = Path(tmp) / "reader.json"
            output_path = Path(tmp) / "packet.json"
            reader_path.write_text(json.dumps(self.reader_output()), encoding="utf-8")
            subprocess.run(
                [
                    sys.executable,
                    "tools/release_evidence.py",
                    "generate",
                    "--reader-output",
                    str(reader_path),
                    "--output",
                    str(output_path),
                    "--observed-at",
                    "2026-05-20T00:00:00Z",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            verify = subprocess.run(
                [sys.executable, "tools/release_evidence.py", "verify", "--input", str(output_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            replay = subprocess.run(
                [sys.executable, "tools/release_evidence.py", "replay", "--input", str(output_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("PASS", verify.stdout)
            self.assertIn("PASS", replay.stdout)


if __name__ == "__main__":
    unittest.main()
