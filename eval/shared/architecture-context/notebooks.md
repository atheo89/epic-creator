# Notebooks

**Jira component**: Notebooks
**Maturity**: Stable (GA)
**Owning team**: Workbenches
**Upstream**: kubeflow/notebooks (notebook-controller)
**Midstream**: opendatahub-io/kubeflow (notebook-controller fork)
**Konflux onboarded**: yes

## Role in the platform

Workbench (notebook server) lifecycle: the notebook-controller reconciles
Notebook CRs into StatefulSets with OAuth sidecars. Includes the idle culler,
which stops workbenches after a configurable inactivity period; culling defaults
and per-workbench overrides are administered through the Dashboard
(OdhDashboardConfig notebookController settings).

## Dependencies

- Workbench images (imagestreams) maintained by the platform
- Dashboard for spawn UI and culling configuration

## Interfaces

- Notebook CRD (kubeflow.org/v1)
- Culling configured via notebook-controller-culler-config ConfigMap; last
  activity tracked per kernel through Jupyter server API probes
