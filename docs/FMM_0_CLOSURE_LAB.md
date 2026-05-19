# FMM-0 Closure Lab

FlowMemory is not only claiming a memory model.

It is testing the algebra around that model.

The FMM-0 Closure Lab checks whether receipt-bound machine histories remain
valid when they are composed, appended, merged, and promoted. It also checks
that impossible compositions fail before they can become live memory.

Run:

```bash
python tools/fmm0_closure_lab.py demo --pretty
```

Expected result:

```text
Closure laws checked: 8
Valid closures preserved: 4/4
Invalid closures rejected: 4/4
Escaped: 0
```

## Why This Is Different

Most AI-memory systems benchmark recall.

FlowMemory asks a different systems question:

```text
Can this machine memory history be composed without breaking reality?
```

Closure Lab makes that question executable.

Valid memory algebra should stay inside FMM-0:

- a matching receipt can attach to a local draft;
- a reader-derived FlowPulse can promote only with consistency evidence;
- monotonic same-rootfield append can preserve a live history;
- independent rootfields can merge commutatively.

Invalid memory algebra should be rejected:

- rootfield rollback;
- split-brain heads;
- pre-receipt receipt facts;
- semantic truth overclaims.

This is the category-defining point: FlowMemory treats agent memory like a
memory model, not a retrieval cache.

## Non-Claims

Closure Lab is not semantic truth verification. It is not model correctness.
It is not custody, swap control, production verifier infrastructure, Base
mainnet deployment, or GPU acceleration.

It is the local executable proof that FMM-0 has closure behavior around the
FlowPulse proof envelope.
