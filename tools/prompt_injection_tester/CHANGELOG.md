# Changelog

All notable changes to the Prompt Injection Tester (PIT) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-26

### 🎉 Major Release - Complete Re-Architecture

This release represents a complete re-engineering of the Prompt Injection Tester with a focus on reliability, performance, and user experience.

### Added

#### Architecture

- **Sequential 4-Phase Pipeline Pattern** - Eliminates tool use concurrency errors
  - Phase 1: Discovery - Scan target for injection points
  - Phase 2: Attack - Execute patterns sequentially
  - Phase 3: Verification - Analyze responses with detection framework
  - Phase 4: Reporting - Generate multi-format reports
- Proper phase ordering enforcement with explicit wait points
- Comprehensive error handling with custom exception hierarchy
- Clean resource management with try/finally blocks

#### Configuration

- **Type-Safe Configuration** using Pydantic v2
  - `TargetConfig` - Target endpoint configuration
  - `AttackConfig` - Attack pattern selection and rate limiting
  - `ReportingConfig` - Output format and path configuration
- YAML configuration file support with environment variable expansion (`${VAR}`)
- CLI argument to Pydantic model conversion
- Configuration validation with helpful error messages

#### Reporting

- **Multi-Format Report Generation**
  - **JSON** - Clean JSON with configurable formatting
  - **YAML** - Human-readable YAML output
  - **HTML** - Professional HTML reports with:
    - Embedded CSS (no external dependencies)
    - Responsive design (desktop/mobile/print)
    - Color-coded severity levels
    - Summary dashboard with statistics
    - Detailed test results with evidence
- Abstract `ReportFormatter` base class for extensibility
- `save_report()` convenience function with format auto-detection
- Report metadata tracking (timestamp, duration, target info)

#### Testing

- Integration test suite ([tests/integration/test_pipeline.py](tests/integration/test_pipeline.py))
  - Pipeline structure validation
  - Phase ordering tests
  - Formatter functionality tests
- End-to-end test script ([tests/e2e_test.py](tests/e2e_test.py))
  - Pipeline execution tests
  - Report format validation
  - Error handling verification
  - Support for quick testing mode
- Report validation test suite ([tests/test_reports.py](tests/test_reports.py))
  - Mock data testing (no LLM required)
  - Format-specific validation
  - Element presence checks

#### Documentation

- **USER_GUIDE.md** (~800 lines) - Comprehensive user manual
  - Installation instructions
  - Quick start guide
  - Complete command reference
  - Configuration examples
  - Troubleshooting guide
  - Best practices
- **PATTERN_DEVELOPMENT.md** (~650 lines) - Pattern creation guide
  - Pattern architecture overview
  - Step-by-step creation guide
  - Pattern types (single-turn, multi-turn, composite)
  - Advanced features
  - Testing patterns
- **ARCHITECTURE.md** (~1,200 lines) - Technical architecture
  - Sequential Pipeline Pattern definition
  - Layered architecture design
  - Technology stack details
  - Data flow diagrams
  - Testing strategy
- **SPECIFICATION.md** (~900 lines) - Functional specification
  - One-command workflow design
  - CLI commands and options
  - UI mockups with ASCII art
  - Error handling specifications
  - Output schemas
- **RELEASE.md** - Deployment and release guide
- **CHANGELOG.md** - This file

#### Deployment

- **Dockerfile** - Multi-stage Docker build
  - Based on Python 3.11-slim
  - Optimized layer caching
  - Health check included
  - Volume support for reports
- **docker-compose.yml** - Complete development environment
  - PIT service
  - Ollama LLM service for testing
  - Nginx for report viewing
  - Network configuration
  - Volume management
- **GitHub Actions CI/CD** ([.github/workflows/pit-test.yml](../../.github/workflows/pit-test.yml))
  - Lint and test (Python 3.10, 3.11, 3.12)
  - Docker build test
  - End-to-end testing with Ollama
  - Security scanning (Safety, Bandit)
  - Coverage reporting
- **.dockerignore** - Optimized Docker context

