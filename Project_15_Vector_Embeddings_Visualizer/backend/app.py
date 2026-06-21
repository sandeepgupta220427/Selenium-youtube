from __future__ import annotations

import hashlib
import json
import math
import os
import random
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"

ProviderId = Literal["demo", "ollama", "openai", "mistral"]
DEFAULT_MODELS = {
    "demo": "hashed-demo-96d",
    "ollama": "nomic-embed-text",
    "openai": "text-embedding-3-small",
    "mistral": "mistral-embed",
}

app = FastAPI(title="Vector Embeddings Visualizer", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VisualizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=30000)
    provider: ProviderId = "demo"
    model: str | None = None
    chunk_size: int = Field(default=70, ge=20, le=260)
    overlap: int = Field(default=18, ge=0, le=120)
    max_chunks: int = Field(default=10, ge=1, le=24)


class ProviderConfig(BaseModel):
    id: ProviderId
    label: str
    description: str
    default_model: str
    available: bool
    hint: str


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/providers")
def providers() -> dict:
    return {
        "providers": [provider.model_dump() for provider in get_provider_configs()],
        "default_provider": get_default_provider(),
    }


@app.post("/api/visualize")
def visualize(payload: VisualizeRequest) -> dict:
    text = normalize_text(payload.text)
    if not text:
        raise HTTPException(status_code=400, detail="Please provide some text to visualize.")

    if payload.overlap >= payload.chunk_size:
        raise HTTPException(status_code=400, detail="Overlap must be smaller than chunk size.")

    chunks = chunk_text(text, payload.chunk_size, payload.overlap, payload.max_chunks)
    if not chunks:
        raise HTTPException(status_code=400, detail="Unable to create chunks from the provided text.")

    model = (payload.model or DEFAULT_MODELS[payload.provider]).strip()
    all_texts = [text, *[chunk["text"] for chunk in chunks]]

    try:
        embeddings = embed_texts(payload.provider, model, all_texts)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if len(embeddings) != len(all_texts):
        raise HTTPException(status_code=500, detail="Embedding provider returned an unexpected number of vectors.")

    document_embedding = embeddings[0]
    chunk_embeddings = embeddings[1:]
    similarities = cosine_similarity_matrix(chunk_embeddings)
    projected_points = random_projection_points(chunk_embeddings)

    response_chunks = []
    for chunk, embedding, point in zip(chunks, chunk_embeddings, projected_points, strict=True):
        response_chunks.append(
            {
                **chunk,
                "dimension": len(embedding),
                "vector_norm": round(vector_norm(embedding), 4),
                "embedding_head": rounded_list(embedding[:16]),
                "sparkline": rounded_list(bucketize(embedding, buckets=28)),
                "projection": point,
            }
        )

    summary = {
        "provider": payload.provider,
        "model": model,
        "input_characters": len(text),
        "input_words": len(re.findall(r"\S+", text)),
        "chunk_count": len(response_chunks),
        "embedding_dimension": len(document_embedding),
        "document_vector_norm": round(vector_norm(document_embedding), 4),
        "document_embedding_head": rounded_list(document_embedding[:16]),
        "document_sparkline": rounded_list(bucketize(document_embedding, buckets=36)),
        "avg_chunk_words": round(sum(chunk["word_count"] for chunk in response_chunks) / len(response_chunks), 1),
    }

    return {
        "summary": summary,
        "chunking": {
            "strategy": "sliding-word-window",
            "chunk_size_words": payload.chunk_size,
            "overlap_words": payload.overlap,
            "step_words": payload.chunk_size - payload.overlap,
        },
        "chunks": response_chunks,
        "similarity_matrix": [[round(value, 4) for value in row] for row in similarities],
        "projection": {
            "label": "2D teaching projection",
            "description": "A stable random projection that compresses high-dimensional vectors into a 2D teaching view.",
            "points": projected_points,
        },
        "teaching_points": [
            "Chunking splits a longer document into smaller windows so each vector captures a tighter slice of meaning.",
            "Each embedding is a list of numbers. Nearby vectors usually mean semantically similar chunks.",
            "The heatmap uses cosine similarity, which compares the angle between vectors rather than raw length.",
            "The 2D chart is only a teaching projection. The real embedding still lives in a much higher-dimensional space.",
        ],
    }


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


