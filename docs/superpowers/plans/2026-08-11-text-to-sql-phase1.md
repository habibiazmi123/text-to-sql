# Text-to-SQL Phase 1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the core text-to-SQL flow: PostgreSQL → schema introspection → LLM → SQL → validation → execution → natural language answer. No RAG yet.

**Architecture:** Monorepo with Go API (main entry, DB, SQL execution) calling Python AI service (SQL generation, validation, summarization) via internal HTTP. Standard Docker Hub images for infrastructure.

**Tech Stack:** Go (Gin, GORM), Python (FastAPI, sqlparse, openai), PostgreSQL 16 + pgvector, Docker Compose

## Global Constraints

- PostgreSQL 16 with pgvector extension
- Go 1.22+, Python 3.11+
- LLM provider: OpenAI-compatible (configurable base_url, api_key, model)
- SQL validation: read-only (SELECT/WITH only)
- Query timeout: 30s, row limit: 1000
- Dedicated `text_to_sql_user` with SELECT-only
- No Redis (deferred), No frontend (deferred), No RAG (Phase 1 uses full schema)

## File Structure

```
text-to-sql/
├── docker-compose.yml
├── Makefile
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── go.mod
│   ├── cmd/api/main.go
│   ├── internal/
│   │   ├── config/config.go
│   │   ├── handler/health.go
│   │   ├── handler/query.go
│   │   ├── service/query.go
│   │   ├── model/query.go
│   │   └── sqlvalidator/validator.go
│   ├── migrations/
│   │   ├── 001_create_extensions.sql
│   │   ├── 002_create_tables.sql
│   │   ├── 003_create_rag_tables.sql
│   │   └── 004_create_readonly_user.sql
│   └── seeds/seed.sql
├── ai-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/__init__.py
│   │   ├── api/routes.py
│   │   ├── sql/__init__.py
│   │   ├── sql/validator.py
│   │   ├── sql/generator.py
│   │   ├── llm/__init__.py
│   │   ├── llm/client.py
│   │   ├── schema/__init__.py
│   │   └── schema/introspector.py
│   └── tests/
│       ├── __init__.py
│       ├── test_validator.py
│       └── test_generator.py
```

---

## Task 1: Project Scaffolding

**Files:**
- Create: `docker-compose.yml`, `Makefile`, `.env.example`
- Create: `backend/Dockerfile`, `backend/go.mod`
- Create: `ai-service/Dockerfile`, `ai-service/requirements.txt`
- Create: `ai-service/app/__init__.py`, `ai-service/app/main.py`, `ai-service/app/config.py`

- [ ] **Step 1: Create .env.example**

```bash
POSTGRES_DB=text_to_sql
POSTGRES_USER=app_user
POSTGRES_PASSWORD=app_password
DATABASE_URL=postgres://app_user:app_password@postgres:5432/text_to_sql?sslmode=disable
LLM_BASE_URL=http://host.docker.internal:11434/v1
LLM_API_KEY=
LLM_MODEL=gpt-4o
AI_SERVICE_URL=http://ai-service:8000
```

- [ ] **Step 2: Create docker-compose.yml**

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./backend/migrations:/docker-entrypoint-initdb.d
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5

  go-api:
    build: ./backend
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: ${DATABASE_URL}
      AI_SERVICE_URL: ${AI_SERVICE_URL}

  ai-service:
    build: ./ai-service
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: ${DATABASE_URL}
      LLM_BASE_URL: ${LLM_BASE_URL}
      LLM_API_KEY: ${LLM_API_KEY}
      LLM_MODEL: ${LLM_MODEL}

volumes:
  pgdata:
```

- [ ] **Step 3: Create backend/Dockerfile**

```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server ./cmd/api

FROM alpine:3.19
RUN apk --no-cache add ca-certificates
COPY --from=builder /app/server /server
EXPOSE 8080
CMD ["/server"]
```

- [ ] **Step 4: Init Go module and install deps**

```bash
cd backend && go mod init text-to-sql-backend
go get github.com/gin-gonic/gin
go get gorm.io/gorm
go get gorm.io/driver/postgres
go get github.com/google/uuid
```

- [ ] **Step 5: Create ai-service/Dockerfile**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 6: Create ai-service/requirements.txt**

```
fastapi==0.111.0
uvicorn==0.30.1
sqlparse==0.5.0
psycopg2-binary==2.9.9
openai==1.35.0
pydantic-settings==2.3.4
httpx==0.27.0
```

- [ ] **Step 7: Create ai-service/app/__init__.py** (empty)

- [ ] **Step 8: Create ai-service/app/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgres://app_user:app_password@localhost:5432/text_to_sql?sslmode=disable"
    llm_base_url: str = "http://host.docker.internal:11434/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o"

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 9: Create ai-service/app/main.py**

```python
from fastapi import FastAPI

app = FastAPI(title="Text-to-SQL AI Service")


@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 10: Create Makefile**

```makefile
.PHONY: dev test lint seed

dev:
	docker compose up --build

test:
	cd backend && go test ./...
	cd ai-service && python -m pytest tests/

lint:
	cd backend && go vet ./...

seed:
	docker compose exec postgres psql -U app_user -d text_to_sql -f /docker-entrypoint-initdb.d/seeds/seed.sql
```

