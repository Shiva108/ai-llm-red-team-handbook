#!/usr/bin/env python3
"""
Prompt Injection Tester

A professional-grade automated testing framework for LLM prompt injection vulnerabilities.
Based on the AI LLM Red Team Handbook Chapter 14.

Example:
    from prompt_injection_tester import InjectionTester, AttackConfig

    async with InjectionTester(
        target_url="https://api.example.com/v1",
        auth_token="...",
    ) as tester:
        tester.authorize(scope=["all"])
        injection_points = await tester.discover_injection_points()
        results = await tester.run_tests(injection_points=injection_points)
        report = tester.generate_report(format="html")
"""

__version__ = "1.0.0"
__author__ = "AI LLM Red Team Handbook"

from .core import (
    AttackCategory,
    AttackConfig,
    AttackPayload,
    AttackPattern,
    DetectionMethod,
    DetectionResult,
    InjectionPoint,
    InjectionPointType,
    InjectionTester,
    Severity,
    TargetConfig,
    TestContext,
    TestResult,
    TestStatus,
    TestSuite,
)
from .patterns.registry import registry, register_pattern, get_pattern, list_patterns

__all__ = [
    # Core
    "InjectionTester",
    "AttackConfig",
    "TargetConfig",
    "TestResult",
    "TestSuite",
    "InjectionPoint",
    "AttackPattern",
    "AttackPayload",
    # Enums
    "AttackCategory",
    "InjectionPointType",
    "DetectionMethod",
    "Severity",
    "TestStatus",
    # Detection
    "DetectionResult",
    "TestContext",
    # Registry
    "registry",
    "register_pattern",
    "get_pattern",
    "list_patterns",
]
