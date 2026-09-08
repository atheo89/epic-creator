---
strat_id: RHAISTRAT-8006
title: '[TP] Productize & Downstream the Agent Operator'
status: Closed
priority: Critical
labels:
- ac-review-pending
- aicp-team-forge
- confidence-yellow
- refined
- tech-preview
links:
- 'source-rfe: RHAIRFE-7451'
- 'related-strategy: RHAISTRAT-7359'
- 'related-strategy: RHAISTRAT-7559'
- 'related-rfe: RHAIRFE-7587'
- 'related-rfe: RHAIRFE-7588'
- 'related-rfe: RHAIRFE-7589'
- 'out-of-scope-rfe: RHAIRFE-7408'
---

## Summary

Enterprise customers building AI agents on OpenShift AI need a way to register their agent workloads with the platform so that agents become discoverable, observable, and manageable without manual per-agent configuration. Today, each team reinvents onboarding from scratch.

## Problem Statement

AI agents are different from regular web applications. They expose machine-readable capability descriptions, connect to tools dynamically, act autonomously, and communicate with other agents. A vanilla Deployment can run the container, but it cannot express that the container is an agent, what it can do, or how to find it.

Customers deploying agents today must manually wire observability, write custom discovery logic, and build their own onboarding workflows for every agent. This per-agent overhead blocks teams from scaling beyond a handful of agents.

## What Makes an Agent Workload Different

An AI agent workload is a container image that:

* Exposes a machine-readable capability description at a well-known endpoint, declaring its name, skills, and supported protocols
* Connects to external tools dynamically (e.g., via MCP) rather than through hardcoded API endpoints
* Acts autonomously, making inference calls and communicating with other agents without a human in the request loop

Agents range from self-contained (tools and model config baked into the image) to platform-assembled (receiving tools and configuration at deploy time).

## Affected Customers

* **Verdanthal Bank:** Building their own agent platform, described the need as "CR-based agent lifecycle management with sidecar injection for identity, observability, tracing." Maps to their Q2 roadmap.
* **Threnholm Mobile:** Agent prototypes as Python containers. Explicit gaps: no MCP server lifecycle tracking, no production readiness infrastructure.
* **Peregrast Assurance:** Formal RFI for "Agentic Platform" covering agent lifecycle management, versioning, registry, and monitoring.
* **Quintalore Systems (1,000 agents):** "The full agent architecture matters now: control plane, governance, orchestration."
* **Orinthex Software:** Evaluating platforms for native agent deployment and lifecycle management with a portable specification.

## User Journey

1. Customer builds their agent image using any framework. The image exposes a capability description at a well-known endpoint.
2. Customer deploys as a standard Deployment with one label to mark it as an agent.
3. Customer creates one custom resource to onboard the agent to the platform.
4. The platform automatically registers the agent, makes it discoverable, and wires observability.
5. The agent is visible in the console, findable by other agents, and producing telemetry.
6. Total effort beyond a vanilla Deployment: one label, one custom resource.

## Acceptance Criteria

* MUST A customer can make their AI agent discoverable on the platform by creating an AgentRuntime CR that selects their existing Deployment (discovery is through AgentRuntime CR selection via targetRef, not via label queries on Deployments)
* MUST Other platform users and agents can find running agents and see what each agent can do (skills, protocols, endpoints) through the console or API
* MUST Agent metadata is verified and updated on workload rollouts without manual intervention
* MUST The agent operator is enabled via the Data Science Cluster CR (DSC), following the standard component controller pattern
* MUST Documentation covers the minimal image contract for creating a discoverable agent (endpoint format, health check, card structure)
* MUST When the operator is disabled in DSC (managementState: Removed), all operator-managed resources are cleaned up
* MUST When an agent Deployment is deleted, the operator garbage-collects associated resources (AgentRuntime status, generated NetworkPolicies, etc.)
* SHOULD When an agent's A2A endpoint is unreachable or returns malformed metadata, the operator sets a degraded condition on the AgentRuntime CR with a descriptive message
* COULD Agents running in sandboxed environments are automatically registered on the platform

**Open**: The parent RFE (RHAIRFE-7451) has a MUST for OTEL trace sink integration that is not yet reflected here. Under team discussion.

## Success Criteria

* At least 3 early-access customers successfully register and discover agents through the operator during Tech Preview
* Time to make an agent discoverable drops from hours (manual wiring) to minutes (label  one CR)

