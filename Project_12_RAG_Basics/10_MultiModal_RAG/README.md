# 10. Multi-Modal RAG

## Overview

Multi-Modal RAG extends retrieval beyond text to include images, tables, diagrams, charts, and even audio/video. For QA engineers, this is critical because test evidence often includes screenshots, log files, architecture diagrams, and performance charts.

---

## Strategies for Multi-Modal RAG

| Strategy | How It Works | Best For |
|---|---|---|
| Text Extraction | Convert images/tables to text, then standard RAG | Screenshots with text, simple tables |
| Multi-Vector | Store text summaries + original media, retrieve summaries, return media | Complex diagrams, charts |
| Multi-Modal Embeddings | Embed images and text in same vector space (CLIP) | Image-text similarity search |
| Vision LLM | Use GPT-4V/Claude to describe images, index descriptions | Complex visual content |

### Architecture Diagram

```
┌───────────────── MULTI-MODAL INDEXING ──────────────────┐
│                                                          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐              │
│  │  Text   │    │ Images  │    │ Tables  │              │
│  └────┬────┘    └────┬────┘    └────┬────┘              │
│       ↓              ↓              ↓                    │
│  [Text        [Vision LLM     [Table                    │
│   Splitter]    Summarizer]     Parser]                  │
│       ↓              ↓              ↓                    │
│  [Text         [Image          [Table                   │
│   Embeddings]   Summaries]      Summaries]              │
│       └──────────────┼──────────────┘                    │
│                      ↓                                   │
│              [Unified Vector Store]                      │
│                                                          │
│  [Original Content] → [Byte Store (for retrieval)]       │
└──────────────────────────────────────────────────────────┘

┌───────────────── MULTI-MODAL RETRIEVAL ─────────────────┐
│                                                          │
│  [Query] → [Search Vector Store (summaries)]             │
│                      ↓                                   │
│         [Retrieve Original Content (images/tables)]      │
│                      ↓                                   │
│  [Multi-Modal LLM (GPT-4o)] → [Response with visuals]   │
└──────────────────────────────────────────────────────────┘
```

---

## Python Implementation

### Strategy 1: Multi-Vector Retrieval

```python
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryByteStore
from langchain_openai import ChatOpenAI
import base64, uuid

# Use Vision LLM to summarize images and tables
vision_llm = ChatOpenAI(model="gpt-4o", temperature=0)

def summarize_image(image_base64: str) -> str:
    """Use Vision LLM to create a text summary of an image"""
    response = vision_llm.invoke([{
        "type": "image_url",
        "image_url": {"url": f"data:image/png;base64,{image_base64}"}
    }, {
        "type": "text",
        "text": "Describe this image in detail for a QA engineer. "
               "Include any visible error messages, UI elements, and test results."
    }])
    return response.content

# Create multi-vector store
byte_store = InMemoryByteStore()
id_key = "doc_id"

multi_retriever = MultiVectorRetriever(
    vectorstore=vectorstore,
    byte_store=byte_store,
    id_key=id_key
)

# Index: store summaries in vector store, originals in byte store
for img_path in image_paths:
    img_base64 = encode_image(img_path)
    summary = summarize_image(img_base64)
    doc_id = str(uuid.uuid4())

    # Summary goes to vector store for retrieval
    multi_retriever.vectorstore.add_documents(
        [Document(page_content=summary, metadata={id_key: doc_id})]
    )
    # Original image goes to byte store for return
    multi_retriever.docstore.mset([(doc_id, img_base64)])
```

### Strategy 2: Unstructured.io for Complex Documents

```python
from unstructured.partition.pdf import partition_pdf

# Extract text, tables, and images from complex PDFs
elements = partition_pdf(
    filename="test_report.pdf",
    extract_images_in_pdf=True,
    strategy="hi_res",  # Uses layout detection models
    infer_table_structure=True
)

# Separate by element type
texts = [e for e in elements if e.category == "NarrativeText"]
tables = [e for e in elements if e.category == "Table"]
images = [e for e in elements if e.category == "Image"]

# Summarize each type and create unified index
for table in tables:
    summary = llm.invoke(f"Summarize this table: {table.text}")
    # Index summary, store original table HTML
```


---

## 🧪 QA Testing Points for Multi-Modal RAG

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Image summarization accuracy | Does the Vision LLM correctly describe error screenshots? |
| 2 | Table extraction from PDFs | Are numbers and columns preserved? |
| 3 | Mixed queries | Queries needing both text and image context |
| 4 | Original content return | Verify images are returned, not just summaries |
| 5 | Low-quality inputs | Test with low-quality screenshots and scanned documents |

---

**Next:** [Contextual RAG →](../11_Contextual_RAG/)
