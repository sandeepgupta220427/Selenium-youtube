from deepeval.metrics import AnswerRelevancyMetric,HallucinationMetric,ExactMatchMetric
from deepeval.test_case import LLMTestCase
from deepeval import assert_test


def test_sum():

    test = LLMTestCase(
        name= "test_sum",
        input="What is 2+2",
        actual_output="4",
        context=["2+2=4"],
        expected_output="4"
    )

    metric = [
        AnswerRelevancyMetric(threshold=0.5),
        HallucinationMetric(threshold=0.5),
        ExactMatchMetric(threshold=0.5),
        ]

    assert_test(test, metric)