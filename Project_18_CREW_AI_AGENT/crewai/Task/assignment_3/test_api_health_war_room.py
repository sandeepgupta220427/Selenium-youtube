"""
Pytest tests for Assignment 3 - API Health Check War Room

Full test suite including:
- Unit tests for all custom tools
- Configuration tests for all agents
- Task configuration tests
- Crew configuration tests
- Integration test (marked @pytest.mark.slow) that runs the complete crew
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
from api_health_war_room_crew import (
    # Tools
    parse_alert_payload,
    get_service_dependency_map,
    get_recent_deployments,
    # Pydantic models
    IncidentClassification,
    IncidentReport,
    # Agent creators
    create_incident_classifier,
    create_api_test_strategist,
    create_blast_radius_analyst,
    create_incident_commander,
    # Task creators
    create_classification_task,
    create_test_strategy_task,
    create_blast_radius_task,
    create_incident_report_task,
    # Crew creator
    create_crew,
    SAMPLE_ALERT_PAYLOAD,
    groq_llm
)


# ============================================================================
# Custom Tool Unit Tests
# ============================================================================

class TestParseAlertPayloadTool:
    """Unit tests for ParseAlertPayload tool."""

    def test_valid_payload_parsing(self):
        """Test that valid alert payload is parsed correctly."""
        payload = json.dumps({
            "endpoint": "/api/test",
            "error_rate": 5.5,
            "latency_p99": 1500,
            "status_codes": {"200": 100, "500": 10},
            "affected_users": 500
        })

        result = parse_alert_payload.run(payload)
        data = json.loads(result)

        assert data["endpoint"] == "/api/test"
        assert data["error_rate"] == 5.5
        assert data["latency_p99"] == 1500
        assert data["affected_users"] == 500

    def test_computes_error_breakdown(self):
        """Test that error breakdown is computed correctly."""
        payload = json.dumps({
            "endpoint": "/api/test",
            "error_rate": 10.0,
            "latency_p99": 2000,
            "status_codes": {"200": 900, "400": 50, "500": 30, "503": 20},
            "affected_users": 100
        })

        result = parse_alert_payload.run(payload)
        data = json.loads(result)

        assert data["error_breakdown"]["4xx_errors"] == 50
        assert data["error_breakdown"]["5xx_errors"] == 50

    def test_computes_severity_indicators(self):
        """Test that severity indicators are computed correctly."""
        # High severity payload
        high_severity = json.dumps({
            "endpoint": "/api/critical",
            "error_rate": 15.0,
            "latency_p99": 5000,
            "status_codes": {"200": 100, "500": 50},
            "affected_users": 5000
        })

        result = parse_alert_payload.run(high_severity)
        data = json.loads(result)
        indicators = data["severity_indicators"]

        assert indicators["high_error_rate"] is True
        assert indicators["high_latency"] is True
        assert indicators["many_users_affected"] is True
        assert indicators["server_errors"] is True

    def test_handles_missing_fields(self):
        """Test error handling for missing required fields."""
        incomplete_payload = json.dumps({
            "endpoint": "/api/test"
            # Missing other required fields
        })

        result = parse_alert_payload.run(incomplete_payload)

        assert "Error" in result or "error" in result.lower()
        assert "Missing" in result or "missing" in result.lower()

    def test_handles_invalid_json(self):
        """Test error handling for invalid JSON."""
        result = parse_alert_payload.run("not valid json")

        assert "Error" in result or "error" in result.lower()

    def test_handles_empty_status_codes(self):
        """Test handling of empty status codes."""
        payload = json.dumps({
            "endpoint": "/api/test",
            "error_rate": 0,
            "latency_p99": 100,
            "status_codes": {},
            "affected_users": 0
        })

        result = parse_alert_payload.run(payload)
        data = json.loads(result)

        assert data["total_requests"] == 0


class TestGetServiceDependencyMapTool:
    """Unit tests for GetServiceDependencyMap tool."""

    def test_returns_valid_json(self):
        """Test that tool returns valid JSON."""
        result = get_service_dependency_map.run("/api/checkout")
        data = json.loads(result)

        assert isinstance(data, dict)

    def test_checkout_has_dependencies(self):
        """Test that checkout endpoint has expected dependencies."""
        result = get_service_dependency_map.run("/api/checkout")
        data = json.loads(result)

        assert "downstream_services" in data
        assert len(data["downstream_services"]) > 0

    def test_includes_affected_user_flows(self):
        """Test that response includes affected user flows."""
        result = get_service_dependency_map.run("/api/checkout")
        data = json.loads(result)

        assert "affected_user_flows" in data
        assert len(data["affected_user_flows"]) > 0

    def test_includes_scheduled_jobs(self):
        """Test that response includes scheduled jobs."""
        result = get_service_dependency_map.run("/api/checkout")
        data = json.loads(result)

        assert "scheduled_jobs" in data

    def test_handles_unknown_service(self):
        """Test handling of unknown service."""
        result = get_service_dependency_map.run("/api/unknown-service")
        data = json.loads(result)

        # Should return a default response
        assert "service" in data
        assert "note" in data or "downstream_services" in data


class TestGetRecentDeploymentsTool:
    """Unit tests for GetRecentDeployments tool."""

    def test_returns_valid_json(self):
        """Test that tool returns valid JSON."""
        result = get_recent_deployments.run("/api/checkout")
        data = json.loads(result)

        assert isinstance(data, dict)

    def test_returns_deployment_history(self):
        """Test that tool returns deployment history."""
        result = get_recent_deployments.run("checkout-service")
        data = json.loads(result)

        assert "recent_deployments" in data or "message" in data

    def test_deployment_has_required_fields(self):
        """Test that deployments have required fields."""
        result = get_recent_deployments.run("checkout-service")
        data = json.loads(result)

        if "recent_deployments" in data and data["recent_deployments"]:
            deployment = data["recent_deployments"][0]["deployments"][0]
            assert "version" in deployment
            assert "deployed_at" in deployment
            assert "change_type" in deployment

    def test_includes_related_services(self):
        """Test that checkout includes related service deployments."""
        result = get_recent_deployments.run("/api/checkout")
        data = json.loads(result)

        if "recent_deployments" in data:
            services = [d["service"] for d in data["recent_deployments"]]
            # Should include related services like payment, inventory
            assert len(services) >= 1

    def test_handles_unknown_service(self):
        """Test handling of unknown service."""
        result = get_recent_deployments.run("nonexistent-service")
        data = json.loads(result)

        # Should return a message or empty result
        assert "message" in data or "recent_deployments" in data


# ============================================================================
# Pydantic Model Tests
# ============================================================================

class TestIncidentClassificationModel:
    """Tests for IncidentClassification Pydantic model."""

    def test_valid_classification_creation(self):
        """Test creating a valid IncidentClassification."""
        classification = IncidentClassification(
            endpoint="/api/test",
            severity="P1",
            error_rate=7.5,
            latency_p99=2500,
            affected_users=2000,
            classification_reason="High error rate affecting many users",
            immediate_action_required=True
        )

        assert classification.severity == "P1"
        assert classification.immediate_action_required is True

    def test_all_severity_levels_valid(self):
        """Test that all P0-P4 severity levels are accepted."""
        for severity in ["P0", "P1", "P2", "P3", "P4"]:
            classification = IncidentClassification(
                endpoint="/api/test",
                severity=severity,
                error_rate=1.0,
                latency_p99=100,
                affected_users=10,
                classification_reason="Test",
                immediate_action_required=False
            )
            assert classification.severity == severity

    def test_missing_required_fields_raises_error(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            IncidentClassification(
                endpoint="/api/test",
                severity="P1"
                # Missing other required fields
            )


class TestIncidentReportModel:
    """Tests for IncidentReport Pydantic model."""

    def test_valid_report_creation(self):
        """Test creating a valid IncidentReport."""
        report = IncidentReport(
            incident_id="INC-2024-0001",
            severity="P1",
            endpoint="/api/checkout",
            blast_radius=["payment-service", "order-service"],
            immediate_actions=["Scale up services", "Enable circuit breaker"],
            test_plan_summary="Run smoke tests on checkout flow",
            recommended_actions=["Fix timeout handling", "Add retry logic"],
            stakeholder_communication="Checkout API experiencing issues...",
            estimated_impact="$50k/hour revenue impact",
            recent_deployments=["checkout-service v2.15.3"]
        )

        assert report.incident_id == "INC-2024-0001"
        assert len(report.blast_radius) == 2
        assert len(report.immediate_actions) == 2

    def test_empty_lists_valid(self):
        """Test that empty lists are valid."""
        report = IncidentReport(
            incident_id="INC-2024-0002",
            severity="P4",
            endpoint="/api/test",
            blast_radius=[],
            immediate_actions=[],
            test_plan_summary="Monitor only",
            recommended_actions=[],
            stakeholder_communication="Minor anomaly detected",
            estimated_impact="None",
            recent_deployments=[]
        )

        assert len(report.blast_radius) == 0


# ============================================================================
# Agent Configuration Tests
# ============================================================================

class TestAgentConfiguration:
    """Tests for all agent configurations."""

    def test_incident_classifier_configuration(self):
        """Test Incident Classifier agent configuration."""
        agent = create_incident_classifier()

        assert agent.role == "Incident Classifier"
        assert "severity" in agent.goal.lower() or "classify" in agent.goal.lower()
        assert "P0" in agent.backstory and "P4" in agent.backstory
        assert len(agent.tools) >= 1
        assert agent.allow_delegation is False

    def test_incident_classifier_has_alert_tool(self):
        """Test that Incident Classifier has ParseAlertPayload tool."""
        agent = create_incident_classifier()

        tool_names = [t.name for t in agent.tools]
        assert "ParseAlertPayload" in tool_names

    def test_api_test_strategist_configuration(self):
        """Test API Test Strategist agent configuration."""
        agent = create_api_test_strategist()

        assert agent.role == "API Test Strategist"
        assert "test" in agent.goal.lower() or "smoke" in agent.goal.lower()
        assert "playwright" in agent.backstory.lower()

    def test_blast_radius_analyst_configuration(self):
        """Test Blast Radius Analyst agent configuration."""
        agent = create_blast_radius_analyst()

        assert agent.role == "Blast Radius Analyst"
        assert "impact" in agent.goal.lower() or "blast" in agent.goal.lower()
        assert len(agent.tools) >= 2

    def test_blast_radius_analyst_has_required_tools(self):
        """Test that Blast Radius Analyst has required tools."""
        agent = create_blast_radius_analyst()

        tool_names = [t.name for t in agent.tools]
        assert "GetServiceDependencyMap" in tool_names
        assert "GetRecentDeployments" in tool_names

    def test_incident_commander_configuration(self):
        """Test Incident Commander agent configuration."""
        agent = create_incident_commander()

        assert agent.role == "Incident Commander"
        assert "synthesize" in agent.goal.lower() or "report" in agent.goal.lower()

    def test_all_agents_have_llm(self):
        """Test that all agents have LLM configured."""
        agents = [
            create_incident_classifier(),
            create_api_test_strategist(),
            create_blast_radius_analyst(),
            create_incident_commander()
        ]

        for agent in agents:
            assert agent.llm is not None

    def test_all_agents_are_verbose(self):
        """Test that all agents have verbose mode enabled."""
        agents = [
            create_incident_classifier(),
            create_api_test_strategist(),
            create_blast_radius_analyst(),
            create_incident_commander()
        ]

        for agent in agents:
            assert agent.verbose is True


# ============================================================================
# Task Configuration Tests
# ============================================================================

class TestTaskConfiguration:
    """Tests for task configurations."""

    def test_classification_task_has_json_output(self):
        """Test that classification task outputs JSON."""
        classifier = create_incident_classifier()
        task = create_classification_task(classifier)

        assert task.output_json == IncidentClassification

    def test_classification_task_accepts_alert_payload(self):
        """Test that classification task has alert_payload placeholder."""
        classifier = create_incident_classifier()
        task = create_classification_task(classifier)

        assert "{alert_payload}" in task.description

    def test_test_strategy_task_has_context(self):
        """Test that test strategy task has classification context."""
        classifier = create_incident_classifier()
        strategist = create_api_test_strategist()

        classification_task = create_classification_task(classifier)
        test_task = create_test_strategy_task(strategist, classification_task)

        assert classification_task in test_task.context

    def test_test_strategy_mentions_playwright(self):
        """Test that test strategy task mentions Playwright syntax."""
        classifier = create_incident_classifier()
        strategist = create_api_test_strategist()

        classification_task = create_classification_task(classifier)
        test_task = create_test_strategy_task(strategist, classification_task)

        assert "playwright" in test_task.description.lower() or "apiContext" in test_task.description

    def test_blast_radius_task_has_context(self):
        """Test that blast radius task has classification context."""
        classifier = create_incident_classifier()
        analyst = create_blast_radius_analyst()

        classification_task = create_classification_task(classifier)
        blast_task = create_blast_radius_task(analyst, classification_task)

        assert classification_task in blast_task.context

    def test_incident_report_task_has_all_contexts(self):
        """Test that incident report task has all previous tasks as context."""
        classifier = create_incident_classifier()
        strategist = create_api_test_strategist()
        analyst = create_blast_radius_analyst()
        commander = create_incident_commander()

        classification_task = create_classification_task(classifier)
        test_task = create_test_strategy_task(strategist, classification_task)
        blast_task = create_blast_radius_task(analyst, classification_task)
        report_task = create_incident_report_task(
            commander, classification_task, test_task, blast_task
        )

        assert classification_task in report_task.context
        assert test_task in report_task.context
        assert blast_task in report_task.context

    def test_incident_report_task_has_json_output(self):
        """Test that incident report task outputs JSON."""
        classifier = create_incident_classifier()
        strategist = create_api_test_strategist()
        analyst = create_blast_radius_analyst()
        commander = create_incident_commander()

        classification_task = create_classification_task(classifier)
        test_task = create_test_strategy_task(strategist, classification_task)
        blast_task = create_blast_radius_task(analyst, classification_task)
        report_task = create_incident_report_task(
            commander, classification_task, test_task, blast_task
        )

        assert report_task.output_json == IncidentReport


# ============================================================================
# Crew Configuration Tests
# ============================================================================

class TestCrewConfiguration:
    """Tests for crew configuration."""

    def test_crew_has_exactly_four_agents(self):
        """Test that crew has exactly 4 agents."""
        crew = create_crew()

        assert len(crew.agents) == 4

    def test_crew_runs_sequentially(self):
        """Test that crew uses sequential process."""
        crew = create_crew()

        assert crew.process == Process.sequential

    def test_crew_has_four_tasks(self):
        """Test that crew has exactly 4 tasks."""
        crew = create_crew()

        assert len(crew.tasks) == 4

    def test_crew_agent_roles(self):
        """Test that crew has all required agent roles."""
        crew = create_crew()

        roles = [agent.role for agent in crew.agents]
        assert "Incident Classifier" in roles
        assert "API Test Strategist" in roles
        assert "Blast Radius Analyst" in roles
        assert "Incident Commander" in roles

    def test_crew_has_at_least_three_custom_tools(self):
        """Test that crew agents collectively have at least 3 custom tools."""
        crew = create_crew()

        all_tools = set()
        for agent in crew.agents:
            if agent.tools:
                for tool in agent.tools:
                    all_tools.add(tool.name)

        assert len(all_tools) >= 3
        assert "ParseAlertPayload" in all_tools
        assert "GetServiceDependencyMap" in all_tools
        assert "GetRecentDeployments" in all_tools


# ============================================================================
# Integration Test (Slow)
# ============================================================================

class TestCrewIntegration:
    """Integration tests for the complete crew."""

    @pytest.mark.slow
    def test_complete_crew_execution(self):
        """
        Integration test that runs the complete crew against a sample alert.

        This test is marked as slow and should be run separately:
        pytest -m slow
        """
        # Skip if no API key (CI environment)
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY not set - skipping integration test")

        # Create crew and run
        crew = create_crew(output_file="test_incident_report.json")
        result = crew.kickoff(inputs={"alert_payload": SAMPLE_ALERT_PAYLOAD})

        # Convert result to string for assertions
        result_str = str(result)

        # Assert the output contains a severity level
        severity_found = any(s in result_str for s in ["P0", "P1", "P2", "P3", "P4"])
        assert severity_found, "Output should contain a severity level (P0-P4)"

        # Assert the output contains at least one recommended action
        action_keywords = ["action", "recommend", "fix", "implement", "scale", "monitor"]
        action_found = any(keyword in result_str.lower() for keyword in action_keywords)
        assert action_found, "Output should contain at least one recommended action"

        # Clean up test output file
        test_output = Path("test_incident_report.json")
        if test_output.exists():
            test_output.unlink()

    @pytest.mark.slow
    def test_crew_handles_different_alert_payloads(self):
        """Test that crew can handle different alert payloads."""
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY not set - skipping integration test")

        # Low severity payload
        low_severity_payload = json.dumps({
            "endpoint": "/api/health",
            "error_rate": 0.5,
            "latency_p99": 100,
            "status_codes": {"200": 9950, "500": 50},
            "affected_users": 50
        })

        crew = create_crew(output_file="test_low_severity.json")
        result = crew.kickoff(inputs={"alert_payload": low_severity_payload})

        result_str = str(result)
        # Should still produce valid output
        assert len(result_str) > 100, "Output should be substantial"

        # Clean up
        test_output = Path("test_low_severity.json")
        if test_output.exists():
            test_output.unlink()


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (run with: pytest -m slow)"
    )


if __name__ == "__main__":
    # Run all tests except slow ones by default
    pytest.main([__file__, "-v", "-m", "not slow"])
