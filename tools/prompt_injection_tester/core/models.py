#!/usr/bin/env python3
"""
Core Data Models for Prompt Injection Tester

Defines the fundamental data structures used throughout the testing framework.
Based on patterns from AI LLM Red Team Handbook Chapter 14.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable


class Severity(Enum):
    """Vulnerability severity levels aligned with CVSS."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AttackCategory(Enum):
    """Categories of prompt injection attacks from Chapter 14."""
    # Direct Injection
    INSTRUCTION_OVERRIDE = "instruction_override"
    ROLE_MANIPULATION = "role_manipulation"
    DELIMITER_CONFUSION = "delimiter_confusion"
    CONTEXT_SWITCHING = "context_switching"

    # Indirect Injection
    DOCUMENT_POISONING = "document_poisoning"
    WEB_INJECTION = "web_injection"
    EMAIL_INJECTION = "email_injection"
    API_RESPONSE_INJECTION = "api_response_injection"
    DATABASE_INJECTION = "database_injection"

    # Advanced Techniques
    MULTI_TURN = "multi_turn"
    PAYLOAD_FRAGMENTATION = "payload_fragmentation"
    ENCODING_OBFUSCATION = "encoding_obfuscation"
    LANGUAGE_SWITCHING = "language_switching"
    LOGICAL_EXPLOIT = "logical_exploit"

    # Tool/Plugin Exploitation
    TOOL_HIJACKING = "tool_hijacking"
    PLUGIN_ABUSE = "plugin_abuse"


class InjectionPointType(Enum):
    """Types of injection points in LLM systems."""
    CHAT_API = "chat_api"
    COMPLETION_API = "completion_api"
    RAG_DOCUMENT = "rag_document"
    RAG_QUERY = "rag_query"
    PLUGIN_INPUT = "plugin_input"
    TOOL_PARAMETER = "tool_parameter"
    FILE_UPLOAD = "file_upload"
    URL_FETCH = "url_fetch"
    EMAIL_CONTENT = "email_content"
    DATABASE_CONTENT = "database_content"
    SYSTEM_PROMPT = "system_prompt"
    USER_MESSAGE = "user_message"


class DetectionMethod(Enum):
    """Methods for detecting successful injection."""
    PATTERN_MATCHING = "pattern_matching"
    BEHAVIORAL_CHANGE = "behavioral_change"
    TOOL_INVOCATION = "tool_invocation"
    DATA_EXFILTRATION = "data_exfiltration"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM_PROMPT_LEAK = "system_prompt_leak"
    SEMANTIC_ANALYSIS = "semantic_analysis"


class TestStatus(Enum):
    """Status of a test execution."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()
    TIMEOUT = auto()


@dataclass
class InjectionPoint:
    """Represents a discovered injection point in an LLM system."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    point_type: InjectionPointType = InjectionPointType.USER_MESSAGE
    endpoint: str = ""
    method: str = "POST"
    parameter: str = ""
    description: str = ""
    requires_auth: bool = False
    auth_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            self.name = f"{self.point_type.value}_{self.id}"


@dataclass
class AttackPayload:
    """A single attack payload with metadata."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    content: str = ""
    category: AttackCategory = AttackCategory.INSTRUCTION_OVERRIDE
    encoding: str = "plain"
    language: str = "en"
    description: str = ""
    success_indicators: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AttackPattern:
    """Defines an attack pattern with multiple payloads and execution strategy."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    category: AttackCategory = AttackCategory.INSTRUCTION_OVERRIDE
    description: str = ""
    payloads: list[AttackPayload] = field(default_factory=list)
    requires_multi_turn: bool = False
    turn_count: int = 1
    encoding_variants: list[str] = field(default_factory=list)
    success_indicators: list[str] = field(default_factory=list)
    detection_methods: list[DetectionMethod] = field(default_factory=list)
    mitre_tactics: list[str] = field(default_factory=list)
    owasp_category: str = ""
    references: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            self.name = f"pattern_{self.category.value}_{self.id}"
        if not self.detection_methods:
            self.detection_methods = [DetectionMethod.PATTERN_MATCHING]


