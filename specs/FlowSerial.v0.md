# FlowSerial v0

FlowSerial is a draft R&D specification for receipt-linearizable machine
histories.

Category sentence:

> FlowSerial compiles an agent's outputs, tool calls, and state writes into a
> single serial history around FlowPulse receipt boundaries; if no valid order
> exists, the machine history is impossible.

Short form:

> FlowMemory gives agents linearizability against reality.

## Purpose

AI agents are becoming distributed systems: planner loops, model calls, tool
calls, background workers, caches, GPU jobs, and state writers all produce
machine history. The dangerous failure is not only hallucination. It is
impossible history:

- an output claims `txHash` before a reader has attached receipt metadata;
- a state writer rolls a rootfield head backward after it observed a newer
  FlowPulse boundary;
- two workers claim the same canonical state under incompatible FlowPulse heads;
- a cache artifact says it used the latest boundary without carrying that head.

FlowSerial turns those failures into deterministic faults.

## ReceiptBoundary

`ReceiptBoundary` is the FlowSerial form of a reader-attached FlowPulse proof
envelope.

Required fields:

- `schema`: `flowmemory.receipt_boundary.v0`
- `boundaryId`: stable boundary identifier; if omitted, tools can derive one
  from the boundary body.
- `artifactType`: `FlowPulse`
- `boundary`: `uniswap_v4_afterSwap`
- `declaredOrder`: local machine-history position used by the prototype
  scheduler.
- `chainId`
- `hookAddress`
- `txHash`: reader-attached receipt fact.
- `transactionIndex`: reader-attached receipt fact.
- `logIndex`: reader-attached receipt fact.
- `blockNumber`
- `blockHash`
- `receiptStatus`: must be `success`.
- `rootfieldId`
- `commitment`
- `subjectPoolId`
- `parentPulseId`
- `receiptOrderKey`: optional `[chainId, blockNumber, transactionIndex, logIndex]`.

The hook does not know `txHash`, `transactionIndex`, `logIndex`, or block facts
during execution. FlowSerial only accepts those fields after reader/verifier
infrastructure attaches them to the FlowPulse proof envelope.

## MachineEvent

`MachineEvent` is a model output, tool call, state write, cache reuse, compute
draft, or other machine event in the agent history.

Required fields:

- `schema`: `flowmemory.machine_event.v0`
- `eventId`
- `eventType`
- `agentId`
- `rootfieldId`
- `declaredOrder`
- `observedBoundaries`: FlowPulse boundary heads this event has observed.
- `claimedReceiptFacts`: receipt-only facts this event cites.
- `writes`: state writes, including `rootfieldHead`.
- `mustPrecede`: boundary IDs that must appear after the event.
- `mustFollow`: boundary IDs that must appear before the event.
- `exclusiveWriteKey`: optional state key where incompatible FlowPulse heads are
  split-brain faults.
- `outputCommitment`

## FlowSerialHistory

`FlowSerialHistory` combines boundaries and events:

- `schema`: `flowmemory.flow_serial_history.v0`
- `historyId`
- `agentId`
- `rootfieldId`
- `declaredConsistency`: `flow_serializable`
- `boundaries`
- `events`
- `notClaims`

## FlowSerialCertificate

A serializable history emits:

- `schema`: `flowmemory.flow_serial_certificate.v0`
- `certificateId`
- `historyId`
- `agentId`
- `rootfieldId`
- `status`: `serializable`
- `category`: `receipt_linearizable_machine_history`
- `serialSchedule`
- `rootfieldHeads`
- `checks`
- `faults`: empty
- `notClaims`

## FlowSerialFault

An impossible history emits:

- `schema`: `flowmemory.flow_serial_fault.v0`
- `faultId`
- `faultType`
- `historyId`
- `eventId`
- `boundaryId`
- `reason`
- `repairHints`
- `details`
- `notClaims`

Fault types:

- `retrocausal_receipt_claim`: an event claims receipt-only facts before the
  FlowPulse receipt boundary is available.
- `rootfield_rollback`: a later event moves a rootfield head behind the current
  FlowPulse head.
- `split_brain_write`: two exclusive state writers use incompatible FlowPulse
  heads.
- `missing_receipt_metadata`: the boundary lacks reader-attached ordering facts.
- `failed_receipt_boundary`: the boundary is not a successful FlowPulse
  afterSwap receipt boundary.
- `impossible_schedule`: declared ordering constraints cannot be satisfied.

## Non-Claims

FlowSerial does not prove AI outputs are true.
It does not prove model correctness.
It does not prove semantic truth.
It does not prove GPU execution or hardware attestation.
It does not accelerate GPUs.
It does not control swaps.
It does not custody funds or protect funds.
It is not audited production infrastructure.
It is not live mainnet infrastructure.
It does not mean the hook knows `txHash` or `logIndex`.
It does not replace consensus or workflow engines.

FlowSerial is a local R&D primitive for checking whether machine histories can
be serialized around reader-attached FlowPulse receipt boundaries.
