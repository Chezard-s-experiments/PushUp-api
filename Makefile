before-commit: lint mypy pytest

compile-messages:
	uv run pybabel compile -d ./locales/

create-db:
	uv run main.py db create

dev:
	uv run uvicorn main:app --loop uvloop --reload

drop-db:
	uv run main.py db drop

install:
	uv sync

init-db: drop-db create-db migrate

init-test-db:
	$(MAKE) DB__NAME=pushup_api_test init-db

lint:
	uv run ruff format
	uv run ruff check --fix

makemigrations:
	uv run alembic revision --autogenerate

migrate:
	uv run alembic upgrade head

mypy:
	uv run mypy ./

pytest:
	uv run pytest

pytest-accept-diff:
	uv run pytest --accept-diff

pytest-pycharm:
	uv run pytest --ide pycharm

update:
	uv lock --upgrade
	uv sync

