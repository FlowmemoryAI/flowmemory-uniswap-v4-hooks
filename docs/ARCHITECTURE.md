# Architecture

FlowMemory separates execution, emission, evidence, and memory.

That separation is the architecture. The Uniswap v4 swap is execution. The `afterSwap` hook is the verified on-chain emission boundary. The EVM receipt is the proof envelope. The `FlowPulse` is the memory artifact.

This repository is not trying to put a full protocol inside a swap callback. It defines the first public memory-native hook primitive: a narrow, PoolManager-gated surface where DeFi execution can emit a protocol-level memory signal.

## Layer Model

```mermaid
flowchart TB
    subgraph Execution["Execution Layer"]
        PM["Uniswap v4 PoolManager"]
        Swap["swap lifecycle"]
        Boundary["afterSwap boundary"]
    end

    subgraph Emission["Memory Emission Layer"]
        Hook["FlowMemoryAfterSwapHook"]
        Pulse["FlowPulse"]
        Rootfield["rootfieldId"]
        Commitment["commitment"]
        Parent["parentPulseId"]
        Uri["uri"]
    end

    subgraph Evidence["Evidence Layer"]
        Logs["EVM logs"]
        Receipts["transaction receipts"]
        TxHash["txHash"]
        LogIndex["logIndex"]
        Finality["finality policy"]
    end

    subgraph Memory["Memory Layer"]
        Reader["FlowMemory reader"]
        Verifier["verifier policy"]
        Rootflow["FlowMemory / Rootflow state"]
    end

    PM --> Swap --> Boundary --> Hook
    Hook --> Pulse
    Rootfield --> Pulse
    Commitment --> Pulse
    Parent --> Pulse
    Uri --> Pulse
    Pulse --> Logs
    Logs --> Reader
    Receipts --> Reader
    TxHash --> Reader
    LogIndex --> Reader
    Finality --> Reader
    Reader --> Verifier --> Rootflow
```

## System Context

```mermaid
flowchart TB
    subgraph Uniswap["Uniswap v4 execution"]
        PoolManager["PoolManager"]
        Pool["Pool state"]
    end

    subgraph HookRepo["flowmemory-uniswap-v4-hooks"]
        Hook["FlowMemoryAfterSwapHook"]
        Planner["FlowMemoryHookPlanner"]
        FlowPulse["FlowPulse schema"]
    end

    subgraph EvidenceLayer["Receipt-aware evidence"]
        Reader["Reader / indexer"]
        Verifier["Verifier checks"]
    end

    subgraph MemoryLayer["FlowMemory memory"]
        Rootflow["Rootflow / downstream memory state"]
    end

    PoolManager --> Pool
    PoolManager -->|afterSwap callback| Hook
    Planner -->|mines CREATE2 address with 0x40 hook bits| Hook
    Hook -->|AfterSwapObserved| Reader
    Hook -->|FlowPulse SWAP_MEMORY_SIGNAL| Reader
    FlowPulse --> Hook
    Reader -->|adds txHash, logIndex, finality| Verifier
    Verifier --> Rootflow
```

## Execution Flow

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant PM as PoolManager
    participant Hook as FlowMemoryAfterSwapHook
    participant EVM as EVM logs
    participant Reader
    participant Verifier

    User->>PM: swap
    PM->>PM: execute swap lifecycle
    PM->>Hook: afterSwap(sender, PoolKey, SwapParams, swapDelta, hookData)
    Hook->>Hook: require msg.sender == PoolManager
    Hook->>Hook: require sender != 0
    Hook->>Hook: require hookData is non-empty
    Hook->>Hook: decode FlowMemorySwapHookData
    Hook->>Hook: require rootfieldId and commitment are non-zero
    Hook->>EVM: AfterSwapObserved(poolManager, sender, poolId, rootfieldId, commitment, hookDataHash)
    Hook->>EVM: FlowPulse(pulseId, rootfieldId, sender, 4, poolId, commitment, parentPulseId, sequence, occurredAt, uri)
    Hook-->>PM: afterSwap selector, 0 hookDelta
    Reader->>EVM: fetch receipt/logs after block inclusion
    Reader->>Verifier: submit logs + txHash + logIndex + block context
    Verifier->>Verifier: check topics, payload, finality, schema
```

The hook emits the memory signal. The reader proves where it landed.

## Component Responsibilities

| Component | Responsibility | What it must not do |
| --- | --- | --- |
| `FlowMemoryAfterSwapHook` | Validate callback caller, decode memory payload, emit `AfterSwapObserved` and `FlowPulse`. | Custody tokens, override fees, route swaps, fabricate receipt metadata, perform custom accounting. |
| `FlowMemoryHookPlanner` | Compute hook permission bits and CREATE2 candidate addresses for Base Sepolia planning. | Deploy contracts, hold keys, print secrets. |
| `FlowPulse` | Define the public memory signal schema and stable pulse type ids. | Describe off-chain receipt facts as on-chain facts. |
| Reader / indexer | Read logs, attach receipt fields, enforce finality windows. | Rewrite event payloads or treat unfinalized logs as final. |
| Verifier | Check event schema, provenance, expected contract, topic signatures, and finality. | Trust arbitrary UI claims without logs. |
| FlowMemory / Rootflow | Consume verified pulse records as memory artifacts. | Treat ordinary swaps as FlowMemory without an emitted pulse. |

## Trust Boundaries

```mermaid
flowchart LR
    subgraph Onchain["On-chain emission"]
        PM["PoolManager"]
        Hook["FlowMemoryAfterSwapHook"]
        Logs["EVM logs"]
    end

    subgraph ProofEnvelope["Transaction proof envelope"]
        Receipt["transaction receipt"]
        TxHash["txHash"]
        LogIndex["logIndex"]
        Finality["block/finality policy"]
    end

    subgraph Memory["FlowMemory interpretation"]
        Reader["reader"]
        Checks["schema + provenance checks"]
        MemorySignal["FlowPulse memory artifact"]
    end

    PM --> Hook --> Logs
    Logs --> Reader
    Receipt --> Reader
    TxHash --> Reader
    LogIndex --> Reader
    Finality --> Reader
    Reader --> Checks --> MemorySignal

    Hook -. cannot know .-> TxHash
    Hook -. cannot know .-> LogIndex
```

The hook only emits what the EVM can know inside execution. Receipt fields are outside that boundary.

## Why The Hook Surface Is Small

The hook is deliberately minimal because the primitive is not execution control. The primitive is verifiable memory emission.

```mermaid
flowchart TD
    All["Uniswap v4 hook callbacks"] --> BeforeSwap["beforeSwap disabled"]
    All --> AfterSwap["afterSwap enabled"]
    All --> Liquidity["liquidity callbacks disabled"]
    All --> Donate["donate callbacks disabled"]
    All --> Init["initialize callbacks disabled"]
    AfterSwap --> ReturnDelta["afterSwapReturnDelta disabled"]
    AfterSwap --> FlowPulse["emit FlowPulse"]
```

Most hooks change what a swap does. FlowMemory changes what a swap can prove.
