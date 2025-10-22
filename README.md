# Chat Ollama Workspace

This repository contains the initial scaffolding for a full-stack web experience that mirrors the ChatGPT interface while being powered entirely by locally hosted services:

- **Frontend**: Next.js 14 application providing the chat UI, history sidebar, and file uploads.
- **Backend**: FastAPI service coordinating conversations, local Ollama inference, and placeholders for Model Context Protocol (MCP) integrations.

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
- A locally running [Ollama](https://ollama.ai/) container exposing `http://localhost:11434`.

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

## Tunneling
To enable local laptop (Windows) to reach a remote FastAPI server on 10.80.103.68:8000 as if it were running at localhost:8000.
ssh -L 8000:localhost:8000 user@10.80.103.68

#### Environment variables

- `OPENAI_API_KEY` (required): API key used by the backend to call the OpenAI Responses API.
- `OPENAI_BASE_URL` (optional): Override the API base URL. Defaults to `https://api.openai.com/v1`.
- `OPENAI_MODEL` (optional): Model name to use. Defaults to `gpt-4o-mini`.
- `LOG_LEVEL` (optional): Set to `DEBUG` for verbose logs (`INFO` by default).
- `NEXT_PUBLIC_API_BASE_URL` (optional, frontend): URL of the backend (defaults to `http://localhost:8000`).

> Note: Although this project is named "Chat Ollama", the current backend implementation calls the OpenAI Responses API. A local Ollama client can be added in a future iteration.

#### Troubleshooting

- If the chat UI shows: "Sorry, something went wrong while contacting the backend.", the backend likely returned a non-2xx status for `POST /chat/{id}/respond`.
  - Confirm your `OPENAI_API_KEY` is available in the same shell/process where you start `uvicorn`.
  - Check the backend logs for the detailed error (status and message from OpenAI).
  - Verify the frontend is pointing to the right backend URL (`NEXT_PUBLIC_API_BASE_URL`).
  - Ensure your network/firewall/proxy allows outbound HTTPS to the OpenAI API, or set `HTTPS_PROXY`/`HTTP_PROXY` env vars if required by your environment.

## Next steps

- Replace the in-memory vector store with a persistent database (e.g., PostgreSQL + pgvector or ChromaDB).
- Wire the MCP client to your local MCP server for ClickHouse search and analytics generation.
- Expand the UI with streaming responses, markdown rendering, and richer file previews.
- Harden the error handling and authentication model.
