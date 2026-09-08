---
strat_id: RHAISTRAT-9007
title: Bring-your-own vector database for RAG workloads
status: Refinement Done
priority: Major
labels:
- refined
- genai
links: []
---

## Problem Statement

RAG applications built on Llama Stack need a vector store, and today the
platform neither ships one nor documents how to attach an external one.
Customers are split into two camps with incompatible expectations: regulated
customers want a platform-managed vector database with supported images and
lifecycle, while cloud-native customers already run managed services (e.g.
a cloud vector DB) and only want a sanctioned way to connect them. We have not
decided which posture to productize first, and the answer changes most of the
downstream work.

## High-Level Requirements

| ID | Priority | Requirement |
|-------|----------|-------------|
| HLR-1 | P0 | A decision is reached, with a documented evaluation, on the first supported vector store posture: platform-managed (operator-deployed Milvus) versus external-connection-only. |
| HLR-2 | P0 | Depending on that decision: either administrators can deploy the managed vector store through the Platform Operator with productized images, or data scientists can register an external vector store connection per project with validated connectivity. |
| HLR-3 | P1 | Llama Stack distributions can consume the chosen vector store as a RAG provider without hand-editing distribution configs. |
| HLR-4 | P1 | The Dashboard exposes the chosen integration (deploy-and-manage UI for the managed path, or connection management UI for the external path). |
| HLR-5 | P2 | Product documentation covers setup and limits for whichever posture ships. |

## Affected Components

- Llama Stack
- Dashboard
- Platform Operator

## Out of Scope

- Shipping both postures in the same release
- Embedding model selection and lifecycle (separate strategy)

## Open Questions

1. Managed Milvus versus external-connection-only is genuinely undecided — the
   evaluation in HLR-1 must weigh supportability cost, disconnected-environment
   viability, and time-to-market, and the outcome forks the implementation
   structure for HLR-2 through HLR-5.
