---
strat_id: RHAISTRAT-9013
title: FIPS 140-3 compliance for the model serving stack
status: Refinement Done
priority: Critical
labels:
- refined
- compliance
links: []
---

## Problem Statement

Public-sector deals require the model serving stack to run on FIPS-enabled
OpenShift clusters using validated cryptographic modules. Today KServe
components and the serving data plane link non-validated crypto libraries in
several images, and we have no compliance evidence package. Certification
involves an external accredited laboratory (historical turnaround: six to nine
months) and mandatory security review board sign-off at defined milestones —
these human and third-party gates dominate the schedule regardless of
engineering speed.

## High-Level Requirements

| ID | Priority | Requirement |
|-------|----------|-------------|
| HLR-1 | P0 | All serving-stack images run correctly on FIPS-enabled clusters using validated crypto modules (no non-validated crypto in the request path). |
| HLR-2 | P0 | A compliance evidence package (module inventory, build attestations, test results) is assembled and submitted through the security review board to the external certification lab. |
| HLR-3 | P1 | CI enforces FIPS regressions: a gating check fails any serving-stack build that reintroduces non-validated crypto usage. |
| HLR-4 | P2 | Documentation states the FIPS support posture and cluster prerequisites. |

## Affected Components

- KServe
- Platform Operator

## Out of Scope

- FIPS posture for workbenches, pipelines, and training (separate strategies)
- Common Criteria certification

## Open Questions

None on scope — but note that lab scheduling and review-board cadence are
externally controlled and cannot be compressed by engineering effort.
