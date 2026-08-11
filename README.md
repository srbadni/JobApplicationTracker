# Job Application Tracker API

A small FastAPI service that provides the current foundation for the Job Application
Tracker. The codebase deliberately does not implement domain behavior that has not yet
been specified.

## Architecture

The project uses a lightweight feature-first layout suited to its current size:

- `api/` composes versioned HTTP routers and owns cross-feature endpoints such as health.
- `features/` keeps each business capability and its HTTP/schema code together.
- `core/` contains application configuration.
- `db/` owns SQLAlchemy engine, session lifecycle, and FastAPI database dependency setup.
- `common/` contains genuinely shared API contracts.
- `main.py` is the composition root and ASGI entry point.

This avoids premature repository/service abstractions while leaving clear boundaries for
introducing them when real company or application use cases require them.
The detailed engineering assessment and intentionally deferred decisions are recorded in
[`docs/architecture.md`](docs/architecture.md).

## Requirements

- Python 3.12+
- PostgreSQL (only required once a database-backed endpoint is used)

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

On Windows, activate the virtual environment with:

```powershell
.venv\Scripts\activate
```

Configuration is read from environment variables and, for local development, `.env`.
The tracked `.env.example` documents safe development defaults; production credentials
must be supplied through the deployment environment and must not be committed.

| Variable | Purpose | Default |
| --- | --- | --- |
| `APP_NAME` | OpenAPI/service name | `JobTracker API` |
| `APP_VERSION` | Reported API version | `1.0.0` |
| `API_V1_PREFIX` | Versioned API base path | `/api/v1` |
| `DATABASE_URL` | SQLAlchemy async PostgreSQL URL | local development database |
| `DEBUG` | FastAPI and SQLAlchemy diagnostic output | `false` |

## Run

```bash
uvicorn main:app --reload
```

At application startup, SQLAlchemy connects using `DATABASE_URL` and creates any
missing tables registered by the models (currently `companies`) in that PostgreSQL
database. The database itself and the configured PostgreSQL user must already exist,
and that user must have permission to create tables. `create_all()` only creates
missing tables; use a migration tool such as Alembic for future schema changes.

The liveness endpoint is available at `GET /api/v1/health`. It intentionally does not
query PostgreSQL: liveness should continue to report whether the process can serve HTTP,
independently of downstream readiness checks that may be added when database-backed
business behavior exists.

## Quality checks

Tests remain next to their related modules so ownership follows the feature layout.

```bash
pytest
ruff check .
```
