"""
Pytest tests for Assignment 2 - Flaky Test Investigator Crew

Tests validate:
1. Custom tools work correctly
2. Agent roles are configured correctly
3. Crew has exactly 3 agents running sequentially
4. Pydantic models are properly structured
5. Context chaining is configured
"""

import pytest
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from crewai import Process
from pydantic import ValidationError
from flaky_test_investigator_crew import (
    # Tools
    get_test_history,
    get_test_source_code,
    # Pydantic models
    FlakyTestReport,
    FlakyTestReportList,
    # Agent creators
    create_flaky_test_detector,
    create_root_cause_analyst,
    create_fix_recommender,
    # Task creators
    create_detection_task,
    create_analysis_task,
    create_recommendation_task,
    # Crew creator
    create_crew,
    groq_llm
)


# ============================================================================
# Custom Tool Tests
# ============================================================================

class TestGetTestHistoryTool:
    """Tests for the GetTestHistory custom tool."""

    def test_returns_valid_json(self):
        """Test that GetTestHistory returns valid JSON."""
        result = get_test_history.run("integration")
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_returns_test_history_data(self):
        """Test that GetTestHistory returns test names with history."""
        result = get_test_history.run("unit")
        data = json.loads(result)

        # Should have multiple tests
        assert len(data) > 0

        # Each test should have a list of booleans
        for test_name, history in data.items():
            assert isinstance(test_name, str)
            assert isinstance(history, list)
            assert all(isinstance(x, bool) for x in history)

    def test_history_has_ten_runs(self):
        """Test that each test has exactly 10 runs in history."""
        result = get_test_history.run("e2e")
        data = json.loads(result)

        for test_name, history in data.items():
            assert len(history) == 10, f"Test {test_name} should have 10 runs"

    def test_contains_flaky_tests(self):
        """Test that the mock data contains both stable and flaky tests."""
        result = get_test_history.run("all")
        data = json.loads(result)

        has_stable = False
        has_flaky = False

        for history in data.values():
            if all(h == history[0] for h in history):
                has_stable = True  # All same value = stable
            else:
                has_flaky = True  # Mixed values = flaky

        assert has_stable, "Should have at least one stable test"
        assert has_flaky, "Should have at least one flaky test"


class TestGetTestSourceCodeTool:
    """Tests for the GetTestSourceCode custom tool."""

    def test_returns_source_code_for_known_test(self):
        """Test that GetTestSourceCode returns code for known tests."""
        result = get_test_source_code.run("test_payment_processing")

        assert "def test_payment_processing" in result
        assert len(result) > 50  # Should have substantial content

    def test_returns_error_for_unknown_test(self):
        """Test that GetTestSourceCode handles unknown tests gracefully."""
        result = get_test_source_code.run("test_nonexistent")

        assert "not found" in result.lower()

    def test_source_code_contains_dependency_info(self):
        """Test that source code includes dependency information."""
        result = get_test_source_code.run("test_websocket_connection")

        assert "Dependencies:" in result or "dependencies" in result.lower()


# ============================================================================
# Pydantic Model Tests
# ============================================================================

