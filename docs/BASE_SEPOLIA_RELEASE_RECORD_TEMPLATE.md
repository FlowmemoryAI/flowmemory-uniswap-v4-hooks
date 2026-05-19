# Base Sepolia Release Record Template

Copy this file into `releases/base-sepolia/YYYY-MM-DD-hook-release.md` when the first Base Sepolia memory-signal hook is deployed.

Do not fill this template with private keys, RPC URLs, seed phrases, API keys, signed transactions, webhook URLs, or local operator secrets.

## Summary

```text
Release name:
Release date:
Prepared by:
Review status: draft | reviewed | published
```

## Network

```text
Network: Base Sepolia
Chain id: 84532
Official Uniswap deployments checked at:
PoolManager:
CREATE2 deployer:
```

## Source

```text
Repository:
Commit:
Solidity version:
Optimizer:
Optimizer runs:
v4-core version/commit reviewed:
v4-periphery version/commit reviewed:
```

## Hook Plan

```text
Contract:
Constructor args:
Init code hash:
Target hook bits:
Mined salt:
Computed hook address:
Computed hook low bits:
```

## Deployment

```text
Deployer address:
Deployment tx hash:
Deployment block:
Deployed bytecode hash:
Source verification URL:
Constructor args verification URL:
```

## Reader Evidence

```text
Reader version/commit:
Reader from block:
Reader to block:
Reader finality policy:
Current finalized block:
Observed AfterSwapObserved logs:
Observed FlowPulse logs:
Rejected logs:
```

## Sample Signal

```text
Sample tx hash:
Sample transaction index:
Sample log index:
Sample block number:
Sample block hash:
Sample receipt status:
Sample pulse id:
Sample rootfield id:
Sample actor:
Sample pool id:
Sample commitment:
Sample parent pulse id:
Sample sequence:
Sample occurredAt:
Sample uri:
```

## Boundary Statement

```text
This is a Base Sepolia hook release record.
This is not a Base mainnet production deployment claim.
The transaction is the proof envelope.
The FlowPulse is the memory artifact.
Receipt metadata is reader-derived after transaction execution.
The hook returns zero hook delta.
The hook does not take custody.
The hook does not implement dynamic fees.
The hook does not implement custom accounting.
The hook does not route swaps or control swap economics. Strict payload validation can reject malformed memory payloads for pools that intentionally opt into this hook.
```

## Reviewer Signoff

```text
Contract reviewer:
Reader/verifier reviewer:
Release reviewer:
Open issues:
Go/no-go:
```
