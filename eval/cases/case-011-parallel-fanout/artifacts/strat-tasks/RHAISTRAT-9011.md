---
strat_id: RHAISTRAT-9011
title: Adopt structured JSON logging across RHOAI components
status: Refinement Done
priority: Major
labels:
- refined
- observability
links: []
---

## Problem Statement

RHOAI components log in inconsistent formats — plain text, key=value, and
ad-hoc JSON — which breaks centralized log queries and makes support cases
expensive: correlating one user request across Dashboard, serving, and
pipelines requires per-component parsing rules. The platform needs one
structured logging convention, and each component needs to adopt it. Component
adoptions are independent of each other once the convention exists.

## High-Level Requirements

| ID | Priority | Requirement |
|--------|----------|-------------|
| HLR-1  | P0 | A platform logging convention is published: JSON schema, required fields (timestamp, level, component, namespace, correlation id), and library guidance per language (Go, Python, TypeScript). |
| HLR-2  | P0 | Dashboard emits convention-conformant logs. |
| HLR-3  | P0 | KServe controller and serving runtimes emit convention-conformant logs. |
| HLR-4  | P1 | Data Science Pipelines (operator and API server) emits convention-conformant logs. |
| HLR-5  | P1 | Model Registry emits convention-conformant logs. |
| HLR-6  | P1 | TrustyAI services emit convention-conformant logs. |
| HLR-7  | P1 | Notebooks (notebook-controller) emits convention-conformant logs. |
| HLR-8  | P2 | Training Operator emits convention-conformant logs. |
| HLR-9  | P2 | Documentation describes the log format and example queries for common support scenarios. |

## Affected Components

- Dashboard
- KServe
- Data Science Pipelines
- Model Registry
- TrustyAI
- Notebooks
- Training Operator

## Out of Scope

- Log storage, retention, or forwarding infrastructure
- Metrics and tracing conventions (logging only)

## Open Questions

None — the convention work (HLR-1) is prerequisite design, and per-component
adoptions are mechanical once it lands.