- [ ] **Step 11: Verify postgres starts**

```bash
cp .env.example .env
docker compose up postgres -d
docker compose ps
```

Expected: postgres container running and healthy.

- [ ] **Step 12: Commit**

```bash
git init
git add -A
git commit -m "feat: project scaffolding with Docker Compose, Go and Python services"
```

---

## Task 2: Database Schema + Migrations + Seed Data

**Files:**
- Create: `backend/migrations/001_create_extensions.sql`
- Create: `backend/migrations/002_create_tables.sql`
- Create: `backend/migrations/003_create_rag_tables.sql`
- Create: `backend/migrations/004_create_readonly_user.sql`
- Create: `backend/seeds/seed.sql`

- [ ] **Step 1: Create 001_create_extensions.sql**

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
```

- [ ] **Step 2: Create 002_create_tables.sql**

```sql
CREATE TABLE IF NOT EXISTS regions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) NOT NULL UNIQUE,
    parent_region_id UUID REFERENCES regions(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE,
    phone VARCHAR(50),
    segment VARCHAR(50) DEFAULT 'standard',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    price NUMERIC(12,2) NOT NULL,
    sku VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    region_id UUID NOT NULL REFERENCES regions(id),
    order_date TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(30) DEFAULT 'pending',
    total_amount NUMERIC(14,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id),
    product_id UUID NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id),
    method VARCHAR(30) NOT NULL,
    amount NUMERIC(14,2) NOT NULL,
    status VARCHAR(30) DEFAULT 'pending',
    paid_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_region ON orders(region_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id);
