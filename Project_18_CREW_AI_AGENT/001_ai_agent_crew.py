from crewai import Agent, Task, Crew
from llm_config import get_llm

# Get configured LLM (reads from .env)
llm = get_llm()

# --- Hello World CrewAI Example ---

# Step 1: Define an Agent
greeter = Agent(
    role='Friendly Greeter',
    goal='Greet the world in a fun and creative way',
    backstory="You are a cheerful AI who loves saying hello to the world in creative ways.",
    verbose=True,
    llm=llm,
)

# Step 2: Define a Task
greet_task = Task(
    description="Say 'Hello, World!' in 5 different creative and fun styles.",
    expected_output="A list of 5 creative hello world greetings.",
    agent=greeter,
)

# Step 3: Create a Crew and kick it off
crew = Crew(
    agents=[greeter],
    tasks=[greet_task],
    verbose=True,
)

result = crew.kickoff()
print("\n===== CREW RESULT =====")
print(result)