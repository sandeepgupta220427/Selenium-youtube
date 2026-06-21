"""
Assignment 2 — Flaky Test Investigator Crew (Level: Intermediate)

A CrewAI crew with three agents that investigates flaky tests in a CI/CD pipeline:
- Agent 1: Flaky Test Detector - identifies flaky tests from pass/fail history
- Agent 2: Root Cause Analyst - hypothesizes why each test is flaky
- Agent 3: Fix Recommender - produces action plans to fix flaky tests

Features:
- Custom @tool decorators for test history and test source code
- Context chaining between tasks
- Pydantic model for structured JSON output

Usage:
    python flaky_test_investigator_crew.py

Or programmatically:
    from flaky_test_investigator_crew import create_crew
    crew = create_crew()
    result = crew.kickoff()
"""

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from pydantic import BaseModel
from typing import List
import os
import json
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


# ============================================================================
# Pydantic Models
# ============================================================================

class FlakyTestReport(BaseModel):
    """Pydantic model for structured flaky test report output."""
    test_name: str
    flakiness_rate: float  # Percentage of flakiness (0.0 to 1.0)
    probable_cause: str
    recommended_action: str
    quarantine: bool


class FlakyTestReportList(BaseModel):
    """List of flaky test reports."""
    reports: List[FlakyTestReport]


# ============================================================================
# Custom Tools
# ============================================================================

@tool("GetTestHistory")
def get_test_history(test_suite: str) -> str:
    """
    Retrieves the pass/fail history for tests over the last 10 CI runs.
    Returns a dictionary mapping test names to a list of pass (True) / fail (False) results.

    Args:
        test_suite: The name of the test suite to analyze (e.g., "integration", "unit", "e2e")

    Returns:
        JSON string with test names mapped to their pass/fail history
    """
    # Mock data simulating CI test history
    mock_history = {
        "test_user_login": [True, True, True, True, True, True, True, True, True, True],
        "test_payment_processing": [True, False, True, True, False, True, True, False, True, True],
        "test_api_timeout_handling": [False, True, False, True, False, True, False, True, False, True],
        "test_database_connection": [True, True, True, True, True, True, True, True, True, True],
        "test_file_upload": [True, True, False, True, True, True, True, False, True, True],
        "test_websocket_connection": [False, True, True, False, True, False, True, True, False, True],
        "test_cache_invalidation": [True, False, True, False, True, False, True, False, True, False],
        "test_user_registration": [True, True, True, True, True, True, True, True, True, True],
        "test_concurrent_requests": [True, False, False, True, False, True, False, True, False, False],
        "test_email_notification": [True, True, True, True, True, True, True, True, False, True],
    }

    return json.dumps(mock_history, indent=2)


