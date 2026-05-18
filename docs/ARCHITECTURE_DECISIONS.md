# Architecture Decisions

This file records the design decisions that make the first public hook surface reviewable.

The goal is not to make the hook impressive by adding more logic. The goal is to make the hook credible by keeping the on-chain boundary small, proving the invariants, and leaving interpretation to explicit reader/verifier layers.

## ADR-001: Use `afterSwap` As The First Hook Point

Status: accepted.

Decision:

FlowMemory's first Uniswap v4 hook surface uses `afterSwap`, not `beforeSwap`, liquidity hooks, donate hooks, or return-delta hooks.

Reasoning:

- FlowMemory wants a memory signal after a swap reaches the post-execution lifecycle point.
- `beforeSwap` suggests control or policy before execution, which is not the first public use case.
- Return-delta hooks increase custom-accounting surface area.
- Liquidity and donate hooks may become useful later, but they are not necessary for swap memory.

Consequences:

- The first hook is easier to audit.
- The hook is not a routing, policy, or fee engine.
- The public story is clearer: completed swap activity can become memory evidence.

## ADR-002: Emit Evidence, Do Not Hold Assets

Status: accepted.

Decision:

The hook emits `AfterSwapObserved` and `FlowPulse`. It does not hold tokens, transfer assets, or implement custody logic.

Reasoning:

- Custody would change the risk profile immediately.
- The public first release should not require users to trust a new asset-holding system.
- FlowMemory's near-term value is evidence and memory, not custody.

Consequences:

- The hook has a smaller attack surface.
- The public repo can be reviewed without a broader token-security audit.
- Future custody-related features, if any, must be separate work.

## ADR-003: Return Zero Hook Delta

Status: accepted.

Decision:

`afterSwap` returns zero hook delta.

Reasoning:

- Non-zero deltas imply custom accounting.
- Custom accounting is powerful but not required for the first memory-signal hook.
- A zero-delta hook is easier for pool creators and reviewers to understand.

Consequences:

- The hook does not adjust swap accounting.
- The first public hook can focus on signal emission.
- Later designs that need custom accounting must be reviewed as new designs.

## ADR-004: Keep Receipt Metadata Reader-Derived

Status: accepted.

Decision:

`txHash`, `transactionIndex`, `logIndex`, and receipt status are not emitted as hook-known facts. Readers attach them after the transaction is mined.

Reasoning:

- Contracts do not know final receipt fields during execution.
- Emitting placeholders or pretending to know receipt metadata would undermine credibility.
- Separating event payload from receipt facts gives verifiers a clean provenance model.

Consequences:

- The hook event schema stays honest.
- The reader/verifier architecture becomes mandatory for public evidence.
- Public docs must explain this boundary clearly.

## ADR-005: Use Dependency-Light Interfaces

Status: accepted for the reference repo.

Decision:

The public repo uses minimal ABI-compatible interfaces instead of vendoring the entire Uniswap v4 core/periphery tree.

Reasoning:

- The first public artifact should be easy to clone and test.
- Reviewers can see exactly which callback fields the hook depends on.
- The repo avoids dependency noise while linking official Uniswap references.

Consequences:

- The repo is lightweight.
- The code must be checked against official Uniswap docs before live deployment.
- A production deployment package may later add direct pinned dependencies.

## ADR-006: Re-check Official Deployment Addresses

Status: accepted.

Decision:

Deployment addresses are not treated as permanent folklore. The Base Sepolia PoolManager constant must be checked against official Uniswap deployments before release.

Reasoning:

- Uniswap deployment addresses vary by network and version.
- Stale constants are a real integration risk.
- Public release records need reproducible upstream references.

Consequences:

- `OFFICIAL_REFERENCES.md` records the source.
- `FlowMemoryHookPlanner` uses the current official Base Sepolia PoolManager assumption.
- Release records must re-check the upstream deployments page before any broadcast.

## ADR-007: Publish Evidence Before Claims

Status: accepted.

Decision:

The public repo can be shared as a reference implementation. Live claims require deployment and reader evidence.

Reasoning:

- Public trust depends on matching claims to artifacts.
- A deployed hook without reader evidence is incomplete for FlowMemory's purpose.
- A reader record without source verification is not enough for a high-grade public claim.

Consequences:

- `PUBLIC_RELEASE_PATH.md` gates language by evidence level.
- The repo can be shared now, but the release ladder remains explicit.
- Mainnet requires a separate go/no-go review.
