from crewai import Agent, Task, Crew
from crewai import LLM
import os
from dotenv import load_dotenv

load_dotenv()
# Step 0 - set the llm. brain
groq_llm = LLM(
    model="groq/openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY")
)

# 1. Define an Agent
qa_agent = Agent(
    role="QA Engineer",
    goal="Analyze a feature and identify potential test scenarios",
    backstory="You are a senior QA engineer with 15 years of experience in test planning.",
    llm=groq_llm,
    verbose=True
)



# 2. Define a Task
test_plan_task = Task(
    description="Create 5 test scenarios for a Login page with email and password fields.",
    expected_output="A numbered list of 5 test scenarios with brief descriptions.",
    agent=qa_agent
)

# 3. Define a Crew
crew = Crew(
    agents=[qa_agent],
    tasks=[test_plan_task],
    verbose=True
)

# 4. Run the Crew
result = crew.kickoff()
print(result)