@dataclass
class ConversationTurn:
    """A single turn in a multi-turn conversation."""
    role: str = "user"
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestContext:
    """Context for a test execution including conversation history."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_history: list[ConversationTurn] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    extracted_data: dict[str, Any] = field(default_factory=dict)

    def add_turn(self, role: str, content: str) -> None:
        """Add a conversation turn."""
        self.conversation_history.append(
            ConversationTurn(role=role, content=content)
        )

    def get_history_for_api(self) -> list[dict[str, str]]:
        """Get conversation history in API-compatible format."""
        return [
            {"role": turn.role, "content": turn.content}
            for turn in self.conversation_history
        ]


@dataclass
class DetectionResult:
    """Result of running detection heuristics on a response."""
    detected: bool = False
    method: DetectionMethod = DetectionMethod.PATTERN_MATCHING
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)
    matched_patterns: list[str] = field(default_factory=list)
    extracted_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """Complete result of a single test execution."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    test_name: str = ""
    category: AttackCategory = AttackCategory.INSTRUCTION_OVERRIDE
    injection_point: InjectionPoint | None = None
    pattern: AttackPattern | None = None
    payload_used: AttackPayload | None = None

    # Request/Response
    request: dict[str, Any] = field(default_factory=dict)
    response: str = ""
    response_raw: dict[str, Any] = field(default_factory=dict)

    # Results
    status: TestStatus = TestStatus.PENDING
    success: bool = False
    severity: Severity = Severity.INFO
    confidence: float = 0.0

    # Detection
    detection_results: list[DetectionResult] = field(default_factory=list)

    # Evidence
    evidence: dict[str, Any] = field(default_factory=dict)
    extracted_system_prompt: str | None = None
    triggered_tools: list[str] = field(default_factory=list)
    policy_violations: list[str] = field(default_factory=list)

    # Context
    context: TestContext | None = None

    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "test_name": self.test_name,
            "category": self.category.value,
            "injection_point": {
                "id": self.injection_point.id,
                "name": self.injection_point.name,
                "type": self.injection_point.point_type.value,
                "endpoint": self.injection_point.endpoint,
            } if self.injection_point else None,
            "pattern": {
                "id": self.pattern.id,
                "name": self.pattern.name,
                "category": self.pattern.category.value,
            } if self.pattern else None,
            "payload": self.payload_used.content if self.payload_used else None,
            "request": self.request,
            "response": self.response,
            "status": self.status.name,
            "success": self.success,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "detection_results": [
                {
                    "detected": dr.detected,
                    "method": dr.method.value,
                    "confidence": dr.confidence,
                    "evidence": dr.evidence,
                }
                for dr in self.detection_results
            ],
            "evidence": self.evidence,
            "extracted_system_prompt": self.extracted_system_prompt,
            "triggered_tools": self.triggered_tools,
            "policy_violations": self.policy_violations,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class TestSuite:
    """Collection of test results with aggregate statistics."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    target: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    results: list[TestResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tests(self) -> int:
        return len(self.results)

    @property
    def successful_attacks(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failed_tests(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.FAILED)

    @property
    def success_rate(self) -> float:
        if not self.results:
            return 0.0
        return self.successful_attacks / len(self.results)

    @property
    def by_category(self) -> dict[AttackCategory, list[TestResult]]:
        """Group results by attack category."""
        grouped: dict[AttackCategory, list[TestResult]] = {}
        for result in self.results:
            if result.category not in grouped:
                grouped[result.category] = []
            grouped[result.category].append(result)
        return grouped

    @property
    def by_severity(self) -> dict[Severity, list[TestResult]]:
        """Group successful attacks by severity."""
        grouped: dict[Severity, list[TestResult]] = {}
        for result in self.results:
            if result.success:
                if result.severity not in grouped:
                    grouped[result.severity] = []
                grouped[result.severity].append(result)
        return grouped

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "target": self.target,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "summary": {
                "total_tests": self.total_tests,
                "successful_attacks": self.successful_attacks,
                "failed_tests": self.failed_tests,
                "success_rate": self.success_rate,
            },
            "by_severity": {
                sev.value: len(results)
                for sev, results in self.by_severity.items()
            },
            "by_category": {
                cat.value: len(results)
                for cat, results in self.by_category.items()
            },
            "results": [r.to_dict() for r in self.results],
            "metadata": self.metadata,
        }


@dataclass
class TargetConfig:
    """Configuration for a test target."""
    name: str = ""
    base_url: str = ""
    api_type: str = "openai"  # openai, anthropic, custom
    model: str = ""  # Model identifier (e.g., gpt-4, llama3:latest)
    auth_type: str = "bearer"  # bearer, api_key, none
    auth_token: str = ""
    auth_header: str = "Authorization"
    timeout: int = 30
    rate_limit: float = 1.0  # requests per second
    headers: dict[str, str] = field(default_factory=dict)
    verify_ssl: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AttackConfig:
    """Configuration for attack execution."""
    patterns: list[str] = field(default_factory=list)  # Pattern IDs or categories
    max_concurrent: int = 5
    timeout_per_test: int = 60
    rate_limit: float = 1.0
    retry_count: int = 3
    retry_delay: float = 1.0
    encoding_variants: list[str] = field(default_factory=lambda: ["plain"])
    language_variants: list[str] = field(default_factory=lambda: ["en"])
    multi_turn_enabled: bool = True
    max_turns: int = 10
    stop_on_success: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AttackConfig:
        """Create config from dictionary."""
        return cls(
            patterns=data.get("patterns", []),
            max_concurrent=data.get("max_concurrent", 5),
            timeout_per_test=data.get("timeout_per_test", 60),
            rate_limit=data.get("rate_limit", 1.0),
            retry_count=data.get("retry_count", 3),
            retry_delay=data.get("retry_delay", 1.0),
            encoding_variants=data.get("encoding_variants", ["plain"]),
            language_variants=data.get("language_variants", ["en"]),
            multi_turn_enabled=data.get("multi_turn_enabled", True),
            max_turns=data.get("max_turns", 10),
            stop_on_success=data.get("stop_on_success", False),
            metadata=data.get("metadata", {}),
        )


# Type aliases for callbacks
ResponseCallback = Callable[[str, dict[str, Any]], None]
ProgressCallback = Callable[[int, int, TestResult | None], None]
