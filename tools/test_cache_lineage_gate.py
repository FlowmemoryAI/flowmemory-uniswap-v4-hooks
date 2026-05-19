import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools import cache_lineage_gate


ROOTFIELD = "0x" + "1" * 64
MODEL = "0x" + "2" * 64
TOKENIZER = "0x" + "3" * 64
RUNTIME = "0x" + "4" * 64
PREFIX = "0x" + "5" * 64
SIDE = "0x" + "6" * 64
ADAPTER = "0x" + "7" * 64
POLICY = "0x" + "8" * 64
KV_BLOCK = "0x" + "9" * 64


def request(**overrides):
    body = {
        "schema": cache_lineage_gate.REQUEST_SCHEMA,
        "requestId": "req-cache-test",
        "rootfieldId": ROOTFIELD,
        "modelCommitment": MODEL,
        "tokenizerCommitment": TOKENIZER,
        "runtimeCommitment": RUNTIME,
        "prefixCommitment": PREFIX,
        "sideInputCommitment": SIDE,
        "adapterCommitment": ADAPTER,
        "cachePolicyCommitment": POLICY,
        "requestedAt": 1100,
    }
    body.update(overrides)
    return body


def cache(**overrides):
    body = {
        "schema": cache_lineage_gate.CACHE_PULSE_SCHEMA,
        "cachePulseId": "cache-pulse-001",
        "status": "verified",
        "rootfieldId": ROOTFIELD,
        "modelCommitment": MODEL,
        "tokenizerCommitment": TOKENIZER,
        "runtimeCommitment": RUNTIME,
        "prefixCommitment": PREFIX,
        "sideInputCommitment": SIDE,
        "adapterCommitment": ADAPTER,
        "cachePolicyCommitment": POLICY,
        "kvBlockCommitment": KV_BLOCK,
        "completedAt": 1000,
        "executor": "executor-a",
        "attestationRef": "nras://attestation-cache-001",
        "reuseAllowed": True,
    }
    body.update(overrides)
    return body


def ledger(*caches):
    return {"schema": cache_lineage_gate.LEDGER_SCHEMA, "cachePulses": list(caches)}


def policy(**overrides):
    body = {
        "schema": cache_lineage_gate.POLICY_SCHEMA,
        "maxAgeSeconds": 3600,
        "requireAttestationRef": False,
        "allowedExecutors": ["executor-a", "executor-b"],
    }
    body.update(overrides)
    return body


