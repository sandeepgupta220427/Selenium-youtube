from deepeval.test_case import LLMTestCase
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric,HallucinationMetric,ExactMatchMetric
import pytest

def test_hello_world_deepeval():
    test = LLMTestCase(
        name="test_hello_world_deepeval",
        input="Hello World",
        expected_output="Hello World",
        actual_output="Hello World",
        context=["Hello World is a common starting program."],
        retrieval_context=["Hello World is a common starting program."]
    )

    metric = [
        AnswerRelevancyMetric(threshold=0.5),
        HallucinationMetric(threshold=0.5),
        ExactMatchMetric(threshold=0.5)
    ]

    assert_test(test, metric)