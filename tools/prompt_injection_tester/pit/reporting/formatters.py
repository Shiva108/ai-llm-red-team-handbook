"""
Report formatters for different output formats.

Provides JSON, YAML, and HTML formatters for test reports.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

try:
    from jinja2 import Template
except ImportError:
    Template = None  # type: ignore


class ReportFormatter(ABC):
    """Abstract base class for report formatters."""

    @abstractmethod
    def format(self, report_data: Dict[str, Any]) -> str:
        """
        Format report data into output string.

        Args:
            report_data: Report data dictionary

        Returns:
            Formatted report string
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the file extension for this format."""
        pass


class JSONFormatter(ReportFormatter):
    """Format reports as JSON."""

    def __init__(self, indent: int = 2, sort_keys: bool = False):
        """
        Initialize JSON formatter.

        Args:
            indent: Indentation level
            sort_keys: Whether to sort keys
        """
        self.indent = indent
        self.sort_keys = sort_keys

    def format(self, report_data: Dict[str, Any]) -> str:
        """Format report as JSON."""
        return json.dumps(
            report_data,
            indent=self.indent,
            sort_keys=self.sort_keys,
            default=str,
        )

    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".json"


class YAMLFormatter(ReportFormatter):
    """Format reports as YAML."""

    def __init__(self, default_flow_style: bool = False):
        """
        Initialize YAML formatter.

        Args:
            default_flow_style: Whether to use flow style
        """
        self.default_flow_style = default_flow_style

    def format(self, report_data: Dict[str, Any]) -> str:
        """Format report as YAML."""
        if yaml is None:
            raise ImportError("PyYAML is required for YAML formatting")

        return yaml.dump(
            report_data,
            default_flow_style=self.default_flow_style,
            sort_keys=False,
        )

    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".yaml"


class HTMLFormatter(ReportFormatter):
    """Format reports as HTML."""

    def __init__(self, template_path: Path | None = None):
        """
        Initialize HTML formatter.

        Args:
            template_path: Optional custom template path
        """
        self.template_path = template_path

    def format(self, report_data: Dict[str, Any]) -> str:
        """Format report as HTML."""
        if Template is None:
            raise ImportError("Jinja2 is required for HTML formatting")

        template_str = self._get_template()
        template = Template(template_str)

        return template.render(
            report=report_data,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".html"

    def _get_template(self) -> str:
        """Get HTML template."""
        if self.template_path and self.template_path.exists():
            return self.template_path.read_text()

        return self._get_default_template()

    def _get_default_template(self) -> str:
        """Get default HTML template."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Injection Test Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
        }

        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2em;
        }

        h2 {
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }

        .metadata {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }

        .metadata p {
            margin: 5px 0;
        }

        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }

        .summary-card {
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
            text-align: center;
        }

        .summary-card h3 {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
        }

        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }

        .summary-card.success .value {
            color: #e74c3c;
        }

        .summary-card.rate .value {
            color: #e67e22;
        }

        .result {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
            margin: 15px 0;
            background: #fff;
        }

        .result.success {
            border-left: 4px solid #e74c3c;
        }

        .result.failed {
            border-left: 4px solid #95a5a6;
        }

        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .result-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
        }

        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
        }

        .badge.success {
            background: #e74c3c;
            color: white;
        }

        .badge.failed {
            background: #95a5a6;
            color: white;
        }

        .severity-critical {
            background: #c0392b;
            color: white;
        }

        .severity-high {
            background: #e74c3c;
            color: white;
        }

        .severity-medium {
            background: #f39c12;
            color: white;
        }

        .severity-low {
            background: #27ae60;
            color: white;
        }

        .severity-info {
            background: #3498db;
            color: white;
        }

        .result-details {
            display: grid;
            gap: 10px;
        }

        .detail-row {
            display: flex;
            padding: 8px 0;
            border-bottom: 1px solid #ecf0f1;
        }

        .detail-label {
            font-weight: bold;
            color: #7f8c8d;
            min-width: 150px;
        }

        .detail-value {
            flex: 1;
            color: #2c3e50;
        }

        .response-preview {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 3px;
            padding: 10px;
            font-family: "Courier New", monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
            word-wrap: break-word;
            margin-top: 10px;
        }

        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }

        @media print {
            body {
                background: white;
            }
            .container {
                box-shadow: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Prompt Injection Test Report</h1>

        <div class="metadata">
            <p><strong>Generated:</strong> {{ generated_at }}</p>
            <p><strong>Target:</strong> {{ report.metadata.target }}</p>
            <p><strong>Duration:</strong> {{ "%.2f"|format(report.metadata.duration_seconds) }}s</p>
            <p><strong>Version:</strong> {{ report.metadata.version }}</p>
        </div>

        <h2>Summary</h2>
        <div class="summary">
            <div class="summary-card">
                <h3>Total Tests</h3>
                <div class="value">{{ report.summary.total_tests }}</div>
            </div>
            <div class="summary-card success">
                <h3>Successful Attacks</h3>
                <div class="value">{{ report.summary.successful_attacks }}</div>
            </div>
            <div class="summary-card rate">
                <h3>Success Rate</h3>
                <div class="value">{{ "%.1f"|format(report.summary.success_rate * 100) }}%</div>
            </div>
        </div>

        <h2>Test Results</h2>
        {% if report.results %}
            {% for result in report.results %}
            <div class="result {{ result.status }}">
                <div class="result-header">
                    <div class="result-title">{{ result.test_name }}</div>
                    <div>
                        <span class="badge {{ result.status }}">{{ result.status }}</span>
                        <span class="badge severity-{{ result.severity }}">{{ result.severity }}</span>
                    </div>
                </div>
                <div class="result-details">
                    <div class="detail-row">
                        <div class="detail-label">Pattern:</div>
                        <div class="detail-value">{{ result.pattern }}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Category:</div>
                        <div class="detail-value">{{ result.category }}</div>
                    </div>
                    <div class="detail-row">
                        <div class="detail-label">Confidence:</div>
                        <div class="detail-value">{{ "%.1f"|format(result.confidence * 100) }}%</div>
                    </div>
                    {% if result.detection_methods %}
                    <div class="detail-row">
                        <div class="detail-label">Detection Methods:</div>
                        <div class="detail-value">{{ result.detection_methods|join(", ") }}</div>
                    </div>
                    {% endif %}
                    {% if result.response_preview %}
                    <div class="detail-row">
                        <div class="detail-label">Response Preview:</div>
                        <div class="detail-value">
                            <div class="response-preview">{{ result.response_preview }}</div>
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        {% else %}
            <p>No test results available.</p>
        {% endif %}

        <div class="footer">
            <p>Generated by Prompt Injection Tester v{{ report.metadata.version }}</p>
            <p>Part of the AI LLM Red Team Handbook</p>
        </div>
    </div>
</body>
</html>"""


def format_report(
    report_data: Dict[str, Any],
    format: str = "json",
    **kwargs: Any,
) -> str:
    """
    Format report data using the specified formatter.

    Args:
        report_data: Report data dictionary
        format: Output format (json, yaml, html)
        **kwargs: Additional arguments passed to formatter

    Returns:
        Formatted report string

    Raises:
        ValueError: If format is not supported
    """
    formatters = {
        "json": JSONFormatter,
        "yaml": YAMLFormatter,
        "html": HTMLFormatter,
    }

    formatter_class = formatters.get(format.lower())
    if not formatter_class:
        raise ValueError(f"Unsupported format: {format}")

    formatter = formatter_class(**kwargs)
    return formatter.format(report_data)


def save_report(
    report_data: Dict[str, Any],
    output_path: Path,
    format: str | None = None,
    **kwargs: Any,
) -> Path:
    """
    Format and save report to file.

    Args:
        report_data: Report data dictionary
        output_path: Output file path
        format: Output format (auto-detected from extension if not specified)
        **kwargs: Additional arguments passed to formatter

    Returns:
        Path to saved report

    Raises:
        ValueError: If format cannot be determined
    """
    # Auto-detect format from extension
    if format is None:
        ext = output_path.suffix.lower()
        format_map = {
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".html": "html",
            ".htm": "html",
        }
        format = format_map.get(ext)
        if not format:
            raise ValueError(f"Cannot determine format from extension: {ext}")

    # Format the report
    formatted = format_report(report_data, format, **kwargs)

    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(formatted)

    return output_path
