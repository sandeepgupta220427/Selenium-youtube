# 11. Contextual RAG (Anthropic's Approach)

## Overview

Contextual RAG, introduced by Anthropic, solves a fundamental problem with chunking: when you split a document into pieces, each chunk loses the context of where it came from. Contextual RAG uses an LLM to prepend chunk-specific context to each chunk BEFORE embedding it. This dramatically improves retrieval accuracy.

---

## The Problem It Solves

Consider this chunk from a test plan:

> *"The timeout should be set to 30 seconds for this endpoint."*

Without context, which endpoint? Which service?

**With Contextual RAG**, the chunk becomes:

> *"This chunk is from the Payment Service API Test Plan, Section 3.2: Timeout Configuration for the /api/v2/payments/process endpoint. The timeout should be set to 30 seconds for this endpoint."*

### Before vs. After

```
┌─────────────── WITHOUT Context ──────────────────┐
│                                                   │
│  Chunk: "The timeout should be set to 30 seconds  │
│          for this endpoint."                      │
│                                                   │
│  ❌ Which endpoint?                                │
│  ❌ Which service?                                 │
│  ❌ Which test plan?                               │
└───────────────────────────────────────────────────┘

┌─────────────── WITH Context (Contextual RAG) ────┐
│                                                   │
│  Context: "From Payment Service API Test Plan,    │
│            Section 3.2: Timeout Configuration     │
│            for /api/v2/payments/process endpoint." │
│                                                   │
│  Chunk: "The timeout should be set to 30 seconds  │
│          for this endpoint."                      │
│                                                   │
│  ✅ Clear: Payment Service                         │
│  ✅ Clear: /api/v2/payments/process                │
│  ✅ Clear: Section 3.2 of the test plan            │
└───────────────────────────────────────────────────┘
```

---

## Python Implementation

### Context Generation

```python
from langchain_openai import ChatOpenAI
from langchain.schema import Document

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

CONTEXT_PROMPT = """Here is the full document:
<document>
{document}
</document>

Here is a chunk from that document:
<chunk>
{chunk}
</chunk>

Please provide a short, concise context (2-3 sentences) that explains:
1. What document/section this chunk belongs to
2. What the chunk is specifically about
3. Key entities or identifiers mentioned

Context:"""

def add_context_to_chunks(full_document: str, chunks: list) -> list:
    """Add contextual information to each chunk before embedding"""
    contextualized_chunks = []

    for chunk in chunks:
        # Generate context using the LLM
        context = llm.invoke(
            CONTEXT_PROMPT.format(
                document=full_document[:4000],  # Truncate if needed
                chunk=chunk.page_content
            )
        ).content

        # Prepend context to the chunk
        enriched_content = f"{context}\n\n{chunk.page_content}"
        contextualized_chunks.append(
            Document(
                page_content=enriched_content,
                metadata={**chunk.metadata, "original_content": chunk.page_content}
            )
        )

    return contextualized_chunks

# Usage
contextualized = add_context_to_chunks(full_doc_text, chunks)

# Now embed and store the contextualized chunks
vectorstore = Chroma.from_documents(
    documents=contextualized,
    embedding=embeddings
)
```

### Combining Contextual RAG with Hybrid Search

```python
# Anthropic's research shows best results with:
# Contextual Embeddings + Contextual BM25 + Reranking

# Step 1: Contextualize chunks (as above)
ctx_chunks = add_context_to_chunks(full_doc, chunks)

# Step 2: Create both retrievers with contextualized chunks
ctx_bm25 = BM25Retriever.from_documents(ctx_chunks, k=20)
ctx_vector = Chroma.from_documents(ctx_chunks, embeddings).as_retriever(
    search_kwargs={"k": 20}
)

# Step 3: Hybrid retrieval
hybrid = EnsembleRetriever(
    retrievers=[ctx_bm25, ctx_vector],
    weights=[0.4, 0.6]
)

# Step 4: Rerank
final_retriever = ContextualCompressionRetriever(
    base_compressor=CohereRerank(top_n=5),
    base_retriever=hybrid
)

# This combination reduced retrieval failures by 67%
# in Anthropic's benchmarks
```


---

## 🧪 QA Testing Points for Contextual RAG

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Retrieval accuracy comparison | With vs. without contextual enrichment |
| 2 | Context generation quality | Is the prepended context accurate? |
| 3 | Indexing cost | Each chunk requires 1 LLM call during indexing |
| 4 | Similar sections disambiguation | Multiple API endpoints with similar descriptions |
| 5 | Context hallucination | Verify context generation doesn't hallucinate metadata |

> **📊 Benchmark:** Anthropic's research showed Contextual RAG + Hybrid Search + Reranking reduced retrieval failures by **67%** compared to standard approaches.

---

**Next:** [RAG Evaluation & Testing →](../12_RAG_Evaluation/)
