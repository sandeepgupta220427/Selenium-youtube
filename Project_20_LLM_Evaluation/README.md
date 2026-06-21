# Project 20: LLM Evaluation for QA Engineers

## Overview

This project teaches QA engineers how to evaluate LLM-powered applications the same way they evaluate traditional software: with structured test cases, measurable metrics, and reproducible results. You will learn to identify hallucinations, measure answer quality, test safety boundaries, and build evaluation pipelines that run in CI/CD.

## Objective

Train students to test LLM systems for accuracy, safety, reliability, hallucinations, and structured output quality using industry-standard evaluation frameworks.

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.11+ | Core language |
| DeepEval | Primary evaluation framework |
| Promptfoo | Prompt testing and comparison |
| RAGAS | RAG-specific evaluation metrics |
| OpenAI / Ollama | LLM providers for testing |
| Pytest | Test runner integration |

## What You Will Learn

- Understand the difference between traditional testing and LLM evaluation
- Write evaluation test cases using DeepEval metrics (faithfulness, relevancy, hallucination)
- Build golden datasets for regression testing LLM outputs
- Test for hallucination detection and factual accuracy
- Evaluate safety boundaries and harmful content filtering
- Test structured output quality (JSON schema compliance)
- Measure RAG pipeline quality using RAGAS metrics (context precision, recall, faithfulness)
- Integrate LLM evaluation into CI/CD pipelines

## Key Deliverables

1. **Evaluation Test Suite** - Pytest-based test suite using DeepEval metrics
2. **Golden Dataset** - Curated input/expected-output pairs for regression testing
3. **Hallucination Detector** - Tests that catch when the LLM fabricates information
4. **Safety Test Cases** - Boundary tests for harmful, biased, or inappropriate outputs
5. **RAG Evaluator** - RAGAS-based pipeline evaluation for retrieval quality
6. **Structured Output Validator** - JSON schema compliance checker for LLM responses
7. **CI/CD Integration** - GitHub Actions workflow running evaluation on every PR

## Project Structure

```
Project_20_LLM_Evaluation/
├── README.md
├── requirements.txt
├── src/
│   ├── evaluators/
│   │   ├── accuracy_evaluator.py
│   │   ├── hallucination_evaluator.py
│   │   ├── safety_evaluator.py
│   │   ├── rag_evaluator.py
│   │   └── structured_output_evaluator.py
│   ├── datasets/
│   │   ├── golden_dataset.json
│   │   ├── safety_test_cases.json
│   │   └── rag_test_cases.json
│   └── utils/
│       ├── llm_client.py
│       └── metrics_reporter.py
├── tests/
│   ├── test_accuracy.py
│   ├── test_hallucination.py
│   ├── test_safety.py
│   ├── test_rag_quality.py
│   └── test_structured_output.py
├── reports/
│   └── evaluation_report.html
└── .github/
    └── workflows/
        └── llm_evaluation.yml
```

## Getting Started

### Prerequisites
- Python 3.11+
- OpenAI API key or Ollama running locally
- pip or uv package manager

### Installation
```bash
cd Project_20_LLM_Evaluation
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration
```bash
export OPENAI_API_KEY=your_key_here
# OR use Ollama locally (no key needed)
```

### Run Evaluations
```bash
pytest tests/ -v
```

### Generate Report
```bash
python src/utils/metrics_reporter.py
```

## Exercises

This project includes two hands-on exercises in the `exercises/` folder:

### Exercise 1: Basic LLM Evaluation (`exercises/01_basic_llm_evaluation.py`)
- **Level:** Beginner
- **What you do:** Evaluate a customer support chatbot using DeepEval
- **Metrics covered:** AnswerRelevancyMetric, HallucinationMetric, GEval (Correctness)
- **Includes:** 3 working test cases + 2 TODO exercises for you to complete
- **Run:** `deepeval test run exercises/01_basic_llm_evaluation.py`

### Exercise 2: Advanced RAG Evaluation (`exercises/02_advanced_rag_evaluation.py`)
- **Level:** Advanced
- **What you do:** Evaluate a QA knowledge base RAG pipeline with multiple metrics
- **Metrics covered:** Faithfulness, ContextualRelevancy, ContextualPrecision, ContextualRecall
- **Includes:** Multi-metric evaluation, golden dataset batch testing, quality gates, 2 TODO exercises
- **Run:** `deepeval test run exercises/02_advanced_rag_evaluation.py`

## QA Angle

Traditional QA tests check if software does what it should. LLM evaluation checks if AI does what it should, but the challenge is that "correct" is often subjective. This project teaches you to make LLM testing as rigorous as functional testing by defining clear metrics, building reproducible test cases, and automating evaluation in your pipeline. Every QA engineer working with AI features needs this skill.
