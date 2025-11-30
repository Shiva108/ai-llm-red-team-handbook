# file: client.py

import json
from typing import List, Dict, Any, Optional

import requests

from config import LLMConfig, DEFAULT_LLM_CONFIG


class LLMClient:
    """Simple generic client for chat-style LLM APIs."""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or DEFAULT_LLM_CONFIG

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.2,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> str:
        url = f"{self.config.api_base}/chat/completions"
        headers = {
            "Content-Type": "application/json",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        if self.config.extra_headers:
            headers.update(self.config.extra_headers)

        payload: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if self.config.extra_params:
            payload.update(self.config.extra_params)
        if extra_params:
            payload.update(extra_params)

        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=self.config.timeout)
        resp.raise_for_status()
        data = resp.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"Unexpected LLM response format: {data}") from exc
