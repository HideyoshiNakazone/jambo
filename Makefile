### VARIABLES ###
UV_SYNC_ARGS ?= --all-extras


### TASKS ###

validate_env:
	@echo "→ Validating environment: checking for 'uv'"
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "❌ 'uv' is not installed. Please install it from https://github.com/astral-sh/uv"; \
		exit 1; \
	 else \
		echo "✅ 'uv' is installed."; \
	fi

install: validate_env
	@echo "→ Installing dependencies with uv"
	@uv sync $(UV_SYNC_ARGS)

setup: validate_env install
	@echo "→ Setting up the development environment"
	@pre-commit install --config .githooks/pre-commit-config.yaml
	@pre-commit autoupdate --config .githooks/pre-commit-config.yaml

lint: validate_env
	@echo "→ Linting with ruff"
	@ruff check . --fix && ruff format .

test: validate_env
	@echo "→ Running tests with pytest"
	@python -m coverage run -m unittest discover -v

build: validate_env
	@echo "→ Building the package"
	@uv build --sdist

clean:
	@echo "→ Cleaning Python build/test artifacts"
	@rm -rf **/__pycache__/ dist .coverage

.PHONY: validate_env install update lock lint format check-format test clean
