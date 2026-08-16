# job-tracker — job-tracker CLI

`job-tracker` is the developer/operator command-line tool for projects built on the
job-tracker. It generates deployment artifacts, helps prepare the
runtime environment, and serves as the host for plugin commands and feature
generators.

## Install

This package is part of the workspace. From the repo root:

```bash
uv sync                    # syncs the workspace; job-tracker is available via `uv run job-tracker`
uv run job-tracker --help
```

To install `job-tracker` machine-wide so it works outside this repo:

```bash
uv tool install --editable ./cli
job-tracker --help
```

## What's here

```
cli/src/cli/
├── app.py                 root Typer app + plugin discovery
├── plugins.py             entry-point loaders for job_tracker.commands and job_tracker.features
├── commands/              in-tree command sub-apps
│   ├── deploy.py          job-tracker deploy generate <mode>
│   └── env.py             job-tracker env gen-secret / job-tracker env validate
├── features/              feature framework (manifest, plan, installer)
│   └── _builtins/         in-tree features
│       └── deploy/        compose/Dockerfile templates for local/prod/nginx
└── lib/                   shared helpers (project discovery, prompts, render)
```

## Plugin extension points

Two kinds of plugins, kept deliberately separate:

- `job_tracker.commands` entry-point group — third-party Typer sub-apps mounted under
  `job-tracker <name>` (e.g. `job-tracker aws deploy`).
- `job_tracker.features` entry-point group — code generators with a manifest that
  `job-tracker feature` can list, install, and remove.

See `cli/src/cli/plugins.py` for the discovery contracts.
