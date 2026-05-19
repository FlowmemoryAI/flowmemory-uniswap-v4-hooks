# SpendLine

SpendLine is memory-linearizability for autonomous agent spending.

It checks whether a spend claim could have legally emerged from an agent's
receipt-bound memory history before downstream systems treat that spend as
memory-consistent.

## Core Sentence

```text
Agents do not only need wallets. They need spend histories that cannot lie
about what they remembered.
```

## Why This Exists

Base is moving toward agents with wallets, identity, payments, trading, and
service calls. Base documentation describes AI-agent payment flows with x402,
agent wallet setup, agent registration, and identity verification. Base Account
documentation describes Base Accounts as ERC-4337 smart-wallet-backed accounts
with one-tap USDC payments.

Those are necessary rails.

They are not the same thing as memory consistency.

Wallet infrastructure asks:

```text
Who can sign?
What can they spend?
Which app or policy is allowed?
```

SpendLine asks:

```text
Could this spend have emerged from the agent's receipt-bound machine history?
```

That is a different layer.

## What It Checks

SpendLine checks:

- the spend references the current memory head;
- the spend has a nonzero rootfield;
- the spend intent commitment exists;
- the proposed spend commitment exists;
- the spend intent has not already been consumed;
- the current AxiomPatch verdict allows the requested spend surface;
- x402-style payment requirements match the declared asset, amount, and recipient;
- paid compute/service work does not contradict compute/cache reuse gates;
- a post-spend FlowPulse exists when the spend is accepted as settled memory;
- FlowSerial can serialize the spend around the receipt-bound FlowPulse head;
- receipt-only fields are not claimed before the receipt boundary exists;
- rootfield heads do not roll backward after newer boundaries have been observed.

## What It Does Not Do

SpendLine is deliberately not a wallet authorization layer.

Do not claim:

- custody;
- fund protection;
- wallet enforcement;
- live Base mainnet deployment;
- production verifier readiness;
- semantic truth;
- model correctness;
- that a local harness prevents theft;
- that the hook controls swaps or payments.

SpendLine is a local R&D harness for memory-consistent spend histories.

## Relation To Base Agent Infrastructure

Base agent infrastructure gives agents:

- wallets;
- USDC payments;
- x402 pay-per-request flows;
- agent registration;
- identity verification;
- smart-account execution surfaces;
- service discovery.

SpendLine adds the memory layer around those rails:

```text
agent identity + wallet + payment rail
  -> spend claim
  -> receipt-bound FlowPulse memory head
  -> FlowSerial consistency check
  -> ACCEPT_SPENDLINE or REJECT_SPENDLINE
```

This is useful for:

- agent-to-agent payments;
- autonomous service buys;
- x402 API payments;
- compute or model-call payments;
- strategy execution where a stale memory head should not spend;
- preventing duplicate declared intent from becoming accepted memory;
- rejecting spend histories that claim receipt facts too early.

## Relation To Existing FlowMemory Primitives

SpendLine does not replace the existing stack.

It composes it:

- `FlowPulse` supplies the memory artifact;
- the transaction receipt supplies the proof envelope;
- `FlowSerial` catches impossible ordering;
- `AxiomPatch` can downgrade unsafe actions into unsigned proposals;
- `PulseRetire` can retire speculative spend branches after a receipt lands;
- `FlowQuiesce` can stop pre-boundary agent frames from writing post-boundary output;
- `Compute Reuse Consistency` can stop payment-for-compute from reusing stale work.

## Demo

Run:

```bash
python tools/spendline_harness.py demo --pretty
```

Expected result:

```text
SpendLine Harness

Valid spend:
  SPL-OK-001  PASS  ACCEPT_SPENDLINE   all_spendline_gates_passed

Unsafe spends:
  SPL-BAD-001 PASS  REJECT_SPENDLINE   currentMemoryHeadMatchesLedger
  SPL-BAD-002 PASS  REJECT_SPENDLINE   intentNotReplayed
  SPL-BAD-003 PASS  REJECT_SPENDLINE   retrocausal_receipt_claim
  SPL-BAD-004 PASS  REJECT_SPENDLINE   postSpendFlowPulsePresent
  SPL-BAD-005 PASS  REJECT_SPENDLINE   rootfield_rollback
  SPL-BAD-006 PASS  REJECT_SPENDLINE   axiomPatchAllowsSpendSurface
  SPL-BAD-007 PASS  REJECT_SPENDLINE   paymentRequirementMatchesSpend
  SPL-BAD-008 PASS  REJECT_SPENDLINE   computeReuseConsistentIfUsed

Summary:
  spend cases checked: 9
  valid spends accepted: 1/1
  unsafe spends rejected: 8/8
  escaped unsafe spends: 0

Result:
  Autonomous spend must be memory-linearizable.
```

## Why It Is Better Than Logs

An indexer can show that a payment happened.

SpendLine checks whether the spend can be accepted into a consistent agent
memory history.

The difference matters because autonomous agents will not fail only by losing
keys. They will fail by:

- spending from stale state;
- paying twice for one declared intent;
- claiming a receipt before it exists;
- writing incompatible wallet state from multiple workers;
- accepting compute or service work under the wrong memory head.

SpendLine makes those failures executable test cases.

## Sources

- Base AI-agent payments quickstart: <https://docs.base.org/ai-agents/quickstart/payments>
- Base Account overview: <https://docs.base.org/identity/smart-wallet/concepts/features/built-in/>
- Base agent registration and identity: <https://docs.base.org/ai-agents/setup/agent-registration>
- Base AI agents overview: <https://docs.base.org/ai-agents/index>
