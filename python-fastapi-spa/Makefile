PYTHON ?= python3

# Check for python3 first, if not available, use python
# This allows for compatibility across different systems
ifeq ($(shell which $(PYTHON) 2>/dev/null),)
    PYTHON := python
    ifeq ($(shell which $(PYTHON) 2>/dev/null),)
        $(error "No python or python3 interpreter found. Please install one.")
    endif
endif

VENV_DIR = .venv

.PHONY: venv-init venv-install-requirements run-dev clear test

## venv-init: Create a virtual environment
venv-init:
	@echo "🐍 Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)

## venv-install-requirements: Install dependencies from requirements.txt
venv-install-requirements:
	@echo "📦 Installing dependencies..."
	$(VENV_DIR)/bin/$(PYTHON) -m pip install -r requirements.txt

## run-dev: Source the venv and run uvicorn with cache disabled
run-dev:
	@echo "🚀 Starting development server on port 8000..."
	@echo "Disabling Python cache..."
	@PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 $(VENV_DIR)/bin/$(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	@PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. $(VENV_DIR)/bin/$(PYTHON) -m pytest

## clear: Remove the virtual environment and Python cache
clear:
	@echo "🧹 Cleaning up..."
	@rm -rf $(VENV_DIR) __pycache__
	@find . -type d -name "__pycache__" -exec rm -rf {} +
