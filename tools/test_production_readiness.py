import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import production_readiness


class ProductionReadinessTest(unittest.TestCase):
    def test_report_is_not_fail_by_default(self):
        report = production_readiness.build_report()
        self.assertIn(report["readiness"], {"testnet_path_ready", "testnet_path_ready_evidence_blocked"})
        self.assertIn("not_base_mainnet", report["notClaims"])

    def test_missing_docs_are_blocking(self):
        with mock.patch.object(production_readiness, "REQUIRED_DOCS", ["docs/definitely-missing.md"]):
            report = production_readiness.build_report()
        self.assertEqual("testnet_path_ready_evidence_blocked", report["readiness"])
        self.assertIn({"gate": "doc:docs/definitely-missing.md", "status": "BLOCKED"}, report["checks"])

    def test_invalid_manifest_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.json"
            manifest.write_text(json.dumps({"schema": "bad", "chainId": 1, "status": "mainnet_live"}), encoding="utf-8")
            report = production_readiness.build_report(deployment_manifest=str(manifest))
        self.assertEqual("fail", report["readiness"])


if __name__ == "__main__":
    unittest.main()
