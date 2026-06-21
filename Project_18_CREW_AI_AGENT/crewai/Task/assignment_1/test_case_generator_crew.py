"""
Assignment 1 — Test Case Generator Crew (Level: Beginner)

A CrewAI crew with two agents working in a sequential process:
- Agent 1: Requirements Analyst - breaks down feature requirements into testable scenarios
- Agent 2: Test Case Writer - writes detailed test cases from scenarios

Usage:
    python test_case_generator_crew.py

Or programmatically:
    from test_case_generator_crew import create_crew
    crew = create_crew()
    result = crew.kickoff(inputs={"feature": "User Registration with Email Verification"})
"""

from crewai import Agent, Task, Crew, Process, LLM
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Configure Groq LLM
groq_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)


def create_requirements_analyst() -> Agent:
    """Creates the Requirements Analyst agent."""
    return Agent(
        role="Requirements Analyst",
        goal="Break down feature requirements into comprehensive testable scenarios covering positive, negative, and edge cases",
        backstory="""You are a senior QA analyst with 10+ years of experience in
        software testing. You have a keen eye for identifying edge cases and
        potential failure points in any feature. You specialize in translating
        business requirements into clear, testable scenarios that ensure
        complete coverage. You always think about what could go wrong and
        ensure no scenario is left untested.""",
        llm=groq_llm,
        verbose=True,
        allow_delegation=False
    )


def create_test_case_writer() -> Agent:
    """Creates the Test Case Writer agent."""
    return Agent(
        role="Test Case Writer",
        goal="Write detailed, professional test cases with proper structure and clear acceptance criteria",
        backstory="""You are an experienced test documentation specialist who
        has written thousands of test cases for enterprise applications. You
        follow industry best practices and ensure each test case is actionable,
        unambiguous, and easy to execute. You always include test IDs, titles,
        pre-conditions, detailed steps, expected results, and priority levels.""",
        llm=groq_llm,
        verbose=True,
        allow_delegation=False
    )


def create_analysis_task(analyst: Agent) -> Task:
    """Creates the requirements analysis task."""
    return Task(
        description="""Analyze the following feature requirement and break it down
        into testable scenarios:

        Feature: {feature}

        Your analysis must include:
        1. POSITIVE SCENARIOS (at least 3): Happy path scenarios where everything works as expected
        2. NEGATIVE SCENARIOS (at least 3): Error handling, invalid inputs, boundary violations
        3. EDGE CASES (at least 2): Unusual but valid conditions, boundary values, race conditions

        For each scenario, provide:
        - Scenario ID (e.g., SCN-001)
        - Scenario Name
        - Category (Positive/Negative/Edge)
        - Brief Description
        - Key Validation Points
        """,
        expected_output="""A structured list of at least 8 testable scenarios
        organized by category (Positive, Negative, Edge Cases) with IDs, names,
        descriptions, and validation points for each.""",
        agent=analyst
    )


def create_test_writing_task(writer: Agent, output_file: str = "test_cases_output.md") -> Task:
    """Creates the test case writing task."""
    return Task(
        description="""Based on the testable scenarios provided, write detailed
        test cases for each scenario.

        Each test case must include:
        - Test ID: TC-XXX format
        - Title: Clear, descriptive title
        - Priority: P0 (Critical), P1 (High), P2 (Medium), P3 (Low), P4 (Nice-to-have)
        - Pre-conditions: What must be true before test execution
        - Test Steps: Numbered, detailed steps to execute
        - Expected Result: Clear, verifiable expected outcome
        - Test Data: Sample data needed (if applicable)

        Priority Guidelines:
        - P0: Core functionality, security, data integrity
        - P1: Important features, key user flows
        - P2: Secondary features, minor user flows
        - P3: Edge cases, rare scenarios
        - P4: Nice-to-have, cosmetic issues
        """,
        expected_output="""A comprehensive test case document in markdown format
        with all test cases properly structured, including Test ID, Title, Priority,
        Pre-conditions, Steps, Expected Results, and Test Data for each scenario.""",
        agent=writer,
        output_file=output_file
    )


def create_crew(output_file: str = "test_cases_output.md") -> Crew:
    """Creates and returns the Test Case Generator Crew."""
    # Create agents
    requirements_analyst = create_requirements_analyst()
    test_case_writer = create_test_case_writer()

    # Create tasks
    analysis_task = create_analysis_task(requirements_analyst)
    writing_task = create_test_writing_task(test_case_writer, output_file)

    # Create and return crew
    return Crew(
        agents=[requirements_analyst, test_case_writer],
        tasks=[analysis_task, writing_task],
        process=Process.sequential,
        verbose=True
    )


def main():
    """Main function to run the crew."""
    # Create the crew
    crew = create_crew()

    # Sample feature requirement
    feature = "User Registration with Email Verification"

    print(f"\n{'='*60}")
    print(f"Test Case Generator Crew")
    print(f"{'='*60}")
    print(f"Feature: {feature}")
    print(f"{'='*60}\n")

    # Run the crew
    result = crew.kickoff(inputs={"feature": feature})

    print(f"\n{'='*60}")
    print("FINAL OUTPUT")
    print(f"{'='*60}")
    print(result)

    return result


if __name__ == "__main__":
    main()
