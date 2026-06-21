# LLM Basics for QA/SDET

This document is a practical LLM foundation guide for QA Engineers and SDETs.
It combines:
- Core concepts you need to test LLM systems well.
- A QA/SDET explanation of the Transformer paper: https://arxiv.org/html/1706.03762v7
- A complete keyword glossary based on your requested list.

## 1) Why This Matters for QA/SDET

Traditional app testing checks deterministic logic.
LLM app testing also needs to validate probabilistic behavior, prompt safety, grounding, latency, cost, and failure handling.

Your testing scope must cover:
- Model behavior quality.
- Retrieval/tooling correctness.
- Security hardening.
- Reliability and observability in production.

## 2) Transformer Paper (arXiv:1706.03762v7) Explained for QA/SDET

Paper: **Attention Is All You Need**
Version in link: **v7**, dated **August 2, 2023** on arXiv (historical paper with updated arXiv metadata).

### 2.1 What the paper changed

Before Transformer, sequence tasks relied heavily on RNN/CNN families.
The paper proposed replacing recurrence/convolution with attention mechanisms.

Key outcomes reported in the paper:
- Transformer architecture with encoder-decoder stacks.
- Better parallelization than recurrent approaches.
- Strong machine translation results (including 28.4 BLEU EN-DE for Transformer big, 41.8 BLEU EN-FR single model in reported setup).

### 2.2 Core architecture (test-friendly mental model)

```text
Input Tokens
   -> Embeddings + Positional Encoding
   -> Encoder Layers (Self-Attention + FeedForward + Residual + Norm)
   -> Decoder Layers (Masked Self-Attention + Cross-Attention + FeedForward)
   -> Linear + Softmax
   -> Next Token
```

### 2.3 Why QA/SDET should care

The paper defines behaviors you still test in modern LLM systems:
- **Attention behavior**: model can focus on relevant context.
- **Masking behavior**: decoder should not peek future tokens.
- **Long-range dependency handling**: quality under long context.
- **Latency vs length tradeoff**: attention cost grows with sequence length.

### 2.4 QA test cases inspired by the paper

1. Long-context degradation tests
- Increase input length stepwise.
- Track quality, latency, and truncation behavior.

2. Masking/causal behavior tests
- Ensure the model does not leak future answer fragments in staged prompts.

3. Positional sensitivity tests
- Reorder sentence fragments and evaluate semantic drift.

4. Robustness to paraphrase
- Same intent, varied wording, similar output quality expected.

5. Throughput and parallel load tests
- Concurrency tests under realistic token load.

6. Regression suite on benchmark prompts
- Keep golden tasks to detect model/prompt changes.

## 3) LLM System Diagrams for QA/SDET

### 3.1 Inference + RAG pipeline

```text
User Prompt
 -> Guardrails
 -> Retriever (optional)
 -> Context Assembly
 -> LLM Inference
 -> Structured Output Validation
 -> App Response
 -> Logging/Tracing/Monitoring
```

### 3.2 Agent workflow

```text
User Goal
 -> Planner
 -> Tool Selection
 -> Tool Invocation
 -> Memory Read/Write
 -> Executor
 -> Reflection/Retry
 -> Final Answer
```

### 3.3 Training-to-production lifecycle

```text
Pretraining -> Instruction Tuning/SFT -> RLHF/Alignment
-> Evaluation/Red Teaming -> Deployment
-> Observability/LLMOps -> Continuous Improvement
```

## 4) Complete LLM Basics Glossary (QA/SDET-Oriented)

## 4.1 Foundations and Prompting

