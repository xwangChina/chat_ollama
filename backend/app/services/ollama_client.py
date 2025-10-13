from __future__ import annotations

from typing import Any, Dict

import httpx


class OllamaClient:
    """Minimal async client for the local Ollama HTTP API."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3") -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def generate(self, prompt: str) -> str:
        url = f"{self._base_url}/api/generate"
        payload: Dict[str, Any] = {"model": self._model, "prompt": prompt, "stream": False}
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
            except httpx.HTTPError as exc:  # pragma: no cover - integration fallback
                raise RuntimeError("Failed to reach Ollama. Is the container running?") from exc

        data = response.json()
        return data.get("response", "I could not generate a response.")
