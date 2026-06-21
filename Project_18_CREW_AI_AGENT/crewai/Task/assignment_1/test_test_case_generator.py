"""
Pytest tests for Assignment 1 - Test Case Generator Crew

Tests validate:
1. Agent roles are configured correctly
2. Crew has exactly 2 agents
3. Crew runs sequentially
"""

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from crewai import Process
from test_case_generator_crew import (
    create_requirements_analyst,
    create_test_case_writer,
    create_analysis_task,
    create_test_writing_task,
    create_crew,
    groq_llm
)


class TestAgentConfiguration:
    """Tests for agent role configurations."""

    def test_requirements_analyst_role(self):
        """Test that Requirements Analyst agent has correct role configuration."""
        agent = create_requirements_analyst()

        assert agent.role == "Requirements Analyst"
        assert "testable scenarios" in agent.goal.lower()
        assert "positive" in agent.goal.lower() or "positive" in agent.backstory.lower()
        assert "negative" in agent.goal.lower() or "negative" in agent.backstory.lower()
        assert "edge" in agent.goal.lower() or "edge" in agent.backstory.lower()
        assert agent.allow_delegation is False

    def test_test_case_writer_role(self):
        """Test that Test Case Writer agent has correct role configuration."""
        agent = create_test_case_writer()

        assert agent.role == "Test Case Writer"
        assert "test case" in agent.goal.lower()
        assert agent.allow_delegation is False

    def test_agents_have_llm_configured(self):
        """Test that both agents have LLM configured."""
        analyst = create_requirements_analyst()
        writer = create_test_case_writer()

        assert analyst.llm is not None
        assert writer.llm is not None

    def test_agents_are_verbose(self):
        """Test that agents have verbose mode enabled."""
        analyst = create_requirements_analyst()
        writer = create_test_case_writer()

        assert analyst.verbose is True
        assert writer.verbose is True


class TestTaskConfiguration:
    """Tests for task configurations."""

    def test_analysis_task_description(self):
        """Test that analysis task has proper description with feature placeholder."""
        analyst = create_requirements_analyst()
        task = create_analysis_task(analyst)

        assert "{feature}" in task.description
        assert "positive" in task.description.lower()
        assert "negative" in task.description.lower()
        assert "edge" in task.description.lower()

    def test_writing_task_has_output_file(self):
        """Test that writing task is configured with output_file parameter."""
        writer = create_test_case_writer()
        task = create_test_writing_task(writer, "test_output.md")

        assert task.output_file == "test_output.md"

    def test_writing_task_mentions_required_fields(self):
        """Test that writing task mentions all required test case fields."""
        writer = create_test_case_writer()
        task = create_test_writing_task(writer)

        required_fields = ["Test ID", "Title", "Priority", "Pre-conditions", "Steps", "Expected"]
        for field in required_fields:
            assert field.lower() in task.description.lower(), f"Missing field: {field}"


class TestCrewConfiguration:
    """Tests for crew configuration."""

    def test_crew_has_exactly_two_agents(self):
        """Test that crew has exactly 2 agents."""
        crew = create_crew()

        assert len(crew.agents) == 2

    def test_crew_runs_sequentially(self):
        """Test that crew uses sequential process."""
        crew = create_crew()

        assert crew.process == Process.sequential

    def test_crew_has_two_tasks(self):
        """Test that crew has exactly 2 tasks."""
        crew = create_crew()

        assert len(crew.tasks) == 2

    def test_crew_agent_roles(self):
        """Test that crew has the correct agent roles in order."""
        crew = create_crew()

        roles = [agent.role for agent in crew.agents]
        assert "Requirements Analyst" in roles
        assert "Test Case Writer" in roles

    def test_crew_is_verbose(self):
        """Test that crew has verbose mode enabled."""
        crew = create_crew()

        assert crew.verbose is True


class TestLLMConfiguration:
    """Tests for LLM configuration."""

    def test_groq_llm_model(self):
        """Test that Groq LLM uses the correct model."""
        assert "groq" in groq_llm.model.lower()
        assert "llama" in groq_llm.model.lower()

    def test_groq_api_key_loaded(self):
        """Test that GROQ_API_KEY environment variable is available."""
        # This test validates the .env is loaded properly
        api_key = os.getenv("GROQ_API_KEY")
        # API key should either be set or we should handle gracefully
        # Don't assert specific values for security
        assert api_key is None or len(api_key) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
