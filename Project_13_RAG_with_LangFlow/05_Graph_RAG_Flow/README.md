# 5. Graph RAG — LangFlow Implementation

## Overview

Graph RAG augments plain retrieval with a **knowledge graph** made of entities and relationships. Instead of retrieving only similar chunks, it retrieves graph facts such as:

- `Login API -> depends_on -> Auth Service`
- `Checkout Flow -> writes_to -> Orders DB`
- `Recommendation Engine -> increases_load_on -> Redis Cache`

This is useful for **multi-hop reasoning**, dependency analysis, failure impact questions, and architecture-style QA prompts.

For this project, the Langflow version is implemented as a **practical custom-component Graph RAG** that works with Langflow 1.7.x. It does **not** depend on Neo4j-specific built-in nodes, because those are not part of the current installed Langflow stack in this project.

---

## 🟣 LangFlow Implementation: Practical Graph RAG for Langflow 1.7.x

### Flow Diagram

```
┌────────────┐
│ Directory  │
│ Loader     │
└─────┬──────┘
      │
      ▼
┌───────────────────────┐      ┌──────────────────┐
│ Graph Context Engine  │◄─────│ OpenAI Model     │
│ (custom component)    │      │ (graph builder)  │
│ - extract triples     │      └──────────────────┘
│ - build graph facts   │
│ - rank graph edges    │◄─────┌────────────┐
└──────────┬────────────┘      │ Chat Input │
           │                   └────────────┘
           ▼
┌──────────────────┐
│ Prompt Template  │
│ (final answer)   │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ OpenAI Model     │
│ (answer model)   │
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Chat Output      │
└──────────────────┘
```

## Proper Tutorial: Build Graph RAG in Langflow

### What You Are Building

This flow does three things inside Langflow:

1. Loads documents from your QA knowledge base.
2. Uses an LLM to extract **subject-relation-object triples** from those documents.
3. Uses those graph facts to answer questions through a final grounded answer prompt.

### Why This Version Is Better for This Repo

- It is compatible with the current Langflow setup in this project.
- It imports as a real Langflow flow JSON.
- It is understandable and editable directly inside Langflow.
- It is good for **small-to-medium tutorial datasets**.

### Before You Start

You need:

- Langflow running locally
- An OpenAI API key
- A small set of architecture, QA, or system-design documents

Recommended dataset size for this tutorial:

- `5` to `30` documents
- mostly structured technical text
- examples containing components, services, dependencies, events, or ownership relationships

### Step 1: Import the Flow

Import:

**[graph_rag_langflow.json](./graph_rag_langflow.json)**

After import, you should see these main nodes:

- `Directory`
- `Graph Builder LLM`
- `Chat Input`
- `Graph Context Engine`
- `Graph Answer Prompt`
- `Answer LLM`
- `Chat Output`

### Step 2: Configure the Directory Loader

Point the **Directory** node to the folder that contains the documents you want to graph.

The default project path is:

`/Users/promode/Documents/AITesterBlueprint/Project_12_RAG_Basics/RAG_Documents`

Recommended file types:

- `pdf`
- `txt`
- `md`
- `csv`

### Step 3: Configure the Graph Builder LLM

Open the **Graph Builder LLM** node and add your OpenAI API key.

Recommended settings:

- model: `gpt-4o-mini`
- temperature: `0`

This model is used by the custom component to:

- extract graph triples from the documents
- extract entities and keywords from the user question

### Step 4: Understand the Graph Context Engine

The **Graph Context Engine** custom component is the core of this tutorial.

It performs the following sequence during execution:

1. Reads the loaded source documents.
2. Prompts the LLM to convert document text into triples like:
   - `Service A -> depends_on -> Database B`
   - `UI Checkout -> calls -> Orders API`
3. Deduplicates the extracted relationships.
4. Analyzes the user question to identify entities and keywords.
5. Scores graph facts against that question.
6. Returns the highest-signal graph facts as prompt context.

Important limitation:

- This tutorial version rebuilds the graph during execution.
- That is fine for learning and smaller corpora.
- For production-scale Graph RAG, you would persist the graph to Neo4j or another graph store.

### Step 5: Configure the Graph Context Engine

Recommended settings:

- `Max Triples Per Document`: `6`
- `Top Graph Facts`: `8`

If your documents are dense system-design docs, you can increase:

- `Max Triples Per Document` to `8` or `10`

If your answers become noisy, decrease:

- `Top Graph Facts` to `5` or `6`

### Step 6: Configure the Final Answer Model

Open the **Answer LLM** node and add the same OpenAI API key.

Recommended settings:

- model: `gpt-4o-mini`
- temperature: `0`

This node should stay deterministic because the graph context is already doing the heavy lifting.

### Step 7: Run Good Test Questions

Use questions that require relationship reasoning, for example:

- `Which services depend on the authentication service?`
- `What part of the system is affected if Redis becomes unavailable?`
- `Which components write to the orders database?`
- `What does the checkout flow call before payment confirmation?`
- `Which modules are connected through the notification service?`

### Step 8: How to Evaluate the Result

A good Graph RAG answer should:

- mention the correct entities
- preserve the actual relationship chain
- avoid hallucinating components that were not in the graph facts
- cite the retrieved facts where appropriate, such as `[fact-1]`

### How to Extend This Tutorial Later

Once this tutorial flow is stable, you can extend it in three useful directions:

1. Add a persistent graph store such as Neo4j.
2. Split graph building and graph querying into separate Langflow pipelines.
3. Combine graph context with vector retrieval for a **hybrid Graph + Vector RAG** setup.

### 📥 Import the Flow

Import the pre-built flow: **[graph_rag_langflow.json](./graph_rag_langflow.json)**

---

## 🧪 QA Testing Points

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | Entity extraction accuracy | Are the right entities and relationships captured? |
| 2 | Relationship ranking quality | Does the component surface the most relevant graph facts for the question? |
| 3 | Multi-hop questions | Test dependency and impact-analysis questions that require more than one relation |
| 4 | Missing-edge behavior | Verify the flow says there is not enough graph context when key relations are absent |
| 5 | Rebuild cost | Measure execution time and token cost since the tutorial graph is rebuilt during execution |

---

**Next:** [Agentic RAG Flow →](../06_Agentic_RAG_Flow/)
