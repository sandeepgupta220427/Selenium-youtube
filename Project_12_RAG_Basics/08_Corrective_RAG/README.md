# 8. Corrective RAG (CRAG)

## Overview

Corrective RAG adds an evaluator after retrieval that scores the quality of retrieved documents. If the documents score below a confidence threshold, CRAG triggers a corrective action — typically a web search fallback or query reformulation. Think of it as a retry mechanism with fallback: if the primary data source fails, try an alternative.

---

## CRAG Decision Flow

```
┌──────────────────────────────────────────────────────────────┐
│                     CRAG DECISION FLOW                        │
│                                                               │
│  [User Query] → [Retrieve from Vector Store]                  │
│                          ↓                                    │
│               ┌──────────────────────┐                        │
│               │  GRADE Documents     │                        │
│               │  (LLM Relevance      │                        │
│               │   Scoring 0.0-1.0)   │                        │
│               └──────────┬───────────┘                        │
│                          │                                    │
│          ┌───────────────┼───────────────┐                    │
│          ↓               ↓               ↓                    │
│   ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│   │  CORRECT   │  │ AMBIGUOUS  │  │ INCORRECT  │             │
│   │ Score >0.7 │  │ Score 0.4  │  │ Score <0.4 │             │
│   │            │  │  to 0.7    │  │            │             │
│   └─────┬──────┘  └─────┬──────┘  └─────┬──────┘             │
│         ↓               ↓               ↓                    │
│   [Use retrieved]  [Supplement    [Discard docs,             │
│   [docs as-is  ]  [with web     [use ONLY web               │
│                 ]  [search      ][search results]            │
│         ↓               ↓               ↓                    │
│         └───────────────┼───────────────┘                    │
│                          ↓                                    │
│                   [LLM Generation]                            │
│                          ↓                                    │
│                   [Final Response]                            │
└──────────────────────────────────────────────────────────────┘
```

### Confidence Thresholds

| Score Range | Action | Description |
|---|---|---|
| > 0.7 | **CORRECT** | Use retrieved documents as-is |
| 0.4 – 0.7 | **AMBIGUOUS** | Supplement with web search results |
| < 0.4 | **INCORRECT** | Discard retrieved docs, use only web search |

---

## Python Implementation

```python
from langgraph.graph import StateGraph, END
from langchain_community.tools.tavily_search import TavilySearchResults

web_search = TavilySearchResults(max_results=3)

def grade_documents(state):
    """Grade each retrieved document for relevance"""
    question = state["question"]
    documents = state["documents"]
    scored_docs = []

    for doc in documents:
        grade_prompt = f"""Grade relevance of this document to the question.
        Question: {question}
        Document: {doc.page_content[:500]}
        Score (0.0 to 1.0):"""

        score = float(llm.invoke(grade_prompt).content.strip())
        scored_docs.append((doc, score))

    avg_score = sum(s for _, s in scored_docs) / len(scored_docs)

    if avg_score > 0.7:
        return {"action": "correct", "documents": [d for d, s in scored_docs if s > 0.5]}
    elif avg_score > 0.4:
        return {"action": "ambiguous", "documents": [d for d, s in scored_docs if s > 0.5]}
    else:
        return {"action": "incorrect", "documents": []}

def web_search_fallback(state):
    """Fallback to web search when retrieval fails"""
    results = web_search.invoke({"query": state["question"]})
    web_docs = [r["content"] for r in results]
    existing = state.get("documents", [])
    return {"documents": existing + web_docs}

def route_after_grading(state):
    if state["action"] == "correct":
        return "generate"
    elif state["action"] == "ambiguous":
        return "web_search"  # Supplement
    else:
        return "web_search"  # Replace entirely

# Build CRAG graph
workflow = StateGraph(CRAGState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade", grade_documents)
workflow.add_node("web_search", web_search_fallback)
workflow.add_node("generate", generate)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade")
workflow.add_conditional_edges("grade", route_after_grading)
workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", END)

crag_app = workflow.compile()
```


---

## 🧪 QA Testing Points for Corrective RAG

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Threshold boundaries | What happens at exactly 0.4 and 0.7? |
| 2 | Web search fallback | Test when web search also returns irrelevant results |
| 3 | Grading calibration | Does the grading LLM give consistent scores for the same input? |
| 4 | Latency impact | CRAG adds grading + potential web search overhead |
| 5 | Retry pattern | Frame as "retry with fallback" — QA engineers relate to retry logic |

> **💡 QA Connection:** CRAG is essentially the "retry with fallback" pattern that QA engineers use in test frameworks — if the primary assertion source fails, fall back to an alternative.

---

**Next:** [Hybrid RAG →](../09_Hybrid_RAG/)
