# Llama Stack

**Jira component**: Llama Stack
**Maturity**: Tech Preview
**Owning team**: RHOAI GenAI
**Upstream**: meta-llama/llama-stack
**Midstream**: opendatahub-io/llama-stack-k8s-operator
**Konflux onboarded**: yes

## Role in the platform

Unified GenAI API layer (inference, RAG, agents, safety, eval) deployed as a
LlamaStackDistribution CR. Positions the platform's OpenAI-compatible endpoint
surface and provider-plugin model. The eval provider API exists upstream but no
production eval provider is wired in the platform distribution yet.

## Dependencies

- vLLM (Serving Runtimes) as the default inference provider
- Milvus/vector providers for RAG workflows (optional)

## Interfaces

- LlamaStackDistribution CRD (llamastack.io)
- OpenAI-compatible REST APIs; provider plugins configured per distribution
