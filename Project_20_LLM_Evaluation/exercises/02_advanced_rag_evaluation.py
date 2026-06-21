"""
Exercise 2 (Advanced): RAG Pipeline Evaluation with RAGAS Metrics
==================================================================

Goal: Learn how to evaluate a complete RAG (Retrieval-Augmented Generation)
pipeline using multiple metrics simultaneously, build a golden dataset,
and set up threshold-based quality gates.

Scenario:
    You are an SDET responsible for quality of an internal QA knowledge base.
    The RAG system retrieves relevant documentation and generates answers
    about your company's testing standards, tools, and processes.
    You need to evaluate:
    1. Is the retriever finding the RIGHT documents? (Context Precision/Recall)
    2. Is the generator using ONLY the retrieved context? (Faithfulness)
    3. Is the final answer actually useful? (Answer Relevancy)
    4. Does the answer match known correct answers? (Correctness)

What you will learn:
    - How to evaluate RAG systems with multiple metrics at once
    - How to build and use golden datasets (input + expected pairs)
    - How to use FaithfulnessMetric, ContextualRelevancyMetric, ContextualPrecisionMetric
    - How to set up quality gates (minimum score thresholds)
    - How to generate evaluation reports
    - How to compare two RAG configurations side by side

Setup:
    pip install deepeval openai
    export OPENAI_API_KEY=your_key_here

Instructions:
    1. Read through the complete examples
    2. Fill in the TODO sections
    3. Run: deepeval test run exercises/02_advanced_rag_evaluation.py
    4. Analyze the multi-metric report
"""

from deepeval import assert_test, evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    HallucinationMetric,
    GEval,
)
from deepeval.dataset import EvaluationDataset

# ============================================================
# KNOWLEDGE BASE: QA Team Documentation (simulated retrieval)
# In a real system, these come from your vector database.
# ============================================================

DOC_TEST_STRATEGY = """
QA Test Strategy Document v2.1:
- All features require unit tests with minimum 80% code coverage.
- Integration tests must cover all API endpoints.
- E2E tests run on staging before every release.
- Performance tests are mandatory for any endpoint serving > 1000 req/min.
- Security scans run nightly using OWASP ZAP.
- Accessibility testing follows WCAG 2.1 AA standards.
- Test environments: dev, staging, pre-prod, production.
"""

DOC_BUG_PROCESS = """
Bug Reporting Standards:
- All bugs must be filed in Jira with severity (P0-P4).
- P0 bugs: production down, must fix within 4 hours.
- P1 bugs: major feature broken, fix within 24 hours.
- P2 bugs: minor feature issue, fix within current sprint.
- P3/P4 bugs: cosmetic or edge cases, prioritized in backlog.
- Bug reports require: steps to reproduce, expected vs actual, screenshots.
- Regression bugs automatically escalate severity by one level.
"""

DOC_TOOLS = """
QA Tool Stack:
- Test Framework: Playwright (primary), Selenium (legacy migration).
- API Testing: Postman for manual, REST Assured for automated.
- Performance: k6 for load tests, Lighthouse for web vitals.
- CI/CD: GitHub Actions for pipeline, Jenkins for legacy projects.
- Monitoring: Datadog for APM, PagerDuty for alerts.
- Test Management: TestRail for cases, Allure for reporting.
"""

DOC_RELEASE = """
Release Process:
- Code freeze happens 2 days before release.
- All P0 and P1 bugs must be resolved before release.
- Smoke test suite runs in pre-prod (45 min max).
- Release approval requires sign-off from QA Lead and Engineering Manager.
- Rollback plan must be documented before every production deploy.
- Post-release monitoring window is 2 hours.
"""


# ============================================================
# PART 1: Multi-Metric RAG Evaluation
# Evaluate one RAG response with 4 different quality dimensions.
# ============================================================

def test_rag_multi_metric():
    """
    Evaluate a single RAG response with multiple metrics.
    This is how you check overall pipeline quality in one test.
    """

    test_case = LLMTestCase(
        input="What is the minimum code coverage requirement?",
        actual_output="According to our test strategy, all features require unit tests with a minimum of 80% code coverage. Integration tests must also cover all API endpoints.",
        expected_output="All features require unit tests with minimum 80% code coverage.",
        retrieval_context=[DOC_TEST_STRATEGY]
    )

    # Each metric checks a different quality dimension
    metrics = [
        # Does the answer match what was asked?
        AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini"),

        # Does the answer ONLY use facts from the retrieved context?
        FaithfulnessMetric(threshold=0.7, model="gpt-4o-mini"),

        # Is the retrieved context relevant to the question?
        ContextualRelevancyMetric(threshold=0.7, model="gpt-4o-mini"),

        # Does the retrieved context contain the expected answer?
        ContextualRecallMetric(threshold=0.7, model="gpt-4o-mini"),
    ]

    assert_test(test_case, metrics)


