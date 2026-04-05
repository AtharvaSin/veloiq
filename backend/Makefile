.PHONY: demo-reset test test-no-cov dev migrate migration lint format install clean

demo-reset:
	python -m data_seeder.seed_all

test:
	pytest -v --cov=app --cov-report=term-missing

test-no-cov:
	pytest -v --no-cov

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(m)"

lint:
	ruff check app tests data_seeder
	mypy app

format:
	black app tests data_seeder
	ruff check --fix app tests data_seeder

install:
	pip install -r requirements-dev.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
