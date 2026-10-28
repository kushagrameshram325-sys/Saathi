# SAATHI Backend

FastAPI REST backend for the SAATHI safety support platform.

## Module layout

```
backend/
└── app/
    ├── __init__.py
    ├── main.py          ← FastAPI app, CORS, lifespan (table creation + seed)
    ├── api/
    │   └── routes.py    ← REST endpoints
    ├── core/
    │   └── config.py    ← Pydantic-settings (DATABASE_URL, CORS, etc.)
    ├── db/
    │   └── session.py   ← SQLAlchemy engine, SessionLocal, Base, get_db()
    ├── models/
    │   └── entities.py  ← SupportService, HazardReport, SupportRequest ORM models
    ├── schemas/
    │   └── api.py       ← Pydantic request/response schemas
    └── services/
        └── seed.py      ← Demo service-directory seed data (not verified)
```

## Start the server

From the project root with the virtual environment active:

```powershell
uvicorn app.main:app --app-dir backend --reload --port 8000
```

- API health: http://127.0.0.1:8000/api/v1/health
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc:       http://127.0.0.1:8000/redoc

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/services` | List services; `q` and `category` query params |
| GET | `/api/v1/services/{id}` | Get one service |
| POST | `/api/v1/hazards` | Create a hazard report |
| GET | `/api/v1/hazards` | List hazard reports; `status` and `limit` query params |
| POST | `/api/v1/support-requests` | Save a private support preference |

## Privacy contracts enforced by the API

1. **Hazard coordinates** (`latitude`, `longitude`) are stored but never returned in any response.
2. **Support-request `message`** is stored but not echoed back in any response.
3. **No public GET endpoint for support requests** — reference codes cannot be guessed to retrieve submissions.
4. **`consent: true`** is required on every support-request submission; the request is rejected with HTTP 422 otherwise.

## Configuration

Copy `.env.example` to `.env` to override defaults:

```ini
DATABASE_URL=sqlite:///./saathi.db
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```
