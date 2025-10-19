from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import httpx
from openai import AsyncOpenAI, OpenAIError


class OpenAIClient:
    """Async client for the OpenAI Responses API."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        api_key = _resolve_openai_api_key()
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable is required to contact OpenAI."
            )

        # The OpenAI SDK uses httpx under the hood. Configure a shared AsyncClient so we
        # can set a tighter timeout suitable for API requests from the backend service.
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


@lru_cache(maxsize=1)
def _resolve_openai_api_key() -> str | None:
    """Resolve the OpenAI API key from the environment or a nearby .env file."""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key

    for directory in Path(__file__).resolve().parents:
        env_file = directory / ".env"
        if not env_file.exists():
            continue

        try:
            contents = env_file.read_text()
        except OSError:
            continue

        for raw_line in contents.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            key, _, value = line.partition("=")
            if key.strip() != "OPENAI_API_KEY":
                continue

            cleaned_value = value.split("#", 1)[0].strip().strip('"').strip("'")
            return cleaned_value or None

    return None
