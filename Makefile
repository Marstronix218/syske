PYTHON=python3
BACKEND_DIR=backend
FRONTEND_DIR=frontend

.PHONY: install-backend install-frontend dev backend frontend seed test

install-backend:
	@cd $(BACKEND_DIR) && pip install -r requirements.txt

install-frontend:
	@cd $(FRONTEND_DIR) && npm install

backend:
	@cd $(BACKEND_DIR) && uvicorn app.main:app --reload

frontend:
	@cd $(FRONTEND_DIR) && npm run dev

dev:
	@echo "Starting backend and frontend..."
	@cd $(BACKEND_DIR) && uvicorn app.main:app --reload &
	@sleep 2
	@cd $(FRONTEND_DIR) && npm run dev

seed:
	@cd $(BACKEND_DIR) && $(PYTHON) -m app.seed

test:
	@cd $(BACKEND_DIR) && pytest
