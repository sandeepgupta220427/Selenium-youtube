from crewai import Agent, Task, Crew, LLM
import os
from dotenv import load_dotenv


# 0. Set an LLM Brain and Load .env
load_dotenv()
llm = LLM(
    model="ollama/llama3.2:1b",
   base_url=os.getenv("Ollama_URL")
)

# 1. Define a Agent
qa_agent = Agent(
    role = "QA Engineer",
    goal = "Analyze a feature and identify a potential test sceanrios",
    backstory = "You are a Senior QA Engineer with 15 years of experience on creating test plan and test cases",
    llm = llm,
    verbose = True
)

# 2. Define a Task
test_plan_task = Task(
    description= "Create a 5 test cases for login page with email and password for abc application",
    expected_output= "provide a 5 test cases which includes title, steps, actual & expected result of a test case",
    agent= qa_agent
)

# 3. Define a Crew
crew = Crew(
    agents = [qa_agent],
    tasks = [test_plan_task],
    verbose=True
)

# Run a crew
result = crew.kickoff()
print(result)

