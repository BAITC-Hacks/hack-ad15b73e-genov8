PYTHON ?= python3
VENV ?= .venv
ifeq ($(OS),Windows_NT)
PYTHON := python
VENV_PYTHON := $(VENV)/Scripts/python.exe
NPM := npm.cmd
else
VENV_PYTHON := $(VENV)/bin/python
NPM := npm
endif
RUN_PYTHON := $(if $(wildcard $(VENV_PYTHON)),$(VENV_PYTHON),$(PYTHON))

.PHONY: install install-backend install-frontend analyze backend frontend

install: install-backend install-frontend

install-backend:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install -r backend/requirements.txt

install-frontend:
	cd frontend && $(NPM) install

analyze:
	$(RUN_PYTHON) backend/pipeline.py

backend:
	$(RUN_PYTHON) -m uvicorn backend.app.main:app --reload

frontend:
	cd frontend && $(NPM) run dev
