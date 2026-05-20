import unittest

from tools import mainnet_candidate_gate


class MainnetCandidateGateTest(unittest.TestCase):
    def test_local_launch_ready_but_mainnet_blocked_by_default(self):
        report = mainnet_candidate_gate.build_report()
        self.assertEqual(report["schema"], "flowmemory.mainnet_candidate_gate.v0")
        self.assertTrue(report["localLaunchReady"])
        self.assertFalse(report["mainnetCandidateReady"])
        self.assertEqual(report["blockingGateCount"], len(mainnet_candidate_gate.MAINNET_GATES))
        self.assertEqual(report["releaseMode"], "LOCAL_LAUNCH_READY_ONLY")

    def test_can_pass_when_all_external_gates_are_satisfied(self):
        all_gates = {gate["gate"] for gate in mainnet_candidate_gate.MAINNET_GATES}
        report = mainnet_candidate_gate.build_report(all_gates)
        self.assertTrue(report["mainnetCandidateReady"])
        self.assertEqual(report["blockingGateCount"], 0)
        self.assertEqual(report["releaseMode"], "MAINNET_CANDIDATE")


if __name__ == "__main__":
    unittest.main()
