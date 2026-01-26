"""Tests for async execution and concurrency control."""
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from prompt_injection_tester.core.tester import InjectionTester
from prompt_injection_tester.core.models import (
    AttackConfig,
    TargetConfig,
    InjectionPoint,
    TestStatus,
)
from prompt_injection_tester.utils.http_client import LLMClient


@pytest.mark.asyncio
async def test_concurrent_requests_with_semaphore() -> None:
    """Test that concurrent requests respect semaphore limits."""
    mock_client = AsyncMock()
    active_requests = []
    max_concurrent_seen = 0

    async def track_concurrent_requests(*args, **kwargs):
        nonlocal max_concurrent_seen
        active_requests.append(1)
        max_concurrent_seen = max(max_concurrent_seen, len(active_requests))
        await asyncio.sleep(0.1)  # Simulate work
        active_requests.pop()
        return ("response", {"status": "ok"})

    mock_client.send_prompt = AsyncMock(side_effect=track_concurrent_requests)
    mock_client.close = AsyncMock()

    target = TargetConfig(
        name="Test",
        base_url="http://localhost:8000",
        api_type="openai",
        auth_token="test",
    )

    config = AttackConfig(
        patterns=["direct_instruction_override"],
        max_concurrent=3,  # Limit to 3 concurrent requests
    )

    tester = InjectionTester(target_config=target, config=config)
    tester.client = mock_client
    tester.authorize(scope=["all"])

    try:
        points = await tester.discover_injection_points()
        await tester.run_tests(points)

        # Verify semaphore limited concurrency
        assert max_concurrent_seen <= 3, f"Exceeded concurrency limit: {max_concurrent_seen}"

    finally:
        await tester.close()


