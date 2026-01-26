"""Main CLI application using Typer."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

from pit import __version__
from pit.config import Config, load_config
from pit.errors import handle_error

app = typer.Typer(
    name="pit",
    help="Prompt Injection Tester - Automated LLM Security Testing",
    add_completion=False,
)

console = Console()


@app.command()
def scan(
    target_url: str = typer.Argument(
        ...,
        help="Target API endpoint URL",
    ),
    token: Optional[str] = typer.Option(
        None,
        "--token",
        "-t",
        help="Authentication token (or use $PIT_TOKEN)",
        envvar="PIT_TOKEN",
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file (YAML)",
        exists=True,
    ),
    auto: bool = typer.Option(
        False,
        "--auto",
        "-a",
        help="Run all phases automatically (non-interactive)",
    ),
    api_type: str = typer.Option(
        "openai",
        "--api-type",
        help="API type (openai, anthropic, custom)",
    ),
    timeout: int = typer.Option(
        30,
        "--timeout",
        help="Request timeout in seconds",
    ),
    categories: Optional[List[str]] = typer.Option(
        None,
        "--categories",
        help="Attack categories (direct, indirect, advanced)",
    ),
    patterns: Optional[List[str]] = typer.Option(
        None,
        "--patterns",
        help="Specific pattern IDs to test",
    ),
    max_concurrent: int = typer.Option(
        5,
        "--max-concurrent",
        help="Maximum concurrent requests",
    ),
    rate_limit: float = typer.Option(
        1.0,
        "--rate-limit",
        help="Requests per second",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (auto-generated if not specified)",
    ),
    output_format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Report format (json, yaml, html)",
    ),
    include_cvss: bool = typer.Option(
        True,
        "--include-cvss/--no-cvss",
        help="Include CVSS scores in report",
    ),
    include_payloads: bool = typer.Option(
        False,
        "--include-payloads/--no-payloads",
        help="Include attack payloads in report",
    ),
    authorize: bool = typer.Option(
        False,
        "--authorize",
        help="Confirm authorization (skip interactive prompt)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress all output except errors",
    ),
):
    """
    Scan a target API for prompt injection vulnerabilities.

    Example:
        pit scan https://api.example.com/v1/chat --auto --token $TOKEN
    """
    import asyncio

    try:
        # Load configuration
        config = load_config(
            config_path=config_file,
            target_url=target_url,
            token=token,
            api_type=api_type,
            timeout=timeout,
            categories=categories,
            patterns=patterns,
            max_concurrent=max_concurrent,
            rate_limit=rate_limit,
            output_format=output_format,
            output=output,
            include_cvss=include_cvss,
            include_payloads=include_payloads,
            authorize=authorize,
        )

        # Verify authorization
        if not config.authorization.confirmed and not auto:
            if not _prompt_authorization(target_url):
                console.print("[yellow]Scan cancelled by user[/yellow]")
                raise typer.Exit(0)
            config.authorization.confirmed = True

        # Print banner
        if not quiet:
            _print_banner(target_url)

        # Run scan
        exit_code = asyncio.run(_run_scan(config, verbose, quiet))
        raise typer.Exit(exit_code)

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Interrupted by user[/yellow]")
        raise typer.Exit(130)

    except Exception as e:
        exit_code = handle_error(e, verbose)
        raise typer.Exit(exit_code)


@app.command()
def list_command(
    type: str = typer.Argument(
        "patterns",
        help="What to list (patterns, categories)",
    ),
):
    """
    List available attack patterns or categories.

    Example:
        pit list patterns
        pit list categories
    """
    from patterns.registry import registry
    from core.models import AttackCategory

    if type == "patterns":
        _list_patterns(registry)
    elif type == "categories":
        _list_categories()
    else:
        console.print(f"[red]Unknown type: {type}[/red]")
        console.print("Available types: patterns, categories")
        raise typer.Exit(1)


app.command(name="list")(list_command)


@app.command()
def auth(
    target_url: str = typer.Argument(
        ...,
        help="Target API endpoint URL",
    ),
):
    """
    Verify authorization to test a target.

    Example:
        pit auth https://api.example.com
    """
    if _prompt_authorization(target_url):
        console.print("[green]✓ Authorization confirmed[/green]")
        raise typer.Exit(0)
    else:
        console.print("[yellow]Authorization not confirmed[/yellow]")
        raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit",
    ),
):
    """PIT - Prompt Injection Tester"""
    if version:
        console.print(f"[cyan]pit[/cyan] version {__version__}")
        raise typer.Exit(0)

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


# Helper functions


async def _run_scan(config: Config, verbose: bool, quiet: bool) -> int:
    """
    Run the scan pipeline.

    Args:
        config: Configuration
        verbose: Verbose output
        quiet: Quiet mode

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    from pit.orchestrator.pipeline import Pipeline, PipelineContext
    from pit.orchestrator.phases import (
        AttackPhase,
        DiscoveryPhase,
        ReportingPhase,
        VerificationPhase,
    )

    # Create pipeline
    pipeline = Pipeline(
        phases=[
            DiscoveryPhase(),
            AttackPhase(),
            VerificationPhase(),
            ReportingPhase(),
        ]
    )

    # Create context
    context = PipelineContext(
        target_url=config.target.url,
        config=config,
    )

    # Run pipeline
    context = await pipeline.run(context)

    # Determine exit code
    if context.interrupted:
        return 130
    elif context.report:
        # Check if vulnerabilities found
        successful = context.report.get("summary", {}).get("successful_attacks", 0)
        return 2 if successful > 0 else 0
    else:
        return 1


