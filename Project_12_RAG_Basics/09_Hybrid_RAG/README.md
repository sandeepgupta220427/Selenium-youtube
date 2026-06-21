# 9. Hybrid RAG

## Overview

Hybrid RAG combines keyword-based search (BM25/TF-IDF) with semantic/vector search. Keyword search excels at exact matches (error codes, function names, test IDs), while vector search understands meaning and context. Together, they cover each other's blind spots.

---

## Why Hybrid Works Better

| Query Type | BM25 (Keyword) | Vector (Semantic) |
|---|---|---|
| "Error ERR_AUTH_403" | ✅ Excellent (exact match) | ❌ Poor (number confusion) |
| "login doesn't work" | ❌ Poor (no exact match) | ✅ Excellent (semantic understanding) |
| "TC-2451 test case" | ✅ Excellent (ID match) | ❌ Poor (ID is meaningless in vector space) |
| "flaky intermittent failures" | 🔶 Moderate | ✅ Excellent (understands concept) |

### Architecture Diagram

```
                    ┌──────────────────┐
                    │   User Query     │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              ↓                             ↓
     ┌─────────────────┐          ┌─────────────────┐
     │   BM25 Search   │          │  Vector Search   │
     │  (Keyword-based)│          │  (Semantic)      │
     │                 │          │                  │
     │  Weight: 0.4    │          │  Weight: 0.6     │
     └────────┬────────┘          └────────┬─────────┘
              │ Top K results              │ Top K results
              └──────────────┬─────────────┘
                             ↓
                ┌────────────────────────┐
                │  Reciprocal Rank       │
                │  Fusion (RRF)          │
                │  or Weighted Merge     │
                └────────────┬───────────┘
                             ↓
                ┌────────────────────────┐
                │  Deduplicated &        │
                │  Re-ranked Results     │
                └────────────┬───────────┘
                             ↓
                ┌────────────────────────┐
                │  LLM Generation        │
                └────────────────────────┘
```

---

## Python Implementation

### Ensemble Retriever with BM25 + Vector

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# BM25 keyword retriever
bm25_retriever = BM25Retriever.from_documents(
    documents=chunks,
    k=4
)

# Vector retriever
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# Combine with weights (0.5 each for balanced results)
hybrid_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.4, 0.6]  # Slightly favor semantic search
)

# Use like any retriever
results = hybrid_retriever.invoke("Error ERR_AUTH_403 during login test")
# BM25 finds exact error code matches
# Vector finds semantically related auth failure docs
# Results are merged and deduplicated
```

### Reciprocal Rank Fusion (RRF)

```python
def reciprocal_rank_fusion(results_list, k=60):
    """Merge multiple result lists using RRF scoring"""
    fused_scores = {}
    for results in results_list:
        for rank, doc in enumerate(results):
            doc_id = doc.page_content[:100]  # Use content hash in production
            if doc_id not in fused_scores:
                fused_scores[doc_id] = {"doc": doc, "score": 0}
            fused_scores[doc_id]["score"] += 1.0 / (rank + k)

    # Sort by fused score
    sorted_docs = sorted(fused_scores.values(), key=lambda x: x["score"], reverse=True)
    return [item["doc"] for item in sorted_docs]

# Get results from both retrievers
bm25_results = bm25_retriever.invoke(query)
vector_results = vector_retriever.invoke(query)

# Fuse results
hybrid_results = reciprocal_rank_fusion([bm25_results, vector_results])
```


---

## 🧪 QA Testing Points for Hybrid RAG

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Exact identifiers (test IDs, error codes) | BM25 should dominate |
| 2 | Natural language descriptions | Vector search should dominate |
| 3 | Weight tuning | Measure retrieval precision at each ratio |
| 4 | Deduplication | Both retrievers return same doc → should appear once with higher score |
| 5 | Mixed queries | "Explain ERR_AUTH_403 and how to fix it" — needs both |

---

**Next:** [Multi-Modal RAG →](../10_MultiModal_RAG/)
