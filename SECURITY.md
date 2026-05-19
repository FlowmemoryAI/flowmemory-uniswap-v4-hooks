# Security Policy

This repository is a public FlowMemory hook and R&D artifact package.

The on-chain hook is intentionally narrow:

- Uniswap v4 `afterSwap` boundary only;
- PoolManager-gated callback;
- required FlowMemory `hookData`;
- required `rootfieldId`;
- required `commitment`;
- zero hook delta;
- no custody;
- no routing;
- no dynamic fee path;
- no custom accounting path.

## Reporting A Vulnerability

For a potential vulnerability, prefer a private GitHub security advisory if the
repository enables it. If not, open a GitHub issue with a minimal description
and avoid posting exploitable details until maintainers respond.

Do not include:

- private keys;
- funded wallet secrets;
- private RPC URLs;
- unpublished exploit scripts against live assets.

## What Counts As Security-Relevant

Please report:

- a path that bypasses PoolManager gating;
- a path that changes hook delta or custom accounting unexpectedly;
- a custody, transfer, or payable surface not documented by the repo;
- incorrect hook permission assumptions;
- incorrect receipt metadata claims;
- reader/verifier output that fabricates `txHash`, `logIndex`, or receipt status;
- release language that claims deployment, audit, custody, or fund protection
  without evidence.

## Non-Goals

This repository does not claim:

- audited production readiness;
- live mainnet deployment;
- custody or fund protection;
- semantic truth validation;
- model correctness;
- GPU execution or acceleration;
- production verifier infrastructure.

FlowMemory emits memory signals from a verified execution boundary. The
transaction is the proof envelope. The FlowPulse is the memory artifact.
