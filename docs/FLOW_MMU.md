# FlowMMU

FlowMMU is receipt-backed virtual memory for machine reality.

FlowMemory gives agents a page fault for reality.

A machine can hold a virtual pointer to an expected FlowPulse boundary, but it
cannot read receipt facts until a reader maps that pointer with actual
transaction evidence.

```text
PulsePointer(unmapped)
  -> read txHash
  -> ReceiptPageFault
  -> map matching FlowPulse evidence
  -> ReceiptPage(read-only)
  -> read txHash succeeds
```

## Why This Is Different

This is not memory storage.
This is not indexing.
This is not a dashboard.
This is not a policy gate.
This is not proof exploration.

FlowMMU gives agents dereference semantics for external proof coordinates:

- expected boundary facts live in a virtual address;
- receipt facts live only in a mapped receipt page;
- receipt pages are read-only;
- early receipt reads throw `ReceiptPageFault`;
- mismatched evidence throws an address-mismatch fault.

## Why The Boundary Matters

The hook emits the FlowPulse memory artifact. The transaction is the proof
envelope. The reader attaches `txHash`, `logIndex`, receipt status, and block
facts after execution.

That timing gap is the primitive.

Before receipt mapping:

```text
rootfieldId + commitment + hook + pool = readable virtual address
txHash + logIndex + receiptStatus = unavailable
```

After receipt mapping:

```text
receipt metadata = read-only proof page
```

Without the FlowPulse boundary, this is just a log lookup. With FlowPulse, it is
address translation for machine belief about external execution.

## Demo

```bash
python tools/flow_mmu.py demo --pretty
python -m unittest tools.test_flow_mmu
```

Expected story:

```text
Allocated PulsePointer.
Attempted txHash read before mapping.
ReceiptPageFault thrown.

Mapped FlowPulse receipt.
ReceiptPage created.
Retried txHash read.
Read succeeded.

Attempted receipt write.
ReceiptPageFault thrown.
```

## Non-Claims

FlowMMU does not prove semantic truth.
It does not prove model correctness.
It does not prove GPU execution.
It does not accelerate GPUs.
It does not control swaps.
It does not custody or protect funds.
It is not audited production infrastructure.
It is not live mainnet infrastructure.
It does not mean the hook knows `txHash` or `logIndex`.

It proves whether an external proof coordinate is mapped, readable, and
receipt-bound under the declared FlowPulse address.