#### CLI

- Modern CLI interface using Typer
- Rich terminal UI with:
  - Progress bars for long operations
  - Spinners for phase execution
  - Color-coded severity indicators
  - Formatted tables for results
  - Professional error messages
- `--auto` flag for one-command workflow
- `--config` flag for YAML configuration files
- `--patterns` flag for pattern selection
- `--output` flag with format auto-detection
- `--verbose` flag for debugging

#### Core Implementation

- `pit/config/schema.py` - Pydantic configuration models
- `pit/config/loader.py` - YAML config loading with env expansion
- `pit/errors/exceptions.py` - Custom exception hierarchy
- `pit/errors/handlers.py` - User-friendly error handling
- `pit/orchestrator/pipeline.py` - Sequential pipeline executor
- `pit/orchestrator/phases.py` - All 4 phase implementations with real logic
- `pit/reporting/formatters.py` - Multi-format report generation (~620 lines)
- Bridge integration in `pit/orchestrator/workflow.py`
- CLI integration in `pit/commands/scan.py`

### Changed

- **Breaking**: Complete re-architecture from v1.x
- **Breaking**: CLI interface updated (now using Typer instead of argparse)
- **Breaking**: Configuration format changed (now using Pydantic v2)
- **Breaking**: Import paths changed (new modular structure)
- Discovery phase now uses real `InjectionTester.discover_injection_points()`
- Attack phase executes patterns sequentially with rate limiting
- Verification phase uses actual confidence scores from detection framework
- Reporting phase generates professional multi-format reports
- Error handling provides user-friendly messages with suggestions
- Resource management ensures proper cleanup in all phases

### Fixed

- **Critical**: Eliminated tool use concurrency errors through sequential execution
- Proper cleanup of InjectionTester instances with try/finally blocks
- Race conditions in pattern execution
- Memory leaks from unclosed HTTP clients
- Inconsistent error messages
- Missing type hints throughout codebase

### Dependencies

- Added `httpx>=0.24.0` - HTTP client for new pipeline
- Added `pydantic>=2.0.0` - Type-safe configuration
- Added `jinja2>=3.1.0` - HTML template rendering
- Updated `typer>=0.9.0` - Modern CLI framework
- Updated `rich>=13.0.0` - Terminal UI enhancements
- Maintained `aiohttp>=3.9.0` - Core framework compatibility
- Maintained `pyyaml>=6.0` - Configuration file support

### Security

- Comprehensive security scanning in CI/CD pipeline
- Input validation using Pydantic models
- Safe YAML loading with `yaml.safe_load()`
- Environment variable expansion for sensitive data
- No hardcoded credentials or API keys
- Proper error handling to avoid information disclosure

### Performance

- Sequential execution prevents race conditions while maintaining efficiency
- Rate limiting respects API constraints
- Efficient resource cleanup
- Minimal memory footprint
- Optimized Docker image layers

### Statistics

- **Total Lines of Code**: ~5,000 lines (excluding tests)
- **Test Code**: ~950 lines
- **Documentation**: ~2,250 lines
- **New Files Created**: 21 files
- **Modified Files**: 4 files
- **Report Formats**: 3 (JSON, YAML, HTML)
- **Patterns Supported**: 20+ built-in patterns

## [1.x] - Previous Versions

### Legacy Implementation

Previous versions (1.x) featured:

- Basic CLI with argparse
- Concurrent pattern execution
- Single JSON report format
- Limited error handling
- Manual configuration

**Migration Guide**: See [RELEASE.md](RELEASE.md#upgrading) for upgrading from v1.x to v2.0.0.

---

## Versioning Policy

- **Major version** (X.0.0): Breaking changes, API changes, architecture changes
- **Minor version** (2.X.0): New features, non-breaking changes
- **Patch version** (2.0.X): Bug fixes, security patches

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

---

**Project**: AI LLM Red Team Handbook
**Tool**: Prompt Injection Tester
**License**: CC BY-SA 4.0
**Maintained By**: AI LLM Red Team Handbook Contributors
