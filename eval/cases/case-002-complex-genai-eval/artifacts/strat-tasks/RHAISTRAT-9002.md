---
strat_id: RHAISTRAT-9002
title: Integrated GenAI model evaluation for RHOAI
status: Refinement Done
priority: Critical
labels:
- refined
- genai
links: []
---

## Problem Statement

Customers adopting generative models on RHOAI have no supported way to answer
"is this model good enough for my use case?" inside the platform. Evaluation
today happens in ad-hoc notebooks with lm-evaluation-harness or vendor tools,
results live in spreadsheets, and nothing links an evaluation to the model
version that was actually deployed. We need a first-class evaluation capability:
run standard and custom benchmarks against models served on the platform,
persist results alongside the model version, and let users compare candidates
before promoting one to production.

## High-Level Requirements

| ID | Priority | Requirement |
|--------|----------|-------------|
| HLR-1  | P0 | Users can launch an evaluation of a model served on the platform (KServe endpoint or Llama Stack distribution) against a selected benchmark suite. |
| HLR-2  | P0 | Standard benchmark suites (e.g. MMLU, ARC, HellaSwag exposed through lm-eval task names) are available out of the box. |
| HLR-3  | P0 | Evaluation results are persisted and linked to the Model Registry version of the evaluated model. |
| HLR-4  | P1 | Users can define custom evaluation tasks (own datasets and metrics) and run them through the same flow. |
| HLR-5  | P1 | The Dashboard shows evaluation runs, their status, and per-benchmark scores, and allows side-by-side comparison of two model versions. |
| HLR-6  | P1 | Evaluations can be embedded as a step in a Data Science Pipeline so promotion flows can gate on scores. |
| HLR-7  | P1 | Llama Stack's eval provider API is backed by the platform evaluation service, so agents/apps built on Llama Stack get the same results. |
| HLR-8  | P2 | Evaluation runs record cost/duration metadata (tokens, wall-clock, GPU time) for capacity planning. |
| HLR-9  | P2 | Product documentation covers the evaluation workflow end to end, including custom task authoring. |

## Affected Components

- TrustyAI
- Llama Stack
- Dashboard
- Data Science Pipelines
- Model Registry

## Out of Scope

- Human-preference (arena style) evaluation collection
- Automatic model promotion decisions — pipelines gate, humans promote
- Fine-tuning feedback loops driven by evaluation scores

## Open Questions

1. Execution engine: TrustyAI's LMEvalJob (Tech Preview) already wraps
   lm-evaluation-harness — do we build on it as the single execution path, or is
   a new evaluation service needed to also serve Llama Stack's eval provider
   API? Needs a technical investigation with a recommendation.
2. Result schema: what is the canonical result format persisted to Model
   Registry custom properties, and does it survive benchmark-suite version
   bumps? Prototype against real MMLU output before committing.
3. Benchmark dataset licensing: which standard suites can we redistribute in
   disconnected environments, and which must be fetched by the customer?
