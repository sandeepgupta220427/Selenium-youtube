# Project 5: RAG Test Case Pipeline (LangFlow)

## 🔴 Difficulty: Advanced

## Overview

A **full RAG (Retrieval-Augmented Generation) pipeline** built in LangFlow that ingests PDF test documents, chunks and embeds them into a vector database (AstraDB), and generates test cases by retrieving relevant context. This is the most complex project — a complete knowledge retrieval system for QA documentation.

---

## 🎯 What You'll Learn

- Building a **complete RAG pipeline** visually in LangFlow
- Using **AstraDB** as a cloud-hosted vector database
- Implementing the **R-A-G pattern**: Read → Augment → Generate
- Understanding key RAG steps: file loading, chunking, embedding, retrieval, generation
- Using **Groq LLM** for fast generation within LangFlow
- Data type conversion using **TypeConverterComponent**

---

## 📋 Flow Architecture

The flow is organized into **5 clear steps** (as labeled in the original LangFlow notes):

```
┌──────── Step 1: LOAD THE DATA ────────────────────────┐
│                                                        │
│  ┌──────────────┐                                     │
│  │  Read File   │  (PDF files with test documentation)│
│  │  Component   │                                     │
│  └──────┬───────┘                                     │
└─────────┼─────────────────────────────────────────────┘
          ↓
┌──────── Step 2: CHUNKING DATA (with Embedding) ───────┐
│                                                        │
│  ┌──────────────┐    ┌─────────────────────────┐      │
│  │ Split Text   │───→│ OpenAI Embeddings       │      │
│  │ (Chunker)    │    │ (text-embedding-3-small) │      │
│  └──────────────┘    └─────────────────────────┘      │
└────────────────────────────────────────────────────────┘
          ↓
┌──────── Step 3: PUSH TO VECTOR DB ────────────────────┐
│                                                        │
│  ┌──────────────────────────────────────────┐         │
│  │ AstraDB (Ingest)                          │         │
│  │ Collection: vector store for test docs    │         │
│  │ Receives: chunked + embedded documents    │         │
│  └──────────────────────────────────────────┘         │
└────────────────────────────────────────────────────────┘

┌──────── Step 4: RETRIEVE THE RESULTS ─────────────────┐
│                                                        │
│  ┌──────────┐    ┌───────────────┐    ┌────────────┐  │
│  │ Chat     │───→│ AstraDB       │───→│ Type       │  │
│  │ Input    │    │ (Search)      │    │ Converter  │  │
│  └──────────┘    └───────────────┘    └────────────┘  │
└────────────────────────────────────────────────────────┘
          ↓
┌──────── Step 5: GENERATION THE RESULTS ───────────────┐
│                                                        │
│  ┌────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │ Prompt     │───→│ Groq Model   │───→│ Chat       │ │
│  │ Template   │    │ (Generator)  │    │ Output     │ │
│  │ {context}  │    └──────────────┘    └────────────┘ │
│  │ {question} │                                       │
│  └────────────┘                                       │
└───────────────────────────────────────────────────────┘
```

---

## 🧩 Components Used

### Indexing Pipeline (Steps 1-3)

| Component | Type | Purpose |
|---|---|---|
| **Read File** | `File` | Loads PDF files (supports advanced Docling parser) |
| **Split Text** | `SplitText` | Chunks documents into manageable pieces |
| **OpenAI Embeddings** | `OpenAIEmbeddings` | Converts text chunks to vector embeddings |
| **AstraDB (Ingest)** | `AstraDB` | Stores embedded chunks in the vector database |

### Retrieval Pipeline (Steps 4-5)

| Component | Type | Purpose |
|---|---|---|
| **Chat Input** | `ChatInput` | User's question about test documentation |
| **AstraDB (Search)** | `AstraDB` | Searches vector store for relevant chunks |
| **Type Converter** | `TypeConverterComponent` | Converts DataFrame to Message for prompt |
| **Prompt Template** | `Prompt Template` | Combines `{context}` + `{question}` |
| **Groq Model** | `GroqModel` | Generates answer from retrieved context |
| **Chat Output** | `ChatOutput` | Displays the generated answer |

---

## 🔧 Setup Instructions

### Step 1: Install LangFlow
```bash
pip install langflow
langflow run
```

### Step 2: Set Up AstraDB
1. Go to [astra.datastax.com](https://astra.datastax.com/) and create a free database.
2. Create a **Serverless Vector** database.
3. Generate an **Application Token**.
4. Note your **API Endpoint** and **Token**.

### Step 3: Import the Flow
1. Open LangFlow at `http://localhost:7860`
2. Click **"Import"** and select the JSON file
3. Configure credentials:
   - **OpenAI API Key** (for embeddings)
   - **Groq API Key** (for generation LLM)
   - **AstraDB Token** and **API Endpoint**

### Step 4: Ingest Documents
1. Upload your QA PDF documents to the **Read File** component.
2. Run **Steps 1-3** (ingestion) to populate the vector store.

### Step 5: Query
1. Type a question in the Chat Input:
   ```
   Generate test cases for the login functionality
   ```
2. The pipeline retrieves relevant chunks from your uploaded docs and generates test cases.

---

## 📥 Import the Flow

Import the production LangFlow flow: **[LF_RAG_TestCase_PDF_CSV_TC (2).json](../LF_RAG_TestCase_PDF_CSV_TC%20(2).json)**

---

## 🧪 Testing Points

| # | Test | Expected |
|---|---|---|
| 1 | Upload a PDF and ingest | Chunks stored in AstraDB without errors |
| 2 | Query about a covered topic | Relevant test case content retrieved |
| 3 | Query about an uncovered topic | Agent acknowledges no relevant content found |
| 4 | Check chunk quality | Chunks should not split mid-sentence |
| 5 | Embedding accuracy | Related queries should retrieve same chunks |
| 6 | Response quality | Generated test cases reference the source document |
| 7 | Type Converter | DataFrame → Message conversion works properly |

---

## 🔑 Key Concepts

- **Two-phase RAG**: Steps 1-3 (indexing) run once per document set. Steps 4-5 (retrieval + generation) run per query.
- **AstraDB** is a cloud-hosted Cassandra-based vector database — no local installation needed.
- The **Type Converter** is essential because AstraDB returns data as a DataFrame, but the Prompt Template expects a Message.
- The LangFlow flow uses **colored notes** (R=Red, A=Rose, G=Green/Lime) to visually label the flow sections.
- **Groq** is used for generation (fast, cheap) while **OpenAI** handles embeddings (text-embedding-3-small).

---

## 🏗️ Architecture Breakdown

```
 ┌─────────────────────────────────────────────────────────────┐
 │                    LangFlow RAG Pipeline                    │
 │                                                             │
 │  INDEXING (run once):                                       │
 │    PDF → Read File → Split Text → OpenAI Embed → AstraDB   │
 │                                                             │
 │  RETRIEVAL (per query):                                     │
 │    User Query → AstraDB Search → Type Convert →             │
 │    Prompt Template → Groq LLM → Response                    │
 └─────────────────────────────────────────────────────────────┘
```

---

**← Back to [Project Overview](../README.md)**
