# DuplexLine

DuplexLine is co-serializability for autonomous agent exchange.

SpendLine asks whether one agent's declared spend can legally emerge from its
receipt-bound memory history.

DuplexLine asks the harder exchange question:

```text
Could the buyer's spend and the seller's work have emerged from compatible
machine histories?
```

## Core Sentence

```text
Wallets move funds. x402 moves payments. ERC-8004 identifies agents.
DuplexLine asks whether the exchange itself could have legally happened.
```

## Why This Exists

AI agents on Base can hold wallets, pay for services, expose paid endpoints,
register identity, and call other agents. Those rails make agent commerce
possible.

They do not make both sides of an exchange memory-consistent.

An indexer can show that money moved.

A wallet can show that a key signed.

An identity registry can show which agent made a request.

DuplexLine checks a different surface:

```text
buyer SpendLine + seller WorkLine + payment requirement + FlowSerial history
  -> ACCEPT_DUPLEXLINE or REJECT_DUPLEXLINE
```

## What It Checks

DuplexLine checks:

- the buyer agent exists;
- the seller agent exists;
- the buyer memory head matches the buyer ledger;
- the seller memory head matches the seller ledger;
- the task commitment exists;
- the work commitment exists;
- the seller work task matches the buyer task;
- the x402-style payment requirement hash has not drifted;
- the payment requirement task matches the exchange task;
- the seller identity, work author, authorized payee, and payment recipient are bound;
- the service endpoint and delivery endpoint are conserved;
- consumed payment requirements, work commitments, and exchange dedupe keys are not replayed;
- the seller work side actually serializes under FlowSerial;
- the buyer side passes SpendLine;
- paid compute/service work does not contradict compute/cache reuse gates;
- the buyer's compute policy allows the seller's reuse path;
- the exchange schedule is acyclic;
- payment receipt facts are not claimed before settlement;
- the seller state is FMM-0 live, not only reader-derived;
- the combined buyer/seller exchange history is FlowSerial-serializable.

## What It Does Not Do

DuplexLine is not escrow, custody, wallet authorization, dispute resolution, or
work-quality proof.

Do not claim:

- custody;
- fund protection;
- escrow;
- wallet enforcement;
- semantic truth;
- model correctness;
- live Base mainnet deployment;
- production verifier readiness;
- that it proves the seller's answer is correct;
- that it protects the buyer from loss.

DuplexLine is a local R&D harness for memory-consistent agent exchange.

## Why This Is Different

Most agent-commerce infrastructure asks:

```text
Can this identity authenticate?
Can this wallet pay?
Can this API return data?
Can this transaction be indexed?
```

DuplexLine asks:

```text
Do the buyer's spend memory and the seller's work memory describe the same
legal exchange?
```

That is the missing layer for autonomous commerce: not just payment rails, but
exchange memory.

## Relation To SpendLine

SpendLine is one-sided.

It checks whether a buyer's spend can be admitted into the buyer's memory
history.

DuplexLine is two-sided.

It requires the buyer spend and seller work to line up across:

- task commitment;
- payment requirement;
- buyer memory head;
- seller memory head;
- FlowSerial ordering;
- compute/cache reuse status.

## Demo

Run:

```bash
python tools/duplexline_harness.py demo --pretty
```

Expected result:

```text
DuplexLine Harness

Valid exchange:
  DPL-OK-001  PASS  ACCEPT_DUPLEXLINE   all_duplexline_gates_passed

Unsafe exchanges:
  DPL-BAD-001 PASS  REJECT_DUPLEXLINE   taskCommitmentsMatch
  DPL-BAD-002 PASS  REJECT_DUPLEXLINE   buyerMemoryHeadMatchesLedger
  DPL-BAD-003 PASS  REJECT_DUPLEXLINE   paymentRequirementHashMatches
  DPL-BAD-004 PASS  REJECT_DUPLEXLINE   sellerWorkLineSerializable
  DPL-BAD-005 PASS  REJECT_DUPLEXLINE   computeReuseConsistentIfUsed
  DPL-BAD-006 PASS  REJECT_DUPLEXLINE   sellerMemoryHeadMatchesLedger
  DPL-BAD-007 PASS  REJECT_DUPLEXLINE   buyerSpendLineAccepted
  DPL-BAD-008 PASS  REJECT_DUPLEXLINE   counterpartyPayeeBinding
  DPL-BAD-009 PASS  REJECT_DUPLEXLINE   workCommitmentNotReplayed
  DPL-BAD-010 PASS  REJECT_DUPLEXLINE   paymentRequirementNotConsumed
  DPL-BAD-011 PASS  REJECT_DUPLEXLINE   buyerComputePolicyAllowsSellerReuse
  DPL-BAD-012 PASS  REJECT_DUPLEXLINE   exchangeScheduleAcyclic
  DPL-BAD-013 PASS  REJECT_DUPLEXLINE   noPreSettlementPaymentReceiptClaims
  DPL-BAD-014 PASS  REJECT_DUPLEXLINE   serviceEndpointConserved
  DPL-BAD-015 PASS  REJECT_DUPLEXLINE   sellerStateFmm0Live

Invariant coverage:
  DPL-I1  PASS  Co-Serial Exchange
  DPL-I2  PASS  Counterparty-Payee Binding
  DPL-I3  PASS  Quote-Task-Work Conservation
  DPL-I4  PASS  Dual-Head Compatibility
  DPL-I5  PASS  No Pre-Receipt Economic Claims
  DPL-I6  PASS  Buyer Reuse Policy Dominance
  DPL-I7  PASS  Idempotent Exchange Commitment
  DPL-I8  PASS  No Quality/Truth Upgrade

Summary:
  exchanges checked: 16
  valid exchanges accepted: 1/1
  unsafe exchanges rejected: 15/15
  escaped unsafe exchanges: 0

Result:
  Agent-to-agent exchange must be co-serializable across spend, work, payment, and memory state.
```

## Why It Is Better Than Logs

Logs show that events happened.

DuplexLine checks whether the buyer and seller memories can agree on the same
exchange without impossible history.

That matters because agents will not only fail through bad keys. They will fail
through:

- stale buyer memory;
- seller work for the wrong task;
- payment requirement drift;
- missing seller-side FlowSerial evidence;
- compute reuse that contradicts the paid work claim.
- stale seller memory;
- duplicate buyer intents replayed into an exchange.
- counterparty-payee rebinding;
- work replay across buyers;
- double-consumed payment requirements;
- seller reuse that violates buyer fresh-compute policy;
- impossible exchange schedules;
- payment receipt facts smuggled before settlement;
- task endpoint drift;
- reader-derived seller state presented as FMM-0 live.

DuplexLine makes those failures executable test cases.

## Sources

- Base AI agents overview: <https://docs.base.org/ai-agents/index>
- Base AI-agent payments quickstart: <https://docs.base.org/ai-agents/quickstart/payments>
- Base agent registration and identity: <https://docs.base.org/ai-agents/setup/agent-registration>
- x402 payment concepts: <https://docs.base.org/ai-agents/core-concepts/payments-and-transactions>
