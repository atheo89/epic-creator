# TrustyAI

**Jira component**: TrustyAI
**Maturity**: Stable (GA); lm-eval integration Tech Preview
**Owning team**: TrustyAI
**Upstream**: trustyai-explainability/trustyai-service-operator
**Midstream**: red-hat-data-services/trustyai-service-operator
**Konflux onboarded**: yes

## Role in the platform

Model quality and trustworthiness services: fairness/bias metrics, drift
detection, explainability, and guardrails. Ships an operator that manages
TrustyAIService instances per data science project. The lm-eval job runner
(LMEvalJob CRD, wrapping EleutherAI lm-evaluation-harness) is Tech Preview and
is the platform's existing entry point for LLM benchmark execution.

## Dependencies

- KServe/ModelMesh inference endpoints as metric data sources
- Kubernetes Jobs for lm-eval benchmark execution

## Interfaces

- TrustyAIService and LMEvalJob CRDs (trustyai.opendatahub.io)
- REST metrics API consumed by the Dashboard
