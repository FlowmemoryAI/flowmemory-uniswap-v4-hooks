# FlowMMU Example

FlowMMU is receipt-backed virtual memory for machine reality.

A machine can hold a virtual pointer to an expected FlowPulse boundary, but it
cannot read receipt facts until reader-attached evidence maps that pointer into
a read-only receipt page.

```text
unmapped PulsePointer
  -> read txHash
  -> ReceiptPageFault
  -> map matching FlowPulse receipt
  -> read txHash succeeds
```

Run the demo:

```bash
python tools/flow_mmu.py demo --pretty
```

Regenerate the example artifacts:

```bash
python tools/flow_mmu.py init \
  --agent-id demo-agent \
  --rootfield-id 0x1111111111111111111111111111111111111111111111111111111111111111 \
  --out examples/flow-mmu/page-table.initial.json \
  --pretty

python tools/flow_mmu.py alloc \
  --table examples/flow-mmu/page-table.initial.json \
  --pointer examples/flow-mmu/pulse-pointer.request.json \
  --out examples/flow-mmu/page-table.with-pointer.json \
  --pretty

python tools/flow_mmu.py deref \
  --table examples/flow-mmu/page-table.with-pointer.json \
  --pointer-id <pointerId> \
  --field txHash \
  --out examples/flow-mmu/fault.unmapped-txhash.json \
  --pretty

python tools/flow_mmu.py map \
  --table examples/flow-mmu/page-table.with-pointer.json \
  --flowpulse examples/flow-mmu/flowpulse.matching.json \
  --out examples/flow-mmu/page-table.mapped.json \
  --page-out examples/flow-mmu/receipt-page.example.json \
  --pretty
```

The public line:

```text
FlowMemory gives agents a page fault for reality.
```