# ============================================================
# PART 2: Golden Dataset Evaluation
# Run multiple test cases in batch to evaluate overall quality.
# ============================================================

def build_golden_dataset():
    """
    Build a golden dataset: a curated set of (question, expected_answer,
    retrieved_context) triples that represent your quality standard.

    In production, golden datasets come from:
    - Subject matter expert reviews
    - Production query logs with verified answers
    - Manually curated Q&A pairs from documentation
    """

    test_cases = [
        LLMTestCase(
            input="How long do we have to fix a P0 bug?",
            actual_output="P0 bugs are production-down issues and must be fixed within 4 hours according to our bug reporting standards.",
            expected_output="P0 bugs must be fixed within 4 hours.",
            retrieval_context=[DOC_BUG_PROCESS]
        ),
        LLMTestCase(
            input="What test framework do we use?",
            actual_output="Our primary test framework is Playwright. We also use Selenium for legacy migration projects.",
            expected_output="Playwright is the primary test framework, Selenium for legacy.",
            retrieval_context=[DOC_TOOLS]
        ),
        LLMTestCase(
            input="What happens before a release?",
            actual_output="Before a release, there is a code freeze 2 days prior. All P0 and P1 bugs must be resolved. A smoke test suite runs in pre-prod taking a maximum of 45 minutes. Release approval requires sign-off from the QA Lead and Engineering Manager.",
            expected_output="Code freeze 2 days before, P0/P1 bugs resolved, smoke tests in pre-prod, sign-off from QA Lead and Engineering Manager.",
            retrieval_context=[DOC_RELEASE]
        ),
        LLMTestCase(
            input="What severity should a regression bug be?",
            actual_output="Regression bugs are automatically escalated by one severity level. So a bug that would normally be P2 becomes P1 if it's a regression.",
            expected_output="Regression bugs automatically escalate severity by one level.",
            retrieval_context=[DOC_BUG_PROCESS]
        ),
        LLMTestCase(
            input="How do we do performance testing?",
            actual_output="We use k6 for load testing and Lighthouse for measuring web vitals. Performance tests are mandatory for any endpoint serving more than 1000 requests per minute.",
            expected_output="k6 for load tests, Lighthouse for web vitals. Mandatory for endpoints > 1000 req/min.",
            retrieval_context=[DOC_TOOLS, DOC_TEST_STRATEGY]
        ),
    ]

    return EvaluationDataset(test_cases=test_cases)


def test_golden_dataset_batch():
    """
    Run the entire golden dataset through evaluation.
    This gives you an overall quality score for your RAG pipeline.
    """

    dataset = build_golden_dataset()

    faithfulness = FaithfulnessMetric(threshold=0.7, model="gpt-4o-mini")
    relevancy = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")

    # evaluate() runs all test cases and returns aggregate scores
    results = evaluate(dataset, [faithfulness, relevancy])
    print(f"\nGolden Dataset Results: {results}")


# ============================================================
# PART 3: Quality Gate - Fail CI if quality drops
# ============================================================

QUALITY_GATE_THRESHOLD = 0.85  # Minimum acceptable score

def test_quality_gate_faithfulness():
    """
    Quality gate test: if faithfulness drops below 0.85, CI fails.

    This is the pattern for CI/CD integration:
    - Set a strict threshold
    - If the model or prompts change and quality drops, the pipeline breaks
    - Forces the team to investigate before merging
    """

    test_case = LLMTestCase(
        input="What is the post-release monitoring window?",
        actual_output="After every production deploy, there is a 2-hour monitoring window where the team watches for issues.",
        expected_output="Post-release monitoring window is 2 hours.",
        retrieval_context=[DOC_RELEASE]
    )

    strict_faithfulness = FaithfulnessMetric(
        threshold=QUALITY_GATE_THRESHOLD,
        model="gpt-4o-mini"
    )

    assert_test(test_case, [strict_faithfulness])


