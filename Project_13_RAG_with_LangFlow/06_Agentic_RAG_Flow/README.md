# 6. Agentic RAG — LangFlow & n8n Implementation

## Overview

Agentic RAG uses an AI agent that can **reason, plan, and decide dynamically** which tools and retrievers to use. The agent can search multiple sources, refine queries, and iterate until it has enough information.

---

## 🟣 LangFlow Implementation

### Flow Diagram

```
┌────────────┐    ┌──────────────────────────────────────────┐
│ Chat       │───→│        Tool Calling Agent                 │
│ Input      │    │                                           │
└────────────┘    │  ┌─────────────┐  ┌─────────────┐       │
                  │  │ API Test    │  │ UI Test     │       │
                  │  │ Docs Tool   │  │ Docs Tool   │       │
                  │  └─────────────┘  └─────────────┘       │
                  │                                           │
                  │  ┌─────────────┐  ┌─────────────┐       │
                  │  │ Bug Report  │  │ Web Search  │       │
                  │  │ Search Tool │  │ Tool        │       │
                  │  └─────────────┘  └─────────────┘       │
                  │                                           │
                  │  max_iterations = 5                       │
                  └──────────────────────────┬───────────────┘
                                             │
                                    ┌────────┴────────┐
                                    │ ChatOpenAI       │
                                    │ (GPT-4o)         │
                                    └────────┬────────┘
                                             ↓
                                    ┌─────────────────┐
                                    │ Chat Output      │
                                    └─────────────────┘
```

### Step-by-Step Setup

1. Create a new flow named **"Agentic RAG with Tool Selection"**.
2. Add a **"Chat Input"** node for user queries.
3. Create multiple **"Retriever Tool"** components, each connected to a different vector store:
   - API docs retriever
   - UI docs retriever
   - Bug reports retriever
4. Add a **"Tool Calling Agent"** component (or "ReAct Agent" if available).
5. Connect all retriever tools to the agent's tool input.
6. Connect **ChatOpenAI (GPT-4o recommended)** to the agent as the reasoning LLM.
7. Set `max_iterations=5` on the agent to prevent infinite loops.
8. Connect agent output to **"Chat Output"**.
9. Test with complex queries that require multiple retrievers:
   *"Find related bugs for the auth API and suggest new test cases."*
10. Monitor the agent's reasoning trace to verify it selects appropriate tools.

### 📥 Import the Flow

Import the pre-built flow: **[agentic_rag_langflow.json](./agentic_rag_langflow.json)**

---

## 🔶 n8n Implementation

### n8n Flow Diagram

```
┌─────────────┐    ┌──────────────────────────────────────┐
│ Chat        │───→│        AI Agent                       │
│ Trigger     │    │                                       │
└─────────────┘    │  Tools:                               │
                   │  ├── Vector Store (API docs)          │
                   │  ├── Vector Store (UI docs)           │
                   │  ├── Vector Store (Bug reports)       │
                   │  └── HTTP Request (Web search)        │
                   │                                       │
                   │  LLM: GPT-4o (reasoning)              │
                   │  Memory: Window Buffer (last 5 msgs)  │
                   └───────────────────┬───────────────────┘
                                       ↓
                              ┌─────────────────┐
                              │ Chat Response    │
                              └─────────────────┘
```

### 📥 Import the Flow

Import the pre-built n8n flow: **[agentic_rag_n8n_flow.json](./agentic_rag_n8n_flow.json)**

---

## 🧪 QA Testing Points

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | `max_iterations` limit | Does the agent terminate gracefully? |
| 2 | Tool selection accuracy | Does the agent pick the right retriever? |
| 3 | Token consumption | Agents use 3–10x more tokens than basic RAG |
| 4 | Error handling | What happens when a tool fails mid-execution? |
| 5 | Hallucinated tool calls | Verify the agent doesn't call non-existent tools |

---

**Next:** [Self-RAG Flow →](../07_Self_RAG_Flow/)
