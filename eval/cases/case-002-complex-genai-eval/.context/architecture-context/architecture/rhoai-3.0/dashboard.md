# Dashboard

**Jira component**: Dashboard
**Maturity**: Stable (GA)
**Owning team**: RHOAI Dashboard
**Upstream**: opendatahub-io/odh-dashboard
**Midstream**: red-hat-data-services/odh-dashboard
**Konflux onboarded**: yes

## Role in the platform

Single-pane web console for RHOAI. Surfaces data science projects, workbenches,
model serving, pipelines, and distributed workload status. User-facing enablement
of any component requires a Dashboard integration (navigation section, resource
lists, creation/edit forms, status views).

## Dependencies

- OpenShift OAuth for authentication and project-scoped RBAC
- Component backends via Kubernetes CRs (InferenceService, Notebook, PipelineRun,
  Workload) — the Dashboard reads and writes CRs, it owns no data plane

## Interfaces

- Kubernetes API only; no private component APIs
- Per-component feature flags and defaults via the OdhDashboardConfig CR
