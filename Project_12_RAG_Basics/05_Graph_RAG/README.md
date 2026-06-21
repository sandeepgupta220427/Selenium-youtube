# 5. Graph RAG

## Overview

Graph RAG replaces or augments the traditional vector store with a knowledge graph. Instead of just finding semantically similar text chunks, it traverses relationships between entities to perform multi-hop reasoning. This is especially powerful for complex domains where relationships matter — like understanding how a bug in module A affects test coverage in module B.

---

## How It Differs from Vector RAG

| Aspect | Vector RAG | Graph RAG |
|---|---|---|
| Storage | Embeddings in vector DB | Entities & relations in graph DB |
| Retrieval | Cosine similarity search | Graph traversal + community detection |
| Reasoning | Single-hop (find similar text) | Multi-hop (follow relationships) |
| Best For | Factual Q&A, search | Relationship queries, causal analysis |
| Example Query | "What is API rate limiting?" | "Which services depend on the auth module?" |

### Architecture Diagram

```
┌──────────────── GRAPH CONSTRUCTION ─────────────────┐
│                                                      │
│  [Documents] → [LLM Entity Extraction] → [Entities] │
│                                           [Relations]│
│                         ↓                            │
│              [Knowledge Graph (Neo4j)]               │
│                                                      │
│  Example:                                            │
│    (AuthService) --[DEPENDS_ON]-→ (Database)         │
│    (LoginTest)   --[COVERS]-→     (AuthService)      │
│    (PaymentAPI)  --[CALLS]-→      (AuthService)      │
└──────────────────────────────────────────────────────┘

┌──────────────── GRAPH RETRIEVAL ────────────────────┐
│                                                      │
│  [User Query] → [Cypher Query Generation]            │
│                         ↓                            │
│              [Graph Traversal]                       │
│                         ↓                            │
│         [Community Detection (Leiden)]               │
│                         ↓                            │
│              [Relevant Subgraph]                     │
│                         ↓                            │
│              [LLM Generation]                        │
└──────────────────────────────────────────────────────┘
```

---

## Python Implementation

### Using Microsoft's GraphRAG

```bash
# Install GraphRAG
pip install graphrag

# Initialize a GraphRAG project
graphrag init --root ./my_graph_project

# Place your documents in ./my_graph_project/input/
# Edit settings.yaml to configure LLM and embedding models
```

### Building a Knowledge Graph with LangChain + Neo4j

```python
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI

# Connect to Neo4j
graph = Neo4jGraph(
    url="bolt://localhost:7687",
    username="neo4j",
    password="your_password"
)

# Transform documents into graph
llm = ChatOpenAI(model="gpt-4o", temperature=0)
transformer = LLMGraphTransformer(llm=llm)

# Extract entities and relationships
graph_documents = transformer.convert_to_graph_documents(documents)
graph.add_graph_documents(graph_documents)

# Query the graph
from langchain.chains import GraphCypherQAChain
chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True
)

result = chain.invoke({"query": "Which test suites cover the payment module?"})
```

### Community Detection for Summarization

```bash
# GraphRAG uses community detection (Leiden algorithm)
# to group related entities and create hierarchical summaries

# Global search: queries across all community summaries
graphrag query --root ./my_graph_project \
    --method global \
    --query "What are the main testing challenges across all modules?"

# Local search: focused on specific entities
graphrag query --root ./my_graph_project \
    --method local \
    --query "What tests are needed for the authentication service?"
```


---

## 🧪 QA Testing Points for Graph RAG

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Entity extraction accuracy | Are the right entities and relationships captured? |
| 2 | Cypher query generation | Does the LLM produce valid graph queries? |
| 3 | Circular dependencies | Test with circular relationships in your graph |
| 4 | Global vs. local search | Compare results for the same query |
| 5 | Graph construction cost | Measure time and API costs (significantly higher than vector RAG) |

---

**Next:** [Agentic RAG →](../06_Agentic_RAG/)
