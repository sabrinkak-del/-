# AI Chat

A minimal AI-powered web chatbot using OpenAI's GPT API with streaming responses.

## Prerequisites

- Python 3.11+
- An OpenAI API key

## Setup

1. Clone the repository

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and set OPENAI_API_KEY
   ```

## Run

```bash
python server.py
```

Open http://localhost:8000 in your browser.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | The OpenAI model to use |

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat` | Send messages, receive streamed AI response (SSE) |
| `GET` | `/api/health` | Health check |