## Scope

### In Scope

* Agent registration and discovery (operator watches labeled workloads)
* Agent metadata synchronization (capability descriptions kept current)
* Observability wiring (telemetry auto-configuration)
* Console visibility (agents visible in OpenShift AI UI)
* Operator productization (OLM, certification, downstream builds)

### Out of Scope (covered by RHAIRFE-7408)

* Agent identity and authentication
* Trust enforcement and network policy based on agent verification
* Agent-to-agent authorization and delegation chains
* Per-tool access control
* AgentCard signing and attestation

## Open Questions

* What is the minimal image contract for Tech Preview? Do we require the A2A protocol format, or accept a simpler metadata format?
* How does the onboarding custom resource interact with OpenShell's Sandbox CR when both are present?

## Strategy (AI Generated by Agentic SDLC Pipeline)

### TL;DR

Onboard the kagenti-operator into RHOAI as a standard DSC-managed component at Tech Preview maturity. This covers Konflux build pipeline integration (operator + AuthBridge sidecar images), a new component controller in rhods-operator following the established 16-component pattern, OLM/CSV packaging with RELATED_IMAGE entries, and dashboard BFF plugin registration with a feature flag for agent views. The operator's runtime capabilities (agent registration, discovery, sidecar injection) already exist upstream and are not part of this strategy.

**Components**: kagenti-operator, AuthBridge (kagenti-extensions), rhods-operator, odh-dashboard

### Technical Approach

This strategy productizes an existing upstream operator rather than building new functionality. The kagenti-operator provides three controllers (AgentRuntimeReconciler, MLflowReconciler, ClientRegistrationController), a mutating admission webhook for AuthBridge sidecar injection, and the AgentRuntime CRD (`agent.kagenti.dev/v1alpha1`). AgentRuntime is the single CRD for agent workload management; there is no separate AgentCard CRD. Agent metadata is fetched by the AgentRuntimeReconciler from the workload's `/.well-known/agent-card.json` endpoint via mTLS and stored inline in `AgentRuntime.Status.Card`. The work here is build pipeline onboarding, platform integration, and packaging.

#### Konflux Build Pipeline

Two image families need Konflux onboarding:

1. **kagenti-operator image**: Go binary built from `opendatahub-io/kagenti-operator` (midstream fork of `kagenti/kagenti-operator`). Requires FIPS-compliant compilation (`CGO_ENABLED=1`, `GOEXPERIMENT=strictfipsruntime`) on UBI9 base, consistent with all other RHOAI Go operators. The Dockerfile must follow the multi-stage pattern used by rhods-operator, model-registry-operator, and others: builder stage compiles with FIPS flags, production stage copies the binary to `ubi9/ubi-minimal`.

1. **AuthBridge sidecar images**: Go binary built from `opendatahub-io/kagenti-extensions` (midstream fork of `kagenti/kagenti-extensions`). Three image variants exist upstream: `authbridge-proxy` (full proxy), `authbridge-envoy` (Envoy ext_proc mode), and `authbridge-lite` (auth-only). For TP, the minimum viable set is `authbridge-proxy` (default mode). Each variant needs its own Konflux component with FIPS-compliant Go compilation.

All images must include `rpms.lock.yaml` for RPM lockfile pinning and `go.sum` for Go dependency locking. SHA256-pinned image references go into the CSV as `RELATED_IMAGE_*` environment variables for disconnected/air-gapped installation support.

#### DSC Component Controller Integration

Register kagenti-operator as a new component in the rhods-operator component registry (`internal/controller/components/`). This follows the established pattern with 16 existing precedents:

1. **Component CRD**: Define a new `KagentiOperator` kind in the `components.platform.opendatahub.io/v1alpha1` group, following the same pattern as `ModelRegistry`, `Trainer`, `FeastOperator`, and other component CRDs. This CRD manages the lifecycle of the kagenti-operator deployment within RHOAI.

1. **Component controller**: Implement the standard action pipeline: initialize, releases, kustomize render, deploy, check deployments, garbage collect. The controller registers in `internal/controller/components/registry/` and the DSC controller iterates the registry to manage it.

1. **ManagementState lifecycle**: Support `Managed` (deploy operator + CRDs + RBAC + webhook) and `Removed` (clean up all operator-managed resources including the controller Deployment, RBAC resources, CRDs, and namespace-scoped resources). Default to `Removed` for TP (opt-in).

