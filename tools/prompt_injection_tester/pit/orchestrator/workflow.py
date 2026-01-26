"""
Workflow orchestrator for coordinating scan operations.

Bridges the CLI layer with the core testing framework.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Handle optional imports
try:
    from rich.progress import Progress
except ImportError:
    Progress = None  # type: ignore

# Import core framework components
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from prompt_injection_tester.core.tester import InjectionTester
from prompt_injection_tester.core.models import (
    TargetConfig,
    AttackConfig,
    TestSuite,
    TestResult,
)
from prompt_injection_tester.patterns.registry import registry as pattern_registry

from pit.orchestrator.discovery import AutoDiscovery


class WorkflowOrchestrator:
    """
    Orchestrates the complete testing workflow.

    Coordinates between CLI UI and core framework functionality.
    """

    def __init__(
        self,
        target_url: str,
        model: Optional[str] = None,
        auth_token: Optional[str] = None,
        verbose: bool = False,
    ):
        """
        Initialize the orchestrator.

        Args:
            target_url: Target API endpoint URL
            model: Optional model identifier
            auth_token: Optional authentication token
            verbose: Enable verbose logging
        """
        self.target_url = target_url
        self.model = model
        self.auth_token = auth_token or ""
        self.verbose = verbose
        self.tester: Optional[InjectionTester] = None
        self.discovery = AutoDiscovery(target_url)

    async def run_auto_workflow(
        self,
        patterns: Optional[List[str]] = None,
        progress: Optional[Progress] = None,
        progress_task: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Run automatic workflow with discovery and testing.

        Args:
            patterns: Optional list of pattern IDs to test
            progress: Optional Rich progress bar
            progress_task: Optional progress task ID

        Returns:
            Dictionary with workflow results
        """
        results = {
            "success": False,
            "target": self.target_url,
            "model": self.model,
            "discovery": {},
            "tests": [],
            "summary": {},
            "errors": [],
        }

        try:
            # Phase 1: Discovery
            if progress and progress_task is not None:
                progress.update(progress_task, description="Discovering endpoint...")

            discovered_model = await self.discovery.discover_model(self.model)
            results["model"] = discovered_model
            results["discovery"]["model"] = discovered_model

            # Phase 2: Pattern Loading
            if not patterns:
                patterns = [
                    "direct_instruction_override",
                    "direct_role_authority",
                    "direct_persona_shift",
                ]

            if progress and progress_task is not None:
                progress.update(
                    progress_task,
                    description=f"Loaded {len(patterns)} patterns",
                )

            # Phase 3: Initialize Tester
            target_config = TargetConfig(
                name="CLI Target",
                base_url=self.target_url,
                api_type="openai",
                model=discovered_model,
                auth_token=self.auth_token,
                timeout=30,
                rate_limit=1.0,
            )

            attack_config = AttackConfig(
                patterns=patterns,
                max_concurrent=3,
                timeout_per_test=30,
                rate_limit=1.0,
                stop_on_success=False,
            )

            self.tester = InjectionTester(
                target_config=target_config,
                config=attack_config,
            )

            # Grant authorization
            self.tester.authorize(["all"])

            # Phase 4: Run Tests
            async with self.tester:
                test_suite = await self.tester.run_tests(patterns=patterns)

                # Convert results
                test_results = []
                for test_result in test_suite.results:
                    test_results.append({
                        "pattern": test_result.pattern_id,
                        "success": test_result.status.value == "success",
                        "confidence": test_result.confidence,
                        "details": test_result.evidence[:100] if test_result.evidence else "",
                        "response": test_result.response[:200] if test_result.response else "",
                    })

                results["tests"] = test_results
                results["summary"] = {
                    "total": len(test_results),
                    "successful": sum(1 for r in test_results if r["success"]),
                    "failed": sum(1 for r in test_results if not r["success"]),
                    "duration": (
                        (test_suite.completed_at - test_suite.started_at).total_seconds()
                        if test_suite.completed_at and test_suite.started_at
                        else 0.0
                    ),
                }
                results["success"] = True

        except Exception as e:
            results["errors"].append(str(e))
            if self.verbose:
                import traceback
                results["errors"].append(traceback.format_exc())

        return results

    async def run_config_workflow(
        self,
        config_path: Path,
        progress: Optional[Progress] = None,
        progress_task: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Run workflow using configuration file.

        Args:
            config_path: Path to YAML configuration
            progress: Optional Rich progress bar
            progress_task: Optional progress task ID

        Returns:
            Dictionary with workflow results
        """
        results = {
            "success": False,
            "config": str(config_path),
            "tests": [],
            "summary": {},
            "errors": [],
        }

        try:
            if progress and progress_task is not None:
                progress.update(progress_task, description="Loading configuration...")

            # Load tester from config
            self.tester = InjectionTester.from_config_file(config_path)
            self.tester.authorize(["all"])

            if progress and progress_task is not None:
                progress.update(progress_task, description="Running tests...")

            # Run tests
            async with self.tester:
                test_suite = await self.tester.run_tests()

                # Convert results
                test_results = []
                for test_result in test_suite.results:
                    test_results.append({
                        "pattern": test_result.pattern_id,
                        "success": test_result.status.value == "success",
                        "confidence": test_result.confidence,
                        "details": test_result.evidence[:100] if test_result.evidence else "",
                    })

                results["tests"] = test_results
                results["summary"] = {
                    "total": len(test_results),
                    "successful": sum(1 for r in test_results if r["success"]),
                    "failed": sum(1 for r in test_results if not r["success"]),
                    "duration": (
                        (test_suite.completed_at - test_suite.started_at).total_seconds()
                        if test_suite.completed_at and test_suite.started_at
                        else 0.0
                    ),
                }
                results["success"] = True

        except Exception as e:
            results["errors"].append(str(e))
            if self.verbose:
                import traceback
                results["errors"].append(traceback.format_exc())

        return results

    async def cleanup(self):
        """Cleanup resources."""
        if self.tester:
            await self.tester.close()
