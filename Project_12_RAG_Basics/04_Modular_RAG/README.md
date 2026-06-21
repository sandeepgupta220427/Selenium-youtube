# 4. Modular RAG

## Overview

Modular RAG treats the RAG pipeline as a set of interchangeable, plug-and-play components. Instead of a rigid pipeline, each module (retriever, generator, ranker, router) can be independently swapped, upgraded, or configured. Think of it like a testing framework where you can swap drivers (Selenium, Playwright, Cypress) without rewriting your tests.

---

## Architecture Components

| Module | Role | Examples | Swappable? |
|---|---|---|---|
| Router | Directs queries to right retriever | Semantic router, keyword router | ✅ Yes |
| Retriever | Fetches relevant docs | Vector, BM25, SQL, API | ✅ Yes |
| Reranker | Reorders by relevance | Cohere, BGE, Cross-encoder | ✅ Yes |
| Generator | Produces final answer | GPT-4, Claude, Llama | ✅ Yes |
| Memory | Maintains conversation context | Buffer, summary, vector | ✅ Yes |
| Guardrails | Validates input/output | NeMo, custom rules | ✅ Yes |

### Architecture Diagram

```
                    ┌──────────────────┐
                    │   Query Router   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ↓              ↓              ↓
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ API Docs   │  │ UI Docs    │  │ Perf Docs  │
     │ Retriever  │  │ Retriever  │  │ Retriever  │
     └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
           └──────────────┬──────────────────┘
                          ↓
                ┌─────────────────┐
                │   Re-ranker     │  ← Swappable (Cohere / BGE)
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │   Generator     │  ← Swappable (GPT-4 / Claude)
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │   Guardrails    │  ← Swappable (NeMo / Custom)
                └─────────────────┘
```

---

## Python Implementation

### Building a Modular RAG with Routing

```python
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough

# Define specialized retrievers for different domains
api_retriever = vectorstore_api.as_retriever(search_kwargs={"k": 4})
ui_retriever = vectorstore_ui.as_retriever(search_kwargs={"k": 4})
perf_retriever = vectorstore_perf.as_retriever(search_kwargs={"k": 4})

# Router: classifies query intent
router_prompt = ChatPromptTemplate.from_template(
    """Classify this QA query into one category:
    - api_testing
    - ui_testing
    - performance_testing
    Query: {question}
    Category:"""
)

router_chain = router_prompt | ChatOpenAI(temperature=0)

def route_query(info):
    route = info["route"].content.strip().lower()
    if "api" in route:
        return api_retriever.invoke(info["question"])
    elif "ui" in route:
        return ui_retriever.invoke(info["question"])
    else:
        return perf_retriever.invoke(info["question"])

# Modular chain
chain = (
    {"route": router_chain, "question": RunnablePassthrough()}
    | RunnableLambda(route_query)
)
```

### Swappable Generator Pattern

```python
class ModularRAG:
    def __init__(self, retriever, reranker=None, generator=None):
        self.retriever = retriever
        self.reranker = reranker
        self.generator = generator or ChatOpenAI(model="gpt-4o-mini")

    def query(self, question: str):
        # Step 1: Retrieve
        docs = self.retriever.invoke(question)

        # Step 2: Rerank (optional module)
        if self.reranker:
            docs = self.reranker.compress_documents(docs, question)

        # Step 3: Generate
        context = "\n".join([d.page_content for d in docs])
        prompt = f"Context: {context}\nQuestion: {question}\nAnswer:"
        return self.generator.invoke(prompt)

# Swap components easily
rag_v1 = ModularRAG(retriever=bm25_retriever, generator=gpt4)
rag_v2 = ModularRAG(retriever=vector_retriever, reranker=cohere, generator=claude)
```


---

## 🧪 QA Testing Points for Modular RAG

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Routing accuracy | Does the router classify edge-case queries correctly? |
| 2 | Fallback behavior | What happens when the router is uncertain? |
| 3 | A/B testing generators | Compare different generator models with the same retriever |
| 4 | Module hot-swapping | Verify swapping doesn't break the pipeline |
| 5 | Cross-domain queries | Test queries that span multiple domains |

---

**Next:** [Graph RAG →](../05_Graph_RAG/)
