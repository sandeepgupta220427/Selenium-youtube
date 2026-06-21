"""
MCP Server 3: QA Dashboard Resources
======================================
Demonstrates: RESOURCES — read-only data the AI can access.
Resources are like GET endpoints. They SHOW data, no side effects.

Run:   fastmcp dev 03_qa_dashboard.py
Test:  Opens MCP Inspector → click "Resources" tab

QA Use Case: Expose test results, environment status, team metrics,
and configuration as structured data for AI consumption.
"""

from fastmcp import FastMCP
import json
from datetime import datetime

mcp = FastMCP("QA Dashboard")

# ── Resource 1: Latest test results ──
@mcp.resource("testresults://latest")
def latest_test_results() -> str:
    """Latest smoke test execution results."""
    results = {
        "run_id": "RUN-2025-0342",
        "timestamp": datetime.now().isoformat(),
        "suite": "Smoke Tests",
        "duration_seconds": 142,
        "summary": {"total": 25, "passed": 21, "failed": 3, "skipped": 1},
        "pass_rate": "84.0%",
        "failed_tests": [
            {
                "name": "test_checkout_payment",
                "error": "TimeoutError: Payment gateway did not respond in 30s",
                "duration": 30.2,
            },
            {
                "name": "test_user_profile_update",
                "error": "AssertionError: Expected status 200, got 500",
                "duration": 2.1,
            },
            {
                "name": "test_search_pagination",
                "error": "ElementNotFound: Pagination button not visible",
                "duration": 8.7,
            },
        ],
        "slowest_tests": [
            {"name": "test_checkout_payment", "duration": 30.2},
            {"name": "test_image_upload_large", "duration": 15.8},
            {"name": "test_report_generation", "duration": 12.3},
        ],
    }
    return json.dumps(results, indent=2)

# ── Resource 2: Test environments status ──
@mcp.resource("environments://status")
def environment_status() -> str:
    """Current status of all test environments."""
    envs = [
        {
            "name": "Development",
            "url": "https://dev.myapp.com",
            "status": "healthy",
            "version": "2.4.1-dev",
            "last_deploy": "2025-03-14T10:30:00",
            "uptime": "99.2%",
        },
        {
            "name": "Staging",
            "url": "https://staging.myapp.com",
            "status": "healthy",
            "version": "2.4.0",
            "last_deploy": "2025-03-13T16:00:00",
            "uptime": "99.8%",
        },
        {
            "name": "Production",
            "url": "https://myapp.com",
            "status": "healthy",
            "version": "2.3.9",
            "last_deploy": "2025-03-10T08:00:00",
            "uptime": "99.95%",
        },
        {
            "name": "Performance",
            "url": "https://perf.myapp.com",
            "status": "degraded",
            "version": "2.4.0",
            "last_deploy": "2025-03-12T14:00:00",
            "uptime": "95.1%",
            "issue": "High CPU usage - load test running",
        },
    ]
    return json.dumps(envs, indent=2)

# ── Resource 3: Open bugs summary ──
@mcp.resource("bugs://open")
def open_bugs() -> str:
    """All currently open bugs with severity breakdown."""
    bugs = {
        "total_open": 18,
        "by_severity": {"critical": 1, "high": 4, "medium": 8, "low": 5},
        "critical_bugs": [
            {
                "id": "BUG-2891",
                "title": "Payment processing fails for international cards",
                "assignee": "Priya S.",
                "age_days": 2,
                "module": "Payments",
            }
        ],
        "high_bugs": [
            {"id": "BUG-2887", "title": "Search returns stale results after indexing", "assignee": "Amit K.", "age_days": 5},
            {"id": "BUG-2884", "title": "User session expires prematurely on mobile", "assignee": "Neha R.", "age_days": 7},
            {"id": "BUG-2880", "title": "CSV export missing header row", "assignee": "Rahul M.", "age_days": 10},
            {"id": "BUG-2876", "title": "Dashboard charts not loading on Safari", "assignee": "Unassigned", "age_days": 14},
        ],
        "oldest_unresolved_days": 14,
        "avg_resolution_days": 4.2,
    }
    return json.dumps(bugs, indent=2)

# ── Resource 4: Sprint metrics ──
@mcp.resource("metrics://sprint")
def sprint_metrics() -> str:
    """Current sprint QA metrics and velocity."""
    metrics = {
        "sprint": "Sprint 24 (Mar 3 - Mar 14)",
        "days_remaining": 1,
        "test_cases": {"planned": 85, "executed": 78, "remaining": 7},
        "execution_rate": "91.8%",
        "bugs_found_this_sprint": 12,
        "bugs_fixed_this_sprint": 9,
        "bug_leakage_from_last_sprint": 2,
        "automation_coverage": "67%",
        "flaky_test_count": 4,
        "team_members": [
            {"name": "Priya", "tests_executed": 22, "bugs_filed": 4},
            {"name": "Amit", "tests_executed": 18, "bugs_filed": 3},
            {"name": "Neha", "tests_executed": 20, "bugs_filed": 3},
            {"name": "Rahul", "tests_executed": 18, "bugs_filed": 2},
        ],
    }
    return json.dumps(metrics, indent=2)


# ── Resource 5: Dynamic resource with parameter ──
@mcp.resource("coverage://module/{module_name}")
def module_coverage(module_name: str) -> str:
    """Code coverage for a specific module."""
    coverage_data = {
        "auth": {"line": 89, "branch": 76, "function": 92},
        "payments": {"line": 72, "branch": 58, "function": 80},
        "search": {"line": 91, "branch": 84, "function": 95},
        "profile": {"line": 85, "branch": 71, "function": 88},
        "dashboard": {"line": 64, "branch": 52, "function": 70},
    }

    module = module_name.lower()
    if module in coverage_data:
        cov = coverage_data[module]
        return json.dumps({
            "module": module_name,
            "coverage": cov,
            "meets_threshold": cov["line"] >= 80,
            "threshold": 80,
        }, indent=2)

    return json.dumps({
        "error": f"Module '{module_name}' not found",
        "available_modules": list(coverage_data.keys()),
    }, indent=2)

