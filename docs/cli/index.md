# job-tracker — the job-tracker CLI

`job-tracker` is the developer/operator tool that ships alongside the project. It generates deployment artifacts, helps prepare the runtime environment, and serves as the host for plugin commands and feature generators.

It is **not** part of the deployable backend. The backend image stays lean — `job-tracker` lives in its own workspace package (`cli/`) and is only present in development environments and on machines where you've installed it as a tool.

## What's in this section

- **[Commands](commands.md)** — complete reference for the in-tree `deploy` and `env` sub-apps
- **[Plugins](plugins.md)** — extension points (`job_tracker.commands` and `job_tracker.features`) and authoring guide

## Repository Layout

```text
job-tracker/
├── pyproject.toml          # workspace root (uv workspace metadata)
├── backend/                # deployable application — never ships job-tracker
│   └── src/...
├── cli/                    # the job-tracker package
│   ├── pyproject.toml      # typer + jinja2 + workspace dep on backend
│   └── src/cli/
│       ├── app.py          # Typer root + plugin discovery
│       ├── commands/       # in-tree command sub-apps
│       ├── features/       # feature framework + in-tree features
│       └── plugins.py      # entry-point loaders
└── docs/
```

The two-package split is deliberate: `cli/` depends on `backend/` (for things like `job-tracker env validate`), but `backend/` never depends on `cli/`. Production images ship `backend/` only.

## Install

### In-repo (most common)

```bash
git clone https://github.com/job-tracker/job-tracker
cd job-tracker
uv sync                  # syncs the workspace; installs backend + cli into one venv
uv run job-tracker --help         # works from anywhere in the repo
```

The workspace shares a single `.venv/` at the repo root. You can run `uv run job-tracker` from any subdirectory — uv walks up to find the workspace root.

### Machine-wide (optional)

If you want `job-tracker` on `PATH` outside the repo:

```bash
uv tool install --editable ./cli
job-tracker --help
```

`--editable` means edits to `cli/src/cli/` show up immediately without reinstall. Re-run `uv tool install --editable ./cli` only when `cli/pyproject.toml` changes (deps, entry points). To uninstall:

```bash
uv tool uninstall job-tracker-cli
```

## Quick Tour

### Generate a Compose File

```bash
uv run job-tracker deploy generate local                  # hot-reload dev stack
uv run job-tracker deploy generate prod --workers 8       # production stack
uv run job-tracker deploy generate nginx                  # production behind nginx
```

Each command writes `docker-compose.yml` (and `nginx/default.conf` for the nginx mode) to the repo root by default. Use `--output-dir` to target somewhere else.

### Generate a Secret

```bash
uv run job-tracker env gen-secret
# → 64-char hex suitable for SECRET_KEY
```

### Audit Production Settings

```bash
uv run job-tracker env validate
# Forces the production security validator regardless of ENVIRONMENT.
# Exits 1 if any critical issues are found.
```

## Command Tree

```text
job-tracker
├── deploy
│   └── generate <mode> [options]    # mode ∈ {local, prod, nginx}
└── env
    ├── gen-secret [--bytes N]
    └── validate
```

Plugin sub-apps mount as siblings of `deploy` and `env`. See [Plugins](plugins.md) for details.

## Design Principles

- **No surprises in production.** `job-tracker` never runs against production at runtime — it's a developer/operator tool. Production images don't even include the `cli` package.
- **Two extension points, kept separate.** Command plugins (Typer sub-apps) and feature plugins (code generators with manifests) have different lifecycles and shouldn't share machinery.
- **Templates as data.** Built-in features render Jinja templates. Plugin features do the same. The installer is the only thing that needs to know how to execute the plan.
- **Idempotent and dry-runnable.** Every operation that mutates the user's repo prompts before overwriting and supports `--dry-run`.

## Next Steps

- **[Commands](commands.md)** — full reference for the shipped commands
- **[Plugins](plugins.md)** — write your own commands or features
