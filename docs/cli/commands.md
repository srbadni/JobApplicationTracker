# Commands

Complete reference for the in-tree `job-tracker` commands. Plugin commands have their own help text — see [Plugins](plugins.md).

## `job-tracker deploy`

Generate deployment artifacts. Today's only sub-command is `generate`.

### `job-tracker deploy generate <mode>`

Render `docker-compose.yml` (and `nginx/default.conf` for `nginx` mode) for the chosen deployment shape.

```text
Usage: job-tracker deploy generate [OPTIONS] MODE

Arguments:
  MODE                          {local|prod|nginx}  [required]

Options:
  -o, --output-dir DIRECTORY    Where to write the compose file (default: repo root).
  --api-port INTEGER            Host port to publish the API on. [default: 8000]
  --workers INTEGER             Number of API workers (prod / nginx only). [default: 4]
  -f, --force                   Overwrite existing files without asking.
  -y, --yes                     Assume yes for all prompts.
  --dry-run                     Show what would be written, don't touch disk.
```

#### Modes

| Mode    | Stack                                                                    | Use for                                |
|---------|--------------------------------------------------------------------------|----------------------------------------|
| `local` | API (target `dev`) + worker + Postgres + Redis. Source mounted, hot-reload. | Local development                      |
| `prod`  | API (target `prod`, `WORKERS` env) + worker + Postgres + Redis + migrate.  | Single-host production, no proxy       |
| `nginx` | `prod` + nginx reverse proxy on port 80. API exposed on internal network. | Production behind a reverse proxy      |

All modes target the same multi-stage `backend/Dockerfile` — no per-mode Dockerfile is generated.

#### Examples

```bash
# Generate the dev stack at the repo root
uv run job-tracker deploy generate local

# Override workers and port
uv run job-tracker deploy generate prod --workers 8 --api-port 9000

# Dry run — print what would be written, don't touch disk
uv run job-tracker deploy generate nginx --output-dir /tmp/scratch --dry-run

# Generate into a separate directory (for staging configs in CI, etc.)
uv run job-tracker deploy generate prod --output-dir ./deploy/prod --yes
```

#### What it writes

| Mode    | Files                                          |
|---------|------------------------------------------------|
| `local` | `<output-dir>/docker-compose.yml`              |
| `prod`  | `<output-dir>/docker-compose.yml`              |
| `nginx` | `<output-dir>/docker-compose.yml`<br>`<output-dir>/nginx/default.conf` |

Existing files are protected: if a target already exists you'll be prompted to confirm overwrite. Use `--force` (or `--yes`) for non-interactive runs.

#### Generated compose conventions

All three modes use the same service names and networking:

- **`api`** — the FastAPI application
- **`worker`** — Taskiq worker, running `taskiq worker infrastructure.taskiq.worker:default_broker`
- **`postgres`** — Postgres 16 (alpine), with health check
- **`redis`** — Redis 7 (alpine), with health check
- **`migrate`** (prod & nginx) — runs `alembic upgrade head` once, with `CONFIRM_PRODUCTION_MIGRATION=yes`. The `api` and `worker` services depend on it via `service_completed_successfully`.
- **`nginx`** (nginx mode only) — Nginx 1.27 alpine, mounting the generated `nginx/default.conf` read-only

The compose file references `./backend/.env` for env vars. Make sure that file exists (`cp backend/.env.example backend/.env`) before `docker compose up`.

## `job-tracker env`

Inspect and prepare the runtime environment. Two sub-commands today.

### `job-tracker env gen-secret`

Generate a high-entropy hex secret suitable for `SECRET_KEY`.

```text
Usage: job-tracker env gen-secret [OPTIONS]

Options:
  --bytes INTEGER RANGE [16 ≤ x ≤ 128]   Number of random bytes (hex output is 2x). [default: 32]
```

```bash
$ uv run job-tracker env gen-secret
af97045f600bf988041ec4b6fd891763d8f79f01f0a0a4a7ed2022e57f771a9e

$ uv run job-tracker env gen-secret --bytes 16
c042a8aa0d678a9c73dc371e3e0d6a5e
```

The default produces 64 hex characters (256 bits of entropy) — enough for any of the project's secret slots (`SECRET_KEY`, signed-cookie secrets, etc.). Pipe directly into your secrets manager:

```bash
uv run job-tracker env gen-secret | gh secret set SECRET_KEY --repo my-org/my-app
```

### `job-tracker env validate`

Run the production security validator against your current settings, regardless of `ENVIRONMENT`.

```text
Usage: job-tracker env validate
```

```bash
$ uv run job-tracker env validate
Critical (2):
  • SECRET_KEY is using default or insecure value. ...
  • Database is using default credentials (POSTGRES_PASSWORD='postgres'). ...
```

The command:

1. Imports the same `ProductionSecurityValidator` the application uses at startup
2. Forces `_is_production() = True` so the checks run regardless of `ENVIRONMENT`
3. Captures critical errors and warnings, prints them grouped, and exits non-zero if any critical issues exist

Exit codes:

| Code | Meaning                                              |
|------|------------------------------------------------------|
| 0    | No critical issues. Warnings (if any) are advisory.  |
| 1    | One or more critical issues found.                   |

Useful in CI to gate deployments:

```yaml
# .github/workflows/deploy.yml (excerpt)
- run: uv run job-tracker env validate
  env:
    SECRET_KEY: ${{ secrets.SECRET_KEY }}
    POSTGRES_PASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
    # ...
```

The validator's specific checks are documented in [Production → The Production Validator](../user-guide/production.md#the-production-validator).

## Global Options

Typer-provided options work on any sub-command:

| Option                  | Effect                                              |
|-------------------------|-----------------------------------------------------|
| `--help`                | Show command help and exit                          |
| `--install-completion`  | Install shell completion (bash/zsh/fish)            |
| `--show-completion`     | Print completion script for the current shell      |

## Exit Codes

| Code | Meaning                                              |
|------|------------------------------------------------------|
| 0    | Success                                             |
| 1    | Validation or operation failed                      |
| 2    | Argument parsing error (bad flag, missing argument) |

## Discoverability

Every command has `--help`:

```bash
uv run job-tracker --help
uv run job-tracker deploy --help
uv run job-tracker deploy generate --help
uv run job-tracker env --help
uv run job-tracker env validate --help
```

The root `job-tracker --help` lists every mounted command group, including those contributed by plugins. If a plugin you installed isn't showing up, see [Plugins → Troubleshooting](plugins.md#troubleshooting).
