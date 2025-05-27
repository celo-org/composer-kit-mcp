.PHONY: install dev test lint format clean build run help

# Default target
help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  dev        - Install in development mode"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code"
	@echo "  clean      - Clean build artifacts"
	@echo "  build      - Build the package"
	@echo "  run        - Run the MCP server"

# Install dependencies
install:
	pip install -e .

# Install in development mode with dev dependencies
dev:
	pip install -e ".[dev]"

# Run tests
test:
	pytest

# Run linting
lint:
	ruff check .
	mypy .

# Format code
format:
	black .
	ruff check --fix .

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build the package
build: clean
	python -m build

# Run the MCP server
run:
	python -m composer_kit_mcp.server

# Run with debug logging
run-debug:
	PYTHONPATH=src python -c "import logging; logging.basicConfig(level=logging.DEBUG); from composer_kit_mcp.server import main_sync; main_sync()" 
 