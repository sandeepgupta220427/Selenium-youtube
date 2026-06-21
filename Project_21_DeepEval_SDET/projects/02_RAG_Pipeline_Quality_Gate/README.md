# Project 21.2: RAG Pipeline Quality Gate with CI/CD

## What This Project Does

You will build an automated quality gate for a RAG pipeline that runs in CI/CD. When someone changes the prompt, swaps the LLM model, or updates the knowledge base documents, this quality gate automatically evaluates the pipeline and blocks the merge if quality drops below acceptable thresholds.

This is the production pattern every SDET needs: automated LLM evaluation that catches regressions before they reach users.

## Learning Outcomes

By completing this project, you will be able to:
- Build a complete RAG pipeline with ChromaDB and LangChain
- Write a comprehensive DeepEval evaluation suite (6+ metrics)
- Create threshold-based quality gates that fail CI on regression
- Track metric drift across model versions and prompt changes
- Compare two RAG configurations side-by-side (A/B evaluation)
- Set up GitHub Actions to run LLM evaluation on every PR
- Generate evaluation dashboards for stakeholder visibility

## Project Structure

```
02_RAG_Pipeline_Quality_Gate/
├── README.md
├── requirements.txt
├── rag/
│   ├── pipeline.py          # RAG pipeline (ingest + retrieve + generate)
│   ├── ingest.py             # Document chunking and embedding
│   ├── retriever.py          # ChromaDB vector search
│   └── generator.py          # LLM answer generation
├── documents/
│   ├── api_docs.md           # Sample API documentation
│   ├── test_guide.md         # Testing guidelines
│   └── release_process.md    # Release process docs
├── tests/
│   ├── conftest.py           # Pipeline fixtures, metric configs
│   ├── test_retrieval_quality.py   # Context precision & recall
│   ├── test_generation_quality.py  # Faithfulness & relevancy
│   ├── test_hallucination.py       # Hallucination detection
│   ├── test_end_to_end.py          # Full pipeline evaluation
│   └── test_ab_comparison.py       # Compare two configurations
├── datasets/
│   ├── golden_dataset.json   # 25+ curated evaluation pairs
│   └── adversarial_cases.json # Edge cases designed to break the RAG
├── quality_gates/
│   ├── thresholds.yaml       # Minimum acceptable scores per metric
│   └── gate_runner.py        # Reads thresholds, runs evaluation, exits 0/1
├── reports/
│   ├── dashboard.py          # Generate HTML evaluation dashboard
│   └── drift_tracker.py      # Compare scores across runs
└── .github/
    └── workflows/
        └── rag_quality_gate.yml  # GitHub Actions CI pipeline
```

## Step-by-Step Guide

### Step 1: Define Quality Thresholds

```yaml
# quality_gates/thresholds.yaml
# These are your quality standards. CI fails if any metric drops below.

metrics:
  faithfulness:
    threshold: 0.85
    description: "Answer must be grounded in retrieved context"
    severity: "blocker"    # Fails the entire pipeline

  answer_relevancy:
    threshold: 0.80
    description: "Answer must address the question asked"
    severity: "blocker"

  contextual_precision:
    threshold: 0.75
    description: "Top retrieved documents must be relevant"
    severity: "warning"    # Warns but does not block

  contextual_recall:
    threshold: 0.75
    description: "All relevant documents must be retrieved"
    severity: "warning"

  hallucination:
    threshold: 0.30        # Lower is better for this metric
    description: "Answer must not contain made-up facts"
    severity: "blocker"

  correctness:
    threshold: 0.80
    description: "Answer must match golden dataset expected output"
    severity: "blocker"

overall:
  min_pass_rate: 0.90      # 90% of test cases must pass all blockers
```

### Step 2: Build the RAG Pipeline

```python
# rag/pipeline.py
from rag.ingest import ingest_documents
from rag.retriever import retrieve_context
from rag.generator import generate_answer

class RAGPipeline:
    def __init__(self, model="gpt-4o-mini", chunk_size=500, top_k=3):
        self.model = model
        self.chunk_size = chunk_size
        self.top_k = top_k
        self.collection = ingest_documents("documents/", chunk_size=chunk_size)

    def ask(self, question: str) -> dict:
        # Step 1: Retrieve relevant chunks
        contexts = retrieve_context(self.collection, question, top_k=self.top_k)

        # Step 2: Generate answer using retrieved context
        answer = generate_answer(question, contexts, model=self.model)

        return {
            "question": question,
            "answer": answer,
            "retrieved_contexts": contexts,
        }
```

