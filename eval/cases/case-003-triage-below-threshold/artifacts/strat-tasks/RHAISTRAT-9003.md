---
strat_id: RHAISTRAT-9003
title: Reduce default workbench idle culling timeout to 8 hours
status: Refinement Done
priority: Normal
labels:
- refined
links: []
---

## Problem Statement

The default workbench idle culling timeout ships at 24 hours, so abandoned
workbenches hold GPUs overnight and through weekends. Fleet telemetry shows the
median idle-before-stop window admins actually configure is 8 hours. New
clusters should get the sensible default without an admin having to find the
setting.

## High-Level Requirements

| ID | Priority | Requirement |
|-------|----------|-------------|
| HLR-1 | P1 | The default idle culling timeout for newly installed clusters is 8 hours instead of 24. Existing clusters with an explicitly configured value are not changed on upgrade. |
| HLR-2 | P2 | The release note and cluster-settings documentation state the new default and how to override it. |

## Affected Components

- Notebooks
- Dashboard

## Out of Scope

- Per-project or per-user culling policies
- Changes to activity detection (kernel probe behavior)

## Open Questions

None — the setting, its ConfigMap, and the Dashboard administration UI already
exist; only the shipped default changes.
