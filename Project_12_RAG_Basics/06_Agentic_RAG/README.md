# 6. Agentic RAG

## Overview

Agentic RAG gives the retrieval process to an AI agent that can reason, plan, and decide dynamically. Instead of a fixed retrieve-then-generate pipeline, the agent decides when to retrieve, what to search for, whether to search again, and when it has enough information to answer. This is the closest RAG gets to how a human researcher works.

---

## Agent Capabilities

- **Dynamic tool selection:** Agent decides which retriever/tool to use based on the query
- **Iterative retrieval:** Agent can search multiple times, refining its query each time
- **Multi-source:** Agent can query vector stores, web search, APIs, and databases in one turn
- **Self-evaluation:** Agent assesses if retrieved information is sufficient before answering
- **Planning:** Agent breaks complex queries into sub-questions and tackles them systematically

### Architecture Diagram

```
                    ┌──────────────────────┐
                    │    User Question     │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │   ReAct Agent        │
                    │   (Reason + Act)     │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              ↓                ↓                ↓
     ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
     │ API Test     │  │ UI Test     │  │ Bug Report  │
     │ Docs Tool    │  │ Docs Tool   │  │ Search Tool │
     └─────────────┘  └─────────────┘  └─────────────┘
              │                │                │
              ↓                ↓                ↓
     ┌─────────────────────────────────────────────┐
     │        Agent Reasoning Loop                  │
     │  1. Think: "I need API test info"            │
     │  2. Act: Search API docs                     │
     │  3. Observe: Got results                     │
     │  4. Think: "Need bug history too"            │
     │  5. Act: Search bug reports                  │
     │  6. Think: "I have enough info"              │
     │  7. Answer: Synthesized response             │
     └─────────────────────────────────────────────┘
```

---

## Python Implementation

### ReAct Agent with Multiple Tools

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.tools.retriever import create_retriever_tool
from langchain import hub

# Define specialized retriever tools
api_tool = create_retriever_tool(
    api_retriever,
    name="api_test_docs",
    description="Search API testing documentation and test cases"
)

ui_tool = create_retriever_tool(
    ui_retriever,
    name="ui_test_docs",
    description="Search UI testing guides and Selenium/Playwright docs"
)

bug_tool = create_retriever_tool(
    bug_retriever,
    name="bug_reports",
    description="Search historical bug reports and known issues"
)

tools = [api_tool, ui_tool, bug_tool]

# Create ReAct agent
llm = ChatOpenAI(model="gpt-4o", temperature=0)
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,  # Prevent infinite loops
    handle_parsing_errors=True
)

# The agent decides which tools to use and when
response = agent_executor.invoke({
    "input": "Were there any bugs related to payment APIs last quarter, "
             "and what test cases should cover them?"
})
```

### Multi-Step Research Agent

```python
from langchain.tools import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper

# Add web search as an additional tool
search = GoogleSearchAPIWrapper()
web_search_tool = Tool(
    name="web_search",
    description="Search the web for latest testing best practices and tools",
    func=search.run
)

# Agent now has internal docs + web search
tools = [api_tool, ui_tool, bug_tool, web_search_tool]

# Query that requires multiple tools
response = agent_executor.invoke({
    "input": "Compare our current API test coverage with industry "
             "best practices for REST API testing"
})
# Agent will: 1) Search internal docs for coverage,
#              2) Web search for best practices,
#              3) Synthesize a comparison
```


---

## 🧪 QA Testing Points for Agentic RAG

| # | Test Scenario | What to Check |
|---|---|---|
| 1 | `max_iterations` limit | Does the agent terminate gracefully? |
| 2 | Tool selection accuracy | Does the agent pick the right retriever? |
| 3 | Token consumption | Agents use 3–10x more tokens than basic RAG |
| 4 | Error handling | What happens when a tool fails mid-execution? |
| 5 | Hallucinated tool calls | Verify the agent doesn't call non-existent tools |

> **💡 QA Connection:** This maps directly to agentic testing workflows — the agent's reasoning mirrors how a QA engineer investigates issues across multiple data sources.

---

**Next:** [Self-RAG →](../07_Self_RAG/)