# ============================================================
# TODO EXERCISES
# ============================================================

def test_todo_wrong_context_retrieval():
    """
    TODO Exercise A (Context Quality):
    Simulate a BAD retrieval: the retriever returns the WRONG document.

    Steps:
    1. Create a test case where:
       - input: "What CI/CD tool do we use?"
       - actual_output: a reasonable answer about GitHub Actions
       - retrieval_context: [DOC_BUG_PROCESS]  <-- WRONG document!
       - expected_output: "GitHub Actions for pipeline, Jenkins for legacy"
    2. Use ContextualRelevancyMetric and ContextualPrecisionMetric
    3. Run it - the context metrics SHOULD score low because the
       retrieved context (bug process) is irrelevant to the question (CI/CD tools)
    4. Then fix it by using [DOC_TOOLS] and see the scores improve

    This teaches you to catch retriever quality issues.

    Uncomment and fill in:
    """
    # # Version 1: BAD retrieval (should score low on context metrics)
    # bad_retrieval = LLMTestCase(
    #     input="What CI/CD tool do we use?",
    #     actual_output="???",
    #     expected_output="GitHub Actions for pipeline, Jenkins for legacy projects.",
    #     retrieval_context=[DOC_BUG_PROCESS]  # Wrong doc!
    # )
    #
    # # Version 2: GOOD retrieval (should score high)
    # good_retrieval = LLMTestCase(
    #     input="What CI/CD tool do we use?",
    #     actual_output="???",
    #     expected_output="GitHub Actions for pipeline, Jenkins for legacy projects.",
    #     retrieval_context=[DOC_TOOLS]  # Correct doc!
    # )
    #
    # context_relevancy = ContextualRelevancyMetric(threshold=0.7, model="gpt-4o-mini")
    #
    # # Run both and compare the scores
    # print("BAD retrieval score:")
    # assert_test(bad_retrieval, [context_relevancy])
    #
    # print("GOOD retrieval score:")
    # assert_test(good_retrieval, [context_relevancy])
    pass


def test_todo_build_custom_metric():
    """
    TODO Exercise B (Custom Metric):
    Build a custom GEval metric that checks if the answer uses
    professional QA terminology.

    Steps:
    1. Create a GEval metric with:
       - name: "QA Terminology"
       - criteria: define what "professional QA terminology" means
         (e.g., uses terms like "test case", "regression", "severity",
          "smoke test", "code coverage" appropriately)
       - evaluation_params: ["input", "actual_output"]
    2. Test it against two outputs:
       - Professional: "The P1 regression bug requires a hotfix within 24 hours
         and a smoke test in pre-prod before release."
       - Casual: "There's a big bug and we should fix it fast and test it."
    3. The professional version should score higher

    Uncomment and fill in:
    """
    # qa_terminology_metric = GEval(
    #     name="QA Terminology",
    #     criteria="???",  # Define what professional QA language looks like
    #     evaluation_params=["input", "actual_output"],
    #     threshold=0.7,
    #     model="gpt-4o-mini"
    # )
    #
    # professional_case = LLMTestCase(
    #     input="How should we handle this regression bug?",
    #     actual_output="???"  # Write a professional QA response
    # )
    #
    # casual_case = LLMTestCase(
    #     input="How should we handle this regression bug?",
    #     actual_output="???"  # Write a casual, non-professional response
    # )
    #
    # assert_test(professional_case, [qa_terminology_metric])
    # assert_test(casual_case, [qa_terminology_metric])  # This should fail
    pass


# ============================================================
# HOW TO RUN
# ============================================================
#
# Full suite:
#   deepeval test run exercises/02_advanced_rag_evaluation.py
#
# Single test:
#   deepeval test run exercises/02_advanced_rag_evaluation.py::test_rag_multi_metric
#
# With verbose output:
#   deepeval test run exercises/02_advanced_rag_evaluation.py -v
#
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Exercise 2: Advanced RAG Pipeline Evaluation")
    print("=" * 60)
    print()
    print("This exercise covers:")
    print("  1. Multi-metric RAG evaluation (4 quality dimensions)")
    print("  2. Golden dataset batch evaluation (5 test cases)")
    print("  3. Quality gate pattern for CI/CD")
    print("  4. TODO: Catching bad retrieval with context metrics")
    print("  5. TODO: Building custom GEval metrics")
    print()
    print("Run with: deepeval test run exercises/02_advanced_rag_evaluation.py -v")
