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


if __name__ == "__main__":
    unittest.main()
