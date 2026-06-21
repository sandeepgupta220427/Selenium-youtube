# 2. Naive RAG — LangFlow & n8n Implementation

## Overview

This is the simplest RAG pipeline: Load documents → Chunk → Embed → Store → Retrieve → Generate. No optimization layers.

---

## 🟣 LangFlow Implementation

### Flow Diagram

```
┌────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   File     │───→│ Recursive Char   │───→│   Chroma        │
│   Loader   │    │ Text Splitter    │    │   Vector Store  │
└────────────┘    │ chunk_size=1000  │    │                 │
                  │ chunk_overlap=200│    └────────┬────────┘
                  └──────────────────┘             │
                                          ┌────────┴────────┐
┌────────────┐    ┌──────────────────┐    │   Retriever     │
│ OpenAI     │───→│   (embeddings    │───→│   k=4           │
│ Embeddings │    │    connection)   │    └────────┬────────┘
└────────────┘    └──────────────────┘             │
                                                   ↓
┌────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Chat       │───→│   Prompt         │───→│   ChatOpenAI    │
│ Input      │    │   Template       │    │   (gpt-4o-mini) │
└────────────┘    └──────────────────┘    └────────┬────────┘
                                                   ↓
                                          ┌─────────────────┐
                                          │   Chat Output   │
                                          └─────────────────┘
```

### Step-by-Step Setup

1. Open LangFlow and create a new flow. Name it **"Naive RAG Pipeline"**.
2. Add a **"File"** component (or "PDF Loader") and upload your test documents.
3. Connect it to a **"Recursive Character Text Splitter"** node. Set `chunk_size=1000`, `chunk_overlap=200`.
4. Add an **"OpenAI Embeddings"** node and connect it to a **"Chroma"** vector store node.
5. Connect the text splitter output to the Chroma node's document input.
6. Add a **"Chat Input"** component for user queries.
7. Add a **"Retriever"** node connected to the Chroma vector store. Set `k=4`.
8. Add a **"Prompt"** template node with the template:
   ```
   Answer based on context: {context}
   Question: {question}
   ```
9. Connect a **"ChatOpenAI"** node to the prompt template and then to a **"Chat Output"** node.
10. Click **"Run"** and test with a sample query about your test documentation.

### 📥 Import the Flow

Import the pre-built flow: **[naive_rag_langflow.json](./naive_rag_langflow.json)**

---

## 🔶 n8n Implementation

### n8n Flow Diagram

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Webhook     │───→│ AI Agent Node    │───→│ Respond to      │
│ (trigger)   │    │ (Chat Model)     │    │ Webhook         │
└─────────────┘    └────────┬─────────┘    └─────────────────┘
                            │
                   ┌────────┴─────────┐
                   │ Vector Store     │
                   │ Retriever Tool   │
                   │ (Pinecone/Chroma)│
                   └──────────────────┘
```

### n8n Setup Steps

1. Create a new workflow in n8n
2. Add a **Webhook** trigger node (or **Chat Trigger** for chat UI)
3. Add an **AI Agent** node with **OpenAI Chat Model**
4. Attach a **Vector Store Tool** (Pinecone, Supabase, or Qdrant)
5. Configure the vector store with your document embeddings
6. Add a **Respond to Webhook** node for the output
7. Test via the n8n chat interface or webhook URL

### 📥 Import the Flow

Import the pre-built n8n flow: **[naive_rag_n8n_flow.json](./naive_rag_n8n_flow.json)**

---

## 🧪 QA Testing Points

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Query with no relevant docs in the store | Check for hallucination |
| 2 | Query spanning multiple chunks | Verify context continuity |
| 3 | Duplicate documents | Check for redundant retrieval |
| 4 | Very long documents | Verify chunking doesn't split critical info |
| 5 | Embedding model changes | Ensure re-indexing happens correctly |

---

**Next:** [Advanced RAG Flow →](../03_Advanced_RAG_Flow/)
