"""
MCP Server 3: QA Dashboard Resources - REAL JIRA DATA
======================================================
Demonstrates: RESOURCES — read-only data the AI can access.
Resources are like GET endpoints. They SHOW data, no side effects.

Run:   fastmcp dev 04_QA_Dashboard_REAL_DATA.py
Test:  Opens MCP Inspector → click "Resources" tab

QA Use Case: Expose real JIRA data - bugs, sprint metrics, and team performance
for AI consumption from the VWO project.
"""

from fastmcp import FastMCP
import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from typing import Optional
import os

mcp = FastMCP("QA Dashboard - JIRA Live")

# ── JIRA Configuration ──
JIRA_CONFIG = {
    "base_url": os.getenv("JIRA_BASE_URL", "https://bugzz.atlassian.net"),
    "email": os.getenv("JIRA_EMAIL", "thetestingacademy+jira@gmail.com"),
    "api_token": os.getenv("JIRA_API_TOKEN", ""),
    "project": "VWO"
}

def get_jira_auth() -> HTTPBasicAuth:
    """Get JIRA authentication object."""
    return HTTPBasicAuth(JIRA_CONFIG["email"], JIRA_CONFIG["api_token"])

def get_jira_headers() -> dict:
    """Get headers for JIRA API requests."""
    return {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

def jira_request(endpoint: str, params: Optional[dict] = None) -> dict:
    """Make a request to JIRA API."""
    url = f"{JIRA_CONFIG['base_url']}/rest/api/3/{endpoint}"
    try:
        response = requests.get(
            url,
            headers=get_jira_headers(),
            auth=get_jira_auth(),
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "url": url}

def jira_search(jql: str, fields: list = None, max_results: int = 50) -> dict:
    """Search JIRA issues using JQL (using new /search/jql endpoint)."""
    # Use the new JIRA API endpoint (as of 2024)
    url = f"{JIRA_CONFIG['base_url']}/rest/api/3/search/jql"
    params = {
        "jql": jql,
        "maxResults": max_results
    }
    if fields:
        params["fields"] = ",".join(fields)

    try:
        response = requests.get(
            url,
            headers=get_jira_headers(),
            auth=get_jira_auth(),
            params=params,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as e:
        result = {"error": str(e), "url": url, "issues": [], "total": 0}

    # Handle empty results gracefully
    if "issues" not in result:
        result["issues"] = []
    if "total" not in result:
        result["total"] = 0

    return result


# ── Resource 1: Latest test execution issues from JIRA ──
@mcp.resource("testresults://latest")
def latest_test_results() -> str:
    """Latest test execution issues from JIRA VWO project."""

    # Search for test-related issues (Test type or issues with Test label)
    jql = f'project = {JIRA_CONFIG["project"]} AND (type = Test OR type = "Test Execution" OR labels = Test OR labels = "test-case") ORDER BY updated DESC'

    fields = ["summary", "status", "priority", "assignee", "created", "updated", "labels"]
    result = jira_search(jql, fields, max_results=25)

    if "error" in result:
        return json.dumps({"error": result["error"], "jql": jql}, indent=2)

    issues = result.get("issues", [])
    total = result.get("total", 0)

    # Calculate summary stats
    status_counts = {}
    for issue in issues:
        status = issue["fields"]["status"]["name"]
        status_counts[status] = status_counts.get(status, 0) + 1

    passed = status_counts.get("Done", 0) + status_counts.get("Closed", 0) + status_counts.get("Passed", 0)
    failed = status_counts.get("Failed", 0) + status_counts.get("Blocked", 0)
    in_progress = status_counts.get("In Progress", 0) + status_counts.get("In Review", 0)

    test_results = {
        "run_id": f"JIRA-{datetime.now().strftime('%Y%m%d-%H%M')}",
        "timestamp": datetime.now().isoformat(),
        "project": JIRA_CONFIG["project"],
        "source": "JIRA Live Data",
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "in_progress": in_progress,
            "other": total - passed - failed - in_progress
        },
        "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "N/A",
        "status_breakdown": status_counts,
        "recent_tests": [
            {
                "key": issue["key"],
                "title": issue["fields"]["summary"],
                "status": issue["fields"]["status"]["name"],
                "priority": issue["fields"]["priority"]["name"] if issue["fields"].get("priority") else "None",
                "assignee": issue["fields"]["assignee"]["displayName"] if issue["fields"].get("assignee") else "Unassigned",
                "updated": issue["fields"]["updated"]
            }
            for issue in issues[:10]
        ]
    }
    return json.dumps(test_results, indent=2)


# ── Resource 2: Project and sprint status from JIRA ──
@mcp.resource("environments://status")
def environment_status() -> str:
    """Project status and version information from JIRA."""

    # Get project info
    project_info = jira_request(f"project/{JIRA_CONFIG['project']}")

    if "error" in project_info:
        return json.dumps({"error": project_info["error"]}, indent=2)

    # Get versions/releases
    versions = jira_request(f"project/{JIRA_CONFIG['project']}/versions")

    # Get recent activity - issues updated in last 7 days
    jql = f'project = {JIRA_CONFIG["project"]} AND updated >= -7d ORDER BY updated DESC'
    recent_activity = jira_search(jql, ["summary", "status", "updated"], max_results=5)

    env_status = {
        "project": {
            "key": project_info.get("key"),
            "name": project_info.get("name"),
            "description": project_info.get("description", "No description"),
            "lead": project_info.get("lead", {}).get("displayName", "Unknown"),
            "url": f"{JIRA_CONFIG['base_url']}/browse/{JIRA_CONFIG['project']}"
        },
        "versions": [
            {
                "name": v.get("name"),
                "released": v.get("released", False),
                "release_date": v.get("releaseDate", "Not set"),
                "description": v.get("description", "")
            }
            for v in (versions if isinstance(versions, list) else versions.get("values", []))[:5]
        ],
        "recent_activity": {
            "issues_updated_last_7_days": recent_activity.get("total", 0),
            "latest_updates": [
                {
                    "key": issue["key"],
                    "summary": issue["fields"]["summary"],
                    "status": issue["fields"]["status"]["name"],
                    "updated": issue["fields"]["updated"]
                }
                for issue in recent_activity.get("issues", [])[:5]
            ]
        },
        "health": "healthy" if recent_activity.get("total", 0) > 0 else "inactive",
        "timestamp": datetime.now().isoformat()
    }
    return json.dumps(env_status, indent=2)


# ── Resource 3: Open bugs from JIRA ──
@mcp.resource("bugs://open")
def open_bugs() -> str:
    """All currently open bugs from JIRA VWO project with priority breakdown."""

    # JQL for open bugs
    jql = f'project = {JIRA_CONFIG["project"]} AND type = Bug AND status NOT IN (Done, Closed, Resolved) ORDER BY priority DESC, created DESC'

    fields = ["summary", "status", "priority", "assignee", "created", "updated", "components", "labels"]
    result = jira_search(jql, fields, max_results=100)

    if "error" in result:
        return json.dumps({"error": result["error"], "jql": jql}, indent=2)

    issues = result.get("issues", [])
    total = result.get("total", 0)

    # Group by priority
    by_priority = {"Highest": [], "High": [], "Medium": [], "Low": [], "Lowest": []}

    for issue in issues:
        priority = issue["fields"]["priority"]["name"] if issue["fields"].get("priority") else "Medium"
        created = issue["fields"]["created"]
        created_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
        age_days = (datetime.now(created_date.tzinfo) - created_date).days

        bug_data = {
            "id": issue["key"],
            "title": issue["fields"]["summary"],
            "status": issue["fields"]["status"]["name"],
            "assignee": issue["fields"]["assignee"]["displayName"] if issue["fields"].get("assignee") else "Unassigned",
            "age_days": age_days,
            "created": created,
            "components": [c["name"] for c in issue["fields"].get("components", [])],
            "url": f"{JIRA_CONFIG['base_url']}/browse/{issue['key']}"
        }

        if priority in by_priority:
            by_priority[priority].append(bug_data)
        else:
            by_priority["Medium"].append(bug_data)

    # Calculate age stats
    ages = [b["age_days"] for bugs in by_priority.values() for b in bugs]

    bugs_summary = {
        "project": JIRA_CONFIG["project"],
        "timestamp": datetime.now().isoformat(),
        "total_open": total,
        "by_priority": {
            "highest": len(by_priority["Highest"]),
            "high": len(by_priority["High"]),
            "medium": len(by_priority["Medium"]),
            "low": len(by_priority["Low"]),
            "lowest": len(by_priority["Lowest"])
        },
        "critical_bugs": by_priority["Highest"][:5],
        "high_bugs": by_priority["High"][:5],
        "oldest_unresolved_days": max(ages) if ages else 0,
        "avg_age_days": round(sum(ages) / len(ages), 1) if ages else 0,
        "unassigned_count": sum(1 for bugs in by_priority.values() for b in bugs if b["assignee"] == "Unassigned"),
        "jira_filter_url": f"{JIRA_CONFIG['base_url']}/issues/?jql={jql.replace(' ', '%20')}"
    }
    return json.dumps(bugs_summary, indent=2)


# ── Resource 4: Sprint/Project metrics from JIRA ──
@mcp.resource("metrics://sprint")
def sprint_metrics() -> str:
    """Current sprint and project QA metrics from JIRA."""

    project = JIRA_CONFIG["project"]

    # Get issues created this sprint/last 2 weeks
    two_weeks_ago = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")

    # All issues in current sprint window
    jql_total = f'project = {project} AND created >= "{two_weeks_ago}"'
    total_result = jira_search(jql_total, ["key"], max_results=1)

    # Bugs found this sprint
    jql_bugs_found = f'project = {project} AND type = Bug AND created >= "{two_weeks_ago}"'
    bugs_found = jira_search(jql_bugs_found, ["key", "status", "assignee"], max_results=100)

    # Bugs resolved this sprint
    jql_bugs_fixed = f'project = {project} AND type = Bug AND status IN (Done, Closed, Resolved) AND resolved >= "{two_weeks_ago}"'
    bugs_fixed = jira_search(jql_bugs_fixed, ["key"], max_results=100)

    # Issues by assignee
    jql_by_assignee = f'project = {project} AND created >= "{two_weeks_ago}" AND assignee IS NOT EMPTY'
    by_assignee_result = jira_search(jql_by_assignee, ["assignee", "issuetype"], max_results=200)

    # Count by team member
    team_stats = {}
    for issue in by_assignee_result.get("issues", []):
        assignee = issue["fields"]["assignee"]["displayName"] if issue["fields"].get("assignee") else "Unassigned"
        issue_type = issue["fields"]["issuetype"]["name"] if issue["fields"].get("issuetype") else "Unknown"

        if assignee not in team_stats:
            team_stats[assignee] = {"issues": 0, "bugs": 0}
        team_stats[assignee]["issues"] += 1
        if issue_type == "Bug":
            team_stats[assignee]["bugs"] += 1

    # Get issue types breakdown
    jql_types = f'project = {project} AND created >= "{two_weeks_ago}"'
    types_result = jira_search(jql_types, ["issuetype", "status"], max_results=200)

    type_counts = {}
    status_counts = {}
    for issue in types_result.get("issues", []):
        itype = issue["fields"]["issuetype"]["name"]
        status = issue["fields"]["status"]["name"]
        type_counts[itype] = type_counts.get(itype, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1

    done_count = status_counts.get("Done", 0) + status_counts.get("Closed", 0) + status_counts.get("Resolved", 0)
    total_issues = types_result.get("total", 0)

    metrics = {
        "project": project,
        "period": f"Last 14 days (since {two_weeks_ago})",
        "timestamp": datetime.now().isoformat(),
        "issues": {
            "total_created": total_result.get("total", 0),
            "by_type": type_counts,
            "by_status": status_counts
        },
        "completion_rate": f"{(done_count/total_issues*100):.1f}%" if total_issues > 0 else "N/A",
        "bugs": {
            "found_this_period": bugs_found.get("total", 0),
            "fixed_this_period": bugs_fixed.get("total", 0),
            "net_new": bugs_found.get("total", 0) - bugs_fixed.get("total", 0)
        },
        "team_performance": [
            {
                "name": name,
                "issues_worked": stats["issues"],
                "bugs_filed": stats["bugs"]
            }
            for name, stats in sorted(team_stats.items(), key=lambda x: x[1]["issues"], reverse=True)[:10]
        ],
        "jira_dashboard_url": f"{JIRA_CONFIG['base_url']}/secure/Dashboard.jspa"
    }
    return json.dumps(metrics, indent=2)


# ── Resource 5: Component/Module breakdown from JIRA ──
@mcp.resource("coverage://module/{module_name}")
def module_coverage(module_name: str) -> str:
    """Issue statistics for a specific component/module in JIRA."""

    project = JIRA_CONFIG["project"]

    # If asking for all modules, get component list
    if module_name.lower() in ["all", "list", "components"]:
        components = jira_request(f"project/{project}/components")
        if "error" in components:
            return json.dumps({"error": components["error"]}, indent=2)

        return json.dumps({
            "project": project,
            "available_components": [
                {
                    "name": c.get("name"),
                    "description": c.get("description", "No description"),
                    "lead": c.get("lead", {}).get("displayName", "No lead") if c.get("lead") else "No lead"
                }
                for c in (components if isinstance(components, list) else [])
            ],
            "hint": "Use coverage://module/{component_name} to get stats for a specific component"
        }, indent=2)

    # Search for issues in this component
    jql = f'project = {project} AND component = "{module_name}"'
    fields = ["summary", "status", "issuetype", "priority", "created", "resolved"]
    result = jira_search(jql, fields, max_results=100)

    if "error" in result:
        # Try without component filter - maybe it's a label
        jql_label = f'project = {project} AND labels = "{module_name}"'
        result = jira_search(jql_label, fields, max_results=100)

        if "error" in result or result.get("total", 0) == 0:
            # Get available components
            components = jira_request(f"project/{project}/components")
            comp_names = [c.get("name") for c in (components if isinstance(components, list) else [])]

            return json.dumps({
                "error": f"Component/label '{module_name}' not found or has no issues",
                "available_components": comp_names,
                "hint": "Try one of the available components listed above"
            }, indent=2)

    issues = result.get("issues", [])
    total = result.get("total", 0)

    # Calculate stats
    status_counts = {}
    type_counts = {}
    priority_counts = {}

    for issue in issues:
        status = issue["fields"]["status"]["name"]
        itype = issue["fields"]["issuetype"]["name"]
        priority = issue["fields"]["priority"]["name"] if issue["fields"].get("priority") else "None"

        status_counts[status] = status_counts.get(status, 0) + 1
        type_counts[itype] = type_counts.get(itype, 0) + 1
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    done_count = status_counts.get("Done", 0) + status_counts.get("Closed", 0) + status_counts.get("Resolved", 0)
    open_count = total - done_count

    return json.dumps({
        "module": module_name,
        "project": project,
        "timestamp": datetime.now().isoformat(),
        "total_issues": total,
        "completion_stats": {
            "done": done_count,
            "open": open_count,
            "completion_rate": f"{(done_count/total*100):.1f}%" if total > 0 else "N/A"
        },
        "by_status": status_counts,
        "by_type": type_counts,
        "by_priority": priority_counts,
        "health": "good" if open_count < done_count else "needs_attention",
        "jira_url": f"{JIRA_CONFIG['base_url']}/issues/?jql={jql.replace(' ', '%20').replace('\"', '%22')}"
    }, indent=2)


# ── Bonus Resource: Quick project summary ──
@mcp.resource("project://summary")
def project_summary() -> str:
    """Quick summary of the VWO project from JIRA."""

    project = JIRA_CONFIG["project"]

    # Open issues
    jql_open = f'project = {project} AND status NOT IN (Done, Closed, Resolved)'
    open_result = jira_search(jql_open, ["key"], max_results=1)

    # Closed this week
    jql_closed = f'project = {project} AND status IN (Done, Closed, Resolved) AND resolved >= -7d'
    closed_result = jira_search(jql_closed, ["key"], max_results=1)

    # Created this week
    jql_created = f'project = {project} AND created >= -7d'
    created_result = jira_search(jql_created, ["key"], max_results=1)

    # High priority open
    jql_high = f'project = {project} AND priority IN (Highest, High) AND status NOT IN (Done, Closed, Resolved)'
    high_result = jira_search(jql_high, ["key", "summary", "assignee"], max_results=5)

    return json.dumps({
        "project": project,
        "timestamp": datetime.now().isoformat(),
        "snapshot": {
            "total_open": open_result.get("total", 0),
            "closed_this_week": closed_result.get("total", 0),
            "created_this_week": created_result.get("total", 0),
            "high_priority_open": high_result.get("total", 0)
        },
        "high_priority_issues": [
            {
                "key": issue["key"],
                "summary": issue["fields"]["summary"],
                "assignee": issue["fields"]["assignee"]["displayName"] if issue["fields"].get("assignee") else "Unassigned"
            }
            for issue in high_result.get("issues", [])
        ],
        "jira_url": f"{JIRA_CONFIG['base_url']}/browse/{project}"
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
