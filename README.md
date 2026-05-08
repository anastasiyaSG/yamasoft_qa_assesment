# Roadtrippers QA Automation Assessment

## Overview

This repository contains my submission for the Automation QA Engineer technical assessment for Roadpass Digital.

The goal of the assessment was not only to automate several test scenarios, but also to demonstrate:

* test architecture decisions
* maintainability considerations
* scalability awareness
* CI/CD understanding
* practical trade-offs within a limited time budget

The implementation focuses on building a clean and extensible automation foundation rather than maximizing the number of automated scenarios.

---

# Time Spent

| Part   | Description                                       | Approx. Time |
| ------ | ------------------------------------------------- | ------------ |
| Part 1 | UI automation framework and test implementation   | ~5 hours     |
| Part 2 | CI/CD strategy research and implementation        | ~2 hours     |
| Part 3 | Performance/API investigation and experimentation | ~2 hours     |

**Total approximate time spent: ~9 hours**

---

# Deliverables

## Part 1 — Automated Test Implementation

* `tests/test_create_trip_PART_1.py`
* `reports/report_PART_1.html`

## Part 2 — CI/CD Integration Strategy

* `CICD_part_2/`

## Part 3 — Optional Bonus

* `tests/test_API_PART_3.py`

---

# Technical Approach & Decisions

## Framework Selection

I selected **Playwright with Python + pytest** for this assessment.

### Why Playwright

I would currently recommend Playwright for modern web automation because it provides:

* strong auto-waiting capabilities
* stable browser automation APIs
* excellent debugging support (traces, screenshots, videos)
* parallel execution support
* modern locator strategies
* reliable handling of dynamic frontend applications

### Why Python

Python is currently my strongest automation language and allowed me to focus primarily on framework design, maintainability, readability, and testing strategy within the assessment time constraints.

---

# Implementation Strategy

The implementation intentionally focuses on realistic automation engineering practices rather than only creating several passing tests.

The framework includes:

* Page Object Model (POM)
* separation between pages, actions, and assertions
* reusable fixtures and teardown handling
* HTML reporting and Playwright traces
* retry support
* parallel execution support
* environment-based configuration
* UI and API test separation

## Page Object Strategy

All locators and UI interactions are isolated inside Page Object classes to improve maintainability and minimize test impact when UI changes occur.

## Actions Layer

An additional actions/business workflow layer was introduced to:

* encapsulate reusable business logic
* improve readability
* centralize logging and exception handling
* reduce duplicated workflows across tests

## Assertion Strategy

Tests primarily follow the AAA pattern:

* Arrange
* Act
* Assert

to keep scenarios readable and simplify failure analysis.

## Stability & Synchronization

The framework avoids arbitrary `sleep()` usage inside tests and instead relies on:

* Playwright auto-waiting
* explicit waits
* stable locator strategies
* proper synchronization patterns

to reduce flaky execution behavior and improve execution stability.

---

# Scope & Trade-Offs

Given the assessment time constraints, I intentionally prioritized:

* framework structure
* maintainability
* scalability
* debugging support
* clean abstraction layers

over exhaustive functional coverage.

The goal was to demonstrate how I would structure a realistic automation project foundation rather than maximize the number of test cases within limited time.

Some areas intentionally kept simpler:

* advanced test data factories
* complete CI implementation
* large-scale parallel environment management
* advanced reporting customization

---

# AI Usage & Practical Constraints

I prefer being transparent about tooling usage during the assessment.

The CircleCI configuration and CI/CD strategy research required additional learning because my direct hands-on experience is currently stronger with:

* GitHub Actions
* Bitbucket Pipelines

rather than CircleCI specifically.

AI assistance was used primarily for:

* accelerating CircleCI syntax generation
* validating configuration structure
* researching best practices

while still reviewing and understanding the generated implementation before including it in the submission.

The goal was to keep the solution realistic and aligned with my actual engineering understanding rather than artificially over-engineering the implementation.

---

# Real-World Testing Considerations

For reliable parallel execution in real environments, additional considerations would be required such as:

* dedicated test accounts
* isolated test data
* environment stability
* avoiding shared-state collisions
* environment reservation during execution

especially for UI-heavy end-to-end automation.

Test data is currently centralized under the utilities layer, but could be further expanded into dedicated factories or fixture-driven datasets in a production-scale framework.

---

# Quick Start

## Prerequisites

* Python 3.10 or higher
* pip (Python package manager)

---

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

#### Windows (PowerShell)

```powershell
.\venv\Scripts\Activate.ps1
```

#### Windows (Command Prompt)

```cmd
venv\Scripts\activate.bat
```

#### macOS/Linux

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
playwright install
```

### 5. Configure Environment Variables

Update the `.env` file:

```ini
BASE_URL=https://maps.roadtrippers.com/
USERNAME=your_test_username
PASSWORD=your_test_password
```

### 6. Run Tests

```bash
pytest tests/ -v
```

---

# Running Tests

## Run All Tests

```bash
pytest tests/ -v
```

## Run Smoke Tests

```bash
pytest -m smoke -v
```

## Run Tests with HTML Report

```bash
pytest tests/ -v --html=reports/report.html --self-contained-html
```

## Run Tests in Parallel

Note: parallel execution support is included at framework level, but fully isolated execution would require multiple dedicated test accounts and isolated test data management in a real CI environment.

```bash
pytest tests/ -n 4
```

## Run Tests with Retries

```bash
pytest tests/ --reruns 2 --reruns-delay 1
```

---

# Reporting & Debugging

The framework includes:

* HTML reports
* Playwright traces
* screenshots for debugging support

These artifacts help improve failure investigation and reduce debugging time, especially in CI environments.

---

# Metrics I Would Track in Real CI/CD Usage

To evaluate long-term automation effectiveness, I would track:

| Metric                 | Why It Matters                                       |
| ---------------------- | ---------------------------------------------------- |
| Test pass/fail rate    | Measures overall suite health and release confidence |
| Flaky test frequency   | Helps identify unstable automation reducing CI trust |
| Average execution time | Tracks pipeline scalability and feedback speed       |
| Defect escape rate     | Measures how many issues bypass automated validation |

Additional useful metrics:

* test coverage across critical workflows
* failure categorization trends
* mean time to diagnose failures
* automation maintenance effort over time
* CI pipeline stability trends

---

# Future Improvements & Known Constraints

The API and performance-related examples included in Part 3 should be considered exploratory rather than production-ready implementations.

Due to assessment time constraints and external application dependencies (including dynamic request behavior and reCAPTCHA protections), the focus was placed primarily on demonstrating:

* framework structure
* API investigation approach
* traffic inspection strategy
* initial performance testing direction

rather than building a fully stabilized API/performance testing solution.

In a production environment, the next improvements would include:

* dedicated API client abstraction
* authenticated request handling
* request/response schema validation
* mocked or isolated test environments
* stable test data management
* reusable contract validation
* improved observability and logging
* more advanced k6 performance scenarios and thresholds

The current implementation should therefore be viewed as a foundational starting point intended to demonstrate technical direction and testing strategy rather than complete production coverage.
