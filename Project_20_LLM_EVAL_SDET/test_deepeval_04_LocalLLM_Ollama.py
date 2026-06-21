from deepeval.test_case import LLMTestCase
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric,HallucinationMetric,ExactMatchMetric

from deepeval import evaluate
import requests
from deepeval.models import DeepEvalBaseLLM


class LocalLlama(DeepEvalBaseLLM):
    def __init__(self):
        super().__init__()

    def load_model(self):
        return None
        

    def generate(self, prompt: str) -> str:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:1b",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        return response.json()["response"]
    
    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self):
        return "gemma3:1b"


local_llm = LocalLlama()

user_question = "What is REST API?"
model_answer = local_llm.generate(user_question)

test_case = LLMTestCase(
    input=user_question,
    actual_output=model_answer,
    expected_output="REST API is an architectural style for web services.",
)

metric = AnswerRelevancyMetric(threshold=0.6)

evaluate(
    test_cases=[test_case],
    metrics=[metric]
)