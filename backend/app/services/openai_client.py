from __future__ import annotations

import os
import logging
from typing import Any

import httpx


logger = logging.getLogger("app.services.openai")


class OpenAIClient:
    """Async client for the OpenAI Responses API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set.")

        # Allow overriding via environment variables
        base = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self._base_url = base.rstrip("/")
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._timeout = timeout

    async def generate(self, prompt: str) -> str:
        url = f"{self._base_url}/responses"
        logger.debug("OpenAI request: url=%s model=%s prompt_len=%d", url, self._model, len(prompt))
        # Use the simplest Responses API shape to maximize compatibility.
        # See: https://api.openai.com/v1/responses
        payload: dict[str, Any] = {
            "model": self._model,
            "input": prompt,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                logger.debug("OpenAI response status: %s", response.status_code)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:  # pragma: no cover - integration fallback
                # Try to surface the API error body for easier debugging upstream.
                detail = exc.response.text if exc.response is not None else str(exc)
                raise RuntimeError(
                    f"OpenAI API error {exc.response.status_code if exc.response else ''}: {detail}"
                ) from exc
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

        result = "".join(message_chunks) if message_chunks else "I could not generate a response."
        logger.debug("OpenAI parsed output_len=%d", len(result))
        return result
