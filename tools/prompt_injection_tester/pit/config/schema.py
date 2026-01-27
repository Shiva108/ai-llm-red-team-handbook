"""Configuration schema using Pydantic."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class TargetConfig(BaseModel):
    """Target API configuration."""

    url: str = Field(..., description="Target API endpoint URL")
    token: Optional[str] = Field(None, description="Authentication token")
    model: Optional[str] = Field(None, description="Model identifier (e.g., gpt-4, llama3:latest)")
    api_type: str = Field(default="openai", description="API type (openai, anthropic, custom)")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure URL is properly formatted."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class AttackConfig(BaseModel):
    """Attack execution configuration."""

    categories: List[str] = Field(
        default=["direct", "indirect"],
        description="Attack categories to test",
    )
    patterns: Optional[List[str]] = Field(
        None,
        description="Specific pattern IDs to test (overrides categories)",
    )
    exclude_patterns: List[str] = Field(
        default_factory=list,
        description="Pattern IDs to exclude",
    )
    max_concurrent: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum concurrent requests",
    )
    rate_limit: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Requests per second",
    )


class ReportingConfig(BaseModel):
    """Report generation configuration."""

    format: str = Field(
        default="json",
        description="Report format (json, yaml, html)",
    )
    output: Optional[Path] = Field(
        None,
        description="Output file path (auto-generated if not specified)",
    )
    include_cvss: bool = Field(
        default=True,
        description="Include CVSS scores in report",
    )
    include_payloads: bool = Field(
        default=False,
        description="Include attack payloads in report (may be sensitive)",
    )

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Ensure format is supported."""
        allowed = ["json", "yaml", "html"]
        if v not in allowed:
            raise ValueError(f"Format must be one of {allowed}")
        return v


class AuthorizationConfig(BaseModel):
    """Authorization configuration."""

    scope: List[str] = Field(
        default=["all"],
        description="Authorization scope",
    )
    confirmed: bool = Field(
        default=False,
        description="Skip interactive authorization prompt",
    )


class Config(BaseModel):
    """Complete PIT configuration."""

    target: TargetConfig
    attack: AttackConfig = Field(default_factory=AttackConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)
    authorization: AuthorizationConfig = Field(default_factory=AuthorizationConfig)

    @classmethod
    def from_cli_args(
        cls,
        target_url: str,
        token: Optional[str] = None,
        model: Optional[str] = None,
        api_type: str = "openai",
        timeout: int = 30,
        categories: Optional[List[str]] = None,
        patterns: Optional[List[str]] = None,
        max_concurrent: int = 5,
        rate_limit: float = 1.0,
        output_format: str = "json",
        output: Optional[Path] = None,
        include_cvss: bool = True,
        include_payloads: bool = False,
        authorize: bool = False,
    ) -> Config:
        """Create config from CLI arguments."""
        return cls(
            target=TargetConfig(
                url=target_url,
                token=token,
                model=model,
                api_type=api_type,
                timeout=timeout,
            ),
            attack=AttackConfig(
                categories=categories or ["direct", "indirect"],
                patterns=patterns,
                max_concurrent=max_concurrent,
                rate_limit=rate_limit,
            ),
            reporting=ReportingConfig(
                format=output_format,
                output=output,
                include_cvss=include_cvss,
                include_payloads=include_payloads,
            ),
            authorization=AuthorizationConfig(
                confirmed=authorize,
            ),
        )
