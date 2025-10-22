import logging
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
logger = logging.getLogger("app.api.routes")


@api_router.get("/projects", response_model=ProjectListResponse, tags=["projects"])
async def list_projects(chat_manager: ChatManager = Depends(get_chat_manager)) -> ProjectListResponse:
    logger.debug("GET /projects")
    projects = chat_manager.get_projects()
    logger.info("Returned %d projects", len(projects))
    return ProjectListResponse(projects=projects)


@api_router.get("/chats", response_model=ChatListResponse, tags=["chats"])
async def list_chats(chat_manager: ChatManager = Depends(get_chat_manager)) -> ChatListResponse:
    logger.debug("GET /chats")
    chats = chat_manager.get_chats()
    logger.info("Returned %d chats", len(chats))
    return ChatListResponse(chats=chats)


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
    logger.info("POST /chat/%s/files with %d file(s)", chat_id, len(files or []))
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided")

    stored = await chat_manager.store_files(chat_id, files)
    logger.info("Stored %d file(s) for chat %s", len(stored), chat_id)
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
        logger.info("POST /chat/%s/respond payload bytes=%d", chat_id, len(payload.message.encode("utf-8")))
        response = await chat_manager.generate_response(chat_id, payload)
    except RuntimeError as exc:  # pragma: no cover - placeholder error handling
        logger.exception("Completion failed for chat %s: %s", chat_id, exc)
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
    logger.debug("GET /chat/%s/messages", chat_id)
    messages = chat_manager.get_chat_messages(chat_id)
    logger.info("Returned %d message(s) for chat %s", len(messages), chat_id)
    return ChatHistoryResponse(messages=messages)
