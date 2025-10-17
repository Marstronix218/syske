
# Syske

A full-stack application for visualizing and managing habits, tasks, and systems.

## Structure
- **backend/**: FastAPI + SQLAlchemy + Alembic (Python)
- **frontend/**: React + Vite + Zustand (TypeScript)

## Setup

### 1. Python Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # if needed
python -m app.seed    # (optional) load initial data
uvicorn app.main:app --reload --port 8001
```

- SQLite DB is created at `backend/data.db`
- API docs: [http://localhost:8001/docs](http://localhost:8001/docs)

### 2. Node.js Frontend

```bash
cd frontend
npm install
npm run dev
```

- Access: [http://localhost:5173](http://localhost:5173)
- Backend API is proxied via `/api` (see `vite.config.ts`)

## Common Issues
- Port conflicts: Backend runs on 8001, frontend on 5173
- Empty DB: Run `python -m app.seed` in the backend directory
- .env setup: Copy `.env.example` to `.env` if needed

## Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm run lint
npm run build
```

## Directory Structure

```
backend/
  app/
    main.py
    ...
  requirements.txt
  alembic.ini
frontend/
  src/
    App.tsx
    ...
  package.json
  vite.config.ts
```

## License
MIT
