from __future__ import annotations

from functools import lru_cache

from .chat_manager import ChatManager
from .mcp_client import MCPClient
from .openai_client import OpenAIClient
from .vector_store import VectorStore


@lru_cache(maxsize=1)
def get_chat_manager() -> ChatManager:
    openai_client = OpenAIClient()
    vector_store = VectorStore()
    mcp_client = MCPClient()
    return ChatManager(
        llm_client=openai_client,
        vector_store=vector_store,
        mcp_client=mcp_client,
    )
