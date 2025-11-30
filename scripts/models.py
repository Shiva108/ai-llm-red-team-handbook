# file: models.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class TestResult:
    id: str
    category: str
    description: str
    prompt: str
    response: str
    success: bool
    severity: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class BaseTest:
    """Base class for all LLM red-team tests."""

    id_prefix: str = "BASE"
    category: str = "generic"
    description: str = "Base LLM test"

    def run(self, client: "LLMClient") -> List[TestResult]:
        """Execute one or more test variations. Must be implemented by subclasses."""
        raise NotImplementedError
