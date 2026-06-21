# 3. Advanced RAG

## Overview

Advanced RAG addresses the limitations of Naive RAG by adding optimization layers before retrieval (pre-retrieval), during retrieval, and after retrieval (post-retrieval). It's the natural evolution that significantly improves answer quality.

---

## Key Improvements Over Naive RAG

| Stage | Technique | Purpose |
|---|---|---|
| Pre-Retrieval | Query Rewriting / HyDE | Transform queries for better matching |
| Pre-Retrieval | Semantic Chunking | Intelligent document splitting |
| Retrieval | Sentence Window Retrieval | Retrieve surrounding context |
| Retrieval | Parent Document Retrieval | Return full parent when child matches |
| Post-Retrieval | Re-ranking (Cohere, BGE) | Reorder by relevance |
| Post-Retrieval | Compression | Remove irrelevant parts from chunks |

### Architecture Diagram

```
┌───────────── PRE-RETRIEVAL OPTIMIZATION ─────────────┐
│                                                       │
│  [User Query] → [Query Rewriting / HyDE]              │
│                      ↓                                │
│  [Documents] → [Semantic Chunking] → [Smart Embeddings] │
└───────────────────────────────────────────────────────┘
                         ↓
┌───────────── ENHANCED RETRIEVAL ─────────────────────┐
│                                                       │
│  [Rewritten Query] → [Parent Document Retriever]      │
│                     → [Sentence Window Retriever]     │
│                              ↓                        │
│                     [Over-fetch: Top 20 candidates]   │
└───────────────────────────────────────────────────────┘
                         ↓
┌───────────── POST-RETRIEVAL OPTIMIZATION ────────────┐
│                                                       │
│  [20 Candidates] → [Re-ranking (Cohere)] → [Top 4]   │
│                              ↓                        │
│                     [Compression / Filtering]         │
│                              ↓                        │
│                     [LLM Generation]                  │
└───────────────────────────────────────────────────────┘
```

---

## Python Implementation

### Query Rewriting with HyDE (Hypothetical Document Embedding)

```python
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Hypothetical Document Embedding (HyDE)
# Generate a hypothetical answer, then use IT for retrieval
hyde_prompt = ChatPromptTemplate.from_template(
    "Write a short passage that would answer: {question}"
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
hyde_chain = hyde_prompt | llm

# The hypothetical answer is closer in embedding space
# to real answers than the original question
hypothetical_doc = hyde_chain.invoke({"question": "How to test API rate limiting?"})
# Now embed this hypothetical doc and use it for retrieval
```

### Semantic Chunking

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

# Splits based on semantic similarity between sentences
semantic_splitter = SemanticChunker(
    embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95
)

semantic_chunks = semantic_splitter.split_documents(documents)
# Chunks now respect topic boundaries, not arbitrary token counts
```

### Re-ranking Retrieved Results

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

# Base retriever gets top 20 candidates
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 20})

# Cohere reranker selects the best 4
reranker = CohereRerank(model="rerank-english-v3.0", top_n=4)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=base_retriever
)

# Now retrieval returns re-ranked, high-quality results
results = compression_retriever.invoke("What are the edge cases for payment testing?")
```

### Parent Document Retrieval

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore

# Small chunks for precise matching, full docs for context
child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)

store = InMemoryStore()
parent_retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter
)
parent_retriever.add_documents(documents)
```


---

## 🧪 QA Testing Points for Advanced RAG

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Compare retrieval precision before/after reranking | Measure improvement with test queries |
| 2 | Test HyDE with ambiguous queries | Does it improve or degrade results? |
| 3 | Measure latency impact of re-ranking | Adds ~200–500ms |
| 4 | Semantic chunking edge cases | Test with code snippets, tables, and mixed-language content |
| 5 | Parent-child retrieval | Verify correct parent document is returned |

---

**Next:** [Modular RAG →](../04_Modular_RAG/)
