# file: config.py

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class LLMConfig:
    api_base: str           # e.g. "https://api.openai.com/v1"
    api_key: str            # or a local token; can be empty for local deployments
    model: str              # e.g. "gpt-4.1" or "local-llm"
    timeout: int = 60
    extra_headers: Optional[Dict[str, str]] = None
    extra_params: Optional[Dict[str, Any]] = None


@dataclass
class TestConfig:
    max_tokens: int = 1024
    temperature: float = 0.2
    output_dir: str = "reports"
    # synthetic “sensitive” markers used in tests – replace with your own
    synthetic_identifiers: Dict[str, str] = None


DEFAULT_LLM_CONFIG = LLMConfig(
    api_base="http://localhost:11434/v1",  # example: local LLM endpoint
    api_key="",
    model="local-llm",
    extra_headers=None,
    extra_params=None,
)

DEFAULT_TEST_CONFIG = TestConfig(
    max_tokens=1024,
    temperature=0.2,
    output_dir="reports",
    synthetic_identifiers={
        "employee_id": "EMP-999999",
        "customer_id": "CUST-123456",
        "secret_project": "PROJECT-DRAGONFIRE",
    },
)
