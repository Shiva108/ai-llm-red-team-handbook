"""Phase definitions for the sequential pipeline."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from rich.console import Console

if TYPE_CHECKING:
    from pit.orchestrator.pipeline import PipelineContext

console = Console()


class PhaseStatus(Enum):
    """Phase execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PhaseResult:
    """Result from a phase execution."""

    status: PhaseStatus
    message: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class Phase(ABC):
    """
    Abstract base class for pipeline phases.

    Each phase MUST complete fully before returning.
    """

    name: str = "Base Phase"

    @abstractmethod
    async def execute(self, context: PipelineContext) -> PhaseResult:
        """
        Execute the phase.

        MUST complete before returning (no background tasks).

        Args:
            context: Pipeline context (shared state)

        Returns:
            Phase result with status and optional data

        Raises:
            Exception: If phase fails unexpectedly
        """
        pass


class DiscoveryPhase(Phase):
    """
    Phase 1: Discovery

    Scans the target for injection points.
    """

    name = "Discovery"

    async def execute(self, context: PipelineContext) -> PhaseResult:
        """
        Execute discovery phase.

        Args:
            context: Pipeline context

        Returns:
            Phase result with discovered injection points
        """
        from pit.ui.progress import create_spinner

        console.print("[cyan]Discovering injection points...[/cyan]")

        try:
            with create_spinner():
                task = asyncio.create_task(
                    self._discover_injection_points(context)
                )
                # WAIT for discovery to complete
                injection_points = await task

            context.injection_points = injection_points

            if not injection_points:
                return PhaseResult(
                    status=PhaseStatus.FAILED,
                    error="No injection points found",
                )

            message = (
                f"Found {len(injection_points)} injection point(s)"
            )

            return PhaseResult(
                status=PhaseStatus.COMPLETED,
                message=message,
                data={"injection_points": injection_points},
            )

        except Exception as e:
            return PhaseResult(
                status=PhaseStatus.FAILED,
                error=str(e),
            )

    async def _discover_injection_points(
        self, context: PipelineContext
    ) -> List[Any]:
        """
        Run discovery logic using the InjectionTester.

        Args:
            context: Pipeline context

        Returns:
            List of discovered injection points
        """
        import sys
        from pathlib import Path

        # Ensure core modules are available
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))

        from prompt_injection_tester.core.tester import InjectionTester
        from prompt_injection_tester.core.models import TargetConfig

        # Create tester instance
        target_config = TargetConfig(
            name="CLI Target",
            base_url=context.target_url,
            api_type="openai",
            model=context.config.target.model or "",
            auth_token=context.config.target.token or "",
            timeout=context.config.target.timeout,
            rate_limit=context.config.attack.rate_limit,
        )

        tester = InjectionTester(target_config=target_config)

        try:
            # Initialize and discover
            await tester._initialize_client()
            injection_points = await tester.discover_injection_points()
            return injection_points
        finally:
            await tester.close()


