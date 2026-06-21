"""
Assignment 3 — API Health Check War Room (Level: Advanced)

A CrewAI crew simulating a QA war room responding to an API health degradation incident.

Four Agents:
- Agent 1: Incident Classifier - classifies incident severity (P0-P4)
- Agent 2: API Test Strategist - designs immediate smoke test plan
- Agent 3: Blast Radius Analyst - determines downstream impact
- Agent 4: Incident Commander - synthesizes all outputs into final report

Features:
- 3+ custom tools (alert parser, dependency map, deployment history)
- 2 Pydantic models (IncidentClassification, IncidentReport)
- Process.sequential with context chaining
- JSON output on Tasks 1 and 4

Usage:
    python api_health_war_room_crew.py

Or programmatically:
    from api_health_war_room_crew import create_crew
    crew = create_crew()
    alert_payload = '{"endpoint": "/api/checkout", "error_rate": 15.5, ...}'
    result = crew.kickoff(inputs={"alert_payload": alert_payload})
"""

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
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

class IncidentClassification(BaseModel):
    """Pydantic model for incident classification output."""
    endpoint: str = Field(description="The affected API endpoint")
    severity: str = Field(description="Severity level: P0, P1, P2, P3, or P4")
    error_rate: float = Field(description="Current error rate percentage")
    latency_p99: float = Field(description="99th percentile latency in ms")
    affected_users: int = Field(description="Number of affected users")
    classification_reason: str = Field(description="Explanation for the severity classification")
    immediate_action_required: bool = Field(description="Whether immediate action is needed")


class IncidentReport(BaseModel):
    """Pydantic model for final incident report output."""
    incident_id: str = Field(description="Unique incident identifier")
    severity: str = Field(description="Severity level: P0, P1, P2, P3, or P4")
    endpoint: str = Field(description="The affected API endpoint")
    blast_radius: List[str] = Field(description="List of affected services/flows")
    immediate_actions: List[str] = Field(description="List of immediate actions to take")
    test_plan_summary: str = Field(description="Summary of the smoke test plan")
    recommended_actions: List[str] = Field(description="Recommended remediation actions")
    stakeholder_communication: str = Field(description="Draft communication for stakeholders")
    estimated_impact: str = Field(description="Description of estimated business impact")
    recent_deployments: List[str] = Field(description="Recent deployments that may be related")


# ============================================================================
# Custom Tools
# ============================================================================

@tool("ParseAlertPayload")
def parse_alert_payload(alert_json: str) -> str:
    """
    Parses and validates an alert payload JSON string.
    Extracts key metrics and normalizes the data for analysis.

    Args:
        alert_json: JSON string containing alert payload with fields:
                   endpoint, error_rate, latency_p99, status_codes, affected_users

    Returns:
        Parsed and validated alert data with additional computed metrics
    """
    try:
        alert = json.loads(alert_json)

        # Validate required fields
        required_fields = ["endpoint", "error_rate", "latency_p99", "status_codes", "affected_users"]
        missing = [f for f in required_fields if f not in alert]
        if missing:
            return f"Error: Missing required fields: {missing}"

        # Compute additional metrics
        status_codes = alert.get("status_codes", {})
        total_requests = sum(status_codes.values()) if status_codes else 0
        error_codes = {k: v for k, v in status_codes.items() if k.startswith(("4", "5"))}
        success_codes = {k: v for k, v in status_codes.items() if k.startswith("2")}

        parsed = {
            "endpoint": alert["endpoint"],
            "error_rate": alert["error_rate"],
            "latency_p99": alert["latency_p99"],
            "affected_users": alert["affected_users"],
            "status_codes": status_codes,
            "total_requests": total_requests,
            "error_codes": error_codes,
            "success_codes": success_codes,
            "error_breakdown": {
                "4xx_errors": sum(v for k, v in status_codes.items() if k.startswith("4")),
                "5xx_errors": sum(v for k, v in status_codes.items() if k.startswith("5"))
            },
            "severity_indicators": {
                "high_error_rate": alert["error_rate"] > 5,
                "high_latency": alert["latency_p99"] > 2000,
                "many_users_affected": alert["affected_users"] > 1000,
                "server_errors": any(k.startswith("5") for k in status_codes.keys())
            }
        }

        return json.dumps(parsed, indent=2)

    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON - {str(e)}"
    except Exception as e:
        return f"Error parsing alert: {str(e)}"


