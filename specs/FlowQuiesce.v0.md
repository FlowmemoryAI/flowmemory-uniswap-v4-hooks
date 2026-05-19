# FlowQuiesce v0 Draft Spec

FlowQuiesce is a local R&D primitive for receipt-triggered quiescence epochs.

Category sentence:

> FlowQuiesce turns a receipt-bound FlowPulse into a quiescence epoch: any
> in-flight agent or GPU frame that read pre-boundary context must reach a safe
> point before its output can join the post-boundary world.

## ReceiptEpoch

```json
{
  "schema": "flowmemory.receipt_epoch.v0",
  "epochId": "sha256:...",
  "epochType": "flowpulse_receipt_epoch",
  "epochNumber": 1,
  "previousEpochId": "sha256:...",
  "rootfieldId": "0x...",
  "trigger": {
    "artifactType": "FlowPulse",
    "boundary": "uniswap_v4_afterSwap",
    "chainId": "84532",
    "hookAddress": "0x...",
    "txHash": "0x...",
    "logIndex": "7",
    "transactionIndex": "3",
    "blockNumber": "123456",
    "blockHash": "0x...",
    "receiptStatus": "success",
    "subjectPoolId": "0x...",
    "commitment": "0x..."
  },
  "checks": {
    "readerAttachedTxHash": true,
    "readerAttachedLogIndex": true,
    "receiptStatusSuccess": true,
    "nonzeroRootfieldId": true,
    "nonzeroCommitment": true,
    "epochIdMatches": true
  }
}
```

## AgentFrame

```json
{
  "schema": "flowmemory.agent_frame.v0",
  "frameId": "frame-001",
  "agentId": "demo-agent",
  "frameType": "agent",
  "state": "active",
  "openedAtEpochId": "sha256:epoch-0",
  "rootfieldReads": [
    "0x..."
  ],
  "pendingOutputs": [
    {
      "outputId": "output-001",
      "type": "ModelPulseDraft",
      "commitment": "sha256:..."
    }
  ]
}
```

## QuiescenceRequest

```json
{
  "schema": "flowmemory.quiescence_request.v0",
  "requestId": "sha256:...",
  "epochId": "sha256:...",
  "rootfieldId": "0x...",
  "requiredFrames": [
    {
      "frameId": "frame-001",
      "reason": "active_pre_boundary_reader_for_rootfield",
      "requiredSafePoint": "quiesce | revalidate | fork | abandon",
      "pendingOutputs": [
        "output-001"
      ]
    }
  ],
  "unaffectedFrames": [],
  "blockedJoinUntilQuiescent": [
    "output-001"
  ]
}
```

## QuiescenceAck

```json
{
  "schema": "flowmemory.quiescence_ack.v0",
  "ackId": "sha256:...",
  "requestId": "sha256:...",
  "epochId": "sha256:...",
  "frameId": "frame-001",
  "ackMode": "revalidated",
  "frameStateAfter": "quiescent",
  "outputDisposition": {
    "output-001": "revalidated_for_epoch"
  }
}
```

## QuiescenceCertificate

```json
{
  "schema": "flowmemory.quiescence_certificate.v0",
  "certificateId": "sha256:...",
  "epochId": "sha256:...",
  "requestId": "sha256:...",
  "status": "grace_period_closed",
  "requiredFrameCount": 1,
  "ackedFrameCount": 1,
  "blockedFrames": [],
  "safeToJoinPostBoundaryState": true,
  "safeOutputs": [
    "output-001"
  ],
  "unsafeOutputs": []
}
```

## Rule

Outputs from active pre-boundary readers cannot join post-boundary state until
the required frames acknowledge a safe point.

That safe point can be:

- `revalidated`;
- `forked`;
- `abandoned`;
- `readonly_internal`.
