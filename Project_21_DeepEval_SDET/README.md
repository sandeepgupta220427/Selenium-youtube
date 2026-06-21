# Project 21: DeepEval for SDET — Practical LLM Testing

## Overview

This project takes the evaluation concepts from Project 20 and puts them into production-grade SDET practice. You get a **complete, runnable lab** with three apps that talk to each other:

1. A real **Groq-powered support chatbot** to test against (the "app under test")
2. A **DeepEval Metric Verifier** that scores chatbot responses with 9 different metrics
3. A **V2 educational verifier** that walks students through every metric, one lesson at a time, with editable good/bad sample pairs and live scoring

Everything is themed in a clean, Claude-style UI (cream paper, coral accents, serif headings) so you can demo it to students or stakeholders without apologising for the looks.

## Objective

Build production-ready LLM test suites using DeepEval with real SDET patterns: custom metrics, parameterized test cases, threshold-based quality gates, regression tracking, and automated CI/CD evaluation.

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.11+ | Core language |
| DeepEval | LLM evaluation framework |
| FastAPI + Uvicorn | All three local apps (chatbot, verifier, verifier V2) |
| Jinja2 | Server-side templating |
| Pytest | Test runner and assertions |
| Pydantic | Input/output schema validation |
| Groq (Llama 4) | Chatbot LLM |
| OpenAI (GPT-4o-mini) | DeepEval judge model |
| Ollama / OpenAI | Drop-in LLM provider for evaluation |

## What You Will Learn

- Set up DeepEval in an existing SDET project structure
- Write parameterized LLM test cases with multiple metrics per test
- Build custom DeepEval metrics for domain-specific evaluation (G-Eval)
- Test a chatbot for answer relevancy, faithfulness, hallucination, and tone
- Test for bias and toxicity with safety metrics
- Test retrieval quality with Contextual Precision / Recall / Relevancy
- Build golden datasets from production logs
- Set up quality gates (fail CI if faithfulness drops below 0.85)
- Run evaluation suites against both OpenAI and local Ollama models

## What's in this folder

```
Project_21_DeepEval_SDET/
├── README.md                          ← you are here
├── chatbot/                           ← App under test (port 8100)
│   ├── app.py                         ← FastAPI + Groq + chat UI at /ui
│   ├── requirements.txt
│   └── knowledge_base/
│       ├── refund_policy.md
│       ├── shipping_policy.md
│       └── account_help.md
├── verifier/                          ← Classic Verifier (port 5180)
│   ├── app.py                         ← FastAPI + DeepEval scoring API
│   ├── samples.py                     ← 6 categories × 4 sample test cases
│   ├── metrics_info.py                ← Metric reference content
│   ├── integrations_info.py           ← Integration docs
│   ├── requirements.txt
│   └── templates/                     ← Jinja2 templates (Claude theme)
│       ├── _base.html
│       ├── index.html                 ← Evaluator
│       ├── samples.html               ← Sample categories
│       ├── sample_detail.html         ← Per-category samples
│       ├── metrics.html               ← Metric reference
│       └── integrations.html
├── verifier_v2/                       ← Educational Verifier V2 (port 5181)
│   ├── app.py                         ← FastAPI + DeepEval scoring + lesson routes
│   ├── metric_lessons.py              ← Full lesson content for all 9 metrics
│   ├── requirements.txt
│   └── templates/
│       ├── _base.html                 ← Claude-themed shell + progress tracker
│       ├── home.html                  ← Lesson grid, grouped by category
│       └── lesson.html                ← Per-metric lesson page (live scoring)
├── exercises/                         ← Hands-on student exercises
│   ├── 01_basic_answer_relevancy.py
│   ├── 02_medium_rag_triad.py
│   └── 03_advanced_safety_and_conversation.py
└── projects/                          ← Starter projects (legacy reference)
    ├── 01_QA_Chatbot_Evaluator/
    └── 02_RAG_Pipeline_Quality_Gate/
```

