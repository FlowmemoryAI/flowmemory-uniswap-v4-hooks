# Launch Claim Ledger

Every public FlowMemory claim should be mapped to evidence.

The launch claim ledger separates:

- locally testable claims;
- R&D model claims;
- public release evidence claims;
- explicit non-claims.

A claim is launch-safe only if it has:

1. a claim string;
2. supporting files;
3. a command or review action;
4. an expected result;
5. a status;
6. explicit non-claims.

The source ledger lives at:

```text
examples/reviewer-walkthrough/fmm0-claim-ledger.json
```

Render the terminal review packet:

```bash
python tools/reviewer_walkthrough.py --pretty
```

Render the markdown walkthrough:

```bash
python tools/reviewer_walkthrough.py --markdown docs/SKEPTIC_REVIEW_WALKTHROUGH.md
```

Check the public release evidence gate:

```bash
python tools/verify_release_evidence.py --pretty
```

## Status Meanings

`PASS` means the claim is supported by local repo code, docs, examples, and/or
tests.

`PENDING` means the claim needs public release evidence before it can be used as
a live-evidence claim.

`NOT_CLAIMED` means the repo explicitly does not make that claim.

`REVIEW_ONLY` means a human reviewer should inspect the cited files.

`FAIL` means the claim must not be used until the evidence is fixed.

## Launch-Safe Summary

```text
Local FMM-0 consistency surface: PASS
FlowLitmus forbidden outcomes: PASS
Public Base Sepolia receipt evidence: PENDING
Production verifier infrastructure: NOT_CLAIMED
```

## Public Wording

Use:

```text
Everyone treated agent memory like retrieval. FlowMemory treats it like a memory model - and the skeptic walkthrough maps every claim to evidence.
```

Use:

```text
Every launch claim has a command, and every overclaim has a red line.
```

Do not lead with "AI memory on Uniswap." Lead with the stronger systems claim:

```text
Agent memory is a consistency model.
```
