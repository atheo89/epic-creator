# KServe

**Jira component**: KServe
**Maturity**: Stable (GA)
**Owning team**: RHOAI Serving
**Upstream**: kserve/kserve
**Midstream**: opendatahub-io/kserve, red-hat-data-services/kserve
**Konflux onboarded**: yes

## Role in the platform

Primary model serving stack. Deploys models as InferenceService CRs in two modes:
serverless (Knative + Istio) and raw deployment (plain Deployments/Services, no
mesh dependency). Raw deployment mode is the recommended path for disconnected
and edge environments.

## Dependencies

- Serving Runtimes (vLLM, OpenVINO, Caikit) for model execution
- Service Mesh / Serverless operators in serverless mode only
- Authorino for token authentication of inference endpoints

## Interfaces

- InferenceService CRD (serving.kserve.io/v1beta1); deployment state is exposed
  as CR status conditions (Ready, PredictorReady) and Kubernetes events
- Prometheus metrics per inference endpoint
