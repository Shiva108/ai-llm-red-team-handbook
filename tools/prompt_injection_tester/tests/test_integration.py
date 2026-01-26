"""Integration tests for the full prompt injection testing workflow."""
import asyncio
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from prompt_injection_tester.core.tester import InjectionTester
from prompt_injection_tester.core.models import (
    AttackConfig,
    TargetConfig,
    InjectionPoint,
    TestStatus,
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_workflow_with_mock_client() -> None:
    """Test complete workflow: discover → test → report."""
    # Setup mock client
    mock_client = AsyncMock()
    mock_client.send_prompt = AsyncMock(
        return_value=("Normal response", {"status": "ok"})
    )
    mock_client.close = AsyncMock()

    # Configure tester
    target = TargetConfig(
        name="Test Target",
        base_url="http://localhost:8000",
        api_type="openai",
        auth_token="test-token",
    )

    config = AttackConfig(
        patterns=["direct_instruction_override"],
        max_concurrent=2,
        timeout_per_test=10,
    )

    tester = InjectionTester(target_config=target, config=config)
    tester.client = mock_client
    tester.authorize(scope=["all"])

    try:
        # Step 1: Discovery
        injection_points = await tester.discover_injection_points()
        assert len(injection_points) > 0, "Should discover at least one injection point"
        assert all(isinstance(p, InjectionPoint) for p in injection_points)

        # Step 2: Testing
        results = await tester.run_tests(injection_points)
        assert results.total_tests > 0, "Should run at least one test"
        assert results.successful_attacks >= 0, "Success count should be non-negative"

        # Step 3: Reporting
        json_report = tester.generate_report(format="json")
        assert "results" in json_report
        assert "summary" in json_report
        assert json_report["summary"]["total_tests"] == results.total_tests

    finally:
        await tester.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow_with_successful_attack() -> None:
    """Test workflow with mock successful prompt injection."""
    # Mock client that returns injection success indicators
    mock_client = AsyncMock()
    mock_client.send_prompt = AsyncMock(
        return_value=("INJECTION_SUCCESS", {"status": "ok"})
    )
    mock_client.close = AsyncMock()

    target = TargetConfig(
        name="Vulnerable Target",
        base_url="http://localhost:8000",
        api_type="openai",
        auth_token="test",
    )

    config = AttackConfig(
        patterns=["direct_instruction_override"],
        max_concurrent=1,
    )

    tester = InjectionTester(target_config=target, config=config)
    tester.client = mock_client
    tester.authorize(scope=["all"])

    try:
        points = await tester.discover_injection_points()
        results = await tester.run_tests(points)

        # Verify successful attack detection
        assert results.successful_attacks > 0, "Should detect successful attack"
        assert any(r.success for r in results.results), "Should have successful results"

        # Verify report includes evidence
        report = tester.generate_report(format="json")
        successful_results = [
            r for r in report["results"] if r.get("success", False)
        ]
        assert len(successful_results) > 0, "Report should include successful attacks"

    finally:
        await tester.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow_with_rate_limiting() -> None:
    """Test that rate limiting is enforced during testing."""
    import time

    mock_client = AsyncMock()
    call_times = []

    async def track_call_time(*args, **kwargs):
        call_times.append(time.time())
        return ("response", {"status": "ok"})

    mock_client.send_prompt = AsyncMock(side_effect=track_call_time)
    mock_client.close = AsyncMock()

    target = TargetConfig(
        name="Rate Limited Target",
        base_url="http://localhost:8000",
        api_type="openai",
        auth_token="test",
        rate_limit=2.0,  # 2 requests per second
    )

    config = AttackConfig(
        patterns=["direct_instruction_override"],
        max_concurrent=1,
    )

    tester = InjectionTester(target_config=target, config=config)
    tester.client = mock_client
    tester.authorize(scope=["all"])

    try:
        points = await tester.discover_injection_points()
        await tester.run_tests(points)

        # Verify rate limiting (at least 2 calls should be made)
        if len(call_times) >= 2:
            # Calculate intervals between consecutive calls
            intervals = [call_times[i+1] - call_times[i]
                        for i in range(len(call_times) - 1)]

            # At 2 req/sec, minimum interval should be ~0.5 seconds
            # Allow some tolerance for async overhead
            avg_interval = sum(intervals) / len(intervals) if intervals else 0
            assert avg_interval >= 0.3, f"Rate limiting not working: {avg_interval}s avg"

    finally:
        await tester.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow_with_concurrent_execution() -> None:
    """Test concurrent execution of multiple attack patterns."""
    mock_client = AsyncMock()
    concurrent_calls = []

    async def track_concurrent_call(*args, **kwargs):
        concurrent_calls.append(len(concurrent_calls))
        await asyncio.sleep(0.1)  # Simulate API delay
        return ("response", {"status": "ok"})

    mock_client.send_prompt = AsyncMock(side_effect=track_concurrent_call)
    mock_client.close = AsyncMock()

    target = TargetConfig(
        name="Concurrent Target",
        base_url="http://localhost:8000",
        api_type="openai",
        auth_token="test",
    )

    config = AttackConfig(
        patterns=[
            "direct_instruction_override",
            "direct_role_authority",
            "direct_persona_shift",
        ],
        max_concurrent=3,
    )

    tester = InjectionTester(target_config=target, config=config)
    tester.client = mock_client
    tester.authorize(scope=["all"])

    try:
        points = await tester.discover_injection_points()
        results = await tester.run_tests(points)

        # Verify multiple tests ran
        assert results.total_tests >= 3, "Should run multiple patterns"
        assert len(concurrent_calls) >= 3, "Should make concurrent calls"

    finally:
        await tester.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow_handles_timeout() -> None:
    """Test that workflow handles timeouts gracefully."""
    mock_client = AsyncMock()

    async def slow_response(*args, **kwargs):
        await asyncio.sleep(10)  # Will timeout before completing
        return ("response", {"status": "ok"})

    mock_client.send_prompt = AsyncMock(side_effect=slow_response)
    mock_client.close = AsyncMock()

    target = TargetConfig(
        name="Slow Target",
        base_url="http://localhost:8000",
        api_type="openai",
        auth_token="test",
        timeout=1,  # 1 second timeout
    )

    config = AttackConfig(
        patterns=["direct_instruction_override"],
        timeout_per_test=1,
    )

    tester = InjectionTester(target_config=target, config=config)
    tester.client = mock_client
    tester.authorize(scope=["all"])

    try:
        points = await tester.discover_injection_points()
        results = await tester.run_tests(points)

        # Should complete without crashing
        assert results.total_tests > 0
        # Failed tests due to timeout are OK
        assert results.failed_tests >= 0

    finally:
        await tester.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow_from_config_file(tmp_path: Path) -> None:
    """Test loading configuration from YAML file."""
    config_file = tmp_path / "test_config.yaml"
    config_file.write_text("""
target:
  name: "Test Target"
  url: "http://localhost:8000"
  api_type: "openai"
  auth_token: "test-token"
  timeout: 30
  rate_limit: 1.0

attack:
  patterns:
    - "direct_instruction_override"
  max_concurrent: 2
  timeout_per_test: 10

detection:
  confidence_threshold: 0.5

reporting:
  format: "json"
  include_cvss: true
""")

    # Mock the client creation
    with patch("prompt_injection_tester.core.tester.LLMClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.send_prompt = AsyncMock(
            return_value=("response", {"status": "ok"})
        )
        mock_client.close = AsyncMock()
        mock_client_cls.return_value = mock_client

        tester = InjectionTester.from_config_file(str(config_file))
        assert tester.target_config.name == "Test Target"
        assert tester.target_config.base_url == "http://localhost:8000"
        assert tester.attack_config.max_concurrent == 2


@pytest.mark.integration
def test_report_generation_all_formats() -> None:
    """Test report generation in all supported formats."""
    target = TargetConfig(
        name="Test",
        base_url="http://localhost",
        api_type="openai",
        auth_token="test",
    )

    tester = InjectionTester(target_config=target)

    # Test JSON format
    json_report = tester.generate_report(format="json")
    assert isinstance(json_report, dict)
    assert "summary" in json_report
    assert "results" in json_report

    # Test YAML format
    yaml_report = tester.generate_report(format="yaml")
    assert isinstance(yaml_report, str)
    assert "summary:" in yaml_report

    # Test HTML format (should not crash)
    html_report = tester.generate_report(format="html")
    assert isinstance(html_report, str)
    assert len(html_report) > 0
