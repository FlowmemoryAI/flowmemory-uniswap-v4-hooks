# AgentCommerceDifferential.v0

Agent Commerce Differential defines a local comparison between ordinary
agent-commerce rails and FlowMemory memory consistency.

The ordinary baseline is not a wallet implementation, x402 implementation,
indexer, escrow, custody surface, or production verifier. It is a deterministic
simulator for action surfaces that ordinary rails would accept.

## Case Schema

```json
{
  "schema": "flowmemory.agent_commerce_differential_case.v0",
  "caseId": "DIF-BAD-001",
  "name": "valid_signature_stale_memory_head",
  "ordinaryRails": {
    "walletSignatureValid": true,
    "spendPermissionInScope": true,
    "sessionKeyInScope": true,
    "x402PaymentRequirementSatisfied": true,
    "identityPresent": true,
    "receiptObservedByIndexer": true,
    "cacheFingerprintMatches": true
  },
  "flowmemoryChecks": {
    "spendLineDecision": "SPENDLINE_REJECTED",
    "fmm0Faults": ["stale_rootfield_head"]
  },
  "expected": {
    "ordinaryRailDecision": "ACCEPT",
    "flowmemoryDecision": "REJECT",
    "differentialReason": "valid_signature_does_not_imply_memory_currentness"
  }
}
```

## Report Schema

```json
{
  "schema": "flowmemory.agent_commerce_differential_report.v0",
  "casesChecked": 10,
  "validCasesAcceptedByBoth": 1,
  "differentialFailuresCaught": 9,
  "unsafeHistoriesAcceptedByOrdinaryBaselineOnly": 9,
  "escapedUnsafeHistories": 0
}
```

## Core Invariant

An action surface can be executable under ordinary rails and still be illegal
under memory consistency.

That is the category delta.