| Term | Meaning | QA/SDET focus |
|---|---|---|
| LLM | Large Language Model that predicts and generates text tokens. | Validate quality, safety, and consistency across test sets. |
| Transformer | Attention-based neural architecture used by most modern LLMs. | Test long-context behavior and scaling impacts. |
| Token | Small text unit processed by model (word piece/subword). | Verify token budget boundaries and truncation. |
| Tokenization | Process that converts text to tokens and back. | Test edge cases: Unicode, emojis, mixed-language, code blocks. |
| Context Window | Max token span model can consider in one inference. | Test boundary prompts near max window. |
| Prompt | Input instruction/context sent to the model. | Validate prompt templates and required variables. |
| Prompt Engineering | Designing prompts for reliable model behavior. | Maintain prompt regression tests and output contracts. |
| System Prompt | Highest-priority instruction controlling assistant behavior. | Test policy precedence vs user instructions. |
| User Prompt | User-provided message/question. | Fuzz test ambiguous, adversarial, and malformed inputs. |
| Temperature | Sampling randomness control. Lower is more deterministic. | Assert repeatability at low temperature. |
| Top-P | Nucleus sampling threshold for token selection. | Compare response variability across values. |
| Top-K | Sampling from top K likely tokens. | Validate quality/creativity tradeoff in tuned configs. |
| Max Tokens | Max generated output token count. | Ensure truncation and stop behavior are graceful. |
| Stop Sequence | Token/text pattern where generation must stop. | Test leak prevention and early termination correctness. |

## 4.2 Retrieval, Embeddings, and RAG

| Term | Meaning | QA/SDET focus |
|---|---|---|
| Embedding | Dense numeric representation of text meaning. | Validate same-text stability and semantic grouping. |
| Vector | Numeric array representing semantic features. | Check dimensions and schema consistency. |
| Vector Similarity | Score for semantic closeness of vectors. | Verify nearest-neighbor ranking on known pairs. |
| Cosine Similarity | Common vector angle-based similarity metric. | Unit test expected high/low similarity examples. |
| Vector Database | Store optimized for vectors + nearest-neighbor search. | Test ingest integrity, filters, persistence, and recall. |
| Chunking | Splitting documents into smaller retrieval units. | Evaluate chunk size/overlap impact on answer quality. |
| Document Loader | Component to read files/web/docs into pipeline. | Test parsing failures, file type handling, encoding issues. |
| Text Splitter | Utility to split text by size/semantic boundaries. | Validate no data loss and stable chunk IDs. |
| Retrieval | Fetching relevant context from KB/vector store. | Measure precision@k, recall@k, and latency. |
| Retriever | Component implementing retrieval strategy. | Compare BM25/vector/hybrid retriever quality. |
| Semantic Search | Meaning-based retrieval using embeddings. | Test synonym and paraphrase retrieval quality. |
| RAG (Retrieval Augmented Generation) | Grounding generation with retrieved context. | Assert citations/grounding and fallback on missing context. |
| Hybrid Search | Combines lexical + semantic retrieval. | Validate improved recall on exact IDs + fuzzy intent. |
| Indexing | Preprocessing + storing searchable document representations. | Verify re-indexing, versioning, and duplicate handling. |
| Re-ranking | Reordering retrieved candidates with stronger ranker. | Test top-n relevance improvement vs latency overhead. |
| Grounding | Constraining answers to trusted context/sources. | Detect unsupported claims in output. |
| Hallucination | Confident but unsupported/incorrect model output. | Run hallucination benchmark and policy checks. |
| Knowledge Base | Curated domain repository for retrieval. | Validate freshness, ownership, and update workflows. |
| Knowledge Graph | Entity-relationship graph for structured reasoning. | Test relation query correctness and graph consistency. |
| Embedding Model | Model used to generate embeddings. | Ensure ingest/query use same embedding model family. |

## 4.3 Model Internals and Architecture

| Term | Meaning | QA/SDET focus |
|---|---|---|
| Attention | Mechanism weighting relevant tokens for each step. | Probe attention-sensitive tasks and long dependencies. |
| Self-Attention | Attention where sequence tokens attend to each other. | Test contextual resolution across long prompts. |
| Multi-Head Attention | Multiple attention heads learning different relations. | Evaluate robustness on varied linguistic patterns. |
| Positional Encoding | Position signal added so order is represented. | Test sentence-order changes and meaning preservation. |
| Decoder | Generates output tokens autoregressively. | Verify causal behavior and stop conditions. |
| Encoder | Produces contextual representation from input sequence. | Test representation quality on classification/retrieval tasks. |
| Encoder-Decoder | Two-stack architecture for seq2seq tasks. | Validate cross-attention behavior on translation-style tasks. |
| Autoregressive Model | Generates one token at a time from prior tokens. | Check next-token drift and error accumulation. |
| Next Token Prediction | Objective to predict following token. | Use perplexity-style regression for baseline changes. |
| Parameters | Trainable scalar values in a model. | Track model variant differences in performance/cost. |
| Weights | Learned parameter tensors in layers. | Validate model checksum/versioning in deployment. |