```

- [ ] **Step 3: Create 003_create_rag_tables.sql**

```sql
CREATE TABLE IF NOT EXISTS business_rules (
    id SERIAL PRIMARY KEY,
    term VARCHAR(100) NOT NULL,
    definition TEXT NOT NULL,
    example_sql TEXT,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sql_examples (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    sql TEXT NOT NULL,
    description TEXT,
    difficulty VARCHAR(20) DEFAULT 'medium',
    embedding vector(384),
    created_at TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 4: Create 004_create_readonly_user.sql**

```sql
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'text_to_sql_user') THEN
        CREATE ROLE text_to_sql_user WITH LOGIN PASSWORD 'text_to_sql_password';
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO text_to_sql_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO text_to_sql_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO text_to_sql_user;
```

- [ ] **Step 5: Create backend/seeds/seed.sql**

```sql
INSERT INTO regions (id, name, code) VALUES
    ('a1000000-0000-0000-0000-000000000001', 'DKI Jakarta', 'JKT'),
    ('a1000000-0000-0000-0000-000000000002', 'Jawa Barat', 'JBR'),
    ('a1000000-0000-0000-0000-000000000003', 'Jawa Timur', 'JTM'),
    ('a1000000-0000-0000-0000-000000000004', 'Jawa Tengah', 'JTG'),
    ('a1000000-0000-0000-0000-000000000005', 'Banten', 'BTN');

INSERT INTO products (id, name, category, price, sku) VALUES
    ('b1000000-0000-0000-0000-000000000001', 'Laptop ASUS ROG', 'Electronics', 15000000, 'ELC-001'),
    ('b1000000-0000-0000-0000-000000000002', 'iPhone 15 Pro', 'Electronics', 22000000, 'ELC-002'),
    ('b1000000-0000-0000-0000-000000000003', 'Samsung Galaxy S24', 'Electronics', 18000000, 'ELC-003'),
    ('b1000000-0000-0000-0000-000000000004', 'Nike Air Max', 'Fashion', 2500000, 'FAS-001'),
    ('b1000000-0000-0000-0000-000000000005', 'Levis 501 Jeans', 'Fashion', 1200000, 'FAS-002'),
    ('b1000000-0000-0000-0000-000000000006', 'Office Chair', 'Furniture', 3500000, 'FUR-001'),
    ('b1000000-0000-0000-0000-000000000007', 'Standing Desk', 'Furniture', 4200000, 'FUR-002'),
    ('b1000000-0000-0000-0000-000000000008', 'Mech Keyboard', 'Electronics', 1800000, 'ELC-004'),
    ('b1000000-0000-0000-0000-000000000009', 'Wireless Mouse', 'Electronics', 500000, 'ELC-005'),
    ('b1000000-0000-0000-0000-000000000010', 'Monitor 27 inch', 'Electronics', 4500000, 'ELC-006');

INSERT INTO customers (id, name, email, phone, segment) VALUES
    ('c1000000-0000-0000-0000-000000000001', 'PT Maju Bersama', 'info@majubersama.co.id', '021-5551234', 'enterprise'),
    ('c1000000-0000-0000-0000-000000000002', 'PT Sejahtera Abadi', 'contact@sejahtera.co.id', '021-5555678', 'enterprise'),
    ('c1000000-0000-0000-0000-000000000003', 'Toko Berkah', 'berkah@gmail.com', '0812-3456-7890', 'standard'),
    ('c1000000-0000-0000-0000-000000000004', 'Warung Makmur', 'makmur@yahoo.com', '0856-1234-5678', 'standard'),
    ('c1000000-0000-0000-0000-000000000005', 'UD Sentosa', 'sentosa@outlook.com', '0878-9012-3456', 'smb');

INSERT INTO orders (id, customer_id, region_id, order_date, status, total_amount) VALUES
    ('d1000000-0000-0000-0000-000000000001', 'c1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', '2026-07-15', 'completed', 37000000),
    ('d1000000-0000-0000-0000-000000000002', 'c1000000-0000-0000-0000-000000000002', 'a1000000-0000-0000-0000-000000000002', '2026-07-20', 'completed', 22500000),
    ('d1000000-0000-0000-0000-000000000003', 'c1000000-0000-0000-0000-000000000003', 'a1000000-0000-0000-0000-000000000003', '2026-07-25', 'completed', 5000000),
    ('d1000000-0000-0000-0000-000000000004', 'c1000000-0000-0000-0000-000000000004', 'a1000000-0000-0000-0000-000000000004', '2026-08-01', 'completed', 1500000),
    ('d1000000-0000-0000-0000-000000000005', 'c1000000-0000-0000-0000-000000000005', 'a1000000-0000-0000-0000-000000000005', '2026-08-05', 'pending', 18500000);

INSERT INTO payments (order_id, method, amount, status, paid_at) VALUES
    ('d1000000-0000-0000-0000-000000000001', 'bank_transfer', 37000000, 'paid', '2026-07-15'),
    ('d1000000-0000-0000-0000-000000000002', 'credit_card', 22500000, 'paid', '2026-07-20'),
    ('d1000000-0000-0000-0000-000000000003', 'e_wallet', 5000000, 'paid', '2026-07-25'),
    ('d1000000-0000-0000-0000-000000000004', 'bank_transfer', 1500000, 'paid', '2026-08-01'),
    ('d1000000-0000-0000-0000-000000000005', 'credit_card', 18500000, 'pending', NULL);

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    ('d1000000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001', 1, 15000000),
    ('d1000000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000008', 1, 1800000),
    ('d1000000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000009', 2, 500000),
    ('d1000000-0000-0000-0000-000000000002', 'b1000000-0000-0000-0000-000000000002', 1, 22000000),
    ('d1000000-0000-0000-0000-000000000002', 'b1000000-0000-0000-0000-000000000004', 1, 2500000),
    ('d1000000-0000-0000-0000-000000000003', 'b1000000-0000-0000-0000-000000000005', 2, 1200000),
    ('d1000000-0000-0000-0000-000000000004', 'b1000000-0000-0000-0000-000000000009', 3, 500000),
    ('d1000000-0000-0000-0000-000000000005', 'b1000000-0000-0000-0000-000000000003', 1, 18000000),
    ('d1000000-0000-0000-0000-000000000005', 'b1000000-0000-0000-0000-000000000006', 1, 3500000);

INSERT INTO business_rules (term, definition, example_sql) VALUES
    ('Revenue', 'Total amount of orders with status = completed and payment status = paid', 'SELECT SUM(o.total_amount) FROM orders o JOIN payments p ON o.id = p.order_id WHERE o.status = ''completed'' AND p.status = ''paid'''),
    ('Active User', 'A customer who has placed at least one order in the last 30 days', 'SELECT DISTINCT customer_id FROM orders WHERE order_date >= CURRENT_DATE - INTERVAL ''30 days'''),
    ('Monthly Revenue', 'Revenue aggregated by month based on order_date', 'SELECT DATE_TRUNC(''month'', order_date), SUM(total_amount) FROM orders WHERE status = ''completed'' GROUP BY 1'),
    ('Enterprise Customer', 'A customer with segment = enterprise', 'SELECT * FROM customers WHERE segment = ''enterprise''');

INSERT INTO sql_examples (question, sql, description, difficulty) VALUES
    ('Berapa total revenue bulan lalu?', 'SELECT SUM(o.total_amount) AS total_revenue FROM orders o JOIN payments p ON o.id = p.order_id WHERE o.status = ''completed'' AND p.status = ''paid'' AND o.order_date >= DATE_TRUNC(''month'', CURRENT_DATE - INTERVAL ''1 month'') AND o.order_date < DATE_TRUNC(''month'', CURRENT_DATE)', 'Calculate total revenue for last month', 'easy'),
    ('10 customer dengan revenue terbesar', 'SELECT c.name, SUM(o.total_amount) AS total_spent FROM customers c JOIN orders o ON c.id = o.customer_id WHERE o.status = ''completed'' GROUP BY c.id, c.name ORDER BY total_spent DESC LIMIT 10', 'Top 10 customers by revenue', 'medium'),
    ('Revenue per region bulan lalu', 'SELECT r.name AS region, SUM(o.total_amount) AS revenue FROM orders o JOIN regions r ON o.region_id = r.id JOIN payments p ON o.id = p.order_id WHERE o.status = ''completed'' AND p.status = ''paid'' AND o.order_date >= DATE_TRUNC(''month'', CURRENT_DATE - INTERVAL ''1 month'') GROUP BY r.id, r.name ORDER BY revenue DESC', 'Revenue breakdown by region', 'medium');
```

- [ ] **Step 6: Test migrations on fresh postgres**

```bash
docker compose down -v
docker compose up postgres -d
sleep 5
docker compose exec postgres psql -U app_user -d text_to_sql -c "\dt"
```

Expected: 8 tables listed.

- [ ] **Step 7: Test seed data and readonly user**

```bash
docker compose exec postgres psql -U app_user -d text_to_sql -c "SELECT COUNT(*) FROM customers"
docker compose exec postgres psql -U text_to_sql_user -d text_to_sql -c "SELECT COUNT(*) FROM customers"
docker compose exec postgres psql -U text_to_sql_user -d text_to_sql -c "INSERT INTO customers (name) VALUES ('test')" 2>&1
```

Expected: counts return, INSERT fails with permission denied.

- [ ] **Step 8: Commit**

```bash
git add backend/migrations/ backend/seeds/
git commit -m "feat: database schema, migrations, seed data, readonly user"
```

---

## Task 3: Go API Foundation

**Files:**
- Create: `backend/internal/config/config.go`
- Create: `backend/internal/model/query.go`
- Create: `backend/internal/handler/health.go`
- Create: `backend/cmd/api/main.go`

- [ ] **Step 1: Create backend/internal/config/config.go**

```go
package config

import "os"

type Config struct {
	DatabaseURL  string
	AIServiceURL string
	ServerPort   string
}

func Load() *Config {
	return &Config{
		DatabaseURL:  getEnv("DATABASE_URL", "postgres://app_user:app_password@localhost:5432/text_to_sql?sslmode=disable"),
		AIServiceURL: getEnv("AI_SERVICE_URL", "http://localhost:8000"),
		ServerPort:   getEnv("SERVER_PORT", "8080"),
	}
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
```

- [ ] **Step 2: Create backend/internal/model/query.go**

```go
package model

import "time"

type QueryRequest struct {
	Question string `json:"question" binding:"required"`
}

type QueryResponse struct {
	ID            string      `json:"id"`
	Question      string      `json:"question"`
	SQL           string      `json:"sql"`
	Reasoning     string      `json:"reasoning"`
	TablesUsed    []string    `json:"tables_used"`
	Result        interface{} `json:"result"`
	Answer        string      `json:"answer"`
	ExecutionTime int64       `json:"execution_time_ms"`
	RowsReturned  int         `json:"rows_returned"`
}

type QueryRecord struct {
	ID            string    `json:"id" gorm:"primaryKey"`
	Question      string    `json:"question"`
	SQL           string    `json:"sql"`
	Reasoning     string    `json:"reasoning"`
	TablesUsed    string    `json:"tables_used"`
	Answer        string    `json:"answer"`
	ExecutionTime int64     `json:"execution_time"`
	RowsReturned  int       `json:"rows_returned"`
	CreatedAt     time.Time `json:"created_at"`
}
```

- [ ] **Step 3: Create backend/internal/handler/health.go**

```go
package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type HealthHandler struct {
	db *gorm.DB
}

func NewHealthHandler(db *gorm.DB) *HealthHandler {
	return &HealthHandler{db: db}
}

func (h *HealthHandler) Check(c *gin.Context) {
	sqlDB, err := h.db.DB()
	if err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"status": "error"})
		return
	}
	if err := sqlDB.Ping(); err != nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"status": "error"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
```

- [ ] **Step 4: Create backend/cmd/api/main.go**

```go
package main

import (
	"log"
	"time"

	"text-to-sql-backend/internal/config"
	"text-to-sql-backend/internal/handler"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	cfg := config.Load()

	db, err := gorm.Open(postgres.Open(cfg.DatabaseURL), &gorm.Config{})
	if err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}

	sqlDB, err := db.DB()
	if err != nil {
		log.Fatalf("failed to get underlying DB: %v", err)
	}
	sqlDB.SetMaxIdleConns(5)
	sqlDB.SetMaxOpenConns(20)
	sqlDB.SetConnMaxLifetime(time.Hour)

	healthHandler := handler.NewHealthHandler(db)

	r := gin.Default()
	r.GET("/health", healthHandler.Check)

	log.Printf("Server starting on port %s", cfg.ServerPort)
	if err := r.Run(":" + cfg.ServerPort); err != nil {
		log.Fatalf("failed to start server: %v", err)
	}
}
```

- [ ] **Step 5: Verify Go API compiles**

```bash
cd backend && go build ./cmd/api
```

Expected: compiles without errors.

- [ ] **Step 6: Commit**

```bash
git add backend/internal/ backend/cmd/
git commit -m "feat: Go API foundation with health endpoint and DB connection"
```

---

## Task 4: Python SQL Validator

**Files:**
- Create: `ai-service/app/sql/__init__.py`
- Create: `ai-service/app/sql/validator.py`
- Create: `ai-service/tests/__init__.py`
- Create: `ai-service/tests/test_validator.py`

- [ ] **Step 1: Create ai-service/app/sql/__init__.py** (empty)

- [ ] **Step 2: Create ai-service/tests/__init__.py** (empty)

- [ ] **Step 3: Create ai-service/tests/test_validator.py**

```python
import pytest
from app.sql.validator import SQLValidator


def test_allows_select():
    v = SQLValidator()
    result = v.validate("SELECT * FROM customers")
    assert result.is_valid is True


def test_allows_with():
    v = SQLValidator()
    result = v.validate("WITH cte AS (SELECT * FROM orders) SELECT * FROM cte")
    assert result.is_valid is True


def test_rejects_insert():
    v = SQLValidator()
    result = v.validate("INSERT INTO customers (name) VALUES ('test')")
    assert result.is_valid is False
    assert "INSERT" in result.error


def test_rejects_update():
    v = SQLValidator()
    result = v.validate("UPDATE customers SET name = 'test'")
    assert result.is_valid is False


def test_rejects_delete():
    v = SQLValidator()
    result = v.validate("DELETE FROM customers WHERE id = 1")
    assert result.is_valid is False


def test_rejects_drop():
    v = SQLValidator()
    result = v.validate("DROP TABLE customers")
    assert result.is_valid is False


def test_rejects_multiple_statements():
    v = SQLValidator()
    result = v.validate("SELECT 1; DROP TABLE customers")
    assert result.is_valid is False


def test_rejects_system_tables():
    v = SQLValidator()
    result = v.validate("SELECT * FROM pg_catalog.pg_tables")
    assert result.is_valid is False
```

- [ ] **Step 4: Run tests to verify they fail**

```bash
cd ai-service && python -m pytest tests/test_validator.py -v
```

Expected: FAIL (module not found).

- [ ] **Step 5: Create ai-service/app/sql/validator.py**

```python
import sqlparse
from dataclasses import dataclass

BLOCKED_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE"}
BLOCKED_TABLES = {"pg_catalog", "information_schema", "pg_tables", "pg_stat", "pg_class", "pg_roles"}
ALLOWED_STATEMENTS = {"SELECT", "WITH"}


@dataclass
class ValidationResult:
    is_valid: bool
    error: str = ""
    sql: str = ""


class SQLValidator:
    def validate(self, sql: str) -> ValidationResult:
        sql = sql.strip()
        if not sql:
            return ValidationResult(is_valid=False, error="Empty SQL")

        parsed = sqlparse.parse(sql)
        if len(parsed) > 1 and any(str(stmt).strip() for stmt in parsed[1:]):
            return ValidationResult(is_valid=False, error="Multiple statements not allowed")

        stmt = parsed[0]
        stmt_type = stmt.get_type()

        if stmt_type and stmt_type.upper() not in ALLOWED_STATEMENTS:
            return ValidationResult(
                is_valid=False,
                error=f"Statement type '{stmt_type}' not allowed. Only SELECT/WITH permitted."
            )

        sql_upper = sql.upper()
        for keyword in BLOCKED_KEYWORDS:
            if keyword in sql_upper:
                return ValidationResult(is_valid=False, error=f"Keyword '{keyword}' not allowed")

        for table in BLOCKED_TABLES:
            if table in sql_lower:
                return ValidationResult(is_valid=False, error=f"Access to '{table}' not allowed")

        return ValidationResult(is_valid=True, sql=sql)
```

- [ ] **Step 6: Fix bug in validator (sql_lower reference)**

```python
# In validator.py, the BLOCKED_TABLES check uses sql_lower but it's not defined
# Fix: change sql_lower to sql_upper since we already have sql_upper
```

Update the validator.py file:

```python
import sqlparse
from dataclasses import dataclass

BLOCKED_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE"}
BLOCKED_TABLES = {"pg_catalog", "information_schema", "pg_tables", "pg_stat", "pg_class", "pg_roles"}
ALLOWED_STATEMENTS = {"SELECT", "WITH"}


@dataclass
class ValidationResult:
    is_valid: bool
    error: str = ""
    sql: str = ""


class SQLValidator:
    def validate(self, sql: str) -> ValidationResult:
        sql = sql.strip()
        if not sql:
            return ValidationResult(is_valid=False, error="Empty SQL")

        parsed = sqlparse.parse(sql)
        if len(parsed) > 1 and any(str(stmt).strip() for stmt in parsed[1:]):
            return ValidationResult(is_valid=False, error="Multiple statements not allowed")

        stmt = parsed[0]
        stmt_type = stmt.get_type()

        if stmt_type and stmt_type.upper() not in ALLOWED_STATEMENTS:
            return ValidationResult(
                is_valid=False,
                error=f"Statement type '{stmt_type}' not allowed. Only SELECT/WITH permitted."
            )

        sql_upper = sql.upper()
        for keyword in BLOCKED_KEYWORDS:
            if keyword in sql_upper:
                return ValidationResult(is_valid=False, error=f"Keyword '{keyword}' not allowed")

        for table in BLOCKED_TABLES:
            if table in sql_upper:
                return ValidationResult(is_valid=False, error=f"Access to '{table}' not allowed")

        return ValidationResult(is_valid=True, sql=sql)
```

- [ ] **Step 7: Run tests to verify they pass**

```bash
cd ai-service && python -m pytest tests/test_validator.py -v
```

Expected: all PASS.

- [ ] **Step 8: Commit**

```bash
git add ai-service/app/sql/ ai-service/tests/
git commit -m "feat: Python SQL validator with read-only enforcement"
```

---

## Task 5: Python LLM Client

**Files:**
- Create: `ai-service/app/llm/__init__.py`
- Create: `ai-service/app/llm/client.py`

- [ ] **Step 1: Create ai-service/app/llm/__init__.py** (empty)

- [ ] **Step 2: Create ai-service/app/llm/client.py**

```python
from openai import OpenAI
from app.config import settings


def get_llm_client() -> OpenAI:
    return OpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key or "not-needed",
    )


def chat_completion(messages: list[dict], model: str = None) -> str:
    client = get_llm_client()
    response = client.chat.completions.create(
        model=model or settings.llm_model,
        messages=messages,
        temperature=0.1,
    )
    return response.choices[0].message.content
```

- [ ] **Step 3: Commit**

```bash
git add ai-service/app/llm/
git commit -m "feat: OpenAI-compatible LLM client"
```

---

## Task 6: Python Schema Introspector

**Files:**
- Create: `ai-service/app/schema/__init__.py`
- Create: `ai-service/app/schema/introspector.py`

- [ ] **Step 1: Create ai-service/app/schema/__init__.py** (empty)

- [ ] **Step 2: Create ai-service/app/schema/introspector.py**

```python
import psycopg2
from app.config import settings


def get_schema_context() -> str:
    conn = psycopg2.connect(settings.database_url)
    cur = conn.cursor()

    cur.execute("""
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """)
    rows = cur.fetchall()

    tables: dict[str, list] = {}
    for table, col, dtype, nullable in rows:
        if table not in tables:
            tables[table] = []
        tables[table].append(f"  {col} {dtype}{' NULL' if nullable == 'YES' else ' NOT NULL'}")

    cur.execute("""
        SELECT tc.table_name, kcu.column_name,
               ccu.table_name AS ref_table, ccu.column_name AS ref_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
    """)
    fks = cur.fetchall()

    cur.close()
    conn.close()

    lines = ["DATABASE SCHEMA:"]
    for table, cols in tables.items():
        lines.append(f"\nTABLE: {table}")
        lines.extend(cols)

    if fks:
        lines.append("\nRELATIONSHIPS:")
        for table, col, ref_table, ref_col in fks:
            lines.append(f"  {table}.{col} -> {ref_table}.{ref_col}")

    return "\n".join(lines)
```

- [ ] **Step 3: Commit**

```bash
git add ai-service/app/schema/
git commit -m "feat: schema introspector for database metadata"
```

---

## Task 7: Python SQL Generator

**Files:**
- Create: `ai-service/app/sql/generator.py`
- Create: `ai-service/tests/test_generator.py`

- [ ] **Step 1: Create ai-service/tests/test_generator.py**

```python
from app.sql.generator import build_sql_prompt, parse_llm_sql_response


def test_build_sql_prompt():
    schema = "TABLE: customers\n  id uuid\n  name varchar"
    question = "How many customers?"
    prompt = build_sql_prompt(question, schema)
    assert "How many customers?" in prompt
    assert "customers" in prompt


def test_parse_llm_sql_response():
    response = '{"sql": "SELECT COUNT(*) FROM customers", "reasoning": "count customers", "tables_used": ["customers"], "confidence": 0.95}'
    result = parse_llm_sql_response(response)
    assert result["sql"] == "SELECT COUNT(*) FROM customers"
    assert result["tables_used"] == ["customers"]


def test_parse_llm_sql_response_fallback():
    response = "SELECT * FROM customers"
    result = parse_llm_sql_response(response)
    assert result["sql"] == "SELECT * FROM customers"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ai-service && python -m pytest tests/test_generator.py -v
```

Expected: FAIL.

- [ ] **Step 3: Create ai-service/app/sql/generator.py**

```python
import json
from app.llm.client import chat_completion

SYSTEM_PROMPT = """You are a SQL expert. Generate PostgreSQL queries based on user questions.

Rules:
1. Only generate SELECT or WITH (CTE) queries
2. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE
3. Return valid JSON with these fields:
   - sql: the SQL query
   - reasoning: short explanation
   - tables_used: list of table names
   - confidence: 0.0 to 1.0
4. Use PostgreSQL syntax
5. Use proper JOINs based on foreign keys
6. Return results in the exact JSON format"""


def build_sql_prompt(question: str, schema: str) -> str:
    return f"""{schema}

USER QUESTION: {question}

Generate the SQL query. Return ONLY valid JSON:
{{"sql": "...", "reasoning": "...", "tables_used": [...], "confidence": 0.0}}"""


def parse_llm_sql_response(response: str) -> dict:
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"sql": response.strip(), "reasoning": "", "tables_used": [], "confidence": 0.5}


def generate_sql(question: str, schema: str) -> dict:
    user_prompt = build_sql_prompt(question, schema)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    response = chat_completion(messages)
    return parse_llm_sql_response(response)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ai-service && python -m pytest tests/test_generator.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add ai-service/app/sql/generator.py ai-service/tests/test_generator.py
git commit -m "feat: SQL generator with LLM prompt and response parsing"
```

---

## Task 8: Python API Routes

**Files:**
- Create: `ai-service/app/api/__init__.py`
- Create: `ai-service/app/api/routes.py`
- Modify: `ai-service/app/main.py`

- [ ] **Step 1: Create ai-service/app/api/__init__.py** (empty)

- [ ] **Step 2: Create ai-service/app/api/routes.py**

```python
from fastapi import APIRouter
from pydantic import BaseModel
from app.schema.introspector import get_schema_context
from app.sql.generator import generate_sql
from app.sql.validator import SQLValidator

router = APIRouter(prefix="/ai", tags=["ai"])
validator = SQLValidator()


class GenerateRequest(BaseModel):
    question: str


class GenerateResponse(BaseModel):
    sql: str
    reasoning: str
    tables_used: list[str]
    confidence: float
    is_valid: bool
    validation_error: str = ""


class ValidateRequest(BaseModel):
    sql: str


class ValidateResponse(BaseModel):
    is_valid: bool
    error: str = ""
    sql: str = ""


class SummarizeRequest(BaseModel):
    question: str
    sql: str
    result: list[dict]


class SummarizeResponse(BaseModel):
    answer: str


@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    schema = get_schema_context()
    result = generate_sql(req.question, schema)

    validation = validator.validate(result.get("sql", ""))

    return GenerateResponse(
        sql=result.get("sql", ""),
        reasoning=result.get("reasoning", ""),
        tables_used=result.get("tables_used", []),
        confidence=result.get("confidence", 0.0),
        is_valid=validation.is_valid,
        validation_error=validation.error,
    )


@router.post("/validate", response_model=ValidateResponse)
async def validate(req: ValidateRequest):
    result = validator.validate(req.sql)
    return ValidateResponse(
        is_valid=result.is_valid,
        error=result.error,
        sql=result.sql,
    )


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest):
    from app.llm.client import chat_completion

    result_str = str(req.result)
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Summarize SQL query results in natural language. Use Indonesian language. Be concise."},
        {"role": "user", "content": f"Question: {req.question}\nSQL: {req.sql}\nResult: {result_str}\n\nProvide a concise natural language answer."},
    ]
    answer = chat_completion(messages)
    return SummarizeResponse(answer=answer)


@router.post("/index")
async def index():
    return {"status": "indexing not implemented in Phase 1"}
```

- [ ] **Step 3: Update ai-service/app/main.py**

```python
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Text-to-SQL AI Service")
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Verify Python service starts**

```bash
cd ai-service && python -c "from app.main import app; print('OK')"
```

Expected: OK.

- [ ] **Step 5: Commit**

```bash
git add ai-service/app/api/ ai-service/app/main.py
git commit -m "feat: Python API routes for generate, validate, summarize"
```

---

## Task 9: Go Query Handler + Service

**Files:**
- Create: `backend/internal/handler/query.go`
- Create: `backend/internal/service/query.go`
- Modify: `backend/cmd/api/main.go`

- [ ] **Step 1: Create backend/internal/service/query.go**

```go
package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"text-to-sql-backend/internal/config"
	"text-to-sql-backend/internal/model"

	"gorm.io/gorm"
)

type QueryService struct {
	db     *gorm.DB
	cfg    *config.Config
	client *http.Client
}

func NewQueryService(db *gorm.DB, cfg *config.Config) *QueryService {
	return &QueryService{
		db:     db,
		cfg:    cfg,
		client: &http.Client{Timeout: 30 * time.Second},
	}
}

func (s *QueryService) ExecuteQuery(req model.QueryRequest) (*model.QueryResponse, error) {
	genReq, _ := json.Marshal(map[string]string{"question": req.Question})
	resp, err := s.client.Post(s.cfg.AIServiceURL+"/ai/generate", "application/json", bytes.NewReader(genReq))
	if err != nil {
		return nil, fmt.Errorf("failed to call AI service: %w", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var genResult struct {
		Sql           string   `json:"sql"`
		Reasoning     string   `json:"reasoning"`
		TablesUsed    []string `json:"tables_used"`
		Confidence    float64  `json:"confidence"`
		IsValid       bool     `json:"is_valid"`
		ValidationErr string   `json:"validation_error"`
	}
	json.Unmarshal(body, &genResult)

	if !genResult.IsValid {
		return &model.QueryResponse{
			Question:  req.Question,
			SQL:       genResult.Sql,
			Reasoning: fmt.Sprintf("Validation failed: %s", genResult.ValidationErr),
		}, fmt.Errorf("SQL validation failed: %s", genResult.ValidationErr)
	}

	start := time.Now()
	var result []map[string]interface{}
	queryErr := s.db.Raw(genResult.Sql).Scan(&result).Error
	execTime := time.Since(start).Milliseconds()

	if queryErr != nil {
		return nil, fmt.Errorf("query execution failed: %w", queryErr)
	}

	rowsReturned := len(result)

	sumReq, _ := json.Marshal(map[string]interface{}{
		"question": req.Question,
		"sql":      genResult.Sql,
		"result":   result,
	})
	sumResp, err := s.client.Post(s.cfg.AIServiceURL+"/ai/summarize", "application/json", bytes.NewReader(sumReq))
	if err != nil {
		return &model.QueryResponse{
			SQL:           genResult.Sql,
			Result:        result,
			RowsReturned:  rowsReturned,
			ExecutionTime: execTime,
		}, nil
	}
	defer sumResp.Body.Close()

	sumBody, _ := io.ReadAll(sumResp.Body)
	var sumResult struct {
		Answer string `json:"answer"`
	}
	json.Unmarshal(sumBody, &sumResult)

	return &model.QueryResponse{
		Question:      req.Question,
		SQL:           genResult.Sql,
		Reasoning:     genResult.Reasoning,
		TablesUsed:    genResult.TablesUsed,
		Result:        result,
		Answer:        sumResult.Answer,
		ExecutionTime: execTime,
		RowsReturned:  rowsReturned,
	}, nil
}
```

- [ ] **Step 2: Create backend/internal/handler/query.go**

```go
package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"text-to-sql-backend/internal/model"
	"text-to-sql-backend/internal/service"
)

type QueryHandler struct {
	svc *service.QueryService
}

func NewQueryHandler(svc *service.QueryService) *QueryHandler {
	return &QueryHandler{svc: svc}
}

func (h *QueryHandler) Query(c *gin.Context) {
	var req model.QueryRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "question is required"})
		return
	}

	result, err := h.svc.ExecuteQuery(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, result)
}
```

- [ ] **Step 3: Update backend/cmd/api/main.go to wire query handler**

Replace the entire main.go with:

```go
package main

