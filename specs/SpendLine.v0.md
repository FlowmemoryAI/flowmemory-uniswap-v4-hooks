# SpendLine v0

Status: R&D draft.

SpendLine is a local consistency model for autonomous agent spend histories.
It does not authorize wallets, custody funds, protect funds, or prove semantic
truth. It checks whether a declared spend can be serialized against a
receipt-bound FlowPulse memory head.

## Schemas

### SpendLine Case

```json
{
  "schema": "flowmemory.spendline_case.v0",
  "caseId": "SPL-OK-001",
  "title": "valid spend after memory head",
  "expectedDecision": "ACCEPT_SPENDLINE",
  "request": {},
  "ledger": {}
}
```

### SpendLine Request

```json
{
  "schema": "flowmemory.spendline_request.v0",
  "requestId": "spendline-request",
  "agentId": "agent-base-001",
  "agentIdentity": "erc8004:8453:42",
  "wallet": "0x00000000000000000000000000000000000000aa",
  "rootfieldId": "bytes32",
  "currentMemoryHead": "flowpulse-head-a",
  "spendIntentCommitment": "bytes32",
  "proposedSpendCommitment": "bytes32",
  "asset": "USDC",
  "amount": "0.010000",
  "target": "x402://market-data.example",
  "spendSurface": "x402_payment",
  "requestedAction": "approve_for_wallet_submission",
  "axiomPatchVerdict": "allowed",
  "paymentRequirement": {
    "asset": "USDC",
    "amount": "0.010000",
    "recipient": "x402://market-data.example"
  },
  "computeReuseVerdict": "NOT_APPLICABLE",
  "cacheLineageVerdict": "NOT_APPLICABLE",
  "declaredOrder": 3,
  "observedBoundaries": ["flowpulse-head-a"],
  "claimedReceiptFacts": [
    { "field": "txHash", "boundaryId": "flowpulse-head-a" },
    { "field": "logIndex", "boundaryId": "flowpulse-head-a" }
  ],
  "postSpendFlowPulse": "flowpulse-head-a"
}
```

### SpendLine Ledger

```json
{
  "schema": "flowmemory.spendline_ledger.v0",
  "ledgerId": "spendline-ledger",
  "rootfieldId": "bytes32",
  "wallet": "0x00000000000000000000000000000000000000aa",
  "currentMemoryHead": "flowpulse-head-a",
  "spentIntentCommitments": [],
  "receiptBoundaries": []
}
```

## Decisions

`ACCEPT_SPENDLINE`: the spend is locally memory-consistent.

`REJECT_SPENDLINE`: the spend violates a SpendLine invariant or FlowSerial
finds an impossible history.

## Invariants

- case, request, and ledger schemas match;
- rootfield is nonzero;
- wallet is present;
- spend intent commitment is nonzero;
- proposed spend commitment is nonzero;
- request current memory head matches the ledger current memory head;
- post-spend FlowPulse is present;
- post-spend FlowPulse matches the current memory head;
- spend intent has not already been consumed;
- AxiomPatch verdict allows the requested spend surface;
- x402-style payment requirements match the declared spend;
- paid compute/service work does not contradict compute/cache reuse gates;
- FlowSerial certifies the history as serializable.

## Forbidden Cases

- stale memory head spend;
- duplicate intent replay;
- hallucinated receipt claim before receipt boundary;
- missing post-spend FlowPulse;
- rootfield rollback spend;
- AxiomPatch downgrade ignored;
- x402 payment requirement mismatch;
- compute reuse inconsistency for paid work.

## Non-Claims

SpendLine does not claim custody, fund protection, wallet enforcement, semantic
truth, model correctness, production verifier readiness, or live mainnet
deployment.
