#!/usr/bin/env python3
"""
HTTP Client Utilities

Async HTTP client with retry logic, rate limiting, and response handling
for LLM API interactions.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class HTTPResponse:
    """Wrapper for HTTP response data."""
    status: int
    body: str
    json_data: dict[str, Any] | None = None
    headers: dict[str, str] = field(default_factory=dict)
    elapsed_ms: float = 0.0
    error: str | None = None

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300


class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, requests_per_second: float = 1.0):
        self.rate = requests_per_second
        self.tokens = 1.0
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a request can be made."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.tokens = min(1.0, self.tokens + elapsed * self.rate)
            self.last_update = now

            if self.tokens < 1.0:
                wait_time = (1.0 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0.0
            else:
                self.tokens -= 1.0


class AsyncHTTPClient:
    """
    Async HTTP client for LLM API interactions.

    Features:
    - Automatic retry with exponential backoff
    - Rate limiting
    - Request/response logging
    - Timeout handling
    """

    def __init__(
        self,
        base_url: str = "",
        headers: dict[str, str] | None = None,
        timeout: int = 30,
        rate_limit: float = 1.0,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        verify_ssl: bool = True,
    ):
        """
        Initialize the HTTP client.

        Args:
            base_url: Base URL for all requests
            headers: Default headers for all requests
            timeout: Request timeout in seconds
            rate_limit: Maximum requests per second
            retry_count: Number of retries on failure
            retry_delay: Initial delay between retries (exponential backoff)
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip("/")
        self.default_headers = headers or {}
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.rate_limiter = RateLimiter(rate_limit)
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=self.verify_ssl)
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                connector=connector,
            )
        return self._session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def request(
        self,
        method: str,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
        data: str | bytes | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
    ) -> HTTPResponse:
        """
        Make an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (appended to base_url)
            json_data: JSON body data
            data: Raw body data
            headers: Additional headers
            params: Query parameters

        Returns:
            HTTPResponse object
        """
        url = f"{self.base_url}{endpoint}" if endpoint.startswith("/") else endpoint
        request_headers = {**self.default_headers, **(headers or {})}

        last_error = None
        for attempt in range(self.retry_count + 1):
            await self.rate_limiter.acquire()

            start_time = time.monotonic()
            try:
                session = await self._get_session()
                async with session.request(
                    method,
                    url,
                    json=json_data,
                    data=data,
                    headers=request_headers,
                    params=params,
                ) as response:
                    elapsed = (time.monotonic() - start_time) * 1000
                    body = await response.text()

                    json_response = None
                    try:
                        json_response = await response.json()
                    except Exception:
                        pass

                    result = HTTPResponse(
                        status=response.status,
                        body=body,
                        json_data=json_response,
                        headers=dict(response.headers),
                        elapsed_ms=elapsed,
                    )

                    # Don't retry on client errors (4xx)
                    if response.status < 500:
                        return result

                    # Retry on server errors
                    last_error = f"Server error: {response.status}"
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}): {last_error}"
                    )

            except asyncio.TimeoutError:
                elapsed = (time.monotonic() - start_time) * 1000
                last_error = "Request timeout"
                logger.warning(
                    f"Request timeout (attempt {attempt + 1}) after {elapsed:.0f}ms"
                )

            except aiohttp.ClientError as e:
                elapsed = (time.monotonic() - start_time) * 1000
                last_error = str(e)
                logger.warning(
                    f"Client error (attempt {attempt + 1}): {last_error}"
                )

            # Exponential backoff before retry
            if attempt < self.retry_count:
                delay = self.retry_delay * (2 ** attempt)
                await asyncio.sleep(delay)

        # All retries exhausted
        return HTTPResponse(
            status=0,
            body="",
            error=last_error or "Unknown error",
            elapsed_ms=(time.monotonic() - start_time) * 1000,
        )

    async def post(
        self,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> HTTPResponse:
        """Make a POST request."""
        return await self.request("POST", endpoint, json_data=json_data, **kwargs)

    async def get(
        self,
        endpoint: str,
        params: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> HTTPResponse:
        """Make a GET request."""
        return await self.request("GET", endpoint, params=params, **kwargs)


class LLMClient(AsyncHTTPClient):
    """
    Specialized HTTP client for LLM API interactions.

    Supports OpenAI, Anthropic, and custom API formats.
    """

    def __init__(
        self,
        api_type: str = "openai",
        api_key: str = "",
        model: str = "",
        **kwargs: Any,
    ):
        """
        Initialize the LLM client.

        Args:
            api_type: Type of API (openai, anthropic, custom)
            api_key: API key for authentication
            model: Model identifier
            **kwargs: Additional arguments passed to AsyncHTTPClient
        """
        self.api_type = api_type
        self.api_key = api_key
        self.model = model

        # Set up default headers based on API type
        headers = kwargs.pop("headers", {})
        if api_type == "openai":
            headers["Authorization"] = f"Bearer {api_key}"
            headers["Content-Type"] = "application/json"
        elif api_type == "anthropic":
            headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
            headers["Content-Type"] = "application/json"
        else:
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            headers["Content-Type"] = "application/json"

        super().__init__(headers=headers, **kwargs)

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any]]:
        """
        Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters for the API

        Returns:
            Tuple of (response_text, full_response_data)
        """
        if self.api_type == "openai":
            return await self._openai_chat(messages, **kwargs)
        elif self.api_type == "anthropic":
            return await self._anthropic_chat(messages, **kwargs)
        else:
            return await self._custom_chat(messages, **kwargs)

    async def _openai_chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any]]:
        """OpenAI chat completion."""
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            **kwargs,
        }
        payload.pop("model", None)
        payload["model"] = kwargs.get("model", self.model)

        response = await self.post("/v1/chat/completions", json_data=payload)

        if response.ok and response.json_data:
            try:
                content = response.json_data["choices"][0]["message"]["content"]
                return content, response.json_data
            except (KeyError, IndexError):
                pass

        return response.body, {"error": response.error, "status": response.status}

    async def _anthropic_chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any]]:
        """Anthropic messages API."""
        # Extract system message if present
        system = ""
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                filtered_messages.append(msg)

        payload = {
            "model": kwargs.get("model", self.model),
            "messages": filtered_messages,
            "max_tokens": kwargs.get("max_tokens", 1024),
        }
        if system:
            payload["system"] = system

        response = await self.post("/v1/messages", json_data=payload)

        if response.ok and response.json_data:
            try:
                content = response.json_data["content"][0]["text"]
                return content, response.json_data
            except (KeyError, IndexError):
                pass

        return response.body, {"error": response.error, "status": response.status}

    async def _custom_chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any]]:
        """Custom API chat - assumes OpenAI-compatible format."""
        payload = {
            "messages": messages,
            **kwargs,
        }
        if self.model:
            payload["model"] = self.model

        response = await self.post("", json_data=payload)

        if response.ok:
            if response.json_data:
                # Try common response formats
                for path in [
                    ["choices", 0, "message", "content"],
                    ["content", 0, "text"],
                    ["response"],
                    ["text"],
                    ["message"],
                ]:
                    try:
                        data = response.json_data
                        for key in path:
                            data = data[key]
                        return str(data), response.json_data
                    except (KeyError, IndexError, TypeError):
                        continue
            return response.body, {"raw": response.body}

        return response.body, {"error": response.error, "status": response.status}

    async def send_prompt(
        self,
        prompt: str,
        system_prompt: str = "",
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any]]:
        """
        Convenience method to send a single prompt.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Tuple of (response_text, full_response_data)
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return await self.chat(messages, **kwargs)
