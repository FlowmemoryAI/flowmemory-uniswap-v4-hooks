# BoundaryFission v0 Draft Spec

BoundaryFission is a proof-triggered memory release primitive.

When a receipt-bound `FlowPulse` lands, an autonomous system can split its
working memory into conserved facts, compressed residues, quarantined claims,
killed branches, and delegated recompute tasks.

Shortest category sentence:

> A FlowPulse is not context. It is a boundary event that can rupture stale
> cognition.

## Schema

```json
{
  "schema": "flowmemory.boundary_fission.v0",
  "fissionId": "sha256:...",
  "status": "active",
  "fissionType": "proof_triggered_memory_release",
  "trigger": {
    "triggerType": "FlowPulse",
    "boundary": "uniswap_v4_afterSwap",
    "proofTier": "receipt_bound_flowpulse",
    "chainId": "84532",
    "hookAddress": "0x...",
    "txHash": "0x...",
    "logIndex": "7",
    "blockNumber": "123456",
    "receiptStatus": "success",
    "pulseId": "0x...",
    "rootfieldId": "0x...",
    "commitment": "0x...",
    "parentPulseId": "0x...",
    "subjectPoolId": "0x..."
  },
  "inputMemorySet": {
    "workingSetHash": "sha256:...",
    "itemCount": 5,
    "rootfieldId": "0x..."
  },
  "releaseProducts": {
    "conserved": [],
    "residueAtoms": [],
    "quarantined": [],
    "branchAsh": [],
    "delegatedRecompute": []
  },
  "memoryAfter": {
    "schema": "flowmemory.agent_working_memory_after_fission.v0",
    "rawTextPresent": false,
    "containsRawPrivatePayload": false,
    "unsupportedIntentInferencePresent": false,
    "executableOnchainActionPresent": false
  },
  "checks": {
    "txHashReaderAttached": true,
    "logIndexReaderAttached": true,
    "receiptStatusSuccessful": true,
    "triggerRootfieldMatchesWorkingSet": true,
    "noReceiptMetadataFromHookPayload": true,
    "rawPayloadsErasedWhenPolicyRequires": true
  },
  "warnings": [
    "BoundaryFission proves deterministic memory release under this policy; it does not prove semantic truth."
  ]
}
```

## Required Trigger

An active BoundaryFission requires:

- `eventName == FlowPulse`;
- successful receipt status;
- reader-attached `txHash`;
- reader-attached `logIndex`;
- non-zero `rootfieldId`;
- non-zero `commitment`;
- empty validation errors from the reader.

The hook does not supply receipt metadata. The reader does.

## Release Products

### Conserved

Facts that survive the boundary. The current receipt-bound FlowPulse boundary
fact should be conserved.

### ResidueAtoms

Compressed memory products that retain commitments and hashes, not raw payloads.

### Quarantine

Claims that cannot be supported by the proof tier, such as inferred trader
intent or semantic truth claims.

### BranchAsh

Killed executable branches. A pre-boundary `submit_onchain_transaction` plan can
be converted into `BranchAsh` with replacement `propose_unsigned_action`.

### Delegated Recompute

Draft compute tasks created when stale or unattested compute/cache outputs cannot
survive the new boundary as live context.

## Determinism

`fissionId` is the canonical hash of the full report without `fissionId`.

Changing trigger metadata, release actions, retained facts, or release products
must change the hash and cause verification to fail.
