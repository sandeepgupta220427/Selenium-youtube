# 7. Self-RAG (Self-Reflective RAG)

## Overview

Self-RAG introduces a reflection loop into the RAG pipeline. The model generates special reflection tokens that help it decide: (1) whether retrieval is needed, (2) whether the retrieved documents are relevant, and (3) whether the generated response is grounded in the retrieved documents. Think of it as building test assertions directly into your AI pipeline.

---

## The Reflection Token Framework

| Token | Question It Answers | Values |
|---|---|---|
| **Retrieve** | Do I need to look up information? | Yes / No / Continue |
| **ISREL** | Is this retrieved doc relevant? | Relevant / Irrelevant |
| **ISSUP** | Is my response supported by the docs? | Fully / Partially / No Support |
| **ISUSE** | Is the response useful to the user? | 5 (best) to 1 (worst) |

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                   SELF-RAG DECISION FLOW                      │
│                                                               │
│  [User Query]                                                 │
│       ↓                                                       │
│  ┌─────────────────┐                                          │
│  │ DECIDE: Need     │──→ NO ──→ [Generate Directly]           │
│  │ Retrieval?       │                                          │
│  └────────┬─────────┘                                          │
│           │ YES                                                │
│           ↓                                                    │
│  ┌─────────────────┐                                          │
│  │ RETRIEVE Docs    │                                          │
│  └────────┬─────────┘                                          │
│           ↓                                                    │
│  ┌─────────────────┐                                          │
│  │ CHECK: Docs      │──→ IRRELEVANT ──→ [Re-retrieve / Rewrite]│
│  │ Relevant? (ISREL)│                         ↑                │
│  └────────┬─────────┘                         │                │
│           │ RELEVANT                          │                │
│           ↓                                    │                │
│  ┌─────────────────┐                          │                │
│  │ GENERATE Answer  │                          │                │
│  └────────┬─────────┘                          │                │
│           ↓                                    │                │
│  ┌─────────────────┐                          │                │
│  │ CHECK: Grounded? │──→ NOT GROUNDED ─────────┘                │
│  │ (ISSUP)          │                                          │
│  └────────┬─────────┘                                          │
│           │ GROUNDED                                           │
│           ↓                                                    │
│  ┌─────────────────┐                                          │
│  │ ✅ FINAL OUTPUT  │                                          │
│  └──────────────────┘                                          │
└──────────────────────────────────────────────────────────────┘
```

---

## Python Implementation with LangGraph

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

class RAGState(TypedDict):
    question: str
    documents: List[str]
    generation: str
    needs_retrieval: bool
    is_relevant: bool
    is_grounded: bool

def decide_retrieval(state):
    """Decide if retrieval is needed"""
    prompt = f'Does this question need external info? "{state["question"]}"'
    response = llm.invoke(prompt)
    return {"needs_retrieval": "yes" in response.content.lower()}

def retrieve(state):
    """Retrieve relevant documents"""
    docs = retriever.invoke(state["question"])
    return {"documents": [d.page_content for d in docs]}

def check_relevance(state):
    """Check if retrieved docs are relevant"""
    prompt = f'Are these docs relevant to "{state["question"]}"?\n'
    prompt += "\n".join(state["documents"][:2])
    response = llm.invoke(prompt)
    return {"is_relevant": "yes" in response.content.lower()}

def generate(state):
    """Generate response from context"""
    context = "\n".join(state["documents"])
    prompt = f"Context: {context}\nQuestion: {state['question']}\nAnswer:"
    response = llm.invoke(prompt)
    return {"generation": response.content}

def check_groundedness(state):
    """Check if response is grounded in documents"""
    prompt = f"Is this answer grounded in the context?\n"
    prompt += f'Answer: {state["generation"]}\nContext: {state["documents"][0]}'
    response = llm.invoke(prompt)
    return {"is_grounded": "yes" in response.content.lower()}

# Build the graph
workflow = StateGraph(RAGState)
workflow.add_node("decide", decide_retrieval)
workflow.add_node("retrieve", retrieve)
workflow.add_node("check_relevance", check_relevance)
workflow.add_node("generate", generate)
workflow.add_node("check_grounded", check_groundedness)

workflow.set_entry_point("decide")
workflow.add_conditional_edges(
    "decide", lambda s: "retrieve" if s["needs_retrieval"] else "generate"
)
workflow.add_edge("retrieve", "check_relevance")
workflow.add_conditional_edges(
    "check_relevance", lambda s: "generate" if s["is_relevant"] else "retrieve"
)
workflow.add_edge("generate", "check_grounded")
workflow.add_conditional_edges(
    "check_grounded", lambda s: END if s["is_grounded"] else "retrieve"
)

app = workflow.compile()
```


---

## 🧪 QA Testing Points for Self-RAG

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Retrieval decision | Does it correctly skip retrieval for common knowledge? |
| 2 | Infinite loop protection | Force irrelevant docs and verify `max_retries` is respected |
| 3 | Groundedness checking | Test with responses that subtly hallucinate facts |
| 4 | Latency overhead | Reflection adds 2–4x latency vs. naive RAG |
| 5 | Self-healing assertions | The system tests its own output — frame as "built-in QA" |

> **💡 QA Connection:** Self-RAG is essentially "self-healing test assertions" — the system tests its own output quality before returning results.

---

**Next:** [Corrective RAG (CRAG) →](../08_Corrective_RAG/)