### Step 3: Write the Quality Gate Runner

```python
# quality_gates/gate_runner.py
import yaml
import sys
from deepeval import evaluate
from deepeval.metrics import (
    FaithfulnessMetric, AnswerRelevancyMetric,
    ContextualPrecisionMetric, HallucinationMetric,
)

def run_quality_gate():
    with open("quality_gates/thresholds.yaml") as f:
        config = yaml.safe_load(f)

    # Load golden dataset and run pipeline
    dataset = load_golden_dataset("datasets/golden_dataset.json")
    results = evaluate(dataset, build_metrics(config))

    # Check blockers
    blockers_passed = check_blockers(results, config)
    pass_rate = calculate_pass_rate(results)

    print(f"Pass Rate: {pass_rate:.1%}")
    print(f"Required: {config['overall']['min_pass_rate']:.1%}")

    if not blockers_passed or pass_rate < config["overall"]["min_pass_rate"]:
        print("QUALITY GATE FAILED")
        sys.exit(1)
    else:
        print("QUALITY GATE PASSED")
        sys.exit(0)
```

### Step 4: A/B Comparison (Compare Two Configs)

```python
# tests/test_ab_comparison.py
def test_compare_models():
    """
    Compare gpt-4o-mini vs gpt-4o on the same golden dataset.
    Use this when deciding whether to upgrade the model.
    """
    pipeline_a = RAGPipeline(model="gpt-4o-mini", chunk_size=500)
    pipeline_b = RAGPipeline(model="gpt-4o", chunk_size=500)

    dataset = load_golden_dataset()

    results_a = run_evaluation(pipeline_a, dataset)
    results_b = run_evaluation(pipeline_b, dataset)

    print(f"Model A (gpt-4o-mini): faithfulness={results_a.faithfulness:.2f}")
    print(f"Model B (gpt-4o):      faithfulness={results_b.faithfulness:.2f}")

    # The better model should score higher on faithfulness
    assert results_b.faithfulness >= results_a.faithfulness - 0.05, \
        "New model should not regress on faithfulness"
```

### Step 5: GitHub Actions CI Pipeline

```yaml
# .github/workflows/rag_quality_gate.yml
name: RAG Quality Gate

on:
  pull_request:
    paths:
      - 'rag/**'
      - 'documents/**'
      - 'datasets/**'

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run Quality Gate
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python quality_gates/gate_runner.py

      - name: Generate Report
        if: always()
        run: python reports/dashboard.py

      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: evaluation-report
          path: reports/output/
```

### Step 6: Run Everything

```bash
# Set up
pip install -r requirements.txt

# Run the quality gate locally
python quality_gates/gate_runner.py

# Run individual test suites
deepeval test run tests/test_retrieval_quality.py -v
deepeval test run tests/test_generation_quality.py -v

# Compare two configurations
deepeval test run tests/test_ab_comparison.py -v

# Generate dashboard
python reports/dashboard.py
open reports/output/dashboard.html
```

## Success Criteria

| Check | Target | Description |
|-------|--------|-------------|
| Faithfulness | >= 0.85 | No answers with made-up facts from outside context |
| Answer Relevancy | >= 0.80 | Answers address the actual question asked |
| Context Precision | >= 0.75 | Top-ranked retrieved docs are actually relevant |
| Hallucination Rate | <= 0.30 | Less than 30% hallucination score across all tests |
| Golden Dataset Pass Rate | >= 90% | 90% of curated Q&A pairs pass all blocker metrics |
| CI Pipeline | Green | Quality gate passes on every PR that touches RAG code |
| A/B Comparison | No regression | Model swap does not drop faithfulness by more than 5% |

## Why This Matters for SDETs

This is the same pattern you use for any automated quality gate: define thresholds, run tests, block merges on failure. The only difference is that instead of checking HTTP status codes or DOM elements, you are checking faithfulness scores and hallucination rates. If you can write a Playwright E2E test, you can write a DeepEval quality gate. The mental model is identical.