@tool("GetTestSourceCode")
def get_test_source_code(test_name: str) -> str:
    """
    Retrieves the source code and metadata for a specific test.
    Use this to understand the implementation details of a flaky test.

    Args:
        test_name: The name of the test to retrieve source code for

    Returns:
        The test source code and relevant metadata
    """
    # Mock test source code data
    mock_source_code = {
        "test_payment_processing": '''
def test_payment_processing():
    """Tests payment processing with Stripe API"""
    # Setup
    client = PaymentClient(api_key=os.getenv("STRIPE_KEY"))

    # Test
    response = client.process_payment(amount=100, currency="USD")
    time.sleep(0.5)  # Wait for webhook

    # Assert
    assert response.status == "completed"
    assert PaymentRecord.objects.filter(id=response.id).exists()

# Dependencies: external Stripe API, database, async webhooks
# Last modified: 2024-01-15
# Test file: tests/integration/test_payments.py
''',
        "test_api_timeout_handling": '''
def test_api_timeout_handling():
    """Tests API timeout behavior"""
    # This test relies on actual network timeouts
    with pytest.raises(TimeoutError):
        api_client.get("/slow-endpoint", timeout=0.1)

    # Sometimes the endpoint responds faster than expected
    # causing the test to fail

# Dependencies: network conditions, server load
# Last modified: 2024-02-01
# Test file: tests/unit/test_api.py
''',
        "test_websocket_connection": '''
def test_websocket_connection():
    """Tests WebSocket connection stability"""
    ws = WebSocketClient("ws://localhost:8080")
    ws.connect()

    # Race condition: message might arrive before listener is ready
    ws.send("ping")
    response = ws.receive(timeout=1)

    assert response == "pong"
    ws.close()

# Dependencies: WebSocket server, timing, network
# Last modified: 2024-01-20
# Test file: tests/integration/test_websocket.py
''',
        "test_cache_invalidation": '''
def test_cache_invalidation():
    """Tests cache invalidation after data update"""
    # Setup: populate cache
    cache.set("user_1", {"name": "John"})

    # Update database
    User.objects.filter(id=1).update(name="Jane")

    # Cache should be invalidated (but timing is unpredictable)
    time.sleep(0.1)  # Arbitrary wait
    cached = cache.get("user_1")

    assert cached["name"] == "Jane"

# Dependencies: cache service, database, async invalidation
# Last modified: 2024-01-25
# Test file: tests/integration/test_cache.py
''',
        "test_concurrent_requests": '''
def test_concurrent_requests():
    """Tests handling of concurrent API requests"""
    import threading

    results = []
    def make_request():
        response = api_client.post("/counter/increment")
        results.append(response.json()["value"])

    threads = [threading.Thread(target=make_request) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Shared state issue: counter increments are not atomic
    assert len(set(results)) == 10  # All values should be unique

# Dependencies: thread safety, database locks, shared state
# Last modified: 2024-02-10
# Test file: tests/integration/test_concurrent.py
''',
        "test_file_upload": '''
def test_file_upload():
    """Tests file upload functionality"""
    with open("/tmp/test_file.txt", "w") as f:
        f.write("test content")

    response = client.upload("/tmp/test_file.txt")

    # Cleanup sometimes runs before assertion in parallel tests
    assert response.status == 200
    assert response.json()["filename"] == "test_file.txt"

    os.remove("/tmp/test_file.txt")

# Dependencies: filesystem, temp directory, parallel test execution
# Last modified: 2024-01-10
# Test file: tests/integration/test_upload.py
''',
        "test_email_notification": '''
def test_email_notification():
    """Tests email notification sending"""
    # Trigger email
    user.send_welcome_email()

    # Wait for async email job
    time.sleep(2)

    # Check mailbox (sometimes email takes longer)
    emails = mailbox.get_emails(to=user.email)
    assert len(emails) == 1

# Dependencies: email service, async job queue, timing
# Last modified: 2024-02-05
# Test file: tests/integration/test_email.py
'''
    }

    if test_name in mock_source_code:
        return mock_source_code[test_name]
    else:
        return f"Source code not found for test: {test_name}. Available tests: {list(mock_source_code.keys())}"


# ============================================================================
# Agents
# ============================================================================

def create_flaky_test_detector() -> Agent:
    """Creates the Flaky Test Detector agent."""
    return Agent(
        role="Flaky Test Detector",
        goal="Identify flaky tests by analyzing pass/fail patterns over multiple CI runs",
        backstory="""You are a CI/CD reliability engineer who specializes in
        test stability analysis. You can spot patterns in test results that
        indicate flakiness. A test is considered flaky if it has both passed
        and failed in the same analysis window without any code changes. You
        calculate flakiness rates and prioritize tests by their impact on
        CI reliability.""",
        llm=groq_llm,
        tools=[get_test_history],
        verbose=True,
        allow_delegation=False
    )


def create_root_cause_analyst() -> Agent:
    """Creates the Root Cause Analyst agent."""
    return Agent(
        role="Root Cause Analyst",
        goal="Determine the root cause of test flakiness by analyzing test code and patterns",
        backstory="""You are a senior QA architect with deep expertise in test
        design patterns and anti-patterns. You understand common causes of
        flakiness including timing issues, shared state, environment dependencies,
        test data pollution, race conditions, and external service dependencies.
        You analyze test source code to identify the specific cause.""",
        llm=groq_llm,
        tools=[get_test_source_code],
        verbose=True,
        allow_delegation=False
    )


def create_fix_recommender() -> Agent:
    """Creates the Fix Recommender agent."""
    return Agent(
        role="Fix Recommender",
        goal="Provide concrete, actionable recommendations to fix flaky tests",
        backstory="""You are a test automation expert who has fixed hundreds of
        flaky tests across different tech stacks. You provide practical,
        prioritized recommendations including specific code changes,
        architectural improvements, and when to quarantine vs fix immediately.
        You balance test reliability with development velocity.""",
        llm=groq_llm,
        verbose=True,
        allow_delegation=False
    )


# ============================================================================
# Tasks
# ============================================================================

