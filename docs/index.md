# job-tracker

`job-tracker` is the working name for this recruitment and hiring management platform.

The current codebase provides a modular FastAPI foundation with:

- asynchronous SQLAlchemy and PostgreSQL persistence;
- session authentication, OAuth, CSRF protection, and API keys;
- tier-based rate limiting;
- SQLAdmin administration;
- Taskiq background workers;
- Redis or Memcached caching; and
- a `job-tracker` developer CLI for deployment generation and environment checks.

## Start here

- [Installation](getting-started/installation.md)
- [Configuration](getting-started/configuration.md)
- [First run](getting-started/first-run.md)
- [Project structure](user-guide/project-structure.md)
- [Database migrations](user-guide/database/migrations.md)
- [CLI](cli/index.md)

## Quick start

```bash
uv sync --all-packages --all-extras
cp backend/.env.example backend/.env
uv run job-tracker deploy generate local
uv run job-tracker env gen-secret
docker compose up --build
```

The API is served at `http://127.0.0.1:8000`; interactive API documentation is available at `/docs`.
