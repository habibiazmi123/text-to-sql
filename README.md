# Text-to-SQL + RAG

Ask questions in natural language (Indonesian or English) and get answers from a PostgreSQL database — without writing SQL. The system turns *question → relevant schema → SQL → validation → execution → natural language answer* using RAG to feed the LLM only the context it needs.

```
"Berapa total revenue bulan lalu berdasarkan region?"
    ↓
RAG retrieves (schema + business rules + similar SQL examples)
    ↓
LLM generates SQL → validated (SELECT-only, EXPLAIN check, retry loop)
    ↓
Executed via read-only DB user → result summarized back to you
"Total revenue bulan lalu adalah Rp 2,4 miliar..."
```

## Features

- **Schema RAG** — database metadata (tables, columns, PKs/FKs, relationships) embedded with pgvector; only relevant tables/columns are sent to the LLM, not the whole schema.
- **Business Knowledge RAG** — business definitions (e.g. "revenue = successfully paid orders") stored as indexable rules so the LLM never guesses from column names.
- **SQL Example RAG** — verified question→SQL pairs retrieved as guidance (not copied blindly).
- **SQL safety** — parser validation, statement whitelist (SELECT/WITH only), forbidden-keyword rejection, EXPLAIN cost check, retry-with-correction loop (capped), and execution against a dedicated read-only PostgreSQL user.
- **Conversation context** — follow-up questions ("bagaimana dengan bulan sebelumnya?") carry history.
- **Clarification** — ambiguous questions trigger a clarifying response instead of guessing.
- **Result summarization** — executed results are summarized into a concise natural-language answer.
- **Observability** — structured JSON logs plus Prometheus-style metrics (`/metrics`).

## Tech Stack

| Layer | Tech |
|---|---|
| Backend API | Go 1.25, Gin, GORM, pgx |
| AI / RAG service | Python, FastAPI, sentence-transformers embeddings, OpenAI-compatible client |
| LLM | Configurable, OpenAI-compatible (OpenAI, Ollama, vLLM, …) |
| Database | PostgreSQL 17 + pgvector |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4, shadcn/ui, TanStack Query |
| Infra | Docker Compose |

## Architecture

```
┌──────────────┐
│  Frontend    │  Next.js (:3000) — chat UI
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────┐
│  Go API      │  :8080 — routing, DB, metrics
└──────┬───────┘
       │ HTTP (internal)
       ▼
┌──────────────┐
│ Python AI    │  :8000 — RAG, LLM, SQL validation
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ PostgreSQL   │  :5432 — app data + pgvector embeddings
└──────────────┘
```

The Go API is the single entry point; the Python AI service is internal-only and called over HTTP.

## Project Structure

```
text-to-sql/
├── backend/            # Go API (Gin)
│   ├── cmd/api/        # entrypoint: /health, /api/v1/query, /metrics
│   ├── internal/       # config, handler, service, model, middleware, metrics, sqlvalidator
│   ├── migrations/     # 001_extensions … 005_schema_embeddings (auto-run by Docker)
│   ├── seeds/          # seed.sql demo data (regions, customers, products, orders, payments)
│   └── tests/
├── ai-service/         # Python AI/RAG (FastAPI)
│   ├── app/
│   │   ├── api/        # /ai/generate-with-retry, /ai/validate, /ai/summarize, /ai/retrieve, /ai/index
│   │   ├── schema/     # PostgreSQL schema introspection
│   │   ├── sql/        # SQL generator + validator (EXPLAIN checks)
│   │   ├── rag/        # business-rules + SQL-example indexing/retrieval
│   │   ├── embeddings/ # embedding model, schema indexer/retriever
│   │   └── llm/        # OpenAI-compatible chat client
│   ├── tests/          # pytest suite
│   └── eval/           # evaluation dataset + runner (executes SQL, compares results)
├── frontend/           # Next.js chat UI (shadcn/ui)
│   └── app/components/chat/
├── docs/               # design spec & plans
├── docker-compose.yml  # postgres, go-api, ai-service
├── Makefile
├── PRD.md
└── .env.example
```

## Getting Started

### 1. Environment

```bash
cp .env.example .env
```

Set `LLM_MODEL`, `LLM_BASE_URL`, and `LLM_API_KEY` for your provider. Defaults point at a local OpenAI-compatible server (e.g. Ollama on `http://localhost:11434/v1` with a `gpt-4o`-style model name).

### 2. Infrastructure + AI service setup

```bash
make setup      # create ai-service venv + install dependencies
make infra      # docker compose up -d (postgres + go-api + ai-service)
make migrate    # apply migrations (auto-run on first boot; manual re-run also works)
make seed       # insert demo data
make rag-index  # build schema/business-rules/SQL-example embeddings (POST /ai/index)
```

### 3. Run services locally (optional, instead of the compose containers)

```bash
make run-api    # Go API on :8080
make run-ai     # FastAPI on :8000
cd frontend && cp .env.example .env  # if a frontend .env exists
cd frontend && npm install && npm run dev   # UI on :3000
```

## Usage

Open the frontend at `http://localhost:3000` and ask a question, e.g.:

> **Tampilkan 10 customer dengan revenue terbesar dalam 3 bulan terakhir**

Behind the scenes Go's `POST /api/v1/query` calls the AI service, which retrieves context, generates + validates SQL, then Go executes it and the AI service summarizes the result. Ambiguous questions return a clarification prompt; the generated SQL is validated as read-only before any execution.

### Raw API

```bash
curl -X POST http://localhost:8080/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Total revenue bulan lalu per region"}'
```

Useful endpoints:

- `GET /health` — service health
- `GET /metrics` — Prometheus-style counters/latencies
- `POST /ai/retrieve` — inspect what RAG returns for a question (debugging)

## Testing & Linting

```bash
make lint      # go vet + ruff
make test      # go test + pytest
make evaluate  # run eval dataset against a live DB and compare results
```

## Roadmap

Implemented incrementally per the spec — schema introspection → schema RAG → business-rules RAG → SQL-example RAG → validation/security → retries/clarification/conversation → observability/evaluation. Currently in progress; see `PRD.md` and `docs/` for full design and remaining phases.