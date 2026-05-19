import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools import memory_consistency_card


class MemoryConsistencyCardTest(unittest.TestCase):
    def test_no_subprocess_mode_keeps_local_surface_parseable(self):
        card = memory_consistency_card.build_card(run_litmus=False)
        self.assertEqual(memory_consistency_card.CARD_SCHEMA, card["schema"])
        self.assertEqual("fail", next(level for level in card["levels"] if level["id"] == "FM-C5")["status"])
        self.assertEqual("pending", next(level for level in card["levels"] if level["id"] == "FM-C6")["status"])

    def test_litmus_mode_passes_local_surface(self):
        card = memory_consistency_card.build_card(run_litmus=True)
        self.assertEqual("pass", card["localStatus"])
        self.assertEqual("pending", card["publicChainEvidence"])
        self.assertEqual("pass", card["litmus"]["status"])
        self.assertEqual(8, card["litmus"]["passed"])

    def test_output_names_the_consistency_thesis(self):
        text = memory_consistency_card.render_card(memory_consistency_card.build_card(run_litmus=True))
        self.assertIn("Agent memory should be checked like a consistency model", text)
        self.assertIn("not retrieved like text", text)
        self.assertIn("Uniswap v4 afterSwap", text)

    def test_output_marks_public_chain_evidence_pending(self):
        text = memory_consistency_card.render_card(memory_consistency_card.build_card(run_litmus=True))
        self.assertIn("PENDING FM-C6", text)
        self.assertIn("public Base Sepolia receipt evidence", text)

    def test_json_mode_returns_parseable_card(self):
        completed = subprocess.run(
            [sys.executable, "tools/memory_consistency_card.py", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(memory_consistency_card.CARD_SCHEMA, payload["schema"])
        self.assertEqual("pass", payload["localStatus"])

    def test_public_release_evidence_status_can_pass_when_file_exists(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / memory_consistency_card.PUBLIC_RELEASE_EVIDENCE
            evidence.parent.mkdir(parents=True)
            evidence.write_text("{}", encoding="utf-8")
            level = next(item for item in memory_consistency_card.CONSISTENCY_LEVELS if item["id"] == "FM-C6")
            self.assertEqual("pass", memory_consistency_card.level_status(level, root, "pass"))

    def test_avoids_forbidden_overclaims(self):
        text = memory_consistency_card.render_card(memory_consistency_card.build_card(run_litmus=True)).lower()
        for forbidden in ["semantic truth proven", "model correctness proven", "mainnet deployed", "controls swaps"]:
            self.assertNotIn(forbidden, text)
        for boundary in ["no semantic truth claim", "no model correctness claim", "no gpu acceleration"]:
            self.assertIn(boundary, text)


if __name__ == "__main__":
    unittest.main()
