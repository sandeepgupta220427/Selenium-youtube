# CrewAI Agent with Custom Tools


from crewai import Agent, Task, Crew ,LLM
from crewai.tools import tool
import os
from dotenv import load_dotenv

load_dotenv()
# Step 0 - set the llm. brain
llm = LLM(
    model="groq/openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY")
)

#25 * 4 + 10

@tool("Calculator")
def calculator(expression: str):
    """Use this tool to calculate the result of a mathematical expression."""
    try:
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {e}"

@tool("WordCounter")
def word_counter(text: str) -> str:
    """Counts the number of words, characters, and sentences in the given text.
    Use this to analyze any piece of text.
    """
    words = len(text.split())
    chars = len(text)
    sentences = text.count('.') + text.count('!') + text.count('?')
    return f"Words: {words}, Characters: {chars}, Sentences: {sentences}"

@tool("TemperatureConverter")
def temperature_converter(value_and_unit: str) -> str:
    """Converts temperature between Celsius and Fahrenheit.
    Input format: '<number> C' or '<number> F'
    Examples: '100 C' converts 100°C to Fahrenheit, '212 F' converts 212°F to Celsius.
    """
    try:
        parts = value_and_unit.strip().split()
        value = float(parts[0])
        unit = parts[1].upper()
        if unit == "C":
            result = (value * 9 / 5) + 32
            return f"{value}°C = {result:.1f}°F"
        elif unit == "F":
            result = (value - 32) * 5 / 9
            return f"{value}°F = {result:.1f}°C"
        else:
            return "Error: Use 'C' or 'F' as the unit. Example: '100 C'"
    except Exception as e:
        return f"Error: {str(e)}. Use format like '100 C' or '212 F'"


math_helper = Agent(
    role="Smart Assistant",
    goal="Help users with calculations, text analysis, and unit conversions using your tools",
    backstory=(
        "You are a precise and helpful assistant who always uses the right tool for the job. "
        "You never guess — you always use your tools to provide accurate answers."
    ),
    tools=[calculator,word_counter,temperature_converter],
    verbose=True,
    llm=llm,
)

analysis_task = Task(
    description=(
        "Perform the following tasks using your tools:\n"
        "1. Calculate: 145 * 3 + 89\n"
        "2. Count the words in: 'CrewAI is an amazing framework for building AI agents. It makes multi-agent systems easy!'\n"
        "3. Convert 37 degrees Celsius to Fahrenheit\n"
        "Present all results clearly."
    ),
    expected_output="A clear summary of all three results with the tool outputs.",
    agent=math_helper,
)

crew = Crew(
    agents=[math_helper],
    tasks=[analysis_task],
    verbose=True,
)

result = crew.kickoff()
print("\n===== CREW RESULT =====")
print(result)