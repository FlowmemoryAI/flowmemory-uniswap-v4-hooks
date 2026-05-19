# FMM-0 Closure Lab v0

FMM-0 Closure Lab is the executable closure artifact for the FlowMemory Agent
Memory Model.

Counterexamples prove that bad histories are rejected. Closure proves the other
side: legal memory histories can be composed without leaving the model.

The lab checks eight laws:

- receipt attachment preserves a matching local draft;
- reader-derived FlowPulse evidence can promote only with consistency evidence;
- same-rootfield append preserves monotonic sequence;
- independent rootfield merge is commutative;
- same-rootfield append rejects rollback;
- same-rootfield same-sequence merge rejects split-brain heads;
- pre-receipt composition rejects receipt-only facts;
- reader-derived evidence cannot close over semantic truth.

## Boundary Model

The swap is not the memory.

The transaction is the proof envelope.

The FlowPulse is the memory artifact.

FMM-0 Closure Lab does not prove semantic truth, model correctness, custody,
fund protection, production verifier infrastructure, Base mainnet deployment,
or GPU acceleration.

It proves a narrower and more important launch claim:

```text
FMM-0 is closed under valid receipt-bound composition and rejects invalid memory algebra.
```
