"""
003 - CrewAI Agent with Memory

Demonstrates CrewAI's built-in memory system:
  - Short-term memory: remembers context within the current execution
  - Long-term memory: persists learnings across executions
  - Entity memory: tracks information about specific entities (people, places, etc.)

The crew runs TWO tasks where the second task depends on
remembering what happened in the first — showcasing memory in action.
"""

from crewai import Agent, Task, Crew
from llm_config import get_llm

llm = get_llm()

# Configure local embedder for memory so it doesn't default to OpenAI
# It requires a small local embedding model, usually mxbai-embed-large for Ollama
embedder = {
    "provider": "ollama",
    "config": {
        "model": "mxbai-embed-large"  # Typical fast default for Ollama embeddings
    }
}

# --- Define Agents ---

researcher = Agent(
    role="Tech Researcher",
    goal="Research and gather key facts about a given technology topic",
    backstory=(
        "You are a senior technology researcher with deep expertise in software engineering. "
        "You are meticulous about facts and always organize your findings clearly."
    ),
    verbose=True,
    allow_delegation=False,
    max_iter=5,
    llm=llm,
)

writer = Agent(
    role="Content Writer",
    goal="Write engaging summaries based on the research provided",
    backstory=(
        "You are a skilled technical writer who transforms complex research into "
        "clear, engaging content. You always reference the research findings provided to you."
    ),
    verbose=True,
    allow_delegation=False,
    max_iter=5,
    llm=llm,
)

# --- Define Tasks (sequential — second depends on first) ---

research_task = Task(
    description=(
        "Provide a brief research note about Python programming language:\n"
        "1. What it is (one-liner definition)\n"
        "2. Three key features\n"
        "3. Two real-world use cases\n"
        "Be concise and factual. Provide the output as simple text, do not try to use any external tools."
    ),
    expected_output="A structured research brief mapping definition, 3 features, and 2 use cases in plain text.",
    agent=researcher,
)

writing_task = Task(
    description=(
        "Using the research from the previous task, write a short "
        "LinkedIn-style post (under 150 words) about Python. "
        "Make it engaging, professional, and include relevant emojis. "
        "You MUST reference specific facts from the research. Provide the post as simple text."
    ),
    expected_output="A LinkedIn-style post under 150 words about Python.",
    agent=writer,
    context=[research_task],  # This task receives output from research_task
)

# --- Create Crew with Memory Enabled ---

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    verbose=True,
    memory=True,  # Enables short-term, long-term, and entity memory
    embedder=embedder, # Use local embedder instead of OpenAI
)

result = crew.kickoff()
print("\n===== CREW RESULT =====")
print(result)
