# 2. Naive (Basic) RAG

## Overview

Naive RAG is the simplest and most straightforward implementation of Retrieval-Augmented Generation. It follows the basic three-step process: Index, Retrieve, Generate — without any optimization or enhancement layers.

---

## Architecture

The Naive RAG pipeline works as follows:

1. **Document Loading:** Load documents from files (PDF, TXT, HTML, etc.)
2. **Chunking:** Split documents into fixed-size chunks (typically 500–1000 tokens) with overlap
3. **Embedding:** Convert each chunk into a vector using an embedding model
4. **Storage:** Store vectors in a vector database (ChromaDB, Pinecone, FAISS, etc.)
5. **Query Processing:** Embed the user's query using the same embedding model
6. **Retrieval:** Find top-k most similar chunks via cosine similarity
7. **Generation:** Pass retrieved chunks + query to the LLM for response generation

### Architecture Diagram

```
┌─────────────────────────────── INDEXING ────────────────────────────────┐
│                                                                         │
│  [PDF/TXT/HTML] → [Fixed-Size Chunking] → [Embedding Model] → [Vector DB] │
│                     (1000 tokens,           (text-embedding-3-small)      │
│                      200 overlap)                                        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────── RETRIEVAL ───────────────────────────────┐
│                                                                         │
│  [User Query] → [Embedding Model] → [Cosine Similarity Search] → [Top-K Chunks] │
│                                       (same model as indexing)           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────── GENERATION ──────────────────────────────┐
│                                                                         │
│  [Prompt: Query + Retrieved Chunks] → [LLM (GPT-4o-mini)] → [Response]  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Python Implementation

### Step 1: Install Dependencies

```bash
pip install langchain chromadb openai tiktoken
pip install langchain-community langchain-openai
pip install pypdf sentence-transformers
```

### Step 2: Document Loading & Chunking

```python
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load documents
loader = PyPDFLoader("test_documentation.pdf")
documents = loader.load()

# Chunk with overlap
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)
chunks = text_splitter.split_documents(documents)
print(f"Created {len(chunks)} chunks from {len(documents)} pages")
```

### Step 3: Embedding & Vector Store

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# Create embeddings and store
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# Create retriever (top 4 results)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
```

### Step 4: Query & Generate

```python
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

response = qa_chain.invoke({"query": "What are the login test cases?"})
print(response["result"])
print("Sources:", [doc.metadata for doc in response["source_documents"]])
```


---

## 🧪 QA Testing Points for Naive RAG

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Query with no relevant docs in the store | Check for hallucination |
| 2 | Query spanning multiple chunks | Verify context continuity |
| 3 | Duplicate documents | Check for redundant retrieval |
| 4 | Very long documents | Verify chunking doesn't split critical information |
| 5 | Embedding model changes | Ensure re-indexing happens correctly |

---

## Limitations of Naive RAG

- ❌ Fixed chunking can split important context across boundaries
- ❌ No query optimization — poorly phrased queries return poor results
- ❌ No re-ranking — retrieved chunks may not be the most relevant
- ❌ No self-correction — no mechanism to detect or fix hallucinations
- ❌ Single retrieval step — cannot handle multi-hop reasoning

---

**Next:** [Advanced RAG →](../03_Advanced_RAG/)
