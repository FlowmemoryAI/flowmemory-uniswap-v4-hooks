import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools import compute_reuse_router


ROOTFIELD = "0x" + "1" * 64
MODEL = "0x" + "2" * 64
INPUT = "0x" + "3" * 64
RUNTIME = "0x" + "4" * 64
OUTPUT = "0x" + "5" * 64
CACHE = "cache:prefix-alpha"


def request(**overrides):
    body = {
        "schema": compute_reuse_router.REQUEST_SCHEMA,
        "requestId": "req-test",
        "rootfieldId": ROOTFIELD,
        "modelCommitment": MODEL,
        "inputCommitment": INPUT,
        "runtimeCommitment": RUNTIME,
        "sourceCachePulse": CACHE,
        "requestedAt": 1100,
    }
    body.update(overrides)
    return body


def pulse(**overrides):
    body = {
        "schema": compute_reuse_router.COMPUTE_PULSE_SCHEMA,
        "computePulseId": "compute-pulse-001",
        "status": "verified",
        "rootfieldId": ROOTFIELD,
        "modelCommitment": MODEL,
        "inputCommitment": INPUT,
        "outputCommitment": OUTPUT,
        "runtimeCommitment": RUNTIME,
        "hardwareClass": "H100-class",
        "executor": "executor-a",
        "attestationRef": "nras://attestation-report-001",
        "sourceCachePulse": CACHE,
        "completedAt": 1000,
        "reuseAllowed": True,
    }
    body.update(overrides)
    return body


def ledger(*pulses):
    return {"schema": compute_reuse_router.LEDGER_SCHEMA, "computePulses": list(pulses)}


def policy(**overrides):
    body = {
        "schema": compute_reuse_router.POLICY_SCHEMA,
        "maxAgeSeconds": 3600,
        "requireAttestationRef": False,
        "allowedHardwareClasses": ["H100-class", "A100-class"],
        "allowedExecutors": ["executor-a", "executor-b"],
        "allowCrossRootfield": False,
    }
    body.update(overrides)
    return body


