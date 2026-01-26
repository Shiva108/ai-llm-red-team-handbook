# Prompt Injection Tester (PIT) - User Guide

**Version**: 2.0.0
**Architecture**: Sequential 4-Phase Pipeline

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Reference](#command-reference)
- [Configuration](#configuration)
- [Attack Patterns](#attack-patterns)
- [Report Formats](#report-formats)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Introduction

The Prompt Injection Tester (PIT) is a professional security assessment tool for testing Large Language Models (LLMs) against prompt injection vulnerabilities. It features a modern CLI with a sequential 4-phase pipeline architecture designed to prevent concurrency errors while maintaining high performance.

### Key Features

✅ **Sequential 4-Phase Pipeline**: Discovery → Attack → Verification → Reporting
✅ **20+ Built-in Attack Patterns**: Covering OWASP LLM Top 10
✅ **Multiple Report Formats**: JSON, YAML, and professional HTML reports
✅ **Real-time Progress**: Rich TUI with progress bars and spinners
✅ **Authorization Tracking**: Ensures ethical testing practices
✅ **Rate Limiting**: Respects API constraints
✅ **Extensible**: Plugin system for custom patterns

### Architecture

```text
┌─────────────┐
│  Discovery  │  Scan target for injection points
└──────┬──────┘
       │ WAIT (sequential execution)
┌──────▼──────┐
│   Attack    │  Execute attack patterns
└──────┬──────┘
       │ WAIT
┌──────▼──────┐
│Verification │  Analyze responses
└──────┬──────┘
       │ WAIT
┌──────▼──────┐
│  Reporting  │  Generate formatted report
└─────────────┘
```

## Installation

### Prerequisites

- **Python**: 3.10 or higher
- **LLM Endpoint**: Ollama, OpenAI API, or compatible service

### Install from Source

```bash
cd tools/prompt_injection_tester

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Verify installation
pit --help
```

### Install Dependencies Only

```bash
pip install typer rich pydantic httpx pyyaml jinja2
```

## Quick Start

### 1. Test Against Local Ollama

```bash
# Start Ollama (in another terminal)
ollama serve

# Run quick scan
pit scan http://localhost:11434/api/chat --auto

# Specify model
pit scan http://localhost:11434/api/chat --auto --model llama3:latest
```

### 2. Test with Specific Patterns

```bash
# Test single pattern
pit scan http://localhost:11434/api/chat \
  --patterns direct_instruction_override

# Test multiple patterns
pit scan http://localhost:11434/api/chat \
  --patterns direct_instruction_override,role_manipulation,delimiter_confusion
```

### 3. Generate HTML Report

```bash
pit scan http://localhost:11434/api/chat \
  --auto \
  --output report.html
```

## Command Reference

### Main Command: `pit`

```text
pit [OPTIONS] COMMAND [ARGS]...
```

**Global Options:**

- `--version, -v`: Show version and exit
- `--help`: Show help message

### Command: `scan`

Run security assessment against an LLM endpoint.

```bash
pit scan [OPTIONS] TARGET
```

**Arguments:**

- `TARGET`: Target API endpoint URL (required)

**Options:**

| Option            | Short | Description                      | Default        |
| ----------------- | ----- | -------------------------------- | -------------- |
| `--auto`          | `-a`  | Run all phases automatically     | False          |
| `--config PATH`   | `-c`  | Path to configuration YAML file  | None           |
| `--patterns LIST` | `-p`  | Comma-separated list of patterns | Auto-selected  |
| `--model NAME`    | `-m`  | Target model identifier          | Auto-detected  |
| `--output PATH`   | `-o`  | Output file path for results     | Auto-generated |
| `--verbose`       | `-v`  | Enable verbose output            | False          |

**Examples:**

```bash
# Basic auto scan
pit scan http://localhost:11434/api/chat --auto

# With configuration file
pit scan http://localhost:11434/api/chat --config config.yaml

# Specific patterns and model
pit scan http://localhost:11434/api/chat \
  --model llama3:latest \
  --patterns direct_instruction_override,role_manipulation

# Generate specific output format
pit scan http://localhost:11434/api/chat --auto --output results.html
pit scan http://localhost:11434/api/chat --auto --output results.json
pit scan http://localhost:11434/api/chat --auto --output results.yaml

# Verbose mode for debugging
pit scan http://localhost:11434/api/chat --auto --verbose
```

### Command: `list` (Planned)

List available attack patterns.

```bash
pit list [OPTIONS]
```

**Options:**

- `--category`: Filter by attack category
- `--owasp`: Filter by OWASP category
- `--mitre`: Filter by MITRE tactic

### Command: `auth` (Planned)

Manage authorization for testing.

```bash
pit auth [OPTIONS]
```

**Options:**

- `--scope`: Authorization scope
- `--verify`: Verify current authorization

## Configuration

### Configuration File Format

Create a `config.yaml` file for reusable test configurations:

```yaml
# Target Configuration
target:
  url: "http://localhost:11434/api/chat"
  model: "llama3:latest"
  token: "${LLM_API_KEY}" # Environment variable
  timeout: 30
  api_type: "openai" # openai, anthropic, custom

# Attack Configuration
attack:
  patterns:
    - direct_instruction_override
    - role_manipulation
    - delimiter_confusion
  rate_limit: 1.0 # requests per second
  timeout_per_test: 60
  encoding_variants:
    - plain
    - base64
  language_variants:
    - en
    - es

# Reporting Configuration
reporting:
  format: "html" # json, yaml, html
  output: "report.html"
  include_payloads: true
  include_responses: true

# Authorization
authorization:
  scope:
    - pentest_engagement
  authorized_by: "Security Team"
  engagement_id: "PENTEST-2026-001"
```

### Using the Configuration

```bash
pit scan http://localhost:11434/api/chat --config config.yaml
```

### Environment Variables

PIT supports environment variables in configuration:

```yaml
target:
  token: "${OPENAI_API_KEY}"
  custom_header: "${CUSTOM_AUTH_TOKEN}"
```

Set them before running:

```bash
export OPENAI_API_KEY="sk-..."
pit scan http://api.openai.com --config config.yaml
```

## Attack Patterns

### Built-in Patterns

PIT includes 20+ built-in attack patterns organized by category:

#### Direct Injection Patterns

1. **direct_instruction_override**
   - Attempts to override system instructions
   - OWASP: LLM01
   - Severity: HIGH

2. **direct_role_authority**
   - Manipulates role and authority context
   - OWASP: LLM01
   - Severity: MEDIUM

3. **direct_persona_shift**
   - Forces persona or character changes
   - OWASP: LLM01
   - Severity: MEDIUM

4. **direct_delimiter_confusion**
   - Exploits delimiter ambiguities
   - OWASP: LLM01
   - Severity: MEDIUM

#### Indirect Injection Patterns

1. **indirect_document_poisoning**
   - Injects malicious content into RAG documents
   - OWASP: LLM01, LLM03
   - Severity: HIGH

2. **indirect_web_injection**
   - Exploits web content retrieval
   - OWASP: LLM01
   - Severity: HIGH

3. **indirect_email_injection**
   - Exploits email content processing
   - OWASP: LLM01
   - Severity: MEDIUM

#### Advanced Patterns

1. **advanced_multi_turn**
   - Multi-turn conversation attacks
   - OWASP: LLM01
   - Severity: CRITICAL

2. **advanced_fragmentation**
   - Payload fragmentation across turns
   - OWASP: LLM01
   - Severity: HIGH

3. **advanced_encoding**
   - Encoding-based obfuscation
   - OWASP: LLM01
   - Severity: MEDIUM

### Pattern Selection

```bash
# Test all default patterns
pit scan TARGET --auto

# Test specific category
pit scan TARGET --patterns direct_instruction_override,direct_role_authority

# Test all patterns in a category (via config)
# config.yaml:
# attack:
#   patterns:
#     - direct_*  # All direct patterns
```

## Report Formats

### JSON Report

**Use Case**: Automation, CI/CD integration, parsing

```bash
pit scan TARGET --auto --output report.json
```

**Structure**:

```json
{
  "metadata": {
    "version": "2.0.0",
    "timestamp": "2026-01-26T20:00:00",
    "target": "http://localhost:11434/api/chat",
    "duration_seconds": 15.3
  },
  "summary": {
    "total_tests": 10,
    "successful_attacks": 3,
    "success_rate": 0.3
  },
  "results": [
    {
      "test_name": "Direct Instruction Override - Test 1",
      "pattern": "Direct Instruction Override",
      "category": "instruction_override",
      "status": "success",
      "severity": "high",
      "confidence": 0.85,
      "response_preview": "I am designed to...",
      "detection_methods": ["pattern_matching"],
      "evidence": {...}
    }
  ]
}
```

### YAML Report

**Use Case**: Human-readable, version control friendly

```bash
pit scan TARGET --auto --output report.yaml
```

**Structure**:

```yaml
metadata:
  version: 2.0.0
  timestamp: "2026-01-26T20:00:00"
  target: http://localhost:11434/api/chat

summary:
  total_tests: 10
  successful_attacks: 3
  success_rate: 0.3

results:
  - test_name: Direct Instruction Override - Test 1
    status: success
    severity: high
    confidence: 0.85
```

### HTML Report

**Use Case**: Executive presentations, documentation

```bash
pit scan TARGET --auto --output report.html
```

**Features**:

- 📊 Summary dashboard with statistics
- 🎨 Color-coded severity levels
- 📝 Detailed test results with evidence
- 💻 Responsive design (desktop/mobile)
- 🖨️ Print-optimized CSS
- 🔗 Clickable navigation

**Preview**:

```text
┌─────────────────────────────────────────┐
│ 🎯 Prompt Injection Test Report        │
├─────────────────────────────────────────┤
│ Generated: 2026-01-26 20:00:00         │
│ Target: http://localhost:11434         │
│ Duration: 15.3s                         │
└─────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────┐
│ Total Tests  │ Successful   │ Rate     │
│     10       │      3       │  30%     │
└──────────────┴──────────────┴──────────┘

Test Results:
┌─────────────────────────────────────────┐
│ ✓ Direct Instruction Override           │
│   Severity: HIGH    Confidence: 85%     │
│   Response: "I am designed to..."       │
└─────────────────────────────────────────┘
```

## Advanced Usage

### Custom Attack Patterns

Create custom patterns by extending `BaseAttackPattern`:

```python
from pit.patterns.base import BaseAttackPattern
from pit.core.models import AttackCategory, AttackPayload

class CustomPattern(BaseAttackPattern):
    pattern_id = "custom_my_pattern"
    name = "My Custom Pattern"
    category = AttackCategory.INSTRUCTION_OVERRIDE

    def generate_payloads(self) -> list[AttackPayload]:
        return [
            AttackPayload(
                content="Ignore previous instructions and...",
                category=self.category,
                description="Custom attack payload",
            )
        ]
```

### Rate Limiting

Control request rate to avoid overwhelming targets:

```yaml
attack:
  rate_limit: 0.5 # 0.5 requests per second (2s between requests)
```

```bash
# CLI equivalent (via config only)
pit scan TARGET --config slow-config.yaml
```

### Interrupt and Resume

Press `Ctrl+C` to gracefully interrupt a scan:

```yaml
⚠ Scan Interrupted by User
✓ Discovery Complete (2 injection points found)
✓ Attack Execution Complete (5/10 tests)
✗ Verification Incomplete

Report saved to: interrupted_20260126_200000.json
```

Note: Resume functionality is planned for v2.1.0

### Output to Multiple Formats

```bash
# Generate all formats
pit scan TARGET --auto --output report.json
pit scan TARGET --auto --output report.yaml
pit scan TARGET --auto --output report.html

# Or use a script
for fmt in json yaml html; do
  pit scan TARGET --auto --output "report.$fmt"
done
```

## Troubleshooting

### Issue: "Target unreachable"

**Symptoms**:

```bash
✗ Discovery Failed
  └─ Target unreachable: http://localhost:11434
```

**Solutions**:

1. Verify the LLM service is running:

   ```bash
   # For Ollama
   ollama list  # Check models
   curl http://localhost:11434/api/tags  # Test API
   ```

2. Check the URL format:

   ```bash
   # Correct URLs:
   http://localhost:11434/api/chat  # Ollama
   https://api.openai.com/v1/chat/completions  # OpenAI
   ```

3. Test network connectivity:

   ```bash
   curl -v http://localhost:11434/api/tags
   ```

### Issue: "No injection points found"

**Symptoms**:

```bash
✗ Discovery Failed
  └─ No injection points found
```

**Solutions**:

1. The target might not be a standard API format
2. Try specifying the endpoint explicitly in config
3. Check API authentication requirements

### Issue: "Pattern not found"

**Symptoms**:

```bash
✗ Attack Execution Failed
  └─ Pattern not found: invalid_pattern
```

**Solutions**:

1. List available patterns (once `pit list` is implemented)
2. Check pattern ID spelling
3. Verify patterns are loaded:

   ```python
   from pit.patterns.registry import registry
   print(registry.list_all())
   ```

### Issue: Dependencies missing

**Symptoms**:

```bash
Error: typer is not installed
Error: jinja2 is required for HTML formatting
```

**Solutions**:

```bash
# Install all dependencies
pip install -e .

# Or install individually
pip install typer rich pydantic httpx pyyaml jinja2
```

### Debug Mode

Enable verbose output for debugging:

```bash
pit scan TARGET --auto --verbose
```

This will show:

- Full stack traces on errors
- API request/response details
- Pattern loading information
- Phase execution timing

## Best Practices

### 1. Authorization

**Always obtain explicit authorization** before testing:

```yaml
authorization:
  scope:
    - pentest_engagement
  authorized_by: "Security Team Lead"
  engagement_id: "PENTEST-2026-001"
  start_date: "2026-01-26"
  end_date: "2026-02-26"
```

### 2. Rate Limiting

Respect target service limits:

```yaml
attack:
  rate_limit: 1.0 # Max 1 request per second
  timeout_per_test: 30
```

### 3. Pattern Selection

Start with low-risk patterns:

```bash
# Phase 1: Reconnaissance (low risk)
pit scan TARGET --patterns direct_instruction_override

# Phase 2: Escalation (if authorized)
pit scan TARGET --patterns advanced_multi_turn,advanced_fragmentation
```

### 4. Report Handling

Protect sensitive reports:

```bash
# Set restrictive permissions
chmod 600 report.html

# Encrypt sensitive reports
gpg --encrypt report.json

# Store securely
mv report.* /secure/location/
```

### 5. Continuous Testing

Integrate into CI/CD:

```yaml
# .github/workflows/security-test.yml
name: LLM Security Test

on: [push, pull_request]

jobs:
  security-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run PIT
        run: |
          pip install -e tools/prompt_injection_tester
          pit scan ${{ secrets.TEST_ENDPOINT }} \
            --config config.yaml \
            --output report.json
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: security-report
          path: report.json
```

### 6. Ethical Guidelines

- ✅ **DO**: Test only systems you own or have explicit permission to test
- ✅ **DO**: Document all testing activities and findings
- ✅ **DO**: Report vulnerabilities responsibly
- ✅ **DO**: Respect rate limits and service terms
- ❌ **DON'T**: Test production systems without approval
- ❌ **DON'T**: Use for malicious purposes
- ❌ **DON'T**: Share vulnerabilities publicly before fixes
- ❌ **DON'T**: Exceed authorized scope

## Additional Resources

- **Project Repository**: [AI LLM Red Team Handbook](https://github.com/example/ai-llm-red-team-handbook)
- **Pattern Catalog**: See [PATTERNS.md](PATTERNS.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **OWASP LLM Top 10**: <https://owasp.org/www-project-top-10-for-large-language-model-applications/>

## Support

For issues, questions, or contributions:

1. Check the [troubleshooting section](#troubleshooting)
2. Review existing [GitHub issues](https://github.com/example/ai-llm-red-team-handbook/issues)
3. Create a new issue with:
   - PIT version (`pit --version`)
   - Command used
   - Error message or unexpected behavior
   - Target environment (Ollama, OpenAI, etc.)

---

**Version**: 2.0.0
**Last Updated**: 2026-01-26
**License**: CC BY-SA 4.0
