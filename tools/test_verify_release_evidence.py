import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools import verify_release_evidence


class VerifyReleaseEvidenceTest(unittest.TestCase):
    def test_missing_release_packet_is_pending_not_fail(self):
        with TemporaryDirectory() as directory:
            report = verify_release_evidence.build_report(Path(directory) / "missing.json")
            self.assertEqual("pending", report["status"])
            self.assertEqual("PENDING", report["verdict"]["publicBaseSepoliaReceiptEvidence"])

    def test_default_cli_is_pending_safe(self):
        completed = subprocess.run(
            [sys.executable, "tools/verify_release_evidence.py", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Public Base Sepolia receipt evidence: PENDING", completed.stdout)

    def test_require_pass_exits_nonzero_for_missing_release(self):
        completed = subprocess.run(
            [sys.executable, "tools/verify_release_evidence.py", "--require-pass"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, completed.returncode)

    def test_valid_packet_passes(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "flowpulse-receipt.json").write_text(
                json.dumps({"txHash": "0xabc", "logIndex": 4, "receiptStatus": "success"}),
                encoding="utf-8",
            )
            (root / "flowpulse-evidence.json").write_text(
                json.dumps({"flowPulse": {"pulseId": "0x01", "rootfieldId": "0x02", "commitment": "0x03"}, "txHash": "0xabc", "logIndex": 4}),
                encoding="utf-8",
            )
            (root / "fmm0-release-verdict.json").write_text(
                json.dumps({"publicBaseSepoliaReceiptEvidence": "PASS", "productionVerifierInfrastructure": "NOT_CLAIMED"}),
                encoding="utf-8",
            )
            release = {
                "schema": verify_release_evidence.RELEASE_SCHEMA,
                "release": {
                    "name": "test",
                    "network": "Base Sepolia",
                    "status": "public_testnet_evidence",
                    "notClaims": sorted(verify_release_evidence.REQUIRED_NOT_CLAIMS),
                },
                "hookBoundary": {
                    "hookType": "Uniswap v4 afterSwap",
                    "memoryArtifact": "FlowPulse",
                    "proofEnvelope": "transaction_receipt",
                    "receiptMetadataAttachedBy": "reader_verifier",
                },
                "evidenceFiles": {
                    "receipt": "flowpulse-receipt.json",
                    "flowPulseEvidence": "flowpulse-evidence.json",
                    "fmm0Verdict": "fmm0-release-verdict.json",
                },
                "expected": {
                    "publicReceiptEvidence": "PASS",
                    "flowPulseArtifactPresent": True,
                    "txHashReaderAttached": True,
                    "logIndexReaderAttached": True,
                    "hookKnowsTxHashDuringExecution": False,
                    "hookKnowsLogIndexDuringExecution": False,
                },
            }
            release_path = root / "RELEASE_EVIDENCE.json"
            release_path.write_text(json.dumps(release), encoding="utf-8")
            report = verify_release_evidence.build_report(release_path)
            self.assertEqual("pass", report["status"])
            self.assertEqual("PASS", report["verdict"]["publicBaseSepoliaReceiptEvidence"])

    def test_hook_time_receipt_claim_fails(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            release = {
                "schema": verify_release_evidence.RELEASE_SCHEMA,
                "release": {
                    "network": "Base Sepolia",
                    "status": "public_testnet_evidence",
                    "notClaims": sorted(verify_release_evidence.REQUIRED_NOT_CLAIMS),
                },
                "evidenceFiles": {},
                "expected": {
                    "hookKnowsTxHashDuringExecution": True,
                    "hookKnowsLogIndexDuringExecution": False,
                },
            }
            release_path = root / "RELEASE_EVIDENCE.json"
            release_path.write_text(json.dumps(release), encoding="utf-8")
            report = verify_release_evidence.build_report(release_path)
            self.assertEqual("fail", report["status"])

    def test_output_preserves_non_claims(self):
        text = verify_release_evidence.render_report(verify_release_evidence.build_report("releases/base-sepolia/RELEASE_EVIDENCE.json")).lower()
        self.assertIn("production verifier infrastructure: not_claimed", text)
        self.assertIn("semantic truth: not_claimed", text)
        self.assertNotIn("base mainnet", text)
        self.assertNotIn("audited custody", text)


if __name__ == "__main__":
    unittest.main()
