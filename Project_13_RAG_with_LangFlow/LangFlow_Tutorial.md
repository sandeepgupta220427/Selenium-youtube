# Project 13: LangFlow RAG Component Handbook

This guide is LangFlow-only.
It documents how LangFlow works and explains every major component used across your RAG flows.

Source flows referenced from Project 12:
- `../Project_13_RAG_with_LangFlow/02_Naive_RAG_Flow/naive_rag_langflow.json`
- `../Project_13_RAG_with_LangFlow/03_Advanced_RAG_Flow/advanced_rag_langflow.json`
- `../Project_13_RAG_with_LangFlow/04_Modular_RAG_Flow/modular_rag_langflow.json`
- `../Project_13_RAG_with_LangFlow/05_Graph_RAG_Flow/graph_rag_langflow.json`
- `../Project_13_RAG_with_LangFlow/06_Agentic_RAG_Flow/agentic_rag_langflow.json`
- `../Project_13_RAG_with_LangFlow/07_Self_RAG_Flow/self_rag_langflow.json`
- `../Project_13_RAG_with_LangFlow/08_Corrective_RAG_Flow/corrective_rag_langflow.json`
- `../Project_13_RAG_with_LangFlow/09_Hybrid_RAG_Flow/hybrid_rag_langflow.json`
- `../Project_13_RAG_with_LangFlow/10_MultiModal_RAG_Flow/multimodal_rag_langflow.json`
- `../Project_13_RAG_with_LangFlow/11_Contextual_RAG_Flow/contextual_rag_langflow.json`

## 1) What is LangFlow?

LangFlow is a visual orchestration layer for building LLM pipelines as directed graphs.
Each node is a component. Each edge carries typed data between ports.

Typical RAG lifecycle in LangFlow:

```text
Indexing path:
Documents -> Parse/Transform -> Chunk -> Embed -> Store

Query path:
User Query -> Retrieve -> (Optional Rerank/Route/Tools) -> Prompt -> LLM -> Output
```

## 2) How LangFlow Executes a Flow

LangFlow executes based on dependency graph order.
A node runs when its required input(s) are available.

Core data types you use repeatedly:
- `Message`: chat-like text payloads.
- `Data`: structured record object used by many retrievers/components.
- `DataFrame`: tabular batch-like data returned by loaders.
- `Embeddings`: vector model handle or generated embeddings.

Execution tips:
- Build indexing and query paths separately.
- Reuse one embedding model for both ingestion and retrieval when possible.
- Keep collection names explicit per flow to avoid cross-contamination.

## 3) How to Use LangFlow Properly (Practical Workflow)

1. Import flow JSON.
2. Set API keys in all LLM/embedding/rerank/search components.
3. Run indexing path first (ingest documents).
4. Verify collection has non-empty documents and vectors.
5. Run query path.
6. Validate answer quality, grounding, and latency.

Minimal local commands often used with this project:

```bash
langflow run
chroma run --path ./chroma_db
```

## 4) Component-by-Component Reference

### 4.1 Input and Output Components

#### Chat Input (`ChatInput`)
- What it does: Entry point for user question.
- Use it when: You need runtime question input.
- Good wiring: Connect to retriever query, prompt question slot, or router input.
- Common mistake: Connecting it only to generator and skipping retriever.

#### Chat Output (`ChatOutput`)
- What it does: Final response sink.
- Use it when: You want visible chat response in Playground/UI.
- Good wiring: Connect only from final generator/evaluator node.

#### File Loader (`File`)
- What it does: Loads files (e.g., txt/pdf/csv depending on setup).
- Use it when: Ingestion starts from selected files.
- Good wiring: Connect to splitter/parser.
- Common mistake: Loading documents but never passing into splitter/vector store.

#### Directory (`Directory`)
- What it does: Recursively loads files from directory.
- Key settings: `path`, `types`, `recursive`, `depth`.
- Common mistake: Wrong path or low depth causing silent under-ingestion.

### 4.2 Parse, Transform, and Chunk Components

#### Unstructured Parser (`Unstructured`)
- What it does: Extracts text/blocks from mixed formats, including multimodal docs.
- Use it when: You ingest PDF/images/tables and need structured parsed outputs.

