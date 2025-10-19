# Chat Ollama Workspace

This repository contains the initial scaffolding for a full-stack web experience that mirrors the ChatGPT interface while being powered entirely by locally hosted services:

- **Frontend**: Next.js 14 application providing the chat UI, history sidebar, and file uploads.
- **Backend**: FastAPI service coordinating conversations, OpenAI Responses API inference, and placeholders for Model Context Protocol (MCP) integrations.

The current implementation is intentionally lightweight so it can serve as a foundation for future iterations.

## Project structure

```
.
├── backend/   # FastAPI application and service layer
└── frontend/  # Next.js interface
```

## Getting started

### Prerequisites

- Node.js 18+
- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/) exported as `OPENAI_API_KEY`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The development server defaults to `http://localhost:3000` and expects the backend at `http://localhost:8000`. Override with `NEXT_PUBLIC_API_BASE_URL` if needed.

### Backend

```bash
cd backend
pip install .
uvicorn app.main:app --reload
```

The FastAPI service exposes REST endpoints for projects, chat history, file uploads, and chat completions. It currently contains placeholder logic for MCP integrations and a simple in-memory vector store so the development experience remains self-contained.

## Next steps

- Replace the in-memory vector store with a persistent database (e.g., PostgreSQL + pgvector or ChromaDB).
- Wire the MCP client to your local MCP server for ClickHouse search and analytics generation.
- Expand the UI with streaming responses, markdown rendering, and richer file previews.
- Harden the error handling and authentication model.
