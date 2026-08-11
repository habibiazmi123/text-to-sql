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
