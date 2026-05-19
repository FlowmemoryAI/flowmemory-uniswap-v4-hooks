# FlowLitmus v0

FlowLitmus is a draft R&D specification for executable forbidden outcomes in
FlowMemory runtime semantics.

Killer sentence:

> FlowLitmus is a conformance suite for reality: it feeds agents impossible
> FlowPulse histories and proves whether their runtime can tell impossible from
> live.

Sharper launch line:

> FlowMemory does not just give agents memory. It gives them forbidden
> outcomes.

## Purpose

FlowMemory now has multiple R&D primitives: receipt pages, speculative
retirement, boundary fission, quiescence, and receipt-linearizability.
FlowLitmus ties them together as a runtime consistency suite.

The point is not another memory feature. The point is an executable model of
what machine histories are no longer allowed to do once FlowPulse receipt
boundaries exist.

## FlowLitmusCase

Required fields:

- `schema`: `flowmemory.flow_litmus_case.v0`
- `caseId`: stable case ID such as `FM-SER-001`
- `title`
- `category`
- `runner`
- `invariant`
- `whyFlowPulseMatters`
- `boundaryRequirement`
- `artifacts`
- `forbiddenOutcome`
- `expected`
- `notClaims`

Supported runners in this prototype:

- `flow_mmu_pre_receipt_read`
- `flow_serial`
- `flow_quiesce_open_certificate`
- `pulse_retire_enforcement`
- `boundary_fission_stale_survival`

## FlowLitmusResult

Required fields:

- `schema`: `flowmemory.flow_litmus_result.v0`
- `caseId`
- `title`
- `category`
- `status`: `pass` or `fail`
- `observed`
- `expected`
- `problems`
- `invariant`
- `whyFlowPulseMatters`
- `notClaims`
- `resultId`

## FlowLitmusSuite

Required fields:

- `schema`: `flowmemory.flow_litmus_suite.v0`
- `suiteId`
- `title`
- `cases`

The suite emits `flowmemory.flow_litmus_suite_result.v0` with aggregate pass and
fail counts plus individual case results.

## Prototype Cases

- `FM-LB-001`: pre-receipt `txHash` read.
- `FM-SER-001`: retrocausal receipt claim.
- `FM-QS-001`: unquiesced post-boundary output.
- `FM-RT-001`: speculative output escaped before retirement.
- `FM-FIS-001`: stale output survived a boundary.
- `FM-SER-002`: rootfield rollback.
- `FM-SER-003`: split-brain canonical write.
- `FM-OK-001`: valid boundary history.

## Non-Claims

FlowLitmus does not prove AI outputs are true.
It does not prove model correctness.
It does not prove semantic truth.
It does not prove GPU execution or hardware attestation.
It does not accelerate GPUs.
It does not control swaps.
It does not protect funds.
It does not have custody.
It is not audited production infrastructure.
It is not live mainnet infrastructure.
It does not mean the hook knows `txHash` or `logIndex`.
It does not replace verification infrastructure.
It does not prove production safety.

FlowLitmus is a local R&D conformance suite for FlowPulse receipt-boundary
rules.
