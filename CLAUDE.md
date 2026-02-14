# CLAUDE.md

## Project Overview

AI Chat — a minimal web chatbot powered by OpenAI's GPT API with real-time streaming responses. Single-file Python backend, vanilla JS frontend, no build tools.

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **AI:** OpenAI Python SDK (v2.x) with `AsyncOpenAI`
- **Frontend:** Vanilla HTML/CSS/JavaScript (no framework, no build step)
- **Static serving:** FastAPI `StaticFiles` mount (frontend served from same process)

## Project Structure

```
├── server.py          # Entire backend: FastAPI app, OpenAI streaming, SSE endpoint
├── static/
│   ├── index.html     # Chat page markup
│   ├── style.css      # Chat UI styles
│   └── app.js         # Chat client logic, SSE stream parsing
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variable template
├── .gitignore         # Python + .env exclusions
└── README.md          # Setup and usage docs
```

## Key Architecture Decisions

- **Single `server.py`** — no package splitting. The app is small enough for one file.
- **No database** — conversation history lives in browser memory and is sent with each POST request.
- **SSE streaming** — `POST /api/chat` returns `text/event-stream`. Each event is `data: {"content": "token"}\n\n`, ending with `data: [DONE]\n\n`.
- **`fetch` + ReadableStream** on frontend (not `EventSource`) because `EventSource` only supports GET. The client manually buffers and parses SSE chunks.
- **Static mount order matters** — `app.mount("/", ...)` must come after all `@app` route definitions to avoid shadowing `/api/*` routes.

## Development

### Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set OPENAI_API_KEY in .env
```

### Run
```bash
python server.py
```
Server starts at http://localhost:8000 with auto-reload enabled.

### Test backend with curl
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Say hello"}]}' \
  --no-buffer
```

### Health check
```bash
curl http://localhost:8000/api/health
```

## API Reference

| Method | Path | Request Body | Response |
|--------|------|-------------|----------|
| `POST` | `/api/chat` | `{"messages": [{"role": "user", "content": "..."}]}` | SSE stream (`text/event-stream`) |
| `GET` | `/api/health` | — | `{"status": "ok"}` |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o` | Model to use for completions |

## Conventions

- **No frameworks on frontend** — keep it vanilla JS. No React, Vue, etc.
- **No build tools** — no npm, webpack, or bundlers. Browser loads files directly.
- **Single backend file** — if the backend grows beyond ~200 lines, consider splitting into a package.
- **System prompt** is defined as `SYSTEM_PROMPT` constant in `server.py`.
- **Error handling** — backend catches OpenAI API errors and sends them as SSE error events. Frontend displays errors inline in the chat.
- **Pydantic models** for request validation (`Message`, `ChatRequest`) in `server.py`.
