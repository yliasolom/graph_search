.PHONY: help install dev-install test lint format type-check clean run docker-build docker-up docker-down

# Default target
help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make dev-install   - Install development dependencies"
	@echo "  make test          - Run tests with coverage"
	@echo "  make lint          - Run linting checks"
	@echo "  make format        - Format code with black and isort"
	@echo "  make type-check    - Run type checking with mypy"
	@echo "  make clean         - Clean cache and build files"
	@echo "  make run           - Run the API server"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"

# Installation
install:
	pip install -r requirements.txt

dev-install: install
	pip install -e .

# Testing
test:
	pytest -v --cov=src --cov-report=html --cov-report=term

test-unit:
	pytest -v -m unit

test-integration:
	pytest -v -m integration

# Code quality
lint:
	flake8 src/ tests/ --max-line-length=100 --exclude=__pycache__,.venv

format:
	black src/ tests/ examples/ --line-length=100
	isort src/ tests/ examples/ --profile black

type-check:
	mypy src/ --ignore-missing-imports

# Cleaning
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage dist/ build/

# Running
run:
	python -m src.api.main

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-restart:
	docker-compose restart

docker-clean:
	docker-compose down -v
	docker system prune -f

# Database
neo4j-start:
	docker-compose up -d neo4j

neo4j-stop:
	docker-compose stop neo4j

neo4j-shell:
	docker exec -it rag-neo4j cypher-shell -u neo4j -p password

# Development helpers
check: format lint type-check test

pre-commit:
	pre-commit run --all-files

requirements:
	pip freeze > requirements.txt
