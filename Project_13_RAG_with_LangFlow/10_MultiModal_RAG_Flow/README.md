# 10. Multi-Modal RAG — LangFlow Implementation

## Overview

Multi-Modal RAG extends retrieval beyond text to include **images, tables, charts, and diagrams**. It uses Vision LLMs (GPT-4o) to summarize images into text, then indexes those summaries while storing the original media for retrieval.

---

## 🟣 LangFlow Implementation

### Flow Diagram

```
┌──────── INDEXING PIPELINE ────────────────────────────────┐
│                                                            │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ PDF/File  │→ │ Unstructured │→ │ Split into:      │   │
│  │ Loader    │  │ Parser       │  │ • Text chunks    │   │
│  └───────────┘  └──────────────┘  │ • Tables         │   │
│                                    │ • Images         │   │
│                                    └────────┬─────────┘   │
│                                             │              │
│                        ┌────────────────────┼──────┐      │
│                        ↓                    ↓      ↓      │
│                  [Text chunks]        [Tables] [Images]   │
│                        │                 │        │       │
│                        │            [LLM     [Vision      │
│                        │             Summary]  LLM        │
│                        │                │     Summary]    │
│                        └────────────────┼────────┘       │
│                                         ↓                 │
│                              [Unified Vector Store]       │
│                                                            │
│        [Original Media] → [Byte Store]                    │
└────────────────────────────────────────────────────────────┘

┌──────── RETRIEVAL PIPELINE ───────────────────────────────┐
│                                                            │
│  ┌──────────┐    ┌─────────────────┐    ┌──────────────┐  │
│  │ Chat     │───→│ Multi-Vector    │───→│ GPT-4o       │  │
│  │ Input    │    │ Retriever       │    │ (Generates   │  │
│  └──────────┘    │ (finds summary, │    │  answer with │  │
│                  │  returns orig.) │    │  media refs) │  │
│                  └─────────────────┘    └──────┬───────┘  │
│                                                ↓           │
│                                       ┌──────────────┐    │
│                                       │ Chat Output  │    │
│                                       └──────────────┘    │
└────────────────────────────────────────────────────────────┘
```

### Step-by-Step Setup

1. Create a new flow named **"Multi-Modal RAG"**.
2. For the **indexing path**:
   - Add an **"Unstructured"** or **"PDF Loader"** component for complex documents.
   - Configure it with `strategy="hi_res"` for layout detection.
   - It will automatically extract text, tables, and images.
3. For **image processing**:
   - Add a **ChatOpenAI (GPT-4o)** node configured for vision.
   - Create a prompt that describes images for a QA engineer.
4. For **table processing**:
   - Add a **ChatOpenAI** node to summarize table contents.
5. Connect all summaries + text chunks to a **"Chroma"** vector store with **"Multi-Vector Retriever"**.
6. Store originals (images, table HTML) in the byte store.
7. For the **retrieval path**:
   - Add **Chat Input → Multi-Vector Retriever → Prompt → GPT-4o → Chat Output**.
   - The retriever returns original content (including images) when summaries match.
8. Test with queries about content in images/tables vs. text.

### 📥 Import the Flow

Import the pre-built flow: **[multimodal_rag_langflow.json](./multimodal_rag_langflow.json)**

---

## 🧪 QA Testing Points

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Image summarization accuracy | Does GPT-4o correctly describe error screenshots? |
| 2 | Table data preservation | Are numbers and columns correct in summaries? |
| 3 | Mixed-content queries | Queries needing both text and image context |
| 4 | Original content return | Images actually embedded in response, not just text |
| 5 | Low-quality input handling | Blurry screenshots, scanned documents |

---

**Next:** [Contextual RAG Flow →](../11_Contextual_RAG_Flow/)
