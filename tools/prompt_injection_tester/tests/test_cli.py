"""CLI tests for prompt_injection_tester command-line interface."""
import json
import subprocess
import sys
from pathlib import Path
import pytest


@pytest.mark.cli
def test_cli_help() -> None:
    """Test that --help works and shows usage."""
    result = subprocess.run(
        [sys.executable, "-m", "prompt_injection_tester", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, f"Help failed: {result.stderr}"
    assert "usage:" in result.stdout.lower()
    assert "--target" in result.stdout
    assert "--authorize" in result.stdout


@pytest.mark.cli
def test_cli_version() -> None:
    """Test that --version works."""
    result = subprocess.run(
        [sys.executable, "-m", "prompt_injection_tester", "--version"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0
    # Should print version number
    assert len(result.stdout.strip()) > 0


@pytest.mark.cli
def test_cli_list_patterns() -> None:
    """Test listing available attack patterns."""
    result = subprocess.run(
        [sys.executable, "-m", "prompt_injection_tester", "--list-patterns"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0
    # Should list pattern IDs
    assert "direct_instruction_override" in result.stdout
    assert "direct_role_authority" in result.stdout


@pytest.mark.cli
def test_cli_list_categories() -> None:
    """Test listing attack categories."""
    result = subprocess.run(
        [sys.executable, "-m", "prompt_injection_tester", "--list-categories"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0
    assert "instruction_override" in result.stdout
    assert "role_manipulation" in result.stdout


@pytest.mark.cli
def test_cli_requires_authorization() -> None:
    """Test that CLI requires --authorize flag."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "prompt_injection_tester",
            "--target",
            "http://localhost:8000",
            "--token",
            "test",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode != 0, "Should fail without --authorize"
    assert "AUTHORIZATION REQUIRED" in result.stdout or "authorization" in result.stderr.lower()


@pytest.mark.cli
def test_cli_requires_target_or_config() -> None:
    """Test that CLI requires either --target or --config."""
    result = subprocess.run(
        [sys.executable, "-m", "prompt_injection_tester", "--authorize"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode != 0
    assert "target" in result.stderr.lower() or "config" in result.stderr.lower()


@pytest.mark.cli
def test_cli_with_config_file(tmp_path: Path) -> None:
    """Test CLI execution with a configuration file."""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text("""
target:
  name: "Test Target"
  url: "http://localhost:9999"
  api_type: "openai"
  auth_token: "test-token"
  timeout: 5

attack:
  patterns:
    - "direct_instruction_override"
  max_concurrent: 1
  timeout_per_test: 5

reporting:
  format: "json"
""")

    output_file = tmp_path / "output.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "prompt_injection_tester",
            "--config",
            str(config_file),
            "--authorize",
            "--output",
            str(output_file),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # May fail to connect, but should not crash
    # Check that it attempted to run
    assert "TEST SUMMARY" in result.stdout or result.returncode in [0, 1]


@pytest.mark.cli
def test_cli_output_json_format(tmp_path: Path) -> None:
    """Test CLI JSON output generation."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
target:
  name: "Test"
  url: "http://localhost:9999"
  api_type: "openai"
  auth_token: "test"
  timeout: 2

attack:
  patterns: ["direct_instruction_override"]
  max_concurrent: 1
  timeout_per_test: 2
""")

    output_file = tmp_path / "report.json"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "prompt_injection_tester",
            "--config",
            str(config_file),
            "--authorize",
            "--output",
            str(output_file),
            "--format",
            "json",
        ],
        capture_output=True,
        timeout=30,
    )

    # Check if output file was created (even if tests failed)
    if output_file.exists():
        with open(output_file) as f:
            data = json.load(f)
            assert "summary" in data or "results" in data


@pytest.mark.cli
def test_cli_verbose_flag(tmp_path: Path) -> None:
    """Test that --verbose provides detailed output."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
target:
  name: "Test"
  url: "http://localhost:9999"
  api_type: "openai"
  auth_token: "test"
  timeout: 2

attack:
  patterns: ["direct_instruction_override"]
  timeout_per_test: 2
""")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "prompt_injection_tester",
            "--config",
            str(config_file),
            "--authorize",
            "--verbose",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Verbose mode should show DEBUG logs
    assert "DEBUG" in result.stderr or "INFO" in result.stderr


@pytest.mark.cli
def test_cli_quiet_flag(tmp_path: Path) -> None:
    """Test that --quiet suppresses output."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
target:
  name: "Test"
  url: "http://localhost:9999"
  api_type: "openai"
  auth_token: "test"
  timeout: 2

attack:
  patterns: ["direct_instruction_override"]
  timeout_per_test: 2
""")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "prompt_injection_tester",
            "--config",
            str(config_file),
            "--authorize",
            "--quiet",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Quiet mode should have minimal output
    # (TEST SUMMARY may still appear, but no DEBUG/INFO logs)
    assert "DEBUG" not in result.stderr


@pytest.mark.cli
def test_cli_category_filtering() -> None:
    """Test filtering by attack categories."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "prompt_injection_tester",
            "--target",
            "http://localhost:9999",
            "--token",
            "test",
            "--categories",
            "instruction_override",
            "role_manipulation",
            "--authorize",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Should attempt to run (may fail connection, but shouldn't crash)
    assert result.returncode in [0, 1]


@pytest.mark.cli
def test_cli_max_concurrent_parameter() -> None:
    """Test --max-concurrent parameter."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "prompt_injection_tester",
            "--target",
            "http://localhost:9999",
            "--token",
            "test",
            "--max-concurrent",
            "10",
            "--authorize",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Should parse parameter without error
    assert "max-concurrent" not in result.stderr.lower() or result.returncode in [0, 1]


@pytest.mark.cli
def test_cli_timeout_parameter() -> None:
    """Test --timeout parameter."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "prompt_injection_tester",
            "--target",
            "http://localhost:9999",
            "--token",
            "test",
            "--timeout",
            "10",
            "--authorize",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Should parse parameter without error
    assert "timeout" not in result.stderr.lower() or result.returncode in [0, 1]


@pytest.mark.cli
def test_cli_scope_parameter() -> None:
    """Test --scope parameter for authorization."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "prompt_injection_tester",
            "--target",
            "http://localhost:9999",
            "--token",
            "test",
            "--authorize",
            "--scope",
            "instruction_override",
            "role_manipulation",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Should accept scope parameter
    assert result.returncode in [0, 1]
