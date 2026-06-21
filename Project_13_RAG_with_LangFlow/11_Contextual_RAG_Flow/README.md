# 11. Contextual RAG — LangFlow Implementation

## Overview

Contextual RAG (Anthropic's approach) solves the chunking context-loss problem. Before embedding chunks, an LLM prepends a context sentence explaining **where the chunk came from** and **what it's about**. This dramatically improves retrieval accuracy — Anthropic reported a **67% reduction in retrieval failures**.

---

## 🟣 LangFlow Implementation

### Flow Diagram

```
┌──────── INDEXING (Contextual Enrichment) ─────────────────┐
│                                                            │
│  ┌───────────┐    ┌──────────────┐                        │
│  │ File      │───→│ Text Splitter │                        │
│  │ Loader    │    └──────┬───────┘                        │
│  └───────────┘           │                                 │
│                          ↓                                 │
│                  ┌──────────────────┐                      │
│                  │ FOR EACH CHUNK:  │                      │
│                  │                  │                      │
│                  │ Context Prompt:  │                      │
│                  │ "Given the full  │                      │
│                  │  document, what  │                      │
│                  │  is this chunk   │                      │
│                  │  about?"         │                      │
│                  │                  │                      │
│                  │ → Prepend        │                      │
│                  │   context to     │                      │
│                  │   chunk          │                      │
│                  └──────┬───────────┘                      │
│                         ↓                                  │
│               ┌──────────────────┐                        │
│               │ Chroma +         │                        │
│               │ OpenAI Embeddings│                        │
│               │ (enriched chunks)│                        │
│               └──────────────────┘                        │
└────────────────────────────────────────────────────────────┘

┌──────── RETRIEVAL ────────────────────────────────────────┐
│                                                            │
│  ┌──────────┐    ┌─────────────┐    ┌──────────────────┐  │
│  │ Chat     │───→│ Ensemble    │───→│ Cohere Rerank    │  │
│  │ Input    │    │ Retriever   │    │ (top_n=5)        │  │
│  └──────────┘    │ BM25+Vector │    └──────┬───────────┘  │
│                  └─────────────┘           ↓              │
│                                   ┌──────────────────┐    │
│                                   │ ChatOpenAI       │    │
│                                   │ → Chat Output    │    │
│                                   └──────────────────┘    │
└────────────────────────────────────────────────────────────┘
```

### Step-by-Step Setup

1. Create a new flow named **"Contextual RAG Pipeline"**.
2. **Indexing Phase** (this is the key differentiator):
   - Add **File Loader → Recursive Character Text Splitter**.
   - Add a **"Custom Component"** or **"Python Function"** node that:
     - Takes the full document text and each chunk
     - Uses an LLM to generate 2-3 sentences of context
     - Prepends the context to each chunk
   - Connect to **OpenAI Embeddings → Chroma** (store enriched chunks).
3. **Retrieval Phase** (Anthropic recommends the full combination):
   - Create **BM25 Retriever** with enriched chunks.
   - Create **Vector Retriever** with enriched chunks.
   - Add **Ensemble Retriever** (weights: BM25=0.4, Vector=0.6).
   - Add **Cohere Rerank** (top_n=5) to rerank the combined results.
4. Connect to **Chat Input → Prompt → ChatOpenAI → Chat Output**.
5. Test by comparing retrieval quality:
   - Store the same chunks WITH and WITHOUT context enrichment
   - Run the same test queries against both and compare precision

### Context Generation Prompt

Use this prompt in the context generation step:
```
Here is the full document:
<document>
{document}
</document>

Here is a chunk from that document:
<chunk>
{chunk}
</chunk>

Please provide a short context (2-3 sentences) that explains:
1. What document/section this chunk belongs to
2. What the chunk is specifically about
3. Key entities or identifiers mentioned

Context:
```

### 📥 Import the Flow

Import the pre-built flow: **[contextual_rag_langflow.json](./contextual_rag_langflow.json)**

---

## 🧪 QA Testing Points

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Retrieval accuracy: with vs. without context | Measure precision improvement |
| 2 | Context quality | Is the generated context accurate and helpful? |
| 3 | Indexing cost | Each chunk requires 1 LLM call (track API cost) |
| 4 | Disambiguation | Similar sections in different docs should be distinguishable |
| 5 | Context hallucination | Verify the LLM doesn't invent metadata |

> **📊 Anthropic Benchmark:** Contextual RAG + Hybrid Search + Reranking → **67% fewer retrieval failures** vs. standard RAG.

---

**Next:** [Learning Path & Next Steps →](../12_Learning_Path.md)