#### Type Convert / To Data / Context Formatter (`TypeConverterComponent`)
- What it does: Converts `Message/Data/DataFrame` between compatible formats.
- Use it when: Downstream node expects a different input type.
- Critical note: During ingestion, ensure conversion preserves text fields.
- Common mistake: Converting `DataFrame -> Data` without preserving chunk text, resulting in empty documents.

#### Text Splitter (`RecursiveCharacterTextSplitter`)
- What it does: Fixed-size chunking with overlap.
- Use it when: You need predictable chunk sizes.
- Key settings: `chunk_size`, `chunk_overlap`.

#### Semantic Text Splitter / Semantic Splitter (`SemanticTextSplitter`)
- What it does: Splits by semantic breakpoints instead of fixed length only.
- Use it when: You want meaning-preserving chunks.
- Key settings: `breakpoint_threshold_type`, `breakpoint_threshold_amount`, `number_of_chunks`.

#### Prepend Context to Chunk (`CustomComponent`)
- What it does: Enriches each chunk by adding generated context before indexing.
- Use it when: Implementing Contextual RAG.
- Benefit: Better retrieval precision for ambiguous chunks.

### 4.3 Embedding and Storage Components

#### OpenAI Embeddings (`OpenAIEmbeddings`)
- What it does: Embedding model for indexing/query vector representation.
- Typical model: `text-embedding-3-large`.
- Good wiring: Same embeddings node into splitter/store/retriever chain.
- Common mistake: Different embedding spaces between ingest and query paths.

#### Chroma / Chroma DB / Chroma Vector Store (`Chroma`)
- What it does: Vector store for ingest + similarity/MMR search.
- Key settings: `collection_name`, `persist_directory`, `search_type`, `number_of_results`.
- Good practice: One collection per use case or domain.
- Common mistake: Reusing same collection for unrelated flows without metadata filters.

### 4.4 Retrieval and Ranking Components

#### Vector Store Retriever / Vector Retriever (`Retriever`)
- What it does: Fetches semantic nearest chunks from vector store.
- Key settings: top-k equivalent controls (`number_of_results` upstream in Chroma or retriever config).
- Common mistake: too small k before reranking.

#### BM25 Retriever (`BM25Retriever`)
- What it does: Keyword-based lexical retrieval.
- Use it when: Exact terms, IDs, acronyms matter.

#### Ensemble Retriever (`EnsembleRetriever`)
- What it does: Merges multiple retrievers (e.g., BM25 + vector).
- Use it when: You need hybrid retrieval robustness.
- Example weighting: BM25 `0.4`, vector `0.6`.

#### Cohere Rerank (`CohereRerank`)
- What it does: Reorders candidate chunks by query relevance.
- Key setting: `top_n`.
- Good pattern: fetch 20-30 candidates, rerank to top 4-8.
- Common mistake: reranking too few candidates gives little gain.

#### Multi-Vector Retriever (`MultiVectorRetriever`)
- What it does: Retrieves across mixed representations (text/table/image summaries).
- Use it when: Multimodal RAG indexing includes heterogeneous chunk types.

### 4.5 Prompting and LLM Components

#### Prompt / Prompt Template (`Prompt`, `Prompt Template`)
- What it does: Creates final instruction context for generator/evaluator LLMs.
- Good practice: enforce grounded policy and fallback behavior.
- Common mistake: weak prompts that allow outside knowledge despite RAG context.

#### OpenAI (`OpenAIModel`)
- What it does: Chat model node variant used in several flows.
- Typical use: generator, HyDE query writer, router-classifier LLM.

#### ChatOpenAI (`ChatOpenAI`)
- What it does: Chat model component used for generation/evaluation.
- Good setting: low temperature (`0` or `0.1`) for deterministic QA.

### 4.6 Routing, Branching, and Agent Components

#### Smart Router (`SmartRouter`)
- What it does: LLM-guided route selection across named categories.
- Use it when: Modular domain stores (API/UI/Performance) require query routing.
- Common mistake: route definitions too vague; causes misrouting.

