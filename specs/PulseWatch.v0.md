# PulseWatch v0

PulseWatch is the always-on reader/verifier loop for FlowMemory hook evidence.

## Boundary

The Uniswap v4 hook is transaction-triggered.

PulseWatch is continuous.

```text
transaction-bound hook emission
  -> reader-derived receipt evidence
  -> append-only memory record
  -> cursor advance
```

## State

```json
{
  "schema": "flowmemory.pulsewatch_state.v0",
  "chainId": "84532",
  "hookAddress": "0x...",
  "cursorBlock": 0,
  "seenLogIds": [],
  "recordsObserved": 0,
  "memoryRecordsWritten": 0,
  "rejectedRecords": 0
}
```

## Memory Record

```json
{
  "schema": "flowmemory.pulsewatch_memory_record.v0",
  "chainId": "84532",
  "hookAddress": "0x...",
  "eventName": "FlowPulse",
  "status": "l2_confirmed",
  "txHash": "0x...",
  "logIndex": "0",
  "blockNumber": "0",
  "finality": {},
  "pulseId": "0x...",
  "rootfieldId": "0x...",
  "commitment": "0x...",
  "proofEnvelope": {
    "transactionIndex": "0",
    "receiptStatus": "success",
    "blockHash": "0x..."
  }
}
```

## Validity Rules

A PulseWatch batch is valid when:

- reader output uses `flowmemory.hook_log_reader.v0`;
- chain id is present;
- hook address is present;
- each record uses `flowmemory.uniswap_v4_swap_signal.v0`;
- record hook address matches batch hook address;
- each accepted record has `txHash` and `logIndex`;
- `FlowPulse` records do not use zero `rootfieldId`;
- `FlowPulse` records do not use zero `commitment`;
- rejected records include rejection reasons;
- receipt metadata is reader-derived, not hook-time.

## Non-Claims

PulseWatch v0 does not claim production verifier readiness, live deployment,
custody, fund protection, or hooks that run without transactions.
