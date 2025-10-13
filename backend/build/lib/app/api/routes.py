from fastapi import APIRouter, Depends, File, UploadFile
from fastapi import HTTPException, status

from ..schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatListResponse,
    FileUploadResponse,
    ChatHistoryResponse,
    ProjectListResponse,
)
from ..services.chat_manager import ChatManager
from ..services.dependencies import get_chat_manager

api_router = APIRouter()


@api_router.get("/projects", response_model=ProjectListResponse, tags=["projects"])
async def list_projects(chat_manager: ChatManager = Depends(get_chat_manager)) -> ProjectListResponse:
    return ProjectListResponse(projects=chat_manager.get_projects())


@api_router.get("/chats", response_model=ChatListResponse, tags=["chats"])
async def list_chats(chat_manager: ChatManager = Depends(get_chat_manager)) -> ChatListResponse:
    return ChatListResponse(chats=chat_manager.get_chats())


@api_router.post(
    "/chat/{chat_id}/files",
    response_model=FileUploadResponse,
    tags=["chats"],
)
async def upload_files(
    chat_id: str,
    files: list[UploadFile] = File(...),
    chat_manager: ChatManager = Depends(get_chat_manager),
) -> FileUploadResponse:
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided")

    stored = await chat_manager.store_files(chat_id, files)
    return FileUploadResponse(file_ids=stored)


@api_router.post(
    "/chat/{chat_id}/respond",
    response_model=ChatCompletionResponse,
    tags=["chats"],
)
async def create_completion(
    chat_id: str,
    payload: ChatCompletionRequest,
    chat_manager: ChatManager = Depends(get_chat_manager),
) -> ChatCompletionResponse:
    try:
        response = await chat_manager.generate_response(chat_id, payload)
    except RuntimeError as exc:  # pragma: no cover - placeholder error handling
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return response


@api_router.get(
    "/chat/{chat_id}/messages",
    response_model=ChatHistoryResponse,
    tags=["chats"],
)
async def get_chat_messages(
    chat_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager),
) -> ChatHistoryResponse:
    messages = chat_manager.get_chat_messages(chat_id)
    return ChatHistoryResponse(messages=messages)
