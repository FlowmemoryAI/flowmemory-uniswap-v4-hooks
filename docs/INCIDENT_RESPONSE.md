# Incident Response

FlowMemory's hook architecture is narrow, but the operating boundary still
needs a direct incident path.

This document is for a future public deployment candidate. It does not claim
live Base mainnet deployment, production verifier infrastructure, audited
custody, fund protection, or wallet enforcement.

## Incident Classes

| Class | Trigger | Immediate action |
| --- | --- | --- |
| Hook deployment mismatch | Hook bytecode, source verification, or permission bits do not match the release packet. | Freeze public release copy, mark the release packet invalid, and publish a correction. |
| Reader/verifier drift | Reader attaches wrong chain, transaction, log index, finality, or contract metadata. | Stop accepting new evidence packets from that reader and replay from canonical RPC/indexer sources. |
| Claim drift | Public copy implies mainnet, custody, fund protection, semantic truth, model correctness, or production verifier status without evidence. | Revert the copy, run `python tools/public_claim_gate.py --pretty`, and publish the corrected boundary. |
| Evidence loss | Release packet references missing logs, unavailable artifacts, or non-reproducible reader output. | Reclassify public evidence as pending and regenerate the packet from receipts. |
| Dependency or RPC fault | Official deployment records, explorer verification, or RPC responses conflict. | Hold deployment promotion until the conflict is resolved with source-linked evidence. |

## Response Order

1. Preserve the current release packet, logs, command output, and commit SHA.
2. Stop new public claims that depend on the disputed evidence.
3. Run the local gates:

```bash
python tools/public_claim_gate.py --pretty
python tools/launch_reality_check.py --pretty
python tools/mainnet_candidate_gate.py --pretty
python tools/verify_release_evidence.py --pretty
```

4. Re-read the disputed receipt or deployment evidence from canonical sources.
5. Publish one of three outcomes:
   - evidence remains valid;
   - evidence is pending until repaired;
   - evidence is invalid and the release packet is withdrawn.

## Operator Rule

The operator can publish evidence status. The operator must not rewrite the
meaning of the hook.

FlowMemory's first hook emits a memory signal. It does not custody funds, protect
funds, control swaps, enforce wallets, prove semantic truth, prove work quality,
or know `txHash`/`logIndex` during hook execution.

## Recovery Standard

A recovery is complete only when:

- the corrected repo state is committed;
- claim gate passes with zero unguarded overclaims;
- launch reality check passes;
- release evidence is either valid or explicitly pending;
- any public announcement uses the corrected evidence status.
