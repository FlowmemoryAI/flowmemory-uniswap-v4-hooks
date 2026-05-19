# Agent Commerce Skeptic Responses

This document is for the reviewer who is trying to dismiss the agent-commerce
stack as fake, overclaimed, or only a collection of validation scripts.

The short answer:

```text
Yes, this repo is local deterministic conformance, not production enforcement.
That is the point of this release surface.
```

FlowMemory is defining the memory-consistency rules for autonomous commerce
without claiming wallet enforcement, custody, escrow, mainnet deployment, or
production verifier infrastructure.

## Attack 1: This Is Just Validation Scripts

Response:

```text
Correct: these are local deterministic conformance harnesses.
```

They are not presented as a live verifier network.

They define forbidden states:

- compute payment that does not match compute route;
- receipt settlement that does not discharge the right obligation;
- buyer/seller exchange histories that cannot be co-serialized;
- commerce episodes that do not conserve obligations;
- delegated obligations that launder away memory constraints.

That is how infrastructure starts: name the invariants, make them executable,
then connect enforcement later.

Run:

```bash
python tools/flowmemory_release_transcript.py --pretty
python tools/launch_reality_check.py --pretty
```

## Attack 2: This Does Not Enforce Anything Onchain

Response:

```text
Correct. This repo does not claim enforcement.
```

The Uniswap v4 hook emits the FlowPulse memory signal. The downstream agent
commerce harnesses define local memory-consistency rules around that evidence.

Wallets, smart accounts, policy engines, agent runtimes, and future verifier
systems can consume these rules later. This repo does not claim that those
systems are already live.

## Attack 3: This Does Not Prove Work Quality

Response:

```text
Correct. Work quality is not the claim.
```

FlowMemory checks whether the obligation history is legal under declared
memory, receipt, payment, compute, and delegation constraints.

It does not prove that the work was good.

It does not prove semantic truth.

It does not prove model correctness.

That boundary is explicit because mixing work quality, custody, routing,
payment, and memory into one claim would be weaker, not stronger.

## Attack 4: This Is Not Live On Base Mainnet

Response:

```text
Correct. This repo does not claim live Base mainnet deployment.
```

The release transcript marks public Base Sepolia receipt evidence as pending
until a real release record exists.

Run:

```bash
python tools/verify_release_evidence.py --pretty
```

Expected current state:

```text
Public Base Sepolia receipt evidence: PENDING
Production verifier infrastructure: NOT_CLAIMED
```

## Attack 5: This Does Not Make GPUs Faster

Response:

```text
Correct. FlowMemory does not make GPU hardware faster.
```

The claim is workflow consistency:

- safe reuse can avoid recomputation;
- unsafe reuse stays blocked;
- compute payment must match the route;
- runtime drift and stale memory heads are rejected.

The GPU does the work. FlowMemory checks whether the work can be remembered,
reused, charged, and discharged without violating receipt-bound memory state.

## Attack 6: The JSON Fixtures Could Be Made Up

Response:

```text
Correct. Local fixtures are not public chain evidence.
```

They are deterministic test vectors for the model.

The repo separates local conformance from public evidence:

- local harnesses: `PASS`;
- public Base Sepolia receipt evidence: `PENDING`;
- production verifier infrastructure: `NOT_CLAIMED`.

This is why the release transcript exists.

## Attack 7: Too Many Primitives

Response:

```text
They are not separate product claims. They are layers in one memory-consistency stack.
```

Read [AGENT_COMMERCE_STACK.md](AGENT_COMMERCE_STACK.md):

- Compute Reuse Consistency: can this compute route be reused?
- Compute ChargeLine: can this compute route be charged this way?
- SpendLine: can this spend join memory?
- DischargeLine: did this receipt close the right obligation?
- DuplexLine: can buyer spend and seller work co-serialize?
- Agent Commerce Conservation: did the episode balance?
- Obligation Membrane: did delegation preserve constraints?

The category is not "more scripts."

The category is memory-native agent commerce.

## Attack 8: The Transaction Is Not Memory

Response:

```text
Correct. The transaction is the proof envelope. The FlowPulse is the memory artifact.
```

The repo explicitly rejects the claim that the swap transaction itself is
memory.

The Uniswap v4 `afterSwap` hook is a verified emission boundary. FlowPulse is
the memory signal emitted from that boundary. Receipt facts are attached later
by reader/verifier infrastructure.

## Launch-Safe Summary

Use:

```text
FlowMemory defines local deterministic memory-consistency rules for autonomous commerce.
```

Use:

```text
Payments move value. FlowMemory checks whether the obligation history is legal.
```

Use:

```text
Settlement is not discharge.
```

Do not claim:

- custody;
- escrow;
- wallet authorization;
- fund protection;
- work-quality proof;
- semantic truth;
- model correctness;
- GPU acceleration;
- live Base mainnet deployment;
- production verifier infrastructure.
