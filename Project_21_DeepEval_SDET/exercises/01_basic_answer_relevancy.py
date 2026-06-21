"""
Exercise 1 (Basic): Answer Relevancy & Hallucination Detection
================================================================

Level: BASIC
Time: ~20 minutes
Prereqs: Groq API key, DeepEval installed

Goal:
    Learn the two most fundamental LLM evaluation metrics:
    1. Answer Relevancy  — Does the chatbot answer the question asked?
    2. Hallucination      — Does the chatbot make up facts not in the context?

Setup:
    export GROQ_API_KEY=your_key_here
    export OPENAI_API_KEY=your_key_here   # DeepEval uses this for judging
    cd chatbot && uvicorn app:app --port 8100

Run:
    deepeval test run exercises/01_basic_answer_relevancy.py -v
"""

import sys
import requests
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, HallucinationMetric, GEval

CHATBOT_URL = "http://localhost:8100/chat"


def ask_chatbot(question: str) -> dict:
    """Send a question to the chatbot and get the response + context."""
    try:
        response = requests.post(CHATBOT_URL, json={"message": question}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.ConnectionError:
        print("\nERROR: Chatbot not running!  cd chatbot && uvicorn app:app --port 8100\n")
        sys.exit(1)


# ─── TEST 1: Answer Relevancy ──────────────────────────────

def test_refund_policy_relevancy():
    """Ask about refund policy. The chatbot should give a relevant answer."""
    result = ask_chatbot("What is your refund policy?")
    test_case = LLMTestCase(
        input="What is your refund policy?",
        actual_output=result["reply"],
        retrieval_context=result["retrieval_context"],
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")])


def test_shipping_time_relevancy():
    """Ask about shipping time. Answer should mention delivery timeframes."""
    result = ask_chatbot("How long does shipping take?")
    test_case = LLMTestCase(
        input="How long does shipping take?",
        actual_output=result["reply"],
        retrieval_context=result["retrieval_context"],
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")])


def test_subscription_cancel_relevancy():
    """Ask how to cancel subscription."""
    result = ask_chatbot("How do I cancel my subscription?")
    test_case = LLMTestCase(
        input="How do I cancel my subscription?",
        actual_output=result["reply"],
        retrieval_context=result["retrieval_context"],
    )
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")])


# ─── TEST 2: Hallucination ──────────────────────────────────

def test_refund_no_hallucination():
    """The chatbot should NOT hallucinate about the refund policy."""
    result = ask_chatbot("How many days do I have to return electronics?")
    test_case = LLMTestCase(
        input="How many days do I have to return electronics?",
        actual_output=result["reply"],
        retrieval_context=result["retrieval_context"],
    )
    assert_test(test_case, [HallucinationMetric(threshold=0.5, model="gpt-4o-mini")])


def test_shipping_no_hallucination():
    """Ask about express shipping cost."""
    result = ask_chatbot("How much does express shipping cost?")
    test_case = LLMTestCase(
        input="How much does express shipping cost?",
        actual_output=result["reply"],
        retrieval_context=result["retrieval_context"],
    )
    assert_test(test_case, [HallucinationMetric(threshold=0.5, model="gpt-4o-mini")])


# ─── TEST 3: Correctness with GEval ────────────────────────

def test_refund_timeline_correctness():
    """Use GEval to check if the answer is factually correct."""
    result = ask_chatbot("How long does a refund take to process?")
    test_case = LLMTestCase(
        input="How long does a refund take to process?",
        actual_output=result["reply"],
        expected_output="Refunds are processed within 5-7 business days after receiving the returned item.",
    )
    correctness = GEval(
        name="Correctness",
        criteria="The actual output must state that refunds take 5-7 business days.",
        evaluation_params=["input", "actual_output", "expected_output"],
        threshold=0.7,
        model="gpt-4o-mini",
    )
    assert_test(test_case, [correctness])


# ─── TODO EXERCISE ─────────────────────────────────────────

def test_todo_sale_items_relevancy():
    """
    TODO: Write a test for the question "Can I return sale items?"
    Expected answer: Sale items are final sale and cannot be returned.
    """
    # YOUR CODE HERE
    pass


if __name__ == "__main__":
    print("Exercise 1 (Basic): Answer Relevancy & Hallucination")
    print("Run: deepeval test run exercises/01_basic_answer_relevancy.py -v")
