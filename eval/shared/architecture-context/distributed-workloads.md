# Distributed Workloads

**Jira component**: Distributed Workloads
**Maturity**: Stable (GA); topology-aware scheduling Tech Preview
**Owning team**: Distributed Workloads
**Upstream**: kubernetes-sigs/kueue, project-codeflare/codeflare-operator, ray-project/kuberay
**Midstream**: opendatahub-io/kueue, opendatahub-io/codeflare-operator, opendatahub-io/kuberay
**Konflux onboarded**: yes

## Role in the platform

Queueing and orchestration layer for batch AI workloads. Kueue is the platform's
queueing system (ClusterQueue/LocalQueue quota model, all-or-nothing admission
via waitForPodsReady); Volcano is not shipped or supported. KubeRay manages Ray
clusters; CodeFlare SDK is the user-facing entry point for Ray-based jobs.

## Dependencies

- cert-manager for Kueue webhooks
- NVIDIA GPU Operator for GPU resource discovery and time-slicing configuration

## Interfaces

- ClusterQueue, LocalQueue, Workload CRDs (kueue.x-k8s.io)
- RayCluster/RayJob CRDs (ray.io); PyTorchJob admission via Kueue integration
- Kueue metrics (pending/admitted workloads per queue) exposed to Prometheus
