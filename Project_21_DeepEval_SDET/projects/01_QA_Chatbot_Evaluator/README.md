# Project 21.1: QA Chatbot Evaluator

## What This Project Does

You will build and evaluate a QA knowledge-base chatbot that answers questions about testing processes. The chatbot uses a simple RAG pipeline (documents + LLM), and you will write a complete DeepEval test suite to measure its quality across multiple dimensions.

This is a realistic scenario: your team has a chatbot that helps junior testers find answers about test strategy, tools, and processes. Your job as an SDET is to make sure the chatbot gives accurate, relevant, and safe answers.

## Learning Outcomes

By completing this project, you will be able to:
- Set up a FastAPI chatbot with a simple document retrieval backend
- Write DeepEval test cases for a real LLM application
- Evaluate answer relevancy, faithfulness, and hallucination
- Build a golden dataset from real Q&A pairs
- Generate HTML evaluation reports
- Set a quality baseline and detect regressions

## Project Structure

```
01_QA_Chatbot_Evaluator/
├── README.md
├── requirements.txt
├── app.py                  # FastAPI chatbot server
├── knowledge_base/
│   ├── test_strategy.md    # QA test strategy document
│   ├── bug_process.md      # Bug reporting standards
│   └── tool_stack.md       # QA tool documentation
├── tests/
│   ├── conftest.py         # Shared fixtures and chatbot client
│   ├── test_relevancy.py   # Answer relevancy tests
│   ├── test_faithfulness.py # Faithfulness tests
│   ├── test_hallucination.py # Hallucination detection
│   └── test_golden.py      # Golden dataset regression tests
├── datasets/
│   └── golden_dataset.json # Curated Q&A pairs with expected answers
└── reports/
    └── generate_report.py  # HTML report generator
```

## Step-by-Step Guide

### Step 1: Set Up the Chatbot

```python
# app.py - Simple QA chatbot with document retrieval
from fastapi import FastAPI
from pydantic import BaseModel
import openai

app = FastAPI()

# Load knowledge base documents
knowledge_base = {}
for doc_name in ["test_strategy", "bug_process", "tool_stack"]:
    with open(f"knowledge_base/{doc_name}.md") as f:
        knowledge_base[doc_name] = f.read()

class Question(BaseModel):
    query: str

class Answer(BaseModel):
    response: str
    source_doc: str

@app.post("/ask", response_model=Answer)
async def ask_question(question: Question):
    # Simple keyword-based retrieval (replace with vector search in production)
    best_doc = find_best_document(question.query, knowledge_base)

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Answer based on this context only:\\n{best_doc['content']}"},
            {"role": "user", "content": question.query}
        ]
    )

    return Answer(
        response=response.choices[0].message.content,
        source_doc=best_doc["name"]
    )
```

### Step 2: Write Your First DeepEval Test

```python
# tests/test_relevancy.py
import requests
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric

CHATBOT_URL = "http://localhost:8000/ask"

def get_chatbot_answer(question: str) -> str:
    response = requests.post(CHATBOT_URL, json={"query": question})
    return response.json()["response"]

def test_coverage_question_relevancy():
    answer = get_chatbot_answer("What is the minimum code coverage?")

    test_case = LLMTestCase(
        input="What is the minimum code coverage?",
        actual_output=answer,
    )

    metric = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")
    assert_test(test_case, [metric])
```

### Step 3: Build a Golden Dataset

```json
// datasets/golden_dataset.json
[
    {
        "input": "What is the minimum code coverage?",
        "expected_output": "80% minimum code coverage for unit tests",
        "context": "test_strategy"
    },
    {
        "input": "How fast should a P0 bug be fixed?",
        "expected_output": "P0 bugs must be fixed within 4 hours",
        "context": "bug_process"
    },
    {
        "input": "What tool do we use for load testing?",
        "expected_output": "k6 is used for load testing",
        "context": "tool_stack"
    }
]
```

### Step 4: Run Evaluations

```bash
# Start the chatbot
uvicorn app:app --port 8000 &

# Run all tests
deepeval test run tests/ -v

# Run specific suite
deepeval test run tests/test_relevancy.py -v
```

## Success Criteria

| Metric | Threshold | What It Measures |
|--------|-----------|-----------------|
| Answer Relevancy | >= 0.80 | Does the answer address the question? |
| Faithfulness | >= 0.85 | Does the answer only use facts from context? |
| Hallucination | <= 0.30 | Does the answer make up facts? (lower is better) |
| Golden Dataset Pass Rate | >= 90% | How many curated Q&A pairs pass all metrics? |
