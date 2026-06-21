# 12. Learning Path & Next Steps

## Recommended Learning Order

### 🟢 Beginner (Week 1–2)

| Step | Topic | What You'll Learn |
|---|---|---|
| 1 | [LangFlow Quick-Start](../Project_11_LangFlow/01_LangFlow_QuickStart/) | Setting up LangFlow, understanding components |
| 2 | [Naive RAG Flow](./02_Naive_RAG_Flow/) | The foundational RAG pipeline |
| 3 | [RAG Basics: Introduction](../Project_12_RAG_Basics/01_Introduction_to_RAG.md) | Core theory behind RAG |
| 4 | Build your own Naive RAG | Upload your QA docs and test queries |

### 🟡 Intermediate (Week 3–4)

| Step | Topic | What You'll Learn |
|---|---|---|
| 5 | [Advanced RAG Flow](./03_Advanced_RAG_Flow/) | Re-ranking, HyDE, semantic chunking |
| 6 | [Hybrid RAG Flow](./09_Hybrid_RAG_Flow/) | BM25 + Vector search combination |
| 7 | [Modular RAG Flow](./04_Modular_RAG_Flow/) | Query routing, plug-and-play components |
| 8 | [Corrective RAG Flow](./08_Corrective_RAG_Flow/) | Document grading, web search fallback |

### 🔴 Advanced (Week 5–6)

| Step | Topic | What You'll Learn |
|---|---|---|
| 9 | [Agentic RAG Flow](./06_Agentic_RAG_Flow/) | Multi-tool agents, dynamic retrieval |
| 10 | [Self-RAG Flow](./07_Self_RAG_Flow/) | Reflection loops, groundedness checking |
| 11 | [Graph RAG Flow](./05_Graph_RAG_Flow/) | Knowledge graphs, entity relationships |
| 12 | [Contextual RAG Flow](./11_Contextual_RAG_Flow/) | Anthropic's enrichment approach |
| 13 | [Multi-Modal RAG Flow](./10_MultiModal_RAG_Flow/) | Images, tables, and mixed content |

### 🏆 Capstone (Week 7)

Build a complete RAG evaluation pipeline:
1. Create a knowledge base from your QA team's test documentation
2. Implement **3 different RAG types** using LangFlow flows
3. Create a test suite with **50+ test queries**
4. Evaluate each implementation using RAGAS metrics
5. Report: Which RAG type works best for your domain?

---

## RAG Type Decision Guide

```
Is your query about exact identifiers (IDs, error codes)?
  → Yes → Hybrid RAG (BM25 + Vector)
  → No ↓

Does your question require multi-hop reasoning?
  → Yes → Graph RAG
  → No ↓

Do you need to search multiple knowledge bases?
  → Yes → Agentic RAG or Modular RAG
  → No ↓

Is your knowledge base potentially outdated/incomplete?
  → Yes → Corrective RAG (CRAG)
  → No ↓

Do you need high-confidence, grounded answers?
  → Yes → Self-RAG (with reflection)
  → No ↓

Are your documents losing context when chunked?
  → Yes → Contextual RAG
  → No ↓

Do your docs contain images/tables/diagrams?
  → Yes → Multi-Modal RAG
  → No → Start with Naive or Advanced RAG
```

---

## Tool Comparison

| Feature | LangFlow | n8n |
|---|---|---|
| **Best For** | RAG prototyping & experimentation | Production workflows & integrations |
| **RAG Components** | Full LangChain component library | AI Agent + Vector Store nodes |
| **Learning Curve** | Low (drag-and-drop) | Low (visual workflow builder) |
| **Customization** | Custom Python components | Custom JavaScript/Python functions |
| **Deployment** | API endpoint per flow | Webhook endpoints, scheduled runs |
| **Integrations** | LangChain ecosystem | 350+ app integrations (Slack, Jira, etc.) |
| **Use Case** | "Test this RAG pipeline" | "Connect RAG to my Slack/Jira/CI" |

### When to Use Which

- **LangFlow:** When you're experimenting with different RAG architectures, comparing retrieval strategies, or teaching RAG concepts visually.
- **n8n:** When you're building production integrations (e.g., RAG bot in Slack, automated test report analysis, CI/CD pipeline with AI).
- **Both:** Use LangFlow to prototype → Export the best approach → Rebuild in n8n for production with integrations.

---

## Resources

- **LangFlow Docs:** [https://docs.langflow.org](https://docs.langflow.org)
- **n8n Docs:** [https://docs.n8n.io](https://docs.n8n.io)
- **RAGAS Framework:** [https://docs.ragas.io](https://docs.ragas.io)
- **LangChain Docs:** [https://python.langchain.com](https://python.langchain.com)
- **RAG Basics (Theory):** [Project 12](../Project_12_RAG_Basics/)

---

**The Testing Academy — Building the Next Generation of AI-Powered QA Engineers**
