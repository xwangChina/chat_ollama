from __future__ import annotations

from functools import lru_cache

from .chat_manager import ChatManager
from .mcp_client import MCPClient
from .ollama_client import OllamaClient
from .vector_store import VectorStore


@lru_cache(maxsize=1)
def get_chat_manager() -> ChatManager:
    ollama = OllamaClient()
    vector_store = VectorStore()
    mcp_client = MCPClient()
    return ChatManager(ollama_client=ollama, vector_store=vector_store, mcp_client=mcp_client)
