---
strat_id: RHAISTRAT-9005
title: Queue-aware GPU scheduling for distributed training workloads
status: Refinement Done
priority: Critical
labels:
- refined
links: []
---

## Problem Statement

Large training jobs fail or waste capacity because pods are admitted piecemeal:
a 16-GPU job can hold 12 GPUs for hours waiting for the last 4, starving other
teams, and partially scheduled jobs die on timeout. Customers running mixed
fleets also report that jobs land on suboptimal GPU topologies (crossing NVLink
domains) with significant throughput loss. We need admission and placement that
treats a multi-node training job as one unit and uses GPU topology where it
matters.

## High-Level Requirements

| ID | Priority | Requirement |
|-------|----------|-------------|
| HLR-1 | P0 | Multi-node training jobs are admitted all-or-nothing: no partial GPU occupation while waiting for remaining pods. |
| HLR-2 | P0 | Per-project GPU quota is enforced at admission time across training job types (PyTorchJob, RayJob). |
| HLR-3 | P1 | Users can see queue position, quota consumption, and admission state for their pending jobs in the Dashboard. |
| HLR-4 | P1 | Higher-priority workloads can preempt lower-priority ones according to an admin-defined policy. |
| HLR-5 | P2 | Job placement can prefer GPU-topology-aligned nodes when the cluster exposes topology information. |

## Affected Components

- Distributed Workloads
- Training Operator
- Dashboard

## Out of Scope

- GPU sharing/fractioning (MIG, time-slicing policy management)
- Cross-cluster or multi-cluster queueing

## Open Questions

1. Do Kueue's current gang-admission semantics (waitForPodsReady) actually
   satisfy HLR-1 for PyTorchJob and RayJob at our target scale, or do we need
   scheduler-plugin work (e.g. coscheduling) beyond Kueue? The answer changes
   the shape of most implementation work.
2. Topology-aware placement (HLR-5) depends on node topology discovery that is
   only Tech Preview — is it mature enough to build on this release?
3. What preemption semantics do reference customers actually need — full
   eviction with requeue, or checkpoint-aware graceful preemption? We have
   conflicting field signals and no benchmark of checkpoint overhead.