def get_provider_configs() -> list[ProviderConfig]:
    return [
        ProviderConfig(
            id="demo",
            label="Deterministic Demo",
            description="No API key needed. Great for teaching chunking and vector mechanics.",
            default_model=DEFAULT_MODELS["demo"],
            available=True,
            hint="Uses a stable hashed vector, not a cloud embedding provider.",
        ),
        ProviderConfig(
            id="ollama",
            label="Ollama / Nomic",
            description="Free local embeddings through Ollama. Recommended for workshops.",
            default_model=DEFAULT_MODELS["ollama"],
            available=True,
            hint=f"Start Ollama and pull `{DEFAULT_MODELS['ollama']}`.",
        ),
        ProviderConfig(
            id="openai",
            label="OpenAI",
            description="Cloud embeddings with strong defaults for semantic search demos.",
            default_model=DEFAULT_MODELS["openai"],
            available=bool(os.getenv("OPENAI_API_KEY")),
            hint="Set OPENAI_API_KEY to enable this provider.",
        ),
        ProviderConfig(
            id="mistral",
            label="Mistral",
            description="Cloud embeddings via the Mistral embeddings endpoint.",
            default_model=DEFAULT_MODELS["mistral"],
            available=bool(os.getenv("MISTRAL_API_KEY")),
            hint="Set MISTRAL_API_KEY to enable this provider.",
        ),
    ]


def get_default_provider() -> ProviderId:
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("MISTRAL_API_KEY"):
        return "mistral"
    return "demo"


def normalize_text(text: str) -> str:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def chunk_text(text: str, chunk_size: int, overlap: int, max_chunks: int) -> list[dict]:
    words = re.findall(r"\S+", text)
    if not words:
        return []

    step = max(1, chunk_size - overlap)
    chunks: list[dict] = []

    for index, start in enumerate(range(0, len(words), step), start=1):
        end = min(len(words), start + chunk_size)
        chunk_words = words[start:end]
        chunk_text_value = " ".join(chunk_words)
        chunks.append(
            {
                "id": index,
                "text": chunk_text_value,
                "word_start": start + 1,
                "word_end": end,
                "word_count": len(chunk_words),
                "character_count": len(chunk_text_value),
            }
        )
        if end >= len(words) or len(chunks) >= max_chunks:
            break

    return chunks


def embed_texts(provider: ProviderId, model: str, texts: list[str]) -> list[list[float]]:
    if provider == "demo":
        return [demo_embedding(text) for text in texts]
    if provider == "ollama":
        return embed_with_ollama(model, texts)
    if provider == "openai":
        return embed_with_openai(model, texts)
    if provider == "mistral":
        return embed_with_mistral(model, texts)
    raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")


def embed_with_ollama(model: str, texts: list[str]) -> list[list[float]]:
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    try:
        response = post_json(
            f"{base_url}/api/embed",
            {"model": model, "input": texts},
            headers={},
            timeout=60,
        )
        embeddings = response.get("embeddings")
        if not embeddings:
            raise ValueError("Ollama returned no embeddings.")
        return embeddings
    except HTTPException as exc:
        if exc.status_code != 404:
            raise
    except ValueError:
        raise
    except Exception:
        pass

    embeddings = []
    for text in texts:
        response = post_json(
            f"{base_url}/api/embeddings",
            {"model": model, "prompt": text},
            headers={},
            timeout=60,
        )
        vector = response.get("embedding")
        if not vector:
            raise HTTPException(status_code=502, detail="Ollama did not return an embedding vector.")
        embeddings.append(vector)
    return embeddings


