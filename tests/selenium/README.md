# Selenium Regression Suite

This directory contains end-to-end regression tests for Tajir POS using Selenium + PyTest.

## Install

```bash
pip install -r requirements.txt
```

## Running locally

1. Ensure the app is running locally at `http://localhost:5000` (e.g., run `start_flask.bat`).
2. Run the tests:

```bash
pytest -q --maxfail=1 --html=tests/selenium/report.html --self-contained-html
```

The first run will download the appropriate WebDriver automatically via `webdriver-manager`.

## Structure
- `conftest.py`: PyTest fixtures (WebDriver, base URL, helpers)
- `test_smoke.py`: Smoke test covering login page and app shell load
- `test_employees.py`: CRUD coverage for Employees
- `test_billing.py`: Create/print bill happy path

## Tips
- Set `BASE_URL` env var to override the default: `http://localhost:5000`
- Use `PYTEST_ADDOPTS=-k "employees"` to run a subset
- Generated HTML report: `tests/selenium/report.html`


