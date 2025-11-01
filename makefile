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