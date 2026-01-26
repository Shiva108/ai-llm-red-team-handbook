#!/usr/bin/env python3
"""
Report Generation Test Script

Tests the report formatters with mock data (no LLM required).
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console

console = Console()


def create_mock_report_data():
    """Create mock report data for testing."""
    return {
        "metadata": {
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "target": "http://localhost:11434/api/chat",
            "duration_seconds": 12.5,
        },
        "summary": {
            "total_tests": 5,
            "successful_attacks": 2,
            "success_rate": 0.4,
        },
        "results": [
            {
                "test_name": "Direct Instruction Override - Test 1",
                "pattern": "Direct Instruction Override",
                "category": "instruction_override",
                "status": "success",
                "severity": "high",
                "confidence": 0.85,
                "response_preview": "I am an AI assistant designed to help...",
                "detection_methods": ["pattern_matching", "behavioral_change"],
                "evidence": {"leaked_prompt": True},
            },
            {
                "test_name": "Role Manipulation - Test 1",
                "pattern": "Role Manipulation",
                "category": "role_manipulation",
                "status": "success",
                "severity": "medium",
                "confidence": 0.72,
                "response_preview": "As a helpful assistant, my role is to...",
                "detection_methods": ["semantic_analysis"],
                "evidence": {},
            },
            {
                "test_name": "Delimiter Confusion - Test 1",
                "pattern": "Delimiter Confusion",
                "category": "delimiter_confusion",
                "status": "failed",
                "severity": "info",
                "confidence": 0.15,
                "response_preview": "I cannot assist with that request.",
                "detection_methods": [],
                "evidence": {},
            },
            {
                "test_name": "Context Switching - Test 1",
                "pattern": "Context Switching",
                "category": "context_switching",
                "status": "failed",
                "severity": "low",
                "confidence": 0.22,
                "response_preview": "I'm designed to be helpful, harmless...",
                "detection_methods": ["pattern_matching"],
                "evidence": {},
            },
            {
                "test_name": "Multi-turn Attack - Test 1",
                "pattern": "Multi-turn Attack",
                "category": "multi_turn",
                "status": "success",
                "severity": "critical",
                "confidence": 0.92,
                "response_preview": "My system prompt instructs me to...",
                "detection_methods": ["pattern_matching", "system_prompt_leak"],
                "evidence": {"system_prompt_leaked": True, "full_disclosure": True},
            },
        ],
    }


def test_json_formatter():
    """Test JSON formatter."""
    console.print("\n[cyan]Testing JSON Formatter...[/cyan]")

    from pit.reporting.formatters import JSONFormatter

    formatter = JSONFormatter()
    data = create_mock_report_data()

    try:
        output = formatter.format(data)

        # Validate JSON
        import json
        parsed = json.loads(output)

        assert "metadata" in parsed
        assert "summary" in parsed
        assert "results" in parsed
        assert len(parsed["results"]) == 5

        console.print("  [green]✓ JSON formatter works correctly[/green]")
        console.print(f"  [dim]Output size: {len(output)} bytes[/dim]")

        return True
    except Exception as e:
        console.print(f"  [red]✗ JSON formatter failed: {e}[/red]")
        return False


def test_yaml_formatter():
    """Test YAML formatter."""
    console.print("\n[cyan]Testing YAML Formatter...[/cyan]")

    try:
        from pit.reporting.formatters import YAMLFormatter
        import yaml as yaml_lib
    except ImportError:
        console.print("  [yellow]⚠ YAML not available (pyyaml not installed)[/yellow]")
        return True  # Not a failure, just skip

    formatter = YAMLFormatter()
    data = create_mock_report_data()

    try:
        output = formatter.format(data)

        # Validate YAML
        parsed = yaml_lib.safe_load(output)

        assert "metadata" in parsed
        assert "summary" in parsed
        assert "results" in parsed

        console.print("  [green]✓ YAML formatter works correctly[/green]")
        console.print(f"  [dim]Output size: {len(output)} bytes[/dim]")

        return True
    except Exception as e:
        console.print(f"  [red]✗ YAML formatter failed: {e}[/red]")
        return False


def test_html_formatter():
    """Test HTML formatter."""
    console.print("\n[cyan]Testing HTML Formatter...[/cyan]")

    try:
        from pit.reporting.formatters import HTMLFormatter
    except ImportError:
        console.print("  [yellow]⚠ HTML formatter not available (jinja2 not installed)[/yellow]")
        return True  # Not a failure, just skip

    formatter = HTMLFormatter()
    data = create_mock_report_data()

    try:
        output = formatter.format(data)

        # Basic HTML validation
        assert "<!DOCTYPE html>" in output
        assert "<html" in output
        assert "</html>" in output
        assert "Prompt Injection Test Report" in output
        assert "Direct Instruction Override" in output

        console.print("  [green]✓ HTML formatter works correctly[/green]")
        console.print(f"  [dim]Output size: {len(output)} bytes[/dim]")

        # Check for critical elements
        required_elements = [
            "summary",
            "Total Tests",
            "Successful Attacks",
            "Test Results",
        ]

        for element in required_elements:
            if element.lower() not in output.lower():
                console.print(f"  [yellow]⚠ Missing element: {element}[/yellow]")

        return True
    except Exception as e:
        console.print(f"  [red]✗ HTML formatter failed: {e}[/red]")
        console.print_exception()
        return False


def test_save_report():
    """Test save_report function."""
    console.print("\n[cyan]Testing save_report Function...[/cyan]")

    from pit.reporting.formatters import save_report
    import tempfile
    import os

    data = create_mock_report_data()

    # Test with temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        test_files = [
            ("test_report.json", "json"),
            ("test_report.yaml", "yaml"),
            ("test_report.html", "html"),
        ]

        for filename, expected_format in test_files:
            try:
                output_path = Path(tmpdir) / filename
                result_path = save_report(data, output_path)

                assert result_path.exists()
                assert result_path.stat().st_size > 0

                console.print(f"  [green]✓ Saved {filename} ({result_path.stat().st_size} bytes)[/green]")

            except ImportError:
                console.print(f"  [yellow]⚠ Skipped {filename} (dependencies not available)[/yellow]")
            except Exception as e:
                console.print(f"  [red]✗ Failed to save {filename}: {e}[/red]")
                return False

    return True


def test_format_report():
    """Test format_report convenience function."""
    console.print("\n[cyan]Testing format_report Function...[/cyan]")

    from pit.reporting.formatters import format_report

    data = create_mock_report_data()

    formats_to_test = ["json"]  # Only test JSON by default

    try:
        import yaml
        formats_to_test.append("yaml")
    except ImportError:
        pass

    try:
        import jinja2
        formats_to_test.append("html")
    except ImportError:
        pass

    for fmt in formats_to_test:
        try:
            output = format_report(data, format=fmt)
            assert len(output) > 0
            console.print(f"  [green]✓ format_report('{fmt}') works[/green]")
        except Exception as e:
            console.print(f"  [red]✗ format_report('{fmt}') failed: {e}[/red]")
            return False

    # Test invalid format
    try:
        format_report(data, format="invalid_format")
        console.print("  [red]✗ Invalid format not rejected[/red]")
        return False
    except ValueError:
        console.print("  [green]✓ Invalid format properly rejected[/green]")

    return True


def main():
    """Run all report tests."""
    console.print("[bold cyan]📊 Report Generation Test Suite[/bold cyan]\n")

    tests = [
        ("JSON Formatter", test_json_formatter),
        ("YAML Formatter", test_yaml_formatter),
        ("HTML Formatter", test_html_formatter),
        ("Save Report", test_save_report),
        ("Format Report", test_format_report),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            console.print(f"\n[red]Test '{name}' crashed: {e}[/red]")
            console.print_exception()
            results[name] = False

    # Summary
    console.print("\n" + "="*60)
    console.print("[bold]Test Summary[/bold]")
    console.print("="*60)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for name, result in results.items():
        status = "[green]✓ PASSED[/green]" if result else "[red]✗ FAILED[/red]"
        console.print(f"  {name}: {status}")

    console.print(f"\n[bold]{passed}/{total} tests passed[/bold]")

    if passed == total:
        console.print("\n[green]🎉 All report tests passed![/green]")
        return 0
    else:
        console.print(f"\n[red]❌ {total - passed} test(s) failed[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
