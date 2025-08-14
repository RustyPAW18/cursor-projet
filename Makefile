.PHONY: doctor lint format test all
doctor:
	poetry run python run.py doctor

lint:
	poetry run ruff check src tests

format:
	poetry run black src tests

test:
	poetry run pytest -q

all: lint format test
