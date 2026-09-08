# Data Science Pipelines

**Jira component**: Data Science Pipelines
**Maturity**: Stable (GA)
**Owning team**: RHOAI Pipelines
**Upstream**: kubeflow/pipelines (v2)
**Midstream**: opendatahub-io/data-science-pipelines-operator
**Konflux onboarded**: yes

## Role in the platform

Workflow orchestration for training, batch scoring, and evaluation flows. The
DSPO operator manages per-project DataSciencePipelinesApplication instances
(API server, persistence, Argo Workflows backend).

## Dependencies

- Argo Workflows (embedded) as the execution engine
- S3-compatible object storage for artifacts

## Interfaces

- DataSciencePipelinesApplication CRD (datasciencepipelinesapplications.opendatahub.io)
- KFP v2 REST API and SDK; pipeline runs surfaced in the Dashboard
