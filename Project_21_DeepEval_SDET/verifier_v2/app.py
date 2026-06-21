"""
DeepEval Metric Verifier V2 — Educational Mode
==============================================
A guided walkthrough of every DeepEval metric, one lesson at a time, with
good/bad sample pairs, editable inputs, and live scoring.

Run:
    cd verifier_v2
    OPENAI_API_KEY=... uvicorn app:app --reload --port 5181 --loop asyncio

Then open: http://localhost:5181
"""

import os
import time
import traceback
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests

from metric_lessons import LESSONS, LESSONS_BY_ID, LESSONS_BY_CATEGORY

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


app = FastAPI(title="DeepEval Verifier V2 — Educational Mode", version="2.0.0")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

CHATBOT_URL = os.environ.get("CHATBOT_URL", "http://localhost:8100/chat")
CHATBOT_HEALTH_URL = os.environ.get("CHATBOT_HEALTH_URL", "http://localhost:8100/health")


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


class ScoreRequest(BaseModel):
    metric: str
    query: str
    actual_output: str
    expected_output: str = ""
    retrieval_context: list = []
    threshold: float = 0.7
    model: str = "gpt-4o-mini"


class ChatbotRequest(BaseModel):
    message: str


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {
        "lessons_by_category": LESSONS_BY_CATEGORY,
        "total": len(LESSONS),
    })


@app.get("/lesson/{lesson_id}", response_class=HTMLResponse)
async def lesson_page(request: Request, lesson_id: str):
    lesson = LESSONS_BY_ID.get(lesson_id)
    if not lesson:
        return HTMLResponse("Lesson not found", status_code=404)
    idx = next(i for i, l in enumerate(LESSONS) if l["id"] == lesson_id)
    prev_l = LESSONS[idx - 1] if idx > 0 else None
    next_l = LESSONS[idx + 1] if idx + 1 < len(LESSONS) else None
    return templates.TemplateResponse(request, "lesson.html", {
        "lesson": lesson,
        "lessons": LESSONS,
        "current_index": idx,
        "total": len(LESSONS),
        "prev_lesson": prev_l,
        "next_lesson": next_l,
    })


@app.post("/api/score")
async def score(req: ScoreRequest):
    start = time.time()
    try:
        kwargs = {"input": req.query, "actual_output": req.actual_output}
        if req.expected_output:
            kwargs["expected_output"] = req.expected_output
        if req.retrieval_context:
            kwargs["retrieval_context"] = req.retrieval_context

        # HallucinationMetric in DeepEval uses 'context' (ground truth), not retrieval_context
        if req.metric == "hallucination" and req.retrieval_context:
            kwargs["context"] = req.retrieval_context

        test_case = LLMTestCase(**kwargs)
        metric = create_metric(req.metric, req.threshold, req.model)
        metric.measure(test_case)

        elapsed = round(time.time() - start, 2)
        score_val = round(metric.score, 4) if metric.score is not None else None

        # Hallucination, Bias, Toxicity: higher = worse, so "passed" means score <= threshold
        inverse_metrics = {"hallucination", "bias", "toxicity"}
        if req.metric in inverse_metrics and score_val is not None:
            passed = score_val <= req.threshold
        else:
            passed = score_val >= req.threshold if score_val is not None else False

        return {
            "success": True,
            "metric": req.metric,
            "score": score_val,
            "threshold": req.threshold,
            "passed": passed,
            "inverse": req.metric in inverse_metrics,
            "reason": metric.reason if hasattr(metric, "reason") else None,
            "elapsed_seconds": elapsed,
        }
    except Exception as e:
        return {
            "success": False,
            "metric": req.metric,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "elapsed_seconds": round(time.time() - start, 2),
        }


@app.post("/api/chatbot")
async def query_chatbot(req: ChatbotRequest):
    try:
        resp = requests.post(CHATBOT_URL, json={"message": req.message}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return {"success": True, "reply": data["reply"], "sources": data.get("sources", []), "retrieval_context": data.get("retrieval_context", [])}
    except requests.ConnectionError:
        return {"success": False, "error": "Chatbot not running on port 8100."}
    except Exception as e:
        return {"success": False, "error": str(e)}


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
        "version": "2.0.0",
        "chatbot_connected": chatbot_ok,
        "openai_key_set": bool(os.environ.get("OPENAI_API_KEY")),
        "lessons": len(LESSONS),
        "port": 5181,
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("  DeepEval Verifier V2 — Educational Mode")
    print("  http://localhost:5181")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=5181, loop="asyncio")
