# ResidueAtom v0 Draft Spec

`ResidueAtom` is the irreducible product of proof-triggered memory compression.

It proves that a memory item was compressed or erased under a `BoundaryFission`
policy without retaining the raw payload itself.

## Schema

```json
{
  "schema": "flowmemory.residue_atom.v0",
  "residueId": "sha256:...",
  "sourceMemoryHash": "sha256:...",
  "boundaryPulseHash": "sha256:...",
  "releaseAction": "compress_to_commitment_only",
  "retainedFacts": {
    "memoryId": "mem-old-model-output",
    "type": "ModelPulseDraft",
    "rootfieldId": "0x...",
    "sourceCommitment": "sha256:...",
    "proofTier": "local_draft",
    "createdBeforeBoundary": true,
    "boundaryPulseId": "0x..."
  },
  "erasedFieldHashes": {
    "rawText": "sha256:..."
  },
  "notRetained": [
    "rawText",
    "privatePayload",
    "unsupportedInference"
  ],
  "reason": "draft_or_unattested_compute_cannot_survive_boundary_as_raw_context"
}
```

## Why It Exists

A system should be able to prove that it released unsafe or stale memory without
publishing the memory it released.

That makes `ResidueAtom` different from a summary. It is not a smaller text
memory. It is the cryptographic residue of a memory release.

## Non-Claims

`ResidueAtom` does not prove semantic truth.
It does not prove the erased content was correct.
It does not recover the raw payload.
It does not authorize future action.

It only proves deterministic compression under a stated BoundaryFission policy.
