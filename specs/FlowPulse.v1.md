# FlowPulse v1 Draft Spec

FlowPulse is the first public FlowMemory memory artifact.

It is emitted from an on-chain execution boundary and later bound to a transaction receipt by reader/verifier infrastructure.

## Category

FlowPulse is a boundary-born memory signal.

It is not the swap.

It is not the transaction.

It is not an indexer label.

The transaction is the proof envelope. The FlowPulse is the memory artifact.

## Required Boundary

For this repository, a FlowPulse is born at:

```text
Uniswap v4 PoolManager -> afterSwap -> FlowMemoryAfterSwapHook -> FlowPulse
```

The hook must preserve these properties:

- PoolManager-gated;
- `afterSwap` only;
- explicit `hookData`;
- non-zero `rootfieldId`;
- non-zero `commitment`;
- explicit actor;
- zero hook delta;
- no custody path;
- no fee path;
- no routing path;
- no custom accounting path;
- no hook-known `txHash`;
- no hook-known `logIndex`.

## Event Fields

The on-chain event carries:

| Field | Meaning |
| --- | --- |
| `pulseType` | Memory signal type. For this hook, `SWAP_MEMORY_SIGNAL`. |
| `pulseId` | Hook-derived local pulse id. |
| `rootfieldId` | Memory namespace receiving the pulse. |
| `actor` | Sender observed by the hook. May be a router or contract sender. |
| `subjectPoolId` | Pool context for the swap boundary. |
| `commitment` | Opaque downstream memory commitment. |
| `parentPulseId` | Optional prior memory artifact. |
| `sequence` | Per-rootfield sequence assigned by the hook. |
| `occurredAt` | Hook-time timestamp. |
| `uri` | Advisory pointer. Not authority. |

## Reader-Attached Fields

The reader attaches facts the hook cannot know during execution:

| Field | Source |
| --- | --- |
| `chainId` | RPC/network context. |
| `txHash` | Transaction receipt. |
| `transactionIndex` | Transaction receipt. |
| `logIndex` | Log receipt position. |
| `blockHash` | Block/receipt. |
| `blockNumber` | Block/receipt. |
| `receiptStatus` | Transaction receipt. |
| `emitter` | Log address. |
| `eventSignature` | Log topic 0. |
| `hookCodeHash` | Chain bytecode lookup. |
| `finalityStatus` | Reader policy. |

## Public Canonical ID

The hook cannot compute a public canonical id that depends on receipt metadata.

The reader can compute:

```text
flowPulsePublicId = keccak256(
  "FlowPulse/v1",
  chainId,
  txHash,
  logIndex,
  hookAddress,
  subjectPoolId,
  rootfieldId,
  commitment
)
```

This makes the public memory artifact receipt-bound.

## Verification Checks

A verifier should check:

- receipt exists;
- receipt status is successful;
- log exists at the claimed `logIndex`;
- log emitter equals the hook address;
- event signature equals `FlowPulse`;
- decoded `rootfieldId` is non-zero;
- decoded `commitment` is non-zero;
- decoded `subjectPoolId` matches the expected pool context;
- hook bytecode hash matches the release record;
- hook release claims `afterSwap` only and zero hook delta;
- reader metadata was attached after execution.

## Minimal Proof Object

```json
{
  "schema": "flowmemory.flowpulse.v1",
  "status": "verified",
  "flowPulsePublicId": "0x...",
  "chainId": 84532,
  "txHash": "0x...",
  "logIndex": 7,
  "hookAddress": "0x...",
  "subjectPoolId": "0x...",
  "rootfieldId": "0x...",
  "commitment": "0x...",
  "checks": {
    "receiptFound": true,
    "receiptSuccessful": true,
    "flowPulseLogFound": true,
    "emitterMatchesHook": true,
    "rootfieldNonZero": true,
    "commitmentNonZero": true,
    "hookBytecodeMatchesRelease": true,
    "readerAttachedReceiptMetadata": true
  }
}
```

## Design Line

FlowPulse makes DeFi execution memory-addressable without letting memory logic touch swap economics.
