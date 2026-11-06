# Backend

FastAPI service for Suggestor. The database and login are on Supabase (Postgres + pgvector + Auth).

## Setup

1. Install Python 3.12 (CI uses 3.12).
2. Create and activate a virtual environment from the repo root:
   ```bash
   python -m venv backend/.venv
   # Windows (PowerShell): .\backend\.venv\Scripts\Activate.ps1
   # macOS / Linux:        source backend/.venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Copy `.env.example` to `.env` in the repo root and fill in your own values:
   - `SUPABASE_URL` and `SUPABASE_ANON_KEY`: Supabase dashboard, Project Settings, API.
   - `DATABASE_URL`: Supabase dashboard, Connect, **Session pooler** string. Replace the whole `[YOUR-PASSWORD]` placeholder, brackets included, with the password from the team password manager. URL-encode special characters (`@` becomes `%40`).
   - The backend does not need the `service_role` key.
   - Never commit `.env`.

## Run

From the repo root, with the virtual environment active:

```bash
python -m uvicorn backend.app.main:app --reload --env-file .env
```

- Health check: http://127.0.0.1:8000/health
- Interactive API docs: http://127.0.0.1:8000/docs

Each new terminal needs the virtual environment activated again. After editing `.env`, restart the server.

## Rules of thumb

- A direct database connection bypasses row-level security, so every query must filter by the signed-in user itself.
- Never log passwords or phone numbers.
- Schema changes are new numbered files in `backend/db/migrations/`, run in the Supabase SQL editor. Never edit one that has been applied.