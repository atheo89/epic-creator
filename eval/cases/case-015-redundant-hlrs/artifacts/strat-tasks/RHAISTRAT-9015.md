---
strat_id: RHAISTRAT-9015
title: Experiment comparison for training and pipeline runs
status: Refinement Done
priority: Major
labels:
- refined
links: []
---

## Problem Statement

Data scientists iterate across dozens of training and pipeline runs but have no
way to compare them inside the platform: parameters and metrics live in
per-run pages, so comparison happens in exported spreadsheets. Model promotion
decisions need side-by-side visibility into what changed between candidate
runs and how their metrics differ. (Requirements below were consolidated from
two customer councils; some overlap in wording was kept from the sources.)

## High-Level Requirements

| ID | Priority | Requirement |
|-------|----------|-------------|
| HLR-1 | P0 | Users can select two or more runs and view their parameters and metrics side by side in the Dashboard. |
| HLR-2 | P1 | Registered model versions link back to the run that produced them, so a comparison can be opened from the Model Registry. |
| HLR-3 | P1 | Provide a run "diff" view that highlights which parameters and metrics changed between two selected runs. |
| HLR-4 | P2 | Documentation covers the comparison workflow from both the runs list and the registry. |

## Affected Components

- Dashboard
- Model Registry
- Data Science Pipelines

## Out of Scope

- Automatic best-run selection or promotion
- Comparison across clusters or across projects

## Open Questions

None.