1. **Kustomize manifests**: Pull upstream manifests from the midstream fork via `get_all_manifests.sh` at pinned commits. Store in `prefetched-manifests/kagenti-operator/`. Apply RHOAI-specific overlays for namespace, image references, and RBAC adjustments.

1. **Namespace**: Deploy the kagenti-operator into `redhat-ods-applications`, consistent with all other platform component operators. The operator itself watches all namespaces for AgentRuntime CRs, deploying agent workloads into user-defined namespaces.

#### OLM/CSV Packaging

Add kagenti-operator images to the ClusterServiceVersion:

* `RELATED_IMAGE_KAGENTI_OPERATOR`: kagenti-operator image (SHA256 pinned)
* `RELATED_IMAGE_AUTHBRIDGE_PROXY`: AuthBridge proxy sidecar image (SHA256 pinned)
* Additional AuthBridge variants as needed for future modes

The CSV must declare the new `KagentiOperator` CRD and include RBAC for the component controller to manage kagenti-operator resources.

#### Dashboard BFF Plugin Registration

Register a kagenti dashboard plugin using the odh-dashboard Module Federation architecture. This involves:

1. **Feature flag**: Add a `disableKagenti` flag (or equivalent) to the `OdhDashboardConfig` CR, gated by the DSC component state. When the kagenti-operator component is `Removed` in DSC, the dashboard hides all agent-related UI elements.

1. **BFF plugin**: A new Go BFF container following the pattern of `gen-ai-ui`, `maas-ui`, and other federated modules. The BFF proxies requests to the Kubernetes API for AgentRuntime CR management. It runs as a sidecar container in the dashboard pod on a dedicated port (next available in the 8043-8743 range).

1. **TP scope**: For Tech Preview, the dashboard integration provides basic agent visibility (list AgentRuntime CRs, show status, link to workload details). Full agent management UI is out of scope for this strategy.

### Affected Components

| Component | Change | Owner Team |
| --- | --- | --- |
| kagenti-operator | Konflux build onboarding, FIPS-compliant Go compilation, UBI9 base image, midstream fork setup | Kagenti |
| kagenti-extensions (AuthBridge) | Konflux build onboarding for AuthBridge proxy sidecar images, FIPS-compliant Go compilation | Kagenti |
| rhods-operator | New `KagentiOperator` component controller, DSC CR schema extension, kustomize manifest integration, CSV updates | Platform / ODH Operator |
| odh-dashboard | BFF plugin for agent views, feature flag in OdhDashboardConfig, Module Federation registration | Dashboard |

### Impacted Teams

| Team | Components Owned | Involvement |
| --- | --- | --- |
| Kagenti | kagenti-operator, kagenti-extensions | Konflux onboarding, midstream fork maintenance, upstream-first development, operator and AuthBridge image builds |
| Platform / ODH Operator | rhods-operator | Component controller implementation, DSC schema extension, CSV packaging, kustomize manifest integration |
| Dashboard | odh-dashboard | BFF plugin development, feature flag wiring, Module Federation integration |
| QE | N/A | Test plan creation, E2E test development for component lifecycle, disconnected validation |
| Docs | N/A | Installation and upgrade documentation for enabling kagenti-operator via DSC |

### High Level Requirements

* \[P0\] Operator images built via Konflux with FIPS-compliant Go compilation (`GOEXPERIMENT=strictfipsruntime`, `CGO_ENABLED=1`) on UBI9 base (RFE acceptance criterion)
* \[P0\] Operator enabled/disabled via DataScienceCluster CR following the standard component controller pattern with `managementState: Managed/Removed` (RFE acceptance criterion)
* \[P0\] When disabled (`managementState: Removed`), all operator-managed resources are cleaned up: controller Deployment, RBAC, CRDs, namespace-scoped resources (RFE acceptance criterion)
* \[P0\] Upstream-first policy: significant changes go to `kagenti/*` repos before being pulled into `opendatahub-io/*` midstream forks (RFE acceptance criterion)
* \[P0\] Tech Preview maturity level with explicit opt-in (disabled by default in DSC) (RFE acceptance criterion)
* \[P1\] Dashboard integration infrastructure: BFF plugin registration and feature flag for agent views (RFE acceptance criterion)
* \[P1\] OLM/CSV packaging with `RELATED_IMAGE_*` entries for disconnected installation
* \[P1\] AuthBridge proxy sidecar image built via Konflux with FIPS compliance
* \[P2\] Multi-arch builds (AMD64 required for TP; arm64 if pipeline supports it without additional effort)