## Quick Start (the full stack in one go)

### Prerequisites
- Python 3.11+
- A free **Groq** API key — https://console.groq.com (chatbot LLM)
- An **OpenAI** API key — https://platform.openai.com (DeepEval judge model)

### Install dependencies
```bash
cd Project_21_DeepEval_SDET
pip install -r chatbot/requirements.txt
pip install -r verifier/requirements.txt
pip install -r verifier_v2/requirements.txt
```

### 1. Start the chatbot (Terminal 1) — port 8100
```bash
cd chatbot
export GROQ_API_KEY=gsk_...
uvicorn app:app --reload --port 8100
```
Open **http://localhost:8100/ui** for the Claude-themed chat interface.

### 2. Start the classic verifier (Terminal 2) — port 5180
```bash
cd verifier
export OPENAI_API_KEY=sk-...
uvicorn app:app --reload --port 5180 --loop asyncio
```
Open **http://localhost:5180** for the metric evaluator.

> **Why `--loop asyncio`?** DeepEval uses `nest_asyncio` to run inside event loops, but this is incompatible with Uvicorn's default `uvloop`. Always start verifier processes with `--loop asyncio`.

### 3. Start the V2 educational verifier (Terminal 3) — port 5181
```bash
cd verifier_v2
export OPENAI_API_KEY=sk-...
uvicorn app:app --reload --port 5181 --loop asyncio
```
Open **http://localhost:5181** for the lesson-style metric explorer.

## The three apps

### 🛍️ Chatbot — `chatbot/` (port 8100)

A **ShopEasy customer-support chatbot** powered by Groq's Llama 4 with simple keyword-based RAG over three knowledge-base markdown files (refund policy, shipping policy, account help).

| Endpoint | What it does |
|---|---|
| `GET /` | JSON service info |
| `GET /ui` | **Chat UI** — Claude theme, suggested prompts, live retrieval-context panel |
| `GET /health` | Health check |
| `GET /docs` | FastAPI auto-docs |
| `POST /chat` | `{"message": "..."}` → `{"reply", "sources", "retrieval_context"}` |

The chatbot is deliberately simple so it's easy to break — perfect target for testing hallucinations, faithfulness, and answer relevancy.

### 🔬 Classic Verifier — `verifier/` (port 5180)

A practitioner's tool for **manual** DeepEval scoring. Pick a metric, type or fetch an answer from the chatbot, set a threshold, click Evaluate.

| Page | Purpose |
|---|---|
| `/` | Evaluator — pick metric(s), threshold, judge model; pull from chatbot or paste; run single or multi-metric |
| `/samples` | Six categories of pre-loaded test cases (refund, shipping, subscription, RAG triad, safety, quality gate) |
| `/samples/{cat}` | 3-4 ready-to-run samples per category, each with recommended metrics |
| `/metrics` | Reference: what each metric does, when to use it |
| `/integrations` | DeepEval integrations docs |

Supports all 9 metrics: Faithfulness, Answer Relevancy, Hallucination, Contextual Precision/Recall/Relevancy, Bias, Toxicity, and Completeness (G-Eval).

### 🎓 V2 Educational Verifier — `verifier_v2/` (port 5181) ⭐ NEW

A **guided learning experience**: every metric is a self-contained lesson with explanation, formula, when-to-use, threshold guidance, gotchas, and a **good/bad sample pair you can run live**.

**Features unique to V2:**

| Feature | What it does |
|---|---|
| **Lesson grid home** | All 9 metrics grouped by category with "needs context" / "needs expected" tags |
| **3-section per-lesson layout** | (1) What it checks; (2) When to use + thresholds + gotchas; (3) Live samples |
| **Good vs Bad pair** | Side-by-side cards — see contrasting scores on the same metric |
| **Editable inputs** | Every field is editable; re-run to see scores change |
| **Run side-by-side** | One click scores both samples in parallel |
| **Inverse metric handling** | Hallucination / Bias / Toxicity correctly invert pass logic (lower = better) |
| **Progress tracking** | localStorage tracks explored lessons; shows "X / 9 explored" pill |
| **Stepper sidebar** | Numbered list of all lessons with active highlight + completion ticks |
| **Prev / Next navigation** | Walk through metrics linearly |
| **Animated score reveal** | Score bar animates; pass/fail color-coded; LLM judge reasoning shown |

