#!/usr/bin/env python3
"""
Command-Line Interface for Prompt Injection Tester

Usage:
    python -m prompt_injection_tester --target https://api.example.com --token $API_KEY
    python -m prompt_injection_tester --config config.yaml
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from . import AttackCategory, AttackConfig, InjectionTester

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("prompt_injection_tester")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="prompt_injection_tester",
        description="Automated Prompt Injection Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with URL and token
  %(prog)s --target https://api.openai.com --token $OPENAI_API_KEY

  # Use configuration file
  %(prog)s --config config.yaml

  # Test specific categories
  %(prog)s --target URL --token TOKEN --categories direct indirect

  # Generate HTML report
  %(prog)s --target URL --token TOKEN --output report.html --format html

Security Note:
  Always ensure you have explicit authorization before testing any system.
  Unauthorized testing may be illegal in your jurisdiction.
""",
    )

    # Target configuration
    target_group = parser.add_argument_group("Target Configuration")
    target_group.add_argument(
        "--target", "-t",
        help="Target API URL",
    )
    target_group.add_argument(
        "--token", "-k",
        help="Authentication token",
    )
    target_group.add_argument(
        "--api-type",
        choices=["openai", "anthropic", "custom"],
        default="openai",
        help="API type (default: openai)",
    )
    target_group.add_argument(
        "--config", "-c",
        type=Path,
        help="Configuration file (YAML)",
    )

    # Test configuration
    test_group = parser.add_argument_group("Test Configuration")
    test_group.add_argument(
        "--patterns", "-p",
        nargs="+",
        help="Specific pattern IDs to test",
    )
    test_group.add_argument(
        "--categories",
        nargs="+",
        choices=[c.value for c in AttackCategory],
        help="Attack categories to test",
    )
    test_group.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum concurrent tests (default: 5)",
    )
    test_group.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )
    test_group.add_argument(
        "--rate-limit",
        type=float,
        default=1.0,
        help="Requests per second (default: 1.0)",
    )

    # Output configuration
    output_group = parser.add_argument_group("Output Configuration")
    output_group.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file for report",
    )
    output_group.add_argument(
        "--format", "-f",
        choices=["json", "yaml", "html"],
        default="json",
        help="Output format (default: json)",
    )
    output_group.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )
    output_group.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output except errors",
    )

    # Authorization
    auth_group = parser.add_argument_group("Authorization")
    auth_group.add_argument(
        "--authorize",
        action="store_true",
        help="Confirm authorization to test target",
    )
    auth_group.add_argument(
        "--scope",
        nargs="+",
        default=["all"],
        help="Authorization scope (default: all)",
    )

    # Utility
    parser.add_argument(
        "--list-patterns",
        action="store_true",
        help="List available attack patterns and exit",
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List attack categories and exit",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    return parser.parse_args()


async def run_tests(args: argparse.Namespace) -> int:
    """Run the injection tests."""
    # Create tester
    if args.config:
        tester = InjectionTester.from_config_file(args.config)
    elif args.target and args.token:
        config = AttackConfig(
            max_concurrent=args.max_concurrent,
            patterns=args.patterns or [],
        )
        tester = InjectionTester(
            target_url=args.target,
            auth_token=args.token,
            config=config,
        )
        tester.target_config.api_type = args.api_type
        tester.target_config.timeout = args.timeout
        tester.target_config.rate_limit = args.rate_limit
    else:
        logger.error("Must provide either --config or --target and --token")
        return 1

    # Check authorization
    if not args.authorize:
        print("\n" + "=" * 60)
        print("AUTHORIZATION REQUIRED")
        print("=" * 60)
        print(f"\nTarget: {tester.target_config.base_url}")
        print("\nYou must have explicit authorization to test this system.")
        print("Unauthorized testing may be illegal.\n")
        print("Add --authorize flag to confirm you have authorization.")
        print("=" * 60 + "\n")
        return 1

    tester.authorize(scope=args.scope)

    # Parse categories
    categories = None
    if args.categories:
        categories = [AttackCategory(c) for c in args.categories]

    # Run tests
    async with tester:
        logger.info(f"Starting tests against {tester.target_config.base_url}")

        # Discover injection points
        injection_points = await tester.discover_injection_points()
        logger.info(f"Discovered {len(injection_points)} injection points")

        # Run tests
        results = await tester.run_tests(
            patterns=args.patterns,
            categories=categories,
            injection_points=injection_points,
            max_concurrent=args.max_concurrent,
        )

        # Generate report
        report = tester.generate_report(format=args.format, include_cvss=True)

        # Output
        if args.output:
            with open(args.output, "w") as f:
                if args.format == "json":
                    json.dump(report, f, indent=2, default=str)
                else:
                    f.write(str(report))
            logger.info(f"Report written to {args.output}")
        elif not args.quiet:
            if args.format == "json":
                print(json.dumps(report, indent=2, default=str))
            else:
                print(report)

        # Summary
        if not args.quiet:
            print("\n" + "=" * 60)
            print("TEST SUMMARY")
            print("=" * 60)
            print(f"Total Tests: {results.total_tests}")
            print(f"Successful Attacks: {results.successful_attacks}")
            print(f"Success Rate: {results.success_rate:.1%}")
            if results.successful_attacks > 0:
                print("\nVulnerabilities found by severity:")
                for sev, tests in results.by_severity.items():
                    print(f"  {sev.value.upper()}: {len(tests)}")
            print("=" * 60)

    return 0 if results.successful_attacks == 0 else 2


def list_available_patterns() -> None:
    """List all available attack patterns."""
    from .patterns.registry import registry

    if len(registry) == 0:
        registry.load_builtin_patterns()

    print("\nAvailable Attack Patterns:")
    print("=" * 60)

    for category in AttackCategory:
        patterns = registry.list_by_category(category)
        if patterns:
            print(f"\n{category.value}:")
            for pid in patterns:
                pattern_class = registry.get(pid)
                if pattern_class:
                    print(f"  - {pid}: {pattern_class.name}")

    print("\n" + "=" * 60)


def list_categories() -> None:
    """List all attack categories."""
    print("\nAttack Categories:")
    print("=" * 60)

    for category in AttackCategory:
        print(f"  - {category.value}")

    print("\n" + "=" * 60)


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)

    # Handle utility commands
    if args.list_patterns:
        list_available_patterns()
        return 0

    if args.list_categories:
        list_categories()
        return 0

    # Run tests
    try:
        return asyncio.run(run_tests(args))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            raise
        return 1


if __name__ == "__main__":
    sys.exit(main())
