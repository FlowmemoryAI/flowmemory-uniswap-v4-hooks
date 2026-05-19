import json
import subprocess
import sys
import unittest

from tools import fmm0_phase_table


TABLE = "examples/fmm0-phase-table/phase-table.json"
PRE_LOCAL = "examples/fmm0-phase-table/artifacts/pre_receipt_local_output.json"
READER_FLOWPULSE = "examples/fmm0-phase-table/artifacts/reader_derived_flowpulse.json"
FMM0_HISTORY = "examples/fmm0-phase-table/artifacts/fmm0_conforming_history.json"
ILLEGAL_SMUGGLE = "examples/fmm0-phase-table/artifacts/illegal_receipt_smuggle.json"
VALID_ATTACHMENT = "examples/fmm0-phase-table/transitions/valid_reader_attachment.json"
VALID_FMM0 = "examples/fmm0-phase-table/transitions/valid_reader_to_fmm0.json"
INVALID_LOCAL_FMM0 = "examples/fmm0-phase-table/transitions/invalid_local_to_fmm0.json"
INVALID_READER_FMM0 = "examples/fmm0-phase-table/transitions/invalid_reader_to_fmm0_missing_checks.json"


class Fmm0PhaseTableTest(unittest.TestCase):
    def test_phase_table_loads_with_required_axes(self):
        table = fmm0_phase_table.load_table(TABLE)
        self.assertEqual(fmm0_phase_table.TABLE_SCHEMA, table["schema"])
        for axis, required in fmm0_phase_table.REQUIRED_AXES.items():
            self.assertTrue(required.issubset(set(table["axes"][axis])))

    def test_pre_receipt_local_output_classifies(self):
        table = fmm0_phase_table.load_table(TABLE)
        result = fmm0_phase_table.classify_artifact(table, fmm0_phase_table.read_json(PRE_LOCAL))
        self.assertEqual("PRE-LOCAL-SPEC", result["cellId"])
        self.assertEqual("phase_limited", result["status"])
        self.assertIn("publish_as_live", [item["operation"] for item in result["requestedOperationFaults"]])

    def test_reader_derived_flowpulse_classifies(self):
        table = fmm0_phase_table.load_table(TABLE)
        result = fmm0_phase_table.classify_artifact(table, fmm0_phase_table.read_json(READER_FLOWPULSE))
        self.assertEqual("POST-READER-LIVE", result["cellId"])
        self.assertEqual("pass", result["status"])

    def test_fmm0_conforming_history_classifies(self):
        table = fmm0_phase_table.load_table(TABLE)
        result = fmm0_phase_table.classify_artifact(table, fmm0_phase_table.read_json(FMM0_HISTORY))
        self.assertEqual("FMM0-LIVE", result["cellId"])
        self.assertEqual("pass", result["status"])

    def test_illegal_receipt_smuggle_is_invalid(self):
        table = fmm0_phase_table.load_table(TABLE)
        result = fmm0_phase_table.classify_artifact(table, fmm0_phase_table.read_json(ILLEGAL_SMUGGLE))
        self.assertEqual("invalid", result["status"])
        self.assertEqual("INVALID", result["cellId"])
        self.assertEqual("receipt_field_smuggled_before_reader_attachment", result["fault"])
        self.assertEqual(["logIndex", "txHash"], result["forbiddenFields"])

    def test_before_receipt_artifact_cannot_contain_txhash_or_logindex(self):
        artifact = fmm0_phase_table.read_json(ILLEGAL_SMUGGLE)
        fields = fmm0_phase_table.non_empty_receipt_fields(artifact)
        self.assertIn("txHash", fields)
        self.assertIn("logIndex", fields)

    def test_local_only_artifact_cannot_jump_to_fmm0_live(self):
        table = fmm0_phase_table.load_table(TABLE)
        result = fmm0_phase_table.evaluate_transition(table, fmm0_phase_table.read_json(INVALID_LOCAL_FMM0))
        self.assertEqual("forbidden", result["status"])
        self.assertEqual("missing_reader_derived_receipt_metadata", result["fault"])
        self.assertTrue(result["expectationMet"])

    def test_reader_derived_flowpulse_can_become_eligible_for_fmm0(self):
        table = fmm0_phase_table.load_table(TABLE)
        attachment = fmm0_phase_table.evaluate_transition(table, fmm0_phase_table.read_json(VALID_ATTACHMENT))
        fmm0 = fmm0_phase_table.evaluate_transition(table, fmm0_phase_table.read_json(VALID_FMM0))
        self.assertEqual("allowed", attachment["status"])
        self.assertEqual("allowed", fmm0["status"])
        self.assertTrue(attachment["expectationMet"])
        self.assertTrue(fmm0["expectationMet"])

    def test_reader_derived_flowpulse_still_needs_consistency_checks_for_fmm0_live(self):
        table = fmm0_phase_table.load_table(TABLE)
        result = fmm0_phase_table.evaluate_transition(table, fmm0_phase_table.read_json(INVALID_READER_FMM0))
        self.assertEqual("forbidden", result["status"])
        self.assertEqual("missing_fmm0_consistency_checks", result["fault"])
        self.assertTrue(result["expectationMet"])

    def test_anneal_matches_rootfield_and_commitment(self):
        table = fmm0_phase_table.load_table(TABLE)
        result = fmm0_phase_table.anneal(
            table,
            fmm0_phase_table.read_json(PRE_LOCAL),
            fmm0_phase_table.read_json(READER_FLOWPULSE),
        )
        self.assertEqual("pass", result["status"])
        self.assertEqual("POST-READER-LIVE", result["after"])
        self.assertEqual("eligible_for_serial_check", result["fmm0Status"])

    def test_demo_contains_phase_space_sentence(self):
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_phase_table.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FMM-0 treats machine memory as phase space, not retrieval text.", completed.stdout)
        self.assertIn("illegal_receipt_smuggle", completed.stdout)
        self.assertIn("reader_derived/live -> fmm0_conforming/live without consistency checks", completed.stdout)
        self.assertIn("CAUGHT", completed.stdout)

    def test_render_json_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_phase_table.py", "render", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(fmm0_phase_table.TABLE_SCHEMA, payload["schema"])

    def test_classify_illegal_cli_exits_nonzero_and_names_fault(self):
        completed = subprocess.run(
            [sys.executable, "tools/fmm0_phase_table.py", "classify", "--artifact", ILLEGAL_SMUGGLE, "--pretty"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, completed.returncode)
        self.assertIn("receipt_field_smuggled_before_reader_attachment", completed.stdout)

    def test_nonclaims_avoid_overstating_model(self):
        table = fmm0_phase_table.load_table(TABLE)
        for claim in [
            "not_semantic_truth",
            "not_model_correctness",
            "not_gpu_acceleration",
            "not_custody",
            "not_fund_protection",
            "not_base_mainnet",
            "not_production_verifier_infrastructure",
        ]:
            self.assertIn(claim, table["notClaims"])

    def test_rendered_outputs_avoid_forbidden_claims(self):
        table = fmm0_phase_table.load_table(TABLE)
        outputs = [
            fmm0_phase_table.render_table(table),
            fmm0_phase_table.render_demo(fmm0_phase_table.build_demo(table)),
            fmm0_phase_table.render_anneal(
                fmm0_phase_table.anneal(
                    table,
                    fmm0_phase_table.read_json(PRE_LOCAL),
                    fmm0_phase_table.read_json(READER_FLOWPULSE),
                )
            ),
        ]
        text = "\n".join(outputs)
        for phrase in fmm0_phase_table.FORBIDDEN_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