## 4.4 Training and Alignment

| Term | Meaning | QA/SDET focus |
|---|---|---|
| Pretraining | Large-scale unsupervised training on broad corpora. | Understand baseline strengths/weaknesses and bias origin. |
| Training Dataset | Data used for model training phases. | Audit data quality, leakage, and representativeness. |
| Fine-tuning | Additional training for domain/task adaptation. | Regression-test pre/post fine-tune behavior. |
| Instruction Tuning | Fine-tuning on instruction-response examples. | Validate instruction-following and refusal behavior. |
| Supervised Fine-Tuning (SFT) | Label-based fine-tuning with curated outputs. | Check overfitting and style constraints. |
| Reinforcement Learning from Human Feedback (RLHF) | Preference-based optimization using reward models/human feedback. | Validate helpfulness vs harmlessness tradeoffs. |
| Alignment | Techniques to keep model behavior aligned with goals/policies. | Test policy adherence under adversarial prompts. |
| Safety Guardrails | Safety controls to reduce harmful outputs/actions. | Build harmful-content and abuse scenario suites. |
| Perplexity | Metric for uncertainty over token prediction. | Use for model comparison trends, not sole quality metric. |
| Distillation | Compressing larger model knowledge into smaller model. | Compare quality drop vs latency/cost gains. |
| Model Quantization | Reducing numeric precision for efficiency. | Validate latency gain and accuracy regression thresholds. |
| Mixture of Experts (MoE) | Architecture routing tokens to selected expert subnetworks. | Test routing stability and tail-latency behavior. |

## 4.5 Reasoning and Prompting Strategies

| Term | Meaning | QA/SDET focus |
|---|---|---|
| Chain of Thought (CoT) | Prompting strategy encouraging intermediate reasoning steps. | Check answer quality gains vs verbosity/safety concerns. |
| Self-Consistency | Sampling multiple reasoning paths and selecting consistent answer. | Evaluate accuracy improvement vs higher token cost. |
| Few-Shot Learning | Providing several examples in prompt. | Validate sensitivity to example quality/order. |
| Zero-Shot Learning | No examples; model relies on instruction only. | Benchmark baseline ability without demonstrations. |
| One-Shot Learning | Single example provided in prompt. | Compare to zero-shot/few-shot outcomes. |
| In-Context Learning | Learning behavior from prompt context without weight updates. | Test context contamination and instruction conflict handling. |

## 4.6 Inference, Performance, and Cost

| Term | Meaning | QA/SDET focus |
|---|---|---|
| LLM Inference | Runtime generation using trained model weights. | Measure p50/p95 latency and error rate. |
| Latency | Time to get response (first token/full response). | Set SLOs and validate under load. |
| Throughput | Requests/tokens processed per time unit. | Stress test concurrency and scaling. |
| Streaming | Returning tokens incrementally while generating. | Validate partial outputs and stream termination behavior. |
| Batch Inference | Processing multiple inputs in grouped execution. | Verify ordering and per-item output integrity. |
| API Endpoint | URL/function exposing model capability. | Contract test schema, auth, and error codes. |
| Rate Limit | Allowed request/token frequency caps. | Test retry/backoff and user-facing errors. |
| Cost per Token | Billing metric tied to token usage. | Create budget alerts and cost regression tests. |
| Token Usage | Count of input/output tokens consumed. | Validate telemetry and cost attribution accuracy. |
| Structured Output | Model output constrained to schema. | Enforce JSON schema validation in tests. |
| JSON Mode | Generation mode targeting valid JSON output. | Fuzz malformed prompts and verify valid JSON recovery. |

## 4.7 Tool Use, Agents, and Memory

