# Test Setup Guide

## Quick Start

### 1. Install Test Dependencies

```bash
pip install pytest pytest-cov pytest-mock
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
pytest --version
```

You should see: `pytest 7.4.x` or higher

### 3. Run Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=providers --cov=config --cov-report=html
```

## Test Structure Created

```
tests/
├── __init__.py              ✅ Test package
├── README.md                ✅ Comprehensive guide
├── SETUP.md                 ✅ This file
├── conftest.py              ✅ Pytest fixtures
├── pytest.ini               ✅ Root pytest config
├── .env.test                ✅ Test environment vars
├── test_config.py           ✅ Config module tests
├── test_providers.py        ✅ Provider abstraction tests
├── unit/                    ✅ Unit test directory
│   └── __init__.py
├── integration/             ✅ Integration test directory
│   └── __init__.py
└── fixtures/                ✅ Test data directory
    ├── __init__.py
    └── sample_metadata.json ✅ Sample test data
```

## Available Fixtures

### Environment Fixtures
- `mock_env_openai_only` - Environment with only OpenAI key
- `mock_env_gemini_only` - Environment with only Gemini key
- `mock_env_both_providers` - Environment with both keys
- `mock_env_no_providers` - Environment with no keys

### Mock Providers
- `mock_llm_provider` - Mock LLM provider
- `mock_tts_provider` - Mock TTS provider

### Sample Data
- `sample_script` - Sample podcast script
- `sample_show_notes` - Sample show notes
- `sample_metadata` - Sample episode metadata
- `temp_output_dir` - Temporary directory for test outputs

## Example Test

```python
def test_example(mock_env_openai_only, temp_output_dir):
    """Example test using fixtures"""
    from providers import detect_available_providers
    
    # Use environment fixture
    available = detect_available_providers()
    assert "openai" in available
    
    # Use temp directory
    test_file = temp_output_dir / "test.txt"
    test_file.write_text("test")
    assert test_file.exists()
```

## Test Categories

### Unit Tests (`tests/unit/`)
Fast, isolated tests for individual components.

**To create:**
```bash
touch tests/unit/test_openai_provider.py
touch tests/unit/test_gemini_provider.py
touch tests/unit/test_factory.py
```

### Integration Tests (`tests/integration/`)
Slower tests that verify complete workflows.

**To create:**
```bash
touch tests/integration/test_openai_workflow.py
touch tests/integration/test_gemini_workflow.py
touch tests/integration/test_hybrid_workflow.py
```

## Running Specific Tests

```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run tests matching pattern
pytest tests/ -k "provider"

# Run tests with markers
pytest tests/ -m "not slow"
```

## Test Markers

```python
@pytest.mark.slow
def test_long_running():
    """This test takes a while"""
    pass

@pytest.mark.integration
def test_full_workflow():
    """This is an integration test"""
    pass

@pytest.mark.requires_openai
def test_with_openai():
    """This needs real OpenAI key"""
    pass
```

## Coverage Reports

Generate HTML coverage report:
```bash
pytest tests/ --cov=providers --cov=config --cov-report=html
```

View report:
```bash
# On Windows
start htmlcov/index.html

# On Mac/Linux
open htmlcov/index.html
```

## Continuous Integration

Add to `.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=providers --cov=config
```

## Next Steps

1. **Install pytest:** `pip install pytest pytest-cov`
2. **Run existing tests:** `pytest tests/ -v`
3. **Add more tests:** Create files in `tests/unit/` and `tests/integration/`
4. **Aim for coverage:** Target 80%+ test coverage
5. **Set up CI:** Add automated testing on commits

## Troubleshooting

### "No module named pytest"
```bash
pip install pytest
```

### "No tests found"
Make sure files start with `test_` or end with `_test.py`

### "Import errors in tests"
Make sure you're running from the project root:
```bash
cd /path/to/podcast_creator_agent
pytest tests/
```

### "Fixtures not found"
Check that `conftest.py` is in the `tests/` directory

---

**Created**: 2026-04-07  
**Status**: Ready for testing