@tool("GetServiceDependencyMap")
def get_service_dependency_map(service_name: str) -> str:
    """
    Retrieves the service dependency map showing upstream and downstream services,
    affected user flows, and scheduled jobs.

    Args:
        service_name: The service or endpoint name (e.g., "/api/checkout", "payment-service")

    Returns:
        JSON with dependencies, affected flows, and scheduled jobs
    """
    # Mock service dependency data
    dependency_maps = {
        "/api/checkout": {
            "service": "checkout-service",
            "upstream_services": [
                {"name": "api-gateway", "type": "ingress", "critical": True},
                {"name": "load-balancer", "type": "infrastructure", "critical": True}
            ],
            "downstream_services": [
                {"name": "payment-service", "type": "core", "critical": True},
                {"name": "inventory-service", "type": "core", "critical": True},
                {"name": "order-service", "type": "core", "critical": True},
                {"name": "notification-service", "type": "async", "critical": False},
                {"name": "analytics-service", "type": "async", "critical": False}
            ],
            "affected_user_flows": [
                "Purchase completion",
                "Cart checkout",
                "Payment processing",
                "Order confirmation",
                "Email receipts"
            ],
            "scheduled_jobs": [
                {"name": "inventory-sync", "frequency": "every 5 minutes", "impacted": True},
                {"name": "order-reconciliation", "frequency": "hourly", "impacted": True},
                {"name": "payment-settlement", "frequency": "daily at 2 AM", "impacted": True}
            ],
            "database_dependencies": ["orders-db", "inventory-db", "payments-db"]
        },
        "/api/users": {
            "service": "user-service",
            "upstream_services": [
                {"name": "api-gateway", "type": "ingress", "critical": True}
            ],
            "downstream_services": [
                {"name": "auth-service", "type": "core", "critical": True},
                {"name": "profile-service", "type": "core", "critical": False},
                {"name": "preferences-service", "type": "async", "critical": False}
            ],
            "affected_user_flows": [
                "User login",
                "User registration",
                "Profile management",
                "Password reset"
            ],
            "scheduled_jobs": [
                {"name": "session-cleanup", "frequency": "every 15 minutes", "impacted": True}
            ],
            "database_dependencies": ["users-db", "sessions-db"]
        },
        "/api/search": {
            "service": "search-service",
            "upstream_services": [
                {"name": "api-gateway", "type": "ingress", "critical": True},
                {"name": "cdn", "type": "caching", "critical": False}
            ],
            "downstream_services": [
                {"name": "elasticsearch", "type": "core", "critical": True},
                {"name": "recommendation-service", "type": "enhancement", "critical": False},
                {"name": "analytics-service", "type": "async", "critical": False}
            ],
            "affected_user_flows": [
                "Product search",
                "Autocomplete suggestions",
                "Category browsing",
                "Filter and sort"
            ],
            "scheduled_jobs": [
                {"name": "index-rebuild", "frequency": "daily at 3 AM", "impacted": True},
                {"name": "cache-warmup", "frequency": "every 30 minutes", "impacted": False}
            ],
            "database_dependencies": ["elasticsearch-cluster", "redis-cache"]
        }
    }

    # Extract service from endpoint
    service_key = service_name.lower()
    for key in dependency_maps:
        if key in service_key or service_key in key:
            return json.dumps(dependency_maps[key], indent=2)

    # Default response for unknown services
    return json.dumps({
        "service": service_name,
        "upstream_services": [{"name": "api-gateway", "type": "ingress", "critical": True}],
        "downstream_services": [{"name": "unknown", "type": "unknown", "critical": False}],
        "affected_user_flows": ["Unknown - manual investigation required"],
        "scheduled_jobs": [],
        "database_dependencies": ["unknown"],
        "note": "Service not found in dependency map. Manual investigation required."
    }, indent=2)


