# Tajir POS - Test Suite

**Pre-PostgreSQL Migration Testing**

This directory contains a comprehensive test suite for the Tajir POS application to ensure all functionality is preserved during the PostgreSQL migration.

## 📋 Overview

The test suite covers:
- **Unit Tests**: Individual function and component testing
- **Integration Tests**: End-to-end workflow testing
- **API Tests**: REST API endpoint testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Security vulnerability testing
- **Database Tests**: Database operations and integrity

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Required packages** installed:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov
   ```

### Running Tests

#### Run All Tests
```bash
python tests/run_tests.py
```

#### Run Specific Test Types
```bash
# Unit tests only
python tests/run_tests.py --type unit

# Integration tests only
python tests/run_tests.py --type integration

# API tests only
python tests/run_tests.py --type api

# Performance tests only
python tests/run_tests.py --type performance

# Security tests only
python tests/run_tests.py --type security
```

#### Run with Coverage
```bash
python tests/run_tests.py --coverage
```

#### Run with Verbose Output
```bash
python tests/run_tests.py --verbose
```

#### Generate Test Report
```bash
python tests/run_tests.py --report
```

#### Check Prerequisites Only
```bash
python tests/run_tests.py --check-prereq
```

## 📁 Test Structure

```
tests/
├── README.md                 # This file
├── test_suite.py            # Main test suite
├── run_tests.py             # Test runner
├── api_tests.py             # API endpoint tests
├── performance_tests.py     # Performance tests
├── security_tests.py        # Security tests
├── test_data/               # Test data files
│   ├── sample_products.json
│   ├── sample_customers.json
│   └── sample_bills.json
└── reports/                 # Generated test reports
    ├── coverage/
    └── performance/
```

## 🧪 Test Categories

### 1. Unit Tests (`test_suite.py`)

**Authentication & User Management**
- User login/logout
- Plan status checking
- Feature access control
- Session management

**Product Management**
- Product type CRUD operations
- Product catalog management
- Barcode/QR code functionality
- Pricing and discount handling

**Customer Management**
- Customer CRUD operations
- Customer search and filtering
- Geographic data handling
- Customer history tracking

**Billing System**
- Bill creation and management
- Invoice generation
- Payment processing
- Bill numbering system

**Analytics & Reporting**
- Dashboard metrics
- Financial analytics
- Expense breakdown
- Report generation

**Configuration**
- Shop settings management
- VAT configuration
- Employee management
- Expense tracking

### 2. Integration Tests

**Complete Workflows**
- Customer → Product → Bill workflow
- End-to-end billing process
- Data consistency across modules
- Multi-user scenarios

**Data Integrity**
- Foreign key relationships
- Transaction handling
- Data validation
- Error handling

### 3. API Tests

**REST Endpoints**
- All API endpoints testing
- Request/response validation
- Error handling
- Authentication/authorization

**Data Formats**
- JSON request/response
- File uploads
- Export functionality
- Print generation

### 4. Performance Tests

**Load Testing**
- Large dataset handling
- Concurrent user access
- Database query optimization
- Memory usage monitoring

**Stress Testing**
- High-volume operations
- Resource utilization
- Response time analysis
- Scalability assessment

### 5. Security Tests

**Input Validation**
- SQL injection prevention
- XSS protection
- Input sanitization
- Malicious data handling

**Access Control**
- Unauthorized access prevention
- Session security
- Multi-tenant isolation
- Plan-based restrictions

### 6. Database Tests

**Database Operations**
- Connection management
- Query execution
- Transaction handling
- Data integrity

**Migration Readiness**
- Schema compatibility
- Data type handling
- Index optimization
- Performance baseline

## 📊 Test Reports

### Coverage Report
When running with `--coverage`, the test suite generates:
- **HTML Coverage Report**: `htmlcov/index.html`
- **Terminal Coverage Summary**: Shows line and branch coverage
- **Coverage Data**: `.coverage` file for further analysis

### Performance Report
Performance tests generate:
- **Response Time Analysis**: Average, min, max response times
- **Throughput Metrics**: Requests per second
- **Resource Usage**: CPU, memory, database connections
- **Baseline Comparison**: Pre vs post-migration performance

### Security Report
Security tests generate:
- **Vulnerability Assessment**: Known security issues
- **Input Validation Results**: Malicious input handling
- **Access Control Verification**: Authorization testing
- **Recommendations**: Security improvements needed

## 🔧 Configuration

### Test Environment
Tests run in an isolated environment with:
- **Temporary Database**: Each test uses a fresh SQLite database
- **Mock External Services**: Email, WhatsApp, payment gateways
- **Test Data**: Predefined test datasets
- **Cleanup**: Automatic cleanup after each test

### Test Data
Test data is located in `tests/test_data/`:
- **Sample Products**: Pre-configured product catalog
- **Sample Customers**: Test customer records
- **Sample Bills**: Test invoice data
- **Configuration Files**: Test-specific settings

## 🚨 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure you're in the project root directory
cd /path/to/tailor_pos
python tests/run_tests.py
```

**2. Database Errors**
```bash
# Check if database schema exists
ls database_schema.sql
# Regenerate if needed
python -c "from app import setup_database; setup_database()"
```

**3. Missing Dependencies**
```bash
# Install test dependencies
pip install pytest pytest-cov requests
```

**4. Permission Errors**
```bash
# Make test files executable
chmod +x tests/run_tests.py
chmod +x tests/test_suite.py
```

### Debug Mode
Run tests in debug mode for detailed output:
```bash
python tests/run_tests.py --verbose --type unit
```

## 📈 Metrics & Benchmarks

### Success Criteria
- **Test Coverage**: >90% line coverage
- **Performance**: <1s response time for API calls
- **Security**: 0 critical vulnerabilities
- **Data Integrity**: 100% foreign key constraint compliance

### Baseline Metrics
- **Total Tests**: 150+ test cases
- **API Endpoints**: 50+ endpoints tested
- **Database Operations**: 100+ operations verified
- **Security Checks**: 20+ security scenarios

## 🔄 Continuous Integration

### GitHub Actions
The test suite can be integrated with CI/CD:
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python tests/run_tests.py --report
```

### Pre-commit Hooks
Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: test-suite
        name: Run Test Suite
        entry: python tests/run_tests.py --type unit
        language: system
        pass_filenames: false
```

## 📝 Adding New Tests

### Test Structure
```python
class NewFeatureTests(TajirPOSTestCase):
    """Test new feature functionality"""
    
    def test_new_feature(self):
        """Test new feature"""
        # Arrange
        # Act
        # Assert
        self.assertEqual(expected, actual)
```

### Test Naming Convention
- **Test Classes**: `FeatureNameTests`
- **Test Methods**: `test_specific_functionality`
- **Test Files**: `test_feature_name.py`

### Test Data
Add test data to `tests/test_data/`:
```json
{
  "feature_name": {
    "valid_input": {...},
    "invalid_input": {...},
    "expected_output": {...}
  }
}
```

## 🎯 Migration Checklist

### Pre-Migration Testing
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Performance baseline established
- [ ] Security tests pass
- [ ] Database integrity verified

### Post-Migration Testing
- [ ] Re-run all tests with PostgreSQL
- [ ] Compare performance metrics
- [ ] Verify data integrity
- [ ] Test all API endpoints
- [ ] Validate security measures

## 📞 Support

For test-related issues:
1. Check the troubleshooting section
2. Review test logs and reports
3. Run tests in verbose mode
4. Check prerequisites

---

**Test Suite Version**: 1.0  
**Last Updated**: August 22, 2025  
**Compatible With**: Tajir POS Pre-PostgreSQL Migration
