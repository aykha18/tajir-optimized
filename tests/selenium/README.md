# Selenium Test Suite - Tajir POS

This directory contains end-to-end regression tests for Tajir POS using Selenium + PyTest.

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Running Tests

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Run all tests**:
   ```bash
   pytest -q --maxfail=1 --html=tests/selenium/report.html --self-contained-html
   ```

3. **Run specific test categories**:
   ```bash
   # Smoke tests only
   pytest -k "smoke"
   
   # Employee tests only
   pytest -k "employees"
   
   # Billing tests only
   pytest -k "billing"
   ```

## 📁 Test Structure

### Core Test Files
- **`conftest.py`**: PyTest fixtures (WebDriver, base URL, helpers)
- **`test_smoke.py`**: Basic functionality tests (login, app shell)
- **`test_employees.py`**: Employee CRUD operations
- **`test_billing.py`**: Billing page functionality

### Test Categories

#### 🔥 Smoke Tests (`test_smoke.py`)
- **Login Page**: Verifies login form loads correctly
- **App Shell**: Ensures navigation and basic UI elements work

#### 👥 Employee Tests (`test_employees.py`)
- **CRUD Operations**: Create, read, update employee records
- **Form Validation**: Input field validation and error handling
- **Data Persistence**: Verify data saves and loads correctly

#### 💰 Billing Tests (`test_billing.py`)
- **Page Load**: Billing form initialization
- **Form Elements**: Verify all billing components are present
- **Navigation**: Billing section accessibility

## ⚙️ Configuration

### Environment Variables
- **`BASE_URL`**: Override default URL (default: `http://localhost:5000`)
- **`PYTEST_ADDOPTS`**: Additional pytest options

### Browser Configuration
- **Headless Mode**: Enabled by default for CI/CD
- **Window Size**: 1400x900
- **Chrome Options**: Optimized for stability

## 📊 Test Reports

### HTML Report
- **Location**: `tests/selenium/report.html`
- **Features**: Self-contained, detailed test results
- **Includes**: Screenshots, error details, test timing

### Console Output
- **Verbose Mode**: `pytest -v`
- **Quiet Mode**: `pytest -q`
- **Stop on First Failure**: `pytest --maxfail=1`

## 🛠️ Troubleshooting

### Common Issues

1. **WebDriver Not Found**
   - Selenium Manager automatically downloads drivers
   - Ensure Chrome/Firefox is installed

2. **Element Not Found**
   - Check if app is running on correct port
   - Verify element selectors haven't changed

3. **Test Timeouts**
   - Increase wait times in test files
   - Check application performance

### Debug Mode
```bash
# Run with detailed output
pytest -v -s

# Run single test
pytest -k "test_login_page_loads" -v -s
```

## 🔧 Maintenance

### Cleaning Up
```bash
# Remove test artifacts
Remove-Item -Path "tests\selenium\__pycache__" -Recurse -Force
Remove-Item -Path "tests\selenium\report.html" -Force

# Clear logs
Clear-Content -Path "logs\errors.log"
```

### Best Practices
- Keep tests independent and isolated
- Use unique test data to avoid conflicts
- Add proper error handling and assertions
- Document complex test scenarios
- Regular cleanup of test artifacts