def embed_with_openai(model: str, texts: list[str]) -> list[list[float]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not set.")

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/")
    response = post_json(
        f"{base_url}/v1/embeddings",
        {"model": model, "input": texts},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=60,
    )
    data = response.get("data", [])
    if not data:
        raise HTTPException(status_code=502, detail="OpenAI returned no embedding data.")
    return [item["embedding"] for item in data]


def embed_with_mistral(model: str, texts: list[str]) -> list[list[float]]:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="MISTRAL_API_KEY is not set.")

    base_url = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai").rstrip("/")
    response = post_json(
        f"{base_url}/v1/embeddings",
        {"model": model, "input": texts},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=60,
    )
    data = response.get("data", [])
    if not data:
        raise HTTPException(status_code=502, detail="Mistral returned no embedding data.")
    return [item["embedding"] for item in data]


def post_json(url: str, payload: dict, headers: dict[str, str], timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise HTTPException(status_code=exc.code, detail=detail or f"HTTP error while calling {url}") from exc
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=502, detail=f"Unable to reach {url}: {exc.reason}") from exc


def demo_embedding(text: str, dimension: int = 96) -> list[float]:
    vector = [0.0] * dimension
    tokens = re.findall(r"[A-Za-z0-9_'-]+", text.lower())
    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for offset in range(0, 24, 4):
            index = int.from_bytes(digest[offset : offset + 2], "big") % dimension
            sign = 1.0 if digest[offset + 2] % 2 == 0 else -1.0
            weight = 0.35 + (digest[offset + 3] / 255.0)
            vector[index] += sign * weight

    for trigram in character_ngrams(text.lower(), size=3):
        digest = hashlib.md5(trigram.encode("utf-8")).digest()  # noqa: S324
        index = int.from_bytes(digest[:2], "big") % dimension
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        vector[index] += sign * 0.12

    norm = vector_norm(vector)
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def character_ngrams(text: str, size: int) -> list[str]:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) < size:
        return [compact] if compact else []
    return [compact[index : index + size] for index in range(len(compact) - size + 1)]


def vector_norm(vector: list[float]) -> float:
    return math.sqrt(sum(value * value for value in vector))


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    denom = vector_norm(vector_a) * vector_norm(vector_b)
    if denom == 0:
        return 0.0
    return sum(a * b for a, b in zip(vector_a, vector_b, strict=True)) / denom


def cosine_similarity_matrix(vectors: list[list[float]]) -> list[list[float]]:
    matrix = []
    for row_vector in vectors:
        row = []
        for column_vector in vectors:
            row.append(cosine_similarity(row_vector, column_vector))
        matrix.append(row)
    return matrix


def bucketize(vector: list[float], buckets: int) -> list[float]:
    if not vector:
        return []
    size = max(1, math.ceil(len(vector) / buckets))
    values = []
    for index in range(0, len(vector), size):
        segment = vector[index : index + size]
        values.append(sum(segment) / len(segment))
    return values[:buckets]


def rounded_list(values: list[float]) -> list[float]:
    return [round(value, 4) for value in values]


def random_projection_points(vectors: list[list[float]]) -> list[dict]:
    if not vectors:
        return []

    dimension = len(vectors[0])
    randomizer = random.Random(42)
    weights_x = [randomizer.uniform(-1.0, 1.0) for _ in range(dimension)]
    weights_y = [randomizer.uniform(-1.0, 1.0) for _ in range(dimension)]

    raw_points = []
    for index, vector in enumerate(vectors, start=1):
        x_value = sum(value * weight for value, weight in zip(vector, weights_x, strict=True))
        y_value = sum(value * weight for value, weight in zip(vector, weights_y, strict=True))
        raw_points.append({"id": index, "x": x_value, "y": y_value})

    min_x = min(point["x"] for point in raw_points)
    max_x = max(point["x"] for point in raw_points)
    min_y = min(point["y"] for point in raw_points)
    max_y = max(point["y"] for point in raw_points)

    x_span = max(max_x - min_x, 1e-9)
    y_span = max(max_y - min_y, 1e-9)

    normalized = []
    for point in raw_points:
        normalized.append(
            {
                "id": point["id"],
                "x": round(12 + ((point["x"] - min_x) / x_span) * 76, 2),
                "y": round(12 + ((point["y"] - min_y) / y_span) * 76, 2),
            }
        )
    return normalized
