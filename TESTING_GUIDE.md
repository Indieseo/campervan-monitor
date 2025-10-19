# 🧪 Testing Guide - Quick Reference

## Quick Start

### Run All Tests
```powershell
python tests\run_all_tests.py
```

### Run Specific Test Suite
```powershell
# Database tests only
python tests\run_all_tests.py database

# Scraper tests only
python tests\run_all_tests.py scrapers

# Integration tests only
python tests\run_all_tests.py integration
```

### Run Individual Test File
```powershell
python tests\test_database_models.py
python tests\test_scrapers.py
python tests\test_integration.py
```

---

## Test Coverage

### Database Model Tests (20+ tests)
- ✅ Table creation and schema validation
- ✅ CRUD operations for all models
- ✅ Data integrity and constraints
- ✅ JSON field serialization
- ✅ Query and filtering
- ✅ Timestamp auto-population

### Scraper Tests (25+ tests)
- ✅ Scraper initialization
- ✅ Price extraction (multiple formats)
- ✅ Promotion detection
- ✅ Payment method detection
- ✅ Review extraction
- ✅ Data completeness calculation
- ✅ Navigation strategies and fallbacks
- ✅ Error handling

### Integration Tests (15+ tests)
- ✅ Database-scraper integration
- ✅ Market analysis workflow
- ✅ Alert generation
- ✅ Data quality validation
- ✅ Full end-to-end workflow
- ✅ Concurrent operations

---

## Configuration Testing

### Validate Configuration
```powershell
python -c "from core_config import config; config.print_summary()"
```

### Check Configuration Validity
```powershell
python -c "from core_config import config; is_valid, issues = config.validate(); print('Valid!' if is_valid else '\n'.join(issues))"
```

---

## Continuous Integration

### Pre-Commit Checklist
```powershell
# 1. Run all tests
python tests\run_all_tests.py

# 2. Check for linting errors (if you have flake8)
flake8 scrapers/ database/ tests/

# 3. Check type hints (if you have mypy)
mypy scrapers/ database/

# 4. Run the main application
python run_intelligence.py
```

### Setting Up Git Hooks (Optional)
```powershell
# Create pre-commit hook to run tests
# In .git/hooks/pre-commit:
#!/bin/sh
python tests/run_all_tests.py
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

---

## Writing New Tests

### Database Model Test Template
```python
import unittest
from database.models import CompetitorPrice, get_session

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test database"""
        # Create temp database
        pass
    
    def tearDown(self):
        """Clean up"""
        pass
    
    def test_feature(self):
        """Test your feature"""
        # Arrange
        # Act
        # Assert
        pass
```

### Scraper Test Template
```python
import unittest
from unittest.mock import patch, AsyncMock

class TestNewScraper(unittest.TestCase):
    @patch('scrapers.base_scraper.Page')
    def test_extraction(self, mock_page):
        """Test data extraction"""
        # Mock page response
        mock_page.evaluate = AsyncMock(return_value="test data")
        
        # Test extraction
        # Assert results
        pass
```

---

## Test Best Practices

### Do's ✅
- ✅ Test one thing per test
- ✅ Use descriptive test names
- ✅ Clean up after tests
- ✅ Use temporary databases
- ✅ Mock external dependencies
- ✅ Test both success and failure cases
- ✅ Use setUp() and tearDown()
- ✅ Keep tests independent

### Don'ts ❌
- ❌ Don't test external services (mock them)
- ❌ Don't depend on test order
- ❌ Don't use production database
- ❌ Don't hard-code paths
- ❌ Don't skip cleanup
- ❌ Don't test framework code
- ❌ Don't write giant tests
- ❌ Don't commit failing tests

---

## Troubleshooting

### Tests Failing?

1. **Check Python version**
   ```powershell
   python --version  # Should be 3.9+
   ```

2. **Check dependencies**
   ```powershell
   pip list | findstr "unittest sqlalchemy"
   ```

3. **Check database**
   ```powershell
   # Delete old test databases
   del /Q tests\*.db 2>nul
   ```

4. **Check imports**
   ```powershell
   python -c "import sys; sys.path.insert(0, '.'); import database.models; print('OK')"
   ```

### Common Issues

**Issue:** `ModuleNotFoundError`
```powershell
# Solution: Add project to path
set PYTHONPATH=%CD%
python tests\run_all_tests.py
```

**Issue:** `Database is locked`
```powershell
# Solution: Close all Python processes
taskkill /F /IM python.exe
python tests\run_all_tests.py
```

**Issue:** `asyncio errors on Windows`
```python
# Solution: Add this to test files
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
```

---

## Performance Testing

### Measure Test Execution Time
```powershell
# Time all tests
powershell "Measure-Command { python tests\run_all_tests.py }"

# Time specific suite
powershell "Measure-Command { python tests\test_database_models.py }"
```

### Profile Tests
```powershell
# Install profiler
pip install pytest-profiling

# Run with profiling
python -m pytest tests/ --profile
```

---

## Coverage Analysis

### Install Coverage Tool
```powershell
pip install coverage
```

### Run Tests with Coverage
```powershell
# Run tests and collect coverage
coverage run -m pytest tests/

# Generate report
coverage report

# Generate HTML report
coverage html
# Open htmlcov/index.html
```

### Coverage Goals
- **Unit Tests:** 90%+ coverage
- **Integration Tests:** 80%+ coverage
- **Overall:** 85%+ coverage

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests

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
        run: python tests/run_all_tests.py
```

---

## Test Maintenance

### Regular Maintenance Tasks

**Weekly:**
- ✅ Run all tests
- ✅ Check test coverage
- ✅ Update tests for new features

**Monthly:**
- ✅ Review failing tests
- ✅ Update mock data
- ✅ Refactor slow tests
- ✅ Update test documentation

**Quarterly:**
- ✅ Review test strategy
- ✅ Clean up obsolete tests
- ✅ Update test frameworks
- ✅ Performance optimization

---

## Quick Commands Reference

```powershell
# Run all tests
python tests\run_all_tests.py

# Run specific suite
python tests\run_all_tests.py database

# Run with verbose output
python tests\test_database_models.py -v

# Run specific test class
python -m unittest tests.test_database_models.TestCompetitorPriceModel

# Run specific test method
python -m unittest tests.test_database_models.TestCompetitorPriceModel.test_create_price_record

# List all tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run tests in parallel (if pytest installed)
pytest tests/ -n 4

# Run tests with coverage
coverage run -m pytest tests/ && coverage report
```

---

## Resources

### Documentation
- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/core/pooling.html#using-fifo-vs-lifo)
- [Async Testing](https://docs.python.org/3/library/unittest.html#unittest.IsolatedAsyncioTestCase)

### Best Practices
- [Testing Best Practices](https://realpython.com/python-testing/)
- [Mock Objects](https://docs.python.org/3/library/unittest.mock.html)
- [Test-Driven Development](https://testdriven.io/blog/modern-tdd/)

---

**Last Updated:** October 11, 2025  
**Version:** 1.0

🧪 Happy Testing! 🚀


