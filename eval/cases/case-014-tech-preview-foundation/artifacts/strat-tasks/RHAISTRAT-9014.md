---
strat_id: RHAISTRAT-9014
title: Graduate Llama Stack to General Availability
status: Refinement Done
priority: Critical
labels:
- refined
- genai
links: []
---

## Problem Statement

Llama Stack shipped as Tech Preview and adoption is strong, but enterprise
customers will not build production GenAI applications on a TP component.
Graduating to GA requires API stability commitments, a production support
posture, and closing the quality gaps that TP status currently excuses. The
full inventory of those gaps is not yet known — TP feedback is scattered across
support tickets, and no systematic GA-readiness assessment has been done.

## High-Level Requirements

| ID | Priority | Requirement |
|-------|----------|-------------|
| HLR-1 | P0 | A GA-readiness assessment inventories the gaps between current TP quality and GA bar (API stability, upgrade paths, scale limits, error handling), producing the definitive GA scope. |
| HLR-2 | P0 | Published API surface carries a stability guarantee: versioned APIs, deprecation policy, and a tested upgrade path from the last two TP releases. |
| HLR-3 | P0 | Production support posture is in place: documented SLO targets, backport policy, and supported configuration matrix. |
| HLR-4 | P1 | Safety guardrails via TrustyAI are a supported, documented integration (not an experimental flag) for GA distributions. |
| HLR-5 | P1 | The Dashboard enables Llama Stack management by default for entitled clusters (no TP opt-in gate). |
| HLR-6 | P2 | Documentation is uplifted to GA standards, including migration notes from TP. |

## Affected Components

- Llama Stack
- TrustyAI
- Dashboard

## Out of Scope

- New Llama Stack feature development beyond GA-bar quality work
- Deprecating alternative GenAI serving paths

## Open Questions

1. The GA scope itself depends on HLR-1's assessment — until it lands, the
   size of the stability and hardening work is an estimate.