**Lesson URLs:**
- `/lesson/faithfulness`
- `/lesson/answer_relevancy`
- `/lesson/hallucination`
- `/lesson/contextual_precision`
- `/lesson/contextual_recall`
- `/lesson/contextual_relevancy`
- `/lesson/bias`
- `/lesson/toxicity`
- `/lesson/completeness`

## Running the exercises

The `exercises/` folder has three pytest-style files for hands-on practice:

```bash
export OPENAI_API_KEY=sk-...
cd Project_21_DeepEval_SDET/exercises

# Beginner
pytest 01_basic_answer_relevancy.py -v

# Intermediate
pytest 02_medium_rag_triad.py -v

# Advanced
pytest 03_advanced_safety_and_conversation.py -v
```

Or run them with the DeepEval CLI for richer output:
```bash
deepeval test run exercises/
```

## Metric reference (what's covered)

### Answer Quality
- **Faithfulness** — every claim in the answer is backed by retrieval context
- **Answer Relevancy** — the answer stays on topic
- **Hallucination** — explicit detection of statements that contradict context

### Context Quality (Retrieval)
- **Contextual Precision** — relevant chunks are ranked higher than irrelevant ones
- **Contextual Recall** — everything needed to answer is actually retrieved
- **Contextual Relevancy** — most retrieved chunks are on-topic

### Safety
- **Bias** — output free of biased / prejudiced statements
- **Toxicity** — output free of rude, harmful, or abusive language

### Presentation (Custom)
- **Completeness (G-Eval)** — actual output covers all key points from expected output, using DeepEval's chain-of-thought G-Eval framework

## Common gotchas

1. **`Can't patch loop of type <class 'uvloop.Loop'>`** — DeepEval can't run under Uvicorn's default uvloop. Start verifier processes with `--loop asyncio`.
2. **`OPENAI_API_KEY not set`** — DeepEval's default judge is `gpt-4o-mini` from OpenAI. The chatbot and verifier need different keys (Groq vs OpenAI).
3. **Hallucination / Bias / Toxicity scores look weird** — these are INVERSE metrics (higher = worse). V2 handles the threshold logic correctly; in the classic verifier, read the `reason` field to interpret.
4. **Hallucination needs `context`, not `retrieval_context`** — V2 maps this automatically; if you call DeepEval directly, pass the ground-truth context as the `context` field on `LLMTestCase`.

## Starter Projects

This project also includes two complete starter projects in the `projects/` folder for further exploration:

### Project 21.1: QA Chatbot Evaluator (`projects/01_QA_Chatbot_Evaluator/`)
A FastAPI QA chatbot + complete DeepEval test suite. Evaluates answer relevancy, faithfulness, and hallucination. Includes a chatbot server, knowledge base, golden dataset, and HTML report generator.

### Project 21.2: RAG Pipeline Quality Gate (`projects/02_RAG_Pipeline_Quality_Gate/`)
An automated CI/CD quality gate for a RAG pipeline. 6 metrics with threshold-based pass/fail, A/B model comparison, full RAG pipeline, GitHub Actions workflow, and drift tracker.

## QA Angle

This is where SDET meets AI evaluation. As an SDET, you already write automated test suites, set up CI/CD gates, and track quality metrics. This project teaches you to apply those exact same patterns to LLM-powered features. Instead of asserting `response.status == 200`, you assert `faithfulness_score >= 0.85`. Instead of checking UI elements, you check if the AI hallucinates. The testing mindset is the same — the metrics are different. Every SDET working on AI-powered products needs this in their toolkit.
