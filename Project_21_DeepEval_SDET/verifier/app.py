"""
DeepEval Metric Verifier — Local Web App
==========================================
A local web application to manually verify DeepEval metric scores.
Connects to the ShopEasy chatbot (port 8100) and runs DeepEval metrics.

Run:
    cd verifier
    pip install -r requirements.txt
    uvicorn app:app --reload --port 5180

Then open: http://localhost:5180
"""

import os
import json
import time
import traceback
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests

from samples import SAMPLES, ALL_SAMPLES
from metrics_info import METRICS_INFO
from integrations_info import INTEGRATIONS

# DeepEval imports
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
    BiasMetric,
    ToxicityMetric,
    GEval,
)

# ─── App Setup ───────────────────────────────────────────────

app = FastAPI(title="DeepEval Metric Verifier", version="1.0.0")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

CHATBOT_URL = os.environ.get("CHATBOT_URL", "http://localhost:8100/chat")
CHATBOT_HEALTH_URL = os.environ.get("CHATBOT_HEALTH_URL", "http://localhost:8100/health")

AVAILABLE_METRICS = [
    {"id": "faithfulness", "name": "Faithfulness", "category": "Answer Quality", "needs_context": True, "needs_expected": False, "description": "Did the LLM stick to the source context?"},
    {"id": "answer_relevancy", "name": "Answer Relevancy", "category": "Answer Quality", "needs_context": True, "needs_expected": False, "description": "Did the answer address what was asked?"},
    {"id": "hallucination", "name": "Hallucination", "category": "Answer Quality", "needs_context": True, "needs_expected": False, "description": "Did the LLM make up facts not in context?"},
    {"id": "contextual_precision", "name": "Contextual Precision", "category": "Context Quality", "needs_context": True, "needs_expected": True, "description": "Are relevant chunks ranked higher?"},
    {"id": "contextual_recall", "name": "Contextual Recall", "category": "Context Quality", "needs_context": True, "needs_expected": True, "description": "Did we retrieve everything needed?"},
    {"id": "contextual_relevancy", "name": "Contextual Relevancy", "category": "Context Quality", "needs_context": True, "needs_expected": False, "description": "Is the retrieved context relevant to the query?"},
    {"id": "bias", "name": "Bias", "category": "Safety", "needs_context": False, "needs_expected": False, "description": "Does the output contain bias?"},
    {"id": "toxicity", "name": "Toxicity", "category": "Safety", "needs_context": False, "needs_expected": False, "description": "Does the output contain toxic content?"},
    {"id": "completeness", "name": "Completeness (GEval)", "category": "Presentation", "needs_context": False, "needs_expected": True, "description": "Are all expected parts present?"},
]


class EvaluateRequest(BaseModel):
    metric: str
    query: str
    actual_output: str
    expected_output: str = ""
    retrieval_context: list = []
    threshold: float = 0.7
    model: str = "gpt-4o-mini"


class ChatbotRequest(BaseModel):
    message: str


def create_metric(metric_id: str, threshold: float, model: str):
    metric_map = {
        "faithfulness": lambda: FaithfulnessMetric(threshold=threshold, model=model),
        "answer_relevancy": lambda: AnswerRelevancyMetric(threshold=threshold, model=model),
        "hallucination": lambda: HallucinationMetric(threshold=threshold, model=model),
        "contextual_precision": lambda: ContextualPrecisionMetric(threshold=threshold, model=model),
        "contextual_recall": lambda: ContextualRecallMetric(threshold=threshold, model=model),
        "contextual_relevancy": lambda: ContextualRelevancyMetric(threshold=threshold, model=model),
        "bias": lambda: BiasMetric(threshold=threshold, model=model),
        "toxicity": lambda: ToxicityMetric(threshold=threshold, model=model),
        "completeness": lambda: GEval(
            name="Completeness",
            criteria="The actual output must contain ALL key information from the expected output.",
            evaluation_params=["input", "actual_output", "expected_output"],
            threshold=threshold,
            model=model,
        ),
    }
    factory = metric_map.get(metric_id)
    if not factory:
        raise ValueError(f"Unknown metric: {metric_id}")
    return factory()


