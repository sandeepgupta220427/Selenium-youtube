# Project 13: RAG with LangFlow

## Visual RAG Pipeline Implementations

### For QA Engineers & AI Testing Professionals

**The Testing Academy | Author: Dev (Principal SDET & AI Testing Educator)**
**2026 Edition**

---

## 📚 What's Inside

This project provides **visual, no-code/low-code implementations** of the RAG patterns in this course using **LangFlow**. Each chapter includes step-by-step instructions, importable JSON flow files, and configuration guides.

LangFlow fundamentals and starter agents now live in **[Project 11: LangFlow Fundamentals](../Project_11_LangFlow/)**.

## 📂 Table of Contents

| # | Topic | Tools |
|---|---|---|
| 1 | [Naive RAG Flow](./02_Naive_RAG_Flow/) | LangFlow + n8n |
| 2 | [Advanced RAG Flow](./03_Advanced_RAG_Flow/) | LangFlow + n8n |
| 3 | [Modular RAG Flow](./04_Modular_RAG_Flow/) | LangFlow |
| 4 | [Graph RAG Flow](./05_Graph_RAG_Flow/) | LangFlow |
| 5 | [Agentic RAG Flow](./06_Agentic_RAG_Flow/) | LangFlow + n8n |
| 6 | [Self-RAG Flow](./07_Self_RAG_Flow/) | LangFlow |
| 7 | [Corrective RAG Flow](./08_Corrective_RAG_Flow/) | LangFlow + n8n |
| 8 | [Hybrid RAG Flow](./09_Hybrid_RAG_Flow/) | LangFlow |
| 9 | [Multi-Modal RAG Flow](./10_MultiModal_RAG_Flow/) | LangFlow |
| 10 | [Contextual RAG Flow](./11_Contextual_RAG_Flow/) | LangFlow |
| 11 | [Learning Path & Next Steps](./12_Learning_Path.md) | — |

## 🛠️ Prerequisites

- **LangFlow:** `pip install langflow` then `langflow run` (access at `http://localhost:7860`)
- **n8n:** `npx n8n` or Docker: `docker run -p 5678:5678 n8nio/n8n`
- API keys: OpenAI, Cohere (for re-ranking), Tavily (for web search)

## 📥 How to Import Flows

### LangFlow Flows
1. Open LangFlow at `http://localhost:7860`
2. Click **"Import"** or **"New Flow → Import"**
3. Select the `*.json` file from the chapter folder
4. Configure your API keys in the component settings
5. Click **"Run"** to test

### n8n Flows
1. Open n8n at `http://localhost:5678`
2. Go to **Settings → Import from File**
3. Select the `*_n8n_flow.json` file
4. Configure credentials (OpenAI, Pinecone, etc.)
5. Click **"Execute Workflow"** to test

## 🔗 Related Project

For theory and Python code examples, see **[Project 12: RAG Basics](../Project_12_RAG_Basics/)**.

---

**The Testing Academy — Building the Next Generation of AI-Powered QA Engineers**