### Dependencies

| Dependency | Type | Status | Impact if Blocked |
| --- | --- | --- | --- |
| Upstream kagenti-operator (functional, with AgentRuntime CRD) | External | Exists (kagenti GitHub org) | Cannot productize without a working upstream operator. If upstream is incomplete, the team must finish it first, increasing effort. |
| Upstream kagenti-extensions (AuthBridge sidecar) | External | Exists (kagenti GitHub org) | AuthBridge images cannot be built without functional upstream code. |
| Midstream forks in opendatahub-io | Internal | Exists (opendatahub-io/kagenti-operator) | Required for Konflux builds. Fork sync process must be established. |
| Konflux build pipeline capacity | Internal | Needs submission | Build pipeline onboarding has lead time. Late submission risks missing code-complete deadline. |
| rhods-operator component registry pattern | Internal | Exists (16 precedents) | Well-established pattern; low risk. |
| odh-dashboard Module Federation infrastructure | Internal | Exists (7 BFF plugins) | Well-established pattern; low risk. |

### Non-Functional Requirements

* **FIPS compliance**: All Go binaries must be compiled with `GOEXPERIMENT=strictfipsruntime` and `CGO_ENABLED=1`, matching the platform-wide FIPS posture. AuthBridge sidecar proxy handles TLS termination and must use FIPS-approved cipher suites (architecture context: rhods-operator.md, kube-rbac-proxy FIPS cipher suite list).
* **Container security**: Non-root execution (USER 65532:65532 for Go operators, following distroless convention), capability dropping (`capabilities.drop: ["ALL"]`), `seccompProfile.type: RuntimeDefault` (architecture context: PLATFORM.md container security patterns).
* **Disconnected installation**: All images referenced via `RELATED_IMAGE_*` environment variables with SHA256-pinned digests in the CSV. This enables OLM relatedImages for air-gapped operation with image mirroring (architecture context: PLATFORM.md).
* **Backwards compatibility**: As a new TP component, no backwards compatibility concerns. The component defaults to `Removed` (disabled), so existing clusters are unaffected by the RHOAI upgrade.
* **Resource cleanup on disable**: When `managementState` transitions to `Removed`, the component controller must delete: the kagenti-operator Deployment, all associated RBAC (ClusterRoles, ClusterRoleBindings, Roles, RoleBindings), the AgentRuntime CRD, the mutating webhook configuration, and any namespace-scoped resources (ConfigMaps, Secrets) in `redhat-ods-applications`. This follows the garbage collection pattern used by all existing component controllers (architecture context: rhods-operator.md component action pipeline).

### Out-of-Scope

* Agent registration, discovery, and lifecycle management runtime behavior (tracked in RHAIRFE-7587). This strategy productizes the operator; RHAIRFE-7587 covers its runtime features.
* Agent metadata extraction and sync (RHAIRFE-7588).
* Agent Runtime Contract / ARC specification and injection (RHAIRFE-7589).
* Agent identity and authorization, including SPIFFE binding, agent attestation, and trust enforcement (RHAIRFE-7408, explicitly separated per April 25 RFE revision).
* Full agent management UI in the dashboard. TP scope is read-only agent list with status display.
* Kagenti backend (FastAPI) and full React UI deployment. These are part of the kagenti Helm chart and may be addressed separately.
* Observability stack for agent workloads (PodMonitor/ServiceMonitor, agent-specific dashboards). The operator itself will be monitored via the standard platform monitoring pattern, but agent workload metrics depend on the ARC (RHAIRFE-7589).
* Keycloak deployment or OAuth2 client registration infrastructure. These are prerequisites managed outside this strategy.

### Acceptance Criteria (Proposed -- requires PM/Engineering validation)

1. Given a fresh RHOAI deployment with DSC configured with kagenti-operator `managementState: Managed`,

   when the DSC controller reconciles,    then the kagenti-operator Deployment is created in `redhat-ods-applications` with the Konflux-built image,    measured by `kubectl get deployment -n redhat-ods-applications -l app=kagenti-operator` returning a Ready deployment.

1. Given the kagenti-operator component is `Managed` in DSC,

   when a user creates an AgentRuntime CR in their namespace referencing an existing Deployment,    then the operator's AgentRuntimeReconciler applies the `kagenti.io/type: agent` label to the target workload,    measured by `kubectl get deployment <name> -o jsonpath='{.metadata.labels.kagenti\.io/type}'` returning `agent`.

