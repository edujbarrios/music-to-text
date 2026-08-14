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
        content = _response_content(response.json())
        return _parse_json_content(content)


def _response_content(payload: object) -> str:
    """Extract message content from a chat-completions response."""

    try:
        content = payload["choices"][0]["message"]["content"]  # type: ignore[index]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("LLM response is missing choices[0].message.content.") from exc
    if not isinstance(content, str):
        raise ValueError("LLM response choices[0].message.content must be text.")
    return content


def _parse_json_content(content: str) -> dict[str, Any]:
    """Parse JSON returned as raw text, fenced markdown, or surrounding prose."""

    cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE).strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1).strip()

    parsed = _loads_json_object(cleaned)
    if parsed is None:
        for candidate in reversed(_json_object_candidates(cleaned)):
            parsed = _loads_json_object(candidate)
            if parsed is not None:
                break
    if parsed is None:
        raise json.JSONDecodeError("No JSON object found in LLM response.", cleaned, 0)

    return parsed


def _loads_json_object(value: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        raise ValueError("LLM response JSON must be an object.")
    return parsed


def _json_object_candidates(value: str) -> list[str]:
    candidates: list[str] = []
    stack = 0
    start: int | None = None
    in_string = False
    escaped = False

    for index, char in enumerate(value):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            if stack == 0:
                start = index
            stack += 1
        elif char == "}" and stack:
            stack -= 1
            if stack == 0 and start is not None:
                candidates.append(value[start : index + 1])
                start = None

    return candidates
