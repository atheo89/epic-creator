# Model Registry

**Jira component**: Model Registry
**Maturity**: Stable (GA)
**Owning team**: Model Registry
**Upstream**: kubeflow/model-registry
**Midstream**: opendatahub-io/model-registry
**Konflux onboarded**: yes

## Role in the platform

Central catalog of registered models and versions with lifecycle metadata.
Source of truth linking a registered model version to its serving deployments
and training lineage. Custom properties on model versions are the extension
point for attaching structured metadata (e.g. evaluation results).

## Dependencies

- MySQL/MariaDB backing store
- Dashboard for the registry UI; KServe for deploy-from-registry flows

## Interfaces

- REST API (model-registry.opendatahub.io); OpenAPI-specified
- RegisteredModel / ModelVersion / ModelArtifact entities with custom properties
