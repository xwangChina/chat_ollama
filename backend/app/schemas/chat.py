from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectSummary(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class ChatSessionSummary(BaseModel):
    id: str
    title: str
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True


class ProjectListResponse(BaseModel):
    projects: List[ProjectSummary]


class ChatListResponse(BaseModel):
    chats: List[ChatSessionSummary]


class ChatCompletionRequest(BaseModel):
    message: str
    file_ids: List[str] | None = Field(default=None, alias="fileIds")


class ChatCompletionResponse(BaseModel):
    id: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")

    class Config:
        populate_by_name = True


class FileUploadResponse(BaseModel):
    file_ids: List[str] = Field(alias="fileIds")

    class Config:
        populate_by_name = True


class ChatMessage(BaseModel):
    id: str
    author: str
    content: str
    created_at: datetime = Field(..., alias="createdAt")

    class Config:
        populate_by_name = True


class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessage]
