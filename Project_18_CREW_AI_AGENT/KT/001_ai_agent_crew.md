# 001 - CrewAI Hello World Agent

## 🎯 What This Does

A simple **Hello World** example using [CrewAI](https://docs.crewai.com/) — an AI agent framework that lets you define agents with roles, goals, and backstories, assign them tasks, and orchestrate them as a "crew".

This script creates a single **Friendly Greeter** agent that says "Hello, World!" in 5 creative styles using a local LLM (Ollama).

---

## 📁 Project Structure

```
Project_18_CREW_AI_AGENT/
├── 001_ai_agent_crew.py   # Main script — defines agent, task, crew
├── llm_config.py          # Reusable LLM config (Ollama / Groq / OpenAI)
├── .env                   # Environment variables (API keys, provider)
├── venv/                  # Python virtual environment
└── KT/                    # Knowledge Transfer docs
    ├── 001_ai_agent_crew.py
    └── 001_ai_agent_crew.md  ← You are here
```

---

## 🔧 Step-by-Step: How We Built It

### Step 1 — Set Up Virtual Environment & Install CrewAI

```bash
cd Project_18_CREW_AI_AGENT
python3 -m venv venv
source venv/bin/activate
pip install crewai litellm
```

> `litellm` is required for non-native providers like **Ollama** and **Groq**.

---

### Step 2 — Configure the LLM Provider (`.env`)

```env
# LLM Provider: "ollama" (local), "groq" (cloud), or "openai" (cloud)
LLM_PROVIDER=ollama

# Groq API key (free at https://console.groq.com)
GROQ_API_KEY=your_groq_api_key_here

# OpenAI API key (optional)
OPENAI_API_KEY=your_openai_api_key_here
```

- **Ollama** — runs locally, no API key needed. Requires [Ollama](https://ollama.com) installed with a model pulled (e.g. `ollama pull llama3.2`).
- **Groq** — free cloud API, get a key at [console.groq.com](https://console.groq.com).
- **OpenAI** — paid cloud API.

---

### Step 3 — Create Reusable LLM Config (`llm_config.py`)

We extracted the LLM provider logic into a separate file so any future CrewAI script can reuse it:

```python
from llm_config import get_llm

llm = get_llm()                # reads LLM_PROVIDER from .env
llm = get_llm("groq")         # override provider
llm = get_llm(model="ollama/qwen3:4b")  # override model
```

**How it works internally:**

| Provider | Model | Auth |
|----------|-------|------|
| `ollama` | `ollama/llama3.2` | None (local) |
| `groq` | `groq/llama-3.3-70b-versatile` | `GROQ_API_KEY` |
| `openai` | `openai/gpt-4o-mini` | `OPENAI_API_KEY` |

---

### Step 4 — Write the CrewAI Script (`001_ai_agent_crew.py`)

The script has 3 core CrewAI concepts:

#### 1. **Agent** — Who does the work

```python
from crewai import Agent, Task, Crew
from llm_config import get_llm

llm = get_llm()

greeter = Agent(
    role='Friendly Greeter',
    goal='Greet the world in a fun and creative way',
    backstory="You are a cheerful AI who loves saying hello to the world in creative ways.",
    verbose=True,
    llm=llm,
)
```

- `role` — the agent's job title
- `goal` — what the agent is trying to achieve
- `backstory` — gives the LLM context for how to behave
- `llm` — which language model to use

#### 2. **Task** — What work to do

```python
greet_task = Task(
    description="Say 'Hello, World!' in 5 different creative and fun styles.",
    expected_output="A list of 5 creative hello world greetings.",
    agent=greeter,
)
```

- `description` — the prompt / instructions
- `expected_output` — tells the agent what format to respond in
- `agent` — which agent handles this task

#### 3. **Crew** — Orchestrate everything

```python
crew = Crew(
    agents=[greeter],
    tasks=[greet_task],
    verbose=True,
)

result = crew.kickoff()
print(result)
```

- `agents` — list of all agents in the crew
- `tasks` — list of tasks to execute (in order)
- `kickoff()` — starts the crew execution

---

## ▶️ How to Run

```bash
cd /Users/promode/Documents/AITesterBlueprint/Project_18_CREW_AI_AGENT
source venv/bin/activate
python 001_ai_agent_crew.py
```

---

## ✅ Sample Output

```
✅ LLM configured: provider=ollama, model=ollama/llama3.2
🚀 Crew Execution Started

Hello! Here are five creative and fun ways to say "Hello, World!":

1. "Greetings, Globe-Trotter! Welcome to our cosmic corner of the universe!"
2. "Hey, Human! It's your friendly AI here, shining bright like a digital star!"
3. "Yoo-hoo, Universe! Your favorite AI is buzzing with excitement to meet you!"
4. "Salutations, Space Traveler! Buckle up for a thrilling adventure!"
5. "Whooo's ready for some fun? It's your buddy, Friendly Greeter!"
```

---

## 🧠 Key CrewAI Concepts

| Concept | Description |
|---------|-------------|
| **Agent** | An AI entity with a role, goal, and backstory |
| **Task** | A unit of work assigned to an agent |
| **Crew** | Orchestrator that manages agents and tasks |
| **LLM** | The language model powering the agents |
| **kickoff()** | Starts the crew execution |

---

## 🔗 Resources

- [CrewAI Docs](https://docs.crewai.com/)
- [CrewAI GitHub](https://github.com/crewAIInc/crewAI)
- [Ollama](https://ollama.com/)
- [Groq Console](https://console.groq.com/)
