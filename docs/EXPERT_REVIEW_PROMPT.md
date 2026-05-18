# Expert Review Prompt

Use this prompt with ChatGPT, another LLM, or a human protocol reviewer when you want an adversarial architecture review.

The goal is to force the reviewer to ask for missing information, challenge assumptions, and identify gaps before the hook is presented as live.

## Prompt

```text
You are a senior Solidity and DeFi protocol architect reviewing a public repository:

https://github.com/FlowmemoryAI/flowmemory-uniswap-v4-hooks

The repo implements a FlowMemory Uniswap v4 afterSwap hook reference. It contains:

- FlowMemoryAfterSwapHook.sol
- FlowMemoryHookPlanner.sol
- FlowPulse.sol
- minimal Uniswap v4 afterSwap-compatible interfaces
- Foundry tests
- architecture, event model, security model, release path, and Base Sepolia docs

Please review it as if it will be the first public technical artifact for the project.

Questions to answer:

1. Is the afterSwap-only design coherent for a first public hook?
2. Are the hook permission bits and CREATE2 planning explained well enough?
3. Does the repo clearly separate on-chain event payload from reader-derived receipt metadata?
4. Are the no-custody, no-dynamic-fee, and zero-hook-delta boundaries technically credible?
5. What would a senior Uniswap v4 reviewer object to?
6. What would a skeptical security reviewer ask for before Base Sepolia deployment?
7. What should be added before a Base Sepolia release record?
8. What should be added before any Base mainnet claim?
9. Are there public claims in the docs that are too strong?
10. Which tests, scripts, diagrams, or docs would make this repository more professional?

Please produce:

- a concise architecture assessment;
- a list of missing information;
- a list of high-risk assumptions;
- recommended additional tests;
- recommended additional docs;
- recommended release gates;
- language that is safe to use publicly;
- language that must be avoided.

Assume the project wants to be conservative and technically precise.
Do not invent deployment facts. If a live deployment is not in the repo, say so.
```

## Information The Reviewer Should Inspect

- `contracts/FlowMemoryAfterSwapHook.sol`
- `contracts/FlowMemoryHookPlanner.sol`
- `contracts/FlowPulse.sol`
- `test/FlowMemoryAfterSwapHook.t.sol`
- `docs/ARCHITECTURE.md`
- `docs/WHY_IT_WORKS.md`
- `docs/EVENT_MODEL.md`
- `docs/READER_VERIFIER_ARCHITECTURE.md`
- `docs/SECURITY_MODEL.md`
- `docs/PUBLIC_RELEASE_PATH.md`
- `docs/BASE_SEPOLIA_PLAN.md`
- `docs/OFFICIAL_REFERENCES.md`

## Expected Good Reviewer Pushback

A good reviewer should push on:

- whether the minimal `IUniswapV4SwapHookLike` interface should be replaced with pinned v4-core dependencies before deployment;
- whether the current tests are enough without an integration test against a real PoolManager harness;
- whether the release record includes source verification and deployed bytecode matching;
- whether finality policy is defined concretely enough;
- whether the reader/verifier implementation exists or is still planned;
- whether public language avoids implying production readiness.

## Current Intended Answer

The intended architecture answer is:

FlowMemory's public hook starts as a narrow, event-first `afterSwap` path. It is PoolManager-gated, emits `FlowPulse`, returns zero hook delta, and avoids custody, dynamic fees, and custom accounting. It does not claim receipt metadata during execution. A reader/verifier layer must attach receipt facts after the transaction lands. The repo is shareable as a reference implementation now; live Base Sepolia and Base mainnet claims require release records and observed evidence.
