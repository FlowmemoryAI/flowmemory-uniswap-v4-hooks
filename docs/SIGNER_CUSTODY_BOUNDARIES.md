# Signer And Custody Boundaries

FlowMemory's hook repo must keep signing, custody, and memory emission separate.

The hook emits `FlowPulse` memory signals from the `afterSwap` boundary. It is
not a wallet, custodian, escrow, swap controller, routing engine, fee engine, or
settlement authority.

## Boundary Table

| Surface | Owns | Does not own |
| --- | --- | --- |
| `FlowMemoryAfterSwapHook` | Hook-time payload validation and `FlowPulse` emission. | Private keys, user funds, routing, fees, custom accounting, swap authorization, receipt metadata. |
| Deployer wallet | Deployment transaction and source verification workflow. | User assets, FlowPulse semantic truth, reader-derived receipt facts. |
| PoolManager | Uniswap v4 swap lifecycle and hook callback routing. | FlowMemory downstream memory semantics. |
| Reader/verifier | Receipt metadata, finality, source verification, and evidence packet construction. | Hook-time memory payload creation or custody. |
| Release operator | Public release evidence publication and claim discipline. | Wallet enforcement, fund protection, or production verifier claims without evidence. |

## Signing Rules

- Deployment keys should be hardware-backed or otherwise isolated from repo
  tooling.
- No private key, mnemonic, API key, signed transaction, or production RPC secret
  belongs in this repository.
- The reader/verifier should read chain state and produce evidence. It should
  not need custody authority.
- Public release packets should identify deployer, hook address, chain id,
  source verification, and receipt evidence without exposing secrets.

## Custody Rule

The safest hook is the one that does not pretend to do settlement, custody,
routing, accounting, and memory all at once.

FlowMemory's first hook does one thing: emit the memory signal.

That is the production boundary. If a future system adds wallets, payment rails,
bonding, or policy cards, those surfaces must live behind separate interfaces
and separate risk reviews.

## Reviewer Check

A reviewer should be able to confirm:

- no custody path exists in the Solidity hook;
- no token transfer path exists in the hook;
- no custom accounting or dynamic-fee path exists in the hook;
- no `txHash`, `transactionIndex`, or `logIndex` field exists in the hook-time
  `FlowPulse` schema;
- release evidence is attached after execution by reader/verifier tooling.
