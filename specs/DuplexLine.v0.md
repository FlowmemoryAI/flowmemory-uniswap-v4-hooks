# DuplexLine v0

Status: R&D draft.

DuplexLine is a local consistency model for autonomous buyer/seller exchange
histories. It does not escrow payments, authorize wallets, custody funds,
protect funds, prove work quality, or prove semantic truth. It checks whether a
declared buyer spend and seller work delivery can be serialized against
compatible receipt-bound FlowPulse memory heads.

## Schemas

### DuplexLine Case

```json
{
  "schema": "flowmemory.duplexline_case.v0",
  "caseId": "DPL-OK-001",
  "title": "valid buyer seller exchange",
  "expectedDecision": "ACCEPT_DUPLEXLINE",
  "exchange": {},
  "ledger": {}
}
```

### DuplexLine Exchange

```json
{
  "schema": "flowmemory.duplexline_exchange.v0",
  "exchangeId": "duplexline-exchange",
  "buyerAgentId": "erc8004:buyer-agent-001",
  "sellerAgentId": "erc8004:seller-agent-009",
  "buyerWallet": "0x00000000000000000000000000000000000000aa",
  "buyerRootfieldId": "bytes32",
  "sellerRootfieldId": "bytes32",
  "buyerMemoryHead": "flowpulse-buyer-head",
  "sellerMemoryHead": "flowpulse-seller-head",
  "taskCommitment": "sha256:task-agent-market-data",
  "sellerTaskCommitment": "sha256:task-agent-market-data",
  "workCommitment": "sha256:work-agent-market-data",
  "sellerIdentityRef": "erc8004:seller-agent-009",
  "workAuthorAgentId": "erc8004:seller-agent-009",
  "authorizedPayee": "x402://market-data.example",
  "paymentRecipient": "x402://market-data.example",
  "serviceEndpointHash": "sha256:service-endpoint-market-data",
  "deliveryEndpointHash": "sha256:service-endpoint-market-data",
  "paymentRequirement": {
    "asset": "USDC",
    "amount": "0.010000",
    "recipient": "x402://market-data.example",
    "taskCommitment": "sha256:task-agent-market-data"
  },
  "paymentRequirementHash": "sha256:...",
  "spendSurface": "x402_payment",
  "requestedAction": "approve_for_wallet_submission",
  "axiomPatchVerdict": "allowed",
  "computeReuseVerdict": "NOT_APPLICABLE",
  "cacheLineageVerdict": "NOT_APPLICABLE",
  "buyerComputePolicy": {
    "freshComputeRequired": false,
    "reuseAllowed": true,
    "attestationRequired": false
  },
  "sellerStatePhase": "FMM0_LIVE",
  "claimedPaymentReceiptFacts": [],
  "serialSchedule": {
    "events": []
  }
}
```

### DuplexLine Ledger

```json
{
  "schema": "flowmemory.duplexline_ledger.v0",
  "ledgerId": "duplexline-ledger",
  "buyerCurrentMemoryHead": "flowpulse-buyer-head",
  "sellerCurrentMemoryHead": "flowpulse-seller-head",
  "spentBuyerIntentCommitments": [],
  "consumedPaymentRequirementHashes": [],
  "consumedWorkCommitments": [],
  "consumedExchangeDedupeKeys": [],
  "buyerReceiptBoundaries": [],
  "sellerReceiptBoundaries": []
}
```

## Decisions

`ACCEPT_DUPLEXLINE`: the exchange is locally memory-consistent.

`REJECT_DUPLEXLINE`: the exchange violates a DuplexLine invariant, the embedded
buyer SpendLine check, or the combined FlowSerial history.

## Invariants

- case and exchange schemas match;
- buyer agent exists;
- seller agent exists;
- buyer memory head matches the buyer ledger;
- seller memory head matches the seller ledger;
- task commitment exists;
- work commitment exists;
- seller task commitment matches the exchange task;
- payment requirement hash matches the declared requirement;
- payment requirement task matches the exchange task;
- seller identity, work author, authorized payee, and payment recipient are bound;
- service endpoint and delivery endpoint are conserved;
- payment requirement has not already been consumed;
- work commitment has not already been consumed;
- exchange dedupe key has not already been consumed;
- seller work history serializes under FlowSerial;
- buyer SpendLine is accepted;
- paid compute/service work does not contradict compute/cache reuse gates;
- buyer compute policy allows the seller reuse path;
- serial schedule is acyclic;
- payment receipt facts are not claimed before settlement;
- seller state is FMM-0 live;
- combined buyer/seller exchange history is FlowSerial-serializable.

## Forbidden Cases

- seller output wrong task;
- buyer stale memory head;
- payment requirement drift;
- seller missing FlowSerial;
- compute reuse inconsistency for paid work;
- seller stale memory head;
- duplicate buyer intent replay;
- counterparty payee rebinding;
- work replay across buyer;
- payment requirement double consumed;
- buyer requires fresh compute while seller reuses;
- impossible exchange schedule;
- payment receipt smuggled before settlement;
- task endpoint drift;
- seller reader-derived state presented as FMM-0 live.

## Named Invariant Coverage

- `DPL-I1`: Co-Serial Exchange.
- `DPL-I2`: Counterparty-Payee Binding.
- `DPL-I3`: Quote-Task-Work Conservation.
- `DPL-I4`: Dual-Head Compatibility.
- `DPL-I5`: No Pre-Receipt Economic Claims.
- `DPL-I6`: Buyer Reuse Policy Dominance.
- `DPL-I7`: Idempotent Exchange Commitment.
- `DPL-I8`: No Quality/Truth Upgrade.

## Non-Claims

DuplexLine does not claim custody, escrow, fund protection, wallet enforcement,
work quality, semantic truth, model correctness, production verifier readiness,
or live mainnet deployment.
