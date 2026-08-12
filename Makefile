.PHONY: dev infra run-api run-ai test lint seed rag-index migrate setup evaluate

# --- Setup ---

setup:
	cd ai-service && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# --- Infrastructure (Docker) ---

infra:
	docker compose up -d

infra-down:
	docker compose down

infra-fresh:
	docker compose down -v
	docker compose up -d

# --- Apps (run locally) ---

run-api:
	cd backend && go run ./cmd/api

run-ai:
	cd ai-service && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# --- Database (via Docker psql) ---

migrate:
	docker compose exec postgres psql -U app_user -d text_to_sql -f /docker-entrypoint-initdb.d/001_create_extensions.sql
	docker compose exec postgres psql -U app_user -d text_to_sql -f /docker-entrypoint-initdb.d/002_create_tables.sql
	docker compose exec postgres psql -U app_user -d text_to_sql -f /docker-entrypoint-initdb.d/003_create_rag_tables.sql
	docker compose exec postgres psql -U app_user -d text_to_sql -f /docker-entrypoint-initdb.d/004_create_readonly_user.sql
	docker compose exec postgres psql -U app_user -d text_to_sql -f /docker-entrypoint-initdb.d/005_create_schema_embeddings.sql

seed:
	docker compose exec postgres psql -U app_user -d text_to_sql -f /docker-entrypoint-initdb.d/seeds/seed.sql

rag-index:
	curl -X POST http://localhost:8000/ai/index

evaluate:
	cd ai-service && .venv/bin/python eval/evaluate.py

# --- Test / Lint ---

test:
	cd backend && go test ./...
	cd ai-service && .venv/bin/python -m pytest tests/

lint:
	cd backend && go vet ./...
	cd ai-service && .venv/bin/ruff check
