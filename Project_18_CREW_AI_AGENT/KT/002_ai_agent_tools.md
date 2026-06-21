# 002 - CrewAI Custom Tools

## 🎯 What This Does

This example demonstrates how to give agents **Custom Tools** using the `@tool` decorator. Instead of just answering questions with their built-in knowledge, agents can execute code to perform external actions.

In this script, a **Smart Assistant** agent is equipped with three tools:
1. `Calculator` — evaluates math expressions
2. `WordCounter` — counts words, characters, and sentences
3. `TemperatureConverter` — converts between Celsius and Fahrenheit

---

## 🔧 How Tools Work in CrewAI

CrewAI provides a `@tool` decorator that turns any Python function into a tool an agent can use.

### Defining a Tool

```python
from crewai.tools import tool

@tool("Calculator")
def calculator(expression: str) -> str:
    """Evaluates a math expression and returns the result.
    Example input: '25 * 4 + 10'
    """
    return f"Result: {eval(expression)}"
```

**Important:** The **docstring** (`"""..."""`) is critical. The LLM reads the docstring to understand *what* the tool does and *how* to construct the input arguments.

### Giving Tools to an Agent

You attach tools to an agent by passing them in a list:

```python
math_helper = Agent(
    role="Smart Assistant",
    goal="Help users with calculations using your tools",
    backstory="You never guess — you always use your tools.",
    tools=[calculator],  # <-- Attach tools here
    llm=llm
)
```

---

## ▶️ Example Execution

When running the task:
```python
"Calculate: 145 * 3 + 89"
```

The agent's internal thought process will look like this:
1. "I need to calculate `145 * 3 + 89`."
2. "I will use the `Calculator` tool."
3. Agent calls: `calculator("145 * 3 + 89")`
4. Tool returns: `"Result: 524"`
5. Agent formulates the final answer based on the tool's output.

---

## 🔗 Resources

- [CrewAI Custom Tools Documentation](https://docs.crewai.com/core-concepts/Tools/)
