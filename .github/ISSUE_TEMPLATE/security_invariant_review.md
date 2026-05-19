---
name: Security or invariant review
about: Report a potential hook invariant, release-claim, or receipt-boundary issue
title: "[Security/Invariant]: "
labels: security, review
assignees: ''
---

## Summary

Describe the concern without posting exploitable live-asset details.

## Area

- [ ] PoolManager gating
- [ ] `afterSwap` selector / hook permission surface
- [ ] Zero hook delta / no custom accounting
- [ ] No custody / transfer path
- [ ] `hookData` validation
- [ ] `rootfieldId` / `commitment` validation
- [ ] Receipt metadata separation
- [ ] Reader/verifier evidence
- [ ] Release or marketing claim

## Why It Matters

What invariant or claim boundary could be broken?

## Suggested Fix

Optional.

## Private Disclosure Needed?

If this includes exploitable details, prefer a private GitHub security advisory
if available. Do not post secrets, private keys, or funded-wallet details.
