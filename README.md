# Roadtrippers QA Automation Assessment

## Overview

This is my submission for the Automation QA Engineer technical assessment for Roadpass Digital.

The goal was to automate key trip planning scenarios while demonstrating how I approach framework design, test stability, and CI strategy. I focused on building a clean, maintainable foundation rather than maximising the number of test cases — the structure reflects how I'd start a real project.

---

## Time Spent

| Part   | Description                                       | Approx. Time |
| ------ | ------------------------------------------------- | ------------ |
| Part 1 | UI automation framework and test implementation   | ~5 hours     |
| Part 2 | CI/CD strategy research and implementation        | ~2 hours     |
| Part 3 | API investigation and experimentation             | ~3 hours     |

**Total: ~9 hours** — roughly one working day, scoped to show direction over completeness.

---

## Deliverables

| Part | Files |
| ---- | ----- |
| Part 1 — UI Tests | `tests/test_create_trip_PART_1.py`, `pages/`, `actions/trip_creation.py`, `reports/` |
| Part 2 — CI/CD Strategy | `CICD_PART_2/CICD_STRATEGY.md`, `CICD_PART_2/config.yml` |
| Part 3 — API Bonus | `tests/test_API_PART_3.py`, `actions/http_session.py` |

---

## Project Structure

```
├── actions/
│   ├── trip_creation.py           # Fixtures and shared setup helpers for UI tests
│   └── http_session.py            # aiohttp session fixtures for API tests
├── pages/
│   ├── login_page.py              # Login page object
│   ├── my_trips_page.py           # My Trips page object
│   └── trip_creation_page.py      # Trip creation page object
├── tests/
│   ├── test_create_trip_PART_1.py # UI test suite
│   └── test_API_PART_3.py         # API test suite (skipped — see Part 3 notes)
├── helpers/
│   └── helpers.py                 # Shared utilities (safe_click, toast handling)
├── conftest.py                    # Pytest hooks and fixture imports
├── pytest.ini                     # Pytest configuration
└── CICD_PART_2/
    ├── CICD_STRATEGY.md           # CI/CD strategy document
    └── config.yml                 # CircleCI configuration
```

---

## Framework & Technical Decisions

### Why Playwright + Python

I chose Playwright because it fits this stack well — it handles dynamic React frontends reliably, has strong auto-waiting built in, and the tracing and screenshot tooling makes CI debugging practical. Python is my strongest automation language so it let me focus on design decisions rather than syntax.

### Page Object Model

Pages live in `pages/` and cover login, trip creation, and my trips. Locators use Playwright's semantic APIs (`get_by_role`, `get_by_text`) rather than CSS selectors where possible, which makes them more resilient to DOM changes and easier to read.

```python
# Example from login_page.py
self.login_button = page.get_by_role("link", name="Log in")
self.submit_button = page.get_by_role("button", name="Log in")
```

### Actions / Fixture Layer

Rather than putting setup logic inside tests, I introduced an actions layer (`actions/trip_creation.py`) with composable fixtures for different scenarios. This keeps tests short and focused on assertions, and means adding a new scenario doesn't require duplicating setup code.

The fixture chain looks like this:

```
set_up_create_trip  →  browser + navigation + overlay dismissal
        └── login   →  authentication + pre-test cleanup
                └── trip_with_registration  →  trip creation + teardown
```

Each fixture handles its own teardown with `try/finally`, so browser cleanup and trip deletion happen even when tests fail mid-run.

### Overlay Handling

The app has three overlays that can block interactions: a gist embed, a marketing popup inside an iframe, and a cookie consent banner. These are handled in `_dismiss_overlays()` before any test interaction, with each one individually guarded so a missing overlay doesn't fail the setup.

### Synchronisation Strategy

No `sleep()` calls anywhere in the test or fixture code. All synchronisation uses Playwright's built-in auto-waiting and explicit `expect()` assertions with appropriate timeouts. The `TIMEOUT` constant is defined once per file so it's easy to adjust across the suite.

---

## Test Coverage

### Part 1 — UI Tests (`test_create_trip_PART_1.py`)

| Test | Type | Description |
| ---- | ---- | ----------- |
| `test_create_trip_no_registration` | Smoke | Guest user creates and launches a trip |
| `test_create_trip_with_registration` | Smoke | Logged-in user creates, launches, and verifies trip persists in My Trips |
| `test_create_trip_with_registration_with_stops` | Smoke | Logged-in user adds a waypoint stop before launching |
| `test_create_trip_with_registration_without_destination` | Negative | Form submission with only a date — verifies Launch Trip does not appear |

Each authenticated test deletes its trip in teardown to avoid state bleed between runs.

### Part 3 — API Tests (`test_API_PART_3.py`)

**All API tests are currently skipped.**

The Roadtrippers login endpoint requires a valid Google reCAPTCHA v3 token. I investigated a hybrid approach — using Playwright to execute `grecaptcha.execute()` in a real browser, then seeding the token and session cookie into an `aiohttp` session to complete the login POST. The authentication logic is implemented in `actions/http_session.py` and the test cases are fully written in `test_API_PART_3.py`.

However, the browser phase hits a reliable timeout: `wait_for_function` never sees `grecaptcha` become available, which means token generation doesn't complete. I investigated `networkidle` vs `domcontentloaded` load strategies and headless browser detection mitigations, but couldn't get this stable within the assessment time budget.