class CacheLineageGateTest(unittest.TestCase):
    def test_exact_lineage_match_reuses_cache(self):
        verdict = cache_lineage_gate.decide(request(), ledger(cache()), policy())
        self.assertEqual("reuse_cache", verdict["status"])
        self.assertEqual("REUSE_CACHE", verdict["decision"])
        self.assertEqual("cache-pulse-001", verdict["selectedCachePulseId"])

    def test_tokenizer_drift_requires_prefill(self):
        verdict = cache_lineage_gate.decide(request(tokenizerCommitment="0x" + "a" * 64), ledger(cache()), policy())
        self.assertEqual("run_prefill", verdict["status"])
        self.assertIn("tokenizerCommitmentMatches", verdict["nearestRejectedCandidate"]["reasons"])

    def test_side_input_drift_requires_prefill(self):
        verdict = cache_lineage_gate.decide(request(sideInputCommitment="0x" + "a" * 64), ledger(cache()), policy())
        self.assertEqual("run_prefill", verdict["status"])
        self.assertIn("sideInputCommitmentMatches", verdict["nearestRejectedCandidate"]["reasons"])

    def test_adapter_drift_requires_prefill(self):
        verdict = cache_lineage_gate.decide(request(adapterCommitment="0x" + "a" * 64), ledger(cache()), policy())
        self.assertEqual("run_prefill", verdict["status"])
        self.assertIn("adapterCommitmentMatches", verdict["nearestRejectedCandidate"]["reasons"])

    def test_runtime_drift_requires_prefill(self):
        verdict = cache_lineage_gate.decide(request(runtimeCommitment="0x" + "a" * 64), ledger(cache()), policy())
        self.assertEqual("run_prefill", verdict["status"])
        self.assertIn("runtimeCommitmentMatches", verdict["nearestRejectedCandidate"]["reasons"])

    def test_unverified_cache_is_rejected(self):
        verdict = cache_lineage_gate.decide(request(), ledger(cache(status="local_draft")), policy())
        self.assertEqual("run_prefill", verdict["status"])
        self.assertIn("statusVerified", verdict["nearestRejectedCandidate"]["reasons"])

    def test_missing_kv_block_commitment_is_rejected(self):
        verdict = cache_lineage_gate.decide(request(), ledger(cache(kvBlockCommitment=cache_lineage_gate.ZERO32)), policy())
        self.assertEqual("run_prefill", verdict["status"])
        self.assertIn("kvBlockCommitmentPresent", verdict["nearestRejectedCandidate"]["reasons"])

    def test_attestation_requirement_is_enforced(self):
        verdict = cache_lineage_gate.decide(request(requireAttestationRef=True), ledger(cache(attestationRef="")), policy())
        self.assertEqual("run_prefill", verdict["status"])
        self.assertIn("attestationSatisfied", verdict["nearestRejectedCandidate"]["reasons"])

    def test_expired_cache_is_rejected(self):
        verdict = cache_lineage_gate.decide(request(requestedAt=10000), ledger(cache(completedAt=1)), policy())
        self.assertEqual("run_prefill", verdict["status"])
        self.assertIn("freshEnough", verdict["nearestRejectedCandidate"]["reasons"])

    def test_uri_is_not_part_of_reuse_authority(self):
        verdict = cache_lineage_gate.decide(request(uri="ipfs://request"), ledger(cache(uri="ipfs://cache")), policy())
        self.assertEqual("reuse_cache", verdict["status"])

    def test_latest_eligible_cache_is_selected(self):
        older = cache(cachePulseId="cache-old", completedAt=900)
        newer = cache(cachePulseId="cache-new", completedAt=1000)
        verdict = cache_lineage_gate.decide(request(), ledger(older, newer), policy())
        self.assertEqual("cache-new", verdict["selectedCachePulseId"])

    def test_verdict_verifies_and_detects_tampering(self):
        verdict = cache_lineage_gate.decide(request(), ledger(cache()), policy())
        self.assertEqual("valid", cache_lineage_gate.verify_verdict(verdict)["status"])
        tampered = copy.deepcopy(verdict)
        tampered["selectedKvBlockCommitment"] = "0x" + "a" * 64
        self.assertEqual("invalid", cache_lineage_gate.verify_verdict(tampered)["status"])

    def test_demo_passes(self):
        demo = cache_lineage_gate.build_demo()
        self.assertEqual("pass", demo["status"])
        self.assertEqual(5, demo["requestsChecked"])
        self.assertEqual(1, demo["cacheReuseAccepted"])
        self.assertEqual(4, demo["unsafeCacheReuseRejected"])

    def test_demo_output_is_screenshot_ready(self):
        completed = subprocess.run(
            [sys.executable, "tools/cache_lineage_gate.py", "demo", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Cache Lineage Gate", completed.stdout)
        self.assertIn("cache reuse accepted: 1", completed.stdout)
        self.assertIn("unsafe cache reuse rejected: 4/4", completed.stdout)

    def test_json_cli_is_parseable(self):
        completed = subprocess.run(
            [sys.executable, "tools/cache_lineage_gate.py", "demo", "--json", "--pretty"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])

    def test_gate_cli_writes_verifiable_verdict(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "verdict.json"
            subprocess.run(
                [
                    sys.executable,
                    "tools/cache_lineage_gate.py",
                    "gate",
                    "--request",
                    "examples/cache-lineage-gate/request.reuse.json",
                    "--ledger",
                    "examples/cache-lineage-gate/ledger.example.json",
                    "--policy",
                    "examples/cache-lineage-gate/policy.example.json",
                    "--out",
                    str(out),
                    "--pretty",
                ],
                check=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual("reuse_cache", payload["status"])
            verify = subprocess.run(
                [sys.executable, "tools/cache_lineage_gate.py", "verify-verdict", "--verdict", str(out)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn('"status": "valid"', verify.stdout)

    def test_nonclaims_are_present(self):
        verdict = cache_lineage_gate.decide(request(), ledger(cache()), policy())
        for claim in cache_lineage_gate.NON_CLAIMS:
            self.assertIn(claim, verdict["notClaims"])

    def test_rendered_output_avoids_banned_claims(self):
        text = cache_lineage_gate.render_demo(cache_lineage_gate.build_demo()).lower()
        for phrase in cache_lineage_gate.BANNED_OUTPUT_PHRASES:
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
