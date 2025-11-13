# Person Detection and Counting System Makefile

.PHONY: help install install-dev test test-unit test-integration test-e2e lint format type-check clean build docs run demo setup

# Default target
help:
	@echo "Person Detection and Counting System"
	@echo "===================================="
	@echo ""
	@echo "Available commands:"
	@echo "  install       Install production dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo "  setup         Setup the project (install + download models)"
	@echo "  test          Run all tests"
	@echo "  test-unit     Run unit tests"
	@echo "  test-integration Run integration tests"
	@echo "  test-e2e      Run end-to-end tests"
	@echo "  lint          Run linting (flake8)"
	@echo "  format        Format code (black + isort)"
	@echo "  type-check    Run type checking (mypy)"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build package"
	@echo "  docs          Generate documentation"
	@echo "  run           Run main application"
	@echo "  demo          Run demo application"
	@echo "  security      Run security checks"
	@echo ""

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

setup:
	python scripts/setup.py

# Testing
test:
	pytest

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v

test-coverage:
	pytest --cov=src --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	black src tests
	isort src tests

format-check:
	black --check src tests
	isort --check-only src tests

type-check:
	mypy src

# Security
security:
	bandit -r src/
	safety check

# Build and package
build:
	python -m build

build-check:
	twine check dist/*

# Documentation
docs:
	cd docs && make html

docs-serve:
	cd docs/_build/html && python -m http.server 8000

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

# Development workflow
dev-setup: install-dev setup
	@echo "Development environment setup complete!"

dev-test: format-check lint type-check test
	@echo "All development checks passed!"

# CI/CD simulation
ci-test: install-dev
	pytest tests/unit/ tests/integration/ -v --cov=src --cov-report=xml
	flake8 src tests --count --exit-zero --max-complexity=15 --max-line-length=127 --statistics --ignore=E203,E402,F403,F405
	black --check src tests
	isort --check-only src tests
	mypy src --ignore-missing-imports --python-version=3.10
	bandit -r src/ || true
	safety check || true

# Data management
download-models:
	python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

create-dirs:
	mkdir -p data/raw data/processed
	mkdir -p models/pretrained models/trained
	mkdir -p output/reports

# Quick start
quick-start: install setup
	@echo "Quick start complete! Run 'make run' to start the application."

# Full development setup
full-setup: create-dirs install-dev setup
	@echo "Full development setup complete!"
