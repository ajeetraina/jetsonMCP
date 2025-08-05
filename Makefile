# JetsonMCP Makefile
# Provides common development and deployment tasks

.PHONY: help install install-dev test test-coverage lint format clean run docker-build docker-run

# Default target
help:
	@echo "JetsonMCP Development Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install      Install JetsonMCP for production"
	@echo "  install-dev  Install JetsonMCP with development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test         Run all tests"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  lint         Run code linting (flake8, mypy)"
	@echo "  format       Format code with black and isort"
	@echo "  clean        Clean up build artifacts"
	@echo ""
	@echo "Running:"
	@echo "  run          Start JetsonMCP server"
	@echo "  test-conn    Test connection to Jetson Nano"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run JetsonMCP in Docker container"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,test]"
	pre-commit install

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=jetsonmcp --cov-report=html --cov-report=term

test-integration:
	pytest tests/ -v -m integration

test-unit:
	pytest tests/ -v -m "not integration"

# Code quality
lint:
	flake8 jetsonmcp/
	mypy jetsonmcp/
	vulture jetsonmcp/ --exclude=__pycache__ --min-confidence=80

format:
	black jetsonmcp/ tests/
	isort jetsonmcp/ tests/

format-check:
	black --check jetsonmcp/ tests/
	isort --check-only jetsonmcp/ tests/

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Running
run:
	python -m jetsonmcp.server

test-conn:
	jetsonmcp test-connection

validate-config:
	jetsonmcp validate-config

# Docker
docker-build:
	docker build -t jetsonmcp:latest .

docker-run:
	docker run -it --rm \
		-v $(PWD)/.env:/app/.env \
		-p 8080:8080 \
		jetsonmcp:latest

# Development server with auto-reload
dev:
	watchfiles 'python -m jetsonmcp.server' jetsonmcp/

# Security scan
security-scan:
	bandit -r jetsonmcp/
	safety check

# Documentation
docs:
	mkdocs serve

docs-build:
	mkdocs build

# Release preparation
release-test:
	python -m build
	twine check dist/*

release:
	python -m build
	twine upload dist/*

# CI/CD helpers
ci-install:
	pip install -e ".[dev,test]"

ci-test:
	pytest tests/ -v --cov=jetsonmcp --cov-report=xml --cov-report=term

ci-lint:
	flake8 jetsonmcp/ --format=github
	mypy jetsonmcp/

ci-security:
	bandit -r jetsonmcp/ -f json -o bandit-report.json
	safety check --json > safety-report.json
