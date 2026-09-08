# Training Operator

**Jira component**: Training Operator
**Maturity**: Stable (GA)
**Owning team**: Distributed Workloads
**Upstream**: kubeflow/training-operator
**Midstream**: opendatahub-io/training-operator
**Konflux onboarded**: yes

## Role in the platform

Runs distributed training jobs (PyTorchJob primarily) on the cluster. Multi-node
jobs are admitted through Kueue when workload queueing is enabled; the operator
itself performs no scheduling beyond creating pods for the job topology.

## Dependencies

- Kueue (Distributed Workloads) for admission, quota, and gang semantics
- GPU-enabled worker nodes (NVIDIA GPU Operator) for accelerated training

## Interfaces

- PyTorchJob CRD (kubeflow.org/v1)
- Workload admission via kueue.x-k8s.io labels/queues
