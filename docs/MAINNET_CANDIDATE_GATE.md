# Mainnet Candidate Gate

The mainnet candidate gate prevents local launch readiness from being mistaken
for production deployment status.

Run:

```bash
python tools/mainnet_candidate_gate.py --pretty
```

Current expected status:

```text
localLaunchReady:      True
mainnetCandidateReady: False
releaseMode:           LOCAL_LAUNCH_READY_ONLY
```

## What The Gate Checks

The gate combines:

- public claim safety;
- launch reality check status;
- external deployment/evidence gates.

The local checks can pass today. The external gates stay blocking until real
evidence exists.

## Blocking External Gates

| Gate | Required evidence |
| --- | --- |
| `verified_mainnet_poolmanager` | Official PoolManager address and chain assumptions are re-checked before promotion. |
| `mainnet_hook_deployment` | Hook deployment record exists for the target chain. |
| `source_verification` | Hook source and bytecode are verified on the target explorer. |
| `observed_after_swap_log` | A finalized `AfterSwapObserved` log exists. |
| `observed_flowpulse_log` | A finalized `FlowPulse` log exists. |
| `reader_verifier_evidence` | Reader-derived receipt metadata is attached and reproducible. |
| `incident_response_owner` | An operator owns release status and incident response. |
| `security_review` | Hook, deployment, reader, and claim boundaries are reviewed. |

## Release Modes

| Mode | Meaning |
| --- | --- |
| `LOCAL_LAUNCH_READY_ONLY` | The repo can demonstrate the hook primitive and local conformance suite, but must not claim a production deployment. |
| `MAINNET_CANDIDATE` | Local checks pass and every external gate has recorded evidence. |

## Command Contract

Default mode exits zero when the local launch surface is healthy:

```bash
python tools/mainnet_candidate_gate.py --pretty
```

Strict mode exits non-zero unless every external gate is satisfied:

```bash
python tools/mainnet_candidate_gate.py --require-mainnet-candidate
```

That split lets CI enforce local launch health without making a false production
claim.
