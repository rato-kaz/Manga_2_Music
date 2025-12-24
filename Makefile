.PHONY: help install install-dev test lint format clean api

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make install-dev   - Install dev dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make api           - Run API server"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	PYTHONPATH=. pytest tests/ -v

lint:
	PYTHONPATH=. pylint src/
	PYTHONPATH=. mypy src/

format:
	black src/ tests/
	isort src/ tests/

api:
	python scripts/run_api.py

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/ .coverage htmlcov/

