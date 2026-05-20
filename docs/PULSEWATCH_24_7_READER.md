# PulseWatch 24/7 Reader

The Uniswap v4 hook is transaction-triggered.

It does not wake up by itself. It does not run every second. It does not create
memory without a PoolManager transaction calling the hook.

PulseWatch is the always-on layer.

```text
Uniswap v4 transaction
  -> afterSwap hook
  -> FlowPulse log
  -> transaction receipt
  -> PulseWatch reader/verifier
  -> append-only memory record
  -> downstream FlowMemory / Rootflow systems
```

## Why This Exists

The hook is the verified on-chain emission boundary.

PulseWatch is the continuous memory ingestion boundary.

That split is the correct architecture:

- the hook stays narrow, auditable, and transaction-bound;
- the reader runs 24/7 outside the EVM;
- receipt metadata stays reader-derived;
- every accepted log advances an explicit cursor;
- duplicate logs are skipped;
- rejected logs carry typed reasons;
- memory records are append-only.

## What Runs 24/7

PulseWatch can run continuously as an operator process:

```bash
python tools/pulse_watch.py run \
  --rpc-url "$FLOWMEMORY_RPC_URL" \
  --hook-address "$FLOWMEMORY_HOOK_ADDRESS" \
  --from-block "$FLOWMEMORY_FROM_BLOCK" \
  --state .flowmemory/pulsewatch-state.json \
  --memory-store .flowmemory/pulsewatch-memory.jsonl
```

For a single polling pass:

```bash
python tools/pulse_watch.py run \
  --rpc-url "$FLOWMEMORY_RPC_URL" \
  --hook-address "$FLOWMEMORY_HOOK_ADDRESS" \
  --from-block "$FLOWMEMORY_FROM_BLOCK" \
  --state .flowmemory/pulsewatch-state.json \
  --memory-store .flowmemory/pulsewatch-memory.jsonl \
  --once
```

No private key is required. PulseWatch reads logs and receipts; it does not
submit transactions.

## Local Demo

Run:

```bash
python tools/pulse_watch.py demo
python tools/pulse_watch.py demo --json --pretty
```

Expected shape:

```text
FlowMemory PulseWatch

Watch report:
  status: PASS
  records seen: 2
  records accepted: 2
  memory records written: 2
  cursor: 119 -> 121

Result:
  The hook is transaction-triggered. PulseWatch is the always-on memory layer.
```

## What The Hook Does

The hook emits a `FlowPulse` during a valid Uniswap v4 lifecycle call.

It can only execute when the PoolManager calls it inside a transaction.

That is a feature, not a weakness. It keeps the on-chain primitive minimal and
auditable.

## What PulseWatch Does

PulseWatch:

- polls `eth_getLogs`;
- fetches transaction receipts;
- decodes `AfterSwapObserved`;
- decodes `FlowPulse`;
- attaches `txHash`, `transactionIndex`, `logIndex`, block facts, receipt
  status, and finality classification;
- writes append-only memory records;
- stores a cursor;
- skips duplicate log ids;
- rejects invalid records with explicit reasons.

## Validation Rules

PulseWatch rejects or flags:

- wrong reader schema;
- missing hook address;
- missing chain id;
- record hook mismatch;
- missing `txHash`;
- missing `logIndex`;
- zero `rootfieldId`;
- zero `commitment`;
- rejected record without a reason;
- hook-time receipt metadata smuggling.

## Non-Claims

PulseWatch does not claim production verifier readiness, live Base deployment,
custody, fund protection, or that hooks run without transactions.

The correct claim is:

```text
The hook emits memory during transactions. PulseWatch keeps the memory pipeline alive continuously.
```