# ─── Routes ──────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"metrics": AVAILABLE_METRICS})


@app.get("/samples", response_class=HTMLResponse)
async def samples_page(request: Request):
    return templates.TemplateResponse(request, "samples.html", {"categories": SAMPLES})


@app.get("/samples/{category}", response_class=HTMLResponse)
async def samples_category_page(request: Request, category: str):
    if category not in SAMPLES:
        return templates.TemplateResponse(request, "samples.html", {"categories": SAMPLES})
    return templates.TemplateResponse(request, "sample_detail.html", {
        "category_id": category, "category": SAMPLES[category], "categories": SAMPLES,
    })


@app.get("/metrics", response_class=HTMLResponse)
async def metrics_page(request: Request):
    return templates.TemplateResponse(request, "metrics.html", {"metrics": METRICS_INFO})


@app.get("/integrations", response_class=HTMLResponse)
async def integrations_page(request: Request):
    return templates.TemplateResponse(request, "integrations.html", {"integrations": INTEGRATIONS})


@app.get("/api/metrics")
async def get_metrics():
    return {"metrics": AVAILABLE_METRICS}


@app.post("/api/chatbot")
async def query_chatbot(req: ChatbotRequest):
    try:
        resp = requests.post(CHATBOT_URL, json={"message": req.message}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return {"success": True, "reply": data["reply"], "sources": data.get("sources", []), "retrieval_context": data.get("retrieval_context", [])}
    except requests.ConnectionError:
        return {"success": False, "error": "Chatbot not running. Start: cd chatbot && uvicorn app:app --port 8100"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/evaluate")
async def evaluate_metric(req: EvaluateRequest):
    start_time = time.time()
    try:
        kwargs = {"input": req.query, "actual_output": req.actual_output}
        if req.expected_output:
            kwargs["expected_output"] = req.expected_output
        if req.retrieval_context:
            kwargs["retrieval_context"] = req.retrieval_context

        test_case = LLMTestCase(**kwargs)
        metric = create_metric(req.metric, req.threshold, req.model)
        metric.measure(test_case)

        elapsed = round(time.time() - start_time, 2)
        return {
            "success": True, "metric": req.metric,
            "score": round(metric.score, 4) if metric.score is not None else None,
            "threshold": req.threshold,
            "passed": metric.score >= req.threshold if metric.score is not None else False,
            "reason": metric.reason if hasattr(metric, "reason") else None,
            "elapsed_seconds": elapsed,
        }
    except Exception as e:
        return {
            "success": False, "metric": req.metric,
            "error": str(e), "traceback": traceback.format_exc(),
            "elapsed_seconds": round(time.time() - start_time, 2),
        }


@app.post("/api/evaluate-multi")
async def evaluate_multi(req: dict):
    metrics_to_run = req.get("metrics", [])
    results = []
    for mid in metrics_to_run:
        er = EvaluateRequest(
            metric=mid, query=req.get("query", ""),
            actual_output=req.get("actual_output", ""),
            expected_output=req.get("expected_output", ""),
            retrieval_context=req.get("retrieval_context", []),
            threshold=req.get("threshold", 0.7), model=req.get("model", "gpt-4o-mini"),
        )
        results.append(await evaluate_metric(er))
    passed = sum(1 for r in results if r.get("passed"))
    return {
        "success": True, "results": results,
        "summary": {"total": len(results), "passed": passed, "failed": len(results) - passed, "all_passed": passed == len(results)},
    }


@app.get("/health")
async def health():
    chatbot_ok = False
    try:
        resp = requests.get(CHATBOT_HEALTH_URL, timeout=5)
        chatbot_ok = resp.status_code == 200
    except Exception:
        pass
    return {
        "status": "healthy",
        "chatbot_connected": chatbot_ok,
        "chatbot_url": CHATBOT_URL,
        "openai_key_set": bool(os.environ.get("OPENAI_API_KEY")),
        "verifier_port": 5180,
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("  DeepEval Metric Verifier")
    print("  http://localhost:5180")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=5180)
