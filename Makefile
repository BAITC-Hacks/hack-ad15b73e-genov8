PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
RUN_PYTHON := $(if $(wildcard $(VENV_PYTHON)),$(VENV_PYTHON),$(PYTHON))

.PHONY: install install-backend install-frontend analyze backend frontend

install: install-backend install-frontend

install-backend:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install -r backend/requirements.txt

install-frontend:
	cd frontend && npm install

analyze:
	$(RUN_PYTHON) backend/pipeline.py

backend:
	$(RUN_PYTHON) -m uvicorn backend.app.main:app --reload

frontend:
	cd frontend && npm run dev