class TestFlakyTestReportModel:
    """Tests for the FlakyTestReport Pydantic model."""

    def test_valid_report_creation(self):
        """Test creating a valid FlakyTestReport."""
        report = FlakyTestReport(
            test_name="test_example",
            flakiness_rate=0.5,
            probable_cause="Timing issue",
            recommended_action="Add explicit wait",
            quarantine=False
        )

        assert report.test_name == "test_example"
        assert report.flakiness_rate == 0.5
        assert report.quarantine is False

    def test_flakiness_rate_bounds(self):
        """Test that flakiness_rate accepts valid float values."""
        report = FlakyTestReport(
            test_name="test",
            flakiness_rate=0.0,
            probable_cause="None",
            recommended_action="None",
            quarantine=False
        )
        assert report.flakiness_rate == 0.0

        report2 = FlakyTestReport(
            test_name="test",
            flakiness_rate=1.0,
            probable_cause="Critical",
            recommended_action="Quarantine",
            quarantine=True
        )
        assert report2.flakiness_rate == 1.0

    def test_missing_required_fields_raises_error(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            FlakyTestReport(
                test_name="test",
                # Missing other required fields
            )


class TestFlakyTestReportListModel:
    """Tests for the FlakyTestReportList Pydantic model."""

    def test_valid_list_creation(self):
        """Test creating a valid FlakyTestReportList."""
        reports = FlakyTestReportList(
            reports=[
                FlakyTestReport(
                    test_name="test1",
                    flakiness_rate=0.3,
                    probable_cause="Shared state",
                    recommended_action="Isolate test data",
                    quarantine=False
                ),
                FlakyTestReport(
                    test_name="test2",
                    flakiness_rate=0.8,
                    probable_cause="Race condition",
                    recommended_action="Add synchronization",
                    quarantine=True
                )
            ]
        )

        assert len(reports.reports) == 2

    def test_empty_list_is_valid(self):
        """Test that an empty reports list is valid."""
        reports = FlakyTestReportList(reports=[])
        assert len(reports.reports) == 0


# ============================================================================
# Agent Configuration Tests
# ============================================================================

class TestAgentConfiguration:
    """Tests for agent role configurations."""

    def test_flaky_test_detector_role(self):
        """Test Flaky Test Detector agent configuration."""
        agent = create_flaky_test_detector()

        assert agent.role == "Flaky Test Detector"
        assert "flaky" in agent.goal.lower() or "flaky" in agent.backstory.lower()
        assert len(agent.tools) >= 1
        assert agent.allow_delegation is False

    def test_flaky_test_detector_has_history_tool(self):
        """Test that Flaky Test Detector has the GetTestHistory tool."""
        agent = create_flaky_test_detector()

        tool_names = [t.name for t in agent.tools]
        assert "GetTestHistory" in tool_names

    def test_root_cause_analyst_role(self):
        """Test Root Cause Analyst agent configuration."""
        agent = create_root_cause_analyst()

        assert agent.role == "Root Cause Analyst"
        assert "root cause" in agent.goal.lower() or "cause" in agent.backstory.lower()
        assert len(agent.tools) >= 1

    def test_root_cause_analyst_has_source_code_tool(self):
        """Test that Root Cause Analyst has the GetTestSourceCode tool."""
        agent = create_root_cause_analyst()

        tool_names = [t.name for t in agent.tools]
        assert "GetTestSourceCode" in tool_names

    def test_fix_recommender_role(self):
        """Test Fix Recommender agent configuration."""
        agent = create_fix_recommender()

        assert agent.role == "Fix Recommender"
        assert "recommend" in agent.goal.lower() or "fix" in agent.goal.lower()


# ============================================================================
# Task Configuration Tests
# ============================================================================

class TestTaskConfiguration:
    """Tests for task configurations."""

    def test_analysis_task_has_context(self):
        """Test that analysis task has detection task in context."""
        detector = create_flaky_test_detector()
        analyst = create_root_cause_analyst()

        detection_task = create_detection_task(detector)
        analysis_task = create_analysis_task(analyst, detection_task)

        assert detection_task in analysis_task.context

    def test_recommendation_task_has_context(self):
        """Test that recommendation task has analysis task in context."""
        detector = create_flaky_test_detector()
        analyst = create_root_cause_analyst()
        recommender = create_fix_recommender()

        detection_task = create_detection_task(detector)
        analysis_task = create_analysis_task(analyst, detection_task)
        recommendation_task = create_recommendation_task(recommender, analysis_task)

        assert analysis_task in recommendation_task.context

    def test_recommendation_task_has_json_output(self):
        """Test that recommendation task is configured for JSON output."""
        detector = create_flaky_test_detector()
        analyst = create_root_cause_analyst()
        recommender = create_fix_recommender()

        detection_task = create_detection_task(detector)
        analysis_task = create_analysis_task(analyst, detection_task)
        recommendation_task = create_recommendation_task(recommender, analysis_task)

        assert recommendation_task.output_json == FlakyTestReportList


# ============================================================================
# Crew Configuration Tests
# ============================================================================

class TestCrewConfiguration:
    """Tests for crew configuration."""

    def test_crew_has_exactly_three_agents(self):
        """Test that crew has exactly 3 agents."""
        crew = create_crew()

        assert len(crew.agents) == 3

    def test_crew_runs_sequentially(self):
        """Test that crew uses sequential process."""
        crew = create_crew()

        assert crew.process == Process.sequential

    def test_crew_has_three_tasks(self):
        """Test that crew has exactly 3 tasks."""
        crew = create_crew()

        assert len(crew.tasks) == 3

    def test_crew_agent_roles(self):
        """Test that crew has the correct agent roles."""
        crew = create_crew()

        roles = [agent.role for agent in crew.agents]
        assert "Flaky Test Detector" in roles
        assert "Root Cause Analyst" in roles
        assert "Fix Recommender" in roles

    def test_crew_has_custom_tools(self):
        """Test that crew agents have custom tools assigned."""
        crew = create_crew()

        all_tools = []
        for agent in crew.agents:
            if agent.tools:
                all_tools.extend([t.name for t in agent.tools])

        assert "GetTestHistory" in all_tools
        assert "GetTestSourceCode" in all_tools


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
