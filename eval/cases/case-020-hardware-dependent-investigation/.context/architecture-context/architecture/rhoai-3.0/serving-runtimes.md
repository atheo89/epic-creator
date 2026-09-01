# Serving Runtimes

**Jira component**: Serving Runtimes
**Maturity**: Stable (GA)
**Owning team**: RHOAI Serving
**Upstream**: vllm-project/vllm, openvinotoolkit/model_server, caikit/caikit
**Midstream**: opendatahub-io/vllm, red-hat-data-services/vllm
**Konflux onboarded**: yes

## Role in the platform

Productized model runtimes executed under KServe InferenceServices: vLLM (LLM
serving, the default GenAI runtime), OpenVINO Model Server, and Caikit. Runtime
images are built and released per platform version; only CUDA (NVIDIA) builds
are currently productized — ROCm and Gaudi builds exist upstream but are not
shipped or supported.

## Dependencies

- KServe for lifecycle and routing (ServingRuntime CRD)
- NVIDIA GPU Operator for accelerator discovery on supported hardware

## Interfaces

- ServingRuntime / ClusterServingRuntime CRDs (serving.kserve.io)
- OpenAI-compatible endpoints exposed by vLLM-based runtimes