@tool("GetRecentDeployments")
def get_recent_deployments(service_name: str) -> str:
    """
    Retrieves recent deployment history for the specified service and related services.
    Useful for correlating incidents with recent changes.

    Args:
        service_name: The service or endpoint name to check deployments for

    Returns:
        JSON with recent deployments including timestamps, versions, and change descriptions
    """
    # Mock deployment history
    deployments = {
        "checkout-service": [
            {
                "version": "2.15.3",
                "deployed_at": "2024-02-15T14:30:00Z",
                "deployed_by": "jenkins-ci",
                "change_type": "hotfix",
                "description": "Fix timeout handling in payment callback",
                "commit": "a1b2c3d",
                "rollback_available": True
            },
            {
                "version": "2.15.2",
                "deployed_at": "2024-02-14T10:00:00Z",
                "deployed_by": "jenkins-ci",
                "change_type": "feature",
                "description": "Add support for new payment provider",
                "commit": "e4f5g6h",
                "rollback_available": True
            },
            {
                "version": "2.15.1",
                "deployed_at": "2024-02-12T09:00:00Z",
                "deployed_by": "jenkins-ci",
                "change_type": "minor",
                "description": "Dependency updates and security patches",
                "commit": "i7j8k9l",
                "rollback_available": True
            }
        ],
        "payment-service": [
            {
                "version": "3.8.1",
                "deployed_at": "2024-02-15T16:00:00Z",
                "deployed_by": "jenkins-ci",
                "change_type": "config",
                "description": "Updated API rate limits",
                "commit": "m1n2o3p",
                "rollback_available": True
            }
        ],
        "api-gateway": [
            {
                "version": "1.45.0",
                "deployed_at": "2024-02-13T11:00:00Z",
                "deployed_by": "jenkins-ci",
                "change_type": "feature",
                "description": "New routing rules for checkout flow",
                "commit": "q4r5s6t",
                "rollback_available": True
            }
        ],
        "inventory-service": [
            {
                "version": "4.2.0",
                "deployed_at": "2024-02-15T15:00:00Z",
                "deployed_by": "jenkins-ci",
                "change_type": "feature",
                "description": "Real-time inventory sync optimization",
                "commit": "u7v8w9x",
                "rollback_available": True
            }
        ]
    }

    # Find relevant deployments
    service_key = service_name.lower().replace("/api/", "").replace("-", "")
    relevant_deployments = []

    for service, deps in deployments.items():
        service_normalized = service.lower().replace("-", "")
        if service_key in service_normalized or service_normalized in service_key:
            relevant_deployments.append({
                "service": service,
                "deployments": deps
            })

    # Also include related services
    if "checkout" in service_key:
        for related in ["payment-service", "inventory-service", "api-gateway"]:
            if related in deployments and related not in [d["service"] for d in relevant_deployments]:
                relevant_deployments.append({
                    "service": related,
                    "deployments": deployments[related]
                })

    if not relevant_deployments:
        return json.dumps({
            "message": f"No deployment history found for {service_name}",
            "suggestion": "Check deployment logs manually or verify service name"
        }, indent=2)

    return json.dumps({
        "query": service_name,
        "recent_deployments": relevant_deployments,
        "total_deployments_24h": sum(len(d["deployments"]) for d in relevant_deployments),
        "potential_correlations": [
            d["service"] for d in relevant_deployments
            if any(dep["change_type"] in ["feature", "hotfix"] for dep in d["deployments"])
        ]
    }, indent=2)


# ============================================================================
# Agents
# ============================================================================

def create_incident_classifier() -> Agent:
    """Creates the Incident Classifier agent."""
    return Agent(
        role="Incident Classifier",
        goal="Accurately classify incident severity using the P0-P4 scale based on impact metrics",
        backstory="""You are a senior SRE with extensive experience in incident
        management. You can quickly assess the severity of an incident based on
        error rates, latency, affected users, and business impact. You use the
        following severity scale:

        - P0 (Critical): Complete service outage, >10% error rate, revenue impact, >10k users affected
        - P1 (High): Major degradation, 5-10% error rate, significant user impact, >1k users
        - P2 (Medium): Partial degradation, 1-5% error rate, moderate impact, >100 users
        - P3 (Low): Minor issues, <1% error rate, limited impact, <100 users
        - P4 (Informational): Anomalies for monitoring, no user impact

        You always explain your classification reasoning clearly.""",
        llm=groq_llm,
        tools=[parse_alert_payload],
        verbose=True,
        allow_delegation=False
    )


