# Compute ChargeLine

Compute ChargeLine checks whether payment for AI/GPU work matches the
memory-consistent compute route.

The strongest line:

```text
Compute billing without memory consistency is invoice optimism.
```

FlowMemory does not make a GPU chip faster. Compute ChargeLine does something
more precise: it checks whether a charge for fresh compute, reused compute, or
recomputed work agrees with the FlowMemory evidence that produced the artifact.

## What It Checks

Compute ChargeLine checks:

- fresh-compute charges point to a fresh compute route;
- reuse charges point to accepted compute/cache reuse evidence;
- unsafe reuse cannot close a compute payment;
- a buyer fresh-compute policy cannot be laundered into reuse;
- payment requirement hashes stay stable;
- a compute charge is not consumed twice;
- required attestation references are present;
- runtime commitments do not drift under the same payment;
- the buyer memory head is current.

## Demo

Run:

```bash
python tools/compute_chargeline.py demo --pretty
```

Expected result:

```text
Compute ChargeLine

Valid charges:
  CCL-OK-001  fresh compute charged as fresh           CHARGE_ACCEPTED
  CCL-OK-002  safe reuse charged as reuse              CHARGE_ACCEPTED

Invalid charges:
  CCL-BAD-001 reuse route charged as fresh             REJECT_CHARGE
  CCL-BAD-002 unsafe reuse charged                     REJECT_CHARGE
  CCL-BAD-003 buyer requires fresh seller reuses       REJECT_CHARGE
  CCL-BAD-004 duplicate compute charge                 REJECT_CHARGE
  CCL-BAD-005 missing required attestation             REJECT_CHARGE
  CCL-BAD-006 runtime drift under same payment         REJECT_CHARGE
  CCL-BAD-007 payment requirement drift                REJECT_CHARGE
  CCL-BAD-008 stale buyer memory head                  REJECT_CHARGE

Summary:
  compute charges checked: 10
  valid charges accepted: 2/2
  invalid charges rejected: 8/8
  escaped invalid charges: 0
```

## Why It Matters

Agents will pay for compute.

Some compute will be fresh.

Some compute will be reused.

Some reuse will be unsafe.

The payment rail alone cannot tell the difference.

Compute ChargeLine makes the charge follow the memory-consistent compute route.

## Non-Claims

This is not custody.

This is not escrow.

This is not wallet authorization.

This is not fund protection.

This is not work-quality proof.

This is not semantic truth.

This is not model correctness.

This is not GPU acceleration.

This is not hardware execution proof.

This is not production attestation infrastructure.

This is not a live Base mainnet deployment claim.
