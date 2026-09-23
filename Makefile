.PHONY: install analyze backend frontend

install:
	python3 -m pip install -r backend/requirements.txt
	cd frontend && npm install

analyze:
	python3 backend/pipeline.py

backend:
	uvicorn backend.app.main:app --reload

frontend:
	cd frontend && npm run dev
