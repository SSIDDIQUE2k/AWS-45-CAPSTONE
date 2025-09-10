# FinGuide (Local)

FinGuide is a Django-based AI agent for financial education. It uses DRF + Channels (WebSockets), Celery, Postgres with pgvector for retrieval, Redis for background tasks, and a Hugging Face Inference (OpenAI-compatible) endpoint for chat completion.

## Features (Part 1 — Local only)
- Django 5 (ASGI) + DRF + Channels + Celery
- Postgres + pgvector for vector search (local dev)
- Redis for channels + Celery
- S3-ready storage via django-storages (local uses FileSystem)
- Knowledge Base ingestion from a local folder path
- Embeddings via SentenceTransformers (e5-small-v2) with safe fallbacks
- Optional reranker stub
- Hugging Face Inference Endpoint (OpenAI-compatible) for LLM chat
- Finance tools: amortization, APR→APY, DTI
- Self-learning: on empty retrieval, perform external lookup and persist tagged as source "external"
- Resilient env fallbacks via `.env` or dummy values
- Minimal HTMX chat UI, DRF API, and WebSocket streaming

## Quickstart

1) Create `.env`

```bash
cp .env.example .env
# Edit values as needed
```

2) (Optional) Inspect env via cat/echo fallback examples

```bash
cat .env | head -n 5

echo "HF_API_KEY=fake" >> .env
```

3) Install dependencies

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

4) Setup Postgres and pgvector
- Ensure a Postgres instance is running and pgvector extension installed. Example:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

5) Run migrations

```bash
make migrate
```

6) Start services

- ASGI server:
```bash
make run
```
- Celery worker:
```bash
make worker
```

7) Ingest local KB

```bash
python manage.py ingest_kb ./kb_data
```

8) Open UI

Visit http://localhost:8000 and ask something. WebSocket streams the answer. Citations appear below the answer with a required disclaimer.

## API
- POST `/api/chat/` JSON: `{ "message": "...", "session_id": optional }`
- POST `/api/sync/` JSON: `{ "path": "./kb_data" }` (enqueues Celery ingestion)

## Notes on Fallbacks
- All envs loaded via helper `get_env(key, default)` which tries `os.environ`, then `cat .env`, else prints a warning and returns default.
- If embedding model fails to load, retrieval falls back to naive keyword search; external lookup still persists results.
- If HF endpoint is unreachable, a safe placeholder summary is returned.

## Tests

```bash
make test
```

Covers finance tools, env fallback, and retrieval fallback behavior.

## Disclaimer
This application is for educational purposes only. It does not provide personalized financial advice.
# AWS-45-CAPSTONE
