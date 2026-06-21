"""
Shared pytest fixtures and configuration for all CrewAI assignments.
"""

import pytest
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from parent .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


@pytest.fixture(scope="session")
def groq_api_key():
    """Fixture that provides GROQ_API_KEY or skips test if not available."""
    key = os.getenv("GROQ_API_KEY")
    if not key:
        pytest.skip("GROQ_API_KEY not set")
    return key


@pytest.fixture(scope="session")
def sample_feature():
    """Fixture that provides a sample feature for test case generation."""
    return "User Registration with Email Verification"


@pytest.fixture(scope="session")
def sample_alert_payload():
    """Fixture that provides a sample alert payload for API health checks."""
    import json
    return json.dumps({
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


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
