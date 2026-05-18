# Public Review Checklist

Use this checklist before sharing the repo publicly, before Base Sepolia deployment, and again before any mainnet claim.

## Repo Review

- [ ] `README.md` explains what the hook does in the first screen.
- [ ] Mermaid diagrams render on GitHub.
- [ ] `forge test -vvv` passes.
- [ ] GitHub Actions are green.
- [ ] License is present.
- [ ] No private keys, seed phrases, RPC URLs, API keys, webhooks, or signed transaction blobs are committed.
- [ ] Official Uniswap references are linked.
- [ ] Base Sepolia PoolManager address is re-checked against official Uniswap deployments.

## Contract Review

- [ ] `afterSwap` is gated to the configured PoolManager.
- [ ] Hook data must be non-empty.
- [ ] `rootfieldId` must be non-zero.
- [ ] `commitment` must be non-zero.
- [ ] Hook emits `AfterSwapObserved`.
- [ ] Hook emits `FlowPulse`.
- [ ] Hook returns zero hook delta.
- [ ] Hook has no custody path.
- [ ] Hook has no dynamic-fee path.
- [ ] Hook does not claim `txHash`, `transactionIndex`, or `logIndex`.

## Planner Review

- [ ] `AFTER_SWAP_FLAG` is `1 << 6`.
- [ ] Target hook bits are exactly `0x40`.
- [ ] Return-delta flags are not enabled.
- [ ] CREATE2 deployer is documented.
- [ ] Init code hash is recorded in the release record.
- [ ] Salt is recorded in the release record.
- [ ] Computed hook address matches the mined permission bits.

## Base Sepolia Release Review

- [ ] Deployment transaction hash is public.
- [ ] Deployment block is public.
- [ ] Source verification URL is public.
- [ ] Constructor args are public.
- [ ] Deployed bytecode matches source.
- [ ] Reader block range is public.
- [ ] At least one `AfterSwapObserved` log is decoded.
- [ ] At least one `FlowPulse` log is decoded.
- [ ] Sample `txHash` and `logIndex` are receipt-derived.
- [ ] Release record explicitly says this is not Base mainnet.

## Mainnet Claim Review

- [ ] Base Sepolia release record is complete.
- [ ] Mainnet PoolManager address is re-checked against official Uniswap deployments.
- [ ] Ownership and operational policy are documented.
- [ ] Incident response path is documented.
- [ ] Public dashboard/API distinguishes pending, finalized, verified, and rejected evidence.
- [ ] A separate go/no-go record exists.

## Public Language Review

Allowed before live deployment:

- [ ] "Public reference implementation."
- [ ] "Designed for the FlowMemory Uniswap v4 afterSwap hook path."
- [ ] "CI-tested Foundry implementation."
- [ ] "Base Sepolia release path."

Allowed after live Base Sepolia evidence:

- [ ] "Verified Base Sepolia hook deployment."
- [ ] "Observed FlowPulse logs."
- [ ] "Reader-derived receipt evidence."

Not allowed unless separately proven:

- [ ] "Production Base mainnet hook is live."
- [ ] "Audited custody system."
- [ ] "Production verifier network."
- [ ] "The hook knows transaction hash or log index during execution."