import (
	"log"
	"time"

	"text-to-sql-backend/internal/config"
	"text-to-sql-backend/internal/handler"
	"text-to-sql-backend/internal/service"

	"github.com/gin-gonic/gin"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	cfg := config.Load()

	db, err := gorm.Open(postgres.Open(cfg.DatabaseURL), &gorm.Config{})
	if err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}

	sqlDB, err := db.DB()
	if err != nil {
		log.Fatalf("failed to get underlying DB: %v", err)
	}
	sqlDB.SetMaxIdleConns(5)
	sqlDB.SetMaxOpenConns(20)
	sqlDB.SetConnMaxLifetime(time.Hour)

	healthHandler := handler.NewHealthHandler(db)
	queryService := service.NewQueryService(db, cfg)
	queryHandler := handler.NewQueryHandler(queryService)

	r := gin.Default()
	r.GET("/health", healthHandler.Check)
	r.POST("/api/v1/query", queryHandler.Query)

	log.Printf("Server starting on port %s", cfg.ServerPort)
	if err := r.Run(":" + cfg.ServerPort); err != nil {
		log.Fatalf("failed to start server: %v", err)
	}
}
```

- [ ] **Step 4: Verify Go API compiles**

```bash
cd backend && go build ./cmd/api
```

Expected: compiles without errors.

- [ ] **Step 5: Commit**

```bash
git add backend/internal/handler/query.go backend/internal/service/query.go backend/cmd/api/main.go
git commit -m "feat: Go query handler and service for text-to-SQL flow"
```

---

## Task 10: Integration Test + End-to-End Verification

**Files:**
- Create: `backend/tests/query_test.go`

- [ ] **Step 1: Create backend/tests/query_test.go**

```go
package tests

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestHealthEndpoint(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	req, _ := http.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	if w.Code != 200 {
		t.Errorf("expected 200, got %d", w.Code)
	}

	var resp map[string]string
	json.Unmarshal(w.Body.Bytes(), &resp)
	if resp["status"] != "ok" {
		t.Errorf("expected status ok, got %s", resp["status"])
	}
}