1. Given the kagenti-operator component is changed from `Managed` to `Removed` in DSC,

   when the component controller reconciles the state change,    then all operator-managed resources (Deployment, RBAC, CRDs, webhook configuration) are deleted from the cluster,    measured by `kubectl get deployment -n redhat-ods-applications -l app=kagenti-operator` returning no results, and `kubectl get crd agentrimes.agent.kagenti.dev` returning "not found".

1. The kagenti-operator container image passes Konflux build pipeline `check-payload` validation for FIPS compliance (binary linked against OpenSSL, no statically-linked Go crypto).

1. The AuthBridge proxy sidecar container image passes Konflux build pipeline `check-payload` validation for FIPS compliance.

1. Given the odh-dashboard is deployed with the kagenti BFF plugin enabled (feature flag active),

   when a user navigates to the agent views section,    then the dashboard displays a list of AgentRuntime CRs from the user's accessible namespaces,    measured by the dashboard rendering AgentRuntime data retrieved via the BFF API proxy.

1. Given a disconnected RHOAI installation using image mirroring,

   when the kagenti-operator component is `Managed`,    then the operator and AuthBridge images are resolved from the mirrored registry via `RELATED_IMAGE_*` environment variables,    measured by the kagenti-operator Deployment running with images from the mirror registry.

### Effort Estimate

**L (6-9 sprints)** - justified but at the higher end of L:

* **Konflux onboarding (2-3 sprints)**: Two image families (operator + AuthBridge), each requiring Dockerfile conversion, FIPS build flag integration, RPM lockfile setup, and pipeline validation. This is procedural but has lead time.
* **rhods-operator component controller (2-3 sprints)**: Well-precedented pattern (16 existing controllers), but includes CRD definition, kustomize manifest integration, garbage collection logic, and DSC schema extension. Testing the Managed/Removed lifecycle thoroughly adds time.
* **OLM/CSV packaging (1 sprint)**: Adding RELATED_IMAGE entries, CRD declarations, and RBAC to the CSV. Straightforward with existing tooling.
* **Dashboard BFF plugin (1-2 sprints)**: Module Federation is well-established (7 existing plugins), but a new BFF for AgentRuntime requires Go backend implementation and basic React UI for the agent list view.
* **QE and documentation (1 sprint)**: Test plan, E2E tests for component lifecycle, disconnected validation, installation docs.

The L estimate assumes the upstream kagenti-operator is functional and the midstream fork is ready. If upstream gaps exist that require operator development work, the estimate shifts to XL. The CRD schema (AgentRuntime) is already defined upstream per overlay 0014, which removes a previously-flagged sizing risk. The removal of the AgentCard CRD simplifies the operator surface area (three controllers instead of six in earlier iterations), which supports the L estimate.

### Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Konflux onboarding misses code-complete deadline | Operator images not available for 3.5 release, blocking the entire strategy | Submit Konflux onboarding request immediately. Track as P0 with weekly status checks against the deadline. If submission is delayed past 2 weeks before deadline, escalate to platform lead for expedited processing. |
| Upstream kagenti-operator has functional gaps | Additional development work needed, pushing effort to XL and potentially missing 3.5 timeline | Validate the upstream operator against the three controllers listed in overlay 0014 within the first sprint. Create a gap analysis document. If gaps exceed 2 sprints of work, negotiate scope reduction for TP (e.g., defer MLflowReconciler, defer ClientRegistrationController). |
| AuthBridge sidecar injection conflicts with platform webhook ordering | Pod creation failures or unexpected sidecar behavior when combined with other mutating webhooks (HardwareProfile, connection injection) | Test webhook ordering explicitly in E2E suite. The kagenti webhook uses `reinvocationPolicy: IfNeeded`, which handles ordering conflicts. If conflicts arise, set explicit `webhookOrder` annotations. |
| DSC component cleanup leaves orphaned resources | AgentRuntime CRs or webhook configurations persist after component is disabled | Implement explicit finalizer on the component CR that enumerates and deletes all owned resources. Test cleanup in E2E suite with resources in multiple namespaces. |
| Dashboard BFF plugin port collision | New BFF sidecar port conflicts with existing Module Federation ports | Allocate the next available port in the 8043-8743 range. Verify against current assignments (8043-model-registry, 8143-gen-ai, 8243-maas, 8343-mlflow, 8443-eval-hub, 8543-automl, 8643-autorag). |

