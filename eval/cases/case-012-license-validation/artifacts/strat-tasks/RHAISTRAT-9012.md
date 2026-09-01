---
strat_id: RHAISTRAT-9012
title: Bundle an S3-compatible object store for disconnected installs
status: Refinement Done
priority: Major
labels:
- refined
- disconnected
links: []
---

## Problem Statement

Pipelines and model serving both require S3-compatible object storage, but
disconnected customers frequently have none. Field teams work around this by
installing upstream MinIO ad hoc — unsupported, unpatched, and invisible to the
platform. We want a supported, bundled S3-compatible store that administrators
can enable for disconnected and PoC clusters. The leading candidate, MinIO, is
AGPL-3.0 licensed; redistribution terms must be cleared before any productization
work can ship, and the outcome may force a different upstream.

## High-Level Requirements

| ID | Priority | Requirement |
|-------|----------|-------------|
| HLR-1 | P0 | Legal review of redistributing the candidate object store (MinIO, AGPL-3.0) is completed and documented, including the derivative-work posture for operator integration. This clearance blocks all shipping work. |
| HLR-2 | P0 | Administrators can enable a supported, bundled S3-compatible object store through the Platform Operator, with productized images and upgrade lifecycle. |
| HLR-3 | P1 | Data Science Pipelines and model serving connection defaults can target the bundled store without manual endpoint configuration. |
| HLR-4 | P2 | Documentation covers enablement, sizing guidance, and the supported/unsupported boundary versus customer-provided storage. |

## Affected Components

- Platform Operator
- Data Science Pipelines
- Dashboard
- Documentation

## Out of Scope

- Replacing customer-provided S3 in connected environments
- Data migration tooling between stores

## Open Questions

1. If AGPL terms cannot be satisfied for our distribution model, the fallback
   candidate is an Apache-2.0 alternative (e.g. SeaweedFS) — acceptable, but it
   restarts image productization.
