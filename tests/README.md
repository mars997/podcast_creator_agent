# Tests Directory

This directory contains all test files for the podcast_creator_agent project.

## Structure

```
tests/
├── __init__.py                 # Test package initialization
├── README.md                   # This file
├── conftest.py                 # Pytest configuration and fixtures
├── test_providers.py           # Provider abstraction tests
├── test_config.py              # Configuration module tests
├── integration/                # Integration tests
│   ├── __init__.py
│   ├── test_openai_workflow.py
│   ├── test_gemini_workflow.py
│   └── test_hybrid_workflow.py
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_openai_provider.py
│   ├── test_gemini_provider.py
│   ├── test_factory.py
│   └── test_base.py
└── fixtures/                   # Test fixtures and mock data
    ├── __init__.py
    ├── sample_scripts.py
    ├── sample_metadata.json
    └── mock_responses.py
```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run specific test file
```bash
pytest tests/test_providers.py
```

### Run with coverage
```bash
pytest tests/ --cov=providers --cov-report=html
```

### Run only unit tests
```bash
pytest tests/unit/
```

### Run only integration tests
```bash
pytest tests/integration/
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run tests matching a pattern
```bash
pytest tests/ -k "provider"
```

## Test Categories

### Unit Tests (`tests/unit/`)
Test individual components in isolation:
- Provider classes
- Factory functions
- Configuration loading
- Helper functions

### Integration Tests (`tests/integration/`)
Test complete workflows:
- OpenAI end-to-end podcast generation
- Gemini end-to-end podcast generation
- Hybrid provider workflows
- Episode regeneration

### Validation Tests (`tests/`)
High-level validation:
- Provider abstraction validation
- Configuration validation
- Backward compatibility checks

## Writing Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

### Example Test
```python
import pytest
from providers import create_llm_provider, ProviderConfig

def test_openai_provider_creation():
    """Test OpenAI LLM provider can be created"""
    config = ProviderConfig(
        llm_provider="openai",
        tts_provider="openai"
    )
    provider = create_llm_provider(config)
    
    assert provider.provider_name == "openai"
    assert provider.model_name == "gpt-4.1-mini"
```

### Using Fixtures
```python
def test_with_fixture(mock_openai_response):
    """Test using a fixture from conftest.py"""
    # mock_openai_response is defined in conftest.py
    assert mock_openai_response.status_code == 200
```

## Test Coverage Goals

- [ ] Provider abstraction: 90%+
- [ ] Configuration module: 90%+
- [ ] Factory functions: 100%
- [ ] Integration workflows: 80%+

## Continuous Integration

Tests are run automatically on:
- Every commit (if CI configured)
- Pull requests
- Before releases

## Troubleshooting

### Tests require API keys
Some integration tests require valid API keys. Set them in `.env.test`:
```bash
OPENAI_API_KEY=sk-test-...
GOOGLE_API_KEY=test-...
```

### Mock external calls
Use `@pytest.fixture` and `unittest.mock` to avoid real API calls in unit tests.

### Skip slow tests
```bash
pytest tests/ -m "not slow"
```

Mark slow tests with:
```python
@pytest.mark.slow
def test_long_running():
    pass
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
