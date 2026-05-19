# FlowMemory Reality Check

FlowMemory Reality Check is the launch-grade command for this repository.

It gives a reviewer one terminal screenshot that connects the hook, the
FlowPulse boundary model, receipt metadata separation, FlowSerial, and
FlowLitmus.

It now also names the runtime model and its state surface:

- **FMM-0: FlowMemory Agent Memory Model**;
- **FMM-0 Phase Space**;
- **FMM-0 Counterexample Forge**;
- **FMM-0 Closure Lab**;
- **FMM-0 Boundary Bisimulation**;
- **FMM-0 Forbidden Core Extractor**;
- **FMM-0 Witness Pack**;
- **FlowPulse Boundary ABI**;
- **Compute Reuse Router**;
- **FlowMemory Release Transcript**.

## Command

```bash
python tools/launch_reality_check.py --pretty
```

Optional screenshot artifact:

```bash
python tools/launch_reality_check.py --pretty \
  --write examples/launch-reality-check/latest-output.txt
```

For the claim-to-evidence launch scorecard, run:

```bash
python tools/memory_consistency_card.py --pretty
```

For the 10-minute skeptic review packet, run:

```bash
python tools/reviewer_walkthrough.py --pretty
```

For the pending-safe public receipt evidence gate, run:

```bash
python tools/verify_release_evidence.py --pretty
```

For the forbidden-outcomes casebook, run:

```bash
python tools/render_flowlitmus_casebook.py --check
```

For the phase-space demo, run:

```bash
python tools/fmm0_phase_table.py demo --pretty
```

For the adversarial counterexample harness, run:

```bash
python tools/fmm0_counterexample_forge.py demo --pretty
```

For the memory-algebra closure harness, run:

```bash
python tools/fmm0_closure_lab.py demo --pretty
```

For the cross-layer boundary projection harness, run:

```bash
python tools/fmm0_boundary_bisim.py demo --pretty
```

For the minimal forbidden-core diagnostic harness, run:

```bash
python tools/fmm0_forbidden_core.py demo --pretty
```

For the local witness packet, run:

```bash
python tools/fmm0_witness_pack.py demo --pretty
```

For ABI/model drift checks, run:

```bash
python tools/flowpulse_boundary_abi.py check --pretty
```

## What This Demo Proves

It proves the repo can execute local runtime consistency checks around
receipt-bound FlowPulse boundaries.

It checks:

- the boundary model;
- the narrow hook invariant surface;
- required launch artifacts;
- FMM-0 Phase Space;
- FMM-0 Counterexample Forge;
- FMM-0 Closure Lab;
- FMM-0 Boundary Bisimulation;
- FMM-0 Forbidden Core Extractor;
- FMM-0 Witness Pack;
- FlowPulse Boundary ABI;
- Compute Reuse Router;
- FlowMemory Release Transcript;
- the FlowLitmus forbidden-outcome suite.

Expected result:

```text
Result: FlowMemory can tell impossible histories from live ones using receipt-bound FlowPulse boundaries.
```

## Runtime Path

```mermaid
flowchart LR
    Swap["Uniswap v4 swap lifecycle"] --> Hook["FlowMemory afterSwap hook"]
    Hook --> Pulse["FlowPulse memory artifact"]
    Pulse --> Receipt["transaction proof envelope"]
    Receipt --> Reader["reader attaches txHash/logIndex"]
    Reader --> Phase["FMM-0 Phase Space"]
    Phase --> Forge["Counterexample Forge"]
    Forge --> Closure["Closure Lab checks memory algebra"]
    Closure --> Bisim["Boundary Bisimulation checks projection drift"]
    Bisim --> Core["Forbidden Core shrinks impossible histories"]
    Core --> ABI["FlowPulse Boundary ABI checks event drift"]
    ABI --> Witness["Witness Pack bundles local evidence"]
    Witness --> Router["Compute Reuse Router checks reuse decisions"]
    Router --> Transcript["Release Transcript summarizes launch state"]
    Transcript --> Serial["FlowSerial checks serial history"]
    Serial --> Litmus["FlowLitmus runs forbidden outcomes"]
    Litmus --> Check["FlowMemory Reality Check"]

    Hook -. absent .-> Custody["custody"]
    Hook -. absent .-> Routing["routing"]
    Hook -. absent .-> Fees["dynamic fees"]
    Hook -. absent .-> Accounting["custom accounting"]
```

