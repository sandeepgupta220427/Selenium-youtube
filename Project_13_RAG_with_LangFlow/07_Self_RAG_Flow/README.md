# 7. Self-RAG — LangFlow Implementation

## Overview

Self-RAG adds a **reflection loop** to the RAG pipeline. The LLM evaluates its own output using reflection tokens and can decide to re-retrieve or revise its answer if the quality is insufficient.

---

## 🟣 LangFlow Implementation

### Flow Diagram

```
┌────────────┐    ┌──────────────────┐
│ Chat       │───→│ Should Retrieve? │
│ Input      │    │ (LLM Decision)   │
└────────────┘    └────────┬─────────┘
                           │
                  ┌────────┴─────────┐
              Yes ↓                  ↓ No
     ┌──────────────────┐   ┌──────────────────┐
     │ Vector Store     │   │ Direct LLM       │
     │ Retriever        │   │ Response          │
     └────────┬─────────┘   └────────┬─────────┘
              │                      │
     ┌────────┴─────────┐           │
     │ Generate with    │           │
     │ Context          │           │
     └────────┬─────────┘           │
              │                      │
     ┌────────┴─────────┐           │
     │ Groundedness     │           │
     │ Check (LLM)      │           │
     │ "Is the answer   │           │
     │  supported by    │           │
     │  the context?"   │           │
     └────────┬─────────┘           │
              │                      │
      ┌───────┴───────┐             │
   Yes↓            No ↓             │
┌──────────┐  ┌──────────┐         │
│ Return   │  │ Re-try   │         │
│ Answer   │  │ (loop    │         │
│          │  │  back)   │         │
└──────────┘  └──────────┘         │
       │                            │
       └────────────┬───────────────┘
                    ↓
           ┌─────────────────┐
           │   Chat Output   │
           └─────────────────┘
```

### Step-by-Step Setup

1. Create a new flow named **"Self-RAG with Reflection"**.
2. This requires using LangFlow's **"Custom Component"** or **"Flow as Tool"** feature, as Self-RAG is stateful.
3. **Step 1 – Retrieve Decision:** Add a **"Prompt"** node asking the LLM:
   *"Does this question require external knowledge retrieval? Respond YES or NO."*
4. **Step 2 – Retrieval:** If YES, route to the vector store retriever.
5. **Step 3 – Generate:** Connect retrieved context + query to a generation prompt.
6. **Step 4 – Groundedness Check:** Add a second **"Prompt"** node:
   *"Is this answer fully supported by the context? Respond SUPPORTED or NOT_SUPPORTED."*
7. **Step 5 – Loop or Return:** Use a **"Conditional Router"** to either return the answer or loop back for re-retrieval with a refined query.
8. Set `max_loops=3` to prevent infinite loops.
9. Connect the final output to **"Chat Output"**.

### 📥 Import the Flow

Import the pre-built flow: **[self_rag_langflow.json](./self_rag_langflow.json)**

---

## 🧪 QA Testing Points

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Loop termination | Verify `max_loops` prevents infinite cycles |
| 2 | Groundedness scoring | Does NOT_SUPPORTED trigger re-retrieval? |
| 3 | Direct answer path | Simple factual queries should skip retrieval |
| 4 | Token usage | Each loop iteration adds ~2x token cost |
| 5 | Answer improvement | Compare loop 1 vs. loop 3 answer quality |

---

**Next:** [Corrective RAG Flow →](../08_Corrective_RAG_Flow/)
