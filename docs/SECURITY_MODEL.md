# Security Model

This repository is intentionally conservative. The first public hook path should be simple enough for reviewers to understand without trusting private infrastructure.

## Security Goals

| Goal | Mechanism |
| --- | --- |
| Prevent arbitrary callback spoofing | `afterSwap` requires `msg.sender == poolManager`. |
| Keep hook permissions narrow | Planner targets only the `afterSwap` flag. |
| Avoid token custody risk | The hook has no payable receive path and no asset transfer logic. |
| Avoid custom accounting risk | The hook returns zero hook delta. |
| Avoid fee-policy risk | The hook has no dynamic-fee path. |
| Preserve event honesty | Receipt metadata is reader-derived, not emitted as if the hook knew it. |
| Make launch claims auditable | Public release path requires deployment and reader evidence. |

## Threat Model

```mermaid
flowchart TB
    Attacker["Attacker / confused integrator"]
    WrongCaller["Direct afterSwap call"]
    BadData["Invalid hookData"]
    MetadataClaim["False txHash/logIndex claim"]
    BroadHook["Overbroad hook permissions"]
    LiveClaim["Premature production claim"]

    WrongCaller --> Gate["PoolManager gate"]
    BadData --> Validation["rootfield/commitment validation"]
    MetadataClaim --> Boundary["reader-derived metadata boundary"]
    BroadHook --> Planner["afterSwap-only planner"]
    LiveClaim --> Release["public release checklist"]

    Gate --> Revert["revert"]
    Validation --> Revert
    Boundary --> Docs["documented non-goal + tests"]
    Planner --> Tests["permission tests"]
    Release --> Evidence["required deployment evidence"]
```

## On-Chain Invariants

The hook must preserve these properties:

1. Only the configured `PoolManager` can invoke the callback successfully.
2. `sender` cannot be zero.
3. `hookData` cannot be empty.
4. `rootfieldId` cannot be zero.
5. `commitment` cannot be zero.
6. Valid swaps emit `AfterSwapObserved`.
7. Valid swaps emit `FlowPulse`.
8. `afterSwap` returns the v4 callback selector and zero hook delta.
9. The hook has no token-transfer path.
10. The hook has no dynamic-fee path.

## Off-Chain Invariants

Readers and verifiers must preserve these properties:

1. Only accept logs from the expected hook address.
2. Check event topic signatures.
3. Decode `FlowPulse` according to the committed schema.
4. Require `pulseType == SWAP_MEMORY_SIGNAL` for swap memory.
5. Attach `txHash`, `transactionIndex`, and `logIndex` from receipts.
6. Apply a finality policy before presenting evidence as finalized.
7. Preserve raw log provenance for audit.

## Failure Modes

| Failure mode | Expected behavior |
| --- | --- |
| Wrong caller invokes `afterSwap` | Revert with `UnauthorizedPoolManager`. |
| Empty hook data | Revert with `EmptyHookData`. |
| Zero rootfield id | Revert with `ZeroRootfieldId`. |
| Zero commitment | Revert with `ZeroCommitment`. |
| Reader sees unfinalized logs | Keep status pending until finality policy is met. |
| Reader cannot fetch receipt | Do not claim txHash/logIndex-derived evidence. |
| Source verification missing | Do not call deployment public-ready. |

## What Reviewers Should Look For

Reviewers should start with:

- `contracts/FlowMemoryAfterSwapHook.sol`;
- `contracts/FlowMemoryHookPlanner.sol`;
- `test/FlowMemoryAfterSwapHook.t.sol`;
- `docs/PUBLIC_RELEASE_PATH.md`.

Key questions:

- Does the hook mutate token balances? It should not.
- Does the hook alter fees? It should not.
- Does the hook return non-zero delta? It should not.
- Does the hook claim to know receipt metadata? It should not.
- Does the release record show real deployment and reader evidence? It must before live claims.

## Non-Goals

The public hook reference does not claim:

- audited production readiness;
- production Base mainnet deployment;
- governance completeness;
- multisig completeness;
- verifier-network completeness;
- tokenomics;
- custody;
- dynamic fees.

Those may become future workstreams, but they are outside this first public hook surface.