### Assumptions

* A functional upstream kagenti-operator exists in the `kagenti` GitHub org with the AgentRuntime CRD and core controllers -- needs validation (critical, must validate in sprint 1)
* The midstream fork `opendatahub-io/kagenti-operator` is set up and synced with upstream -- needs validation
* The AgentRuntime CRD schema (`agent.kagenti.dev/v1alpha1`) is stable enough for TP -- needs validation (CRD field changes after productization require migration)
* The Konflux build pipeline supports Go 1.25 with `GOEXPERIMENT=strictfipsruntime` (same version used by rhods-operator) -- confirmed (architecture context: rhods-operator uses Go 1.25)
* The kagenti-operator can run in `redhat-ods-applications` namespace alongside other platform operators without RBAC conflicts -- needs validation
* AuthBridge proxy sidecar images can be built with UBI9 base following the same pattern as other Go sidecars -- confirmed (standard pattern)

### Open Questions

| Question | Why It Matters | Owner |
| --- | --- | --- |
| Is the upstream kagenti-operator functional with all three controllers listed in overlay 0014? | If the operator is incomplete, effort estimate changes from L to XL. Validate against: AgentRuntimeReconciler (including metadata fetch from `/.well-known/agent-card.json`), MLflowReconciler, ClientRegistrationController. | Kagenti team |
| Which AuthBridge sidecar variants are needed for TP? | `authbridge-proxy` is the default. Are `authbridge-envoy` and `authbridge-lite` needed for 3.5, or can they ship in a later release? Each variant requires a separate Konflux component. | Kagenti team / PM |
| Dashboard integration depth for TP: minimal agent list tab vs. standalone navigation entry? | Affects dashboard BFF scope and effort. A tab in an existing project view is \~1 sprint; a standalone section is \~2 sprints. | PM / UX |
| Does the kagenti-operator require Keycloak as a runtime dependency? | The ClientRegistrationController manages OAuth2 client registration with Keycloak. If Keycloak is required, it becomes an external dependency that must be documented and validated. For TP, can this controller be disabled? | Kagenti team |
| What happens to AgentRuntime CRs in user namespaces when the component is disabled via DSC? | The component controller cleans up operator-managed resources in `redhat-ods-applications`, but user-created CRs in other namespaces may become orphaned. Should the cleanup include cross-namespace CRD deletion? | Platform / ODH Operator team |

### Supporting Documentation

* Source RFE: RHAIRFE-7451
* Architecture context: PLATFORM.md (component controller pattern, FIPS compliance, container security), rhods-operator.md (component registry, DSC integration, kustomize manifest rendering, CSV packaging)
* Architecture context overlay: 0014 (kagenti-operator architecture, AgentRuntime CRD, AuthBridge, controller inventory)
* Related strategies: RHAISTRAT-7359 (Kagenti codebase cleanup, 3.4), RHAISTRAT-7559 (Kagenti operator quality / E2E tests)
* Related RFEs: RHAIRFE-7587 (agent lifecycle), RHAIRFE-7588 (agent metadata), RHAIRFE-7589 (Agent Runtime Contract), RHAIRFE-7408 (agent identity/authorization)
* Design doc: \_To be created\_ (ADR for CRD schema decisions and image contract)
* Konflux onboarding guide: \_Link to internal Konflux onboarding docs\_

### Prerequisites & Process Gates

| Prerequisite | Status | Notes |
| --- | --- | --- |
| Architecture Review | \_Pending human review\_ | Overlay 0014 provides initial architecture context |
| ODH/RHOAI Build Onboarding | \_Pending human review\_ | Konflux onboarding is the critical-path item |
| Licence Validation | \_Pending human review\_ | Upstream kagenti repos use Apache 2.0 |
| Accelerator/Package Support | \_Pending human review\_ |  |
| Documentation Support | \_Pending human review\_ | Installation docs needed for DSC component enablement |
| UXD Support | \_Pending human review\_ | Dashboard plugin requires UX design for agent list view |
| Performance Team Support | \_Pending human review\_ |  |

## Staff Engineer / SME Input

_Add technical corrections, architectural direction, component preferences, or domain expertise below. Write in declarative, cumulative form — statements that remain valid across refinement iterations. This input takes priority over architecture context when they conflict. After review: address findings, then remove the needs-attention label from Jira._
