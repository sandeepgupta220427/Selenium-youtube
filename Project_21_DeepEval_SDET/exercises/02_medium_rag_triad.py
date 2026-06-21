"""
Exercise 2 (Medium): The RAG Triad
====================================

Level: MEDIUM
Time: ~30 minutes

Goal:
    Learn the RAG Triad:
    1. Context Relevancy  (Question -> Retrieved Context)
    2. Faithfulness       (Context -> Answer)
    3. Answer Relevancy   (Question -> Answer)

Setup:
    cd chatbot && uvicorn app:app --port 8100
    export GROQ_API_KEY=...  && export OPENAI_API_KEY=...

Run:
    deepeval test run exercises/02_medium_rag_triad.py -v
"""

import sys
import requests
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    GEval,
)

CHATBOT_URL = "http://localhost:8100/chat"


def ask_chatbot(question: str) -> dict:
    try:
        resp = requests.post(CHATBOT_URL, json={"message": question}, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        print("\nERROR: Chatbot not running!  cd chatbot && uvicorn app:app --port 8100\n")
        sys.exit(1)


# ─── PART 1: The RAG Triad ───────────────────────────────

def test_rag_triad_refund_question():
    """Test all three edges of the RAG Triad."""
    result = ask_chatbot("How long do I have to return an item?")
    test_case = LLMTestCase(
        input="How long do I have to return an item?",
        actual_output=result["reply"],
        expected_output="Standard items can be returned within 30 days. Electronics have a 15-day return window.",
        retrieval_context=result["retrieval_context"],
    )
    assert_test(test_case, [
        ContextualRelevancyMetric(threshold=0.7, model="gpt-4o-mini"),
        FaithfulnessMetric(threshold=0.7, model="gpt-4o-mini"),
        AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini"),
    ])


# ─── PART 2: Context Precision & Recall ──────────────────

def test_context_precision_shipping():
    result = ask_chatbot("What are the express shipping options?")
    test_case = LLMTestCase(
        input="What are the express shipping options?",
        actual_output=result["reply"],
        expected_output="Express shipping takes 2-3 business days and costs $9.99 flat rate.",
        retrieval_context=result["retrieval_context"],
    )
    assert_test(test_case, [ContextualPrecisionMetric(threshold=0.7, model="gpt-4o-mini")])


def test_context_recall_subscription():
    result = ask_chatbot("What subscription plans do you offer and how much do they cost?")
    test_case = LLMTestCase(
        input="What subscription plans do you offer and how much do they cost?",
        actual_output=result["reply"],
        expected_output="Free tier, Plus at $9.99/month, Premium at $19.99/month.",
        retrieval_context=result["retrieval_context"],
    )
    assert_test(test_case, [ContextualRecallMetric(threshold=0.7, model="gpt-4o-mini")])


# ─── PART 3: Golden Dataset ──────────────────────────────

GOLDEN_DATASET = [
    {"input": "What is the return window for electronics?", "expected": "15-day return window."},
    {"input": "Can I return sale items?", "expected": "Sale items are final sale."},
    {"input": "How do I cancel my subscription?", "expected": "Account > Billing > Cancel Subscription."},
    {"input": "How much does express shipping cost?", "expected": "$9.99 flat rate, 2-3 business days."},
    {"input": "Do you ship internationally?", "expected": "45 countries, 10-21 business days."},
    {"input": "What payment methods do you accept?", "expected": "Visa, Mastercard, Amex, PayPal, Apple Pay, Google Pay."},
    {"input": "How do I track my order?", "expected": "shopEasy.com/track, mobile app, or text TRACK to 55123."},
    {"input": "What happens if my package is lost?", "expected": "Contact support within 48 hours."},
]


@pytest.mark.parametrize("row", GOLDEN_DATASET, ids=[r["input"][:40] for r in GOLDEN_DATASET])
def test_golden_dataset(row):
    """Run each golden dataset entry through the RAG Triad."""
    result = ask_chatbot(row["input"])
    test_case = LLMTestCase(
        input=row["input"],
        actual_output=result["reply"],
        expected_output=row["expected"],
        retrieval_context=result["retrieval_context"],
    )
    assert_test(test_case, [
        AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini"),
        FaithfulnessMetric(threshold=0.7, model="gpt-4o-mini"),
        ContextualRecallMetric(threshold=0.7, model="gpt-4o-mini"),
    ])


# ─── PART 4: Tone with GEval ─────────────────────────────

def test_chatbot_tone():
    result = ask_chatbot("My order hasn't arrived and I'm frustrated!")
    test_case = LLMTestCase(
        input="My order hasn't arrived and I'm frustrated!",
        actual_output=result["reply"],
    )
    tone_metric = GEval(
        name="Support Tone",
        criteria="The response should be warm, empathetic, and professional. Acknowledge the customer's frustration.",
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.7,
        model="gpt-4o-mini",
    )
    assert_test(test_case, [tone_metric])


# ─── TODO ────────────────────────────────────────────────

def test_todo_diagnose_bad_retrieval():
    """TODO: Diagnose retrieval failure for 'What is your phone support number?'"""
    pass


if __name__ == "__main__":
    print("Exercise 2: RAG Triad")
    print("Run: deepeval test run exercises/02_medium_rag_triad.py -v")
