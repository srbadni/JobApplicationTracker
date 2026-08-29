# job-tracker

`job-tracker` is the working name for a growing recruitment and hiring management platform. The repository currently contains an asynchronous FastAPI backend and a developer/operator CLI.

## Features

- FastAPI and SQLAlchemy 2.0 with PostgreSQL
- Pydantic v2 validation
- Session authentication, OAuth, CSRF protection, and API keys
- Tier-based rate limiting
- SQLAdmin administration panel
- Taskiq background workers
- Redis or Memcached caching
- Docker deployment generation through the `job-tracker` CLI

## Repository layout

```text
job-tracker/
├── backend/  # deployable FastAPI application
├── cli/      # developer/operator CLI
└── docs/     # project documentation
```

## Quick start

```bash
uv sync --all-packages --all-extras
cp backend/.env.example backend/.env
uv run job-tracker deploy generate local
uv run job-tracker env gen-secret
uv run job-tracker env validate
docker compose up --build
```

The API is then available at <http://127.0.0.1:8000>, with Swagger UI at `/docs`.

Without Docker, provide PostgreSQL and Redis, then run:

```bash
cd backend
uv run alembic upgrade head
uv run python -m scripts.setup_initial_data
uv run fastapi dev src/interface_adapters/main.py
```

Alembic is the only schema-management mechanism. The initial-data command is
idempotent and inserts seed data only, so always apply migrations before running
it.

Run a Taskiq worker in a second terminal:

```bash
cd backend
uv run taskiq worker infrastructure.taskiq.worker:default_broker
```

## Common commands

```bash
uv run job-tracker deploy generate prod --workers 8
uv run job-tracker env validate
```

## Database rename note

The default PostgreSQL database is now `job-tracker`. Existing installations are **not renamed automatically**. See the migration notes in the response accompanying this change before switching an environment that already has data.

## License

[MIT](LICENSE.md)
