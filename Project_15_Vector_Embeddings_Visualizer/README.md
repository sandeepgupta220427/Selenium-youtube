# Project 15: Vector Embeddings Visualizer

## Interactive Chunking + Embedding Playground for QA Engineers

This project is a small teaching application that shows how raw text becomes:

1. chunks
2. embeddings
3. similarity signals
4. a simple 2D vector-space projection

It is built for workshops and student demos where you want to explain embeddings visually instead of abstractly.

---

## What This Project Teaches

- How long text gets split into smaller chunks
- Why chunk overlap matters
- How each chunk becomes a vector embedding
- How cosine similarity compares chunk meaning
- Why a 2D projection is only a teaching view, not the real vector space

---

## Features

- Beautiful single-page HTML UI built for classroom demos
- FastAPI backend that serves the UI and embedding APIs from one app
- Provider support for:
  - `Deterministic Demo` (no API key needed)
  - `Ollama / Nomic` using `nomic-embed-text`
  - `OpenAI` using `text-embedding-3-small`
  - `Mistral` using `mistral-embed`
- Adjustable chunk size and overlap
- Chunk cards with vector previews
- Cosine similarity heatmap
- 2D projection map for chunk vectors
- QA-focused sample texts for instant demos

---

## Project Structure

```text
Project_15_Vector_Embeddings_Visualizer/
├── backend/
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   └── index.html
├── .env.example
├── start_app.sh
└── README.md
```

---

## Quick Start

### 1. Create a virtual environment

```bash
cd Project_15_Vector_Embeddings_Visualizer
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Configure a provider

You have 4 options.

#### Option A: Demo mode

No setup required.

#### Option B: Ollama + Nomic embeddings

```bash
ollama pull nomic-embed-text
```

Then start Ollama locally.

#### Option C: OpenAI embeddings

Set `OPENAI_API_KEY`.

#### Option D: Mistral embeddings

Set `MISTRAL_API_KEY`.

### 4. Run the app

```bash
./start_app.sh
```

Open:

```text
http://localhost:8001
```

---

## Environment Variables

See `.env.example`.

Important ones:

- `OLLAMA_BASE_URL=http://localhost:11434`
- `OPENAI_API_KEY=...`
- `OPENAI_BASE_URL=https://api.openai.com`
- `MISTRAL_API_KEY=...`
- `MISTRAL_BASE_URL=https://api.mistral.ai`

---

## How to Use It in Class

### Flow

1. Paste a story, PRD paragraph, or bug report
2. Pick a provider
3. Adjust chunk size and overlap
4. Click `Generate vectors`
5. Walk students through:
   - summary cards
   - chunk cards
   - similarity heatmap
   - 2D projection
   - selected chunk dimensions

### Suggested explanation

- Chunking breaks a long document into retrieval units.
- Each chunk becomes a vector of numbers.
- Similar chunks have closer vectors.
- The heatmap compares chunk-to-chunk similarity.
- The 2D plot is only a compressed teaching view of a much larger vector space.

---

## Provider Notes

### Ollama

Recommended for workshops because it is free and local.

Default model:

- `nomic-embed-text`

### OpenAI

Default model:

- `text-embedding-3-small`

### Mistral

Default model:

- `mistral-embed`

---

## Why the Demo Provider Exists

The demo provider uses a deterministic hashed vector instead of a hosted embedding API.

That means:

- the app still works without keys
- students can immediately understand chunking and vector comparison
- you can switch to a real provider later without changing the teaching flow

---

## API Endpoints

- `GET /api/health`
- `GET /api/providers`
- `POST /api/visualize`

Example payload:

```json
{
  "text": "As a user, I want to log in so I can access my dashboard.",
  "provider": "ollama",
  "model": "nomic-embed-text",
  "chunk_size": 70,
  "overlap": 18,
  "max_chunks": 10
}
```

---

## Teaching Angle for RAG

This project is a good bridge before full RAG because students can see:

- chunking before retrieval
- embeddings before vector databases
- similarity before semantic search

That makes Project 12 and Project 13 easier to teach afterwards.
