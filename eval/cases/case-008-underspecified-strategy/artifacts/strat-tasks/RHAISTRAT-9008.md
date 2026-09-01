---
strat_id: RHAISTRAT-9008
title: Make RHOAI more usable for enterprise teams
status: Refinement Done
priority: Normal
labels:
- refined
links: []
---

## Problem Statement

Several strategic accounts have told field teams that RHOAI "feels hard to use
at enterprise scale". Feedback arrived through different channels and has not
been consolidated; the quotes below are representative but partially
contradictory. Leadership wants visible usability progress this release.

## High-Level Requirements

| ID | Priority | Requirement |
|-------|----------|-------------|
| HLR-1 | — | Administration should be simpler. One account wants fewer configuration options exposed ("too many knobs"), another explicitly wants more fine-grained controls per project. |
| HLR-2 | — | Onboarding a new data scientist should take "less than a day". It is not defined what onboarding includes or where the day is currently spent. |
| HLR-3 | — | The platform should "integrate better" with existing enterprise tooling. No specific tools were named in the consolidated feedback. |
| HLR-4 | P2 | Publish a whitepaper describing enterprise usability best practices on RHOAI. |

## Affected Components

- Dashboard
- Notebooks

## Out of Scope

Nothing has been explicitly scoped out.

## Open Questions

1. Which accounts' feedback takes precedence when requirements conflict (HLR-1)?
2. What does "onboarding" cover for HLR-2 — cluster access, project setup,
   first workbench, or first deployed model?
3. Which enterprise tools does HLR-3 actually mean?
