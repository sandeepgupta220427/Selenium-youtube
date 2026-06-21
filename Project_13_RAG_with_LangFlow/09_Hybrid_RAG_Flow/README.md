# 9. Hybrid RAG — LangFlow Implementation

## Overview

Hybrid RAG combines **BM25 keyword search** with **vector semantic search** using an Ensemble Retriever and Reciprocal Rank Fusion (RRF). Keyword search excels at exact matches (error codes, test IDs), while vector search understands natural language meaning.

---

## 🟣 LangFlow Implementation

### Flow Diagram

```
┌────────────┐    ┌──────────────────┐
│   File     │───→│ Recursive Char   │
│   Loader   │    │ Text Splitter    │
└────────────┘    └────────┬─────────┘
                           │
              ┌────────────┴────────────┐
              ↓                         ↓
     ┌─────────────────┐      ┌─────────────────┐
     │   BM25          │      │  Chroma          │
     │   Retriever     │      │  Vector Store    │
     │   (keyword)     │      │  Retriever       │
     │   weight=0.4    │      │  (semantic)      │
     │   k=4           │      │  weight=0.6      │
     └────────┬────────┘      │  k=4             │
              │               └────────┬─────────┘
              └────────────┬───────────┘
                           ↓
                  ┌─────────────────┐
                  │ Ensemble        │
                  │ Retriever       │
                  │ (RRF merge)     │
                  └────────┬────────┘
                           ↓
┌────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Chat       │───→│   Prompt        │───→│   ChatOpenAI    │
│ Input      │    │   Template      │    │   (gpt-4o-mini) │
└────────────┘    └─────────────────┘    └────────┬────────┘
                                                  ↓
                                         ┌─────────────────┐
                                         │   Chat Output   │
                                         └─────────────────┘
```

### Step-by-Step Setup

1. Create a new flow named **"Hybrid RAG Pipeline"**.
2. Add **File Loader → Recursive Character Text Splitter** (chunk_size=1000).
3. Connect splitter output to both:
   - **BM25Retriever** (keyword-based, weight=0.4)
   - **Chroma Vector Store + Retriever** (semantic, weight=0.6)
4. Add an **"Ensemble Retriever"** component.
5. Connect both retrievers into the Ensemble Retriever.
6. Set weights: `[0.4, 0.6]` (slightly favor semantic search).
7. Add **Chat Input → Prompt Template → ChatOpenAI → Chat Output**.
8. Connect Ensemble Retriever output to the Prompt Template's context input.
9. Test with different query types:
   - Error codes: `"Error ERR_AUTH_403"` → BM25 should dominate
   - Natural language: `"login doesn't work"` → Vector should dominate

### 📥 Import the Flow

Import the pre-built flow: **[hybrid_rag_langflow.json](./hybrid_rag_langflow.json)**

---

## 🧪 QA Testing Points

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Exact identifiers (test IDs, error codes) | BM25 should rank these highest |
| 2 | Natural language descriptions | Vector search should rank these highest |
| 3 | Weight tuning | Measure precision at BM25=0.3/0.5/0.7 |
| 4 | Deduplication | Same doc from both retrievers → single entry with higher score |
| 5 | Mixed queries | "Explain ERR_AUTH_403" — needs both exact + semantic |

---

**Next:** [Multi-Modal RAG Flow →](../10_MultiModal_RAG_Flow/)