## What This Demo Does Not Prove

No live mainnet deployment.

No audited production infrastructure.

No custody.

No fund protection.

No swap control.

No semantic truth.

No model correctness.

No GPU acceleration.

No production verifier infrastructure.

## What To Screenshot

Screenshot the terminal output from:

```bash
python tools/launch_reality_check.py --pretty
```

The strongest part is the FlowLitmus table:

```text
FM-LB-001   pre-receipt txHash read                PASS  forbidden_pre_receipt_read
FM-SER-001  retrocausal receipt claim              PASS  retrocausal_receipt_claim
FM-QS-001   unquiesced post-boundary output        PASS  QuiescenceViolation
FM-RT-001   speculative output escaped             PASS  RetirementViolation
FM-FIS-001  stale output survived boundary         PASS  BoundaryFissionViolation
FM-SER-002  rootfield rollback                     PASS  rootfield_rollback
FM-SER-003  split-brain canonical write            PASS  split_brain_write
FM-OK-001   valid boundary history                 PASS  Serializable
```

## What To Say Publicly

Use these three lines first:

```text
The swap is not the memory.
The transaction is the proof envelope.
The FlowPulse is the memory artifact.
```

Then add:

```text
FlowLitmus shows why this matters: agents can now fault impossible histories around receipt-bound execution boundaries.
```

For the AI-memory angle, use:

```text
Everyone treated agent memory like retrieval. FlowMemory treats it like a memory model.
```

For the phase-table angle, use:

```text
Retrieval treats memory as text; FMM-0 treats machine history as a phase space with forbidden transitions.
```

## 30-Second Founder Script

FlowMemory starts with a Uniswap v4 `afterSwap` hook that emits a FlowPulse.
The swap is not the memory. The transaction is the proof envelope. The
FlowPulse is the memory artifact.

But the deeper launch claim is runtime consistency. Agents are becoming
distributed systems: model calls, tool calls, state writes, caches, and compute
jobs all crossing external events. FlowLitmus is our executable
forbidden-outcome suite. It tests whether an agent history respects FlowPulse
receipt boundaries or becomes impossible.

FMM-0 Phase Space makes the boundary visible before the litmus suite runs. A
local output, a reader-derived FlowPulse, and an
FMM-0-conforming history are different phases of machine state. A pre-receipt
artifact cannot claim `txHash` or `logIndex`, and a local artifact cannot jump
straight into live FMM-0 state.

The Counterexample Forge is the adversarial layer. It mutates valid artifacts
into impossible histories and requires FMM-0 to catch every one.

The Closure Lab is the algebra layer. It checks that valid receipt-bound
memory histories stay valid under composition and that invalid composition
cannot escape.

Boundary Bisimulation is the cross-layer layer. It checks that the same
FlowPulse boundary survives hook signal, receipt envelope, and FMM-0 runtime
projection without drift.

Forbidden Core is the diagnostic layer. It shrinks impossible histories to the
smallest mutation core that still violates FMM-0, so the failure becomes
explainable instead of only rejected.

The Witness Pack is the evidence-quality layer. It bundles the local
conformance outputs into one reproducible packet and keeps public release
evidence pending until real receipt data exists.

FlowPulse Boundary ABI is the hook/model drift layer. It checks that the
Solidity event surface still excludes receipt-only fields and matches the
runtime boundary assumptions.

Compute Reuse Router is the GPU workflow bridge. It proves when committed
compute memory can become a scheduler reuse decision, and when unsafe reuse must
be rejected.

FlowMemory Release Transcript is the launch packaging layer. It gives one
offline object for passed local evidence, pending public evidence, and explicit
non-claims.

So the launch is not "we emitted an event." The launch is: FlowMemory gives
machines a way to tell live histories from impossible ones.

## Claims To Avoid

Do not say:

- live mainnet deployment;
- audited production infrastructure;
- custody;
- fund protection;
- swap control;
- custom accounting;
- semantic truth;
- model correctness;
- GPU acceleration;
- production compute verifier;
- `txHash` or `logIndex` known inside the hook.

Say instead:

- local R&D runtime conformance;
- receipt-bound FlowPulse artifacts;
- reader-attached receipt metadata;
- forbidden outcomes for machine histories;
- `afterSwap` emission boundary;
- zero hook delta;
- no custody, no routing, no custom accounting.
