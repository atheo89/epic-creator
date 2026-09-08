---
strat_id: RHAISTRAT-9004
title: Disconnected environment guidance for KServe raw deployment mode
status: Refinement Done
priority: Major
labels:
- refined
- disconnected
links: []
---

## Problem Statement

Raw deployment mode is the recommended KServe path for disconnected clusters,
but our documentation only covers serverless mode installs. Field teams keep
rediscovering the same steps — which images to mirror, which operators to skip,
how to verify an air-gapped install — in private gists. Nothing in this
strategy changes product behavior; the capability exists and works. The gap is
entirely published guidance.

## High-Level Requirements

| ID | Priority | Requirement |
|-------|----------|-------------|
| HLR-1 | P1 | A disconnected install guide for KServe raw deployment mode exists in the product documentation, covering prerequisites, operator configuration, and validation steps. |
| HLR-2 | P1 | The guide includes a complete image-mirroring reference (required images and how to derive the digest list per release). |
| HLR-3 | P2 | A troubleshooting section covers the three most common field-reported failure modes (image pull errors, missing runtime, storage-initializer misconfiguration). |

## Affected Components

- KServe
- Documentation

## Out of Scope

- Any code, operator, or default-configuration change
- Serverless mode disconnected support

## Open Questions

None — source material exists in field enablement docs; this is authoring and
technical review work.