#### Conditional Router / Retrieve or Direct / Quality Router (`ConditionalRouter`)
- What it does: Branches execution based on decision outputs.
- Use it when: Self-RAG and Corrective-RAG control loops.

#### Tool Calling Agent (`ToolCallingAgent`)
- What it does: Agent model that chooses and calls tools.
- Use it when: You need dynamic multi-tool retrieval/search.

#### Retriever Tool (`RetrieverTool`)
- What it does: Wraps retrievers as tools for agent consumption.
- Use it when: Agentic RAG over multiple knowledge sources.

#### Search API Tool (`SearchAPITool`)
- What it does: Web search tool exposed to agent.
- Use it when: Need external knowledge fallback.

### 4.7 Web and Graph Components

#### Tavily Web Search (`TavilySearchResults`)
- What it does: Web retrieval fallback for low-quality local retrieval.
- Use it in: Corrective RAG.

#### LLM Graph Transformer (`LLMGraphTransformer`)
- What it does: Extracts entities/relations into graph-friendly structure.
- Use it in: Graph RAG indexing pipeline.

#### Neo4j Graph Database (`Neo4jGraph`)
- What it does: Stores/query graph data.
- Use it in: Graph RAG with entity relationship queries.

#### Graph Cypher QA Chain (`GraphCypherQAChain`)
- What it does: Converts NL question to Cypher and answers from graph.
- Common caution: validate generated Cypher and graph schema alignment.

## 5) RAG Types Used and Their Component Stacks

## 5.1 Naive RAG

```text
Directory/File -> Type Convert -> Semantic Splitter -> Chroma
OpenAI Embeddings -> (Splitter + Chroma)
Chat Input -> Chroma Retrieve -> Type Convert -> Prompt -> OpenAI/ChatOpenAI -> Chat Output
```

Primary components:
- Directory/File Loader
- TypeConverterComponent
- SemanticTextSplitter
- OpenAIEmbeddings
- Chroma
- Prompt Template
- OpenAIModel/ChatOpenAI

Best use case:
- Baseline internal QA over a focused doc set.

## 5.2 Advanced RAG

```text
Ingestion: Directory -> Convert -> Semantic Splitter -> Chroma
Query: Chat Input -> (Optional HyDE LLM rewrite) -> Chroma (MMR/Similarity)
       -> Cohere Rerank -> Context Formatter -> Grounded Prompt -> Generator -> Output
```

Added components vs Naive:
- CohereRerank
- Extra LLM node for query rewriting (HyDE style)

Best use case:
- Better relevance and grounded answers with modest latency increase.

## 5.3 Modular RAG

```text
One ingestion path -> split -> three Chroma stores (API/UI/Performance)
Chat Input + Router LLM -> Smart Router -> selected store
retrieved context -> formatter -> final prompt -> generator
```

Key components:
- SmartRouter
- Multiple Chroma stores
- Router classifier LLM

Best use case:
- Multi-domain QA where each domain has separate corpus.

## 5.4 Graph RAG

```text
File Loader + Entity Extractor LLM -> LLM Graph Transformer -> Neo4j
Chat Input -> Graph Cypher QA Chain -> Output
```

Key components:
- LLMGraphTransformer
- Neo4jGraph
- GraphCypherQAChain

Best use case:
- Relationship-heavy questions and multi-hop entity reasoning.

## 5.5 Agentic RAG

```text
Chat Input + Agent LLM + Tool set (API docs, UI docs, bugs, web)
-> Tool Calling Agent -> Output
```

Key components:
- ToolCallingAgent
- RetrieverTool(s)
- SearchAPITool

Best use case:
- Open-ended tasks requiring dynamic tool selection.

## 5.6 Self-RAG

```text
Chat Input -> retrieval decision prompt -> decision LLM
-> router (retrieve or direct)
-> retriever path -> generate with context -> groundedness check -> evaluator -> output
```

Key components:
- Prompt + ChatOpenAI decision/evaluation pair
- ConditionalRouter
- Retriever

Best use case:
- Balancing cost/latency by retrieving only when needed.

## 5.7 Corrective RAG

```text
Chat Input -> retriever -> document grader -> grader LLM -> quality router
quality good -> final answer prompt
quality poor -> Tavily web search + final answer prompt
-> generator -> output
```

