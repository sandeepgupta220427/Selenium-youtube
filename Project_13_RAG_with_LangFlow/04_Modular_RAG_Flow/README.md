# 4. Modular RAG — LangFlow Implementation

## Overview

Modular RAG treats the RAG pipeline as a set of interchangeable, plug-and-play components with a **query router** that directs queries to the appropriate domain-specific retriever.

---

## 🟣 LangFlow Implementation: Modular RAG with Smart Router

### Flow Diagram

```
                         ┌──────────────────┐
                         │   Chat Input     │
                         └────────┬─────────┘
                                  │
                         ┌────────┴─────────┐
                         │ ChatOpenAI        │
                         │ (router LLM)      │
                         └────────┬─────────┘
                                  │
                         ┌────────┴─────────┐
                         │ Smart Router      │
                         │ api / ui / perf   │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ↓                   ↓                   ↓
     ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
     │ API Docs         │ │ UI Docs          │ │ Perf Docs        │
     │ Vector Store     │ │ Vector Store     │ │ Vector Store     │
     │ + Retriever      │ │ + Retriever      │ │ + Retriever      │
     └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
              └───────────────────┼───────────────────┘
                                  ↓
                         ┌─────────────────┐
                         │ Context Merge    │
                         │ Formatter        │
                         └────────┬────────┘
                                  ↓
                         ┌─────────────────┐
                         │ Prompt Template  │
                         │ (final answer)   │
                         └────────┬────────┘
                                  ↓
                         ┌─────────────────┐
                         │ ChatOpenAI       │
                         │ (generator)      │
                         └────────┬────────┘
                                  ↓
                         ┌─────────────────┐
                         │ Chat Output      │
                         └─────────────────┘
```

### Step-by-Step Setup

1. Create a new flow named **"Modular RAG with Query Router"**.
2. Add a **"Directory"** node to load your source QA knowledge base.
3. Convert the loaded files into `Data`, then split and index them into **three separate Chroma collections**:
   - `modular_api_docs`
   - `modular_ui_docs`
   - `modular_performance_docs`
4. Add a **"Chat Input"** node for the user question.
5. Add an **"OpenAI"** model node that acts as the router LLM.
6. Add a **"Smart Router"** node with exactly three routes:
   - `api_testing`
   - `ui_testing`
   - `performance_testing`
7. Connect the router outputs to the correct Chroma retriever branch.
8. Add a **"Context Merge Formatter"** custom component to merge the active branch retrieval results into one clean context message.
9. Feed that merged context into the final **"Prompt Template"** and then into the generator **OpenAI** node.
10. Connect the generator to **"Chat Output"**.

### What This Flow Actually Does

- Uses **LLM routing** to classify the question into API, UI, or performance testing.
- Sends the question to the matching retriever branch.
- Merges the returned chunks with a **custom context formatter** so the prompt gets the active branch context instead of an arbitrary first result.
- Uses one shared final prompt and one shared answer model.

### 📥 Import the Flow

Import the pre-built flow: **[modular_rag_langflow.json](./modular_rag_langflow.json)**

---

## 🧪 QA Testing Points

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Routing accuracy | Does the router classify edge-case queries correctly? |
| 2 | Fallback behavior | What happens when the router is uncertain? |
| 3 | A/B testing generators | Compare different generator models with the same retriever |
| 4 | Module hot-swapping | Verify swapping doesn't break the pipeline |
| 5 | Cross-domain queries | Test queries that span multiple domains |

---

**Next:** [Graph RAG Flow →](../05_Graph_RAG_Flow/)
