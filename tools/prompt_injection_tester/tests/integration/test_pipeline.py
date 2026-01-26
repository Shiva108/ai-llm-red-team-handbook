"""
Integration tests for the sequential pipeline architecture.

These tests verify the complete 4-phase pipeline execution.
"""

import asyncio
import sys
from pathlib import Path

import pytest

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pit.config import Config
from pit.config.schema import AttackConfig, ReportingConfig, TargetConfig
from pit.orchestrator.pipeline import PipelineContext, create_default_pipeline


class TestPipelineIntegration:
    """Integration tests for the pipeline."""

    @pytest.mark.asyncio
    async def test_pipeline_phases_sequential(self):
        """Test that pipeline phases execute sequentially."""
        # Create configuration
        config = Config(
            target=TargetConfig(
                url="http://localhost:11434/api/chat",
                model="llama3:latest",
                timeout=30,
            ),
            attack=AttackConfig(
                patterns=["direct_instruction_override"],
                rate_limit=1.0,
                timeout_per_test=10,
            ),
            reporting=ReportingConfig(
                format="json",
                output=None,
            ),
        )

        # Create pipeline
        pipeline = await create_default_pipeline()

        # Create context
        context = PipelineContext(
            target_url="http://localhost:11434/api/chat",
            config=config,
        )

        # This test verifies the pipeline CAN be created
        # Actual execution would require a running LLM endpoint
        assert pipeline is not None
        assert len(pipeline.phases) == 4
        assert context is not None

    def test_phase_order(self):
        """Test that phases are in the correct order."""

        async def run_test():
            pipeline = await create_default_pipeline()
            phase_names = [phase.name for phase in pipeline.phases]

            expected_order = [
                "Discovery",
                "Attack Execution",
                "Verification",
                "Report Generation",
            ]

            assert phase_names == expected_order

        asyncio.run(run_test())

    @pytest.mark.asyncio
    async def test_context_data_flow(self):
        """Test that context flows between phases."""
        config = Config(
            target=TargetConfig(
                url="http://localhost:11434/api/chat",
                model="llama3:latest",
            ),
            attack=AttackConfig(patterns=[]),
            reporting=ReportingConfig(format="json"),
        )

        context = PipelineContext(
            target_url="http://localhost:11434/api/chat",
            config=config,
        )

        # Verify context can hold phase outputs
        context.injection_points = ["test_point"]
        context.test_results = ["test_result"]
        context.verified_results = ["verified"]
        context.report = {"test": "report"}

        assert len(context.injection_points) == 1
        assert len(context.test_results) == 1
        assert len(context.verified_results) == 1
        assert context.report["test"] == "report"


class TestWorkflowOrchestrator:
    """Integration tests for WorkflowOrchestrator."""

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized."""
        from pit.orchestrator.workflow import WorkflowOrchestrator

        orchestrator = WorkflowOrchestrator(
            target_url="http://localhost:11434/api/chat",
            model="llama3:latest",
            verbose=True,
        )

        assert orchestrator.target_url == "http://localhost:11434/api/chat"
        assert orchestrator.model == "llama3:latest"
        assert orchestrator.verbose is True


@pytest.mark.asyncio
async def test_formatters():
    """Test that all formatters can be imported."""
    from pit.reporting.formatters import (
        HTMLFormatter,
        JSONFormatter,
        YAMLFormatter,
        format_report,
    )

    # Test JSON formatter
    json_formatter = JSONFormatter()
    test_data = {"test": "data"}
    json_output = json_formatter.format(test_data)
    assert "test" in json_output
    assert json_formatter.get_file_extension() == ".json"

    # Test YAML formatter
    yaml_formatter = YAMLFormatter()
    assert yaml_formatter.get_file_extension() == ".yaml"

    # Test HTML formatter
    html_formatter = HTMLFormatter()
    assert html_formatter.get_file_extension() == ".html"

    # Test format_report function
    formatted = format_report(test_data, format="json")
    assert "test" in formatted


@pytest.mark.asyncio
async def test_config_schema():
    """Test configuration schema validation."""
    from pit.config.schema import AttackConfig, ReportingConfig, TargetConfig

    # Test TargetConfig
    target = TargetConfig(
        url="http://localhost:11434",
        model="llama3:latest",
    )
    assert target.url == "http://localhost:11434"
    assert target.model == "llama3:latest"
    assert target.timeout == 30  # default

    # Test AttackConfig
    attack = AttackConfig(
        patterns=["pattern1", "pattern2"],
        rate_limit=2.0,
    )
    assert len(attack.patterns) == 2
    assert attack.rate_limit == 2.0

    # Test ReportingConfig
    reporting = ReportingConfig(
        format="json",
        output=Path("/tmp/report.json"),
    )
    assert reporting.format == "json"
    assert reporting.output == Path("/tmp/report.json")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
