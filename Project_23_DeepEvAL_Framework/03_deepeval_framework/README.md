# Subsystem C — DeepEval Framework

A test framework that evaluates **Subsystem A (chatbot)** and **Subsystem B (RAG Explorer)** with **20 distinct DeepEval metrics**, against **swappable judge LLMs** (OpenAI, Groq, or local Ollama).

## What it tests

| # | Metric | Target | Type |
|---|--------|--------|------|
| 0 | Smoke (judge / health) | both | infra |
| 1 | Answer Relevancy | chatbot | quality |
| 2 | Faithfulness | chatbot | quality |
| 3 | Hallucination | chatbot | quality |
| 4 | Bias | chatbot | safety |
| 5 | Toxicity | chatbot | safety |
| 6 | G-Eval Completeness | chatbot | g-eval |
| 7 | G-Eval No-Prompt-Leak (PII) | chatbot | safety / g-eval |
| 8 | Contextual Precision | RAG | retrieval |
| 9 | Contextual Recall | RAG | retrieval |
| 10 | Contextual Relevancy | RAG | retrieval |
| 11 | RAG Faithfulness | RAG | quality |
| 12 | RAG Answer Relevancy | RAG | quality |
| 13 | RAG Hallucination | RAG | quality |
| 14 | G-Eval Correctness | RAG | g-eval |
| 15 | G-Eval Citation Quality | RAG | g-eval |
| 16 | RAG Bias | RAG | safety |
| 17 | RAG Toxicity | RAG | safety |
| 18 | Summarization | (synthetic) | quality |
| 19 | Conversation Relevancy (multi-turn) | chatbot | conversational |
| 20 | G-Eval Helpfulness | RAG | g-eval |

## Switchable judge LLMs

Set `JUDGE_PROVIDER` to one of:

- **`openai`** → uses `OPENAI_API_KEY` and `gpt-4o-mini` (override with `JUDGE_MODEL_OPENAI`)
- **`groq`** → uses `GROQ_API_KEY` and `openai/gpt-oss-120b` (override with `JUDGE_MODEL_GROQ`)
- **`ollama`** → uses local Ollama at `http://localhost:11434/v1` and `gpt-oss:20b` (override with `JUDGE_MODEL_OLLAMA`)

The same `CompatibleJudge` class works for all three because OpenAI, Groq, and Ollama all expose an OpenAI-compatible endpoint. `instructor` handles structured-output schema extraction uniformly.

## Quick start

```bash
cd 03_deepeval_framework
pip install -r requirements.txt

# Pick judge
export JUDGE_PROVIDER=groq
export GROQ_API_KEY=gsk_...

# (or OpenAI)
# export JUDGE_PROVIDER=openai
# export OPENAI_API_KEY=sk-...

# (or fully local)
# export JUDGE_PROVIDER=ollama

# Make sure Subsystem A and B are running
# (see their READMEs)

python run_all.py
open reports/report.html
```

## Filtering

```bash
# Just chatbot quality metrics
python run_all.py --only "chatbot and quality"

# Just retrieval metrics
python run_all.py --only retrieval

# Skip safety metrics
python run_all.py --only "not safety"

# Run a specific metric
python run_all.py --keyword answer_relevancy

# Cap to 2 golden cases per metric for fast dev iteration
python run_all.py --max-goldens 2

# Switch judge per-run
python run_all.py --provider ollama --judge-model gpt-oss:20b
```

## File map

```
03_deepeval_framework/
├── run_all.py              one-command runner
├── pytest.ini              markers + html report config
├── conftest.py             fixtures: judge, chatbot, rag, goldens
├── llm_providers/
│   ├── base.py             CompatibleJudge (works for OpenAI/Groq/Ollama)
│   └── factory.py          reads JUDGE_PROVIDER and builds the judge
├── targets/
│   ├── chatbot.py          HTTP client → Subsystem A
│   └── rag_pipeline.py     HTTP client → Subsystem B
├── datasets/
│   ├── chatbot_goldens.py  8 golden Q&A + 5 adversarial safety prompts
│   └── rag_goldens.py      8 golden Q&A with expected sources/keywords
└── tests/
    └── test_NN_*.py        one file per metric (20 files)
```

## Scoring conventions

| Direction | Metrics |
|-----------|---------|
| Higher is better (threshold = floor) | answer relevancy, faithfulness, contextual precision/recall/relevancy, summarization, all G-Evals, conversation relevancy |
| Lower is better (threshold = ceiling) | hallucination, bias, toxicity |

DeepEval handles the inversion automatically; just use `is_successful()`.
