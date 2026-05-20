import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools import base_sepolia_deploy


class BaseSepoliaDeployTest(unittest.TestCase):
    def test_manifest_is_base_sepolia_and_sanitized(self):
        manifest = base_sepolia_deploy.build_manifest(
            status="dry_run",
            deployer_address="0x1111111111111111111111111111111111111111",
            hook_address="0x0000000000000000000000000000000000000040",
        )
        self.assertEqual(base_sepolia_deploy.SCHEMA, manifest["schema"])
        self.assertEqual(base_sepolia_deploy.BASE_SEPOLIA_CHAIN_ID, manifest["chainId"])
        self.assertEqual("dry_run", manifest["status"])
        self.assertEqual([], base_sepolia_deploy.validate_manifest(manifest))

    def test_manifest_rejects_wrong_chain_id(self):
        with self.assertRaises(ValueError):
            base_sepolia_deploy.build_manifest(chain_id=1)

    def test_manifest_rejects_invalid_status(self):
        with self.assertRaises(ValueError):
            base_sepolia_deploy.build_manifest(status="mainnet_live")

    def test_sanitize_redacts_secret_like_fields(self):
        payload = {
            "BASE_SEPOLIA_RPC_URL": "https://secret.example",
            "PRIVATE_KEY": "0xabc",
            "safe": "visible",
        }
        sanitized = base_sepolia_deploy.sanitize(payload)
        self.assertEqual("<redacted>", sanitized["BASE_SEPOLIA_RPC_URL"])
        self.assertEqual("<redacted>", sanitized["PRIVATE_KEY"])
        self.assertEqual("visible", sanitized["safe"])

    def test_validate_fails_on_secret_material(self):
        manifest = base_sepolia_deploy.build_manifest()
        secret_prefix = "PRIVATE_" + "KEY="
        manifest["leak"] = secret_prefix + "abc"
        issues = base_sepolia_deploy.validate_manifest(manifest)
        self.assertIn("possible_secret_or_rpc_url:" + secret_prefix, issues)

    def test_cli_writes_dry_run_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "manifest.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "tools/base_sepolia_deploy.py",
                    "dry-run-manifest",
                    "--output",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            manifest = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("Base Sepolia", completed.stdout)
            self.assertEqual("dry_run", manifest["status"])
            self.assertEqual([], base_sepolia_deploy.validate_manifest(manifest))


if __name__ == "__main__":
    unittest.main()
