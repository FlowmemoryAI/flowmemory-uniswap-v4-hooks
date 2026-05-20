# Documentation Index

This index gives first-time reviewers a cleaner path through the repository. The project has many specs and harnesses; start with the short path before opening the full evidence surface.

## First Read

| Doc | Use |
| --- | --- |
| [Reviewer Quickstart](REVIEWER_QUICKSTART.md) | Fastest technical review path and command list. |
| [How It Works](HOW_IT_WORKS.md) | Plain explanation of the hook, reader, and memory model. |
| [Event Model](EVENT_MODEL.md) | Exact `AfterSwapObserved` and `FlowPulse` event boundaries. |
| [Reader And Verifier Architecture](READER_VERIFIER_ARCHITECTURE.md) | How logs and receipts become verified memory records. |
| [Security Model](SECURITY_MODEL.md) | What the hook does and does not secure. |
| [Non-Claims](NON_CLAIMS.md) | Claims the repo explicitly does not make. |

## Public Launch And Review

| Doc | Use |
| --- | --- |
| [External Developer Review Packet](EXTERNAL_DEVELOPER_REVIEW_PACKET.md) | Send this to outside technical reviewers. |
| [Expert Review Prompt](EXPERT_REVIEW_PROMPT.md) | Adversarial reviewer prompt. |
| [Skeptic Review Walkthrough](SKEPTIC_REVIEW_WALKTHROUGH.md) | Claim ledger with evidence, commands, and non-claims. |
| [Public Review Checklist](PUBLIC_REVIEW_CHECKLIST.md) | Checklist before sharing publicly. |
| [Launch Claim Ledger](LAUNCH_CLAIM_LEDGER.md) | Claim-to-evidence rules. |
| [Public Launch Copy](PUBLIC_LAUNCH_COPY.md) | Public messaging and safe wording. |

## Architecture

| Doc | Use |
| --- | --- |
| [Architecture](ARCHITECTURE.md) | Hook and system architecture. |
| [Architecture Decisions](ARCHITECTURE_DECISIONS.md) | Design decisions and tradeoffs. |
| [Integration Blueprint](INTEGRATION_BLUEPRINT.md) | How hook, reader, verifier, and public API fit together. |
| [Production Readiness Architecture](PRODUCTION_READINESS_ARCHITECTURE.md) | Production candidate stack and trust boundaries. |
| [Repo Boundary And Future Runtime](REPO_BOUNDARY_AND_FUTURE_RUNTIME.md) | What belongs in this repo versus future packages. |
| [Uniswap v4 Compatibility](UNISWAP_V4_COMPATIBILITY.md) | Compatibility notes and hook assumptions. |

## Reader, Evidence, And Operations

| Doc | Use |
| --- | --- |
| [PulseWatch 24/7 Reader](PULSEWATCH_24_7_READER.md) | Always-on reader concept and demo. |
| [PulseWatch Operations](PULSEWATCH_OPERATIONS.md) | Operational reader notes. |
| [Release Evidence](RELEASE_EVIDENCE.md) | Release evidence packet shape. |
| [Public Status](PUBLIC_STATUS.md) | Public status surface. |
| [Base Sepolia Plan](BASE_SEPOLIA_PLAN.md) | Base Sepolia release path. |
| [Base Sepolia Deployment Runbook](BASE_SEPOLIA_DEPLOYMENT_RUNBOOK.md) | Deployment runbook. |
| [Mainnet Candidate Gate](MAINNET_CANDIDATE_GATE.md) | Mainnet readiness gate. |
| [Incident Response](INCIDENT_RESPONSE.md) | Incident response process. |
| [SLOs](SLOS.md) | Service-level objectives. |

## Memory Model

| Doc | Use |
| --- | --- |
| [FlowMemory Memory Model](FLOWMEMORY_MEMORY_MODEL.md) | FMM-0 overview. |
| [FlowMemory Runtime Model](FLOWMEMORY_RUNTIME_MODEL.md) | Runtime interpretation of memory boundaries. |
| [Memory Consistency Card](MEMORY_CONSISTENCY_CARD.md) | Claim-to-evidence scorecard. |
| [FMM-0 Conformance Matrix](FMM_0_CONFORMANCE_MATRIX.md) | Conformance surface. |
| [FlowLitmus Forbidden Outcomes](FLOWLITMUS_FORBIDDEN_OUTCOMES.md) | Executable impossible histories. |
| [FlowSerial](FLOW_SERIAL.md) | Receipt-linearizable machine histories. |
| [FlowQuiesce](FLOW_QUIESCE.md) | Receipt-triggered safe points. |
| [FlowMMU](FLOW_MMU.md) | Receipt-backed dereference semantics. |

## Compute, Cache, And Workflow Reuse

| Doc | Use |
| --- | --- |
| [Cache Lineage Gate](CACHE_LINEAGE_GATE.md) | Proof-carried KV/context reuse checks. |
| [Compute Reuse Router](COMPUTE_REUSE_ROUTER.md) | Proof-backed compute reuse routing. |
| [Compute Reuse Consistency](COMPUTE_REUSE_CONSISTENCY.md) | Bridge across cache, compute, and memory history. |
| [Compute ChargeLine](COMPUTE_CHARGELINE.md) | Compute payment and route consistency. |
| [DischargeLine](DISCHARGELINE.md) | Receipt-bound obligation discharge. |
| [SpendLine](SPENDLINE.md) | Autonomous spend history checks. |
| [DuplexLine](DUPLEXLINE.md) | Buyer/seller exchange co-serialization. |
| [Agent Commerce Stack](AGENT_COMMERCE_STACK.md) | End-to-end agent commerce memory stack. |

## Deep Evidence Surface

| Doc | Use |
| --- | --- |
| [FMM-0 Phase Table](FMM_0_PHASE_TABLE.md) | Machine-state phase space. |
| [FMM-0 Counterexample Forge](FMM_0_COUNTEREXAMPLE_FORGE.md) | Adversarial impossible-history generator. |
| [FMM-0 Closure Lab](FMM_0_CLOSURE_LAB.md) | Memory composition laws. |
| [FMM-0 Boundary Bisimulation](FMM_0_BOUNDARY_BISIMULATION.md) | Cross-layer projection drift checks. |
| [FMM-0 Forbidden Core Extractor](FMM_0_FORBIDDEN_CORE_EXTRACTOR.md) | Minimal failing cores. |
| [FMM-0 Witness Pack](FMM_0_WITNESS_PACK.md) | Local conformance evidence packet. |
| [FlowPulse Boundary ABI](FLOWPULSE_BOUNDARY_ABI.md) | Solidity event/model drift gate. |

## Broader Positioning

| Doc | Use |
| --- | --- |
| [Beyond DeFi Memory](BEYOND_DEFI_MEMORY.md) | Broader memory-for-execution category. |
| [Proof-Carried Agent Memory](PROOF_CARRIED_AGENT_MEMORY.md) | Agent memory thesis. |
| [Marketing Positioning](MARKETING_POSITIONING.md) | Positioning language and boundaries. |
| [Launch Reality Check](LAUNCH_REALITY_CHECK.md) | Screenshot-ready local proof point. |
