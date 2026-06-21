# 8. Corrective RAG (CRAG) — LangFlow & n8n Implementation

## Overview

Corrective RAG (CRAG) adds a **document quality evaluator** that scores each retrieved document as CORRECT, AMBIGUOUS, or INCORRECT. If documents are poor quality, it falls back to web search for better results.

---

## 🟣 LangFlow Implementation

### Flow Diagram

```
┌────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Chat       │───→│   Vector Store   │───→│ Document Grader  │
│ Input      │    │   Retriever      │    │ (LLM Evaluator) │
└────────────┘    │   k=4            │    │                 │
                  └──────────────────┘    │ Score each doc: │
                                          │ CORRECT /       │
                                          │ AMBIGUOUS /     │
                                          │ INCORRECT       │
                                          └────────┬────────┘
                                                   │
                              ┌────────────────────┼────────────────────┐
                              ↓                    ↓                    ↓
                     ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
                     │  CORRECT      │   │  AMBIGUOUS    │   │  INCORRECT    │
                     │  → Use docs   │   │  → Use docs   │   │  → Web search │
                     │  as-is        │   │  + Web search │   │  (Tavily API) │
                     └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
                             └────────────────────┼────────────────────┘
                                                  ↓
                                         ┌─────────────────┐
                                         │ Prompt Template  │
                                         │ (combine context)│
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

1. Create a new flow named **"Corrective RAG with Document Grading"**.
2. Add **Chat Input → Vector Store Retriever** (k=4).
3. Add a **"Prompt"** node for document grading:
   ```
   Score the relevance of this document to the question.
   Document: {document}
   Question: {question}
   Score as: CORRECT (clearly relevant), AMBIGUOUS (partially relevant), 
   or INCORRECT (not relevant). Respond with ONLY the score.
   ```
4. Connect a **ChatOpenAI** to evaluate each document.
5. Add a **Conditional Router**:
   - CORRECT → Use retrieved documents directly
   - AMBIGUOUS → Combine retrieved docs + web search results
   - INCORRECT → Use web search only (discard retrieved docs)
6. For web search, add a **"Tavily Search"** or **"HTTP Request"** tool node.
7. Merge all context into a final **Prompt Template → ChatOpenAI → Chat Output**.
8. Test with queries where your knowledge base has varying quality coverage.

### 📥 Import the Flow

Import the pre-built flow: **[corrective_rag_langflow.json](./corrective_rag_langflow.json)**

---

## 🔶 n8n Implementation

### n8n Flow Diagram

```
┌─────────────┐    ┌────────────────┐    ┌──────────────────┐
│ Webhook     │───→│ Vector Store   │───→│ OpenAI (Grade    │
│ Trigger     │    │ Retriever      │    │ Documents)       │
└─────────────┘    └────────────────┘    └────────┬─────────┘
                                                  │
                                         ┌────────┴─────────┐
                                         │ IF: score ==     │
                                         │ "INCORRECT"       │
                                         └────────┬─────────┘
                                                  │
                                    ┌─────────────┴─────────────┐
                                Yes ↓                           ↓ No
                         ┌──────────────┐              ┌──────────────┐
                         │ HTTP Request │              │ Use retrieved │
                         │ (Tavily Web  │              │ docs directly │
                         │  Search API) │              └──────┬───────┘
                         └──────┬───────┘                     │
                                └──────────────┬──────────────┘
                                               ↓
                                      ┌─────────────────┐
                                      │ OpenAI (final   │
                                      │ answer gen)     │
                                      └────────┬────────┘
                                               ↓
                                      ┌─────────────────┐
                                      │ Respond to      │
                                      │ Webhook          │
                                      └─────────────────┘
```

### 📥 Import the Flow

Import the pre-built n8n flow: **[corrective_rag_n8n_flow.json](./corrective_rag_n8n_flow.json)**

---

## 🧪 QA Testing Points

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Grade accuracy | Does the grader correctly identify irrelevant docs? |
| 2 | Web search fallback | Does it produce better results than poor local docs? |
| 3 | Confidence threshold tuning | Test different threshold levels |
| 4 | AMBIGUOUS handling | Does combining docs + web search improve quality? |
| 5 | Cost monitoring | Web search adds external API calls |

---

**Next:** [Hybrid RAG Flow →](../09_Hybrid_RAG_Flow/)