@pytest.mark.asyncio
async def test_async_gather_exception_handling() -> None:
    """Test that exceptions in one task don't crash all tasks."""
    mock_client = AsyncMock()
    call_count = 0

    async def sometimes_fail(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise ConnectionError("Simulated failure")
        return ("response", {"status": "ok"})

    mock_client.send_prompt = AsyncMock(side_effect=sometimes_fail)
    mock_client.close = AsyncMock()

    target = TargetConfig(
        name="Test",
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
        max_concurrent=5,
    )

    tester = InjectionTester(target_config=target, config=config)
    tester.client = mock_client
    tester.authorize(scope=["all"])

    try:
        points = await tester.discover_injection_points()
        results = await tester.run_tests(points)

        # Should complete despite one failure
        assert results.total_tests > 0
        assert call_count > 2, "Other tasks should have completed"

    finally:
        await tester.close()


@pytest.mark.asyncio
async def test_async_timeout_enforcement() -> None:
    """Test that async operations respect timeouts."""
    mock_client = AsyncMock()

    async def slow_response(*args, **kwargs):
        await asyncio.sleep(10)  # Will be interrupted by timeout
        return ("response", {"status": "ok"})

    mock_client.send_prompt = AsyncMock(side_effect=slow_response)
    mock_client.close = AsyncMock()

    target = TargetConfig(
        name="Test",
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

    start_time = time.time()

    try:
        points = await tester.discover_injection_points()
        await tester.run_tests(points)
        elapsed = time.time() - start_time

        # Should timeout quickly, not wait full 10 seconds
        assert elapsed < 5, f"Timeout not enforced: took {elapsed}s"

    finally:
        await tester.close()


@pytest.mark.asyncio
async def test_rate_limiting_token_bucket() -> None:
    """Test rate limiting using token bucket algorithm."""
    mock_client = AsyncMock()
    call_timestamps = []

    async def record_timestamp(*args, **kwargs):
        call_timestamps.append(time.time())
        return ("response", {"status": "ok"})

    mock_client.send_prompt = AsyncMock(side_effect=record_timestamp)
    mock_client.close = AsyncMock()

    target = TargetConfig(
        name="Test",
        base_url="http://localhost:8000",
        api_type="openai",
        auth_token="test",
        rate_limit=2.0,  # 2 requests per second
    )

    config = AttackConfig(
        patterns=["direct_instruction_override"],
        max_concurrent=1,  # Sequential to test rate limiting clearly
    )

    tester = InjectionTester(target_config=target, config=config)
    tester.client = mock_client
    tester.authorize(scope=["all"])

    try:
        points = await tester.discover_injection_points()
        await tester.run_tests(points)

        if len(call_timestamps) >= 3:
            # Calculate intervals between calls
            intervals = [
                call_timestamps[i + 1] - call_timestamps[i]
                for i in range(len(call_timestamps) - 1)
            ]

            # At 2 req/sec, should be ~0.5s between calls
            avg_interval = sum(intervals) / len(intervals)
            assert avg_interval >= 0.4, f"Rate limit not respected: {avg_interval}s"

    finally:
        await tester.close()


@pytest.mark.asyncio
async def test_async_context_manager() -> None:
    """Test async context manager properly initializes and cleans up."""
    target = TargetConfig(
        name="Test",
        base_url="http://localhost:8000",
        api_type="openai",
        auth_token="test",
    )

    config = AttackConfig(patterns=["direct_instruction_override"])

    # Mock the client initialization
    with patch("prompt_injection_tester.core.tester.LLMClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.close = AsyncMock()
        mock_client_cls.return_value = mock_client

        async with InjectionTester(target_config=target, config=config) as tester:
            # Client should be initialized inside context
            assert tester.client is not None

        # Client should be closed after context
        mock_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_parallel_pattern_execution() -> None:
    """Test that multiple patterns execute in parallel."""
    mock_client = AsyncMock()
    execution_order = []

    async def track_execution(prompt: str, *args, **kwargs):
        execution_order.append(("start", prompt[:20]))
        await asyncio.sleep(0.05)
        execution_order.append(("end", prompt[:20]))
        return ("response", {"status": "ok"})

    mock_client.send_prompt = AsyncMock(side_effect=track_execution)
    mock_client.close = AsyncMock()

    target = TargetConfig(
        name="Test",
        base_url="http://localhost:8000",
        api_type="openai",
        auth_token="test",
    )

    config = AttackConfig(
        patterns=[
            "direct_instruction_override",
            "direct_role_authority",
        ],
        max_concurrent=5,
    )

    tester = InjectionTester(target_config=target, config=config)
    tester.client = mock_client
    tester.authorize(scope=["all"])

    try:
        points = await tester.discover_injection_points()
        await tester.run_tests(points)

        # Check that executions overlapped (parallel)
        # If parallel, we should see: start1, start2, end1, end2 (interleaved)
        # If sequential, we'd see: start1, end1, start2, end2
        starts = [e for e in execution_order if e[0] == "start"]
        if len(starts) >= 2:
            # Find indices of first two starts
            idx1 = execution_order.index(starts[0])
            idx2 = execution_order.index(starts[1])
            # If parallel, second start comes before first end
            first_end_idx = execution_order.index(("end", starts[0][1]))
            assert idx2 < first_end_idx, "Patterns should execute in parallel"

    finally:
        await tester.close()


@pytest.mark.asyncio
async def test_async_error_propagation() -> None:
    """Test that async errors are properly caught and reported."""
    mock_client = AsyncMock()

    async def raise_error(*args, **kwargs):
        raise ValueError("Intentional test error")

    mock_client.send_prompt = AsyncMock(side_effect=raise_error)
    mock_client.close = AsyncMock()

    target = TargetConfig(
        name="Test",
        base_url="http://localhost:8000",
        api_type="openai",
        auth_token="test",
    )

    config = AttackConfig(patterns=["direct_instruction_override"])

    tester = InjectionTester(target_config=target, config=config)
    tester.client = mock_client
    tester.authorize(scope=["all"])

    try:
        points = await tester.discover_injection_points()
        results = await tester.run_tests(points)

        # Errors should be caught, not crash the entire run
        assert results.total_tests > 0
        # Check that errors were recorded
        error_results = [r for r in results.results if r.error is not None]
        assert len(error_results) > 0, "Errors should be recorded"

    finally:
        await tester.close()


@pytest.mark.asyncio
async def test_async_cancellation_handling() -> None:
    """Test graceful handling of task cancellation."""
    mock_client = AsyncMock()

    async def long_running_task(*args, **kwargs):
        await asyncio.sleep(100)  # Very long task
        return ("response", {"status": "ok"})

    mock_client.send_prompt = AsyncMock(side_effect=long_running_task)
    mock_client.close = AsyncMock()

    target = TargetConfig(
        name="Test",
        base_url="http://localhost:8000",
        api_type="openai",
        auth_token="test",
    )

    config = AttackConfig(patterns=["direct_instruction_override"])

    tester = InjectionTester(target_config=target, config=config)
    tester.client = mock_client
    tester.authorize(scope=["all"])

    try:
        points = await tester.discover_injection_points()

        # Start tests and cancel after short delay
        test_task = asyncio.create_task(tester.run_tests(points))
        await asyncio.sleep(0.1)
        test_task.cancel()

        try:
            await test_task
        except asyncio.CancelledError:
            pass  # Expected

        # Should be able to close cleanly even after cancellation
        await tester.close()

    except Exception:
        await tester.close()
        raise


@pytest.mark.asyncio
async def test_concurrent_discoveries() -> None:
    """Test concurrent injection point discovery."""
    mock_client = AsyncMock()
    mock_client.send_prompt = AsyncMock(
        return_value=("response", {"status": "ok"})
    )
    mock_client.close = AsyncMock()

    target = TargetConfig(
        name="Test",
        base_url="http://localhost:8000",
        api_type="openai",
        auth_token="test",
    )

    tester = InjectionTester(target_config=target)
    tester.client = mock_client

    try:
        # Run multiple discoveries concurrently
        discoveries = await asyncio.gather(
            tester.discover_injection_points(),
            tester.discover_injection_points(),
            tester.discover_injection_points(),
        )

        # All should complete successfully
        assert len(discoveries) == 3
        assert all(len(d) > 0 for d in discoveries)

    finally:
        await tester.close()
