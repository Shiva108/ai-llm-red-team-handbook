"""
Main CLI application using Typer.

This module defines the primary CLI interface for the Prompt Injection Tester.
"""

import sys
from typing import Optional

try:
    import typer
    from typing_extensions import Annotated
except ImportError:
    print("Error: typer is not installed. Please run: pip install typer")
    sys.exit(1)

try:
    from rich.console import Console
except ImportError:
    print("Error: rich is not installed. Please run: pip install rich")
    sys.exit(1)

from pit.commands import scan


# Initialize Typer app
app = typer.Typer(
    name="pit",
    help="🎯 Prompt Injection Tester - Enterprise LLM Security Assessment",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Initialize Rich console
console = Console()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit",
            is_flag=True,
        ),
    ] = None,
):
    """
    🎯 Prompt Injection Tester (PIT)

    A premium terminal experience for LLM security assessment.
    """
    if version:
        from pit import __version__
        console.print(f"[bold cyan]Prompt Injection Tester[/bold cyan] v{__version__}")
        raise typer.Exit()


# Register commands
app.add_typer(scan.app, name="scan", help="🔍 Run security assessment")


def cli_main():
    """Entry point for the CLI application."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Interrupted by user[/yellow]")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"[bold red]✗ Error:[/bold red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    cli_main()
