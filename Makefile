.DEFAULT_GOAL := help
VENV := .venv
PY := $(VENV)/bin/python

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk -F':.*?## ' '{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

$(PY):
	python3.12 -m venv $(VENV)

.PHONY: install
install: $(PY) ## Create the virtualenv and install runtime + dev dependencies
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -e ".[dev]"
	$(VENV)/bin/pre-commit install

.PHONY: run
run: ## Start the development server on http://127.0.0.1:5000
	$(PY) app.py

.PHONY: lint
lint: ## Check formatting and lint rules
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .

.PHONY: format
format: ## Apply formatting and auto-fixable lint rules
	$(VENV)/bin/ruff check --fix .
	$(VENV)/bin/ruff format .

.PHONY: typecheck
typecheck: ## Run static type analysis
	$(VENV)/bin/mypy .

.PHONY: test
test: ## Run the test suite with coverage
	$(VENV)/bin/pytest --cov=. --cov-report=term-missing

.PHONY: check
check: lint typecheck test ## Everything CI runs

.PHONY: docker
docker: ## Build the production container image
	docker build -t rent-roll-tool:local .

.PHONY: clean
clean: ## Remove caches and build artefacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov build dist *.egg-info
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
