"""
Exercise 1 (Basic): Your First LLM Evaluation
================================================

Goal: Learn how to evaluate an LLM response for correctness, relevancy,
and hallucination using DeepEval's built-in metrics.

Scenario:
    You are a QA engineer testing a customer support chatbot.
    The chatbot answers questions about a fictional e-commerce return policy.
    Your job is to write evaluation tests that check if the chatbot:
    1. Gives answers that are relevant to the question asked
    2. Does not hallucinate (make up facts not in the context)
    3. Produces answers that match the expected ground truth

What you will learn:
    - How to install and set up DeepEval
    - How to create test cases with input, actual_output, and expected_output
    - How to use AnswerRelevancyMetric, HallucinationMetric, and CorrectnessMetric
    - How to interpret evaluation scores (0 to 1 scale)
    - How to run evaluations and read the results

Setup:
    pip install deepeval openai
    export OPENAI_API_KEY=your_key_here

Instructions:
    1. Read through the code below
    2. Fill in the TODO sections
    3. Run: deepeval test run exercises/01_basic_llm_evaluation.py
    4. Check the scores - aim for > 0.8 on each metric
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    HallucinationMetric,
    GEval,
)

# ============================================================
# CONTEXT: This is the "source of truth" the chatbot should use.
# Think of it as the knowledge base or documentation.
# ============================================================

RETURN_POLICY = """
Return Policy for ShopEasy:
1. Items can be returned within 30 days of purchase.
2. Items must be in original packaging and unused condition.
3. Refunds are processed within 5-7 business days after receiving the item.
4. Electronics have a 15-day return window instead of 30 days.
5. Sale items are final sale and cannot be returned.
6. Free return shipping is available for orders over $50.
7. Gift cards and downloadable software are non-refundable.
"""

# ============================================================
# TEST CASE 1: Basic relevancy check
# Does the chatbot answer the question that was asked?
# ============================================================

def test_answer_relevancy():
    """
    Test that the chatbot's answer is relevant to the user's question.
    A relevant answer directly addresses what was asked.
    An irrelevant answer talks about something else entirely.
    """

    test_case = LLMTestCase(
        input="How many days do I have to return an item?",
        actual_output="You have 30 days to return most items. Electronics have a shorter 15-day return window.",
        retrieval_context=[RETURN_POLICY]
    )

    metric = AnswerRelevancyMetric(
        threshold=0.7,  # Score must be >= 0.7 to pass
        model="gpt-4o-mini"
    )

    assert_test(test_case, [metric])


# ============================================================
# TEST CASE 2: Hallucination check
# Does the chatbot make up facts NOT in the context?
# ============================================================

def test_no_hallucination():
    """
    Test that the chatbot does not hallucinate.
    A hallucination is when the LLM states something as fact
    that is NOT supported by the provided context.

    Example hallucination: "Returns are accepted within 60 days"
    (The policy says 30 days, not 60)
    """

    test_case = LLMTestCase(
        input="What is the return policy for electronics?",
        actual_output="Electronics can be returned within 15 days of purchase. They must be in original packaging and unused condition.",
        retrieval_context=[RETURN_POLICY]
    )

    metric = HallucinationMetric(
        threshold=0.5,  # Lower score = less hallucination (this metric is inverted)
        model="gpt-4o-mini"
    )

    assert_test(test_case, [metric])


# ============================================================
# TEST CASE 3: Correctness check
# Does the answer match the expected "ground truth" output?
# ============================================================

def test_answer_correctness():
    """
    Test that the chatbot's answer matches the expected correct answer.
    This uses GEval (a general-purpose LLM evaluator) to compare
    the actual output against the expected output.
    """

    test_case = LLMTestCase(
        input="Can I return a sale item?",
        actual_output="Unfortunately, sale items are final sale and cannot be returned or exchanged.",
        expected_output="Sale items are final sale and cannot be returned."
    )

    correctness_metric = GEval(
        name="Correctness",
        criteria="Determine whether the actual output is factually correct based on the expected output.",
        evaluation_params=[
            "input",
            "actual_output",
            "expected_output"
        ],
        threshold=0.7,
        model="gpt-4o-mini"
    )

    assert_test(test_case, [correctness_metric])


# ============================================================
# TODO EXERCISES - Fill these in yourself!
# ============================================================

def test_todo_refund_timeline():
    """
    TODO Exercise A:
    Write a test case that checks if the chatbot correctly answers:
    "How long does it take to get my refund?"

    Expected: The chatbot should say 5-7 business days.

    Steps:
    1. Create an LLMTestCase with:
       - input: the question above
       - actual_output: write a realistic chatbot response
       - expected_output: the correct answer from the policy
       - retrieval_context: [RETURN_POLICY]
    2. Use AnswerRelevancyMetric with threshold=0.7
    3. Run and check if it passes

    Uncomment and fill in below:
    """
    # test_case = LLMTestCase(
    #     input="How long does it take to get my refund?",
    #     actual_output="???",  # Write a realistic chatbot answer
    #     expected_output="Refunds are processed within 5-7 business days after receiving the item.",
    #     retrieval_context=[RETURN_POLICY]
    # )
    #
    # metric = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")
    # assert_test(test_case, [metric])
    pass


def test_todo_catch_hallucination():
    """
    TODO Exercise B:
    Write a test case where the chatbot HALLUCINATES.
    The goal is to see what a FAILING hallucination test looks like.

    Steps:
    1. Create an LLMTestCase where actual_output contains
       made-up information NOT in the return policy
       (e.g., "You can return items within 90 days" or
        "We offer store credit for all returns")
    2. Use HallucinationMetric
    3. Run it - this test SHOULD FAIL (that's the point!)
    4. Read the failure output to understand how DeepEval reports it

    Uncomment and fill in below:
    """
    # test_case = LLMTestCase(
    #     input="What is the return policy?",
    #     actual_output="???",  # Write a response with FAKE information
    #     retrieval_context=[RETURN_POLICY]
    # )
    #
    # metric = HallucinationMetric(threshold=0.5, model="gpt-4o-mini")
    # assert_test(test_case, [metric])
    pass


# ============================================================
# HOW TO RUN THIS FILE
# ============================================================
#
# Option 1 - DeepEval CLI:
#   deepeval test run exercises/01_basic_llm_evaluation.py
#
# Option 2 - Pytest:
#   pytest exercises/01_basic_llm_evaluation.py -v
#
# Option 3 - Direct Python (for debugging):
#   python exercises/01_basic_llm_evaluation.py
#
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Exercise 1: Basic LLM Evaluation")
    print("=" * 60)
    print()
    print("Run this file with DeepEval or Pytest:")
    print("  deepeval test run exercises/01_basic_llm_evaluation.py")
    print("  pytest exercises/01_basic_llm_evaluation.py -v")
    print()
    print("This exercise has 3 working tests and 2 TODO exercises.")
    print("Fill in the TODO functions to practice writing your own evaluations.")
