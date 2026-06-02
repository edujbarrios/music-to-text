"""Provider-agnostic OpenAI-compatible chat client."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

import requests
from dotenv import load_dotenv


@dataclass(frozen=True)
class LLMConfig:
    api_key: str | None = None
    base_url: str | None = None
    model: str | None = None

    @classmethod
    def from_env(cls) -> "LLMConfig":
        load_dotenv()
        return cls(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL", "https://api.llm7.io/v1"),
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        )


class OpenAICompatibleClient:
    """Minimal client for OpenAI-compatible `/chat/completions` APIs."""

    def __init__(self, config: LLMConfig | None = None, timeout: int = 60) -> None:
        self.config = config or LLMConfig.from_env()
        self.timeout = timeout

    def complete_json(self, prompt: str) -> dict[str, Any]:
        if not self.config.api_key:
            raise ValueError("Missing LLM_API_KEY. Set it or run with --no-llm.")
        base_url = (self.config.base_url or "https://api.llm7.io/v1").rstrip("/")
        model = self.config.model or "gpt-4o-mini"
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "Return only valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return _parse_json_content(content)


def _parse_json_content(content: str) -> dict[str, Any]:
    """Parse JSON returned as raw text, fenced markdown, or surrounding prose."""

    cleaned = content.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        parsed = json.loads(cleaned[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("LLM response JSON must be an object.")
    return parsed
