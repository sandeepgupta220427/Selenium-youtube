# 003 - CrewAI Memory System

## 🎯 What This Does

This example demonstrates CrewAI's built-in **Memory System**. Memory allows multi-agent crews to:
- Remember context within a single run (Short-Term Memory).
- Retain knowledge across multiple runs (Long-Term Memory).
- Track specific people, places, or topics (Entity Memory).

In this script, a **Tech Researcher** gathers facts about Python, and a **Content Writer** uses that exact research to write a LinkedIn post.

---

## 🧠 Enabling Memory

Memory is enabled at the **Crew** level:

```python
embedder = {
    "provider": "ollama",
    "config": {
        "model": "mxbai-embed-large"  # Local embedding model
    }
}

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    memory=True,            # <-- Turns on the memory system
    embedder=embedder,      # <-- Configures local memory storage (avoids OpenAI API errors)
)
```

### Why Do We Need an Embedder?
Memory relies on a vector database (ChromaDB) to store and retrieve past context mathematically. Converting text into these mathematical vectors requires an "Embedding Model".

By default, CrewAI tries to use OpenAI's embedder. Since we are running locally (via Ollama), we configure it to use a local embedding model instead (like `mxbai-embed-large`).

---

## 🔄 Task Context (Sequential Execution)

In a Crew workflow, you can explicitly tell one task that it depends on the output of a previous task using the `context` parameter:

```python
writing_task = Task(
    description="Write a LinkedIn post using the research provided.",
    agent=writer,
    context=[research_task],  # <-- Forces the writer to use the researcher's output
)
```

The Writer agent will read both the direct output of the `research_task` AND use its internal memory system to recall any relevant entities or context gathered during that step.

---

## 🔗 Resources

- [CrewAI Memory Documentation](https://docs.crewai.com/core-concepts/Memory/)
- [Ollama Embedding Models](https://ollama.com/library/mxbai-embed-large)