def create_api_test_strategist() -> Agent:
    """Creates the API Test Strategist agent."""
    return Agent(
        role="API Test Strategist",
        goal="Design immediate smoke test plans to validate API health and isolate failures",
        backstory="""You are a QA automation architect who specializes in API
        testing. You can quickly design targeted smoke tests using Playwright's
        API testing syntax. You focus on critical path validation, isolation
        testing, and quick feedback. Your tests use the Playwright APIRequestContext
        pattern with proper assertions.""",
        llm=groq_llm,
        verbose=True,
        allow_delegation=False
    )


def create_blast_radius_analyst() -> Agent:
    """Creates the Blast Radius Analyst agent."""
    return Agent(
        role="Blast Radius Analyst",
        goal="Determine the full impact of the incident on services, user flows, and scheduled jobs",
        backstory="""You are a systems architect who understands complex
        microservices topologies. You can trace dependencies upstream and
        downstream to determine the full blast radius of an incident. You
        identify all affected user flows, scheduled jobs, and dependent
        services to ensure nothing is missed in the incident response.""",
        llm=groq_llm,
        tools=[get_service_dependency_map, get_recent_deployments],
        verbose=True,
        allow_delegation=False
    )


def create_incident_commander() -> Agent:
    """Creates the Incident Commander agent."""
    return Agent(
        role="Incident Commander",
        goal="Synthesize all incident data into a comprehensive report with clear actions",
        backstory="""You are an experienced incident commander who has led
        response efforts for numerous P0/P1 incidents. You excel at synthesizing
        complex technical information into clear, actionable reports. You
        coordinate between teams and ensure stakeholders receive timely,
        appropriate communications. You always include severity, blast radius,
        immediate actions, and a test plan in your reports.""",
        llm=groq_llm,
        verbose=True,
        allow_delegation=False
    )


# ============================================================================
# Tasks
# ============================================================================

def create_classification_task(classifier: Agent) -> Task:
    """Creates the incident classification task."""
    return Task(
        description="""Analyze the following alert payload and classify the incident severity.

        Alert Payload: {alert_payload}

        Use the ParseAlertPayload tool to extract and analyze the metrics.

        Determine the severity level (P0-P4) based on:
        1. Error rate percentage
        2. P99 latency
        3. Number of affected users
        4. Types of errors (4xx vs 5xx)
        5. Business criticality of the endpoint

        Output your classification as a JSON object matching the IncidentClassification schema.
        """,
        expected_output="""A JSON object with incident classification:
        {
            "endpoint": "/api/...",
            "severity": "P0|P1|P2|P3|P4",
            "error_rate": 0.0,
            "latency_p99": 0.0,
            "affected_users": 0,
            "classification_reason": "...",
            "immediate_action_required": true|false
        }""",
        agent=classifier,
        output_json=IncidentClassification
    )


def create_test_strategy_task(strategist: Agent, classification_task: Task) -> Task:
    """Creates the API test strategy task."""
    return Task(
        description="""Based on the incident classification, design an immediate smoke test plan.

        Create a test plan that:
        1. Validates the affected endpoint's basic functionality
        2. Tests critical dependencies
        3. Isolates the failure point
        4. Can be executed quickly (< 2 minutes total)

        Use Playwright API testing syntax:
        - apiContext.get(), apiContext.post(), etc.
        - expect(response).toBeOK()
        - expect(response.status()).toBe(200)
        - response.json() for body assertions

        For each test, specify:
        - Test name
        - Endpoint and method
        - Headers/payload (if applicable)
        - Assertions to check
        - Priority (run order)
        """,
        expected_output="""A smoke test plan in pseudocode using Playwright syntax:

        Test 1: [Name]
        Priority: [1-5]
        ```
        const response = await apiContext.get('/endpoint');
        expect(response).toBeOK();
        expect(response.json()).toHaveProperty('field');
        ```

        [Additional tests...]
        """,
        agent=strategist,
        context=[classification_task]
    )


