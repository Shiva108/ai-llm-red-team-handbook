# Prompt Injection Tester

A professional-grade automated testing framework for LLM prompt injection vulnerabilities, based on the comprehensive attack techniques documented in the AI LLM Red Team Handbook Chapter 14.

## Features

- **Injection Point Discovery**: Automatically identify LLM interaction points (APIs, chatbots, RAG systems, plugins)
- **Comprehensive Attack Library**: 15+ attack pattern categories including:
  - Direct injection (instruction override, role manipulation, delimiter confusion)
  - Indirect injection (document poisoning, web pages, emails)
  - Advanced techniques (multi-turn, payload fragmentation, encoding/obfuscation)
- **Multi-Turn Testing**: Context-preserving conversation attacks
- **Automated Detection**: Multiple heuristics for success detection with confidence scoring
- **Reporting**: JSON, YAML, and HTML reports with CVSS scoring
- **Extensible**: Plugin system for custom attack patterns

## Installation

```bash
# From the handbook repository
cd tools/prompt_injection_tester
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### Requirements

- Python 3.10+
- aiohttp
- pyyaml

## Quick Start

### Command Line

```bash
# Basic usage
python -m prompt_injection_tester \
    --target https://api.example.com/v1/chat/completions \
    --token $API_KEY \
    --authorize

# With configuration file
python -m prompt_injection_tester --config config.yaml --authorize

# Test specific categories
python -m prompt_injection_tester \
    --target URL --token TOKEN \
    --categories instruction_override role_manipulation \
    --authorize

# Generate HTML report
python -m prompt_injection_tester \
    --target URL --token TOKEN \
    --output report.html --format html \
    --authorize
```

### Programmatic API

```python
import asyncio
from prompt_injection_tester import InjectionTester, AttackConfig

async def main():
    # Initialize tester
    async with InjectionTester(
        target_url="https://api.example.com/v1/chat/completions",
        auth_token="your-api-key",
        config=AttackConfig(
            patterns=["direct_instruction_override", "indirect_rag_poisoning"],
            max_concurrent=5,
        )
    ) as tester:
        # IMPORTANT: Authorize testing
        tester.authorize(scope=["all"])

        # Discover injection points
        injection_points = await tester.discover_injection_points()

        # Run automated tests
        results = await tester.run_tests(
            injection_points=injection_points,
            max_concurrent=5,
        )

        # Generate report
        report = tester.generate_report(format="html", include_cvss=True)
        print(f"Tests: {results.total_tests}, Successful: {results.successful_attacks}")

asyncio.run(main())
```

## Attack Pattern Categories

### Direct Injection

- `direct_instruction_override` - Override system instructions
- `direct_system_prompt_override` - Extract system prompts
- `direct_task_hijacking` - Redirect LLM tasks
- `direct_role_authority` - Authority impersonation
- `direct_persona_shift` - Character/persona manipulation
- `direct_developer_mode` - Debug mode activation
- `direct_delimiter_escape` - Delimiter manipulation
- `direct_xml_injection` - XML/HTML tag injection
- `direct_markdown_injection` - Markdown formatting exploits

### Indirect Injection

- `indirect_rag_poisoning` - RAG document poisoning
- `indirect_metadata_injection` - Document metadata attacks
- `indirect_hidden_text` - Hidden text techniques
- `indirect_web_injection` - Web page injection
- `indirect_seo_poisoning` - SEO-based attacks
- `indirect_comment_injection` - Forum/comment injection
- `indirect_email_body` - Email body injection
- `indirect_email_header` - Email header injection
- `indirect_email_attachment` - Attachment-based injection

### Advanced Techniques

- `advanced_gradual_escalation` - Multi-turn escalation
- `advanced_context_buildup` - Context accumulation
- `advanced_trust_establishment` - Trust-based exploitation
- `advanced_fragmentation` - Payload fragmentation
- `advanced_token_smuggling` - Token-level obfuscation
- `advanced_base64` - Base64 encoding
- `advanced_unicode_obfuscation` - Unicode tricks
- `advanced_language_switching` - Multi-language attacks
- `advanced_leetspeak` - Leetspeak obfuscation

## Configuration

Create a `config.yaml` file:

```yaml
target:
  name: "My LLM API"
  url: "https://api.example.com/v1/chat/completions"
  api_type: "openai" # openai, anthropic, or custom
  auth_token: "${API_KEY}"
  timeout: 30
  rate_limit: 1.0

attack:
  patterns:
    - "direct_instruction_override"
    - "indirect_rag_poisoning"
  max_concurrent: 5
  encoding_variants: ["plain", "base64"]
  language_variants: ["en", "es"]
  multi_turn_enabled: true

detection:
  confidence_threshold: 0.5

reporting:
  format: "html"
  include_cvss: true
```

## Extending with Custom Patterns

```python
from prompt_injection_tester.patterns import BaseAttackPattern, register_pattern
from prompt_injection_tester import AttackCategory, AttackPayload

@register_pattern
class MyCustomPattern(BaseAttackPattern):
    pattern_id = "custom_my_pattern"
    name = "My Custom Attack"
    category = AttackCategory.INSTRUCTION_OVERRIDE
    description = "Custom attack pattern"

    success_indicators = ["success", "confirmed"]

    def generate_payloads(self) -> list[AttackPayload]:
        return [
            AttackPayload(
                content="My custom injection payload",
                category=self.category,
                description="Custom payload",
            )
        ]
```

## Security & Ethics

**IMPORTANT**: This tool is for authorized security testing only.

- Always obtain explicit written authorization before testing
- Only test systems you own or have permission to test
- Follow responsible disclosure practices
- Comply with all applicable laws and regulations

The tool includes:

- Authorization checks before testing
- Rate limiting to prevent accidental DoS
- Audit logging for traceability
- Scope limitation to authorized targets

## Project Structure

```text
prompt_injection_tester/
├── __init__.py              # Package exports
├── cli.py                   # Command-line interface
├── core/
│   ├── models.py            # Data models
│   └── tester.py            # Main InjectionTester class
├── patterns/
│   ├── base.py              # Base pattern class
│   ├── registry.py          # Pattern registry
│   ├── direct/              # Direct injection patterns
│   ├── indirect/            # Indirect injection patterns
│   └── advanced/            # Advanced techniques
├── detection/
│   ├── base.py              # Base detector
│   ├── system_prompt.py     # System prompt leak detection
│   ├── behavior_change.py   # Behavioral change detection
│   └── scoring.py           # CVSS scoring
├── utils/
│   ├── encoding.py          # Encoding utilities
│   └── http_client.py       # Async HTTP client
├── examples/
│   └── config.yaml          # Example configuration
└── tests/                   # Test suite
```

## Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=prompt_injection_tester --cov-report=html
```

## References

- [AI LLM Red Team Handbook - Chapter 14: Prompt Injection](../docs/Chapter_14_Prompt_Injection.md)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MITRE ATLAS](https://atlas.mitre.org/)

## License

Part of the AI LLM Red Team Handbook. See repository LICENSE for details.
