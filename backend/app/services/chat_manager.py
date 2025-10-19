from __future__ import annotations

from datetime import datetime
from typing import Iterable

from fastapi import UploadFile

from ..schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatSessionSummary,
    ChatMessage,
    ProjectSummary,
)
from .mcp_client import MCPClient
from .openai_client import OpenAIClient
from .vector_store import MessageRecord, VectorStore


class ChatManager:
    """Coordinates chat state, file storage, and model interactions."""

    def __init__(
        self,
        llm_client: OpenAIClient,
        vector_store: VectorStore,
        mcp_client: MCPClient,
    ) -> None:
        self._llm_client = llm_client
        self._vector_store = vector_store
        self._mcp_client = mcp_client
        self._projects: list[ProjectSummary] = [
            ProjectSummary(
                id="default",
                name="Getting started",
                description="Placeholder project showcasing how to hook the MCP tools",
            )
        ]

    def get_projects(self) -> list[ProjectSummary]:
        return self._projects

    def get_chats(self) -> list[ChatSessionSummary]:
        chat_records = self._vector_store.list_chats()
        if not chat_records:
            now = datetime.utcnow()
            return [
                ChatSessionSummary(id="demo", title="Demo conversation", updated_at=now)
            ]
        return [
            ChatSessionSummary(
                id=str(record["id"]),
                title=str(record["title"]),
                updated_at=record["updated_at"],
            )
            for record in chat_records
        ]

    async def store_files(self, chat_id: str, files: Iterable[UploadFile]) -> list[str]:
        file_ids: list[str] = []
        for uploaded in files:
            content = await uploaded.read()
            file_id = self._vector_store.add_file(chat_id=chat_id, filename=uploaded.filename, content=content)
            file_ids.append(file_id)
        return file_ids

    async def generate_response(
        self,
        chat_id: str,
        payload: ChatCompletionRequest,
    ) -> ChatCompletionResponse:
        enriched_prompt = await self._augment_prompt(chat_id, payload)
        model_response = await self._llm_client.generate(enriched_prompt)
        record = self._vector_store.add_message(
            chat_id=chat_id,
            author="assistant",
            content=model_response,
        )
        return ChatCompletionResponse(id=record.message_id, content=model_response, created_at=record.created_at)

    def get_chat_messages(self, chat_id: str) -> list[ChatMessage]:
        records = self._vector_store.get_messages(chat_id)
        return [
            ChatMessage(
                id=record.message_id,
                author=record.author,
                content=record.content,
                created_at=record.created_at,
            )
            for record in records
        ]

    async def _augment_prompt(
        self,
        chat_id: str,
        payload: ChatCompletionRequest,
    ) -> str:
        self._vector_store.add_message(chat_id=chat_id, author="user", content=payload.message)

        similar_messages: list[MessageRecord] = self._vector_store.similar_messages(
            chat_id=chat_id,
            content=payload.message,
            limit=5,
        )
        context_snippets = "\n".join(f"- {record.content}" for record in similar_messages)

        tool_summaries = await self._mcp_client.get_tool_summaries(payload.message)

        prompt_sections = [
            "You are a helpful assistant running on OpenAI's Responses API.",
            "Conversation context:",
            context_snippets or "(no prior context)",
            "Relevant MCP tool insights:",
            tool_summaries or "(no insights)",
            "User message:",
            payload.message,
        ]

        if payload.file_ids:
            prompt_sections.append(f"Files referenced: {', '.join(payload.file_ids)}")

        return "\n\n".join(prompt_sections)
