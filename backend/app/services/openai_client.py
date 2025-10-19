from __future__ import annotations

import os
from typing import Any

import httpx


class OpenAIClient:
    """Async client for the OpenAI Responses API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    async def generate(self, prompt: str) -> str:
        url = f"{self._base_url}/responses"
        payload: dict[str, Any] = {
            "model": self._model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        }
                    ],
                }
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
            except httpx.HTTPError as exc:  # pragma: no cover - integration fallback
                raise RuntimeError("Failed to reach the OpenAI Responses API.") from exc

        data = response.json()
        message_chunks = []
        for output in data.get("output", []):
            if output.get("type") != "message":
                continue
            for content in output.get("content", []):
                if content.get("type") == "output_text":
                    text = content.get("text")
                    if text:
                        message_chunks.append(text)
        if not message_chunks and (fallback := data.get("output_text")):
            message_chunks.append(fallback)

        return "".join(message_chunks) if message_chunks else "I could not generate a response."
