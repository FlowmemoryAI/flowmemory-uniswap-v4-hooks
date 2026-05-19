# FlowPulse Proof Explorer

The launch should not make reviewers read the primitive.

It should let them see the primitive.

The FlowPulse Proof Explorer is the public surface where a transaction stops looking like a raw receipt and starts looking like a memory artifact.

## Core Demo

Paste a transaction hash.

The explorer shows:

```text
Swap executed -> FlowPulse emitted -> receipt metadata attached -> memory artifact verified -> rootfield graph updated
```

The demo should make one claim visually unavoidable:

The swap is not the memory.

The transaction is the proof envelope.

The FlowPulse is the memory artifact.

## Four Panels

### 1. Proof Envelope

Shows the reader-derived receipt facts:

- chain id;
- PoolManager address;
- hook address;
- pool id;
- block number;
- transaction hash;
- transaction index;
- log index;
- receipt status;
- event signature;
- source verification status;
- hook bytecode hash.

This panel proves where the memory signal landed.

### 2. FlowPulse Artifact

Shows the memory signal:

- pulse id;
- pulse type;
- rootfield id;
- commitment;
- parent pulse id;
- advisory URI;
- schema version;
- sequence;
- actor;
- hook version;
- artifact status.

This panel proves what was remembered.

### 3. Non-Interference Proof

Shows why this is a memory hook, not a trading hook:

- afterSwap only;
- PoolManager-gated;
- zero hook delta;
- no token custody;
- no ERC20 transfer path;
- no dynamic fee path;
- no routing path;
- no custom accounting path;
- no beforeSwap permission;
- no reader-derived metadata claimed during execution.

This panel is the credibility engine.

It turns minimalism into strength.

### 4. Memory Graph

Shows where the pulse goes next:

```text
Rootfield
  -> FlowPulse
       -> proof envelope
       -> swap context
       -> commitment
       -> parent pulse
       -> downstream memory
```

Later, this same graph can include ComputePulse:

```text
Rootfield
  -> FlowPulse: swap boundary memory
  -> ComputePulse: AI/GPU job memory
  -> AgentPulse: agent decision memory
```

## Canonical Pulse ID

The hook should not compute a pulse id that depends on `txHash` or `logIndex`.

Those are receipt facts.

The reader can compute the canonical public id:

```text
pulseId = keccak256(
  "FlowPulse/v1",
  chainId,
  txHash,
  logIndex,
  hookAddress,
  poolId,
  rootfieldId,
  commitment
)
```

The result is a memory artifact anchored to the proof envelope.

## Verify Button

The explorer should include a "Verify this pulse" action that outputs a JSON proof:

```json
{
  "status": "verified",
  "pulseId": "0x...",
  "chainId": 84532,
  "txHash": "0x...",
  "logIndex": 7,
  "hook": "0x...",
  "poolId": "0x...",
  "rootfieldId": "0x...",
  "commitment": "0x...",
  "checks": {
    "receiptContainsFlowPulseLog": true,
    "emitterIsHook": true,
    "hookBytecodeHashMatchesRelease": true,
    "poolManagerGated": true,
    "afterSwapOnly": true,
    "zeroHookDelta": true,
    "noCustodyPath": true,
    "readerAttachedReceiptMetadata": true
  }
}
```

## Public Visual

The strongest visual is a split proof path:

```text
left side: execution
swap -> PoolManager -> afterSwap -> FlowPulse event

right side: memory
receipt -> verifier -> pulse id -> rootfield graph -> reusable memory
```

Then one second panel:

```text
GPU job -> compute receipt -> ComputePulse -> same Rootflow graph
```

The public should understand the leap immediately:

FlowMemory is not just reading logs.

FlowMemory is creating a memory artifact model for execution itself.

## MVP Scope

For the first public version, the explorer can be static or semi-static:

- one canonical Base Sepolia transaction;
- one parsed receipt JSON file;
- one FlowPulse proof JSON file;
- one non-interference card;
- one Mermaid graph;
- one "copy proof" button;
- one CLI command that reproduces the proof.

The first version does not need a backend if the release artifact is stable.

It needs to make the primitive undeniable.

## Why This Is More Impressive Than Another Doc

Most people will not understand the hook by reading Solidity.

They will understand it when the explorer shows:

```text
This event came from this hook,
at this exact receipt position,
after this swap boundary,
with this zero-delta non-interference profile,
inside this memory namespace.
```

That is the moment FlowMemory stops looking like an event and starts looking like infrastructure.
