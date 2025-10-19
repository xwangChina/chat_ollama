from __future__ import annotations

import os

import httpx
from openai import AsyncOpenAI
from openai.error import OpenAIError


class OpenAIClient:
    """Async client for the OpenAI Responses API."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable is required to contact OpenAI."
            )

        transport = httpx.AsyncHTTPTransport(retries=3)
        http_client = httpx.AsyncClient(timeout=httpx.Timeout(30.0), transport=transport)

        self._http_client = http_client
        self._client = AsyncOpenAI(api_key=api_key, http_client=http_client)
        self._model = model

    async def generate(self, prompt: str) -> str:
        try:
            response = await self._client.responses.create(
                model=self._model,
                input=prompt,
            )
        except OpenAIError as exc:  # pragma: no cover - depends on remote API
            raise RuntimeError("Failed to fetch response from OpenAI.") from exc

        output_text: str | None = response.output_text
        if not output_text:
            return "I could not generate a response."
        return output_text

    async def aclose(self) -> None:
        await self._http_client.aclose()