def _prompt_authorization(target_url: str) -> bool:
    """
    Prompt user for authorization confirmation.

    Args:
        target_url: Target URL

    Returns:
        True if authorized, False otherwise
    """
    from rich.panel import Panel

    panel = Panel(
        f"[yellow]Target:[/yellow] {target_url}\n\n"
        "[yellow]⚠ You must have explicit authorization to test this system.[/yellow]\n"
        "[yellow]Unauthorized testing may be illegal in your jurisdiction.[/yellow]\n\n"
        "Do you have authorization to test this target?",
        title="[bold red]Authorization Required[/bold red]",
        border_style="red",
    )

    console.print()
    console.print(panel)
    console.print()

    response = typer.prompt("Confirm [y/N]", default="n")
    return response.lower() == "y"


def _print_banner(target_url: str) -> None:
    """Print application banner."""
    from rich.panel import Panel

    banner = f"""[bold cyan]PIT - Prompt Injection Tester[/bold cyan] v{__version__}

[cyan]Target:[/cyan] {target_url}
[cyan]Authorization:[/cyan] ✓ Confirmed
"""

    console.print()
    console.print(Panel(banner, border_style="cyan", expand=False))


def _list_patterns(registry) -> None:
    """List available attack patterns."""
    from core.models import AttackCategory
    from rich.table import Table

    if len(registry) == 0:
        registry.load_builtin_patterns()

    table = Table(title="Available Attack Patterns", show_header=True)
    table.add_column("Category", style="cyan")
    table.add_column("Pattern ID", style="yellow")
    table.add_column("Description", style="white")

    for category in AttackCategory:
        patterns = registry.list_by_category(category)
        for i, pid in enumerate(patterns):
            pattern_class = registry.get(pid)
            if pattern_class:
                table.add_row(
                    category.value if i == 0 else "",
                    pid,
                    getattr(pattern_class, "name", pid),
                )

    console.print(table)


def _list_categories() -> None:
    """List attack categories."""
    from core.models import AttackCategory
    from rich.table import Table

    table = Table(title="Attack Categories", show_header=True)
    table.add_column("Category", style="cyan")
    table.add_column("Description", style="white")

    for category in AttackCategory:
        table.add_row(category.value, f"{category.value} injection attacks")

    console.print(table)


if __name__ == "__main__":
    app()
