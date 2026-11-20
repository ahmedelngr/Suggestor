# Backend

FastAPI service for Suggestor. The database and login are on Supabase (Postgres + pgvector + Auth).

The API contract (every endpoint, status code and field) is in [API.md](API.md).

## Run it locally

You need Python 3.12 (CI uses 3.12) and the database password from the team password manager.

1. From the repo root, create and activate a virtual environment:
   ```bash
   python -m venv backend/.venv
   # Windows (PowerShell): .\backend\.venv\Scripts\Activate.ps1
   # macOS / Linux:        source backend/.venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Copy `.env.example` to `.env` in the repo root and fill in your own values:
   - `SUPABASE_URL` and `SUPABASE_ANON_KEY`: Supabase dashboard, Project Settings, API.
   - `DATABASE_URL`: Supabase dashboard, Connect, **Session pooler** string. Replace the whole `[YOUR-PASSWORD]` placeholder, brackets included, with the password. URL-encode special characters (`@` becomes `%40`).
   - The backend does not need the `service_role` key. Never commit `.env`.
4. Start the API:
   ```bash
   python -m uvicorn backend.app.main:app --reload --env-file .env
   ```

- Health check: http://127.0.0.1:8000/health
- Interactive API docs: http://127.0.0.1:8000/docs

Each new terminal needs the virtual environment activated again. After editing `.env`, restart the server.

## Run it on a free host (Render)

This gives the frontend a public URL without anyone running the API on a laptop. It is free, with one catch: the service **sleeps after 15 minutes without requests, and waking it takes about a minute**. Open `/health` a minute before a demo.

1. Create a free account at https://render.com.
2. **New > Web Service > Public Git Repository**, paste `https://github.com/ahmedelngr/Suggestor`, and click **Connect**.
3. Use these settings:

   | Setting | Value |
   |---|---|
   | Language | Python 3 |
   | Branch | `main` |
   | Build Command | `pip install -r backend/requirements.txt` |
   | Start Command | `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` |
   | Instance Type | Free |
   | Health Check Path (Advanced) | `/health` |

4. Under **Advanced > Environment Variables**, add `DATABASE_URL`, `SUPABASE_URL` and `SUPABASE_ANON_KEY` with the same values as your `.env`. Add `CORS_ORIGINS` only if a web build needs another address. Secrets go here, never in git.
5. Create the service. The first deploy takes a few minutes. Then open `<your-url>/health` (expect `{"status":"ok"}`) and `<your-url>/docs`.

Notes:
- The Python version comes from `.python-version` (3.12). Render's newest default may not be supported by our dependencies yet.
- A service made from a public repo URL does not redeploy by itself. After new code reaches `main`, click **Manual Deploy** in the Render dashboard.
- Frontend: set the app's API address to the Render URL.

## Settings

All optional. They are listed in `.env.example`.

| Variable | Default | What it does |
|---|---|---|
| `CORS_ORIGINS` | `http://localhost:8081,http://localhost:19006` | Web addresses allowed to call the API from a browser |
| `COOLDOWN_DAYS` | `14` | Days a swiped restaurant stays out of the feed |
| `LIKE_WEIGHT` | `1.0` | How much a like adds to the taste vector |
| `DISLIKE_WEIGHT` | `0.5` | How much a pass subtracts |

## Tests

```bash
python -m pytest backend
```

Most tests need no database. The ones that run real SQL are skipped unless `TEST_DATABASE_URL` points to a **local** scratch Postgres with pgvector (the tests refuse any other address). Never point it at Supabase. To make one with Docker:

```bash
docker run --name suggestor-scratch -e POSTGRES_PASSWORD=scratch -p 5433:5432 -d pgvector/pgvector:pg16
```

Wait a few seconds, then load the first two migrations (003 needs Supabase's auth schema) and add the `auth_id` column that 003 would add:

```bash
# macOS / Linux
docker exec -i suggestor-scratch psql -U postgres -v ON_ERROR_STOP=1 < backend/db/migrations/001_init.sql
docker exec -i suggestor-scratch psql -U postgres -v ON_ERROR_STOP=1 < backend/db/migrations/002_accounts_and_onboarding.sql
docker exec suggestor-scratch psql -U postgres -c "ALTER TABLE users ADD COLUMN auth_id uuid UNIQUE;"
```

```powershell
# Windows (PowerShell)
Get-Content backend\db\migrations\001_init.sql | docker exec -i suggestor-scratch psql -U postgres -v ON_ERROR_STOP=1
Get-Content backend\db\migrations\002_accounts_and_onboarding.sql | docker exec -i suggestor-scratch psql -U postgres -v ON_ERROR_STOP=1
docker exec suggestor-scratch psql -U postgres -c "ALTER TABLE users ADD COLUMN auth_id uuid UNIQUE;"
```

Next time, `docker start suggestor-scratch` brings it back.

Then, in the same terminal:

```bash
# Windows (PowerShell):  $env:TEST_DATABASE_URL = "postgresql://postgres:scratch@localhost:5433/postgres?connect_timeout=3"
# macOS / Linux:         export TEST_DATABASE_URL="postgresql://postgres:scratch@localhost:5433/postgres?connect_timeout=3"
python -m pytest backend
```

`connect_timeout=3` makes a stopped database fail in seconds instead of hanging.

## Rules of thumb

- A direct database connection bypasses row-level security, so every query must filter by the signed-in user itself.
- Never log passwords or phone numbers.
- Schema changes are new numbered files in `backend/db/migrations/`, run in the Supabase SQL editor. Never edit one that has been applied.
