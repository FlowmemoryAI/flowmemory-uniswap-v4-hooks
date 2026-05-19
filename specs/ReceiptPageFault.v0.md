# ReceiptPageFault v0 Draft Spec

`ReceiptPageFault` is a deterministic runtime exception for machine agents.

It is thrown when an agent tries to read receipt-only facts from a FlowPulse
pointer before reader-attached receipt metadata exists, or when attempted mapping
fails.

## Fault Types

| Fault | Meaning |
| --- | --- |
| `forbidden_pre_receipt_read` | The agent tried to read `txHash`, `logIndex`, or another receipt-only field before mapping. |
| `missing_receipt_metadata` | Evidence exists but lacks reader-attached receipt coordinates. |
| `address_mismatch` | FlowPulse evidence does not match the pointer's virtual address. |
| `illegal_write` | The agent tried to mutate a read-only receipt page. |
| `generic_log_not_mappable` | The evidence is not a FlowPulse receipt record. |
| `unmapped_pointer` | The requested pointer is not allocated or not mapped. |

## Schema

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
  ],
  "handlerHint": "map_with_flowpulse_receipt_or_treat_as_unresolved_external_fact"
}
```

## Why It Matters

Most agent systems treat expected facts, inferred facts, logs, and settled facts
as text in the same context window.

`ReceiptPageFault` makes those states different at runtime.

The agent can point at a boundary before proof exists. It cannot dereference
reality until the receipt maps it.
