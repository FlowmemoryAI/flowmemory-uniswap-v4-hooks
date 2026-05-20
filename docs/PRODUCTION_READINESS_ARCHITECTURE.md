# Production Readiness Architecture

This repository is production-shaped, not production-deployed.

Its production candidate architecture separates hook emission, reader evidence, verifier policy, and public release claims.

## Candidate Stack

```text
Uniswap v4 PoolManager
  -> FlowMemoryAfterSwapHook
  -> FlowPulse log
  -> transaction receipt
  -> reader/verifier
  -> release evidence packet
  -> public claim gate
  -> incident response and monitoring
```

## Deployable Components

Production candidate:

- `FlowMemoryAfterSwapHook`;
- hook planner and CREATE2 address planning;
- reader/verifier service;
- release evidence verifier;
- public claim gate;
- mainnet candidate gate;
- incident response process.

Local-only in this repo:

- FMM-0 harnesses;
- FlowLitmus cases;
- compute and agent-commerce conformance demos;
- pending release evidence templates.

## Trust Boundaries

| Boundary | Rule |
| --- | --- |
| Hook | Emits memory signals; does not custody funds or control swaps. |
| Transaction receipt | Proof envelope; not the memory artifact. |
| Reader/verifier | Attaches txHash, logIndex, finality, and source verification evidence after execution. |
| Release operator | Publishes evidence only after claim gates pass. |
| Public copy | Must not claim mainnet, custody, production verifier, semantic truth, or fund protection without evidence. |

## Current Gate

Run:

```powershell
python tools/mainnet_candidate_gate.py --pretty
```

Expected current status:

```text
localLaunchReady:      True
mainnetCandidateReady: False
releaseMode:           LOCAL_LAUNCH_READY_ONLY
```

## Non-Claims

This architecture does not claim live Base mainnet deployment, custody, fund protection, audited production readiness, or production verifier infrastructure.