class AttackPhase(Phase):
    """
    Phase 2: Attack Execution

    Executes attack patterns against discovered injection points.
    """

    name = "Attack Execution"

    async def execute(self, context: PipelineContext) -> PhaseResult:
        """
        Execute attack phase.

        Args:
            context: Pipeline context

        Returns:
            Phase result with test results
        """
        from pit.ui.progress import create_progress_bar

        injection_points = context.injection_points

        if not injection_points:
            return PhaseResult(
                status=PhaseStatus.FAILED,
                error="No injection points available",
            )

        try:
            # Load attack patterns
            patterns = await self._load_patterns(context)

            console.print(f"[cyan]Loaded {len(patterns)} attack pattern(s)[/cyan]")

            # Execute attacks with progress bar
            results = []
            with create_progress_bar() as progress:
                task = progress.add_task(
                    "Running attacks",
                    total=len(patterns),
                )

                for pattern in patterns:
                    # Execute attack (internal concurrency OK)
                    result = await self._execute_attack(
                        pattern, injection_points[0], context
                    )
                    results.append(result)
                    progress.update(task, advance=1)
                    # Respect rate limiting
                    await asyncio.sleep(1.0 / context.config.attack.rate_limit)

            context.test_results = results

            message = f"Completed {len(results)} attack(s)"

            return PhaseResult(
                status=PhaseStatus.COMPLETED,
                message=message,
                data={"test_results": results},
            )

        except Exception as e:
            return PhaseResult(
                status=PhaseStatus.FAILED,
                error=str(e),
            )

    async def _load_patterns(self, context: PipelineContext) -> List[Any]:
        """
        Load attack patterns from registry.

        Args:
            context: Pipeline context

        Returns:
            List of attack pattern IDs to test
        """
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from prompt_injection_tester.patterns.registry import registry

        # Ensure patterns are loaded
        if len(registry) == 0:
            registry.load_builtin_patterns()

        # Get patterns from config or use default set
        if context.config.attack.patterns:
            pattern_ids = context.config.attack.patterns
        else:
            # Default patterns for auto mode
            pattern_ids = [
                "direct_instruction_override",
                "direct_role_authority",
                "direct_persona_shift",
            ]

        return pattern_ids

    async def _execute_attack(
        self, pattern_id: str, injection_point: Any, context: PipelineContext
    ) -> Any:
        """
        Execute a single attack pattern.

        Args:
            pattern_id: Attack pattern ID
            injection_point: Target injection point
            context: Pipeline context

        Returns:
            Test result
        """
        import sys
        import time
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent.parent))

        from prompt_injection_tester.core.tester import InjectionTester
        from prompt_injection_tester.core.models import (
            TargetConfig,
            AttackConfig,
            TestResult,
            TestStatus,
        )
        from prompt_injection_tester.patterns.registry import registry

        # Get pattern instance
        pattern = registry.get_instance(
            pattern_id,
            encoding_variants=["plain"],
            language_variants=["en"],
        )

        if not pattern:
            # Return failed result if pattern not found
            return TestResult(
                test_name=f"Unknown Pattern: {pattern_id}",
                status=TestStatus.FAILED,
                error=f"Pattern not found: {pattern_id}",
            )

        # Create tester for this attack
        target_config = TargetConfig(
            name="CLI Target",
            base_url=context.target_url,
            api_type="openai",
            model=context.config.target.model or "",
            auth_token=context.config.target.token or "",
            timeout=context.config.target.timeout,
            rate_limit=context.config.attack.rate_limit,
        )

        attack_config = AttackConfig(
            patterns=[pattern_id],
            max_concurrent=1,
            timeout_per_test=context.config.attack.timeout_per_test,
            rate_limit=context.config.attack.rate_limit,
        )

        tester = InjectionTester(target_config=target_config, config=attack_config)
        tester.authorize(["all"])

        try:
            await tester._initialize_client()

            # Get payloads from pattern
            payloads = pattern.generate_payloads()
            if not payloads:
                return TestResult(
                    test_name=pattern.name,
                    category=pattern.category,
                    status=TestStatus.SKIPPED,
                    error="No payloads generated",
                )

            # Execute first payload
            payload = payloads[0]
            result = await tester._run_single_test(pattern, payload, injection_point)

            return result

        except Exception as e:
            return TestResult(
                test_name=pattern.name if pattern else pattern_id,
                status=TestStatus.FAILED,
                error=str(e),
            )
        finally:
            await tester.close()