| Term | Meaning | QA/SDET focus |
|---|---|---|
| Function Calling | Model returns tool/function arguments instead of free text. | Validate argument schema and tool selection correctness. |
| Tool Use | Model invokes external systems (search, DB, APIs). | Test tool timeout, retries, and fallback logic. |
| Agent | LLM-driven system deciding actions and tools iteratively. | Validate plan quality and bounded execution steps. |
| Agent Framework | Runtime/orchestration library for agent loops. | Test state transitions and error propagation. |
| Multi-Agent System | Multiple collaborating agents with roles. | Validate coordination, conflict handling, and deadlock avoidance. |
| Planner | Component generating task plan/subgoals. | Assert plan completeness and constraint awareness. |
| Executor | Component performing planned actions/tools. | Verify execution safety, retries, and idempotency. |
| Reflection | Self-critique loop to improve intermediate outputs. | Check quality gain vs latency/cost overhead. |
| Memory | Stored context across steps/conversations. | Validate memory write/read correctness and privacy. |
| Short-Term Memory | Session-scoped temporary context. | Ensure expiry and reset between sessions. |
| Long-Term Memory | Persistent memory across sessions. | Test stale memory and conflict resolution. |
| Conversation Memory | History of dialogue turns used for continuity. | Check context-window truncation and summarization quality. |
| External Memory | Memory in external stores (DB/vector/KG). | Validate retrieval freshness and access controls. |
| Agent Workflow | End-to-end graph of planning, tools, memory, and response. | Trace each transition with deterministic logs. |
| Tool Invocation | Actual execution call to a selected tool. | Contract-test inputs/outputs and failure handling. |

## 4.8 Security, Safety, and Evaluation

| Term | Meaning | QA/SDET focus |
|---|---|---|
| Guardrails | Rules/filters to constrain unsafe or invalid model behavior. | Test deny/allow paths and false-positive rate. |
| Prompt Injection | Malicious prompt tries to override system/tool policies. | Run adversarial corpora and check policy isolation. |
| Jailbreak | Attempts to bypass model safety constraints. | Maintain evolving jailbreak test suites. |
| Evaluation Benchmark | Standardized task set for objective comparison. | Track quality trend release-over-release. |
| Model Benchmark | Comparative metrics across models/configurations. | Select model by quality-latency-cost tradeoff. |
| Red Teaming | Structured adversarial testing for security and abuse. | Include privacy, harmful output, and tool abuse scenarios. |
| Safety Guardrails | Explicit safety control layer for policy compliance. | Validate content moderation + refusal consistency. |

## 4.9 Observability and Operations

| Term | Meaning | QA/SDET focus |
|---|---|---|
| Observability | Ability to inspect system behavior via logs/metrics/traces. | Ensure end-to-end visibility per request ID. |
| Tracing | Step-level timeline of prompts, tools, and model calls. | Debug failures and latency bottlenecks quickly. |
| Model Monitoring | Continuous tracking of quality, drift, latency, and failures. | Alert on regression thresholds. |
| LLMOps | Operational discipline for LLM lifecycle in production. | Standardize deployment gates and rollback plans. |
| AI Pipeline | Full flow from data to model to application response. | Test stage contracts and recovery points. |

## 5) QA/SDET Test Strategy Template for LLM Apps

Use this as a minimum checklist:

1. Functional quality
- Golden prompt suites by domain.
- Correctness scoring with rubric.

2. Retrieval quality (if RAG)
- Precision@k, Recall@k, MRR, hit-rate.
- Groundedness and citation correctness.

3. Safety and security
- Prompt injection/jailbreak corpus.
- PII leakage and policy refusal tests.

4. Reliability
- Timeout/retry/backoff tests for APIs and tools.
- Chaos tests for vector DB/tool outages.

5. Performance and cost
- p50/p95 latency by token bucket.
- Cost per request regression tracking.

6. Observability
- Request-level tracing across model + tools.
- Dashboard alerts for drift and failure spikes.

## 6) Quick Study Path for QA/SDET

Recommended order:
1. LLM, Transformer, Tokenization, Prompt basics.
2. Attention, Context Window, decoding controls.
3. Embeddings, Retrieval, RAG, Hybrid Search.
4. Agents, Tool Use, Function Calling, Memory.
5. Guardrails, Red Teaming, Monitoring, LLMOps.

## 7) References

- Vaswani et al., *Attention Is All You Need* (arXiv HTML): https://arxiv.org/html/1706.03762v7
- arXiv abstract page: https://arxiv.org/abs/1706.03762

