# FlowMMU v0 Draft Spec

FlowMMU is a local R&D primitive for receipt-backed dereference semantics.

Category sentence:

> FlowMMU gives agents a page fault for reality: a machine can hold a virtual
> pointer to a future FlowPulse, but it cannot read receipt facts until the
> transaction proof envelope maps that pointer into a read-only proof page.

## PulsePointer

```json
{
  "schema": "flowmemory.pulse_pointer.v0",
  "pointerId": "sha256:...",
  "pointerType": "virtual_flowpulse_address",
  "state": "unmapped",
  "agentId": "demo-agent",
  "virtualAddress": {
    "boundary": "uniswap_v4_afterSwap",
    "rootfieldId": "0x...",
    "commitment": "0x...",
    "hookAddress": "0x...",
    "subjectPoolId": "0x...",
    "parentPulseId": "0x..."
  },
  "forbiddenAtAllocation": [
    "txHash",
    "logIndex",
    "transactionIndex",
    "blockHash",
    "receiptStatus"
  ],
  "allowedReadsBeforeMapping": [
    "rootfieldId",
    "commitment",
    "hookAddress",
    "subjectPoolId",
    "parentPulseId",
    "boundary"
  ],
  "forbiddenReadsBeforeMapping": [
    "txHash",
    "logIndex",
    "transactionIndex",
    "blockHash",
    "receiptStatus"
  ]
}
```

## ReceiptPage

```json
{
  "schema": "flowmemory.receipt_page.v0",
  "pageId": "sha256:...",
  "pointerId": "sha256:...",
  "state": "mapped",
  "pageType": "read_only_flowpulse_receipt_page",
  "mappedBy": {
    "mapper": "reader_verifier",
    "source": "flowpulse_evidence"
  },
  "physicalAddress": {
    "artifactType": "FlowPulse",
    "boundary": "uniswap_v4_afterSwap",
    "chainId": "84532",
    "hookAddress": "0x...",
    "txHash": "0x...",
    "logIndex": "7",
    "transactionIndex": "3",
    "blockNumber": "123456",
    "blockHash": "0x...",
    "receiptStatus": "success",
    "rootfieldId": "0x...",
    "commitment": "0x...",
    "subjectPoolId": "0x...",
    "parentPulseId": "0x..."
  },
  "readOnly": true,
  "causalAddress": "sha256:...",
  "checks": {
    "readerAttachedTxHash": true,
    "readerAttachedLogIndex": true,
    "receiptStatusSuccess": true,
    "rootfieldMatches": true,
    "commitmentMatches": true,
    "hookAddressMatches": true,
    "subjectPoolMatches": true,
    "pageIdMatches": true
  }
}
```

## ReceiptPageFault

```json
{
  "schema": "flowmemory.receipt_page_fault.v0",
  "faultId": "sha256:...",
  "faultType": "forbidden_pre_receipt_read",
  "pointerId": "sha256:...",
  "attemptedAccess": {
    "operation": "read",
    "field": "txHash"
  },
  "reason": "txHash is receipt metadata and cannot be read before reader mapping",
  "requiredResolution": [
    "provide FlowPulse evidence",
    "require reader-attached txHash",
    "require reader-attached logIndex",
    "require matching rootfieldId",
    "require matching commitment"
  ]
}
```

## Rules

- A pointer cannot be allocated with receipt-only fields.
- An unmapped pointer may expose only virtual address fields.
- `txHash`, `logIndex`, receipt status, transaction index, block hash, and block
  facts require a mapped receipt page.
- Receipt pages are read-only.
- Mapping requires matching FlowPulse evidence with reader-attached receipt
  metadata.
- Address mismatches produce faults instead of partial pages.

## Systems Analogy

```text
PulsePointer = virtual address
FlowPulse receipt = physical page mapping
ReceiptPageFault = attempted dereference before mapping
ReceiptPage = read-only mapped proof page
```