def create_detection_task(detector: Agent) -> Task:
    """Creates the flaky test detection task."""
    return Task(
        description="""Use the GetTestHistory tool to retrieve test pass/fail data
        for the CI pipeline.

        Analyze the results and identify which tests are FLAKY. A test is flaky if:
        - It has BOTH passed AND failed within the 10-run window
        - The failures are not consistent (intermittent)

        For each flaky test found, calculate:
        - Flakiness Rate = (number of state changes) / (total runs - 1)
        - Failure Rate = (failures) / (total runs)

        Provide a ranked list of flaky tests ordered by severity (highest flakiness first).
        """,
        expected_output="""A detailed report listing all identified flaky tests with:
        - Test name
        - Pass/fail pattern (e.g., "TTFTTTFTTT")
        - Flakiness rate (percentage)
        - Failure rate (percentage)
        - Severity ranking""",
        agent=detector
    )


def create_analysis_task(analyst: Agent, detection_task: Task) -> Task:
    """Creates the root cause analysis task."""
    return Task(
        description="""For each flaky test identified in the previous analysis,
        use the GetTestSourceCode tool to retrieve the test implementation.

        Analyze each test and determine the probable root cause from these categories:
        - TIMING_ISSUE: Sleep statements, arbitrary waits, timeouts
        - SHARED_STATE: Global variables, database state, cache pollution
        - EXTERNAL_DEPENDENCY: API calls, network, external services
        - RACE_CONDITION: Threading, async operations, parallel execution
        - ENVIRONMENT_DEPENDENCY: Filesystem, temp files, environment variables
        - TEST_DATA_POLLUTION: Data leaking between tests

        Provide specific evidence from the code that supports your diagnosis.
        """,
        expected_output="""A root cause analysis report for each flaky test with:
        - Test name
        - Root cause category
        - Specific code evidence (line references)
        - Explanation of why this causes flakiness""",
        agent=analyst,
        context=[detection_task]
    )


def create_recommendation_task(recommender: Agent, analysis_task: Task, output_file: str = "flaky_test_report.json") -> Task:
    """Creates the fix recommendation task."""
    return Task(
        description="""Based on the root cause analysis, create an action plan for each flaky test.

        For each test, provide:
        1. test_name: The name of the flaky test
        2. flakiness_rate: The calculated flakiness rate (0.0 to 1.0)
        3. probable_cause: A concise description of the root cause
        4. recommended_action: Specific steps to fix the test, including:
           - Code changes needed
           - Design pattern improvements
           - Infrastructure changes if needed
        5. quarantine: Boolean - whether to quarantine immediately (true if flakiness > 50% or affecting critical path)

        Prioritize by:
        - Impact on CI reliability
        - Ease of fix
        - Test importance

        Output must be valid JSON matching the FlakyTestReport schema.
        """,
        expected_output="""A JSON object with a "reports" array containing FlakyTestReport objects:
        {
            "reports": [
                {
                    "test_name": "test_example",
                    "flakiness_rate": 0.5,
                    "probable_cause": "Description",
                    "recommended_action": "Fix steps",
                    "quarantine": false
                }
            ]
        }""",
        agent=recommender,
        context=[analysis_task],
        output_json=FlakyTestReportList,
        output_file=output_file
    )


# ============================================================================
# Crew
# ============================================================================

def create_crew(output_file: str = "flaky_test_report.json") -> Crew:
    """Creates and returns the Flaky Test Investigator Crew."""
    # Create agents
    flaky_detector = create_flaky_test_detector()
    root_cause_analyst = create_root_cause_analyst()
    fix_recommender = create_fix_recommender()

    # Create tasks with context chaining
    detection_task = create_detection_task(flaky_detector)
    analysis_task = create_analysis_task(root_cause_analyst, detection_task)
    recommendation_task = create_recommendation_task(fix_recommender, analysis_task, output_file)

    # Create and return crew
    return Crew(
        agents=[flaky_detector, root_cause_analyst, fix_recommender],
        tasks=[detection_task, analysis_task, recommendation_task],
        process=Process.sequential,
        verbose=True
    )


def main():
    """Main function to run the crew."""
    print("\n" + "=" * 60)
    print("Flaky Test Investigator Crew")
    print("=" * 60)
    print("Analyzing CI pipeline for flaky tests...")
    print("=" * 60 + "\n")

    # Create and run the crew
    crew = create_crew()
    result = crew.kickoff()

    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(result)

    return result


if __name__ == "__main__":
    main()
