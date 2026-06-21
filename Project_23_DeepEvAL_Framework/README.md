# Project 23 — DeepEval Framework

A complete, locally-runnable lab for evaluating LLM-powered e-commerce features. **Three independent subsystems plus a live web dashboard**, each in its own folder:

| Folder | What | Stack | Port |
|--------|------|-------|------|
| `01_chatbot/` | **ShopSphere e-commerce chatbot** (the app under test) | React (Vite) + FastAPI + Groq | 5173 / 8201 |
| `02_rag_explorer/` | **RAG Explorer** — full pipeline with auditable stages | FastAPI + ChromaDB + Ollama Nomic Embed + Groq | 8202 |
| `03_deepeval_framework/` | **DeepEval framework + Live Dashboard** — 22 metrics, swappable judge LLMs | DeepEval + pytest + FastAPI dashboard + OpenAI/Groq/Ollama | 8203 (UI) |

## Screenshots

### DeepEval Dashboard (Subsystem C)

Live metric runs with target/judge dropdowns and per-card pass/fail indicators.

![DeepEval Dashboard](screenshots/DeepEval-Dashboard-04-26-2026_12_40_PM.png)

### ShopSphere Chatbot (Subsystem A)

React UI with the FastAPI backend talking to Groq's `llama-3.3-70b-versatile`.

![ShopSphere Support Chat](screenshots/ShopSphere-—-Support-Chat-04-26-2026_12_41_PM.png)

### RAG Explorer (Subsystem B)

Pipeline dashboard exposing every stage from ingest through answer.

![RAG Explorer Dashboard](screenshots/Dashboard-·-RAG-Explorer-04-26-2026_12_41_PM.png)

## Why three subsystems

You can't evaluate something you haven't built. **A** and **B** are real, working LLM apps that exhibit real LLM problems (hallucination, weak retrieval, prompt leakage). **C** points DeepEval at them and reports.

```
   A (chatbot)               B (RAG Explorer)
       │                            │
       └────────────┬───────────────┘
                    │
            DeepEval framework C
                    │
              HTML report
```

## One-shot setup

```bash
cd Project_23_DeepEvAL_Framework

# Shared Python venv
uv venv .venv
source .venv/bin/activate
uv pip install -r 01_chatbot/backend/requirements.txt \
                -r 02_rag_explorer/requirements.txt \
                -r 03_deepeval_framework/requirements.txt

# React deps for the chatbot UI
cd 01_chatbot/frontend && npm install && cd ../..

# Pull the embedding model into Ollama (one-time)
ollama pull nomic-embed-text

# Set your keys
export GROQ_API_KEY=gsk_...
export JUDGE_PROVIDER=groq            # or openai, or ollama
```

## Run everything

Open three terminals (all from the project root, with the venv activated):

```bash
# Terminal 1 — chatbot backend (port 8201)
cd 01_chatbot/backend && uvicorn app:app --reload --port 8201

# Terminal 2 — chatbot frontend (port 5173)
cd 01_chatbot/frontend && npm run dev

# Terminal 3 — RAG Explorer (port 8202)
cd 02_rag_explorer && uvicorn app:app --reload --port 8202 --loop asyncio
```

Visit:
- <http://localhost:5173> — chatbot UI
- <http://localhost:8202> — RAG Explorer

Then evaluate via the **live web dashboard** (recommended) or pytest:

```bash
# Live dashboard at http://localhost:8203 — run individual metrics or all visible
cd 03_deepeval_framework
uvicorn dashboard.app:app --port 8203 --loop asyncio

# Or batch CLI run with HTML report
python run_all.py
open reports/report.html
```

## Switching judge LLMs

```bash
# OpenAI (default)
export JUDGE_PROVIDER=openai OPENAI_API_KEY=sk-...

# Groq with OSS-120B (cheaper, fast)
export JUDGE_PROVIDER=groq GROQ_API_KEY=gsk-...

# Local Ollama (no API costs, slower)
export JUDGE_PROVIDER=ollama
```

The same metric tests run against all three providers — `instructor` makes their structured-output behavior uniform.

## Per-subsystem READMEs

- [`01_chatbot/README.md`](01_chatbot/README.md)
- [`02_rag_explorer/README.md`](02_rag_explorer/README.md)
- [`03_deepeval_framework/README.md`](03_deepeval_framework/README.md)
