# Integration Blueprint

This document describes how the hook repo fits into the larger FlowMemory public launch without requiring the full private system to be public on day one.

## Layers

```mermaid
flowchart TB
    L1["Layer 1: Hook contract"]
    L2["Layer 2: Reader/indexer"]
    L3["Layer 3: Verifier policy"]
    L4["Layer 4: Rootflow memory state"]
    L5["Layer 5: Public dashboard/API"]

    L1 --> L2 --> L3 --> L4 --> L5
```

| Layer | Public artifact | Launch expectation |
| --- | --- | --- |
| Hook contract | This repo | Public, tested, source-verifiable. |
| Reader/indexer | Release evidence, later code package | Must show receipt-derived records before live claims. |
| Verifier policy | Public checklist/report | Must explain accepted/rejected evidence. |
| Rootflow memory state | Public summary or dashboard | Must not overstate finality or verifier scope. |
| Public dashboard/API | FlowMemory public surface | Must show status, contract, logs, and boundaries. |

## Data Flow

```mermaid
flowchart LR
    Swap["Uniswap v4 swap"] --> Hook["afterSwap hook"]
    Hook --> Events["AfterSwapObserved + FlowPulse"]
    Events --> Reader["reader/indexer"]
    Reader --> Evidence["normalized evidence record"]
    Evidence --> Verifier["verifier checks"]
    Verifier --> Rootflow["Rootflow state update"]
    Rootflow --> Public["public page/API"]
```

## Integration Contracts

The hook repo exposes a small contract interface:

- `afterSwap(...) returns (bytes4 selector, int128 hookDelta)`;
- `encodeSwapHookData(...) returns (bytes memory)`;
- `hasPermissionedHookAddress() returns (bool)`;
- `AfterSwapObserved`;
- `FlowPulse`.

The downstream system should treat those as the stable boundary. Anything more complex belongs outside the hook.

## Public API Shape

A later public API can expose:

```text
GET /hooks/uniswap-v4/status
GET /hooks/uniswap-v4/releases/latest
GET /hooks/uniswap-v4/signals?chainId=84532
GET /hooks/uniswap-v4/signals/:txHash/:logIndex
```

The API should never require browser users to submit private keys, seed phrases, RPC credentials, API keys, or wallet vault material.

## Release Dependencies

```mermaid
flowchart TD
    A["Public hook repo"] --> B["Mined Base Sepolia hook address"]
    B --> C["Verified deployment"]
    C --> D["Observed hook logs"]
    D --> E["Reader-derived receipts"]
    E --> F["Verifier report"]
    F --> G["Public status page"]
    G --> H["Mainnet go/no-go review"]
```

## What Can Be Shared First

Share this repo first when you want to show:

- the contract architecture;
- why `afterSwap` is the chosen lifecycle point;
- the event model;
- what safety boundaries are intentionally absent;
- how reviewers can run the tests;
- what evidence will be required next.

Do not use this repo alone to claim:

- Base Sepolia deployment;
- Base mainnet deployment;
- production readiness;
- audited custody;
- completed verifier network.

## Suggested Public Narrative

FlowMemory's first public Uniswap v4 work is an `afterSwap` hook that emits a verifiable memory signal when swap activity reaches a post-execution lifecycle point. The hook keeps the on-chain surface narrow: PoolManager-gated, afterSwap-only, zero hook delta, no custody, no dynamic fee path. Receipt facts are derived by readers after the transaction lands. That separation gives the public a clean contract to inspect now and a concrete evidence path for Base Sepolia next.