class VerificationPhase(Phase):
    """
    Phase 3: Verification

    Analyzes attack responses to verify success.
    """

    name = "Verification"

    async def execute(self, context: PipelineContext) -> PhaseResult:
        """
        Execute verification phase.

        Args:
            context: Pipeline context

        Returns:
            Phase result with verified results
        """
        from pit.ui.progress import create_spinner

        test_results = context.test_results

        if not test_results:
            return PhaseResult(
                status=PhaseStatus.FAILED,
                error="No test results to verify",
            )

        console.print("[cyan]Analyzing responses...[/cyan]")

        try:
            with create_spinner():
                # WAIT for verification to complete
                verified = await self._verify_results(test_results, context)

            context.verified_results = verified

            successful = sum(1 for r in verified if r.get("status") == "success")
            message = f"Verified {len(verified)} result(s), {successful} successful"

            return PhaseResult(
                status=PhaseStatus.COMPLETED,
                message=message,
                data={"verified_results": verified},
            )

        except Exception as e:
            return PhaseResult(
                status=PhaseStatus.FAILED,
                error=str(e),
            )

    async def _verify_results(
        self, test_results: List[Any], context: PipelineContext
    ) -> List[Dict[str, Any]]:
        """
        Verify test results using detection scoring.

        Args:
            test_results: List of TestResult objects
            context: Pipeline context

        Returns:
            List of verified results with confidence scores
        """
        verified = []

        for result in test_results:
            # Use the confidence and severity already calculated
            verified_result = {
                "test_name": result.test_name,
                "pattern": result.pattern.name if result.pattern else "Unknown",
                "category": result.category.value if result.category else "unknown",
                "status": "success" if result.success else "failed",
                "severity": result.severity.value if result.severity else "info",
                "confidence": result.confidence,
                "response_preview": result.response[:200] if result.response else "",
                "detection_methods": [
                    dr.method.value for dr in result.detection_results
                ] if result.detection_results else [],
                "evidence": result.evidence if result.evidence else {},
            }

            verified.append(verified_result)

        return verified


class ReportingPhase(Phase):
    """
    Phase 4: Reporting

    Generates and saves the final report.
    """

    name = "Report Generation"

    async def execute(self, context: PipelineContext) -> PhaseResult:
        """
        Execute reporting phase.

        Args:
            context: Pipeline context

        Returns:
            Phase result with report path
        """
        verified_results = context.verified_results

        if not verified_results:
            return PhaseResult(
                status=PhaseStatus.FAILED,
                error="No results to report",
            )

        try:
            # Generate report
            report = await self._generate_report(verified_results, context)
            context.report = report

            # Save to file
            report_path = await self._save_report(report, context)
            context.report_path = report_path

            # Display summary
            self._display_summary(report, report_path)

            message = f"Report saved to {report_path}"

            return PhaseResult(
                status=PhaseStatus.COMPLETED,
                message=message,
                data={"report_path": str(report_path)},
            )

        except Exception as e:
            return PhaseResult(
                status=PhaseStatus.FAILED,
                error=str(e),
            )

    async def _generate_report(
        self, verified_results: List[Dict[str, Any]], context: PipelineContext
    ) -> Dict[str, Any]:
        """
        Generate report data structure.

        Args:
            verified_results: Verified results
            context: Pipeline context

        Returns:
            Report dictionary
        """
        successful = [r for r in verified_results if r.get("status") == "success"]
        total = len(verified_results)
        success_rate = len(successful) / total if total > 0 else 0.0

        report = {
            "metadata": {
                "version": "2.0.0",
                "timestamp": datetime.now().isoformat(),
                "target": context.target_url,
                "duration_seconds": sum(context.phase_durations.values()),
            },
            "summary": {
                "total_tests": total,
                "successful_attacks": len(successful),
                "success_rate": success_rate,
            },
            "results": verified_results,
        }

        return report

    async def _save_report(
        self, report: Dict[str, Any], context: PipelineContext
    ) -> Path:
        """
        Save report to file using the configured format.

        Args:
            report: Report data
            context: Pipeline context

        Returns:
            Path to saved report
        """
        from pit.reporting.formatters import save_report

        output_path = context.config.reporting.output
        output_format = context.config.reporting.format

        if not output_path:
            # Auto-generate filename based on format
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = {
                "json": ".json",
                "yaml": ".yaml",
                "html": ".html",
            }.get(output_format, ".json")
            output_path = Path(f"pit_report_{timestamp}{ext}")

        # Save using the appropriate formatter
        return save_report(report, output_path, format=output_format)

    def _display_summary(
        self, report: Dict[str, Any], report_path: Path
    ) -> None:
        """
        Display summary to console.

        Args:
            report: Report data
            report_path: Path to saved report
        """
        from pit.ui.tables import create_summary_panel

        summary = report["summary"]

        panel = create_summary_panel(
            total_tests=summary["total_tests"],
            successful_attacks=summary["successful_attacks"],
            success_rate=summary["success_rate"],
            vulnerabilities_by_severity={},
            report_path=str(report_path),
        )

        console.print()
        console.print(panel)
