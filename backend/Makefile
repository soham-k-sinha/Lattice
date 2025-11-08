.PHONY: install run dev test lint format clean db-init db-migrate db-upgrade db-seed db-reset help

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies using Poetry"
	@echo "  make run         - Run the FastAPI server"
	@echo "  make dev         - Run server in development mode with hot reload"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linters (ruff, mypy)"
	@echo "  make format      - Format code with black"
	@echo "  make clean       - Clean up cache files"
	@echo "  make db-init     - Initialize database (create tables)"
	@echo "  make db-migrate  - Create a new migration"
	@echo "  make db-upgrade  - Apply migrations"
	@echo "  make db-seed     - Seed database with demo data"
	@echo "  make db-reset    - Reset database (WARNING: deletes all data)"

install:
	poetry install

install-pip:
	pip install -r requirements.txt

run:
	poetry run python run.py

dev:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	poetry run pytest

lint:
	poetry run ruff check app/
	poetry run mypy app/

format:
	poetry run black app/
	poetry run ruff check --fix app/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Database commands
db-init:
	poetry run python scripts/init_db.py

db-migrate:
	poetry run alembic revision --autogenerate -m "$(msg)"

db-upgrade:
	poetry run alembic upgrade head

db-seed:
	poetry run python scripts/seed_data.py

db-reset:
	@echo "WARNING: This will delete all data. Press Ctrl+C to cancel."
	@sleep 3
	poetry run alembic downgrade base
	poetry run alembic upgrade head
	poetry run python scripts/seed_data.py

