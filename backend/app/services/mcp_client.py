from __future__ import annotations

from typing import Any


class MCPClient:
    """Placeholder client for a local Model Context Protocol (MCP) server."""

    def __init__(self) -> None:
        self._connected = False

    async def ensure_connection(self) -> None:
        self._connected = True

    async def get_tool_summaries(self, query: str) -> str:
        await self.ensure_connection()
        return (
            "MCP tools ready. In future iterations this will include ClickHouse search results "
            "and generated analytics for the prompt: "
            f"{query}"
        )

    async def search_clickhouse(self, query: str) -> list[dict[str, Any]]:
        await self.ensure_connection()
        return [{"title": "Placeholder search result", "snippet": f"Query: {query}"}]

    async def generate_graph(self, query: str) -> dict[str, Any]:
        await self.ensure_connection()
        return {
            "type": "line",
            "data": [
                {"label": "t-3", "value": 42},
                {"label": "t-2", "value": 45},
                {"label": "t-1", "value": 49},
            ],
            "description": f"Mock graph for query: {query}",
        }