Key components:
- Document grading prompt + LLM
- Quality router
- TavilySearchResults fallback

Best use case:
- Robustness under weak retrieval quality.

## 5.8 Hybrid RAG

```text
File -> Split
Split -> BM25 retriever
Split + Embeddings -> Chroma -> Vector retriever
BM25 + Vector -> Ensemble (RRF) -> Prompt -> LLM -> Output
```

Key components:
- BM25Retriever
- Retriever (vector)
- EnsembleRetriever

Best use case:
- Queries mixing exact tokens and semantic intent.

## 5.9 Multi-Modal RAG

```text
PDF/Image Loader -> Unstructured Parser
Parser -> image prompt -> vision LLM summary
Parser -> table summarizer
Parser + image/table summaries + embeddings -> Multi-Vector Retriever
Chat Input + retrieved context -> final multimodal prompt -> generator -> output
```

Key components:
- Unstructured
- Vision-capable ChatOpenAI node
- Prompt summarizers
- MultiVectorRetriever

Best use case:
- Documents containing text + figures + tables.

## 5.10 Contextual RAG

```text
File -> Text Splitter
(full doc + chunk) -> context generation prompt -> context LLM
-> custom prepend component -> index into Chroma + BM25
Query -> Ensemble(BM25+Vector) -> Cohere Rerank -> Prompt -> Generator -> Output
```

Key components:
- Context generation prompt + LLM
- CustomComponent (prepend context)
- BM25 + vector hybrid + rerank

Best use case:
- Reducing retrieval misses for ambiguous chunks.

## 6) Component Selection Cheat Sheet

If your problem is mostly straightforward document QA:
- Start with Naive RAG components.

If retrieval precision is weak:
- Add semantic chunking + rerank (`SemanticTextSplitter` + `CohereRerank`).

If corpus is domain-diverse:
- Add routing (`SmartRouter`) and multiple stores.

If questions require relationship traversal:
- Use Graph RAG stack (`LLMGraphTransformer`, `Neo4jGraph`, `GraphCypherQAChain`).

If answerability varies by question:
- Use Self-RAG/Corrective-RAG decision loops.

If docs contain images/tables:
- Use Multi-Modal stack with parser + multi-vector retrieval.

If chunks lose context after splitting:
- Use Contextual RAG enrichment before embedding.

## 7) Practical Quality Checklist

Before marking a flow production-ready:

1. Ingestion integrity
- Non-zero collection count.
- Non-empty `documents` in vector store.
- Embedding dimensions consistent across records.

2. Retrieval quality
- Validate top-k and reranked top-n with test questions.
- Confirm routed questions hit expected domain store/tool.

3. Generation quality
- Prompt enforces grounded answers and fallback for missing context.
- Temperature tuned for deterministic QA.

4. Operational quality
- Clear collection naming convention.
- Separate staging/test/prod collections.
- Basic latency/cost tracking for rerank and agent/tool calls.

## 8) Common Issues and Fixes

Issue: `localhost:8000` shows 404.
- Meaning: Chroma root path has no UI endpoint; API still may be healthy.
- Check: `GET /api/v2/heartbeat`.

Issue: Collection exists but answers are weak.
- Check if documents are empty strings.
- Root cause is often incorrect `Type Convert` path during ingestion.

Issue: Node appears detached in UI.
- Validate both source and target handles match component input/output fields.
- Reconnect in UI if component version changed after update.

Issue: Retrieval too noisy.
- Increase candidate fetch size and apply rerank.
- Use MMR in Chroma for diversity.

Issue: Hallucinated answers.
- Strengthen prompt policy: context-only + explicit fallback message.

## 9) Suggested Learning Sequence

1. Naive RAG
2. Advanced RAG
3. Hybrid RAG
4. Modular RAG
5. Corrective RAG
6. Self-RAG
7. Agentic RAG
8. Graph RAG
9. Multi-Modal RAG
10. Contextual RAG

This order builds from simple retrieval to routing, control loops, tools, graph reasoning, and multimodal/contextual indexing.

---

If you add a new flow, update this README by recording:
- New component type(s)
- Why they were introduced
- Required settings
- Failure modes and validation tests
