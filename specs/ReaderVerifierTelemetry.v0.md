# ReaderVerifierTelemetry.v0

Draft telemetry schema for FlowMemory reader/verifier operations.

This schema describes reader-derived evidence. It is not hook-time data.

## Record

```json
{
  "schema": "flowmemory.reader-verifier-telemetry.v0",
  "chainId": 8453,
  "hookAddress": "0x...",
  "poolManager": "0x...",
  "blockNumber": "123456",
  "txHash": "0x...",
  "transactionIndex": 12,
  "logIndex": 3,
  "eventName": "FlowPulse",
  "rootfieldId": "0x...",
  "pulseId": "0x...",
  "commitment": "0x...",
  "finality": {
    "status": "finalized",
    "confirmations": 64
  },
  "sourceVerification": {
    "status": "verified",
    "explorerUrl": "https://..."
  },
  "reader": {
    "name": "flowmemory-reader",
    "version": "0.1.0",
    "readAt": "2026-05-20T00:00:00Z"
  }
}
```

## Required Rule

`txHash`, `transactionIndex`, `logIndex`, finality, and source verification are
reader-derived facts. They must not be claimed as hook-time facts.

## Validation

A telemetry record is valid only when:

- `chainId`, `hookAddress`, and `poolManager` match the release packet;
- `txHash`, `transactionIndex`, and `logIndex` identify the emitted event;
- the event schema matches `FlowPulse`;
- finality status satisfies the release policy;
- source verification status is linked to the promoted hook deployment.
