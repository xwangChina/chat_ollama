from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

import numpy as np


@dataclass
class MessageRecord:
    message_id: str
    chat_id: str
    author: str
    content: str
    created_at: datetime
    embedding: np.ndarray


class VectorStore:
    """Very small in-memory store with cosine similarity search."""

    def __init__(self, embedding_dimensions: int = 384) -> None:
        self._embedding_dimensions = embedding_dimensions
        self._messages: list[MessageRecord] = []
        self._files: Dict[str, Dict[str, bytes]] = {}

    def _encode(self, text: str) -> np.ndarray:
        rng = np.random.default_rng(abs(hash(text)) % (2**32))
        vector = rng.normal(size=self._embedding_dimensions)
        norm = np.linalg.norm(vector)
        return vector / norm if norm else vector

    def add_message(self, chat_id: str, author: str, content: str) -> MessageRecord:
        embedding = self._encode(content)
        record = MessageRecord(
            message_id=secrets.token_hex(8),
            chat_id=chat_id,
            author=author,
            content=content,
            created_at=datetime.utcnow(),
            embedding=embedding,
        )
        self._messages.append(record)
        return record

    def similar_messages(self, chat_id: str, content: str, limit: int = 5) -> list[MessageRecord]:
        query_embedding = self._encode(content)
        scored: list[tuple[float, MessageRecord]] = []
        for record in self._messages:
            if record.chat_id != chat_id:
                continue
            score = float(np.dot(query_embedding, record.embedding))
            scored.append((score, record))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [record for _, record in scored[:limit]]

    def list_chats(self) -> list[dict[str, object]]:
        by_chat: Dict[str, list[MessageRecord]] = {}
        for record in self._messages:
            by_chat.setdefault(record.chat_id, []).append(record)

        summaries = []
        for chat_id, records in by_chat.items():
            last_message = max(records, key=lambda item: item.created_at)
            summaries.append(
                {
                    "id": chat_id,
                    "title": f"Chat {chat_id[:6]}",
                    "updated_at": last_message.created_at,
                }
            )
        return summaries

    def add_file(self, chat_id: str, filename: str, content: bytes) -> str:
        file_id = secrets.token_hex(8)
        chat_files = self._files.setdefault(chat_id, {})
        chat_files[file_id] = content
        metadata = f"File:{filename}"
        self.add_message(chat_id=chat_id, author="system", content=metadata)
        return file_id

    def get_file(self, chat_id: str, file_id: str) -> bytes | None:
        return self._files.get(chat_id, {}).get(file_id)

    def get_messages(self, chat_id: str) -> list[MessageRecord]:
        history = [record for record in self._messages if record.chat_id == chat_id]
        history.sort(key=lambda record: record.created_at)
        return history
