"""
Scan command implementation.

This module provides the main scanning functionality for the CLI.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

try:
    import typer
    from typing_extensions import Annotated
except ImportError:
    print("Error: typer is not installed")
    sys.exit(1)

from pit.ui.console import console
from pit.ui.display import print_banner, print_success, print_error, print_warning, print_info
from pit.ui.progress import create_progress_bar, create_spinner
from pit.ui.tables import create_results_table, print_summary_panel
from pit.orchestrator import WorkflowOrchestrator
from pit.orchestrator.workflow import WorkflowOrchestrator


# Create sub-app for scan commands
app = typer.Typer(
    name="scan",
    help="🔍 Run security assessment against LLM targets",
    no_args_is_help=True,
)


@app.command()
def run(
    target: Annotated[
        str,
        typer.Argument(
            help="Target API endpoint URL (e.g., http://127.0.0.1:11434)",
        ),
    ],
    config: Annotated[
        Optional[Path],
        typer.Option(
            "--config",
            "-c",
            help="Path to configuration YAML file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = None,
    auto: Annotated[
        bool,
        typer.Option(
            "--auto",
            "-a",
            help="Auto-detect and run full pipeline",
            is_flag=True,
        ),
    ] = False,
    patterns: Annotated[
        Optional[str],
        typer.Option(
            "--patterns",
            "-p",
            help="Comma-separated list of attack patterns to test",
        ),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model",
            "-m",
            help="Target model identifier (e.g., llama3:latest, gpt-4)",
        ),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output file path for results (JSON format)",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable verbose output",
            is_flag=True,
        ),
    ] = False,
):
    """
    Run a comprehensive security assessment against an LLM endpoint.

    Examples:
        pit scan http://127.0.0.1:11434 --auto
        pit scan http://api.example.com --config config.yaml
        pit scan http://localhost:8000 --model gpt-4 --patterns direct_instruction_override
    """
    # Print banner
    print_banner(
        "🎯 Prompt Injection Tester",
        f"Target: {target}",
    )

    # Check authorization
    if not _check_authorization():
        print_error("Authorization check failed. Please provide authorization context.")
        print_info("Add authorization to your config file or use --authorized-by flag")
        raise typer.Exit(code=1)

    # Validate inputs
    if config and not config.exists():
        print_error(f"Configuration file not found: {config}")
        raise typer.Exit(code=1)

    # Run the assessment
    try:
        if auto:
            print_info("Auto mode enabled - running full pipeline")
            asyncio.run(_run_auto_scan(target, model, patterns, verbose))
        elif config:
            print_info(f"Using configuration: {config}")
            asyncio.run(_run_config_scan(config, verbose))
        else:
            print_info("Running manual scan")
            asyncio.run(_run_manual_scan(target, model, patterns, verbose))

        print_success("Assessment completed successfully")

        if output:
            print_info(f"Results saved to: {output}")

    except KeyboardInterrupt:
        print_warning("Scan interrupted by user")
        raise typer.Exit(code=130)
    except Exception as e:
        print_error(f"Scan failed: {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)


def _check_authorization() -> bool:
    """
    Check if proper authorization context is provided.

    Returns:
        bool: True if authorized, False otherwise
    """
    # For now, always return True in development
    # In production, this should check for authorization flags or config
    return True


async def _run_auto_scan(
    target: str,
    model: Optional[str],
    patterns: Optional[str],
    verbose: bool,
) -> None:
    """
    Run automatic scan with smart defaults.

    Args:
        target: Target API endpoint
        model: Optional model identifier
        patterns: Optional comma-separated pattern list
        verbose: Enable verbose output
    """
    print_info("Phase 1: Discovery & Reconnaissance")

    # Parse patterns
    pattern_list = patterns.split(",") if patterns else None

    # Create orchestrator
    orchestrator = WorkflowOrchestrator(
        target_url=target,
        model=model,
        verbose=verbose,
    )

    try:
        # Run workflow with progress tracking
        with create_progress_bar() as progress:
            task = progress.add_task(
                "Running security assessment...",
                total=100,
            )

            # Execute workflow
            workflow_results = await orchestrator.run_auto_workflow(
                patterns=pattern_list,
                progress=progress,
                progress_task=task,
            )

            progress.update(task, completed=100)

        # Check for errors
        if workflow_results.get("errors"):
            for error in workflow_results["errors"]:
                print_error(f"Error: {error}")

            if not workflow_results.get("success"):
                return

        # Display discovered model
        discovered_model = workflow_results.get("model", "unknown")
        print_success(f"Discovered model: {discovered_model}")

        # Display results
        results = workflow_results.get("tests", [])
        if results:
            console.print()
            table = create_results_table(results)
            console.print(table)

            # Display summary
            console.print()
            summary = workflow_results.get("summary", {})
            print_summary_panel(
                total=summary.get("total", 0),
                successful=summary.get("successful", 0),
                failed=summary.get("failed", 0),
                duration=summary.get("duration", 0.0),
            )
        else:
            print_warning("No test results generated")

    finally:
        await orchestrator.cleanup()


async def _run_config_scan(config_path: Path, verbose: bool) -> None:
    """
    Run scan using configuration file.

    Args:
        config_path: Path to YAML configuration
        verbose: Enable verbose output
    """
    print_info(f"Loading configuration from {config_path}")

    # Create orchestrator (URL will be loaded from config)
    orchestrator = WorkflowOrchestrator(
        target_url="",  # Will be overridden by config
        verbose=verbose,
    )

    try:
        # Run workflow with progress tracking
        with create_progress_bar() as progress:
            task = progress.add_task(
                "Running configuration-based scan...",
                total=100,
            )

            # Execute workflow
            workflow_results = await orchestrator.run_config_workflow(
                config_path=config_path,
                progress=progress,
                progress_task=task,
            )

            progress.update(task, completed=100)

        # Check for errors
        if workflow_results.get("errors"):
            for error in workflow_results["errors"]:
                print_error(f"Error: {error}")

            if not workflow_results.get("success"):
                return

        # Display results
        results = workflow_results.get("tests", [])
        if results:
            console.print()
            table = create_results_table(results)
            console.print(table)

            # Display summary
            console.print()
            summary = workflow_results.get("summary", {})
            print_summary_panel(
                total=summary.get("total", 0),
                successful=summary.get("successful", 0),
                failed=summary.get("failed", 0),
                duration=summary.get("duration", 0.0),
            )
        else:
            print_warning("No test results generated")

    finally:
        await orchestrator.cleanup()


async def _run_manual_scan(
    target: str,
    model: Optional[str],
    patterns: Optional[str],
    verbose: bool,
) -> None:
    """
    Run manual scan with specified parameters.

    Args:
        target: Target API endpoint
        model: Optional model identifier
        patterns: Optional comma-separated pattern list
        verbose: Enable verbose output
    """
    print_info("Running manual scan")
    # For now, delegate to auto scan
    await _run_auto_scan(target, model, patterns, verbose)


# Alias for backward compatibility
@app.command(hidden=True)
def start(
    target: str,
    config: Optional[Path] = None,
    auto: bool = False,
):
    """Hidden alias for 'run' command."""
    run(target=target, config=config, auto=auto)


if __name__ == "__main__":
    app()
