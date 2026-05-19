import json
import subprocess
import sys
import unittest

from tools import render_flowlitmus_casebook


CASEBOOK = "examples/flow-litmus/flowlitmus-casebook.json"


class FlowLitmusCasebookTest(unittest.TestCase):
    def test_casebook_loads(self):
        casebook = render_flowlitmus_casebook.load_casebook(CASEBOOK)
        self.assertEqual(render_flowlitmus_casebook.CASEBOOK_SCHEMA, casebook["schema"])
        self.assertEqual(8, len(casebook["cases"]))

    def test_all_case_files_exist(self):
        report = render_flowlitmus_casebook.evaluate_casebook(render_flowlitmus_casebook.load_casebook(CASEBOOK))
        self.assertEqual("pass", report["status"])
        self.assertTrue(all(case["caseFileExists"] for case in report["cases"]))

    def test_casebook_mentions_each_expected_fault(self):
        report = render_flowlitmus_casebook.evaluate_casebook(render_flowlitmus_casebook.load_casebook(CASEBOOK))
        text = render_flowlitmus_casebook.render_markdown(report)
        for phrase in [
            "forbidden_pre_receipt_read",
            "retrocausal_receipt_claim",
            "QuiescenceViolation",
            "RetirementViolation",
            "BoundaryFissionViolation",
            "rootfield_rollback",
            "split_brain_write",
            "Serializable",
        ]:
            self.assertIn(phrase, text)

    def test_cli_json_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/render_flowlitmus_casebook.py", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("flowmemory.flowlitmus.casebook_report.v0", payload["schema"])
        self.assertEqual("pass", payload["status"])

    def test_check_mode_passes(self):
        completed = subprocess.run(
            [sys.executable, "tools/render_flowlitmus_casebook.py", "--check"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)

    def test_nonclaims_are_preserved(self):
        report = render_flowlitmus_casebook.evaluate_casebook(render_flowlitmus_casebook.load_casebook(CASEBOOK))
        for claim in ["not_semantic_truth", "not_model_correctness", "not_production_verifier_infrastructure"]:
            self.assertIn(claim, report["nonClaims"])


if __name__ == "__main__":
    unittest.main()
