"""
Metric definitions with simple line-diagram flows for the /metrics page.
Each metric has: what it measures, inputs needed, flow diagram, and pass/fail signals.
"""

METRICS_INFO = {
    "faithfulness": {
        "name": "Faithfulness",
        "icon": "&#x1F441;",
        "category": "Answer Quality",
        "color": "green",
        "one_line": "Did the LLM stick to the facts in the retrieved context?",
        "range": "0.0 to 1.0 (higher is better)",
        "threshold": "0.7+",
        "inputs": ["input (query)", "actual_output (LLM reply)", "retrieval_context (docs)"],
        "diagram": [
            {"node": "Retrieval Context", "color": "blue"},
            {"arrow": "grounded in"},
            {"node": "LLM Output", "color": "purple"},
            {"arrow": "scored by"},
            {"node": "Judge LLM", "color": "green"},
            {"arrow": "produces"},
            {"node": "Score 0-1", "color": "accent"},
        ],
        "pass_signals": ["Every claim in output traces back to context", "No invented facts"],
        "fail_signals": ["LLM made up numbers, dates, policies", "Claims contradicted by context"],
        "use_case": "Core metric for RAG chatbots. Catches hallucinations.",
        "code_example": '''from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase

metric = FaithfulnessMetric(threshold=0.7, model="gpt-4o-mini")
test_case = LLMTestCase(
    input="What is your return policy?",
    actual_output=chatbot_reply,
    retrieval_context=retrieved_docs,
)
metric.measure(test_case)
print(metric.score, metric.reason)''',
    },

    "answer_relevancy": {
        "name": "Answer Relevancy",
        "icon": "&#x1F3AF;",
        "category": "Answer Quality",
        "color": "green",
        "one_line": "Did the output directly answer the question that was asked?",
        "range": "0.0 to 1.0 (higher is better)",
        "threshold": "0.7+",
        "inputs": ["input (query)", "actual_output (LLM reply)"],
        "diagram": [
            {"node": "User Query", "color": "accent"},
            {"arrow": "addressed by"},
            {"node": "LLM Output", "color": "purple"},
            {"arrow": "scored by"},
            {"node": "Judge LLM", "color": "green"},
            {"arrow": "produces"},
            {"node": "Score 0-1", "color": "accent"},
        ],
        "pass_signals": ["Output directly addresses the query", "Focused, on-topic answer"],
        "fail_signals": ["Generic evasive response", "Answers a different question", "Off-topic info"],
        "use_case": "Catches when the LLM refuses to answer or goes off-topic.",
        "code_example": '''from deepeval.metrics import AnswerRelevancyMetric

metric = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini")
metric.measure(test_case)''',
    },

    "hallucination": {
        "name": "Hallucination",
        "icon": "&#x1F47B;",
        "category": "Answer Quality",
        "color": "green",
        "one_line": "Did the LLM fabricate information not in the context?",
        "range": "0.0 to 1.0 (LOWER is better)",
        "threshold": "&lt; 0.5",
        "inputs": ["input (query)", "actual_output", "context (list of docs)"],
        "diagram": [
            {"node": "Context", "color": "blue"},
            {"arrow": "checked against"},
            {"node": "LLM Output", "color": "purple"},
            {"arrow": "scored by"},
            {"node": "Judge LLM", "color": "green"},
            {"arrow": "flags made-up info"},
            {"node": "Score 0-1", "color": "red"},
        ],
        "pass_signals": ["All claims supported by context", "No invented details"],
        "fail_signals": ["Made-up phone numbers, names, facts", "Unsupported specific claims"],
        "use_case": "Critical for production LLMs. Complements Faithfulness.",
        "code_example": '''from deepeval.metrics import HallucinationMetric

metric = HallucinationMetric(threshold=0.5, model="gpt-4o-mini")
# Lower score is better for this one
metric.measure(test_case)''',
    },

    "contextual_precision": {
        "name": "Contextual Precision",
        "icon": "&#x1F3AF;",
        "category": "Context Quality",
        "color": "blue",
        "one_line": "Are the RELEVANT retrieved chunks ranked higher than irrelevant ones?",
        "range": "0.0 to 1.0 (higher is better)",
        "threshold": "0.7+",
        "inputs": ["input (query)", "expected_output", "retrieval_context (ordered list)"],
        "diagram": [
            {"node": "Query", "color": "accent"},
            {"arrow": "retrieves"},
            {"node": "Ranked Chunks", "color": "blue"},
            {"arrow": "ranking scored"},
            {"node": "Judge LLM", "color": "green"},
            {"arrow": "produces"},
            {"node": "Precision Score", "color": "accent"},
        ],
        "pass_signals": ["Most relevant chunks at top", "Reranker is working"],
        "fail_signals": ["Irrelevant chunks at top positions", "Bad reranking"],
        "use_case": "Tunes your reranker / retrieval ordering.",
        "code_example": '''from deepeval.metrics import ContextualPrecisionMetric

metric = ContextualPrecisionMetric(threshold=0.7, model="gpt-4o-mini")
# Requires expected_output
metric.measure(test_case)''',
    },

    "contextual_recall": {
        "name": "Contextual Recall",
        "icon": "&#x1F4E5;",
        "category": "Context Quality",
        "color": "blue",
        "one_line": "Did the retriever fetch ALL the chunks needed to answer fully?",
        "range": "0.0 to 1.0 (higher is better)",
        "threshold": "0.7+",
        "inputs": ["input (query)", "expected_output", "retrieval_context"],
        "diagram": [
            {"node": "Expected Answer", "color": "accent"},
            {"arrow": "requires"},
            {"node": "All Relevant Docs", "color": "blue"},
            {"arrow": "vs retrieved"},
            {"node": "Judge LLM", "color": "green"},
            {"arrow": "produces"},
            {"node": "Recall Score", "color": "accent"},
        ],
        "pass_signals": ["All needed info was retrieved", "Complete answer possible"],
        "fail_signals": ["Missing docs, incomplete answer", "Chunking too aggressive"],
        "use_case": "Detects retrieval gaps. Tune chunk size and top-k.",
        "code_example": '''from deepeval.metrics import ContextualRecallMetric

metric = ContextualRecallMetric(threshold=0.7, model="gpt-4o-mini")
metric.measure(test_case)''',
    },

    "contextual_relevancy": {
        "name": "Contextual Relevancy",
        "icon": "&#x1F50D;",
        "category": "Context Quality",
        "color": "blue",
        "one_line": "Is the retrieved context actually relevant to the query?",
        "range": "0.0 to 1.0 (higher is better)",
        "threshold": "0.7+",
        "inputs": ["input (query)", "retrieval_context"],
        "diagram": [
            {"node": "Query", "color": "accent"},
            {"arrow": "matched to"},
            {"node": "Retrieved Context", "color": "blue"},
            {"arrow": "scored by"},
            {"node": "Judge LLM", "color": "green"},
            {"arrow": "produces"},
            {"node": "Relevancy Score", "color": "accent"},
        ],
        "pass_signals": ["Context clearly addresses query topic"],
        "fail_signals": ["Retrieved wrong topic docs", "Embedding similarity too loose"],
        "use_case": "Diagnoses retriever quality in RAG Triad.",
        "code_example": '''from deepeval.metrics import ContextualRelevancyMetric

metric = ContextualRelevancyMetric(threshold=0.7, model="gpt-4o-mini")
metric.measure(test_case)''',
    },

    "bias": {
        "name": "Bias",
        "icon": "&#x2696;",
        "category": "Safety",
        "color": "red",
        "one_line": "Does the output show gender, racial, political, or religious bias?",
        "range": "0.0 to 1.0 (LOWER is better)",
        "threshold": "&lt; 0.5",
        "inputs": ["input (query)", "actual_output"],
        "diagram": [
            {"node": "LLM Output", "color": "purple"},
            {"arrow": "analyzed for"},
            {"node": "Bias Patterns", "color": "red"},
            {"arrow": "detected by"},
            {"node": "Judge LLM", "color": "green"},
            {"arrow": "produces"},
            {"node": "Bias Score", "color": "red"},
        ],
        "pass_signals": ["Neutral, inclusive language", "No stereotyping"],
        "fail_signals": ["Gendered assumptions", "Cultural stereotyping", "Political lean"],
        "use_case": "Production safety gate. Required for consumer apps.",
        "code_example": '''from deepeval.metrics import BiasMetric

metric = BiasMetric(threshold=0.5, model="gpt-4o-mini")
metric.measure(test_case)''',
    },

    "toxicity": {
        "name": "Toxicity",
        "icon": "&#x2620;",
        "category": "Safety",
        "color": "red",
        "one_line": "Does the output contain toxic, harmful, or offensive language?",
        "range": "0.0 to 1.0 (LOWER is better)",
        "threshold": "&lt; 0.5",
        "inputs": ["input (query)", "actual_output"],
        "diagram": [
            {"node": "LLM Output", "color": "purple"},
            {"arrow": "screened for"},
            {"node": "Toxic Content", "color": "red"},
            {"arrow": "detected by"},
            {"node": "Judge LLM", "color": "green"},
            {"arrow": "produces"},
            {"node": "Toxicity Score", "color": "red"},
        ],
        "pass_signals": ["Professional tone, no slurs", "Empathetic under pressure"],
        "fail_signals": ["Mirrors user hostility", "Offensive language", "Aggressive tone"],
        "use_case": "Block toxic outputs before they reach the user.",
        "code_example": '''from deepeval.metrics import ToxicityMetric

metric = ToxicityMetric(threshold=0.5, model="gpt-4o-mini")
metric.measure(test_case)''',
    },

    "completeness": {
        "name": "Completeness (GEval)",
        "icon": "&#x2705;",
        "category": "Presentation",
        "color": "purple",
        "one_line": "Are ALL expected facts present in the output?",
        "range": "0.0 to 1.0 (higher is better)",
        "threshold": "0.7+",
        "inputs": ["input", "actual_output", "expected_output"],
        "diagram": [
            {"node": "Expected Facts", "color": "accent"},
            {"arrow": "checked in"},
            {"node": "LLM Output", "color": "purple"},
            {"arrow": "scored by"},
            {"node": "Judge LLM", "color": "green"},
            {"arrow": "produces"},
            {"node": "Completeness Score", "color": "purple"},
        ],
        "pass_signals": ["All key facts, numbers, steps present"],
        "fail_signals": ["Missing prices, dates, conditions", "Partial answer"],
        "use_case": "When the answer must include every field (e.g., product specs).",
        "code_example": '''from deepeval.metrics import GEval

metric = GEval(
    name="Completeness",
    criteria="Output must contain ALL key information from expected output.",
    evaluation_params=["input", "actual_output", "expected_output"],
    threshold=0.7, model="gpt-4o-mini",
)''',
    },
}
