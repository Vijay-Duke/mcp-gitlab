.PHONY: help install install-dev test test-cov lint format clean build docker-build docker-run

# Variables
PYTHON := python3
UV := uv
PROJECT_NAME := mcp-gitlab
DOCKER_IMAGE := $(PROJECT_NAME):latest
SRC_DIR := src/mcp_gitlab
TEST_DIR := tests

# Colors for terminal output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo '$(GREEN)Available targets:$(NC)'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install the package and dependencies
	$(UV) pip install -e .

install-dev: ## Install development dependencies
	$(UV) pip install -e .[dev,test]
	pre-commit install

test: ## Run tests
	pytest $(TEST_DIR) -v

test-cov: ## Run tests with coverage
	pytest $(TEST_DIR) -v --cov=$(SRC_DIR) --cov-report=html --cov-report=term

test-integration: ## Run integration tests
	pytest $(TEST_DIR)/test_integration.py -v -m integration

lint: ## Run linters
	@echo "$(GREEN)Running Ruff...$(NC)"
	ruff check $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)Running Black check...$(NC)"
	black --check $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)Running isort check...$(NC)"
	isort --check-only $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)Running MyPy...$(NC)"
	mypy $(SRC_DIR) --ignore-missing-imports

format: ## Format code
	@echo "$(GREEN)Running Black...$(NC)"
	black $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)Running isort...$(NC)"
	isort $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)Running Ruff fix...$(NC)"
	ruff check --fix $(SRC_DIR) $(TEST_DIR)

security: ## Run security checks
	@echo "$(GREEN)Running Bandit...$(NC)"
	bandit -r $(SRC_DIR)
	@echo "$(GREEN)Running Safety...$(NC)"
	safety check
	@echo "$(GREEN)Running pip-audit...$(NC)"
	pip-audit

clean: ## Clean build artifacts
	rm -rf build dist *.egg-info
	rm -rf .coverage htmlcov .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean ## Build distribution packages
	$(PYTHON) -m build

docker-build: ## Build Docker image
	docker build -t $(DOCKER_IMAGE) .

docker-run: ## Run Docker container
	docker run --rm -it \
		-e GITLAB_PRIVATE_TOKEN=$${GITLAB_PRIVATE_TOKEN} \
		-e GITLAB_URL=$${GITLAB_URL:-https://gitlab.com} \
		$(DOCKER_IMAGE)

docker-push: ## Push Docker image to registry
	docker tag $(DOCKER_IMAGE) ghcr.io/vijay-duke/$(PROJECT_NAME):latest
	docker push ghcr.io/vijay-duke/$(PROJECT_NAME):latest

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

update-deps: ## Update dependencies
	$(UV) pip install --upgrade pip setuptools wheel
	$(UV) lock --upgrade

ci-local: ## Run CI checks locally
	@echo "$(GREEN)Running local CI checks...$(NC)"
	@$(MAKE) lint
	@$(MAKE) test-cov
	@$(MAKE) security
	@echo "$(GREEN)All checks passed!$(NC)"

docs: ## Generate documentation
	@echo "$(YELLOW)Documentation generation not yet configured$(NC)"

version: ## Show current version
	@grep "^version" pyproject.toml | cut -d'"' -f2

.DEFAULT_GOAL := help