class ComputeReuseRouterTest(unittest.TestCase):
    def test_exact_commitment_match_reuses_prior_compute(self):
        decision = compute_reuse_router.route(request(), ledger(pulse()), policy())
        self.assertEqual("reuse", decision["status"])
        self.assertEqual("REUSE_PRIOR_COMPUTE", decision["decision"])
        self.assertEqual("compute-pulse-001", decision["selectedComputePulseId"])
        self.assertEqual(1, decision["gpuJobsAvoided"])

    def test_runtime_drift_requires_new_run(self):
        decision = compute_reuse_router.route(request(runtimeCommitment="0x" + "9" * 64), ledger(pulse()), policy())
        self.assertEqual("run_required", decision["status"])
        self.assertIn("runtimeCommitmentMatches", decision["rejectedCandidates"][0]["reasons"])

    def test_model_drift_requires_new_run(self):
        decision = compute_reuse_router.route(request(modelCommitment="0x" + "9" * 64), ledger(pulse()), policy())
        self.assertEqual("run_required", decision["status"])
        self.assertIn("modelCommitmentMatches", decision["rejectedCandidates"][0]["reasons"])

    def test_cross_rootfield_reuse_is_rejected_by_default(self):
        decision = compute_reuse_router.route(request(rootfieldId="0x" + "9" * 64), ledger(pulse()), policy())
        self.assertEqual("run_required", decision["status"])
        self.assertIn("rootfieldMatches", decision["rejectedCandidates"][0]["reasons"])

    def test_unverified_prior_compute_is_rejected(self):
        decision = compute_reuse_router.route(request(), ledger(pulse(status="local_draft")), policy())
        self.assertEqual("run_required", decision["status"])
        self.assertIn("statusVerified", decision["rejectedCandidates"][0]["reasons"])

    def test_missing_output_commitment_is_rejected(self):
        decision = compute_reuse_router.route(request(), ledger(pulse(outputCommitment=compute_reuse_router.ZERO32)), policy())
        self.assertEqual("run_required", decision["status"])
        self.assertIn("outputCommitmentPresent", decision["rejectedCandidates"][0]["reasons"])

    def test_attestation_requirement_is_enforced(self):
        decision = compute_reuse_router.route(request(requireAttestationRef=True), ledger(pulse(attestationRef="")), policy())
        self.assertEqual("run_required", decision["status"])
        self.assertIn("attestationSatisfied", decision["rejectedCandidates"][0]["reasons"])

    def test_expired_compute_is_rejected(self):
        decision = compute_reuse_router.route(request(requestedAt=10000), ledger(pulse(completedAt=1)), policy())
        self.assertEqual("run_required", decision["status"])
        self.assertIn("freshEnough", decision["rejectedCandidates"][0]["reasons"])

    def test_cache_lineage_must_match_when_request_names_source_cache(self):
        decision = compute_reuse_router.route(request(sourceCachePulse="cache:other"), ledger(pulse()), policy())
        self.assertEqual("run_required", decision["status"])
        self.assertIn("lineageMatches", decision["rejectedCandidates"][0]["reasons"])

    def test_uri_is_not_part_of_reuse_authority(self):
        decision = compute_reuse_router.route(request(uri="ipfs://untrusted-request"), ledger(pulse(uri="ipfs://untrusted-pulse")), policy())
        self.assertEqual("reuse", decision["status"])
        self.assertTrue(decision["rejectedCandidates"] == [])

    def test_latest_eligible_candidate_is_selected_deterministically(self):
        older = pulse(computePulseId="compute-pulse-old", completedAt=900)
        newer = pulse(computePulseId="compute-pulse-new", completedAt=1000)
        decision = compute_reuse_router.route(request(), ledger(older, newer), policy())
        self.assertEqual("compute-pulse-new", decision["selectedComputePulseId"])

    def test_decision_id_verifies_and_detects_tampering(self):
        decision = compute_reuse_router.route(request(), ledger(pulse()), policy())
        self.assertEqual("valid", compute_reuse_router.verify_decision(decision)["status"])
        tampered = copy.deepcopy(decision)
        tampered["selectedOutputCommitment"] = "0x" + "9" * 64
        self.assertEqual("invalid", compute_reuse_router.verify_decision(tampered)["status"])

    def test_demo_passes_and_rejects_unsafe_reuse(self):
        demo = compute_reuse_router.build_demo()
        self.assertEqual("pass", demo["status"])
        self.assertEqual(5, demo["requestsChecked"])
        self.assertEqual(1, demo["priorComputeReused"])
        self.assertEqual(4, demo["unsafeReuseRejected"])

    def test_demo_output_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/compute_reuse_router.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Compute Reuse Router", completed.stdout)
        self.assertIn("prior compute reused: 1", completed.stdout)
        self.assertIn("unsafe reuse rejected: 4/4", completed.stdout)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/compute_reuse_router.py", "demo", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(1, payload["gpuJobsAvoided"])

    def test_route_cli_writes_verifiable_decision(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "decision.json"
            subprocess.run(
                [
                    sys.executable,
                    "tools/compute_reuse_router.py",
                    "route",
                    "--request",
                    "examples/compute-reuse-router/request.reuse.json",
                    "--ledger",
                    "examples/compute-reuse-router/ledger.example.json",
                    "--policy",
                    "examples/compute-reuse-router/policy.example.json",
                    "--out",
                    str(out),
                    "--pretty",
                ],
                check=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual("reuse", payload["status"])
            verify = subprocess.run(
                [sys.executable, "tools/compute_reuse_router.py", "verify-decision", "--decision", str(out)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn('"status": "valid"', verify.stdout)

    def test_nonclaims_are_present(self):
        decision = compute_reuse_router.route(request(), ledger(pulse()), policy())
        for claim in compute_reuse_router.NON_CLAIMS:
            self.assertIn(claim, decision["notClaims"])

    def test_rendered_output_avoids_banned_claims(self):
        text = compute_reuse_router.render_demo(compute_reuse_router.build_demo()).lower()
        for phrase in compute_reuse_router.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
