import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools import pulse_watch


class PulseWatchTest(unittest.TestCase):
    def test_demo_builds_always_on_reader_report(self):
        demo = pulse_watch.build_demo()
        report = demo["watchReport"]

        self.assertEqual("flowmemory.pulsewatch_demo.v0", demo["schema"])
        self.assertEqual("pass", demo["status"])
        self.assertEqual([], report["validationFaults"])
        self.assertEqual(2, report["recordsSeen"])
        self.assertEqual(2, report["recordsAccepted"])
        self.assertEqual(2, report["memoryRecordsWritten"])
        self.assertEqual(1, report["flowPulseMemoryRecords"])
        self.assertEqual(121, report["cursorBlockAfter"])
        self.assertIn("not_hook_runs_without_transactions", demo["notClaims"])

    def test_ingest_deduplicates_seen_logs(self):
        demo = pulse_watch.build_demo()
        reader_output = demo["readerOutput"]
        first_report, state, records = pulse_watch.ingest_reader_output(
            reader_output,
            pulse_watch.empty_state(
                chain_id=reader_output["chainId"],
                hook_address=reader_output["hookAddress"],
                cursor_block=119,
            ),
        )
        second_report, _, second_records = pulse_watch.ingest_reader_output(reader_output, state)

        self.assertEqual(2, first_report["recordsAccepted"])
        self.assertEqual(2, len(records))
        self.assertEqual(0, second_report["recordsAccepted"])
        self.assertEqual(2, second_report["duplicatesSkipped"])
        self.assertEqual([], second_records)

    def test_validation_rejects_hook_time_receipt_metadata_smuggling(self):
        demo = pulse_watch.build_demo()
        reader_output = demo["readerOutput"]
        reader_output["records"][0]["source"] = "hook_time"
        faults = pulse_watch.validate_reader_output(reader_output)

        self.assertIn("hook_time_receipt_metadata_smuggled", faults)

    def test_memory_record_preserves_proof_envelope(self):
        demo = pulse_watch.build_demo()
        record = demo["memoryRecords"][0]

        self.assertEqual("flowmemory.pulsewatch_memory_record.v0", record["schema"])
        self.assertTrue(record["memoryRecordId"].startswith("sha256:"))
        self.assertEqual("success", record["proofEnvelope"]["receiptStatus"])
        self.assertTrue(record["txHash"].startswith("0x"))

    def test_demo_cli_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/pulse_watch.py", "demo"],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("FlowMemory PulseWatch", completed.stdout)
        self.assertIn("PulseWatch is the always-on memory layer", completed.stdout)

    def test_verify_cli_accepts_demo_report(self):
        demo = pulse_watch.build_demo()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pulsewatch-demo.json"
            path.write_text(json.dumps(demo), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "tools/pulse_watch.py", "verify", "--input", str(path)],
                check=True,
                capture_output=True,
                text=True,
            )

        self.assertIn("PulseWatch verify: PASS", completed.stdout)

    def test_health_report_includes_reader_lag_and_cursor(self):
        demo = pulse_watch.build_demo()
        health = pulse_watch.health_report(
            demo["nextState"],
            latest_block=130,
            expected_chain_id="84532",
            expected_hook_address=demo["nextState"]["hookAddress"],
        )
        self.assertEqual("flowmemory.pulsewatch_health.v0", health["schema"])
        self.assertEqual("healthy", health["status"])
        self.assertEqual(9, health["readerLagBlocks"])
        self.assertEqual(121, health["latestScannedBlock"])

    def test_health_report_degrades_on_wrong_hook(self):
        demo = pulse_watch.build_demo()
        health = pulse_watch.health_report(
            demo["nextState"],
            latest_block=130,
            expected_hook_address="0x0000000000000000000000000000000000000040",
        )
        self.assertEqual("degraded", health["status"])

    def test_replay_reader_output_is_deterministic(self):
        demo = pulse_watch.build_demo()
        replay = pulse_watch.replay_reader_output(demo["readerOutput"], from_cursor=119)
        self.assertEqual("PASS", replay["status"])
        self.assertTrue(replay["deterministic"])
        self.assertEqual(2, replay["recordsAccepted"])

    def test_health_cli_reports_lag(self):
        demo = pulse_watch.build_demo()
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            state_path.write_text(json.dumps(demo["nextState"]), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "tools/pulse_watch.py",
                    "health",
                    "--state",
                    str(state_path),
                    "--latest-block",
                    "130",
                    "--expected-chain-id",
                    "84532",
                    "--expected-hook-address",
                    demo["nextState"]["hookAddress"],
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        self.assertIn("PulseWatch health: HEALTHY", completed.stdout)
        self.assertIn("readerLagBlocks: 9", completed.stdout)


if __name__ == "__main__":
    unittest.main()