The tests cover what I'd expect from a login API:

- HTTP 200 on valid credentials with a valid JSON body
- Expected user fields present (`id`, `username`, `email`, `auth_token`)
- `auth_token` cookie set and matching the body value
- `_session_id` rotation on login (session fixation prevention)
- 4xx responses for wrong password, missing fields, and empty credentials
- `auth_token` accepted as both a cookie and Bearer header on follow-up requests

In a real project this would be resolved by getting a reCAPTCHA bypass token from the backend team for the test environment, or running API tests against a staging environment where the challenge is disabled.

---

## Locator Strategy

Locators follow this priority:

1. `get_by_role` / `get_by_label` — semantic, accessibility-aware, resilient to DOM changes
2. `get_by_text` — for visible content that's stable
3. Scoped CSS selectors — used sparingly in `my_trips_page.py` where semantic locators aren't available

XPath is avoided. `data-testid` attributes would be the preferred approach in a codebase where the team controls the frontend.

---

## Reporting & Debugging

Each test run produces:

- **HTML report** in `reports/` — generated automatically, includes pass/fail status and logs
- **Playwright traces** in `traces/` — one zip per test, captured in teardown regardless of outcome

Traces are the most useful artifact for diagnosing CI failures. To inspect one locally:

```bash
playwright show-trace traces/<test_name>.zip
```

This opens a step-by-step timeline with DOM snapshots, network calls, and console output at each action — much faster than reading logs alone.

---

## AI & Tooling Usage

I used AI assistance in a few specific places and want to be upfront about it:

- **CircleCI configuration**: my hands-on CI experience is stronger with GitHub Actions and Bitbucket Pipelines. I used AI to accelerate syntax generation, then reviewed and understood the output before including it.
- **aiohttp + Playwright hybrid auth**: used AI to validate the cookie-seeding approach and discuss reCAPTCHA workaround strategies.

Everything included was reviewed and understood before submission. I'd rather be honest about where I used tooling than over-represent familiarity.

---

## Known Constraints & Honest Gaps

- **API tests are fully skipped** due to the reCAPTCHA constraint described above. The test logic and fixture architecture are complete — what's missing is a stable way to generate or bypass the token in an automated context.
- **Bare `except:` blocks in `trip_creation_page.py`** suppress errors silently during autocomplete interactions. In production I'd catch specific exceptions and log them with enough context to diagnose failures.
- **No test data factory** — trip details are hardcoded. A factory or fixture-driven dataset would allow data-driven coverage without duplicating test logic.
- **Parallel execution** is configured at the framework level but would need isolated test accounts per worker to avoid shared-state collisions in practice.

---

## What I Would Do Next

| Priority | Item | Reason |
| -------- | ---- | ------ |
| High | Resolve reCAPTCHA for API tests — staging bypass or backend test token | Unblocks the entire API test suite |
| High | Replace bare `except:` blocks with specific exception types and structured logging | Silent failures are hard to diagnose in CI |
| High | Dedicated API client class with auth injected at session level | Reduces duplication and makes API tests easier to maintain |
| Medium | Response schema validation with `jsonschema` or Pydantic | Catches API contract changes before they reach UI tests |
| Medium | Parameterised test data via fixtures or a simple factory | Removes hardcoded values and enables broader coverage |
| Low | `data-testid` attributes on key elements (requires frontend access) | More stable than role/text locators for frequently changing UI |

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip

### Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # macOS/Linux
.\venv\Scripts\Activate.ps1       # Windows PowerShell

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install

# 4. Configure environment variables
cp .env.example .env
# Edit .env and add your credentials
```

**.env file:**
```ini
BASE_URL=https://maps.roadtrippers.com
USERNAME=your_test_username
PASSWORD=your_test_password
```

---

## Running Tests

```bash
# All tests (API tests are skipped automatically)
pytest tests/ -v

# Smoke tests only
pytest -m smoke -v

# With HTML report
pytest tests/ -v --html=reports/report.html --self-contained-html

# With retries for flaky network conditions
pytest tests/ --reruns 2 --reruns-delay 1

# In parallel — requires isolated test accounts per worker in practice
pytest tests/ -n 4
```

---

## CI/CD

See `CICD_PART_2/CICD_STRATEGY.md` for the full strategy and `CICD_PART_2/config.yml` for the pipeline configuration. The short version:

- Smoke tests run first as a fast gate (~3 min)
- Full UI suite runs in parallel if smoke passes (~12 min)
- HTML reports and Playwright traces are stored as CircleCI artifacts for 30 days
- Flaky tests are quarantined with `@pytest.mark.flaky` and tracked separately from genuine failures

---

## Metrics I Would Track

| Metric | Why it matters | How I'd collect it |
| ------ | -------------- | ------------------ |
| Pass/fail rate per suite | Overall health signal | pytest-html + CircleCI test results tab |
| Flaky test rate | CI trust — teams start ignoring failures above ~10% | pytest-rerunfailures log + manual tagging |
| Execution time trend | Slow feedback reduces the value of automation | CircleCI Insights API |
| Defect escape rate | Measures whether automation is catching real bugs | Post-release bug tagging vs coverage map |