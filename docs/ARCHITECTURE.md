# Architecture

FlowMemory's first public hook path is designed around a small contract surface and a clear evidence boundary.

The hook does not try to be a full protocol inside a swap callback. It records a memory signal at the moment Uniswap v4 gives the hook a valid post-swap execution point, then lets readers and verifiers attach receipt-aware facts after the transaction exists.

## System Context

```mermaid
flowchart TB
    subgraph Uniswap["Uniswap v4"]
        PoolManager["PoolManager"]
        Pool["Pool state"]
    end

    subgraph HookRepo["flowmemory-uniswap-v4-hooks"]
        Hook["FlowMemoryAfterSwapHook"]
        Planner["FlowMemoryHookPlanner"]
        FlowPulse["FlowPulse event schema"]
    end

    subgraph Offchain["FlowMemory off-chain evidence layer"]
        Reader["Reader / indexer"]
        Verifier["Verifier checks"]
        Rootflow["Rootflow memory state"]
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
    PM->>PM: execute swap and compute delta
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

## Trust Boundaries

```mermaid
flowchart LR
    subgraph Onchain["On-chain execution"]
        PM["PoolManager"]
        Hook["FlowMemoryAfterSwapHook"]
        Logs["EVM logs"]
    end

    subgraph Derived["Reader-derived facts"]
        Receipt["transaction receipt"]
        TxHash["txHash"]
        LogIndex["logIndex"]
        Finality["block/finality policy"]
    end

    subgraph Memory["FlowMemory interpretation"]
        Reader["reader"]
        Checks["schema + provenance checks"]
        MemorySignal["memory signal"]
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

## Component Responsibilities

| Component | Responsibility | What it must not do |
| --- | --- | --- |
| `FlowMemoryAfterSwapHook` | Validate callback caller, decode memory payload, emit `AfterSwapObserved` and `FlowPulse`. | Custody tokens, override fees, fabricate receipt metadata, perform custom accounting. |
| `FlowMemoryHookPlanner` | Compute hook permission bits and CREATE2 candidate addresses for Base Sepolia planning. | Deploy contracts, hold keys, print secrets. |
| `FlowPulse` | Define the public event schema and stable pulse type ids. | Describe off-chain receipt facts as on-chain facts. |
| Reader / indexer | Read logs, attach receipt fields, enforce finality windows. | Rewrite event payloads or treat unfinalized logs as final. |
| Verifier | Check event schema, provenance, expected contract, topic signatures, and finality. | Trust arbitrary UI claims without logs. |

## Why The Hook Surface Is Small

The public release needs a low-ambiguity contract. Each additional hook permission increases the number of execution paths that reviewers, pool creators, and users must understand.

FlowMemory starts with exactly one callback:

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

That choice keeps the first public hook focused on evidence, not hidden control.
