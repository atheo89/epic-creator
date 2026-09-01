---
strat_id: RHAISTRAT-9017
title: Keyboard accessibility conformance for core Dashboard flows
status: Refinement Done
priority: Normal
labels:
- refined
- accessibility
links: []
---

## Problem Statement

An accessibility audit found that four core Dashboard flows (project creation,
workbench spawn, model deployment, pipeline run submission) cannot be completed
with keyboard alone: focus is lost in modals, several controls are unreachable,
and focus indicators are inconsistent. Two public-sector customers require an
updated, published conformance statement (VPAT) before renewal — so the fixes
and the published documentation are both deliverables of this strategy.

## High-Level Requirements

| ID | Priority | Requirement |
|-------|----------|-------------|
| HLR-1 | P1 | The four audited core flows are fully operable by keyboard, with no focus traps or unreachable controls. |
| HLR-2 | P1 | Visible focus indicators are consistent across the audited flows. |
| HLR-3 | P2 | The accessibility conformance documentation (VPAT and product docs accessibility statement) is updated and republished to reflect the fixed state, with technical review. |

## Affected Components

- Dashboard
- Documentation

## Out of Scope

- Screen-reader semantics beyond what the keyboard fixes require
- Flows outside the four audited ones

## Open Questions

None — the audit report enumerates the exact defects per flow.