func TestQueryEndpointValidation(t *testing.T) {
	gin.SetMode(gin.TestMode)
	r := gin.New()
	r.POST("/api/v1/query", func(c *gin.Context) {
		var req struct {
			Question string `json:"question" binding:"required"`
		}
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(400, gin.H{"error": "question is required"})
			return
		}
		c.JSON(200, gin.H{"question": req.Question})
	})

	body, _ := json.Marshal(map[string]string{})
	req, _ := http.NewRequest("POST", "/api/v1/query", bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)

	if w.Code != 400 {
		t.Errorf("expected 400, got %d", w.Code)
	}
}
```

- [ ] **Step 2: Run Go tests**

```bash
cd backend && go test ./tests/ -v
```

Expected: PASS.

- [ ] **Step 3: Verify full stack runs**

```bash
docker compose up --build -d
sleep 10
curl http://localhost:8080/health
curl http://localhost:8000/health
```

Expected: both return `{"status":"ok"}`.

- [ ] **Step 4: Test end-to-end query (requires LLM)**

```bash
curl -X POST http://localhost:8080/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How many customers are there?"}'
```

Expected: response with SQL, answer, and execution time. (Will fail if no LLM is configured — that's OK for Phase 1, the validation + execution path still works.)

- [ ] **Step 5: Commit**

```bash
git add backend/tests/
git commit -m "feat: integration tests for query and health endpoints"
```

- [ ] **Step 6: Final verification — all tests pass**

```bash
cd backend && go test ./... -v
cd ai-service && python -m pytest tests/ -v
```

Expected: all PASS.

---

## Summary

After completing all 10 tasks:

1. **Docker Compose** with postgres, go-api, ai-service
2. **Database** with e-commerce schema, seed data, readonly user
3. **Go API** with health check + query endpoint
4. **Python AI service** with SQL validation, generation, summarization
5. **End-to-end flow**: question → schema → LLM → SQL → validation → execution → answer

**Next phases (not in this plan):**
- Phase 2: Schema RAG (pgvector embeddings)
- Phase 3: Business Knowledge RAG
- Phase 4: SQL Example RAG
- Phase 5: EXPLAIN, retry loop, improved validation
- Phase 6: Query planning, clarification, conversation context
- Phase 7: Observability, evaluation, metrics
- Frontend (Next.js)
