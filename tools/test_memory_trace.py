import copy
import unittest

from tools import memory_trace


def example_trace():
    return {
        "schema": "flowmemory.machine_memory_trace.v0",
        "traceId": "trace-1",
        "rootfieldId": "0x" + "11" * 32,
        "summary": "test trace",
        "artifacts": [
            {
                "type": "FlowPulse",
                "status": "example_from_uniswap_v4_after_swap",
                "id": "flow-1",
                "boundary": "uniswap_v4_afterSwap",
                "proofEnvelope": {
                    "chainId": 84532,
                    "txHash": "0x" + "aa" * 32,
                    "logIndex": 7,
                    "hookAddress": "0x0000000000000000000000000000000000000000",
                    "readerAttachedReceiptMetadata": True,
                },
                "memory": {
                    "rootfieldId": "0x" + "11" * 32,
                    "commitment": "0x" + "bb" * 32,
                    "artifact": "FlowPulse memory signal",
                },
            },
            {
                "type": "ComputePulse",
                "status": "mocked_rd_artifact",
                "id": "compute-1",
                "boundary": "post_compute_job",
                "proofEnvelope": {
                    "jobId": "gpu-job-example-001",
                    "executor": "rd-local-worker",
                },
                "memory": {
                    "modelCommitment": "0x" + "cc" * 32,
                    "inputCommitment": "0x" + "dd" * 32,
                    "outputCommitment": "0x" + "ee" * 32,
                    "artifact": "ComputePulse memory signal",
                },
            },
            {
                "type": "ModelPulse",
                "status": "mocked_rd_artifact",
                "id": "model-1",
                "boundary": "model_output_committed",
                "proofEnvelope": {
                    "sourceComputePulse": "compute-1",
                    "outputCommitment": "0x" + "ee" * 32,
                },
                "memory": {
                    "artifact": "ModelPulse output provenance signal",
                },
            },
        ],
        "edges": [
            {"from": "compute-1", "to": "flow-1", "type": "observed_by"},
            {"from": "model-1", "to": "compute-1", "type": "produces"},
        ],
        "verifierNotes": ["test"],
    }


class MemoryTraceTest(unittest.TestCase):
    def test_builds_agent_memory_pack(self):
        pack = memory_trace.build_agent_memory_pack(example_trace())

        self.assertEqual(pack["schema"], memory_trace.PACK_SCHEMA)
        self.assertEqual(pack["status"], "verified_with_notes")
        self.assertEqual(pack["counts"]["artifacts"], 3)
        self.assertEqual(pack["counts"]["edges"], 2)
        self.assertEqual(pack["counts"]["error"], 0)
        self.assertEqual(len(pack["recallCards"]), 3)
        self.assertEqual(len(pack["routing"]["reusableComputeCandidates"]), 1)
        self.assertTrue(pack["traceFingerprint"].startswith("0x"))
        self.assertIn("Rootflow", pack["routing"]["nextBestAction"])

    def test_rejects_missing_edge_target(self):
        trace = example_trace()
        trace["edges"][0]["to"] = "missing"

        pack = memory_trace.build_agent_memory_pack(trace)

        self.assertEqual(pack["status"], "rejected")
        self.assertIn("edge_missing_target", {issue["code"] for issue in pack["issues"]})

    def test_fingerprint_is_stable_for_key_order(self):
        trace_a = example_trace()
        trace_b = copy.deepcopy(trace_a)
        trace_b["artifacts"] = [dict(reversed(list(artifact.items()))) for artifact in trace_b["artifacts"]]

        self.assertEqual(
            memory_trace.digest(trace_a, "MachineMemoryTrace"),
            memory_trace.digest(trace_b, "MachineMemoryTrace"),
        )


if __name__ == "__main__":
    unittest.main()
