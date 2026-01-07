# Configuration Guide

This guide provides detailed instructions for configuring and running the automated AI/LLM red team testing framework.

---

## Table of Contents

- [Quick Setup](#quick-setup)
- [Configuration File](#configuration-file)
- [Environment Variables](#environment-variables)
- [Advanced Configuration](#advanced-configuration)
- [Running Tests](#running-tests)
- [Output and Reporting](#output-and-reporting)
- [Troubleshooting](#troubleshooting)

---

## Quick Setup

### 1. Install Dependencies

```bash
cd scripts
pip install -r config/requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the `scripts/` directory:

```bash
API_ENDPOINT=https://api.example.com/v1/chat/completions
API_KEY=your-secret-api-key
MODEL_NAME=gpt-4
```

### 3. Run Tests

```bash
python examples/runner.py
```

---

## Configuration File

### Basic `config.py`

Create or modify `scripts/config.py` with your target system details:

```python
# Target LLM Configuration
API_ENDPOINT = "https://api.example.com/v1/chat/completions"
API_KEY = "your-api-key-here"  # Or use environment variable
MODEL_NAME = "gpt-4"  # Target model identifier

# Test Configuration
MAX_RETRIES = 3
TIMEOUT = 30  # seconds
REQUEST_DELAY = 1  # seconds between requests

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "test_results.log"

# Test Selection
ENABLE_TESTS = [
    "prompt_injection",
    "safety_bypass",
    "data_exposure",
    "tool_misuse",
    "fuzzing",
    "integrity"
]
```

### Configuration Parameters

| Parameter       | Type   | Default            | Description                                     |
| --------------- | ------ | ------------------ | ----------------------------------------------- |
| `API_ENDPOINT`  | string | required           | Target LLM API endpoint URL                     |
| `API_KEY`       | string | required           | Authentication key for API                      |
| `MODEL_NAME`    | string | required           | Model identifier (e.g., "gpt-4", "claude-3")    |
| `MAX_RETRIES`   | int    | 3                  | Number of retry attempts for failed requests    |
| `TIMEOUT`       | int    | 30                 | Request timeout in seconds                      |
| `REQUEST_DELAY` | float  | 1.0                | Delay between requests to avoid rate limiting   |
| `LOG_LEVEL`     | string | "INFO"             | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE`      | string | "test_results.log" | Path to log file                                |
| `ENABLE_TESTS`  | list   | all tests          | List of test categories to run                  |

---

## Environment Variables

### Using `.env` File (Recommended)

For security, use environment variables instead of hardcoding credentials in `config.py`.

#### 1. Create `scripts/.env`

```bash
# API Configuration
API_ENDPOINT=https://api.openai.com/v1/chat/completions
API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
MODEL_NAME=gpt-4

# Test Configuration
MAX_RETRIES=3
TIMEOUT=30
REQUEST_DELAY=1

# Logging
LOG_LEVEL=INFO
LOG_FILE=test_results.log
```

## 2. Update `config.py` to load from environment

```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Configuration
API_ENDPOINT = os.getenv("API_ENDPOINT")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

# Test Configuration
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT = int(os.getenv("TIMEOUT", "30"))
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.0"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "test_results.log")
```

## 3. Add `.env` to `.gitignore`

```bash
echo ".env" >> .gitignore
```

### Provider-Specific Examples

#### OpenAI

```bash
API_ENDPOINT=https://api.openai.com/v1/chat/completions
API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
MODEL_NAME=gpt-4
```

#### Anthropic (Claude)

```bash
API_ENDPOINT=https://api.anthropic.com/v1/messages
API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
MODEL_NAME=claude-3-opus-20240229
```

#### Azure OpenAI

```bash
API_ENDPOINT=https://your-resource.openai.azure.com/openai/deployments/your-deployment/chat/completions?api-version=2024-02-15-preview
API_KEY=xxxxxxxxxxxxxxxxxxxxx
MODEL_NAME=gpt-4
```

#### Local/Self-Hosted Models

```bash
API_ENDPOINT=http://localhost:8000/v1/chat/completions
API_KEY=none
MODEL_NAME=llama-2-7b
```

---

## Advanced Configuration

### Custom Headers

Add custom headers for authentication or tracking:

```python
CUSTOM_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "X-Request-ID": "red-team-test",
    "User-Agent": "AI-RedTeam-Framework/1.0"
}
```

### Proxy Configuration

Route requests through a proxy:

```python
PROXY_CONFIG = {
    "http": "http://proxy.example.com:8080",
    "https": "https://proxy.example.com:8080"
}
```

### Rate Limiting

Configure rate limiting to avoid API throttling:

```python
RATE_LIMIT = {
    "requests_per_minute": 60,
    "requests_per_day": 10000,
    "retry_after_seconds": 60
}
```

### Test Customization

Enable/disable specific tests or adjust severity:

```python
TEST_CONFIG = {
    "prompt_injection": {
        "enabled": True,
        "severity_threshold": "medium",  # low, medium, high, critical
        "max_attempts": 100
    },
    "safety_bypass": {
        "enabled": True,
        "severity_threshold": "high",
        "max_attempts": 50
    },
    "data_exposure": {
        "enabled": True,
        "severity_threshold": "critical",
        "max_attempts": 75
    }
}
```

---

## Running Tests

### Run All Tests

```bash
python examples/runner.py
```

### Run Specific Test Category

```bash
python examples/runner.py --test prompt_injection
python examples/runner.py --test safety_bypass
python examples/runner.py --test data_exposure
```

### Run Multiple Categories

```bash
python examples/runner.py --test prompt_injection,safety_bypass,data_exposure
```

### Use Custom Configuration File

```bash
python examples/runner.py --config my_custom_config.py
```

### Verbose Output

```bash
python examples/runner.py --verbose
```

### Debug Mode

```bash
python examples/runner.py --debug
```

### Save Results to Custom Location

```bash
python examples/runner.py --output /path/to/results/
```

### Dry Run (Preview Tests)

```bash
python examples/runner.py --dry-run
```

---

## Output and Reporting

### Output Files

Test results are saved to multiple locations:

| File/Directory        | Format | Description                            |
| --------------------- | ------ | -------------------------------------- |
| `test_results.log`    | Text   | Detailed execution log with timestamps |
| `reports/json/`       | JSON   | Machine-readable test results          |
| `reports/html/`       | HTML   | Human-readable HTML reports            |
| `reports/summary.txt` | Text   | Executive summary of findings          |

### Report Structure

#### JSON Report

```json
{
  "test_run_id": "20250630-124530",
  "timestamp": "2025-06-30T12:45:30Z",
  "model": "gpt-4",
  "total_tests": 150,
  "passed": 120,
  "failed": 30,
  "findings": [
    {
      "test_case": "prompt_injection_001",
      "severity": "high",
      "status": "failed",
      "description": "Model revealed system prompt",
      "payload": "Ignore previous instructions...",
      "response": "You are a helpful assistant..."
    }
  ]
}
```

#### HTML Report

- Interactive dashboard with charts
- Filterable findings by severity
- Detailed test case results
- Recommendations for remediation

### Console Output

Real-time progress indicators:

```text
Running AI/LLM Red Team Tests...
[=====>    ] 50% | Prompt Injection (25/50)

✓ test_prompt_injection_001 - PASSED
✗ test_prompt_injection_002 - FAILED (High Severity)
✓ test_prompt_injection_003 - PASSED
...
```

---

## Troubleshooting

### Common Issues

#### API Connection Errors

**Error:**

```text
ConnectionError: Failed to connect to API endpoint
```

**Solution:**

- Verify `API_ENDPOINT` is correct
- Check network connectivity
- Confirm firewall/proxy settings

#### Authentication Failures

**Error:**

```text
AuthenticationError: Invalid API key
```

**Solution:**

- Verify `API_KEY` is correct and active
- Check API key permissions
- Ensure key hasn't expired

#### Rate Limit Errors

**Error:**

```text
RateLimitError: Too many requests
```

**Solution:**

- Increase `REQUEST_DELAY` in config
- Reduce concurrent tests
- Use rate limiting configuration

#### Timeout Issues

**Error:**

```text
TimeoutError: Request timed out after 30s
```

**Solution:**

- Increase `TIMEOUT` value
- Check API service status
- Verify network latency

### Debug Mode

Enable detailed logging:

```python
LOG_LEVEL = "DEBUG"
```

Or run with debug flag:

```bash
python runner.py --debug
```

### Getting Help

- Check [Issues](https://github.com/shiva108/ai-llm-red-team-handbook/issues) for known problems
- Review test logs in `test_results.log`
- Enable debug mode for detailed diagnostics

---

## Best Practices

### Security

- ✅ Use `.env` files for credentials
- ✅ Add `.env` to `.gitignore`
- ✅ Rotate API keys regularly
- ✅ Use minimum required permissions
- ❌ Never commit credentials to version control

### Performance

- Use appropriate `REQUEST_DELAY` to avoid rate limiting
- Run tests during off-peak hours for production systems
- Use `--dry-run` to preview tests before execution
- Consider running test categories separately for large test suites

### Reporting

- Save reports with timestamps for historical tracking
- Export findings to client-ready formats
- Map findings to OWASP/MITRE frameworks
- Document false positives for future reference

---

## Additional Resources

- [Main README](../../README.md)
- [Field Manual](../../docs/AI_LLM%20Red%20Team%20Field%20Manual.md)
