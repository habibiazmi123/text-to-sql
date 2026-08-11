# Text-to-SQL + RAG System — Design Spec

## Overview

Production-grade Text-to-SQL system using RAG. Users ask questions in natural language, system retrieves relevant database context, generates SQL, validates, executes, and returns natural language answers.

## Architecture

**Approach: Monorepo, Go calls Python**

Single repo. Go API is the main entry point. Python AI service is internal-only, called via HTTP REST.

```
┌──────────────┐
│   Frontend   │  (deferred to later phase)
│   Next.js    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Go API     │  :8080 — routing, DB, auth, SQL execution
└──────┬───────┘
       │ HTTP (internal)
       ▼
┌──────────────┐
│ Python AI    │  :8000 — RAG, LLM, SQL validation
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  PostgreSQL  │  :5432 — pgvector, application data
└──────────────┘
```

## Project Structure

```
text-to-sql/
├── backend/                    # Go API
│   ├── cmd/api/main.go
│   ├── internal/
│   │   ├── handler/           # HTTP handlers
│   │   ├── service/           # Business logic
│   │   ├── repository/        # DB queries (GORM)
│   │   ├── middleware/         # CORS, logging
│   │   ├── model/             # Domain models
│   │   └── config/            # Env-based config
│   ├── migrations/
│   ├── go.mod
│   └── Dockerfile
├── ai-service/                 # Python AI/RAG
│   ├── app/
│   │   ├── api/               # FastAPI routes
│   │   ├── agents/            # LangGraph agents (future)
│   │   ├── rag/               # RAG retrieval logic
│   │   ├── embeddings/        # Local embedding model
│   │   ├── sql/               # SQL validation + execution
│   │   ├── llm/               # OpenAI-compatible client
│   │   └── config/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Next.js (deferred)
├── docker-compose.yml
├── Makefile
└── README.md
```

## Database Schema

### Core Tables

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Regions
CREATE TABLE regions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) NOT NULL UNIQUE,
    parent_region_id UUID REFERENCES regions(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Customers
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE,
    phone VARCHAR(50),
    segment VARCHAR(50) DEFAULT 'standard',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Products
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    price NUMERIC(12,2) NOT NULL,
    sku VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Orders
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    region_id UUID NOT NULL REFERENCES regions(id),
    order_date TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(30) DEFAULT 'pending',
    total_amount NUMERIC(14,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Order Items
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id),
    product_id UUID NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL
);

