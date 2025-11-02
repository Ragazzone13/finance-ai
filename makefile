# Project variables
APP=finance_ai.app:app
HOST=127.0.0.1
PORT=8000
UVICORN=poetry run uvicorn

# Default target
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make install        Install dependencies via Poetry"
	@echo "  make run            Start the dev server with reload"
	@echo "  make run0           Start the server binding to 0.0.0.0 (for containers)"
	@echo "  make fmt            Format with black + isort"
	@echo "  make lint           Lint with ruff"
	@echo "  make test           Run pytest"
	@echo "  make shell          Open a Poetry shell"
	@echo "  make lock           Update lockfile (poetry lock)"
	@echo "  make export-reqs    Export requirements.txt from Poetry lock"
	@echo "  make clean          Remove pyc/__pycache__ and local db"
	@echo "  make db             Initialize DB tables (by starting app once)"
	@echo "  make deps           Print dependency tree"

.PHONY: install
install:
	poetry install

.PHONY: run
run:
	$(UVICORN) $(APP) --reload --host $(HOST) --port $(PORT)

.PHONY: run0
run0:
	$(UVICORN) $(APP) --reload --host 0.0.0.0 --port $(PORT)

.PHONY: fmt
fmt:
	poetry run isort .
	poetry run black .

.PHONY: lint
lint:
	poetry run ruff check .

.PHONY: test
test:
	poetry run pytest -q

.PHONY: shell
shell:
	poetry shell

.PHONY: lock
lock:
	poetry lock

.PHONY: export-reqs
export-reqs:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

.PHONY: clean
clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -f finance.db
	rm -rf .pytest_cache

.PHONY: db
db:
	# For SQLite with auto-create tables, starting the app once will init
	$(UVICORN) $(APP) --host 127.0.0.1 --port 9999 & \
	PID=$$!; sleep 2; kill $$PID

.PHONY: deps
deps:
	poetry show --tree


dev:
	poetry run uvicorn finance_ai.app:app --reload --host 0.0.0.0 --port 8000

shell:
	poetry run python

alembic-rev:
	@if [ -z "$(m)" ]; then echo "Missing message. Usage: make alembic-rev m=\"your message\""; exit 1; fi
	poetry run alembic revision --autogenerate -m "$(m)"

# Apply latest migrations to head
alembic-up:
	poetry run alembic upgrade head

# Downgrade one revision
alembic-down-1:
	poetry run alembic downgrade -1

# Show current revision
alembic-current:
	poetry run alembic current

# Show migration history
alembic-history:
	poetry run alembic history

# Stamp the database to head without running migrations (use with caution)
alembic-stamp-head:
	poetry run alembic stamp head

# Recreate local SQLite database and re-apply migrations from scratch
# Adjust DB_FILE if your SQLite file is elsewhere, or replace with a drop/create for Postgres.
DB_FILE := app.db

db-reset:
	@if [ -f "$(DB_FILE)" ]; then rm -f "$(DB_FILE)"; echo "Removed $(DB_FILE)"; fi
	poetry run alembic upgrade head
	@echo "Database reset and migrated to head."

# Quick integrity check via your health endpoint (requires server running in another terminal)
health-db:
	@curl -sS http://127.0.0.1:8000/health/db | jq .