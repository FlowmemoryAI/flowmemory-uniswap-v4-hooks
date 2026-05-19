import json
import subprocess
import sys
import unittest

from tools import fmm0_witness_pack


class Fmm0WitnessPackTest(unittest.TestCase):
    def test_pack_builds_with_all_local_layers_passing(self):
        pack = fmm0_witness_pack.build_pack()
        self.assertEqual(fmm0_witness_pack.PACK_SCHEMA, pack["schema"])
        self.assertEqual("pass", pack["status"])
        self.assertEqual(pack["localConformanceTotal"], pack["localConformancePassed"])
        self.assertEqual(0, pack["escapedFaults"])

    def test_pack_keeps_public_evidence_pending(self):
        pack = fmm0_witness_pack.build_pack()
        self.assertEqual("PENDING", pack["publicBaseSepoliaEvidence"])
        release = next(item for item in pack["checks"] if item["name"] == "Public Base Sepolia Evidence")
        self.assertEqual("PENDING", release["status"])

    def test_required_checks_exist(self):
        names = {item["name"] for item in fmm0_witness_pack.build_pack()["checks"]}
        for name in [
            "FMM-0 Phase Space",
            "FMM-0 Counterexample Forge",
            "FMM-0 Closure Lab",
            "FMM-0 Boundary Bisimulation",
            "FMM-0 Forbidden Core Extractor",
            "FlowPulse Boundary ABI",
            "FlowLitmus",
            "Memory Consistency Card",
            "Public Base Sepolia Evidence",
        ]:
            self.assertIn(name, names)

    def test_every_check_has_digest(self):
        for item in fmm0_witness_pack.build_pack()["checks"]:
            self.assertTrue(str(item["digest"]).startswith("sha256:"))

    def test_demo_output_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_witness_pack.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("local conformance layers passed: 8/8", completed.stdout)
        self.assertIn("public Base Sepolia evidence: PENDING", completed.stdout)
        self.assertIn("escaped faults: 0", completed.stdout)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_witness_pack.py", "demo", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(0, payload["escapedFaults"])

    def test_write_outputs_text_file(self):
        output = fmm0_witness_pack.repo_root() / "examples" / "fmm0-witness-pack" / "generated.tmp.txt"
        try:
            subprocess.run(
                [sys.executable, "tools/fmm0_witness_pack.py", "demo", "--write", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertTrue(output.exists())
            self.assertIn("FMM-0 Witness Pack", output.read_text(encoding="utf-8"))
        finally:
            if output.exists():
                output.unlink()

    def test_rendered_output_avoids_banned_claims(self):
        text = fmm0_witness_pack.render_pack(fmm0_witness_pack.build_pack()).lower()
        for phrase in fmm0_witness_pack.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