def create_blast_radius_task(analyst: Agent, classification_task: Task) -> Task:
    """Creates the blast radius analysis task."""
    return Task(
        description="""Determine the full blast radius of this incident.

        Use the GetServiceDependencyMap tool to get the service topology.
        Use the GetRecentDeployments tool to check for correlated changes.

        Analyze and report:
        1. All downstream services affected
        2. All user flows impacted
        3. Scheduled jobs that may fail or produce incorrect results
        4. Database connections at risk
        5. Recent deployments that may have caused this

        Prioritize by business impact and provide a clear summary.
        """,
        expected_output="""A blast radius analysis including:
        - List of affected downstream services (critical first)
        - Impacted user flows
        - At-risk scheduled jobs
        - Potentially related deployments
        - Estimated business impact""",
        agent=analyst,
        context=[classification_task]
    )


def create_incident_report_task(
    commander: Agent,
    classification_task: Task,
    test_strategy_task: Task,
    blast_radius_task: Task,
    output_file: str = "incident_report.json"
) -> Task:
    """Creates the final incident report task."""
    return Task(
        description="""Synthesize all the information from the previous analyses into a
        comprehensive incident report.

        The report must include:
        1. incident_id: Generate a unique ID (e.g., "INC-2024-0215-001")
        2. severity: The classified severity level
        3. endpoint: The affected endpoint
        4. blast_radius: List of all affected services and flows
        5. immediate_actions: Prioritized list of actions to take NOW
        6. test_plan_summary: Brief summary of the smoke test plan
        7. recommended_actions: Long-term remediation recommendations
        8. stakeholder_communication: Draft message for stakeholders
        9. estimated_impact: Business impact assessment
        10. recent_deployments: Deployments that may be related

        For the stakeholder communication, include:
        - What happened (1 sentence)
        - Current status
        - Impact
        - Next steps
        - ETA for resolution (or "investigating")

        Output must be valid JSON matching the IncidentReport schema.
        """,
        expected_output="""A complete JSON incident report matching IncidentReport schema with
        all fields populated based on the analysis.""",
        agent=commander,
        context=[classification_task, test_strategy_task, blast_radius_task],
        output_json=IncidentReport,
        output_file=output_file
    )


# ============================================================================
# Crew
# ============================================================================

def create_crew(output_file: str = "incident_report.json") -> Crew:
    """Creates and returns the API Health Check War Room Crew."""
    # Create agents
    incident_classifier = create_incident_classifier()
    api_test_strategist = create_api_test_strategist()
    blast_radius_analyst = create_blast_radius_analyst()
    incident_commander = create_incident_commander()

    # Create tasks with context chaining
    classification_task = create_classification_task(incident_classifier)
    test_strategy_task = create_test_strategy_task(api_test_strategist, classification_task)
    blast_radius_task = create_blast_radius_task(blast_radius_analyst, classification_task)
    incident_report_task = create_incident_report_task(
        incident_commander,
        classification_task,
        test_strategy_task,
        blast_radius_task,
        output_file
    )

    # Create and return crew
    return Crew(
        agents=[incident_classifier, api_test_strategist, blast_radius_analyst, incident_commander],
        tasks=[classification_task, test_strategy_task, blast_radius_task, incident_report_task],
        process=Process.sequential,
        verbose=True
    )


# Sample alert payload for testing
SAMPLE_ALERT_PAYLOAD = json.dumps({
    "endpoint": "/api/checkout",
    "error_rate": 15.5,
    "latency_p99": 3500,
    "status_codes": {
        "200": 8450,
        "500": 1200,
        "503": 350,
        "504": 150
    },
    "affected_users": 12500
})


def main():
    """Main function to run the crew."""
    print("\n" + "=" * 70)
    print("API Health Check War Room")
    print("=" * 70)
    print("Incident Response Simulation")
    print("=" * 70 + "\n")

    # Create the crew
    crew = create_crew()

    # Run with sample alert
    print("Processing alert payload...")
    print(f"Alert: {SAMPLE_ALERT_PAYLOAD}")
    print("\n" + "-" * 70 + "\n")

    result = crew.kickoff(inputs={"alert_payload": SAMPLE_ALERT_PAYLOAD})

    print("\n" + "=" * 70)
    print("INCIDENT REPORT")
    print("=" * 70)
    print(result)

    return result


if __name__ == "__main__":
    main()