-- Payments
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id),
    method VARCHAR(30) NOT NULL,
    amount NUMERIC(14,2) NOT NULL,
    status VARCHAR(30) DEFAULT 'pending',
    paid_at TIMESTAMP
);
```

### RAG Metadata Tables

```sql
-- Business rules for RAG
CREATE TABLE business_rules (
    id SERIAL PRIMARY KEY,
    term VARCHAR(100) NOT NULL,
    definition TEXT NOT NULL,
    example_sql TEXT,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Verified SQL examples for RAG
CREATE TABLE sql_examples (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    sql TEXT NOT NULL,
    description TEXT,
    difficulty VARCHAR(20) DEFAULT 'medium',
    embedding vector(384),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Seed Data

- 5 regions (Jawa Barat, Jawa Timur, DKI Jakarta, Jawa Tengah, Banten)
- ~500 customers (diverse segments)
- ~50 products (various categories)
- ~1000 orders (spread across 6 months)
- ~2000 order items
- ~1000 payments (mix of methods and statuses)
- 10+ business rules (revenue definition, active user, churned customer, etc.)
- 10+ SQL examples (common queries)

## Go API Design

### Endpoints

```
POST   /api/v1/query              # Main text-to-SQL endpoint
GET    /api/v1/query/:id          # Get query result by ID
GET    /api/v1/query/history      # Recent queries (paginated)
POST   /api/v1/schema/refresh     # Re-index database schema
GET    /api/v1/health             # Health check
```

### Internal Python AI Service Endpoints

```
POST /ai/retrieve    # RAG retrieval (schema + business rules + examples)
POST /ai/generate    # SQL generation from context
POST /ai/validate    # SQL validation
POST /ai/summarize   # Result → natural language
POST /ai/index       # Index schema/business rules into pgvector
```

### Query Flow

```
Phase 1 (no RAG):
1. Receive question
2. Go API reads full schema from information_schema
3. Call Python /ai/generate → get SQL + metadata
4. Validate SQL (read-only check, whitelist)
5. Execute SQL with timeout + row limit
6. Call Python /ai/summarize → natural language answer
7. Store result + return

Phase 2+ (with RAG):
1. Receive question + optional conversation_id
2. Call Python /ai/retrieve → get relevant context (schema, rules, examples)
3. Call Python /ai/generate → get SQL + metadata
4. Validate SQL (read-only check, whitelist)
5. Execute SQL with timeout + row limit
6. Call Python /ai/summarize → natural language answer
7. Store result + return
```

### Security

- Dedicated `text_to_sql_user` with SELECT-only permissions
- SQL validation: reject anything except SELECT/WITH
- Query timeout: 30s default
- Row limit: 1000 rows max
- Block system tables (`pg_*`, `information_schema`)
- Table/column whitelist from schema introspection

### Dependencies

- `gorm.io/gorm` + `gorm.io/driver/postgres`
- `github.com/gin-gonic/gin` (HTTP router)
- `github.com/joho/godotenv` (env config)

## Python AI Service Design

### Endpoints (Internal Only)

```
POST /ai/retrieve    → retrieves schema context, business rules, SQL examples
POST /ai/generate    → generates SQL from context + question
POST /ai/validate    → validates SQL安全性
POST /ai/summarize   → converts SQL result to natural language
POST /ai/index       → indexes schema/business rules into pgvector
```

### RAG Pipeline (Phase 1 — without RAG)

Phase 1 sends full relevant schema to LLM (no vector search yet):

```
Question
  ↓
Schema introspection (read information_schema)
  ↓
Assemble context (all tables + columns + types)
  ↓
LLM generates SQL (structured JSON output)
  ↓
SQL validation (parse, whitelist check)
  ↓
Execute via Go API (read-only)
  ↓
Result → LLM summarizes to natural language
```

### RAG Pipeline (Full — Phases 2-4)

```
Question
  ↓
Intent Detection (keyword + embedding similarity)
  ↓
Parallel retrieval:
  ├── Schema RAG (pgvector similarity search)
  ├── Business Rules RAG (pgvector search)
  └── SQL Examples RAG (pgvector search)
  ↓
Context assembly
  ↓
LLM generates SQL
  ↓
SQL validation
  ↓
Execute
  ↓
Summarize
```

### Embedding Model

- `sentence-transformers/all-MiniLM-L6-v2`
- 384 dimensions
- Runs locally (no API dependency)
- Used for: schema embeddings, business rule embeddings, SQL example embeddings

### LLM Client

- OpenAI-compatible API format
- Configurable `base_url` + `api_key` + `model` via env vars
- Default: whatever provider the user configures

### SQL Validation

- Parse with `sqlparse`
- Reject: INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, GRANT, REVOKE
- Allow: SELECT, WITH only
- Check table/column whitelist
- Block `pg_*`, `information_schema` tables

### Dependencies

- `fastapi` + `uvicorn`
- `sqlparse`
- `sentence-transformers`
- `pgvector` (Python client)
- `psycopg2`
- `openai` (OpenAI-compatible client)
- `pydantic`

## Docker Compose

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    ports: "5432:5432"
    volumes: pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: text_to_sql
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: app_password

  go-api:
    build: ./backend
    ports: "8080:8080"
    depends_on: postgres
    environment:
      DATABASE_URL: postgres://app_user:app_password@postgres:5432/text_to_sql?sslmode=disable
      AI_SERVICE_URL: http://ai-service:8000

  ai-service:
    build: ./ai-service
    ports: "8000:8000"
    depends_on: postgres
    environment:
      DATABASE_URL: postgres://app_user:app_password@postgres:5432/text_to_sql?sslmode=disable
      LLM_BASE_URL: http://host.docker.internal:11434/v1
      LLM_API_KEY: ""
      LLM_MODEL: gpt-4o
      EMBEDDING_MODEL: all-MiniLM-L6-v2

volumes:
  pgdata:
```

## Makefile

```makefile
dev:
	docker compose up --build

test:
	cd backend && go test ./...
	cd ai-service && python -m pytest

lint:
	cd backend && golangci-lint run
	cd ai-service && ruff check

migrate:
	cd backend && go run cmd/migrate/main.go

seed:
	cd backend && go run cmd/seed/main.go

rag-index:
	curl -X POST http://localhost:8000/ai/index
```

## Phase 1 Scope

**Included:**
1. Docker Compose (postgres, go-api, ai-service)
2. Database schema + seed data (e-commerce)
3. Go API with `/api/v1/query` endpoint
4. Python AI service:
   - Schema introspection (read `information_schema`)
   - Direct schema → LLM → SQL (no RAG yet)
   - SQL validation (read-only, whitelist)
   - Query execution with timeout + row limit
   - Result → natural language summarization
5. Makefile with `dev`, `test`, `lint`, `migrate`, `seed`
6. Basic tests for SQL validation + query flow

**Deferred:**
- Phase 2: Schema RAG (pgvector embeddings)
- Phase 3: Business Knowledge RAG
- Phase 4: SQL Example RAG
- Phase 5: SQL validation pipeline (EXPLAIN, retry loop)
- Phase 6: Query planning, clarification, conversation context
- Phase 7: Observability, evaluation, metrics
- Frontend (Next.js)

## Engineering Rules

1. No dumping entire schema into every LLM prompt (Phase 2+ fixes this)
2. Never execute unvalidated SQL
3. Read-only database user
4. Validate SQL before execution
5. Limit retries
6. Query timeouts + row limits
7. Configurable LLM provider
8. Structured JSON output from LLM
9. Tests for every major component
