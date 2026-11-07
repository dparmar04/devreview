PY ?= python

.PHONY: setup lint test security guard verify

setup:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -e ".[dev]"
	pre-commit install

lint:
	ruff check .
	ruff format --check .

test:
	$(PY) -m pytest

security:
	bandit -r src -q
	pip-audit

guard:
	$(PY) scripts/guard.py

verify: lint test security guard
	@echo "ALL CHECKS PASSED"
