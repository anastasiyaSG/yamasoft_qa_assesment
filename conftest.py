"""
Pytest configuration and fixtures for Roadtrippers QA automation.

Fixtures provide:
- Browser setup and teardown
- Page context management
- Test data fixtures
- Common test scenarios (logged-in, guest, etc.)
"""

import pytest
import json
import logging
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import fixtures from actions
from actions.trip_creation import (
    set_up_create_trip,
    login,
    trip_no_registration,
    trip_with_registration,
    trip_with_registration_with_stop,
    trip_without_registration_with_stop
)
from actions.http_sessoion import (
    http_session,pre_auth_session, logged_in_session)

# Pytest hooks for test execution
def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Create reports directory if it doesn't exist
    Path("reports").mkdir(exist_ok=True)
    Path("traces").mkdir(exist_ok=True)
    logging.info("Pytest configuration completed")


def pytest_sessionstart(session):
    """Run at the start of test session."""
    logging.info(f"Starting test session: {session.name}")
    logging.info(f"Base URL: {os.getenv('BASE_URL')}")


def pytest_sessionfinish(session, exitstatus):
    """Run at the end of test session."""
    logging.info(f"Test session finished with exit status: {exitstatus}")


def pytest_runtest_logreport(report):
    """Hook for test result reporting."""
    if report.when == "call":
        if report.outcome == "passed":
            logging.info(f"✓ {report.nodeid} PASSED")
        elif report.outcome == "failed":
            logging.error(f"✗ {report.nodeid} FAILED")
        elif report.outcome == "skipped":
            logging.warning(f"⊘ {report.nodeid} SKIPPED")


